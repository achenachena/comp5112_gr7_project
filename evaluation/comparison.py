"""
Search Algorithm Comparison Framework

This module provides tools to compare different search algorithms and evaluate
their performance using various metrics.
"""

import time
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
            start_time = time.time()

            # Perform search
            search_results = algorithm.search(query, products, limit=max(k_values))
            retrieved_items = [item.get('id', item.get('item_id')) for item in search_results]

            end_time = time.time()

            # Calculate metrics
            metrics = SearchMetrics.calculate_comprehensive_metrics(
                relevant_items, retrieved_items, k_values, relevance_scores
            )

            results['algorithms'][algo_name] = {
                'metrics': metrics,
                'search_time': end_time - start_time,
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
                'avg_search_time': 0.0,
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

                # Accumulate search time and result count
                aggregated['algorithms'][algo_name]['avg_search_time'] += algo_result['search_time']
                aggregated['algorithms'][algo_name]['total_results'] += algo_result['results_count']

        # Calculate averages
        for algo_name in self.algorithms.keys():
            query_count = len(query_results)

            # Average metrics
            for metric_name in aggregated['algorithms'][algo_name]['metrics']:
                aggregated['algorithms'][algo_name]['metrics'][metric_name] /= query_count

            # Average search time
            aggregated['algorithms'][algo_name]['avg_search_time'] /= query_count

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

        # Speed comparison
        avg_times = [(name, data['avg_search_time'])
                    for name, data in aggregated['algorithms'].items()]
        avg_times.sort(key=lambda x: x[1])
        fastest = avg_times[0][0]
        insights.append(f"Fastest algorithm: {fastest} ({avg_times[0][1]:.4f}s average)")

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

    def print_comparison_report(self):
        """
        Print a formatted comparison report.
        """
        if not self.comparison_results:
            print("No comparison results available. Run comparison first.")
            return

        aggregated = self.comparison_results['aggregated']
        summary = self.comparison_results['summary']

        print("Search Algorithm Comparison Report")
        print("=" * 60)
        print(f"Total Queries: {aggregated['total_queries']}")
        print(f"Algorithms Compared: {', '.join(self.algorithms.keys())}")
        print()

        # Performance metrics table
        print("Performance Metrics (Average across all queries):")
        print("-" * 60)
        print(f"{'Algorithm':<20} {'MAP':<8} {'MRR':<8} {'F1@5':<8} "
              f"{'NDCG@10':<10} {'Avg Time(s)':<12}")
        print("-" * 60)

        for algo_name in summary['performance_ranking']:
            algo_data = aggregated['algorithms'][algo_name]
            metrics = algo_data['metrics']

            print(f"{algo_name:<20} "
                  f"{metrics['map']:<8.4f} "
                  f"{metrics['mrr']:<8.4f} "
                  f"{metrics['f1@5']:<8.4f} "
                  f"{metrics['ndcg@10']:<10.4f} "
                  f"{algo_data['avg_search_time']:<12.4f}")

        print()

        # Best algorithms
        print("Best Performing Algorithms:")
        print("-" * 30)
        for metric, info in summary['best_algorithms'].items():
            print(f"{metric}: {info['algorithm']} ({info['score']:.4f})")

        print()

        # Key insights
        print("Key Insights:")
        print("-" * 15)
        for insight in summary['key_insights']:
            print(f"• {insight}")

        print()

        # Detailed metrics at different K values
        print("Detailed Metrics at Different K Values:")
        print("-" * 50)

        k_values = [1, 3, 5, 10]
        for k in k_values:
            print(f"\nAt K={k}:")
            print(f"{'Algorithm':<20} {'Precision':<10} {'Recall':<10} "
                  f"{'F1-Score':<10} {'NDCG':<10}")
            print("-" * 60)

            for algo_name in summary['performance_ranking']:
                algo_data = aggregated['algorithms'][algo_name]
                metrics = algo_data['metrics']

                print(f"{algo_name:<20} "
                      f"{metrics[f'precision@{k}']:<10.4f} "
                      f"{metrics[f'recall@{k}']:<10.4f} "
                      f"{metrics[f'f1@{k}']:<10.4f} "
                      f"{metrics[f'ndcg@{k}']:<10.4f}")


def demo_comparison():
    """Demonstrate the search algorithm comparison framework."""
    # Import algorithms
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from algorithms.keyword_matching import KeywordSearch
    from algorithms.tfidf_search import TFIDFSearch

    # Sample data
    sample_products = [
        {
            'id': 1,
            'title': 'iPhone 15 Pro Max Case - Clear Transparent',
            'description': ('Premium clear case for iPhone 15 Pro Max with wireless charging '
                            'support'),
            'category': 'Phone Cases',
            'price': {'value': '29.99', 'currency': 'USD'}
        },
        {
            'id': 2,
            'title': 'Samsung Galaxy S24 Ultra Case - Black',
            'description': 'Protective case for Samsung Galaxy S24 Ultra with kickstand',
            'category': 'Phone Cases',
            'price': {'value': '24.99', 'currency': 'USD'}
        },
        {
            'id': 3,
            'title': 'iPhone 15 Screen Protector - Tempered Glass',
            'description': '9H hardness tempered glass screen protector for iPhone 15',
            'category': 'Screen Protectors',
            'price': {'value': '12.99', 'currency': 'USD'}
        },
        {
            'id': 4,
            'title': 'Wireless Charger Pad - Fast Charging',
            'description': 'Universal wireless charging pad compatible with iPhone and Android',
            'category': 'Chargers',
            'price': {'value': '19.99', 'currency': 'USD'}
        },
        {
            'id': 5,
            'title': 'iPhone 14 Pro Case - Silicone',
            'description': 'Soft silicone case for iPhone 14 Pro with MagSafe compatibility',
            'category': 'Phone Cases',
            'price': {'value': '39.99', 'currency': 'USD'}
        }
    ]

    test_queries = ["iPhone case", "wireless charger", "Samsung phone"]

    # Initialize algorithms
    algorithms = {
        'keyword_matching': KeywordSearch(),
        'tfidf': TFIDFSearch()
    }

    # Create relevance judgments
    relevance_judge = RelevanceJudgment()
    relevance_judge.create_synthetic_judgments(test_queries, sample_products)

    # Initialize comparison framework
    comparison = SearchComparison(algorithms, relevance_judge)

    # Run comparison
    comparison.compare_multiple_queries(test_queries, sample_products)

    # Print report
    comparison.print_comparison_report()


if __name__ == "__main__":
    demo_comparison()
