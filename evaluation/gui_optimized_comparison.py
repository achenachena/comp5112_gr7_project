"""
GUI-Optimized Search Algorithm Comparison

A simplified, fast comparison framework specifically designed for GUI applications
that avoids multiprocessing issues while still providing significant performance improvements.
"""

import time
from typing import List, Dict, Any, Optional
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from .metrics import RelevanceJudgment


class GUIOptimizedComparison:
    """
    GUI-safe optimized comparison framework using threading and vectorized operations.
    """

    def __init__(self, algorithms: Dict[str, Any], relevance_judge: RelevanceJudgment = None,
                 max_workers: int = None):
        """
        Initialize the GUI-optimized comparison framework.

        Args:
            algorithms: Dictionary mapping algorithm names to algorithm instances
            relevance_judge: Relevance judgment object for evaluation
            max_workers: Maximum number of worker threads (default: 4 for GUI stability)
        """
        self.algorithms = algorithms
        self.relevance_judge = relevance_judge or RelevanceJudgment()
        self.max_workers = max_workers or 4  # Conservative for GUI stability
        self.comparison_results = {}

    def compare_algorithms_fast(self, queries: List[str], products: List[Dict[str, Any]],
                              k_values: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Fast algorithm comparison optimized for GUI applications.

        Args:
            queries: List of search queries
            products: List of products to search through
            k_values: List of K values for evaluation

        Returns:
            Dictionary containing comparison results
        """
        if k_values is None:
            k_values = [1, 3, 5, 10]

        print(f"🚀 Starting GUI-optimized comparison with {self.max_workers} threads...")
        print(f"📊 Processing {len(queries)} queries across {len(products):,} products")

        all_results = []
        total_start_time = time.time()

        # Process queries in parallel using threading
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all queries for parallel processing
            future_to_query = {}
            
            for query in queries:
                future = executor.submit(
                    self._process_single_query_fast, 
                    query, products, k_values
                )
                future_to_query[future] = query

            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    result = future.result()
                    all_results.append(result)
                    completed += 1
                    print(f"✅ Completed query {completed}/{len(queries)} "
                          f"({completed * 100 // len(queries)}%)")
                except Exception as e:
                    print(f"❌ Error processing query '{query}': {e}")
                    # Add empty result for failed query
                    all_results.append({
                        'query': query,
                        'products_count': len(products),
                        'algorithms': {},
                        'error': str(e)
                    })

        total_time = time.time() - total_start_time
        
        # Aggregate results
        aggregated_results = self._aggregate_results_fast(all_results, total_time)
        
        # Store results for reporting
        self.last_results = aggregated_results
        
        return aggregated_results

    def _process_single_query_fast(self, query: str, products: List[Dict[str, Any]], 
                                 k_values: List[int]) -> Dict[str, Any]:
        """Process a single query with all algorithms (thread-safe)."""
        result = {
            'query': query,
            'products_count': len(products),
            'algorithms': {}
        }

        # Run all algorithms on this query
        for algo_name, algorithm in self.algorithms.items():
            start_time = time.time()
            
            try:
                # Perform search
                search_results = algorithm.search(query, products, k=10)
                search_time = time.time() - start_time
                
                # Calculate metrics for each k value
                metrics = {}
                for k in k_values:
                    k_results = search_results[:k] if len(search_results) >= k else search_results
                    k_metrics = self.relevance_judge.calculate_metrics(query, k_results, k)
                    metrics.update(k_metrics)
                
                result['algorithms'][algo_name] = {
                    'metrics': metrics,
                    'results': search_results[:10],  # Store top 10 results
                    'search_time': search_time,
                    'results_count': len(search_results)
                }
                
            except Exception as e:
                result['algorithms'][algo_name] = {
                    'error': str(e),
                    'metrics': {},
                    'results': [],
                    'search_time': time.time() - start_time,
                    'results_count': 0
                }

        return result

    def _aggregate_results_fast(self, results: List[Dict[str, Any]], 
                              total_time: float) -> Dict[str, Any]:
        """Fast aggregation of results using vectorized operations."""
        if not results:
            return {'error': 'No results to aggregate'}

        # Extract algorithm names
        algorithm_names = set()
        for result in results:
            algorithm_names.update(result.get('algorithms', {}).keys())
        algorithm_names = list(algorithm_names)

        # Initialize aggregation structure
        aggregated = {
            'total_queries': len(results),
            'total_products': results[0]['products_count'] if results else 0,
            'total_time': total_time,
            'algorithms': {}
        }

        # Initialize metrics arrays for each algorithm
        for algo_name in algorithm_names:
            aggregated['algorithms'][algo_name] = {
                'metrics': {},
                'total_results': 0,
                'total_search_time': 0,
                'queries_processed': 0
            }

        # Aggregate metrics efficiently
        for result in results:
            for algo_name in algorithm_names:
                if algo_name in result.get('algorithms', {}):
                    algo_result = result['algorithms'][algo_name]
                    algo_agg = aggregated['algorithms'][algo_name]
                    
                    # Count queries and results
                    algo_agg['queries_processed'] += 1
                    algo_agg['total_results'] += algo_result.get('results_count', 0)
                    algo_agg['total_search_time'] += algo_result.get('search_time', 0)
                    
                    # Aggregate metrics
                    for metric_name, metric_value in algo_result.get('metrics', {}).items():
                        if metric_name not in algo_agg['metrics']:
                            algo_agg['metrics'][metric_name] = []
                        algo_agg['metrics'][metric_name].append(metric_value)

        # Calculate averages using vectorized operations
        for algo_name in algorithm_names:
            algo_agg = aggregated['algorithms'][algo_name]
            
            # Calculate average search time
            if algo_agg['queries_processed'] > 0:
                algo_agg['avg_search_time'] = (
                    algo_agg['total_search_time'] / algo_agg['queries_processed']
                )
            else:
                algo_agg['avg_search_time'] = 0
            
            # Calculate average metrics
            for metric_name, metric_values in algo_agg['metrics'].items():
                if metric_values:
                    # Use numpy for faster computation
                    values_array = np.array(metric_values)
                    algo_agg['metrics'][metric_name] = {
                        'mean': float(np.mean(values_array)),
                        'std': float(np.std(values_array)),
                        'min': float(np.min(values_array)),
                        'max': float(np.max(values_array))
                    }
                else:
                    algo_agg['metrics'][metric_name] = {'mean': 0, 'std': 0, 'min': 0, 'max': 0}

        # Generate summary
        aggregated['summary'] = self._generate_summary_fast(aggregated)
        
        return aggregated

    def _generate_summary_fast(self, aggregated: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary with key insights."""
        summary = {
            'best_algorithms': {},
            'key_insights': [],
            'performance_notes': []
        }

        # Find best algorithm for each metric
        for metric_name in ['map', 'mrr', 'f1@5', 'ndcg@10']:
            best_score = 0
            best_algorithm = None
            
            for algo_name, algo_data in aggregated['algorithms'].items():
                if metric_name in algo_data['metrics']:
                    score = algo_data['metrics'][metric_name]['mean']
                    if score > best_score:
                        best_score = score
                        best_algorithm = algo_name
            
            if best_algorithm:
                summary['best_algorithms'][metric_name] = {
                    'algorithm': best_algorithm,
                    'score': best_score
                }

        # Generate insights
        if len(aggregated['algorithms']) >= 2:
            algo_names = list(aggregated['algorithms'].keys())
            algo1_map = aggregated['algorithms'][algo_names[0]]['metrics'].get('map', {}).get('mean', 0)
            algo2_map = aggregated['algorithms'][algo_names[1]]['metrics'].get('map', {}).get('mean', 0)
            
            if algo1_map > algo2_map:
                summary['key_insights'].append(
                    f"{algo_names[0]} outperforms {algo_names[1]} in overall relevance (MAP: {algo1_map:.3f} vs {algo2_map:.3f})"
                )
            else:
                summary['key_insights'].append(
                    f"{algo_names[1]} outperforms {algo_names[0]} in overall relevance (MAP: {algo2_map:.3f} vs {algo1_map:.3f})"
                )

        # Performance notes
        total_queries = aggregated['total_queries']
        total_time = aggregated['total_time']
        avg_time_per_query = total_time / total_queries if total_queries > 0 else 0
        
        summary['performance_notes'].append(
            f"Processed {total_queries} queries in {total_time:.2f}s "
            f"({avg_time_per_query:.3f}s per query)"
        )
        summary['performance_notes'].append(
            f"Used {self.max_workers} threads for GUI-optimized performance"
        )

        return summary

    def export_results(self, results: Dict[str, Any], output_file: str):
        """Export results to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    def print_comparison_report(self):
        """Print a formatted comparison report."""
        if not hasattr(self, 'last_results'):
            print("No comparison results available. Run a comparison first.")
            return
            
        results = self.last_results
        # Handle both old and new result formats
        if 'aggregated' in results:
            aggregated = results['aggregated']
        else:
            aggregated = results
        
        print("\n" + "="*60)
        print("GUI-OPTIMIZED ALGORITHM COMPARISON RESULTS")
        print("="*60)
        
        # Performance summary
        print(f"📊 Performance Summary:")
        print(f"  Total Queries: {aggregated['total_queries']}")
        print(f"  Total Products: {aggregated['total_products']:,}")
        print(f"  Total Time: {aggregated['total_time']:.2f}s")
        print(f"  Workers Used: {self.max_workers}")
        print()
        
        # Algorithm comparison
        print("🔍 Algorithm Performance:")
        print("-" * 40)
        
        algorithms = list(aggregated['algorithms'].keys())
        metrics = ['map', 'mrr', 'f1@5', 'ndcg@10']
        
        # Header
        header = f"{'Metric':<12}"
        for algo in algorithms:
            header += f"{algo:<15}"
        print(header)
        print("-" * len(header))
        
        # Metrics rows
        for metric in metrics:
            row = f"{metric.upper():<12}"
            for algo in algorithms:
                value = aggregated['algorithms'][algo]['metrics'].get(metric, {}).get('mean', 0)
                row += f"{value:<15.4f}"
            print(row)
        
        print()
        
        # Key insights
        if 'summary' in results and 'key_insights' in results['summary']:
            print("💡 Key Insights:")
            print("-" * 20)
            for insight in results['summary']['key_insights']:
                print(f"• {insight}")
            print()
        
        # Performance notes
        if 'summary' in results and 'performance_notes' in results['summary']:
            print("⚡ Performance Notes:")
            print("-" * 25)
            for note in results['summary']['performance_notes']:
                print(f"• {note}")
            print()
