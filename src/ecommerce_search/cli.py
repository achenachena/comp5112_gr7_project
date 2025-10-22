#!/usr/bin/env python3
"""
Command Line Interface for E-commerce Search Algorithm Comparison
"""

import argparse
import sys
import os
from typing import List, Optional
from sqlalchemy import func

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Project imports
from ecommerce_search.algorithms.keyword_matching import KeywordSearch  # pylint: disable=wrong-import-position
from ecommerce_search.algorithms.tfidf_search import TFIDFSearch  # pylint: disable=wrong-import-position
from ecommerce_search.database.db_manager import get_db_manager  # pylint: disable=wrong-import-position
from ecommerce_search.database.models import Product, SocialMediaProduct  # pylint: disable=wrong-import-position
from ecommerce_search.evaluation.algorithm_comparison import UltraSimpleComparison  # pylint: disable=wrong-import-position
from ecommerce_search.evaluation.metrics import RelevanceJudgment  # pylint: disable=wrong-import-position


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="E-commerce Search Algorithm Comparison CLI"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Perform search')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--algorithm', choices=['keyword', 'tfidf', 'both'],
                              default='both', help='Algorithm to use')
    search_parser.add_argument('--dataset', choices=['api', 'social'],
                              default='api', help='Dataset to use (api or social)')
    search_parser.add_argument('--limit', type=int, default=10,
                              help='Maximum number of results')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare algorithms')
    compare_parser.add_argument('--queries', nargs='+',
                               help='Test queries (if not provided, uses default set)')
    compare_parser.add_argument('--dataset', choices=['api', 'social'],
                              default='api', help='Dataset to use (api or social)')
    compare_parser.add_argument('--limit', type=int, default=1000,
                               help='Maximum number of products to load')

    # Database command
    db_parser = subparsers.add_parser('db', help='Database operations')
    db_subparsers = db_parser.add_subparsers(dest='db_command')

    db_subparsers.add_parser('info', help='Show database information')
    db_subparsers.add_parser('stats', help='Show database statistics')

    args = parser.parse_args()

    if args.command == 'search':
        run_search(args.query, args.algorithm, args.dataset, args.limit)
    elif args.command == 'compare':
        run_comparison(args.queries, args.dataset, args.limit)
    elif args.command == 'db':
        if args.db_command == 'info':
            show_db_info()
        elif args.db_command == 'stats':
            show_db_stats()
        else:
            db_parser.print_help()
    else:
        parser.print_help()


def run_search(query: str, algorithm: str, dataset: str, limit: int):
    """Run search with specified algorithm and dataset."""
    print(f"Searching for: '{query}'")
    print(f"Algorithm: {algorithm}")
    print(f"Dataset: {dataset}")
    print(f"Limit: {limit}")
    print("-" * 50)

    # Initialize algorithms
    algorithms = {
        'keyword': KeywordSearch(),
        'tfidf': TFIDFSearch()
    }

    # Load products based on dataset choice
    db_manager = get_db_manager()
    with db_manager.get_session() as session:
        if dataset == 'api':
            products = session.query(Product).limit(1000).all()
            search_products = []
            for product in products:
                search_products.append({
                    'id': product.external_id,
                    'title': product.title,
                    'description': product.description or '',
                    'category': product.category,
                    'price': {
                        'value': str(product.price_value),
                        'currency': product.price_currency
                    },
                    'brand': product.brand or '',
                    'condition': product.condition
                })
        else:  # social media dataset
            products = session.query(SocialMediaProduct).limit(1000).all()
            search_products = []
            for product in products:
                search_products.append({
                    'id': product.post_id,
                    'title': product.title,
                    'description': product.content or '',
                    'category': product.category or '',
                    'price': {
                        'value': str(product.price_mentioned or 0),
                        'currency': 'USD'
                    },
                    'brand': product.brand or '',
                    'platform': product.platform,
                    'subreddit': product.subreddit,
                    'upvotes': product.upvotes,
                    'comments_count': product.comments_count
                })

    # Run search
    if algorithm == 'both':
        for algo_name, algo in algorithms.items():
            print(f"\n{algo_name.upper()} Results:")
            results = algo.search(query, search_products, limit=limit)
            for i, result in enumerate(results, 1):
                if 'product' in result:
                    # New format with nested structure
                    product = result['product']
                    score = result['score']
                    title = product.get('title', 'No title')
                else:
                    # Old format with direct fields
                    title = result.get('title', 'No title')
                    score = result.get('score', 0)
                print(f"{i}. {title} (Score: {score:.4f})")
    else:
        algo = algorithms[algorithm]
        results = algo.search(query, search_products, limit=limit)
        for i, result in enumerate(results, 1):
            if 'product' in result:
                # New format with nested structure
                product = result['product']
                score = result['score']
                title = product.get('title', 'No title')
            else:
                # Old format with direct fields
                title = result.get('title', 'No title')
                score = result.get('score', 0)
            print(f"{i}. {title} (Score: {score:.4f})")


def run_comparison(queries: Optional[List[str]], dataset: str, limit: int):
    """Run algorithm comparison."""
    if queries is None:
        if dataset == 'api':
            queries = [
                "wool shoes", "natural white shoes", "merino blend hoodie",
                "crew sock natural", "ankle sock grey", "women shoes navy"
            ]
        else:  # social media dataset
            queries = [
                "amazing product", "worth it", "highly recommend",
                "best purchase", "incredible gadget", "fantastic tool"
            ]

    print(f"Running comparison with {len(queries)} queries")
    print(f"Dataset: {dataset}")
    print(f"Product limit: {limit}")
    print("-" * 50)

    # Load products based on dataset choice
    db_manager = get_db_manager()
    search_products = []
    
    with db_manager.get_session() as session:
        if dataset == 'api':
            products = session.query(Product).limit(limit).all()
            print(f"Loaded {len(products)} API products")
            
            # Convert database products to search format
            for product in products:
                search_products.append({
                    'id': product.external_id,
                    'title': product.title,
                    'description': product.description or '',
                    'category': product.category,
                    'price': {
                        'value': str(product.price_value),
                        'currency': product.price_currency
                    },
                    'brand': product.brand or '',
                    'condition': product.condition,
                    'source': product.source
                })
        else:  # social media dataset
            products = session.query(SocialMediaProduct).limit(limit).all()
            print(f"Loaded {len(products)} social media products")
            
            # Convert database products to search format
            for product in products:
                search_products.append({
                    'id': product.post_id,
                    'title': product.title,
                    'description': product.content or '',
                    'category': product.category or '',
                    'price': {
                        'value': str(product.price_mentioned or 0),
                        'currency': 'USD'
                    },
                    'brand': product.brand or '',
                    'platform': product.platform,
                    'subreddit': product.subreddit,
                    'upvotes': product.upvotes,
                    'comments_count': product.comments_count
                })

    # Initialize algorithms
    algorithms = {
        'keyword_matching': KeywordSearch(),
        'tfidf_search': TFIDFSearch()
    }

    # Create relevance judgments
    relevance_judge = RelevanceJudgment()
    relevance_judge.create_synthetic_judgments(queries, search_products)

    # Run comparison using the same framework as web GUI
    print("Running algorithm comparison...")
    comparison = UltraSimpleComparison(algorithms, relevance_judge)
    results = comparison.compare_simple(queries, search_products)

    # Display results
    print("\n" + "="*60)
    print("ALGORITHM COMPARISON RESULTS")
    print("="*60)
    
    for algo_name, algo_data in results['algorithms'].items():
        print(f"\n{algo_name.upper()}:")
        print(f"  Queries Processed: {algo_data['queries_processed']}")
        print(f"  Total Results: {algo_data['total_results']}")
        print(f"  Average Search Time: {algo_data['avg_search_time']:.4f}s")
        
        metrics = algo_data['metrics']
        print(f"  MAP: {metrics['map']:.4f}")
        print(f"  MRR: {metrics['mrr']:.4f}")
        print(f"  F1@5: {metrics['f1@5']:.4f}")
        print(f"  NDCG@10: {metrics['ndcg@10']:.4f}")
        
        # Show precision@k for k=1,3,5,10
        for k in [1, 3, 5, 10]:
            print(f"  Precision@{k}: {metrics[f'precision@{k}']:.4f}")

    # Show performance ranking
    if 'summary' in results and 'performance_ranking' in results['summary']:
        print(f"\nPERFORMANCE RANKING:")
        for i, algo in enumerate(results['summary']['performance_ranking'], 1):
            print(f"  {i}. {algo}")

    print(f"\nTotal comparison time: {results['total_time']:.2f}s")


def show_db_info():
    """Show database information."""
    db_manager = get_db_manager()
    info = db_manager.get_database_info()

    print("Database Information:")
    print(f"Type: {info['database_type']}")
    print(f"Location: {info.get('database_url', 'N/A')}")
    print(f"Tables: {info.get('tables_created', 0)}")


def show_db_stats():
    """Show database statistics."""
    db_manager = get_db_manager()
    with db_manager.get_session() as session:

        # API products
        api_products = session.query(Product).count()
        print(f"API-based products: {api_products:,}")

        if api_products > 0:
            # API product sources
            sources = session.query(
                Product.source, func.count(Product.id)
            ).group_by(Product.source).all()
            print("API sources:")
            for source, count in sources:
                print(f"  {source}: {count:,}")

            # API categories
            categories = session.query(
                Product.category, func.count(Product.id)
            ).group_by(Product.category).all()
            print("\nAPI categories:")
            for category, count in categories:
                print(f"  {category}: {count:,}")

        print("\n" + "="*50)

        # Social media products
        social_products = session.query(SocialMediaProduct).count()
        print(f"Social media products: {social_products:,}")

        if social_products > 0:
            # Social media platforms
            platforms = session.query(
                SocialMediaProduct.platform, func.count(SocialMediaProduct.id)
            ).group_by(SocialMediaProduct.platform).all()
            print("Social media platforms:")
            for platform, count in platforms:
                print(f"  {platform}: {count:,}")

            # Social media categories
            categories = session.query(
                SocialMediaProduct.category, func.count(SocialMediaProduct.id)
            ).group_by(SocialMediaProduct.category).all()
            print("\nSocial media categories:")
            for category, count in categories:
                print(f"  {category}: {count:,}")

        print(f"\nTotal products: {api_products + social_products:,}")


if __name__ == '__main__':
    main()
