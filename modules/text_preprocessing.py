import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextPreprocessor:
    def __init__(self):
        # Download required NLTK resources
        for resource in ['punkt', 'averaged_perceptron_tagger', 'stopwords', 'wordnet']:
            try:
                nltk.download(resource, quiet=True)
            except Exception as e:
                logger.warning(f"Could not download {resource}: {e}")
        
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()

    def preprocess_text(self, text):
        if not isinstance(text, str):
            return "unknown"

        try:
            text = text.lower()
            text = re.sub(r"[^a-zA-Z\s]", "", text)
            tokens = word_tokenize(text)

            try:
                pos_tags = pos_tag(tokens)
                filtered_tokens = [
                    self.lemmatizer.lemmatize(token)
                    for token, pos in pos_tags
                    if pos.startswith(("N", "V", "J", "R"))  # Nouns, Verbs, Adjectives, Adverbs
                ]
            except LookupError:
                filtered_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]

            filtered_tokens = [token for token in filtered_tokens if token not in self.stop_words]
            return " ".join(filtered_tokens) if filtered_tokens else "unknown"
        except Exception as e:
            logger.error(f"Error in text preprocessing: {e}")
            return "unknown" 