"""
Search Algorithm Comparison Framework

This module provides tools to compare different search algorithms and evaluate
their performance using various metrics.
"""

from typing import List, Dict, Any, Optional
import json
from .metrics import SearchMetrics, RelevanceJudgment


class SearchComparison:
    """
    Framework for comparing different search algorithms.
    """

    def __init__(self, algorithms: Dict[str, Any], relevance_judge: RelevanceJudgment = None):
        """
        Initialize the comparison framework.

        Args:
            algorithms: Dictionary mapping algorithm names to algorithm instances
            relevance_judge: Relevance judgment object for evaluation
        """
        self.algorithms = algorithms
        self.relevance_judge = relevance_judge or RelevanceJudgment()
        self.comparison_results = {}

    def compare_single_query(self, query: str, products: List[Dict[str, Any]],
                           k_values: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Compare algorithms on a single query.

        Args:
            query: Search query
            products: List of products to search through
            k_values: List of K values for evaluation

        Returns:
            Dictionary containing comparison results
        """
        if k_values is None:
            k_values = [1, 3, 5, 10]

        results = {
            'query': query,
            'products_count': len(products),
            'algorithms': {}
        }

        # Get ground truth
        relevant_items = self.relevance_judge.get_relevant_items(query)
        relevance_scores = self.relevance_judge.get_relevance_scores(query)

        # Test each algorithm
        for algo_name, algorithm in self.algorithms.items():
            # Perform search
            search_results = algorithm.search(query, products, limit=max(k_values))
            retrieved_items = [item.get('id', item.get('item_id')) for item in search_results]

            # Calculate metrics
            metrics = SearchMetrics.calculate_comprehensive_metrics(
                relevant_items, retrieved_items, k_values, relevance_scores
            )

            results['algorithms'][algo_name] = {
                'metrics': metrics,
                'results_count': len(search_results),
                'results': search_results[:5],  # Store top 5 results for inspection
                'stats': (algorithm.get_search_stats(query, products)
                          if hasattr(algorithm, 'get_search_stats') else {})
            }

        return results

    def compare_multiple_queries(self, queries: List[str], products: List[Dict[str, Any]],
                               k_values: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Compare algorithms on multiple queries.

        Args:
            queries: List of search queries
            products: List of products to search through
            k_values: List of K values for evaluation

        Returns:
            Dictionary containing aggregated comparison results
        """
        if k_values is None:
            k_values = [1, 3, 5, 10]

        query_results = []

        # Compare each query
        for query in queries:
            query_result = self.compare_single_query(query, products, k_values)
            query_results.append(query_result)

        # Aggregate results
        aggregated = self._aggregate_results(query_results, k_values)

        self.comparison_results = {
            'queries': query_results,
            'aggregated': aggregated,
            'summary': self._generate_summary(aggregated)
        }

        return self.comparison_results

    def _aggregate_results(self, query_results: List[Dict[str, Any]],
                         k_values: List[int]) -> Dict[str, Any]:
        """
        Aggregate results across multiple queries.

        Args:
            query_results: List of results from individual queries
            k_values: List of K values used in evaluation

        Returns:
            Aggregated results dictionary
        """
        aggregated = {
            'algorithms': {},
            'total_queries': len(query_results)
        }

        # Initialize aggregated metrics for each algorithm
        for algo_name in self.algorithms.keys():
            aggregated['algorithms'][algo_name] = {
                'metrics': {},
                'total_results': 0
            }

            # Initialize metric accumulators
            for k in k_values:
                aggregated['algorithms'][algo_name]['metrics'][f'precision@{k}'] = 0.0
                aggregated['algorithms'][algo_name]['metrics'][f'recall@{k}'] = 0.0
                aggregated['algorithms'][algo_name]['metrics'][f'f1@{k}'] = 0.0
                aggregated['algorithms'][algo_name]['metrics'][f'ndcg@{k}'] = 0.0

            aggregated['algorithms'][algo_name]['metrics']['map'] = 0.0
            aggregated['algorithms'][algo_name]['metrics']['mrr'] = 0.0

        # Sum up metrics across queries
        for query_result in query_results:
            for algo_name, algo_result in query_result['algorithms'].items():
                # Accumulate metrics
                for metric_name, value in algo_result['metrics'].items():
                    aggregated['algorithms'][algo_name]['metrics'][metric_name] += value

                # Accumulate result count
                aggregated['algorithms'][algo_name]['total_results'] += (
                    algo_result['results_count']
                )

        # Calculate averages
        for algo_name in self.algorithms.keys():
            query_count = len(query_results)

            # Average metrics
            for metric_name in aggregated['algorithms'][algo_name]['metrics']:
                aggregated['algorithms'][algo_name]['metrics'][metric_name] /= query_count

        return aggregated

    def _generate_summary(self, aggregated: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of the comparison results.

        Args:
            aggregated: Aggregated results dictionary

        Returns:
            Summary dictionary
        """
        summary = {
            'best_algorithms': {},
            'performance_ranking': [],
            'key_insights': []
        }

        # Find best algorithm for each metric
        metrics_to_analyze = ['map', 'mrr', 'f1@5', 'ndcg@10']

        for metric in metrics_to_analyze:
            best_algo = None
            best_score = -1

            for algo_name, algo_data in aggregated['algorithms'].items():
                score = algo_data['metrics'].get(metric, 0.0)
                if score > best_score:
                    best_score = score
                    best_algo = algo_name

            summary['best_algorithms'][metric] = {
                'algorithm': best_algo,
                'score': best_score
            }

        # Create performance ranking based on MAP
        algo_map_scores = []
        for algo_name, algo_data in aggregated['algorithms'].items():
            map_score = algo_data['metrics'].get('map', 0.0)
            algo_map_scores.append((algo_name, map_score))

        algo_map_scores.sort(key=lambda x: x[1], reverse=True)
        summary['performance_ranking'] = [algo_name for algo_name, _ in algo_map_scores]

        # Generate insights
        insights = []

        # MAP comparison
        map_scores = [(name, data['metrics']['map'])
                     for name, data in aggregated['algorithms'].items()]
        map_scores.sort(key=lambda x: x[1], reverse=True)
        best_map = map_scores[0][0]
        insights.append(f"Best MAP score: {best_map} ({map_scores[0][1]:.4f})")

        # Performance gap analysis
        if len(map_scores) > 1:
            gap = map_scores[0][1] - map_scores[1][1]
            insights.append(f"Performance gap: {gap:.4f} between best and second-best algorithms")

        summary['key_insights'] = insights

        return summary

    def export_results(self, filename: str):
        """
        Export comparison results to a JSON file.

        Args:
            filename: Output filename
        """
        if not self.comparison_results:
            raise ValueError("No comparison results to export. Run comparison first.")

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.comparison_results, f, indent=2, ensure_ascii=False)

