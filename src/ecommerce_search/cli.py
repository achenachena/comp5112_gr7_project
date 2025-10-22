#!/usr/bin/env python3
"""
Command Line Interface for E-commerce Search Algorithm Comparison
"""

import argparse
import sys
from typing import List, Optional
from sqlalchemy import func

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms import KeywordSearch, TFIDFSearch
from database import get_db_manager
from evaluation import SearchMetrics, RelevanceJudgment


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
            from ecommerce_search.database.models import Product
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
            from ecommerce_search.database.models import SocialMediaProduct
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
    with db_manager.get_session() as session:
        if dataset == 'api':
            from ecommerce_search.database.models import Product
            products = session.query(Product).limit(limit).all()
            print(f"Loaded {len(products)} API products")
        else:  # social media dataset
            from ecommerce_search.database.models import SocialMediaProduct
            products = session.query(SocialMediaProduct).limit(limit).all()
            print(f"Loaded {len(products)} social media products")
    
    # This would implement the comparison logic
    print("Comparison functionality would be implemented here")


def show_db_info():
    """Show database information."""
    db_manager = get_db_manager()
    info = db_manager.get_database_info()
    
    print("Database Information:")
    print(f"Type: {info['database_type']}")
    print(f"Location: {info.get('location', 'N/A')}")
    print(f"Tables: {', '.join(info.get('tables', []))}")


def show_db_stats():
    """Show database statistics."""
    db_manager = get_db_manager()
    with db_manager.get_session() as session:
        from ecommerce_search.database.models import Product, SocialMediaProduct
        
        # API products
        api_products = session.query(Product).count()
        print(f"API-based products: {api_products:,}")
        
        if api_products > 0:
            # API product sources
            sources = session.query(Product.source, func.count(Product.id)).group_by(Product.source).all()
            print("API sources:")
            for source, count in sources:
                print(f"  {source}: {count:,}")
            
            # API categories
            categories = session.query(Product.category, func.count(Product.id)).group_by(Product.category).all()
            print("\nAPI categories:")
            for category, count in categories:
                print(f"  {category}: {count:,}")
        
        print("\n" + "="*50)
        
        # Social media products
        social_products = session.query(SocialMediaProduct).count()
        print(f"Social media products: {social_products:,}")
        
        if social_products > 0:
            # Social media platforms
            platforms = session.query(SocialMediaProduct.platform, func.count(SocialMediaProduct.id)).group_by(SocialMediaProduct.platform).all()
            print("Social media platforms:")
            for platform, count in platforms:
                print(f"  {platform}: {count:,}")
            
            # Social media categories
            categories = session.query(SocialMediaProduct.category, func.count(SocialMediaProduct.id)).group_by(SocialMediaProduct.category).all()
            print("\nSocial media categories:")
            for category, count in categories:
                print(f"  {category}: {count:,}")
        
        print(f"\nTotal products: {api_products + social_products:,}")


if __name__ == '__main__':
    main()
