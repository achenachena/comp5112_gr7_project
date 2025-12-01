"""
Ultra-Simple GUI Comparison

A minimal, bulletproof comparison framework for GUI applications.
No threading, no complex aggregation, just basic comparison that works.
"""

import time
from typing import List, Dict, Any
from .metrics import RelevanceJudgment, SearchMetrics


class UltraSimpleComparison:
    """
    Ultra-simple comparison that just works.
    """

    def __init__(self, algorithms: Dict[str, Any], relevance_judge: RelevanceJudgment = None):
        self.algorithms = algorithms
        self.relevance_judge = relevance_judge or RelevanceJudgment()

    def compare_simple(self, queries: List[str], products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ultra-simple comparison that just works.
        """

        start_time = time.time()

        # Create synthetic judgments first
        self.relevance_judge.create_synthetic_judgments(queries, products)

        # Simple results structure
        results = {
            'total_queries': len(queries),
            'total_products': len(products),
            'algorithms': {}
        }

        # Initialize algorithm results
        for algo_name in self.algorithms.keys():
            metrics = {
                'map': 0.0,
                'mrr': 0.0,
                'f1@5': 0.0,
                'ndcg@10': 0.0
            }

            # Initialize all K-value metrics (1-10)
            for k in range(1, 11):
                metrics[f'precision@{k}'] = 0.0
                metrics[f'recall@{k}'] = 0.0
                metrics[f'f1@{k}'] = 0.0
                metrics[f'ndcg@{k}'] = 0.0

            results['algorithms'][algo_name] = {
                'metrics': metrics,
                'total_results': 0,
                'avg_search_time': 0.0,
                'queries_processed': 0
            }

        # Process each query
        for i, query in enumerate(queries):

            # Process each algorithm
            for algo_name, algorithm in self.algorithms.items():
                try:
                    algo_start = time.time()

                    # Perform search
                    search_results = algorithm.search(query, products, limit=10)
                    search_time = time.time() - algo_start

                    # Simple metrics calculation
                    relevant_items = self.relevance_judge.get_relevant_items(query)
                    # Use actual product IDs from search results
                    retrieved_items = []
                    for result in search_results:
                        # Try to get the product ID from the result
                        product_id = result.get('id')
                        if product_id is None:
                            # If no ID, try to find the product in the original list
                            for i, product in enumerate(products):
                                if (product.get('title') == result.get('title') and
                                    product.get('description') == result.get('description')):
                                    product_id = i
                                    break
                        if product_id is not None:
                            retrieved_items.append(product_id)
                    

                    # Calculate metrics for all K values (1-10)
                    if relevant_items and retrieved_items:
                        map_score = SearchMetrics.mean_average_precision(
                            relevant_items, retrieved_items
                        )
                        mrr_score = SearchMetrics.reciprocal_rank(
                            relevant_items, retrieved_items
                        )

                        # Calculate metrics for each K value
                        for k in range(1, 11):
                            precision_k = SearchMetrics.precision_at_k(
                                relevant_items, retrieved_items, k
                            )
                            recall_k = SearchMetrics.recall_at_k(relevant_items, retrieved_items, k)
                            f1_k = SearchMetrics.f1_score_at_k(relevant_items, retrieved_items, k)
                            ndcg_k = SearchMetrics.ndcg_at_k(relevant_items, retrieved_items, k)

                            # Accumulate metrics for each K
                            results['algorithms'][algo_name]['metrics'][
                                f'precision@{k}'
                            ] += precision_k
                            results['algorithms'][algo_name]['metrics'][f'recall@{k}'] += recall_k
                            results['algorithms'][algo_name]['metrics'][f'f1@{k}'] += f1_k
                            results['algorithms'][algo_name]['metrics'][f'ndcg@{k}'] += ndcg_k
                    else:
                        map_score = mrr_score = 0.0
                        # Set all K values to 0
                        for k in range(1, 11):
                            results['algorithms'][algo_name]['metrics'][f'precision@{k}'] += 0.0
                            results['algorithms'][algo_name]['metrics'][f'recall@{k}'] += 0.0
                            results['algorithms'][algo_name]['metrics'][f'f1@{k}'] += 0.0
                            results['algorithms'][algo_name]['metrics'][f'ndcg@{k}'] += 0.0

                    # Update results
                    results['algorithms'][algo_name]['queries_processed'] += 1
                    results['algorithms'][algo_name]['total_results'] += len(search_results)
                    results['algorithms'][algo_name]['avg_search_time'] += search_time

                    # Accumulate basic metrics
                    results['algorithms'][algo_name]['metrics']['map'] += map_score
                    results['algorithms'][algo_name]['metrics']['mrr'] += mrr_score

                except (AttributeError, KeyError, ValueError, TypeError):
                    # Continue with other algorithms
                    pass

        total_time = time.time() - start_time
        results['total_time'] = total_time

        # Calculate averages
        for algo_name in self.algorithms.keys():
            queries_processed = results['algorithms'][algo_name]['queries_processed']
            if queries_processed > 0:
                results['algorithms'][algo_name]['avg_search_time'] /= queries_processed
                # Average basic metrics
                for metric in ['map', 'mrr']:
                    results['algorithms'][algo_name]['metrics'][metric] /= queries_processed

                # Average all K value metrics
                for k in range(1, 11):
                    for metric in ['precision', 'recall', 'f1', 'ndcg']:
                        key = f'{metric}@{k}'
                        results['algorithms'][algo_name]['metrics'][key] /= queries_processed

        # Add comprehensive summary for GUI compatibility
        # Create performance ranking based on MAP scores
        algorithm_names = list(results['algorithms'].keys())
        performance_ranking = sorted(
            algorithm_names,
            key=lambda name: results['algorithms'][name]['metrics']['map'],
            reverse=True
        )

        # Create best algorithms dictionary
        best_algorithms = {}
        for metric in ['map', 'mrr', 'f1@5', 'ndcg@10']:
            best_score = 0
            best_algorithm = None
            for algo_name in algorithm_names:
                score = results['algorithms'][algo_name]['metrics'].get(metric, 0)
                if score > best_score:
                    best_score = score
                    best_algorithm = algo_name
            if best_algorithm:
                best_algorithms[metric] = {
                    'algorithm': best_algorithm,
                    'score': best_score
                }

        results['summary'] = {
            'key_insights': [
                f"Processed {results['total_queries']} queries across "
                f"{results['total_products']:,} products in {total_time:.2f}s"
            ],
            'performance_notes': [
                "Used ultra-simple sequential processing for maximum stability"
            ],
            'performance_ranking': performance_ranking,
            'best_algorithms': best_algorithms
        }

        return results

