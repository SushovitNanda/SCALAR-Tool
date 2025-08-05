import logging
import os
import json
import warnings
from datetime import datetime

# Suppress TensorFlow and oneDNN warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF logging except errors
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN custom operations
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from modules.text_preprocessing import TextPreprocessor
from modules.wikipedia_extractor import WikiCorpusExtractor
from modules.embedding_generator import EmbeddingGenerator
from modules.bertopic_interpreter import BERTopicInterpreter
from modules.clustering import cluster_and_assign_labels
import modules.visualization as vis
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        print("=== SCALAR - Semantic Clustering and Labeling for Sector Classification of Crowd-Based Software Requirements ===")
        
        # Configuration
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        setup_logger = logging.getLogger("setup")
        
        # User inputs
        file_path = input("Enter path to the CSV file: ").strip()
        embedding_type = input("Choose embedding type (sentence-bert/sentence-roberta): ").strip().lower()
        clustering_method = input("Choose clustering algorithm (kmeans/hac/gmm/birch): ").strip().lower()
        num_clusters = int(input("Enter the number of classes/labels: "))
        use_bertopic = input("Perform BERTopic post-hoc analysis? (y/n): ").strip().lower() == 'y'
        min_wiki_pages = int(input("Minimum Wikipedia pages per term (3-10 recommended): ") or 3)

        # Validate inputs
        if embedding_type not in ["sentence-bert", "sentence-roberta"]:
            print("Defaulting to sentence-bert")
            embedding_type = "sentence-bert"
        
        if clustering_method not in ["kmeans", "hac", "gmm", "birch"]:
            print("Defaulting to kmeans")
            clustering_method = "kmeans"
        
        # Load class descriptions
        class_descriptions = {}
        for i in range(num_clusters):
            class_name = input(f"Class {i+1} domain name: ").strip()
            class_description = input(f"Class {i+1} description: ").strip()
            class_descriptions[class_name] = class_description

        # 1. Data Loading
        print("\n[1/5] Loading data...")
        df = pd.read_csv(file_path, usecols=range(5), dtype=str).fillna("")
        texts = df.apply(lambda row: ' '.join(row.astype(str)), axis=1).tolist()
        print(f"Loaded {len(texts)} samples")

        # Initialize preprocessor and process texts
        preprocessor = TextPreprocessor()
        processed_texts = [preprocessor.preprocess_text(text) for text in texts]

        # Extract Wikipedia knowledge
        print("\n[2/5] Extracting Wikipedia knowledge...")
        wiki_extractor = WikiCorpusExtractor(class_descriptions)
        wiki_extractor.max_pages_per_term = min_wiki_pages
        wiki_corpus = wiki_extractor.extract_corpus()
        wiki_texts = list(wiki_corpus.values())
        
        # Process texts and generate embeddings separately for documents and Wikipedia
        print("\n[3/5] Generating embeddings...")
        embedding_gen = EmbeddingGenerator(embedding_type)
        
        # Generate embeddings for original documents
        document_embeddings = embedding_gen.generate_embeddings(processed_texts)
        
        # Generate embeddings for Wikipedia texts
        wiki_embeddings = {
            label: embedding_gen.generate_embeddings([text])[0]  # Get first (and only) embedding
            for label, text in zip(class_descriptions.keys(), wiki_texts)
        }
        
        print(f"Document embedding shape: {document_embeddings.shape}")
        print(f"Wikipedia embeddings shape: ({len(wiki_embeddings)}, {next(iter(wiki_embeddings.values())).shape[0]})")

        # Perform clustering
        print("\n[4/5] Performing clustering...")
        predicted_labels, cluster_labels, similarity_matrix = cluster_and_assign_labels(
            document_embeddings,
            num_clusters,
            wiki_embeddings,
            list(class_descriptions.keys()),
            clustering_method=clustering_method
        )

        # Visualize clustering results
        print("Generating cluster visualizations...")
        try:
            # Visualize cluster distribution
            cluster_viz = vis.visualize_clusters(
                document_embeddings,
                predicted_labels,
                f"Document Clusters ({clustering_method.upper()})"
            )
            if cluster_viz:
                cluster_viz.savefig(f"clusters_{timestamp}.png", bbox_inches='tight')
                print("Saved cluster visualization")

            # Visualize similarity matrix
            if similarity_matrix is not None:
                sim_viz = vis.plot_similarity_matrix(
                    similarity_matrix,
                    sorted(list(set(cluster_labels))),
                    list(class_descriptions.keys()),
                    "Cluster-Class Similarity Matrix"
                )
                if sim_viz:
                    sim_viz.savefig(f"similarity_matrix_{timestamp}.png", bbox_inches='tight')
                    print("Saved similarity matrix visualization")

            # Visualize cluster sizes
            size_viz = vis.plot_cluster_sizes(cluster_labels, "Cluster Size Distribution")
            if size_viz:
                size_viz.savefig(f"cluster_sizes_{timestamp}.png", bbox_inches='tight')
                print("Saved cluster size distribution")
        except Exception as e:
            print(f"Warning: Some visualizations failed: {str(e)}")

        # BERTopic analysis
        if use_bertopic:
            print("\n[5/5] Running BERTopic analysis...")
            cluster_distribution = Counter(cluster_labels)
            print(f"Cluster distribution: {cluster_distribution}")
            
            # Check if we have enough data for BERTopic
            small_clusters = [c for c, count in cluster_distribution.items() if count < 5]
            if small_clusters:
                print(f"Warning: Clusters {small_clusters} have fewer than 5 documents, which may cause BERTopic issues")
            
            # Create interpreter with appropriate parameters
            min_topic_size = max(3, min(5, min(cluster_distribution.values()) // 3))
            print(f"Using minimum topic size of {min_topic_size}")
            
            bertopic_interpreter = BERTopicInterpreter(
                embedding_model=embedding_gen.model,
                n_gram_range=(1, 3),
                min_topic_size=min_topic_size
            )
            
            # Run analysis with progress tracking
            print("Processing clusters with BERTopic...", end="")
            cluster_topics = bertopic_interpreter.fit_transform_with_clusters(texts, cluster_labels)
            print(" Done!")
            
            # Generate outputs per cluster
            topic_reports = []
            for cluster_id in sorted(set(cluster_labels)):
                print(f"Generating visualizations for cluster {cluster_id}...")
                
                # Get cluster label
                cluster_samples = [i for i, c in enumerate(cluster_labels) if c == cluster_id]
                if cluster_samples:
                    cluster_label = predicted_labels[cluster_samples[0]]
                else:
                    cluster_label = "unknown"
                
                # Visualizations with error handling
                try:
                    viz = bertopic_interpreter.visualize_cluster_topics(
                        cluster_id,
                        save_path=f"topics_{timestamp}_cluster_{cluster_id}"
                    )
                    if viz:
                        print(f"  - Topic visualization saved")
                    else:
                        print(f"  - Topic visualization unavailable")
                except Exception as e:
                    print(f"  - Topic visualization failed: {e}")
                
                try:
                    hier = bertopic_interpreter.visualize_hierarchy(
                        cluster_id,
                        save_path=f"hierarchy_{timestamp}_cluster_{cluster_id}"
                    )
                    if hier:
                        print(f"  - Hierarchy visualization saved")
                    else:
                        print(f"  - Hierarchy visualization unavailable")
                except Exception as e:
                    print(f"  - Hierarchy visualization failed: {e}")
                
                # Collect report data
                if cluster_id in bertopic_interpreter.cluster_topics:
                    for topic_id, words in bertopic_interpreter.cluster_topics[cluster_id].items():
                        if words:  # Check for empty word lists
                            topic_reports.append({
                                'cluster_id': cluster_id,
                                'cluster_label': cluster_label,
                                'topic_id': topic_id,
                                'top_terms': ", ".join([w for w, _ in words[:5]]),
                                'term_scores': str(dict(words[:5])),
                                'sample_count': list(cluster_labels).count(cluster_id)
                            })
                else:
                    print(f"  - No topics available for cluster {cluster_id}")

            # Save reports
            if topic_reports:
                topics_df = pd.DataFrame(topic_reports)
                topics_df.to_csv(f"topic_analysis_{timestamp}.csv", index=False)
                print(f"Saved topic analysis to topic_analysis_{timestamp}.csv")
            else:
                print("Warning: No topics were extracted for any cluster")

        # Save final results
        output_file = f"results_{clustering_method}_{embedding_type}_{timestamp}.csv"
        df['predicted_label'] = predicted_labels
        df['cluster_id'] = cluster_labels
        df.to_csv(output_file, index=False)
        
        # Print summary
        print("\n=== Final Summary ===")
        print(f"Results saved to: {output_file}")
        print("\nCluster Distribution:")
        cluster_counts = Counter(predicted_labels)
        for label, count in cluster_counts.most_common():
            print(f"{label}: {count} samples ({count/len(predicted_labels):.1%})")
            
        if use_bertopic and bertopic_interpreter.cluster_topics:
            print("\nKey Topics per Cluster:")
            for cluster_id in sorted(set(cluster_labels)):
                print(f"\nCluster {cluster_id}:")
                for line in bertopic_interpreter.get_topic_summary(cluster_id):
                    print(f"  {line}")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace for better debugging
        print("Check logs for details")

if __name__ == "__main__":
    main() 