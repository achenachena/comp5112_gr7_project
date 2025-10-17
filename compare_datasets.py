#!/usr/bin/env python3
"""
Dataset Comparison Framework

This module provides tools to compare search algorithm performance
across different dataset types (API vs Social Media).
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithms.keyword_matching import KeywordSearch
from algorithms.tfidf_search import TFIDFSearch
from evaluation.comparison import SearchComparison
from evaluation.metrics import RelevanceJudgment
from database.db_manager import get_db_manager
from database.models import Product, SocialMediaProduct
# from utils.visualizations import SearchVisualization  # Unused for now


class DatasetComparator:
    """Compare search algorithms across different dataset types."""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.relevance_judge = RelevanceJudgment()
        
        # Initialize algorithms with recall-optimized parameters
        self.algorithms = {
            'keyword_matching': KeywordSearch(
                case_sensitive=False,
                exact_match_weight=30.0
            ),
            'tfidf': TFIDFSearch(
                min_df=2,
                max_df=0.7,
                case_sensitive=False
            )
        }
    
    def load_api_products(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load products from API-based dataset."""
        print(f"📦 Loading API products{' (limit: ' + str(limit) + ')' if limit else ''}...")
        
        with self.db_manager.get_session() as session:
            if limit:
                db_products = session.query(Product).limit(limit).all()
            else:
                db_products = session.query(Product).all()
            
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
                    'model': product.model or '',
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
        
        print(f"✅ Loaded {len(products)} API products")
        return products
    
    def load_social_media_products(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load products from social media dataset."""
        limit_str = f" (limit: {limit})" if limit else ""
        print(f"📦 Loading Social Media products{limit_str}...")
        
        with self.db_manager.get_session() as session:
            if limit:
                db_products = session.query(SocialMediaProduct).limit(limit).all()
            else:
                db_products = session.query(SocialMediaProduct).all()
            
            products = []
            for product in db_products:
                product_dict = {
                    'id': product.id,
                    'title': product.title,
                    'description': product.content,
                    'category': product.category or 'Social Media',
                    'price': {
                        'value': str(product.price_mentioned) if product.price_mentioned else '0',
                        'currency': product.price_currency
                    },
                    'brand': product.brand or '',
                    'model': '',
                    'condition': 'Used',  # Social media posts typically about used/experienced
                    'seller': {'username': product.author or ''},
                    'location': product.platform,
                    'url': product.url or '',
                    'image_url': product.image_url or '',
                    'source': f"{product.platform}_scraped",
                    'rating': 0,
                    'review_count': product.comments_count or 0,
                    'tags': product.tags or '',
                    # Social media specific fields
                    'platform': product.platform,
                    'subreddit': product.subreddit,
                    'engagement_score': product.engagement_score,
                    'sentiment_score': product.sentiment_score,
                    'is_review': product.is_review,
                    'is_recommendation': product.is_recommendation
                }
                products.append(product_dict)
        
        print(f"✅ Loaded {len(products)} Social Media products")
        return products
    
    def get_dataset_specific_queries(self, dataset_type: str) -> List[str]:
        """Get test queries optimized for specific dataset types."""
        
        if dataset_type == "api":
            # Queries optimized for structured API data
            return [
                "wool shoes", "natural white shoes", "merino blend hoodie",
                "crew sock natural", "ankle sock grey", "women shoes navy",
                "rugged beige hoodie", "natural grey heather", "blizzard sole shoes",
                "deep navy shoes", "premium quality shoes", "comfortable running shoes",
                "durable outdoor apparel", "sustainable fashion items", 
                "breathable fabric clothing",
                "stony beige lux liberty", "natural white blizzard sole", "medium grey deep navy",
                "casual everyday footwear", "outdoor adventure gear"
            ]
        
        elif dataset_type == "social_media":
            # Queries optimized for social media content (more conversational)
            return [
                "best shoes", "recommended hoodie", "good socks", "quality shoes",
                "comfortable shoes", "durable shoes", "worth buying", "great value",
                "love this", "amazing quality", "terrible product", "disappointed",
                "would recommend", "don't buy", "perfect for", "exactly what I needed",
                "waste of money", "game changer", "must have", "skip this",
                "honest review", "my experience", "tried this", "been using"
            ]
        
        else:
            # Generic queries
            return [
                "quality products", "recommended items", "best choices",
                "good value", "durable goods", "comfortable items"
            ]
    
    def run_dataset_comparison(self, api_limit: Optional[int] = None, 
                              social_limit: Optional[int] = None) -> Dict[str, Any]:
        """Run comparison across different dataset types."""
        
        print("🔬 DATASET COMPARISON ANALYSIS")
        print("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'datasets': {}
        }
        
        # Test API dataset
        print("\n📊 Testing API Dataset...")
        print("-" * 30)
        api_products = self.load_api_products(api_limit)
        
        if api_products:
            api_queries = self.get_dataset_specific_queries("api")
            api_results = self._run_algorithm_comparison(api_products, api_queries, "API")
            results['datasets']['api'] = api_results
        
        # Test Social Media dataset
        print("\n📊 Testing Social Media Dataset...")
        print("-" * 30)
        social_products = self.load_social_media_products(social_limit)
        
        if social_products:
            social_queries = self.get_dataset_specific_queries("social_media")
            social_results = self._run_algorithm_comparison(
                social_products, social_queries, "Social Media"
            )
            results['datasets']['social_media'] = social_results
        
        # Generate comparison summary
        if 'api' in results['datasets'] and 'social_media' in results['datasets']:
            results['comparison_summary'] = self._generate_comparison_summary(results)
        
        return results
    
    def _run_algorithm_comparison(self, products: List[Dict[str, Any]], 
                                 queries: List[str], dataset_name: str) -> Dict[str, Any]:
        """Run algorithm comparison on a specific dataset."""
        
        print(f"🔍 Running comparison on {len(products)} products with {len(queries)} queries...")
        
        # Create relevance judgments
        self.relevance_judge.create_synthetic_judgments(queries, products)
        
        # Run comparison
        comparison = SearchComparison(self.algorithms)
        comparison_results = comparison.compare_multiple_queries(queries, products)
        
        # Extract key metrics
        aggregated = comparison_results['aggregated']
        dataset_results = {
            'dataset_name': dataset_name,
            'products_count': len(products),
            'queries_count': len(queries),
            'algorithms': {}
        }
        
        for algo_name, algo_data in aggregated['algorithms'].items():
            dataset_results['algorithms'][algo_name] = {
                'map': algo_data['metrics'].get('map', 0),
                'mrr': algo_data['metrics'].get('mrr', 0),
                'f1@5': algo_data['metrics'].get('f1@5', 0),
                'ndcg@10': algo_data['metrics'].get('ndcg@10', 0),
                'precision@1': algo_data['metrics'].get('precision@1', 0),
                'recall@10': algo_data['metrics'].get('recall@10', 0)
            }
        
        # Print results
        print(f"📈 {dataset_name} Results:")
        for algo_name, metrics in dataset_results['algorithms'].items():
            print(f"  {algo_name:15s}: MAP={metrics['map']:.4f}, "
                  f"F1@5={metrics['f1@5']:.4f}, Recall@10={metrics['recall@10']:.4f}")
        
        return dataset_results
    
    def _generate_comparison_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary comparing different datasets."""
        
        api_data = results['datasets']['api']
        social_data = results['datasets']['social_media']
        
        summary = {
            'dataset_sizes': {
                'api': api_data['products_count'],
                'social_media': social_data['products_count']
            },
            'algorithm_performance': {}
        }
        
        # Compare each algorithm across datasets
        for algo_name in ['keyword_matching', 'tfidf']:
            if algo_name in api_data['algorithms'] and algo_name in social_data['algorithms']:
                api_metrics = api_data['algorithms'][algo_name]
                social_metrics = social_data['algorithms'][algo_name]
                
                summary['algorithm_performance'][algo_name] = {
                    'api': api_metrics,
                    'social_media': social_metrics,
                    'differences': {
                        'map': api_metrics['map'] - social_metrics['map'],
                        'mrr': api_metrics['mrr'] - social_metrics['mrr'],
                        'f1@5': api_metrics['f1@5'] - social_metrics['f1@5'],
                        'recall@10': api_metrics['recall@10'] - social_metrics['recall@10']
                    }
                }
        
        return summary
    
    def save_comparison_results(self, results: Dict[str, Any], filename: str = None):
        """Save comparison results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/dataset_comparison_{timestamp}.json"
        
        os.makedirs("results", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Comparison results saved to: {filename}")
        return filename
    
    def print_comparison_report(self, results: Dict[str, Any]):
        """Print a formatted comparison report."""
        print("\n" + "=" * 80)
        print("📊 DATASET COMPARISON REPORT")
        print("=" * 80)
        
        if 'comparison_summary' not in results:
            print("❌ No comparison summary available")
            return
        
        summary = results['comparison_summary']
        
        # Dataset sizes
        print(f"\n📈 Dataset Sizes:")
        print(f"  API Products: {summary['dataset_sizes']['api']:,}")
        print(f"  Social Media: {summary['dataset_sizes']['social_media']:,}")
        
        # Algorithm performance comparison
        print("\n🔍 Algorithm Performance Comparison:")
        print(f"{'Algorithm':<20} {'Metric':<12} {'API':<8} {'Social':<8} {'Difference':<10}")
        print("-" * 70)
        
        for algo_name, algo_data in summary['algorithm_performance'].items():
            api_metrics = algo_data['api']
            social_metrics = algo_data['social_media']
            differences = algo_data['differences']
            
            for metric in ['map', 'mrr', 'f1@5', 'recall@10']:
                api_val = api_metrics[metric]
                social_val = social_metrics[metric]
                diff = differences[metric]
                
                print(f"{algo_name:<20} {metric:<12} {api_val:<8.4f} "
                      f"{social_val:<8.4f} {diff:>+9.4f}")
        
        # Key insights
        print("\n🎯 Key Insights:")
        
        # Find which dataset performs better for each algorithm
        for algo_name, algo_data in summary['algorithm_performance'].items():
            api_map = algo_data['api']['map']
            social_map = algo_data['social_media']['map']
            
            if api_map > social_map:
                improvement = ((api_map/social_map-1)*100)
                print(f"  • {algo_name}: API dataset performs {improvement:+.1f}% better")
            else:
                improvement = ((social_map/api_map-1)*100)
                print(f"  • {algo_name}: Social Media dataset performs {improvement:+.1f}% better")


def main():
    """Main function to run dataset comparison."""
    print("🔬 Dataset Comparison Framework")
    print("This tool compares search algorithms across different dataset types")
    print()
    
    # Check if we have data
    db_manager = get_db_manager()
    with db_manager.get_session() as session:
        api_count = session.query(Product).count()
        social_count = session.query(SocialMediaProduct).count()
    
    print("📊 Available Data:")
    print(f"  API Products: {api_count:,}")
    print(f"  Social Media Products: {social_count:,}")
    
    if api_count == 0 and social_count == 0:
        print("\n❌ No data available for comparison!")
        print("   Please collect data first using:")
        print("   1. collect_to_database.py (for API data)")
        print("   2. social_media_scraper.py (for social media data)")
        return
    
    # Initialize comparator
    comparator = DatasetComparator()
    
    # Run comparison
    results = comparator.run_dataset_comparison(
        api_limit=min(api_count, 5000) if api_count > 0 else None,
        social_limit=min(social_count, 5000) if social_count > 0 else None
    )
    
    # Print report
    comparator.print_comparison_report(results)
    
    # Save results
    filename = comparator.save_comparison_results(results)
    
    print("\n✅ Dataset comparison completed!")
    print(f"📄 Detailed results saved to: {filename}")


if __name__ == "__main__":
    main()
