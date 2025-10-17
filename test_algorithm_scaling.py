#!/usr/bin/env python3
"""
Dataset Scaling Test for Search Algorithms

This script tests how Keyword Matching and TF-IDF algorithms perform
as the dataset size increases, demonstrating TF-IDF's advantages with larger datasets.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithms.keyword_matching import KeywordSearch
from algorithms.tfidf_search import TFIDFSearch
from evaluation.comparison import SearchComparison
from evaluation.metrics import RelevanceJudgment
from database.db_manager import get_db_manager
from database.models import Product


class AlgorithmScalingTest:
    """Test algorithm performance across different dataset sizes."""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.relevance_judge = RelevanceJudgment()
        
    def get_dataset_sizes(self) -> List[int]:
        """Get different dataset sizes to test."""
        return [1000, 2500, 5000, 10000, 20000]  # Key sizes for scaling demonstration
        
    def load_dataset_subset(self, limit: int) -> List[Dict[str, Any]]:
        """Load a subset of the dataset."""
        print(f"📦 Loading {limit} products from database...")
        
        with self.db_manager.get_session() as session:
            if limit >= 29571:  # Load all data
                db_products = session.query(Product).all()
            else:
                db_products = session.query(Product).limit(limit).all()
            
            # Convert to format expected by algorithms
            products = []
            for product in db_products:
                product_dict = {
                    'id': product.id,
                    'title': product.title,
                    'description': product.description or '',
                    'category': product.category,
                    'price': {
                        'value': str(product.price_value), 
                        'currency': product.price_currency
                    },
                    'brand': product.brand or '',
                    'condition': product.condition or '',
                    'seller': {'username': product.seller_name or ''},
                    'location': product.seller_location or '',
                    'url': product.product_url or '',
                    'image_url': product.image_url or '',
                    'source': product.source or '',
                    'rating': product.rating or 0,
                    'review_count': product.review_count or 0,
                    'tags': product.tags or ''
                }
                products.append(product_dict)
        
        print(f"✅ Loaded {len(products)} products")
        return products
    
    def get_scaling_test_queries(self) -> List[str]:
        """Get test queries that work well with the fashion/apparel dataset."""
        return [
            # Fashion/Apparel queries (matches actual dataset)
            "wool shoes",                     # Material + category
            "natural white shoes",           # Color + category  
            "merino blend hoodie",           # Material + item
            "crew sock natural",             # Item + color
            "ankle sock grey",               # Item + color
            "women shoes navy",              # Gender + category + color
            "rugged beige hoodie",           # Style + color + item
            "natural grey heather",          # Color combination
            "blizzard sole shoes",           # Feature + category
            "deep navy shoes",               # Color + category
            
            # Queries that benefit TF-IDF (statistical advantages)
            "premium quality shoes",         # Descriptive terms
            "comfortable running shoes",     # Feature + category
            "durable outdoor apparel",       # Feature + category
            "sustainable fashion items",     # Concept + category
            "breathable fabric clothing",    # Feature + material + category
            
            # Queries that test TF-IDF's ability to handle rare terms
            "stony beige lux liberty",       # Specific color combinations
            "natural white blizzard sole",   # Specific feature combinations
            "medium grey deep navy",         # Color combinations
            
            # Queries that test semantic understanding
            "casual everyday footwear",      # Style + frequency + category
            "outdoor adventure gear"         # Activity + category
        ]
    
    def run_scaling_test(self):
        """Run the scaling test across different dataset sizes."""
        print("🚀 ALGORITHM SCALING TEST")
        print("=" * 60)
        print("Testing how algorithms perform as dataset size increases...")
        print("Expected: TF-IDF should outperform Keyword Matching on larger datasets")
        print()
        
        dataset_sizes = self.get_dataset_sizes()
        test_queries = self.get_scaling_test_queries()
        
        results = {
            'dataset_sizes': dataset_sizes,
            'test_queries': test_queries,
            'algorithm_performance': {}
        }
        
        for size in dataset_sizes:
            print(f"\n📊 Testing with {size:,} products...")
            print("-" * 40)
            
            # Load dataset subset
            products = self.load_dataset_subset(size)
            
            if len(products) == 0:
                print(f"⚠️  No products available for size {size}")
                continue
            
            # Initialize algorithms
            algorithms = {
                'keyword_matching': KeywordSearch(
                    case_sensitive=False,
                    exact_match_weight=30.0  # High weight for exact matches
                ),
                'tfidf': TFIDFSearch(
                    min_df=5,        # Better for larger datasets
                    max_df=0.5,      # More discriminative
                    case_sensitive=False
                )
            }
            
            # Create relevance judgments
            self.relevance_judge.create_synthetic_judgments(test_queries, products)
            
            # Run comparison
            comparison = SearchComparison(algorithms)
            comparison_results = comparison.compare_multiple_queries(
                test_queries, products
            )
            
            # Extract key metrics
            aggregated = comparison_results['aggregated']
            size_results = {
                'products_count': len(products),
                'algorithms': {}
            }
            
            for algo_name, algo_data in aggregated['algorithms'].items():
                size_results['algorithms'][algo_name] = {
                    'map': algo_data['metrics'].get('map', 0),
                    'mrr': algo_data['metrics'].get('mrr', 0),
                    'f1@5': algo_data['metrics'].get('f1@5', 0),
                    'ndcg@10': algo_data['metrics'].get('ndcg@10', 0),
                    'avg_search_time': algo_data.get('avg_search_time', 0)
                }
            
            results['algorithm_performance'][size] = size_results
            
            # Print results for this size
            print(f"📈 Results for {size:,} products:")
            for algo_name, metrics in size_results['algorithms'].items():
                print(f"  {algo_name:15s}: MAP={metrics['map']:.4f}, "
                      f"F1@5={metrics['f1@5']:.4f}, Time={metrics['avg_search_time']:.4f}s")
            
            # Check if TF-IDF is outperforming Keyword Matching
            tfidf_map = size_results['algorithms']['tfidf']['map']
            keyword_map = size_results['algorithms']['keyword_matching']['map']
            
            if tfidf_map > keyword_map:
                print(f"  🎯 TF-IDF OUTPERFORMING Keyword Matching! "
                      f"(MAP: {tfidf_map:.4f} vs {keyword_map:.4f})")
            else:
                print(f"  ⚠️  Keyword Matching still ahead "
                      f"(MAP: {keyword_map:.4f} vs {tfidf_map:.4f})")
        
        # Save results
        self.save_scaling_results(results)
        
        # Generate summary
        self.generate_scaling_summary(results)
        
        return results
    
    def save_scaling_results(self, results: Dict[str, Any]):
        """Save scaling test results to file."""
        filename = "results/algorithm_scaling_test.json"
        os.makedirs("results", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Scaling test results saved to: {filename}")
    
    def generate_scaling_summary(self, results: Dict[str, Any]):
        """Generate a summary of scaling test results."""
        print("\n" + "=" * 60)
        print("📊 SCALING TEST SUMMARY")
        print("=" * 60)
        
        dataset_sizes = results['dataset_sizes']
        performance = results['algorithm_performance']
        
        print("Dataset Size | TF-IDF MAP | Keyword MAP | TF-IDF F1@5 | Keyword F1@5 | Winner")
        print("-" * 80)
        
        tfidf_wins = 0
        total_tests = 0
        
        for size in dataset_sizes:
            if size in performance:
                size_results = performance[size]
                tfidf_metrics = size_results['algorithms']['tfidf']
                keyword_metrics = size_results['algorithms']['keyword_matching']
                
                tfidf_map = tfidf_metrics['map']
                keyword_map = keyword_metrics['map']
                tfidf_f1 = tfidf_metrics['f1@5']
                keyword_f1 = keyword_metrics['f1@5']
                
                winner = "TF-IDF" if tfidf_map > keyword_map else "Keyword"
                if tfidf_map > keyword_map:
                    tfidf_wins += 1
                total_tests += 1
                
                print(f"{size:>11,} | {tfidf_map:>9.4f} | {keyword_map:>10.4f} | "
                      f"{tfidf_f1:>11.4f} | {keyword_f1:>12.4f} | {winner}")
        
        print("-" * 80)
        print(f"TF-IDF wins: {tfidf_wins}/{total_tests} ({tfidf_wins/total_tests*100:.1f}%)")
        
        if tfidf_wins > total_tests / 2:
            print("🎉 SUCCESS: TF-IDF shows superior performance on larger datasets!")
        else:
            print("⚠️  TF-IDF needs further optimization for larger datasets")
        
        # Check trend
        if len(dataset_sizes) >= 3:
            small_size = dataset_sizes[0]
            large_size = dataset_sizes[-1]
            
            if small_size in performance and large_size in performance:
                small_tfidf = performance[small_size]['algorithms']['tfidf']['map']
                small_keyword = performance[small_size]['algorithms']['keyword_matching']['map']
                large_tfidf = performance[large_size]['algorithms']['tfidf']['map']
                large_keyword = performance[large_size]['algorithms']['keyword_matching']['map']
                
                tfidf_improvement = large_tfidf - small_tfidf
                keyword_improvement = large_keyword - small_keyword
                
                print(f"\n📈 Performance Improvement from {small_size:,} "
                      f"to {large_size:,} products:")
                print(f"  TF-IDF MAP improvement: {tfidf_improvement:+.4f}")
                print(f"  Keyword MAP improvement: {keyword_improvement:+.4f}")
                
                if tfidf_improvement > keyword_improvement:
                    print("  ✅ TF-IDF shows better scaling with dataset size!")
                else:
                    print("  ⚠️  Keyword Matching scales better (unexpected)")


def main():
    """Main function to run the scaling test."""
    print("🔬 Algorithm Scaling Test")
    print("This test demonstrates how TF-IDF performs better than Keyword Matching")
    print("as the dataset size increases.")
    print()
    
    tester = AlgorithmScalingTest()
    results = tester.run_scaling_test()
    
    print("\n✅ Scaling test completed!")
    print("Check results/algorithm_scaling_test.json for detailed results")


if __name__ == "__main__":
    main()
