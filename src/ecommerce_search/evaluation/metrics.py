"""
Evaluation Metrics for Search Algorithm Comparison

This module provides various metrics to evaluate and compare the performance
of different search algorithms including precision, recall, F1-score, and NDCG.
"""

import math
from typing import List, Dict, Any, Optional
from collections import defaultdict


class SearchMetrics:
    """
    Class for calculating various search evaluation metrics.
    """

    @staticmethod
    def precision_at_k(relevant_items: set, retrieved_items: List[Any], k: int) -> float:
        """
        Calculate Precision@K metric.

        Args:
            relevant_items: Set of relevant item IDs
            retrieved_items: List of retrieved items (ordered by relevance)
            k: Number of top results to consider

        Returns:
            Precision@K score
        """
        if k <= 0:
            return 0.0

        top_k = retrieved_items[:k]
        relevant_in_top_k = sum(1 for item in top_k if item in relevant_items)

        return relevant_in_top_k / k if k > 0 else 0.0

    @staticmethod
    def recall_at_k(relevant_items: set, retrieved_items: List[Any], k: int) -> float:
        """
        Calculate Recall@K metric.

        Args:
            relevant_items: Set of relevant item IDs
            retrieved_items: List of retrieved items (ordered by relevance)
            k: Number of top results to consider

        Returns:
            Recall@K score
        """
        if not relevant_items:
            return 0.0

        top_k = retrieved_items[:k]
        relevant_in_top_k = sum(1 for item in top_k if item in relevant_items)

        return relevant_in_top_k / len(relevant_items)

    @staticmethod
    def f1_score_at_k(relevant_items: set, retrieved_items: List[Any], k: int) -> float:
        """
        Calculate F1-Score@K metric.

        Args:
            relevant_items: Set of relevant item IDs
            retrieved_items: List of retrieved items (ordered by relevance)
            k: Number of top results to consider

        Returns:
            F1-Score@K
        """
        precision = SearchMetrics.precision_at_k(relevant_items, retrieved_items, k)
        recall = SearchMetrics.recall_at_k(relevant_items, retrieved_items, k)

        if precision + recall == 0:
            return 0.0

        return 2 * (precision * recall) / (precision + recall)

    @staticmethod
    def ndcg_at_k(relevant_items: set, retrieved_items: List[Any], k: int,
                  relevance_scores: Dict[Any, float] = None) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain (NDCG)@K.

        Args:
            relevant_items: Set of relevant item IDs
            retrieved_items: List of retrieved items (ordered by relevance)
            k: Number of top results to consider
            relevance_scores: Dictionary mapping items to their relevance scores

        Returns:
            NDCG@K score
        """
        if k <= 0:
            return 0.0

        # Default relevance scores (binary: 1 for relevant, 0 for irrelevant)
        if relevance_scores is None:
            relevance_scores = {item: 1.0 for item in relevant_items}

        top_k = retrieved_items[:k]

        # Calculate DCG
        dcg = 0.0
        for i, item in enumerate(top_k):
            relevance = relevance_scores.get(item, 0.0)
            if relevance > 0:
                dcg += relevance / math.log2(i + 2)  # i+2 because log2(1) = 0

        # Calculate IDCG (Ideal DCG)
        ideal_relevances = sorted([relevance_scores.get(item, 0.0) for item in relevant_items],
                                 reverse=True)[:k]
        idcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(ideal_relevances))

        # Calculate NDCG
        return dcg / idcg if idcg > 0 else 0.0

    @staticmethod
    def mean_average_precision(relevant_items: set, retrieved_items: List[Any]) -> float:
        """
        Calculate Mean Average Precision (MAP).

        Args:
            relevant_items: Set of relevant item IDs
            retrieved_items: List of retrieved items (ordered by relevance)

        Returns:
            MAP score
        """
        if not relevant_items:
            return 0.0

        relevant_count = 0
        precision_sum = 0.0

        for i, item in enumerate(retrieved_items):
            if item in relevant_items:
                relevant_count += 1
                precision = relevant_count / (i + 1)
                precision_sum += precision

        return precision_sum / len(relevant_items) if relevant_items else 0.0

    @staticmethod
    def reciprocal_rank(relevant_items: set, retrieved_items: List[Any]) -> float:
        """
        Calculate Reciprocal Rank (RR).

        Args:
            relevant_items: Set of relevant item IDs
            retrieved_items: List of retrieved items (ordered by relevance)

        Returns:
            Reciprocal rank score
        """
        for i, item in enumerate(retrieved_items):
            if item in relevant_items:
                return 1.0 / (i + 1)

        return 0.0

    @staticmethod
    def calculate_comprehensive_metrics(
        relevant_items: set,
        retrieved_items: List[Any],
        k_values: Optional[List[int]] = None,
        relevance_scores: Dict[Any, float] = None,
    ) -> Dict[str, float]:
        """
        Calculate comprehensive evaluation metrics for a search result.

        Args:
            relevant_items: Set of relevant item IDs
            retrieved_items: List of retrieved items (ordered by relevance)
            k_values: List of K values for P@K, R@K, F1@K, NDCG@K
            relevance_scores: Dictionary mapping items to their relevance scores

        Returns:
            Dictionary containing all calculated metrics
        """
        metrics = {}

        if k_values is None:
            k_values = [1, 3, 5, 10]

        # Basic metrics
        metrics['map'] = SearchMetrics.mean_average_precision(relevant_items, retrieved_items)
        metrics['mrr'] = SearchMetrics.reciprocal_rank(relevant_items, retrieved_items)

        # Metrics at different K values
        for k in k_values:
            metrics[f'precision@{k}'] = SearchMetrics.precision_at_k(
                relevant_items, retrieved_items, k)
            metrics[f'recall@{k}'] = SearchMetrics.recall_at_k(
                relevant_items, retrieved_items, k)
            metrics[f'f1@{k}'] = SearchMetrics.f1_score_at_k(
                relevant_items, retrieved_items, k)
            metrics[f'ndcg@{k}'] = SearchMetrics.ndcg_at_k(
                relevant_items, retrieved_items, k, relevance_scores)

        return metrics


class RelevanceJudgment:
    """
    Helper class for managing relevance judgments and ground truth data.
    """

    def __init__(self):
        self.judgments = defaultdict(dict)  # query -> {item_id: relevance_score}

    def add_judgment(self, query: str, item_id: Any, relevance_score: float):
        """
        Add a relevance judgment for a query-item pair.

        Args:
            query: Search query
            item_id: Item identifier
            relevance_score: Relevance score (0-1, where 1 is most relevant)
        """
        self.judgments[query][item_id] = relevance_score

    def get_relevant_items(self, query: str, threshold: float = 0.5) -> set:
        """
        Get set of relevant items for a query above the threshold.

        Args:
            query: Search query
            threshold: Minimum relevance score threshold

        Returns:
            Set of relevant item IDs
        """
        if query not in self.judgments:
            return set()

        return {item_id for item_id, score in self.judgments[query].items()
                if score >= threshold}

    def get_relevance_scores(self, query: str) -> Dict[Any, float]:
        """
        Get relevance scores for all items for a query.

        Args:
            query: Search query

        Returns:
            Dictionary mapping item IDs to relevance scores
        """
        return self.judgments.get(query, {})

    def load_from_ground_truth(self, ground_truth_data: List[Dict[str, Any]]):
        """
        Load relevance judgments from ground truth data.

        Args:
            ground_truth_data: List of dictionaries with 'query', 'item_id', 'relevance' keys
        """
        for item in ground_truth_data:
            query = item.get('query')
            item_id = item.get('item_id')
            relevance = item.get('relevance', 0.0)

            if query and item_id is not None:
                self.add_judgment(query, item_id, relevance)

    def create_synthetic_judgments(self, queries: List[str], products: List[Dict[str, Any]]):
        """
        Create synthetic relevance judgments based on keyword matching.
        This is useful for demonstration purposes when ground truth is not available.

        Args:
            queries: List of test queries
            products: List of products to judge
        """
        import re

        for query in queries:
            query_terms = set(re.findall(r'\w+', query.lower()))

            for product in products:
                # Combine product text - handle social media data
                product_text = ""
                if 'title' in product and product['title']:
                    product_text += str(product['title']) + " "
                if 'description' in product and product.get('description'):
                    product_text += str(product.get('description', '')) + " "
                if 'product_name' in product and product.get('product_name'):
                    product_text += str(product.get('product_name', '')) + " "
                if 'brand' in product and product.get('brand'):
                    product_text += str(product.get('brand', '')) + " "
                if 'category' in product and product.get('category'):
                    product_text += str(product.get('category', '')) + " "

                product_terms = set(re.findall(r'\w+', product_text.lower()))

                # Calculate relevance based on term overlap
                if query_terms and product_terms:
                    overlap = len(query_terms & product_terms)
                    relevance = overlap / len(query_terms)
                else:
                    relevance = 0.0

                # Add some variation based on exact matches
                if query.lower() in product_text.lower():
                    relevance += 0.3
                
                # Boost for social media specific fields
                if 'product_name' in product and query.lower() in product['product_name'].lower():
                    relevance += 0.4
                if 'brand' in product and query.lower() in product['brand'].lower():
                    relevance += 0.3
                if 'category' in product and query.lower() in product['category'].lower():
                    relevance += 0.2

                # Cap at 1.0
                relevance = min(1.0, relevance)

                if relevance > 0:
                    # Use product index as ID if no explicit ID is available
                    product_id = product.get('id', product.get('item_id'))
                    if product_id is None:
                        # Find the index of this product in the products list
                        try:
                            product_id = products.index(product)
                        except ValueError:
                            product_id = len(products)  # Fallback to length
                    self.add_judgment(query, product_id, relevance)

    def create_social_media_judgments(self, queries: List[str], products: List[Dict[str, Any]]):
        """
        Create synthetic relevance judgments specifically for social media content.
        This method accounts for the informal, conversational nature of social media posts.

        Args:
            queries: List of test queries
            products: List of products to judge
        """
        import re
        
        # Social media specific patterns
        informal_patterns = {
            'amazing': ['amazing', 'awesome', 'incredible', 'fantastic', 'brilliant'],
            'good': ['good', 'great', 'nice', 'decent', 'solid'],
            'bad': ['bad', 'terrible', 'awful', 'horrible', 'disappointing'],
            'recommend': ['recommend', 'suggest', 'advise', 'should buy', 'worth it'],
            'review': ['review', 'opinion', 'experience', 'thoughts', 'impression']
        }

        for query in queries:
            query_lower = query.lower()
            query_terms = set(re.findall(r'\w+', query_lower))
            
            # Track relevance scores for this query
            query_relevances = []

            for product in products:
                # Get all text content from social media post
                post_text = ""
                if 'title' in product and product['title']:
                    post_text += str(product['title']) + " "
                if 'description' in product and product.get('description'):
                    post_text += str(product.get('description', '')) + " "
                if 'content' in product and product.get('content'):
                    post_text += str(product.get('content', '')) + " "
                
                post_text_lower = post_text.lower()
                post_terms = set(re.findall(r'\w+', post_text_lower))

                # Start with base relevance
                relevance = 0.0

                # 1. Exact phrase matching (highest priority for social media)
                if query_lower in post_text_lower:
                    relevance += 0.6

                # 2. Product name matching (if extracted)
                if 'product_name' in product and product.get('product_name'):
                    product_name = str(product.get('product_name', '')).lower()
                    if query_lower in product_name:
                        relevance += 0.5
                    # Partial matching in product name
                    elif any(term in product_name for term in query_terms):
                        relevance += 0.3

                # 3. Brand matching
                if 'brand' in product and product.get('brand'):
                    brand = str(product.get('brand', '')).lower()
                    if query_lower in brand:
                        relevance += 0.4
                    elif any(term in brand for term in query_terms):
                        relevance += 0.2

                # 4. Term overlap (balanced for social media)
                if query_terms and post_terms:
                    overlap = len(query_terms & post_terms)
                    term_relevance = (overlap / len(query_terms)) * 0.4  # Increased weight
                    relevance += term_relevance

                # 5. Social media specific indicators
                # Check for informal language patterns
                for pattern_type, words in informal_patterns.items():
                    if any(word in query_lower for word in words):
                        if any(word in post_text_lower for word in words):
                            relevance += 0.1

                # 6. Content type boosts
                if product.get('is_review', False):
                    relevance += 0.2  # Reviews are more relevant
                if product.get('is_recommendation', False):
                    relevance += 0.3  # Recommendations are highly relevant
                if product.get('is_complaint', False):
                    relevance += 0.1  # Complaints can be relevant too

                # 7. Engagement-based relevance
                upvotes = product.get('upvotes', 0)
                comments = product.get('comments_count', 0)
                
                # Popular posts get slight boost
                if upvotes > 50:
                    relevance += 0.1
                elif upvotes > 10:
                    relevance += 0.05
                
                # Posts with discussion get boost
                if comments > 20:
                    relevance += 0.1
                elif comments > 5:
                    relevance += 0.05

                # 8. Sentiment relevance
                sentiment = product.get('sentiment_score', 0)
                if sentiment > 0.5:  # Very positive
                    relevance += 0.1
                elif sentiment > 0.2:  # Positive
                    relevance += 0.05
                elif sentiment < -0.5:  # Very negative
                    relevance += 0.05  # Negative reviews can be relevant

                # 9. Platform-specific relevance
                platform = product.get('platform', '')
                subreddit = product.get('subreddit', '')
                
                # Certain subreddits might be more relevant for product discussions
                product_focused_subreddits = ['BuyItForLife', 'ProductPorn', 'deals', 'consumerism', 'gadgets']
                if subreddit in product_focused_subreddits:
                    relevance += 0.1

                # Cap at 1.0
                relevance = min(1.0, relevance)

                if relevance > 0.05:  # Lower threshold for social media
                    query_relevances.append((product, relevance))

            # Apply realistic ranking distribution
            query_relevances.sort(key=lambda x: x[1], reverse=True)
            
            # Create more realistic distribution for social media
            for i, (product, relevance) in enumerate(query_relevances):
                # Apply ranking penalty (more aggressive for social media)
                rank_penalty = max(0.05, 1.0 - (i * 0.15))  # Steeper decline
                final_relevance = relevance * rank_penalty
                
                # Balanced threshold for social media
                if final_relevance >= 0.12:
                    product_id = product.get('id', product.get('item_id'))
                    if product_id is None:
                        try:
                            product_id = products.index(product)
                        except ValueError:
                            product_id = len(products)
                    self.add_judgment(query, product_id, final_relevance)
