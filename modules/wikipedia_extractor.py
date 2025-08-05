import re
import time
import logging
import wikipedia
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from .text_preprocessing import TextPreprocessor
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WikiCorpusExtractor:
    def __init__(self, class_descriptions):
        self.class_descriptions = class_descriptions
        self.preprocessor = TextPreprocessor()
        self.max_depth = 4
        self.max_pages_per_term = 5
        self.visited_pages = set()
        self.current_domain = None

    def extract_key_terms(self, description):
        noun_phrases = re.findall(r'([A-Z][a-z]+ [a-z]+ [a-z]+|[A-Z][a-z]+ [a-z]+)', description)
        noun_phrases = [phrase.lower() for phrase in noun_phrases]
        tokens = word_tokenize(description.lower())
        pos_tags = pos_tag(tokens)
        nouns = [token for token, pos in pos_tags if pos.startswith('N') and token not in self.preprocessor.stop_words]
        key_terms = list(set(noun_phrases + nouns))
        if self.current_domain and self.current_domain.lower() not in key_terms:
            key_terms.append(self.current_domain.lower())
        return key_terms
    
    def get_expanded_terms(self, description):
        """Enhanced term extraction with more linguistic patterns"""
        patterns = [
            r'([A-Z][a-z]+(?:\s[A-Za-z][a-z]+)+)',  # Multi-word phrases
            r'\b[A-Z][a-z]+\b',  # Single proper nouns
            r'\b\w{4,}s\b',  # Plural nouns
            r'\w+ly\b',  # Adverbs
            r'\b\w+ing\b'  # Gerunds
        ]
        
        terms = []
        for pattern in patterns:
            terms.extend(re.findall(pattern, description))
        
        if self.current_domain and self.current_domain.lower() not in terms:
            terms.append(self.current_domain.lower())
            
        return list(set(term.lower() for term in terms if len(term.split()) <= 3))

    def fetch_wikipedia_content(self, query):
        try:
            search_results = wikipedia.search(query, results=5)
            if not search_results:
                return []

            corpus_data = []
            queue = [(result, 0) for result in search_results if result not in self.visited_pages]
            self.visited_pages.update([result for result, _ in queue])

            while queue and len(corpus_data) < self.max_pages_per_term:
                current_page, current_depth = queue.pop(0)
                if current_depth >= self.max_depth:
                    continue

                try:
                    page = wikipedia.page(current_page, auto_suggest=False)
                    if "may refer to:" in page.content[:500]:
                        continue

                    processed_content = self.preprocessor.preprocess_text(page.content)
                    corpus_data.append(processed_content)

                    if current_depth < self.max_depth - 1 and len(corpus_data) < self.max_pages_per_term:
                        links = page.links[:5]
                        for link in links:
                            if link not in self.visited_pages and len(corpus_data) < self.max_pages_per_term:
                                queue.append((link, current_depth + 1))
                                self.visited_pages.add(link)

                except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError):
                    continue

                time.sleep(0.3)

            return corpus_data[:self.max_pages_per_term]
        except Exception as e:
            logger.error(f"Error fetching Wikipedia content: {e}")
            return []

    def post_process_corpus(self, corpus):
        filtered_corpus = []
        key_terms = self.extract_key_terms(self.class_descriptions[self.current_domain])
        for text in corpus:
            sentences = sent_tokenize(text)
            for sentence in sentences:
                if len(sentence.split()) >= 10 and any(term in sentence.lower() for term in key_terms):
                    filtered_corpus.append(sentence)
        return " ".join(filtered_corpus)

    def extract_corpus(self):
        corpus = {}
        total_terms = sum(len(self.extract_key_terms(desc)) for desc in self.class_descriptions.values())
        
        with tqdm(total=len(self.class_descriptions), desc="Processing domains", position=0) as domain_pbar:
            for label, description in self.class_descriptions.items():
                self.current_domain = label
                key_terms = self.extract_key_terms(description)
                domain_corpus_data = []
                self.visited_pages = set()

                with tqdm(total=len(key_terms), desc=f"Extracting {label}", position=1, leave=False) as term_pbar:
                    for term in key_terms:
                        search_query = f"{label} {term}" if term != label.lower() else label
                        term_data = self.fetch_wikipedia_content(search_query)
                        domain_corpus_data.extend(term_data)
                        time.sleep(0.5)
                        term_pbar.update(1)

                if domain_corpus_data:
                    corpus[label] = self.post_process_corpus(domain_corpus_data)
                domain_pbar.update(1)
        
        return corpus 