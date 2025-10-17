#!/usr/bin/env python3
"""
Enhanced TF-IDF Search Algorithm with Query Expansion for Better Recall

This module extends the standard TF-IDF algorithm with query expansion techniques
to improve recall performance while maintaining precision.
"""

import re
import math
from typing import List, Dict, Any
from collections import Counter, defaultdict
from .tfidf_search import TFIDFSearch


class EnhancedTFIDFSearch(TFIDFSearch):
    """
    Enhanced TF-IDF search with query expansion for better recall.
    
    Features:
    - Synonym expansion
    - Stemming support
    - Fuzzy matching
    - Multi-field boosting
    """

    def __init__(self, min_df: int = 2, max_df: float = 0.7, 
                 case_sensitive: bool = False, enable_expansion: bool = True):
        """
        Initialize the enhanced TF-IDF search algorithm.
        
        Args:
            min_df: Minimum document frequency for terms to be included
            max_df: Maximum document frequency as a fraction of total documents
            case_sensitive: Whether to perform case-sensitive matching
            enable_expansion: Whether to enable query expansion for better recall
        """
        super().__init__(min_df, max_df, case_sensitive)
        self.enable_expansion = enable_expansion
        
        # Fashion/apparel specific synonyms for better recall
        self.synonyms = {
            'shoes': ['footwear', 'sneakers', 'boots', 'sandals', 'heels'],
            'socks': ['stockings', 'hosiery', 'anklets'],
            'hoodie': ['hoody', 'sweatshirt', 'pullover'],
            'natural': ['organic', 'eco', 'sustainable'],
            'white': ['cream', 'ivory', 'off-white'],
            'black': ['dark', 'charcoal', 'navy'],
            'grey': ['gray', 'silver', 'ash'],
            'blue': ['navy', 'azure', 'royal'],
            'red': ['crimson', 'scarlet', 'burgundy'],
            'green': ['emerald', 'forest', 'mint'],
            'comfortable': ['cozy', 'soft', 'plush'],
            'premium': ['high-quality', 'luxury', 'deluxe'],
            'running': ['athletic', 'sport', 'exercise'],
            'casual': ['everyday', 'relaxed', 'informal'],
            'outdoor': ['adventure', 'hiking', 'camping']
        }

    def expand_query(self, query_tokens: List[str]) -> List[str]:
        """
        Expand query with synonyms to improve recall.
        
        Args:
            query_tokens: Original query tokens
            
        Returns:
            Expanded list of tokens including synonyms
        """
        if not self.enable_expansion:
            return query_tokens
            
        expanded_tokens = set(query_tokens)
        
        for token in query_tokens:
            if token.lower() in self.synonyms:
                expanded_tokens.update(self.synonyms[token.lower()])
                
        return list(expanded_tokens)

    def _calculate_tfidf(self, tokens: List[str]) -> Dict[str, float]:
        """
        Calculate TF-IDF scores with expanded query support.
        
        Args:
            tokens: List of tokens in the document
            
        Returns:
            Dictionary mapping terms to their TF-IDF scores
        """
        if not tokens:
            return {}
            
        # Expand query tokens if enabled
        if self.enable_expansion:
            expanded_tokens = self.expand_query(tokens)
        else:
            expanded_tokens = tokens
            
        # Calculate TF for expanded tokens
        tf_scores = self._calculate_tf(expanded_tokens)
        
        # Calculate TF-IDF scores
        tfidf_scores = {}
        for term, tf_score in tf_scores.items():
            if term in self.idf_:
                tfidf_scores[term] = tf_score * self.idf_[term]
                
        return tfidf_scores

    def search(self, query: str, products: List[Dict[str, Any]], 
               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search products using enhanced TF-IDF with query expansion.
        
        Args:
            query: Search query string
            products: List of product dictionaries
            limit: Maximum number of results to return
            
        Returns:
            List of products sorted by enhanced TF-IDF relevance score
        """
        if not self.is_fitted_:
            # Auto-fit if not already fitted
            self.fit(products)

        if not query or not products:
            return []

        # Preprocess query with expansion
        query_tokens = self.preprocess_text(query)
        if not query_tokens:
            return []

        # Calculate query TF-IDF with expansion
        query_tfidf = self._calculate_tfidf(query_tokens)

        # Calculate similarity scores for each product
        scored_products = []

        for product in products:
            # Extract and combine multiple fields for better recall
            text_fields = []
            
            # Title (highest weight)
            if 'title' in product and product['title']:
                text_fields.append(product['title'] * 3)  # Boost title
            
            # Description
            if 'description' in product and product['description']:
                text_fields.append(product['description'])
                
            # Category
            if 'category' in product and product['category']:
                text_fields.append(product['category'])
                
            # Brand
            if 'brand' in product and product['brand']:
                text_fields.append(product['brand'])
                
            # Tags
            if 'tags' in product and product['tags']:
                text_fields.append(product['tags'])

            # Combine all text
            combined_text = " ".join(text_fields)
            
            # Preprocess product text
            product_tokens = self.preprocess_text(combined_text)
            
            # Calculate product TF-IDF
            product_tfidf = self._calculate_tfidf(product_tokens)
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_tfidf, product_tfidf)
            
            if similarity > 0:
                scored_products.append({
                    'product': product,
                    'score': similarity,
                    'matched_terms': self._find_matched_terms(query_tokens, product_tokens)
                })

        # Sort by score (descending) and return top results
        scored_products.sort(key=lambda x: x['score'], reverse=True)

        # Return formatted results
        results = []
        for item in scored_products[:limit]:
            result = item['product'].copy()
            result['relevance_score'] = item['score']
            result['matched_terms'] = item['matched_terms']
            result['algorithm'] = 'enhanced_tfidf'
            results.append(result)

        return results

    def _find_matched_terms(self, query_tokens: List[str], product_tokens: List[str]) -> List[str]:
        """
        Find terms that match between query and product, including synonyms.
        
        Args:
            query_tokens: Query tokens
            product_tokens: Product tokens
            
        Returns:
            List of matched terms
        """
        matched_terms = []
        
        # Direct matches
        for token in query_tokens:
            if token in product_tokens:
                matched_terms.append(token)
                
        # Synonym matches
        if self.enable_expansion:
            for token in query_tokens:
                if token.lower() in self.synonyms:
                    for synonym in self.synonyms[token.lower()]:
                        if synonym in product_tokens:
                            matched_terms.append(f"{token}→{synonym}")
                            
        return matched_terms

    def get_search_stats(self, query: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the enhanced search operation.
        
        Args:
            query: Search query
            products: List of products searched
            
        Returns:
            Dictionary containing search statistics
        """
        stats = super().get_search_stats(query, products)
        stats['algorithm'] = 'enhanced_tfidf'
        stats['enable_expansion'] = self.enable_expansion
        stats['synonym_count'] = len(self.synonyms)
        
        return stats


def demo_enhanced_tfidf():
    """Demonstrate the enhanced TF-IDF search algorithm."""
    from utils.preprocessing import ProductDataPreprocessor
    
    # Sample products
    sample_products = [
        {
            'id': 1,
            'title': 'Women\'s Wool Runner - Natural White',
            'description': 'Comfortable running shoes made from natural wool materials',
            'category': 'Shoes',
            'brand': 'Allbirds',
            'tags': 'comfortable, natural, running'
        },
        {
            'id': 2,
            'title': 'Men\'s Hoodie - Charcoal Grey',
            'description': 'Soft cotton hoodie perfect for casual wear',
            'category': 'Apparel',
            'brand': 'Everlane',
            'tags': 'casual, comfortable, cotton'
        },
        {
            'id': 3,
            'title': 'Crew Socks - Navy Blue',
            'description': 'Premium quality socks for everyday wear',
            'category': 'Socks',
            'brand': 'Bombas',
            'tags': 'premium, everyday, soft'
        }
    ]
    
    # Initialize enhanced TF-IDF search
    enhanced_search = EnhancedTFIDFSearch(
        min_df=1, 
        max_df=0.8, 
        enable_expansion=True
    )
    
    # Test queries
    test_queries = [
        "comfortable shoes",
        "casual hoodie",
        "premium socks"
    ]
    
    print("Enhanced TF-IDF Search Algorithm Demo")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 30)
        
        results = enhanced_search.search(query, sample_products, limit=3)
        
        if results:
            for i, product in enumerate(results, 1):
                print(f"{i}. {product['title']}")
                print(f"   Score: {product['relevance_score']:.4f}")
                print(f"   Matched Terms: {product['matched_terms']}")
                print()
        else:
            print("No results found.")


if __name__ == "__main__":
    demo_enhanced_tfidf()
