"""
Import Dataset from JSON Files

This script imports the exported dataset JSON files back into the database.
Useful for recreating the database from the submitted dataset.

Usage:
    python scripts/utilities/import_dataset.py [--input-dir INPUT_DIR] [--reset]
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ecommerce_search.database.db_manager import get_db_manager
from src.ecommerce_search.database.models import Product, SocialMediaProduct, SearchQuery, DataCollectionLog


def parse_datetime(dt_str: str) -> datetime:
    """Parse ISO format datetime string."""
    if dt_str is None:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def import_products(session, products_data: List[Dict[str, Any]]):
    """Import API products into database."""
    imported = 0
    skipped = 0
    
    for product_data in products_data:
        try:
            # Check if product already exists
            existing = session.query(Product).filter_by(
                external_id=product_data.get('external_id')
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            product = Product(
                external_id=product_data.get('external_id'),
                source=product_data.get('source'),
                title=product_data.get('title'),
                description=product_data.get('description'),
                brand=product_data.get('brand'),
                model=product_data.get('model'),
                sku=product_data.get('sku'),
                price_value=product_data.get('price_value'),
                price_currency=product_data.get('price_currency', 'USD'),
                category=product_data.get('category'),
                subcategory=product_data.get('subcategory'),
                condition=product_data.get('condition', 'New'),
                availability=product_data.get('availability', 'In Stock'),
                seller_name=product_data.get('seller_name'),
                seller_location=product_data.get('seller_location'),
                image_url=product_data.get('image_url'),
                product_url=product_data.get('product_url'),
                tags=product_data.get('tags'),
                specifications=product_data.get('specifications'),
                rating=product_data.get('rating'),
                review_count=product_data.get('review_count'),
                created_at=parse_datetime(product_data.get('created_at')),
                updated_at=parse_datetime(product_data.get('updated_at')),
            )
            
            session.add(product)
            imported += 1
            
            if imported % 1000 == 0:
                session.commit()
                print(f"  Imported {imported} products...")
                
        except Exception as e:
            print(f"  Error importing product {product_data.get('external_id')}: {e}")
            skipped += 1
            continue
    
    session.commit()
    return imported, skipped


def import_social_media_products(session, products_data: List[Dict[str, Any]]):
    """Import social media products into database."""
    imported = 0
    skipped = 0
    
    for product_data in products_data:
        try:
            # Check if product already exists
            existing = session.query(SocialMediaProduct).filter_by(
                post_id=product_data.get('post_id')
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            product = SocialMediaProduct(
                post_id=product_data.get('post_id'),
                platform=product_data.get('platform'),
                subreddit=product_data.get('subreddit'),
                title=product_data.get('title'),
                content=product_data.get('content'),
                author=product_data.get('author'),
                post_date=parse_datetime(product_data.get('post_date')),
                product_name=product_data.get('product_name'),
                product_description=product_data.get('product_description'),
                brand=product_data.get('brand'),
                category=product_data.get('category'),
                price_mentioned=product_data.get('price_mentioned'),
                price_currency=product_data.get('price_currency', 'USD'),
                upvotes=product_data.get('upvotes', 0),
                downvotes=product_data.get('downvotes', 0),
                comments_count=product_data.get('comments_count', 0),
                engagement_score=product_data.get('engagement_score'),
                sentiment_score=product_data.get('sentiment_score'),
                is_review=product_data.get('is_review', False),
                is_recommendation=product_data.get('is_recommendation', False),
                is_complaint=product_data.get('is_complaint', False),
                url=product_data.get('url'),
                image_url=product_data.get('image_url'),
                tags=product_data.get('tags'),
                created_at=parse_datetime(product_data.get('created_at')),
            )
            
            session.add(product)
            imported += 1
            
            if imported % 1000 == 0:
                session.commit()
                print(f"  Imported {imported} social media products...")
                
        except Exception as e:
            print(f"  Error importing social media product {product_data.get('post_id')}: {e}")
            skipped += 1
            continue
    
    session.commit()
    return imported, skipped


def import_search_queries(session, queries_data: List[Dict[str, Any]]):
    """Import search queries into database."""
    imported = 0
    skipped = 0
    
    for query_data in queries_data:
        try:
            # Check if query already exists
            existing = session.query(SearchQuery).filter_by(
                query_text=query_data.get('query_text')
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            query = SearchQuery(
                query_text=query_data.get('query_text'),
                category=query_data.get('category'),
                difficulty=query_data.get('difficulty'),
                created_at=parse_datetime(query_data.get('created_at')),
            )
            
            session.add(query)
            imported += 1
            
        except Exception as e:
            print(f"  Error importing query {query_data.get('query_text')}: {e}")
            skipped += 1
            continue
    
    session.commit()
    return imported, skipped


def import_collection_logs(session, logs_data: List[Dict[str, Any]]):
    """Import collection logs into database."""
    imported = 0
    skipped = 0
    
    for log_data in logs_data:
        try:
            log = DataCollectionLog(
                api_source=log_data.get('api_source'),
                search_query=log_data.get('search_query'),
                collection_timestamp=parse_datetime(log_data.get('collection_timestamp')),
                products_collected=log_data.get('products_collected', 0),
                successful_requests=log_data.get('successful_requests', 0),
                failed_requests=log_data.get('failed_requests', 0),
                error_message=log_data.get('error_message'),
                api_response_code=log_data.get('api_response_code'),
                collection_time_seconds=log_data.get('collection_time_seconds'),
            )
            
            session.add(log)
            imported += 1
            
        except Exception as e:
            print(f"  Error importing log: {e}")
            skipped += 1
            continue
    
    session.commit()
    return imported, skipped


def import_dataset(input_dir: str = 'dataset_export', reset: bool = False):
    """Import dataset from JSON files into database."""
    print(f"Starting dataset import from: {input_dir}")
    
    input_path = Path(input_dir)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_path}")
    
    # Get database manager
    db_manager = get_db_manager()
    
    # Reset database if requested
    if reset:
        print("⚠️  Resetting database (all existing data will be deleted)...")
        db_manager.reset_database()
    
    # Ensure tables exist
    db_manager.create_tables()
    
    # Load and import data
    with db_manager.get_session() as session:
        # Import API products
        api_file = input_path / 'api_products.json'
        if api_file.exists():
            print(f"\nImporting API products from {api_file}...")
            with open(api_file, 'r', encoding='utf-8') as f:
                api_products = json.load(f)
            imported, skipped = import_products(session, api_products)
            print(f"  ✅ Imported: {imported}, Skipped: {skipped}")
        else:
            print(f"  ⚠️  File not found: {api_file}")
        
        # Import social media products
        social_file = input_path / 'social_media_products.json'
        if social_file.exists():
            print(f"\nImporting social media products from {social_file}...")
            with open(social_file, 'r', encoding='utf-8') as f:
                social_products = json.load(f)
            imported, skipped = import_social_media_products(session, social_products)
            print(f"  ✅ Imported: {imported}, Skipped: {skipped}")
        else:
            print(f"  ⚠️  File not found: {social_file}")
        
        # Import search queries
        queries_file = input_path / 'search_queries.json'
        if queries_file.exists():
            print(f"\nImporting search queries from {queries_file}...")
            with open(queries_file, 'r', encoding='utf-8') as f:
                queries = json.load(f)
            imported, skipped = import_search_queries(session, queries)
            print(f"  ✅ Imported: {imported}, Skipped: {skipped}")
        else:
            print(f"  ⚠️  File not found: {queries_file}")
        
        # Import collection logs
        logs_file = input_path / 'collection_logs.json'
        if logs_file.exists():
            print(f"\nImporting collection logs from {logs_file}...")
            with open(logs_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            imported, skipped = import_collection_logs(session, logs)
            print(f"  ✅ Imported: {imported}, Skipped: {skipped}")
        else:
            print(f"  ⚠️  File not found: {logs_file}")
    
    # Get final statistics
    with db_manager.get_session() as session:
        from src.ecommerce_search.database.models import get_database_stats
        stats = get_database_stats(session)
    
    print(f"\n✅ Dataset import completed successfully!")
    print(f"\nDatabase Statistics:")
    print(f"  - Products: {stats.get('products', 0):,}")
    print(f"  - Search Queries: {stats.get('search_queries', 0):,}")
    print(f"  - Collection Logs: {stats.get('collection_logs', 0):,}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Import dataset from JSON files')
    parser.add_argument(
        '--input-dir',
        type=str,
        default='dataset_export',
        help='Input directory containing JSON files (default: dataset_export)'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset database before importing (deletes all existing data)'
    )
    
    args = parser.parse_args()
    
    try:
        import_dataset(args.input_dir, args.reset)
    except Exception as e:
        print(f"❌ Error importing dataset: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

