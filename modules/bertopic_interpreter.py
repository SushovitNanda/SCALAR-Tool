import re
import logging
import torch
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings

# Suppress TensorFlow and oneDNN warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF logging except errors
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN custom operations
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from modules.text_preprocessing import TextPreprocessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check for device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class BERTopicInterpreter:
    """
    Enhanced BERTopic interpreter with robust error handling and cluster-specific modeling.
    """
    def __init__(self, embedding_model=None, n_gram_range=(1, 3), min_topic_size=5):
        """
        Args:
            embedding_model: Pre-trained sentence transformer
            n_gram_range: Range of n-grams to consider (default improves diversity)
            min_topic_size: Base minimum topic size (automatically adjusted per cluster)
        """
        # Initialize embedding model
        if embedding_model is None:
            embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            embedding_model.to(device)
        
        self.embedding_model = embedding_model
        self.n_gram_range = n_gram_range
        self.base_min_topic_size = min_topic_size
        
        # Components that will be created per-cluster
        self.cluster_models = {}
        self.cluster_topics = {}
        
        # Initialize shared components
        self.ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
        
        # Initialize MMR if available
        try:
            from bertopic.representation import MaximalMarginalRelevance
            self.mmr = MaximalMarginalRelevance(diversity=0.5)  # Increased diversity
        except ImportError:
            self.mmr = None

    def fit_transform_with_clusters(self, documents, cluster_labels):
        """
        Process each cluster separately with adaptive parameters.
        
        Returns:
            Dictionary {cluster_id: {topic_id: [(word, score)]}}
        """
        self.cluster_topics = {}
        
        for cluster_id in sorted(set(cluster_labels)):
            try:
                # Get documents for this cluster
                cluster_docs = [
                    str(doc) for i, doc in enumerate(documents) 
                    if cluster_labels[i] == cluster_id
                ]
                
                # Filter out empty or very short documents
                valid_docs = [doc for doc in cluster_docs if doc and len(doc.split()) > 3]
                
                # Skip empty clusters or those with too few valid documents
                if not valid_docs:
                    logger.warning(f"Cluster {cluster_id} has no valid documents.")
                    self.cluster_topics[cluster_id] = {0: [("no_valid_documents", 1.0)]}
                    continue
                    
                if len(valid_docs) < 5:
                    logger.warning(f"Not enough valid documents in cluster {cluster_id}: {len(valid_docs)}/{len(cluster_docs)}")
                    self.cluster_topics[cluster_id] = {0: self._extract_basic_keywords(valid_docs)}
                    continue
                
                # Log the document counts for diagnosis
                logger.info(f"Processing cluster {cluster_id} with {len(valid_docs)} valid documents out of {len(cluster_docs)} total")
                
                # Create cluster-specific model
                topic_model = self._create_cluster_model(valid_docs)
                
                # Fit and store model
                try:
                    topics, _ = topic_model.fit_transform(valid_docs)
                    self.cluster_models[cluster_id] = topic_model
                    
                    # Extract and store topics
                    self.cluster_topics[cluster_id] = self._extract_valid_topics(
                        topic_model, 
                        min_words=3  # Require at least 3 words per topic
                    )
                except Exception as e:
                    logger.warning(f"BERTopic fitting failed for cluster {cluster_id}: {str(e)}")
                    self.cluster_topics[cluster_id] = {0: self._extract_basic_keywords(valid_docs)}
                
            except Exception as e:
                logger.warning(f"Cluster {cluster_id} failed: {str(e)}")
                self.cluster_topics[cluster_id] = {
                    0: [("cluster_processing_failed", 1.0)]
                }
        
        return self.cluster_topics

    def get_topic_summary(self, cluster_id):
        """Get a formatted summary of topics for a cluster, using text preprocessing to filter terms"""
        if cluster_id not in self.cluster_topics:
            return ["No topics available"]
        
        preprocessor = TextPreprocessor()
        all_words = []
        for topic_id, words in self.cluster_topics[cluster_id].items():
            if words:
                all_words.extend(words)
        all_words.sort(key=lambda x: x[1], reverse=True)
        top_words = all_words[:50]
        # Preprocess and filter terms
        filtered_words = []
        for word, _ in top_words:
            processed = preprocessor.preprocess_text(word)
            if processed != "unknown" and processed.strip():
                filtered_words.append(processed)
        word_list = ", ".join(filtered_words)
        return [f"Key Terms: {word_list}"]

    def _create_cluster_model(self, cluster_docs):
        """Create BERTopic instance with cluster-optimized parameters"""
        # Adaptive parameters based on cluster size
        cluster_size = len(cluster_docs)
        min_topic_size = max(
            2,
            min(self.base_min_topic_size, cluster_size // 5)
        )
        n_neighbors = min(15, max(5, cluster_size // 3))
        n_components = min(5, max(2, cluster_size // 10))
        
        try:
            # Cluster-specific UMAP
            umap_model = UMAP(
                n_neighbors=n_neighbors,
                n_components=n_components,
                min_dist=0.0,
                metric='cosine'
            )
            
            return BERTopic(
                embedding_model=self.embedding_model,
                umap_model=umap_model,
                ctfidf_model=self.ctfidf_model,
                representation_model=self.mmr,
                nr_topics="auto",
                min_topic_size=min_topic_size,
                n_gram_range=self.n_gram_range,
                top_n_words=15,  # Increased from default 10
                calculate_probabilities=True,
                verbose=False
            )
        except Exception as e:
            logger.error(f"Error creating BERTopic model: {e}")
            raise

    def _extract_valid_topics(self, topic_model, min_words=3):
        """Extract topics filtering invalid ones"""
        topics = {}
        try:
            # Check if topics are available
            if not hasattr(topic_model, 'get_topics'):
                logger.warning("Topic model has no 'get_topics' method")
                return {0: [("no_topics_available", 1.0)]}
                
            model_topics = topic_model.get_topics()
            if not model_topics:
                logger.warning("Topic model returned empty topics")
                return {0: [("empty_topics", 1.0)]}
            
            for topic_id, topic_words in model_topics.items():
                # Skip outliers and topics with too few words
                if topic_id != -1 and len(topic_words) >= min_words:
                    topics[topic_id] = [
                        (word, score) 
                        for word, score in topic_words 
                        if not re.match(r"^\d+$", word)  # Filter pure numbers
                    ][:10]  # Top 10 words
                    
        except Exception as e:
            logger.warning(f"Topic extraction failed: {e}")
            return {0: [("topic_extraction_failed", 1.0)]}
            
        return topics if topics else {0: [("insufficient_topics", 1.0)]}

    def _extract_basic_keywords(self, documents):
        """Fallback keyword extraction for small clusters"""
        try:
            if not documents:
                return [("no_documents", 1.0)]
                
            # Ensure all documents are strings
            documents = [str(doc) for doc in documents]
                
            vectorizer = CountVectorizer(
                ngram_range=self.n_gram_range,
                max_features=15,
                stop_words="english"
            )
            
            try:
                X = vectorizer.fit_transform(documents)
                words = vectorizer.get_feature_names_out()
                counts = X.sum(axis=0).A1
                
                # Ensure we have results
                if len(words) == 0:
                    return [("no_keywords_found", 1.0)]
                    
                return sorted(
                    zip(words, counts),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]  # Top 10 keywords
                
            except ValueError as e:
                logger.warning(f"Vectorization failed: {e}")
                # Try with a less strict regex pattern for tokenization
                custom_analyzer = CountVectorizer(
                    token_pattern=r"[a-zA-Z0-9]+",
                    max_features=10,
                    stop_words="english"
                ).build_analyzer()
                
                # Extract words using custom analyzer
                all_words = []
                for doc in documents:
                    all_words.extend(custom_analyzer(doc))
                
                word_counts = Counter(all_words)
                return sorted(
                    word_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
                
        except Exception as e:
            logger.warning(f"Basic keyword extraction failed: {e}")
            return [("keyword_extraction_failed", 1.0)] 