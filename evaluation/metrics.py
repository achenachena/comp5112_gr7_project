"""
Evaluation Metrics for Search Algorithm Comparison

This module provides various metrics to evaluate and compare the performance
of different search algorithms including precision, recall, F1-score, and NDCG.
"""

import math
from typing import List, Dict, Any, Tuple
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
    def calculate_comprehensive_metrics(relevant_items: set, retrieved_items: List[Any], 
                                      k_values: List[int] = [1, 3, 5, 10],
                                      relevance_scores: Dict[Any, float] = None) -> Dict[str, float]:
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
        
        # Basic metrics
        metrics['map'] = SearchMetrics.mean_average_precision(relevant_items, retrieved_items)
        metrics['mrr'] = SearchMetrics.reciprocal_rank(relevant_items, retrieved_items)
        
        # Metrics at different K values
        for k in k_values:
            metrics[f'precision@{k}'] = SearchMetrics.precision_at_k(relevant_items, retrieved_items, k)
            metrics[f'recall@{k}'] = SearchMetrics.recall_at_k(relevant_items, retrieved_items, k)
            metrics[f'f1@{k}'] = SearchMetrics.f1_score_at_k(relevant_items, retrieved_items, k)
            metrics[f'ndcg@{k}'] = SearchMetrics.ndcg_at_k(relevant_items, retrieved_items, k, relevance_scores)
        
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
                # Combine product text
                product_text = ""
                if 'title' in product:
                    product_text += product['title'] + " "
                if 'description' in product:
                    product_text += product.get('description', '') + " "
                if 'category' in product:
                    product_text += product.get('category', '') + " "
                
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
                
                # Cap at 1.0
                relevance = min(1.0, relevance)
                
                if relevance > 0:
                    self.add_judgment(query, product.get('id', product.get('item_id')), relevance)


def demo_metrics():
    """Demonstrate the evaluation metrics with sample data."""
    # Sample ground truth
    relevant_items = {1, 3, 5, 7, 9}
    retrieved_items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    relevance_scores = {1: 1.0, 2: 0.0, 3: 0.8, 4: 0.0, 5: 0.9, 
                       6: 0.0, 7: 0.7, 8: 0.0, 9: 0.6, 10: 0.0}
    
    print("Search Evaluation Metrics Demo")
    print("=" * 50)
    print(f"Relevant items: {relevant_items}")
    print(f"Retrieved items: {retrieved_items}")
    print()
    
    # Calculate metrics
    metrics = SearchMetrics.calculate_comprehensive_metrics(
        relevant_items, retrieved_items, [1, 3, 5, 10], relevance_scores
    )
    
    print("Evaluation Metrics:")
    print("-" * 30)
    print(f"Mean Average Precision (MAP): {metrics['map']:.4f}")
    print(f"Mean Reciprocal Rank (MRR): {metrics['mrr']:.4f}")
    print()
    
    for k in [1, 3, 5, 10]:
        print(f"At K={k}:")
        print(f"  Precision@{k}: {metrics[f'precision@{k}']:.4f}")
        print(f"  Recall@{k}: {metrics[f'recall@{k}']:.4f}")
        print(f"  F1@{k}: {metrics[f'f1@{k}']:.4f}")
        print(f"  NDCG@{k}: {metrics[f'ndcg@{k}']:.4f}")
        print()
    
    # Demonstrate relevance judgment
    print("Relevance Judgment Demo:")
    print("-" * 30)
    
    relevance_judge = RelevanceJudgment()
    
    # Sample queries and products
    queries = ["iPhone case", "wireless charger"]
    products = [
        {'id': 1, 'title': 'iPhone 15 Case', 'description': 'Clear case for iPhone 15'},
        {'id': 2, 'title': 'Samsung Case', 'description': 'Case for Samsung phone'},
        {'id': 3, 'title': 'Wireless Charger', 'description': 'Fast wireless charging pad'},
    ]
    
    relevance_judge.create_synthetic_judgments(queries, products)
    
    for query in queries:
        relevant_items = relevance_judge.get_relevant_items(query, threshold=0.3)
        print(f"Query: '{query}' -> Relevant items: {relevant_items}")


if __name__ == "__main__":
    demo_metrics()
