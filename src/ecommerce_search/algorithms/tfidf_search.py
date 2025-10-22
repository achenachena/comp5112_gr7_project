"""
TF-IDF (Term Frequency-Inverse Document Frequency) Search Algorithm for E-commerce

This module implements a TF-IDF based search algorithm that uses statistical
methods to determine the relevance of products based on term frequency and
document frequency across the entire product corpus.
"""

import re
import math
from typing import List, Dict, Any
from collections import Counter, defaultdict


class TFIDFSearch:
    """
    TF-IDF based search algorithm for e-commerce products.

    This algorithm uses Term Frequency-Inverse Document Frequency to calculate
    relevance scores, giving higher weights to terms that are frequent in a
    document but rare across the entire corpus.
    """

    def __init__(self, min_df: int = 1, max_df: float = 0.95, case_sensitive: bool = False):
        """
        Initialize the TF-IDF search algorithm.

        Args:
            min_df: Minimum document frequency for terms to be included
            max_df: Maximum document frequency as a fraction of total documents
            case_sensitive: Whether to perform case-sensitive matching
        """
        self.min_df = min_df
        self.max_df = max_df
        self.case_sensitive = case_sensitive
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if',
            'up', 'out', 'many', 'then', 'them', 'can', 'only', 'other',
            'new', 'some', 'could', 'now', 'than', 'first', 'been', 'call',
            'who', 'find', 'long', 'down', 'day', 'did', 'get',
            'come', 'made', 'may', 'part'
        }

        # Model components (initialized during fit)
        self.vocabulary_ = None
        self.idf_ = None
        self.document_count_ = 0
        self.is_fitted_ = False

    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text by tokenizing, removing punctuation, and filtering stop words.

        Args:
            text: Input text to preprocess

        Returns:
            List of cleaned tokens
        """
        if not text:
            return []

        # Convert to lowercase if not case sensitive
        if not self.case_sensitive:
            text = text.lower()

        # Remove punctuation and split into tokens
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()

        # Remove stop words and short tokens
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 1]

        return tokens

    def fit(self, products: List[Dict[str, Any]]):
        """
        Fit the TF-IDF model to the product corpus.

        Args:
            products: List of product dictionaries to build the model from
        """
        if not products:
            raise ValueError("Cannot fit model with empty product list")

        # Extract and preprocess all documents
        documents = []
        for product in products:
            # Combine all text fields - handle social media data
            text = ""
            if 'title' in product:
                text += product['title'] + " "
            if 'description' in product:
                text += product.get('description', '') + " "
            if 'product_name' in product:
                text += product.get('product_name', '') + " "
            if 'brand' in product:
                text += product.get('brand', '') + " "
            if 'category' in product:
                text += product.get('category', '') + " "

            tokens = self.preprocess_text(text)
            documents.append(tokens)

        self.document_count_ = len(documents)

        # Build vocabulary and calculate document frequencies
        term_doc_count = defaultdict(int)
        all_terms = set()

        for doc_tokens in documents:
            unique_terms = set(doc_tokens)
            for term in unique_terms:
                term_doc_count[term] += 1
            all_terms.update(unique_terms)

        # Filter vocabulary based on min_df and max_df
        max_doc_count = int(self.max_df * self.document_count_)
        self.vocabulary_ = {
            term: idx for idx, term in enumerate(
                sorted([term for term in all_terms
                       if self.min_df <= term_doc_count[term] <= max_doc_count])
            )
        }

        # Calculate IDF scores
        self.idf_ = {}
        for term, doc_count in term_doc_count.items():
            if term in self.vocabulary_:
                # IDF = log(N / df) where N is total documents, df is document frequency
                self.idf_[term] = math.log(self.document_count_ / doc_count)

        self.is_fitted_ = True

    def _calculate_tf(self, tokens: List[str]) -> Dict[str, float]:
        """
        Calculate term frequency for a document.

        Args:
            tokens: List of tokens in the document

        Returns:
            Dictionary mapping terms to their TF scores
        """
        if not tokens:
            return {}

        token_count = Counter(tokens)
        # total_tokens = len(tokens)

        # Calculate TF using logarithmic scaling: 1 + log(count)
        tf_scores = {}
        for term, count in token_count.items():
            if term in self.vocabulary_:
                tf_scores[term] = 1 + math.log(count)

        return tf_scores

    def _calculate_tfidf(self, tokens: List[str]) -> Dict[str, float]:
        """
        Calculate TF-IDF scores for a document.

        Args:
            tokens: List of tokens in the document

        Returns:
            Dictionary mapping terms to their TF-IDF scores
        """
        if not tokens or not self.is_fitted_:
            return {}

        # Count term frequencies
        term_counts = Counter(tokens)
        tfidf_scores = {}

        for term, count in term_counts.items():
            if term in self.vocabulary_ and term in self.idf_:
                # TF: 1 + log(count)
                tf = 1 + math.log(count)
                # TF-IDF = TF * IDF
                tfidf_scores[term] = tf * self.idf_[term]

        return tfidf_scores

    def _cosine_similarity(self, query_tfidf: Dict[str, float],
                           doc_tfidf: Dict[str, float]) -> float:
        """
        Calculate cosine similarity between query and document TF-IDF vectors.

        Args:
            query_tfidf: TF-IDF scores for query
            doc_tfidf: TF-IDF scores for document

        Returns:
            Cosine similarity score
        """
        if not query_tfidf or not doc_tfidf:
            return 0.0

        # Get all terms present in either vector
        all_terms = set(query_tfidf.keys()) | set(doc_tfidf.keys())

        if not all_terms:
            return 0.0

        # Calculate dot product and magnitudes
        dot_product = 0.0
        query_magnitude = 0.0
        doc_magnitude = 0.0

        for term in all_terms:
            query_score = query_tfidf.get(term, 0.0)
            doc_score = doc_tfidf.get(term, 0.0)

            dot_product += query_score * doc_score
            query_magnitude += query_score ** 2
            doc_magnitude += doc_score ** 2

        # Calculate cosine similarity
        if query_magnitude == 0 or doc_magnitude == 0:
            return 0.0

        similarity = dot_product / (math.sqrt(query_magnitude) * math.sqrt(doc_magnitude))
        return similarity

    def search(self, query: str, products: List[Dict[str, Any]],
               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search products using TF-IDF algorithm.

        Args:
            query: Search query string
            products: List of product dictionaries
            limit: Maximum number of results to return

        Returns:
            List of products sorted by TF-IDF relevance score
        """
        if not self.is_fitted_:
            # Auto-fit if not already fitted
            self.fit(products)

        if not query or not products:
            return []

        # Preprocess query
        query_tokens = self.preprocess_text(query)
        if not query_tokens:
            return []

        # Calculate query TF-IDF
        query_tfidf = self._calculate_tfidf(query_tokens)

        # Calculate similarity scores for each product
        scored_products = []

        for product in products:
            # Extract product text - handle social media data
            text = ""
            if 'title' in product:
                text += product['title'] + " "
            if 'description' in product:
                text += product.get('description', '') + " "
            if 'product_name' in product:
                text += product.get('product_name', '') + " "
            if 'brand' in product:
                text += product.get('brand', '') + " "
            if 'category' in product:
                text += product.get('category', '') + " "

            # Preprocess and calculate TF-IDF for product
            product_tokens = self.preprocess_text(text)
            product_tfidf = self._calculate_tfidf(product_tokens)

            # Calculate cosine similarity
            similarity_score = self._cosine_similarity(query_tfidf, product_tfidf)

            if similarity_score > 0:
                # Find matched terms (terms present in both query and product)
                matched_terms = []
                for term in query_tokens:
                    if term in product_tokens and term in self.vocabulary_:
                        matched_terms.append(term)

                scored_products.append({
                    'product': product,
                    'score': similarity_score,
                    'matched_terms': matched_terms,
                    'query_tfidf': query_tfidf,
                    'product_tfidf': product_tfidf
                })

        # Sort by similarity score (descending)
        scored_products.sort(key=lambda x: x['score'], reverse=True)

        # Return formatted results
        results = []
        for item in scored_products[:limit]:
            result = item['product'].copy()
            result['relevance_score'] = item['score']
            result['matched_terms'] = item['matched_terms']
            result['algorithm'] = 'tfidf'
            results.append(result)

        return results

    def get_search_stats(self, query: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the search operation.

        Args:
            query: Search query
            products: List of products searched

        Returns:
            Dictionary containing search statistics
        """
        query_tokens = self.preprocess_text(query)

        stats = {
            'query': query,
            'query_tokens': query_tokens,
            'total_products': len(products),
            'algorithm': 'tfidf',
            'is_fitted': self.is_fitted_,
            'vocabulary_size': len(self.vocabulary_) if self.vocabulary_ else 0,
            'document_count': self.document_count_,
            'parameters': {
                'min_df': self.min_df,
                'max_df': self.max_df,
                'case_sensitive': self.case_sensitive
            }
        }

        return stats
