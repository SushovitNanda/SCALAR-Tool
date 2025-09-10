# SCALAR Modules

This directory contains the core modules used in the SCALAR (Semantic Clustering and Labeling for Sector Classification of Crowd-Based Software Requirements) system.

## Module Overview

### `text_preprocessing.py`
- Handles text cleaning, tokenization, and normalization
- Removes stopwords, punctuation, and applies lemmatization
- Used as the first step in the processing pipeline

### `wikipedia_extractor.py`
- Extracts relevant knowledge from Wikipedia based on domain descriptions
- Identifies key terms in class descriptions and fetches related Wikipedia articles
- Creates a knowledge corpus for each domain/class

### `embedding_generator.py`
- Generates vector embeddings using pre-trained language models
- Supports multiple embedding types (sentence-bert, sentence-roberta)
- Includes fallback mechanisms when models fail to load

### `clustering.py`
- Implements clustering algorithms (KMeans, HAC, GMM, BIRCH)
- Assigns labels to clusters by comparing with Wikipedia knowledge embeddings
- Includes enhanced greedy allocation for optimal cluster-label assignment

### `visualization.py`
- Creates visualizations for clustering results
- Plots cluster distributions, similarity matrices, and cluster sizes
- Provides visual analysis tools for interpreting results

### `bertopic_interpreter.py`
- Performs topic modeling on clusters using BERTopic
- Extracts key topics and terms from each cluster
- Visualizes topic hierarchies and distributions


## Greedy Dynamic Allocation Algorithm

The SCALAR tool uses an enhanced greedy allocation algorithm to optimally assign cluster centroids to domain labels based on their semantic similarity. This algorithm is implemented in the `enhanced_greedy_allocation` function in `clustering.py`.

### How It Works

The greedy dynamic allocation algorithm follows these steps:

#### 1. **Input Processing**
- Takes a similarity matrix where rows represent clusters and columns represent domain labels
- Each cell `[i,j]` contains the cosine similarity between cluster `i` and label `j`
- The algorithm aims to find the optimal one-to-one mapping between clusters and labels

#### 2. **Normalization Phase**
The algorithm applies two optional normalization techniques to improve assignment quality:

**Z-Score Normalization** (`use_zscore=True`):
```python
# For each cluster row, normalize similarities
row_mean = np.mean(similarity_matrix[i])
row_std = np.std(similarity_matrix[i])
similarity_matrix[i] = (similarity_matrix[i] - row_mean) / row_std
```
- Standardizes similarity values within each cluster
- Helps handle cases where one cluster has consistently higher similarities
- Falls back to min-max normalization if standard deviation is too small

**Softmax Normalization** (`use_softmax=True`):
```python
# Convert similarities to probabilities
exp_values = np.exp((similarity_matrix[i] - max_val) / temperature)
similarity_matrix[i] = exp_values / sum_exp
```
- Converts similarity scores to probability distributions
- Temperature parameter (default: 1.0) controls the sharpness of the distribution
- Ensures all values sum to 1 for each cluster

#### 3. **Greedy Assignment Phase**
The core greedy algorithm iteratively selects the best cluster-label pairs:

```python
for _ in range(min(num_clusters, num_labels)):
    max_sim = -float('inf')
    selected_cluster, selected_label = None, None
    
    # Find the highest similarity pair
    for i in range(num_clusters):
        if assignments[i] != -1:  # Skip already assigned clusters
            continue
        for j in range(num_labels):
            if j in assigned_labels:  # Skip already assigned labels
                continue
            if similarity_matrix[i, j] > max_sim:
                max_sim = similarity_matrix[i, j]
                selected_cluster, selected_label = i, j
    
    # Assign the best pair and mark as used
    assignments[selected_cluster] = selected_label
    assigned_labels.add(selected_label)
```

#### 4. **Assignment Strategy**
- **One-to-One Mapping**: Each cluster is assigned to exactly one label, and each label is assigned to at most one cluster
- **Deterministic Order**: Uses a fixed iteration order to ensure reproducible results
- **Greedy Selection**: Always chooses the highest similarity pair available
- **Constraint Satisfaction**: Ensures no cluster or label is assigned twice

### Key Features

#### **Numerical Stability**
- Uses epsilon threshold (1e-8) to prevent division by very small numbers
- Implements fallback normalization when standard deviation is too small
- Stabilizes softmax computation by subtracting maximum values

#### **Flexible Configuration**
- `use_zscore`: Controls whether to apply z-score normalization
- `use_softmax`: Controls whether to apply softmax normalization
- `temperature`: Controls the sharpness of softmax distribution (default: 1.0)

#### **Robust Assignment**
- Handles cases where there are more clusters than labels
- Ensures all clusters get assigned (unassigned clusters get "other" label)
- Provides deterministic results for reproducible experiments

### Example Usage

```python
# Calculate similarity matrix between clusters and labels
similarity_matrix = np.zeros((n_clusters, len(all_labels)))
for i, centroid in enumerate(cluster_centroids):
    for j, label in enumerate(all_labels):
        similarity_matrix[i, j] = cosine_similarity(
            centroid.reshape(1, -1), 
            wikipedia_embeddings[label].reshape(1, -1)
        )[0][0]

# Apply enhanced greedy allocation
assignments = enhanced_greedy_allocation(
    similarity_matrix, 
    use_zscore=True, 
    use_softmax=True
)

# Create cluster-to-label mapping
cluster_to_label = {}
for i in range(n_clusters):
    if i < len(assignments) and assignments[i] != -1:
        cluster_to_label[i] = all_labels[assignments[i]]
    else:
        cluster_to_label[i] = "other"
```

### Advantages

1. **Optimal Local Assignment**: Finds the best possible assignment given the similarity matrix
2. **Computational Efficiency**: O(n²) complexity for n clusters/labels
3. **Deterministic Results**: Always produces the same assignment for the same input
4. **Handles Edge Cases**: Robust against numerical instabilities and unusual similarity distributions
5. **Flexible Normalization**: Can be configured for different similarity distributions

### When to Use Different Settings

- **`use_zscore=True`**: When clusters have different similarity ranges
- **`use_softmax=True`**: When you want probability-based assignments
- **Both enabled**: For most general cases with varied similarity distributions
- **Both disabled**: When raw cosine similarities are already well-normalized



## Extending the Tool: Adding More Embedding and Clustering Mechanisms

SCALAR is designed to be easily extensible, allowing users to add new embedding models and clustering algorithms. The tool already includes support for multiple methods, and adding new ones is straightforward.

### Adding New Embedding Models

To add a new embedding model:

1. **Edit the Frontend** (`src/components/ParameterForm.tsx`):
   ```typescript
   // Add new option to the SelectContent
   <SelectItem value="your-new-model">Your New Model</SelectItem>
   ```

2. **Update the Backend** (`modules/embedding_generator.py`):
   ```python
   # Add to the model_map dictionary
   self.model_map = {
       "sentence-bert": [...],
       "sentence-roberta": [...],
       "your-new-model": [
           "sentence-transformers/your-model-name",
           "fallback-model-if-needed"
       ]
   }
   ```

3. **Update Type Definitions**:
   - Update the `embedding_type` type in `ParameterForm.tsx` to include your new model
   - Update the backend parameter validation if needed

### Adding New Clustering Algorithms

To add a new clustering algorithm:

1. **Edit the Frontend** (`src/components/ParameterForm.tsx`):
   ```typescript
   // Add new option to the clustering method SelectContent
   <SelectItem value="your-new-clustering">Your New Clustering</SelectItem>
   ```

2. **Update the Backend** (`modules/clustering.py`):
   ```python
   # Add new elif condition in cluster_and_assign_labels function
   elif clustering_method == "your-new-clustering":
       # Import your clustering algorithm
       from sklearn.cluster import YourClusteringAlgorithm
       
       # Configure and fit the algorithm
       clusterer = YourClusteringAlgorithm(n_clusters=n_clusters, **your_params)
       cluster_labels = clusterer.fit_predict(scaled_embeddings)
       
       # Calculate centroids (adapt based on your algorithm)
       cluster_centroids = np.zeros((n_clusters, scaled_embeddings.shape[1]))
       for i in range(n_clusters):
           cluster_points = scaled_embeddings[cluster_labels == i]
           if len(cluster_points) > 0:
               cluster_centroids[i] = np.mean(cluster_points, axis=0)
   ```

3. **Update Type Definitions**:
   - Update the `clustering_method` type in `ParameterForm.tsx`
   - Add appropriate error handling for unsupported methods

### Enabling/Disabling Existing Methods

The tool includes HAC and BIRCH clustering methods that are already implemented but can be easily enabled or disabled by modifying the frontend components:

#### To Disable HAC or BIRCH:
1. Open `src/components/ParameterForm.tsx`
2. Comment out the respective SelectItem:
   ```typescript
   <SelectContent>
     <SelectItem value="kmeans">K-Means</SelectItem>
     {/* <SelectItem value="hac">Hierarchical Clustering</SelectItem> */}
     <SelectItem value="gmm">Gaussian Mixture Model</SelectItem>
     {/* <SelectItem value="birch">BIRCH</SelectItem> */}
   </SelectContent>
   ```

#### To Re-enable:
Simply uncomment the lines by removing the `{/* */}` comment markers.

### Best Practices for Extensions

1. **Model Compatibility**: Ensure new embedding models are compatible with the `sentence-transformers` library
2. **Parameter Validation**: Add appropriate parameter validation for new clustering algorithms
3. **Error Handling**: Include fallback mechanisms and proper error logging
4. **Testing**: Test new methods with various datasets to ensure stability
5. **Documentation**: Update this section when adding new methods

### Example: Adding DBSCAN Clustering

Here's a complete example of adding DBSCAN clustering:

**Frontend** (`src/components/ParameterForm.tsx`):
```typescript
<SelectItem value="dbscan">DBSCAN</SelectItem>
```

**Backend** (`modules/clustering.py`):
```python
elif clustering_method == "dbscan":
    from sklearn.cluster import DBSCAN
    
    # DBSCAN doesn't require n_clusters, so we'll use a different approach
    clusterer = DBSCAN(eps=0.5, min_samples=5)
    cluster_labels = clusterer.fit_predict(scaled_embeddings)
    
    # Handle noise points (labeled as -1)
    unique_labels = set(cluster_labels)
    if -1 in unique_labels:
        unique_labels.remove(-1)  # Remove noise label
    
    n_clusters = len(unique_labels)
    if n_clusters == 0:
        # Fallback to K-means if DBSCAN finds no clusters
        clusterer = KMeans(n_clusters=2, random_state=42)
        cluster_labels = clusterer.fit_predict(scaled_embeddings)
        cluster_centroids = clusterer.cluster_centers_
        n_clusters = 2
    else:
        # Calculate centroids for DBSCAN clusters
        cluster_centroids = np.zeros((n_clusters, scaled_embeddings.shape[1]))
        for i, label in enumerate(sorted(unique_labels)):
            cluster_points = scaled_embeddings[cluster_labels == label]
            cluster_centroids[i] = np.mean(cluster_points, axis=0)
```

This extensible design allows researchers and developers to easily experiment with different embedding and clustering approaches for their specific use cases.


This algorithm ensures that each cluster is assigned to the most semantically similar domain label, providing optimal classification results for the SCALAR tool. 
