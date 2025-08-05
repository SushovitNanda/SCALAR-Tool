import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import PCA
import logging
from modules.text_preprocessing import TextPreprocessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def visualize_clusters(embeddings, labels, title):
    """
    Enhanced visualization with cluster annotations.
    
    Args:
        embeddings: Input embeddings to visualize
        labels: Labels for each embedding point
        title: Title for the plot
    """
    if embeddings.shape[0] < 2:
        logger.warning("Not enough samples for visualization")
        return
        
    # Convert labels if needed
    if isinstance(labels[0], str):
        label_encoder = LabelEncoder()
        numeric_labels = label_encoder.fit_transform(labels)
        unique_labels = list(label_encoder.classes_)
    else:
        numeric_labels = labels
        unique_labels = sorted(list(set(labels)))
    
    # Reduce dimensionality for visualization
    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(embeddings)
    
    # Create figure and axis
    plt.figure(figsize=(12, 8))
    
    # Plot each cluster with a different color
    unique_numeric_labels = sorted(list(set(numeric_labels)))
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_numeric_labels)))
    
    for label_idx, label in enumerate(unique_numeric_labels):
        mask = numeric_labels == label
        points = reduced_embeddings[mask]
        
        if len(points) > 0:
            plt.scatter(
                points[:, 0],
                points[:, 1],
                c=[colors[label_idx]],
                label=unique_labels[label_idx] if isinstance(labels[0], str) else f"Cluster {label}",
                alpha=0.6
            )
    
    # Add cluster centers if available
    if hasattr(embeddings, 'cluster_centers_'):
        centers = pca.transform(embeddings.cluster_centers_)
        plt.scatter(
            centers[:, 0],
            centers[:, 1],
            c='black',
            marker='x',
            s=200,
            linewidths=3,
            label='Centroids'
        )
    
    # Customize plot
    plt.title(title, fontsize=14, pad=20)
    plt.xlabel(f"First Principal Component\nExplained Variance: {pca.explained_variance_ratio_[0]:.3f}")
    plt.ylabel(f"Second Principal Component\nExplained Variance: {pca.explained_variance_ratio_[1]:.3f}")
    
    # Add legend with smaller font and more columns if many labels
    if len(unique_numeric_labels) > 10:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2, fontsize=8)
    else:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    
    plt.tight_layout()
    return plt.gcf()

def plot_similarity_matrix(similarity_matrix, cluster_labels, class_labels, title="Cluster-Class Similarity Matrix"):
    """
    Plot similarity matrix between clusters and classes.
    
    Args:
        similarity_matrix: Matrix of similarities between clusters and classes
        cluster_labels: Labels for clusters
        class_labels: Labels for classes
        title: Title for the plot
    """
    plt.figure(figsize=(12, 8))
    plt.imshow(similarity_matrix, cmap='YlOrRd', aspect='auto')
    plt.colorbar(label='Similarity Score')
    
    # Add text annotations
    for i in range(similarity_matrix.shape[0]):
        for j in range(similarity_matrix.shape[1]):
            plt.text(j, i, f"{similarity_matrix[i, j]:.2f}",
                    ha="center", va="center",
                    color="black" if similarity_matrix[i, j] > 0.5 else "white")
    
    # Customize plot
    plt.title(title, pad=20)
    plt.xticks(range(len(class_labels)), class_labels, rotation=45, ha='right')
    plt.yticks(range(len(cluster_labels)), [f"Cluster {i}" for i in cluster_labels])
    
    plt.tight_layout()
    return plt.gcf()

def plot_cluster_sizes(cluster_labels, title="Cluster Size Distribution"):
    """
    Plot distribution of cluster sizes.
    
    Args:
        cluster_labels: Labels assigned to each data point
        title: Title for the plot
    """
    unique_labels, counts = np.unique(cluster_labels, return_counts=True)
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(unique_labels)), counts)
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    plt.title(title)
    plt.xlabel("Cluster ID")
    plt.ylabel("Number of Samples")
    plt.xticks(range(len(unique_labels)), [f"Cluster {i}" for i in unique_labels])
    
    plt.tight_layout()
    return plt.gcf()

def visualize_hierarchy(cluster_id, topic_terms, title=None):
    """
    Visualize topic hierarchy for a specific cluster using a horizontal bar chart.
    
    Args:
        cluster_id: ID of the cluster to visualize
        topic_terms: Dictionary of topic terms and their weights or list of tuples [(term, weight)]
        title: Custom title (default: "Topic Hierarchy for Cluster {cluster_id}")
        
    Returns:
        Matplotlib figure object
    """
    # Handle different input formats
    if isinstance(topic_terms, dict):
        items = list(topic_terms.items())
    elif isinstance(topic_terms, list) and all(isinstance(item, tuple) for item in topic_terms):
        items = topic_terms
    else:
        logger.error(f"Invalid topic_terms format for cluster {cluster_id}")
        return None
    
    # Preprocess terms for better readability
    preprocessor = TextPreprocessor()
    processed_items = []
    for term, weight in items:
        processed_term = preprocessor.preprocess_text(term)
        if processed_term != "unknown" and processed_term.strip():
            processed_items.append((processed_term, weight))
    # Remove duplicates while preserving order
    seen = set()
    filtered_items = []
    for term, weight in processed_items:
        if term not in seen:
            filtered_items.append((term, weight))
            seen.add(term)
    # Sort by weight in descending order
    filtered_items.sort(key=lambda x: x[1], reverse=True)
    # Take top 15 terms for readability
    top_items = filtered_items[:15]
    # Extract terms and weights
    terms = [item[0] for item in top_items]
    weights = [item[1] for item in top_items]
    # Create horizontal bar chart
    fig, ax = plt.figure(figsize=(10, 8)), plt.gca()
    # Plot bars in descending order for better visualization
    terms = terms[::-1]  # Reverse to show highest at the top
    weights = weights[::-1]
    # Choose colors based on weights to create a gradient effect
    colors = plt.cm.viridis(np.array(weights) / max(weights) if weights else 1)
    bars = ax.barh(range(len(terms)), weights, color=colors)
    # Add value labels to bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        formatted_weight = f"{width:.3f}" if width < 0.01 else f"{width:.2f}"
        ax.text(
            width + 0.01, 
            bar.get_y() + bar.get_height()/2,
            formatted_weight,
            va='center'
        )
    # Customize plot appearance
    if title is None:
        if cluster_id == 0:
            title = f"Top Terms for Cluster 0 (Entertainment)"
        else:
            title = f"Topic Hierarchy for Cluster {cluster_id}"
    else:
        if cluster_id == 0 and "Entertainment" not in title:
            title += " (Entertainment)"
    ax.set_title(title, fontsize=14, pad=20)
    ax.set_xlabel("Term Weight", fontsize=12)
    ax.set_ylabel("Terms", fontsize=12)
    ax.set_yticks(range(len(terms)))
    ax.set_yticklabels(terms)
    # Add grid lines for readability
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    return fig 