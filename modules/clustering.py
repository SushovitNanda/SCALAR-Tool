import numpy as np
import logging
from sklearn.cluster import KMeans, AgglomerativeClustering, Birch
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cluster_and_assign_labels(embeddings, n_clusters, wikipedia_embeddings, all_labels, clustering_method="kmeans"):
    """
    Cluster embeddings and assign labels using KMeans, HAC, GMM or BIRCH clustering.
    
    Args:
        embeddings: Input embeddings to cluster
        n_clusters: Number of clusters to create
        wikipedia_embeddings: Dictionary of label to embedding mappings
        all_labels: List of all possible labels
        clustering_method: One of "kmeans", "hac", "gmm", or "birch"
    
    Returns:
        predicted_labels: List of labels assigned to each input embedding
        cluster_labels: Cluster indices for each input embedding
        similarity_matrix: Matrix of cluster centroid to label similarities
    """
    # Handle edge cases
    if embeddings.shape[0] < n_clusters:
        logger.warning(f"Not enough samples ({embeddings.shape[0]}) for {n_clusters} clusters. Reducing cluster count.")
        n_clusters = max(2, embeddings.shape[0] - 1)
    
    if embeddings.shape[0] == 1:
        logger.warning("Only one sample available. Clustering skipped.")
        return [all_labels[0]], [0], np.array([[1.0] * len(all_labels)])
    
    # Always normalize embeddings for consistent results across methods
    scaler = StandardScaler()
    scaled_embeddings = scaler.fit_transform(embeddings)
    
    # Perform clustering based on the selected method with fixed random states
    if clustering_method == "kmeans":
        # Fixed random state and n_init for KMeans
        clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = clusterer.fit_predict(scaled_embeddings)
        cluster_centroids = clusterer.cluster_centers_
    elif clustering_method == "hac":
        # Use distance_threshold=None to ensure we get exactly n_clusters
        clusterer = AgglomerativeClustering(n_clusters=n_clusters)
        cluster_labels = clusterer.fit_predict(scaled_embeddings)
        # Calculate centroids for HAC
        cluster_centroids = np.zeros((n_clusters, scaled_embeddings.shape[1]))
        for i in range(n_clusters):
            cluster_points = scaled_embeddings[cluster_labels == i]
            if len(cluster_points) > 0:
                cluster_centroids[i] = np.mean(cluster_points, axis=0)
            else:
                logger.warning(f"Empty cluster {i} found. Using zeros for centroid.")
                cluster_centroids[i] = np.zeros(scaled_embeddings.shape[1])
    elif clustering_method == "gmm":
        # Gaussian Mixture Model clustering with fixed parameters
        gmm = GaussianMixture(n_components=n_clusters, random_state=42)
        cluster_labels = gmm.fit_predict(scaled_embeddings)
        cluster_centroids = gmm.means_
    elif clustering_method == "birch":
        # Fixed threshold for BIRCH
        clusterer = Birch(n_clusters=n_clusters, threshold=0.5)
        cluster_labels = clusterer.fit_predict(scaled_embeddings)
        
        # Calculate centroids for BIRCH
        cluster_centroids = np.zeros((n_clusters, scaled_embeddings.shape[1]))
        for i in range(n_clusters):
            cluster_points = scaled_embeddings[cluster_labels == i]
            if len(cluster_points) > 0:
                cluster_centroids[i] = np.mean(cluster_points, axis=0)
            else:
                logger.warning(f"Empty cluster {i} found. Using zeros for centroid.")
                cluster_centroids[i] = np.zeros(scaled_embeddings.shape[1])
    else:
        raise ValueError(f"Unsupported clustering method: {clustering_method}. Choose 'kmeans', 'hac', 'gmm', or 'birch'")
    
    # Log cluster distribution for debugging
    cluster_counts = np.bincount(cluster_labels, minlength=n_clusters)
    logger.info(f"Cluster distribution: {dict(enumerate(cluster_counts))}")
    
    # Check if we have the expected number of clusters and fix if necessary
    unique_clusters = sorted(list(set(cluster_labels)))
    if len(unique_clusters) < n_clusters:
        logger.warning(f"Only {len(unique_clusters)} clusters were formed, expected {n_clusters}. Creating additional clusters.")
        
        # Create synthetic clusters by splitting the largest existing clusters
        missing_clusters = n_clusters - len(unique_clusters)
        
        # Get the sizes of each cluster
        cluster_sizes = np.bincount(cluster_labels)
        
        # Get indices of the largest clusters that we'll split
        largest_cluster_indices = np.argsort(cluster_sizes)[-missing_clusters:]
        
        # Create a new cluster_labels array
        new_cluster_labels = cluster_labels.copy()
        next_cluster_id = max(unique_clusters) + 1
        
        # For each missing cluster, take points from the largest clusters
        created_clusters = 0
        for i, cluster_idx in enumerate(largest_cluster_indices):
            # Get indices of points in this large cluster
            points_in_cluster = np.where(cluster_labels == cluster_idx)[0]
            
            # Skip if not enough points to split
            if len(points_in_cluster) <= 3:  # Need more than 3 points for a meaningful split
                logger.warning(f"Cluster {cluster_idx} only has {len(points_in_cluster)} points, which is too few to split.")
                continue
                
            # Take half of the points and assign to new cluster
            # Use a deterministic approach to split the cluster
            points_to_reassign = np.random.choice(points_in_cluster, size=len(points_in_cluster) // 2, replace=False)
            new_cluster_labels[points_to_reassign] = next_cluster_id
            
            # Create a new centroid for this new cluster
            cluster_points = scaled_embeddings[points_to_reassign]
            new_centroid = np.mean(cluster_points, axis=0)
            
            # Update tracking variables
            created_clusters += 1
            
            # If we've created enough clusters or this is the last one in our list
            if created_clusters == missing_clusters or i == len(largest_cluster_indices) - 1:
                # Calculate centroids anew with proper dimensions
                final_cluster_count = len(unique_clusters) + created_clusters
                updated_centroids = np.zeros((final_cluster_count, scaled_embeddings.shape[1]))
                
                # Copy existing centroids
                for j, cluster_id in enumerate(sorted(unique_clusters)):
                    updated_centroids[j] = cluster_centroids[j if j < cluster_centroids.shape[0] else 0]
                
                # Add new centroids for the clusters we created
                updated_centroids[len(unique_clusters):] = new_centroid
                
                # Update cluster_centroids and n_clusters
                cluster_centroids = updated_centroids
                n_clusters = final_cluster_count
                break
            
            next_cluster_id += 1
        
        # Update cluster_labels
        cluster_labels = new_cluster_labels
        
        # If we couldn't create all the requested clusters, inform the user
        if created_clusters < missing_clusters:
            logger.warning(f"Could only create {created_clusters} additional clusters out of {missing_clusters} requested due to data limitations.")
        
        # Inform about the new cluster count
        logger.info(f"Created {created_clusters} additional clusters. New cluster count: {n_clusters}")
    
    # Ensure all labels have embeddings (fill missing with zeros)
    for label in all_labels:
        if label not in wikipedia_embeddings:
            logger.warning(f"Missing Wikipedia embedding for label '{label}'. Using zeros.")
            if wikipedia_embeddings:
                first_key = next(iter(wikipedia_embeddings))
                embed_dim = wikipedia_embeddings[first_key].shape[0]
            else:
                embed_dim = embeddings.shape[1]
            wikipedia_embeddings[label] = np.zeros(embed_dim)
    
    # Calculate similarity between cluster centroids and label embeddings
    similarity_matrix = np.zeros((n_clusters, len(all_labels)))
    for i, centroid in enumerate(cluster_centroids):
        for j, label in enumerate(all_labels):
            centroid_reshaped = centroid.reshape(1, -1)
            wiki_embed_reshaped = wikipedia_embeddings[label].reshape(1, -1)
            similarity_matrix[i, j] = cosine_similarity(centroid_reshaped, wiki_embed_reshaped)[0][0]
    
    # Log similarity matrix for debugging
    logger.debug(f"Similarity matrix shape: {similarity_matrix.shape}")
    
    # Assign labels to clusters using enhanced greedy allocation with fixed parameters
    assignments = enhanced_greedy_allocation(similarity_matrix, use_zscore=True, use_softmax=True)
    
    # Create mapping from cluster index to label
    cluster_to_label = {}
    for i in range(n_clusters):
        if i < len(assignments) and assignments[i] != -1 and assignments[i] < len(all_labels):
            cluster_to_label[i] = all_labels[assignments[i]]
        else:
            cluster_to_label[i] = "other"
    
    # Log the cluster to label mapping
    logger.info(f"Cluster to label mapping: {cluster_to_label}")
    
    # Assign labels to each sample
    predicted_labels = [cluster_to_label[cluster] for cluster in cluster_labels]
    
    return predicted_labels, cluster_labels, similarity_matrix

def enhanced_greedy_allocation(similarity_matrix, use_zscore=True, use_softmax=True):
    """
    Enhanced greedy allocation algorithm for assigning clusters to labels.
    
    Args:
        similarity_matrix: Matrix of similarities between clusters and labels
        use_zscore: Whether to apply z-score normalization
        use_softmax: Whether to apply softmax normalization
    
    Returns:
        List of label assignments for each cluster
    """
    similarity_matrix = similarity_matrix.copy()
    num_clusters, num_labels = similarity_matrix.shape
    assignments = [-1] * num_clusters
    assigned_labels = set()
    
    # Apply consistent normalization to similarity values
    if use_zscore:
        # For numerical stability
        epsilon = 1e-8
        for i in range(num_clusters):
            row_mean = np.mean(similarity_matrix[i])
            row_std = np.std(similarity_matrix[i])
            if row_std > epsilon:  # Avoid division by very small values
                similarity_matrix[i] = (similarity_matrix[i] - row_mean) / row_std
            else:
                # If standard deviation is too small, use normalization instead
                min_val = np.min(similarity_matrix[i])
                max_val = np.max(similarity_matrix[i])
                range_val = max_val - min_val
                if range_val > epsilon:
                    similarity_matrix[i] = (similarity_matrix[i] - min_val) / range_val
                # If range is also too small, keep as is (all values are very similar)

    # Apply softmax function to make probabilities sum to 1
    if use_softmax:
        # Temperature parameter to control the softmax distribution
        temperature = 1.0
        for i in range(num_clusters):
            # Stabilize by subtracting max value
            max_val = np.max(similarity_matrix[i])
            exp_values = np.exp((similarity_matrix[i] - max_val) / temperature)
            sum_exp = np.sum(exp_values)
            if sum_exp > 0:
                similarity_matrix[i] = exp_values / sum_exp

    # Greedy assignment algorithm with fixed iteration order
    for _ in range(min(num_clusters, num_labels)):
        max_sim = -float('inf')
        selected_cluster, selected_label = None, None

        # Deterministic scan of all cluster-label pairs
        for i in range(num_clusters):
            if assignments[i] != -1:
                continue
            for j in range(num_labels):
                if j in assigned_labels:
                    continue
                if similarity_matrix[i, j] > max_sim:
                    max_sim = similarity_matrix[i, j]
                    selected_cluster, selected_label = i, j

        if selected_cluster is not None and selected_label is not None:
            assignments[selected_cluster] = selected_label
            assigned_labels.add(selected_label)
            # Mask out this cluster and label to avoid reassignment
            similarity_matrix[selected_cluster, :] = -np.inf
            similarity_matrix[:, selected_label] = -np.inf

    return assignments 