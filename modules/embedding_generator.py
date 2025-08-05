
import logging
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from .text_preprocessing import TextPreprocessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check for device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class EmbeddingGenerator:
    def __init__(self, embedding_type, fine_tune=False):
        self.embedding_type = embedding_type
        self.preprocessor = TextPreprocessor()
        self.fine_tune = fine_tune
        
        # Define model mapping with fallbacks
        self.model_map = {
            "sentence-bert": [
                "sentence-transformers/all-MiniLM-L6-v2",
                "distilbert-base-nli-stsb-mean-tokens",
                "bert-base-nli-mean-tokens"
            ],
            "sentence-roberta": [
                "sentence-transformers/all-distilroberta-v1",
                "roberta-base-nli-stsb-mean-tokens",
                "distilroberta-base-paraphrase-v1"
            ]
        }
        
        if embedding_type not in self.model_map:
            logger.warning(f"Unknown embedding type: {embedding_type}. Defaulting to sentence-bert.")
            embedding_type = "sentence-bert"
        
        # Try loading models with fallbacks
        self.model = self._load_model_with_fallbacks(embedding_type)
        logger.info(f"Successfully loaded {embedding_type} model on {device}")

    def _load_model_with_fallbacks(self, embedding_type):
        """Attempt to load models with fallbacks if initial model fails"""
        errors = []
        
        for model_name in self.model_map[embedding_type]:
            try:
                logger.info(f"Attempting to load model: {model_name}")
                model = SentenceTransformer(model_name)
                model.to(device)
                return model
            except Exception as e:
                error_msg = f"Failed to load model {model_name}: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # If all models failed, raise an error with details
        error_details = "\n".join(errors)
        logger.error(f"All models failed to load. Details:\n{error_details}")
        
        # Create a dummy model that returns zeros (as a last resort)
        logger.warning("Creating fallback dummy encoder that will return zero embeddings")
        return DummyEncoder()

    def generate_embeddings(self, texts):
        """Generate embeddings for a list of texts with error handling"""
        if not texts:
            logger.warning("Empty text list provided to generate_embeddings")
            embedding_dim = self.model.get_sentence_embedding_dimension() if hasattr(self.model, 'get_sentence_embedding_dimension') else 384
            return np.zeros((1, embedding_dim))
        
        processed_texts = []
        for text in texts:
            if isinstance(text, str) and text.strip():
                processed_texts.append(self.preprocessor.preprocess_text(text))
            else:
                processed_texts.append("unknown")
                
        if not processed_texts:
            logger.warning("No valid texts after preprocessing")
            embedding_dim = self.model.get_sentence_embedding_dimension() if hasattr(self.model, 'get_sentence_embedding_dimension') else 384
            return np.zeros((1, embedding_dim))

        try:
            batch_size = 32
            all_embeddings = []
            
            for i in range(0, len(processed_texts), batch_size):
                batch = processed_texts[i:i + batch_size]
                try:
                    logger.info(f"Processing batch {i//batch_size + 1}/{(len(processed_texts)-1)//batch_size + 1} with {len(batch)} texts")
                    batch_embeddings = self.model.encode(batch, device=device)
                    all_embeddings.append(batch_embeddings)
                except Exception as e:
                    logger.error(f"Error encoding batch {i//batch_size + 1}: {str(e)}")
                    # Fallback: generate zeros for this batch
                    embedding_dim = self.model.get_sentence_embedding_dimension() if hasattr(self.model, 'get_sentence_embedding_dimension') else 384
                    batch_embeddings = np.zeros((len(batch), embedding_dim))
                    all_embeddings.append(batch_embeddings)
            
            return np.vstack(all_embeddings)
            
        except Exception as e:
            logger.error(f"Error in generate_embeddings: {str(e)}")
            # Return zeros as fallback
            embedding_dim = self.model.get_sentence_embedding_dimension() if hasattr(self.model, 'get_sentence_embedding_dimension') else 384
            return np.zeros((len(processed_texts), embedding_dim))

class DummyEncoder:
    """Fallback encoder that returns zero embeddings when models fail to load"""
    def __init__(self, embedding_dim=384):
        self.embedding_dim = embedding_dim
        logger.warning(f"Using DummyEncoder with dimension {embedding_dim}")
    
    def get_sentence_embedding_dimension(self):
        return self.embedding_dim
        
    def encode(self, texts, device=None):
        if isinstance(texts, str):
            return np.zeros(self.embedding_dim)
        return np.zeros((len(texts), self.embedding_dim))
    
    def to(self, device):
        # Do nothing
        return self
