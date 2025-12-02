"""
Export Dataset for Submission

This script exports the database contents to JSON format for academic submission.
The exported data can be used to recreate the database or for analysis.

Usage:
    python scripts/utilities/export_dataset.py [--output-dir OUTPUT_DIR]
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ecommerce_search.database.db_manager import get_db_manager
from src.ecommerce_search.database.models import Product, SocialMediaProduct, SearchQuery, DataCollectionLog


def serialize_datetime(obj):
    """Convert datetime objects to ISO format strings."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def export_products(session) -> List[Dict[str, Any]]:
    """Export API products from database."""
    products = session.query(Product).all()
    exported = []
    
    for product in products:
        product_dict = {
            'id': product.id,
            'external_id': product.external_id,
            'source': product.source,
            'title': product.title,
            'description': product.description,
            'brand': product.brand,
            'model': product.model,
            'sku': product.sku,
            'price_value': float(product.price_value) if product.price_value else None,
            'price_currency': product.price_currency,
            'category': product.category,
            'subcategory': product.subcategory,
            'condition': product.condition,
            'availability': product.availability,
            'seller_name': product.seller_name,
            'seller_location': product.seller_location,
            'image_url': product.image_url,
            'product_url': product.product_url,
            'tags': product.tags,
            'specifications': product.specifications,
            'rating': float(product.rating) if product.rating else None,
            'review_count': product.review_count,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None,
        }
        exported.append(product_dict)
    
    return exported


def export_social_media_products(session) -> List[Dict[str, Any]]:
    """Export social media products from database."""
    products = session.query(SocialMediaProduct).all()
    exported = []
    
    for product in products:
        product_dict = {
            'id': product.id,
            'post_id': product.post_id,
            'platform': product.platform,
            'subreddit': product.subreddit,
            'title': product.title,
            'content': product.content,
            'author': product.author,
            'post_date': product.post_date.isoformat() if product.post_date else None,
            'product_name': product.product_name,
            'product_description': product.product_description,
            'brand': product.brand,
            'category': product.category,
            'price_mentioned': float(product.price_mentioned) if product.price_mentioned else None,
            'price_currency': product.price_currency,
            'upvotes': product.upvotes,
            'downvotes': product.downvotes,
            'comments_count': product.comments_count,
            'engagement_score': float(product.engagement_score) if product.engagement_score else None,
            'sentiment_score': float(product.sentiment_score) if product.sentiment_score else None,
            'is_review': product.is_review,
            'is_recommendation': product.is_recommendation,
            'is_complaint': product.is_complaint,
            'url': product.url,
            'image_url': product.image_url,
            'tags': product.tags,
            'created_at': product.created_at.isoformat() if product.created_at else None,
        }
        exported.append(product_dict)
    
    return exported


def export_search_queries(session) -> List[Dict[str, Any]]:
    """Export search queries from database."""
    queries = session.query(SearchQuery).all()
    exported = []
    
    for query in queries:
        query_dict = {
            'id': query.id,
            'query_text': query.query_text,
            'category': query.category,
            'difficulty': query.difficulty,
            'created_at': query.created_at.isoformat() if query.created_at else None,
        }
        exported.append(query_dict)
    
    return exported


def export_collection_logs(session) -> List[Dict[str, Any]]:
    """Export data collection logs from database."""
    logs = session.query(DataCollectionLog).all()
    exported = []
    
    for log in logs:
        log_dict = {
            'id': log.id,
            'api_source': log.api_source,
            'search_query': log.search_query,
            'collection_timestamp': log.collection_timestamp.isoformat() if log.collection_timestamp else None,
            'products_collected': log.products_collected,
            'successful_requests': log.successful_requests,
            'failed_requests': log.failed_requests,
            'error_message': log.error_message,
            'api_response_code': log.api_response_code,
            'collection_time_seconds': float(log.collection_time_seconds) if log.collection_time_seconds else None,
        }
        exported.append(log_dict)
    
    return exported


def generate_dataset_summary(api_products: List, social_products: List, 
                            queries: List, logs: List) -> Dict[str, Any]:
    """Generate a summary of the dataset."""
    # Count products by source
    api_sources = {}
    for product in api_products:
        source = product.get('source', 'unknown')
        api_sources[source] = api_sources.get(source, 0) + 1
    
    # Count products by category
    api_categories = {}
    for product in api_products:
        category = product.get('category', 'unknown')
        api_categories[category] = api_categories.get(category, 0) + 1
    
    # Count social media products by platform
    social_platforms = {}
    for product in social_products:
        platform = product.get('platform', 'unknown')
        social_platforms[platform] = social_platforms.get(platform, 0) + 1
    
    # Price statistics
    prices = [p.get('price_value') for p in api_products if p.get('price_value')]
    price_stats = {}
    if prices:
        price_stats = {
            'min': min(prices),
            'max': max(prices),
            'avg': sum(prices) / len(prices),
            'count': len(prices)
        }
    
    return {
        'export_date': datetime.now().isoformat(),
        'dataset_version': '1.0',
        'summary': {
            'api_products': {
                'total': len(api_products),
                'by_source': api_sources,
                'by_category': api_categories,
                'price_statistics': price_stats
            },
            'social_media_products': {
                'total': len(social_products),
                'by_platform': social_platforms
            },
            'search_queries': {
                'total': len(queries)
            },
            'collection_logs': {
                'total': len(logs)
            }
        }
    }


def export_dataset(output_dir: str = 'dataset_export'):
    """Export the entire dataset to JSON files."""
    print(f"Starting dataset export...")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get database manager
    db_manager = get_db_manager()
    
    # Export data
    with db_manager.get_session() as session:
        print("Exporting API products...")
        api_products = export_products(session)
        print(f"  Exported {len(api_products)} API products")
        
        print("Exporting social media products...")
        social_products = export_social_media_products(session)
        print(f"  Exported {len(social_products)} social media products")
        
        print("Exporting search queries...")
        queries = export_search_queries(session)
        print(f"  Exported {len(queries)} search queries")
        
        print("Exporting collection logs...")
        logs = export_collection_logs(session)
        print(f"  Exported {len(logs)} collection logs")
        
        # Generate summary
        print("Generating dataset summary...")
        summary = generate_dataset_summary(api_products, social_products, queries, logs)
    
    # Write JSON files
    print("\nWriting JSON files...")
    
    api_file = output_path / 'api_products.json'
    with open(api_file, 'w', encoding='utf-8') as f:
        json.dump(api_products, f, indent=2, ensure_ascii=False, default=serialize_datetime)
    print(f"  Written: {api_file} ({api_file.stat().st_size / 1024 / 1024:.2f} MB)")
    
    social_file = output_path / 'social_media_products.json'
    with open(social_file, 'w', encoding='utf-8') as f:
        json.dump(social_products, f, indent=2, ensure_ascii=False, default=serialize_datetime)
    print(f"  Written: {social_file} ({social_file.stat().st_size / 1024 / 1024:.2f} MB)")
    
    queries_file = output_path / 'search_queries.json'
    with open(queries_file, 'w', encoding='utf-8') as f:
        json.dump(queries, f, indent=2, ensure_ascii=False, default=serialize_datetime)
    print(f"  Written: {queries_file}")
    
    logs_file = output_path / 'collection_logs.json'
    with open(logs_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False, default=serialize_datetime)
    print(f"  Written: {logs_file}")
    
    summary_file = output_path / 'dataset_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=serialize_datetime)
    print(f"  Written: {summary_file}")
    
    print(f"\n✅ Dataset export completed successfully!")
    print(f"📁 Output directory: {output_path.absolute()}")
    print(f"\nDataset Statistics:")
    print(f"  - API Products: {len(api_products):,}")
    print(f"  - Social Media Products: {len(social_products):,}")
    print(f"  - Search Queries: {len(queries):,}")
    print(f"  - Collection Logs: {len(logs):,}")
    
    return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Export dataset for submission')
    parser.add_argument(
        '--output-dir',
        type=str,
        default='dataset_export',
        help='Output directory for exported dataset (default: dataset_export)'
    )
    
    args = parser.parse_args()
    
    try:
        export_dataset(args.output_dir)
    except Exception as e:
        print(f"❌ Error exporting dataset: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

