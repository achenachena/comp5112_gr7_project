"""
Keyword Matching Search Algorithm for E-commerce Product Search

This module implements a traditional keyword-based search algorithm that matches
query terms directly against product titles and descriptions.
"""

import re
from typing import List, Dict, Any
from collections import Counter
import math

from ecommerce_search.config import AlgorithmConfig


class KeywordSearch:
    """
    Traditional keyword matching search algorithm.

    This algorithm performs exact and partial keyword matching against product data,
    ranking results based on keyword frequency and exact matches.
    """

    def __init__(self, case_sensitive: bool = None, exact_match_weight: float = None):
        """
        Initialize the keyword search algorithm.

        Args:
            case_sensitive: Whether to perform case-sensitive matching
            exact_match_weight: Weight multiplier for exact keyword matches
        """
        self.case_sensitive = (
            case_sensitive if case_sensitive is not None 
            else AlgorithmConfig.DEFAULT_CASE_SENSITIVE
        )
        self.exact_match_weight = (
            exact_match_weight if exact_match_weight is not None 
            else AlgorithmConfig.DEFAULT_EXACT_MATCH_WEIGHT
        )
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

        # Remove stop words
        tokens = [token for token in tokens if token not in self.stop_words]

        return tokens

    def calculate_keyword_score(self, query_tokens: List[str], product_tokens: List[str]) -> float:
        """
        Calculate relevance score based on keyword matching.

        Args:
            query_tokens: List of query terms
            product_tokens: List of product text tokens

        Returns:
            Relevance score (higher is more relevant)
        """
        if not query_tokens or not product_tokens:
            return 0.0

        # Count token frequencies
        query_counter = Counter(query_tokens)
        product_counter = Counter(product_tokens)

        score = 0.0
        total_query_weight = 0.0

        for query_token, query_freq in query_counter.items():
            # Weight based on query frequency
            query_weight = query_freq

            # Check for exact matches
            if query_token in product_counter:
                exact_matches = product_counter[query_token]
                score += exact_matches * query_weight * self.exact_match_weight

            # Check for partial matches (substring matching)
            partial_matches = 0
            for product_token in product_counter:
                if query_token in product_token or product_token in query_token:
                    # Lower weight for partial matches
                    partial_match_weight = AlgorithmConfig.DEFAULT_PARTIAL_MATCH_WEIGHT
                    partial_matches += product_counter[product_token] * partial_match_weight

            score += partial_matches * query_weight
            total_query_weight += query_weight

        # Normalize by query weight and product length
        if total_query_weight > 0:
            score = score / (total_query_weight * math.log(len(product_tokens) + 1))

        return score

    def search(self, query: str, products: List[Dict[str, Any]],
               limit: int = None) -> List[Dict[str, Any]]:
        """
        Search products using keyword matching algorithm.

        Args:
            query: Search query string
            products: List of product dictionaries
            limit: Maximum number of results to return

        Returns:
            List of products sorted by relevance score
        """
        if not query or not products:
            return []

        # Get limit from config if not provided
        if limit is None:
            limit = AlgorithmConfig.DEFAULT_SEARCH_LIMIT

        # Preprocess query
        query_tokens = self.preprocess_text(query)
        if not query_tokens:
            return []

        # Calculate scores for each product
        scored_products = []

        for product in products:
            # Combine title and description for search
            searchable_text = ""
            if 'title' in product:
                searchable_text += product['title'] + " "
            if 'description' in product:
                searchable_text += product.get('description', '') + " "
            if 'category' in product:
                searchable_text += product.get('category', '') + " "

            # Preprocess product text
            product_tokens = self.preprocess_text(searchable_text)

            # Calculate relevance score
            score = self.calculate_keyword_score(query_tokens, product_tokens)

            if score > 0:
                scored_products.append({
                    'product': product,
                    'score': score,
                    'matched_terms': [token for token in query_tokens if token in product_tokens]
                })

        # Sort by score (descending) and return top results
        scored_products.sort(key=lambda x: x['score'], reverse=True)

        # Return formatted results
        results = []
        for item in scored_products[:limit]:
            result = item['product'].copy()
            result['relevance_score'] = item['score']
            result['matched_terms'] = item['matched_terms']
            result['algorithm'] = 'keyword_matching'
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
            'algorithm': 'keyword_matching',
            'parameters': {
                'case_sensitive': self.case_sensitive,
                'exact_match_weight': self.exact_match_weight,
                'stop_words_count': len(self.stop_words)
            }
        }

        return stats
