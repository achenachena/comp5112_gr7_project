#!/usr/bin/env python3
"""
Real E-commerce API Data Collection with Database Storage

This script collects REAL product data from genuine e-commerce APIs
and stores it in a SQL database for large-scale research.
"""

import json
import requests
import time
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import get_db_manager, get_session
from database.models import Product, SearchQuery, DataCollectionLog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseEcommerceCollector:
    """Collect real product data and store in database."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.db_manager = get_db_manager()
        
        # Initialize database if needed
        try:
            with self.db_manager.get_session() as session:
                pass  # Test connection
        except Exception as e:
            logger.info("Initializing database...")
            self.db_manager.create_tables()
    
    def collect_from_bestbuy_api(self, search_queries: List[str], max_per_query: int = 25) -> int:
        """
        Collect from Best Buy API and store in database.
        Returns number of products collected.
        """
        logger.info("🛒 Collecting from Best Buy API...")
        
        api_key = os.getenv('BESTBUY_API_KEY')
        if not api_key:
            logger.error("❌ BESTBUY_API_KEY not found!")
            logger.info("   Get your free API key at: https://developer.bestbuy.com/")
            return 0
        
        products_collected = 0
        base_url = "https://api.bestbuy.com/v1/products"
        
        with self.db_manager.get_session() as session:
            for query in search_queries:
                collection_start = datetime.utcnow()
                successful_requests = 0
                failed_requests = 0
                products_in_query = 0
                
                try:
                    logger.info(f"  Searching: {query}")
                    
                    # Best Buy API search
                    search_url = f"{base_url}(search={query})"
                    params = {
                        'apiKey': api_key,
                        'format': 'json',
                        'show': 'sku,name,salePrice,description,image,url,categoryPath,brand,manufacturer,modelNumber',
                        'pageSize': min(max_per_query, 25),
                        'sort': 'salePrice.asc'
                    }
                    
                    response = requests.get(search_url, params=params, headers=self.headers, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        successful_requests += 1
                        
                        for item in data.get('products', []):
                            product = self._format_bestbuy_product(item)
                            if product:
                                # Check if product already exists
                                existing = session.query(Product).filter_by(
                                    external_id=product['external_id']
                                ).first()
                                
                                if not existing:
                                    db_product = Product(**product)
                                    session.add(db_product)
                                    products_in_query += 1
                                    products_collected += 1
                        
                        logger.info(f"    ✅ Found {len(data.get('products', []))} products, {products_in_query} new")
                        
                    else:
                        failed_requests += 1
                        logger.error(f"    ❌ Error {response.status_code}")
                    
                    # Log collection activity
                    collection_time = (datetime.utcnow() - collection_start).total_seconds()
                    log_entry = DataCollectionLog(
                        api_source='bestbuy_api',
                        search_query=query,
                        products_collected=products_in_query,
                        successful_requests=successful_requests,
                        failed_requests=failed_requests,
                        collection_time_seconds=collection_time,
                        api_response_code=response.status_code if response else None
                    )
                    session.add(log_entry)
                    
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    failed_requests += 1
                    logger.error(f"    ❌ Error with query '{query}': {e}")
                    
                    # Log error
                    log_entry = DataCollectionLog(
                        api_source='bestbuy_api',
                        search_query=query,
                        products_collected=0,
                        successful_requests=0,
                        failed_requests=failed_requests,
                        error_message=str(e),
                        collection_time_seconds=(datetime.utcnow() - collection_start).total_seconds()
                    )
                    session.add(log_entry)
                    continue
        
        logger.info(f"✅ Collected {products_collected} new products from Best Buy API")
        return products_collected
    
    def collect_from_shopify_stores(self, search_queries: List[str], max_per_store: int = 50) -> int:
        """
        Collect from public Shopify stores and store in database.
        Returns number of products collected.
        """
        logger.info("🛍️ Collecting from Shopify Stores...")
        
        # Public Shopify stores (you can add more)
        shopify_stores = [
            'https://shop.polymer80.com',
            'https://www.allbirds.com',
            'https://www.gymshark.com',
            'https://www.casper.com',
            'https://www.bombas.com',
        ]
        
        products_collected = 0
        
        with self.db_manager.get_session() as session:
            for store_url in shopify_stores:
                collection_start = datetime.utcnow()
                successful_requests = 0
                failed_requests = 0
                products_in_store = 0
                
                try:
                    logger.info(f"  Checking store: {store_url}")
                    
                    # Shopify stores expose products via /products.json
                    products_url = f"{store_url}/products.json"
                    response = requests.get(products_url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        successful_requests += 1
                        
                        for item in data.get('products', [])[:max_per_store]:
                            product = self._format_shopify_product(item, store_url)
                            if product:
                                # Check if product already exists
                                existing = session.query(Product).filter_by(
                                    external_id=product['external_id']
                                ).first()
                                
                                if not existing:
                                    db_product = Product(**product)
                                    session.add(db_product)
                                    products_in_store += 1
                                    products_collected += 1
                        
                        logger.info(f"    ✅ Found {len(data.get('products', []))} products, {products_in_store} new")
                        
                    else:
                        failed_requests += 1
                        logger.error(f"    ❌ Error {response.status_code}")
                    
                    # Log collection activity
                    collection_time = (datetime.utcnow() - collection_start).total_seconds()
                    log_entry = DataCollectionLog(
                        api_source='shopify_api',
                        search_query=store_url,
                        products_collected=products_in_store,
                        successful_requests=successful_requests,
                        failed_requests=failed_requests,
                        collection_time_seconds=collection_time,
                        api_response_code=response.status_code if response else None
                    )
                    session.add(log_entry)
                    
                    time.sleep(2)  # Be respectful
                    
                except Exception as e:
                    failed_requests += 1
                    logger.error(f"    ❌ Error with store {store_url}: {e}")
                    
                    # Log error
                    log_entry = DataCollectionLog(
                        api_source='shopify_api',
                        search_query=store_url,
                        products_collected=0,
                        successful_requests=0,
                        failed_requests=failed_requests,
                        error_message=str(e),
                        collection_time_seconds=(datetime.utcnow() - collection_start).total_seconds()
                    )
                    session.add(log_entry)
                    continue
        
        logger.info(f"✅ Collected {products_collected} new products from Shopify stores")
        return products_collected
    
    def _format_bestbuy_product(self, item: Dict) -> Optional[Dict]:
        """Format Best Buy product data for database storage."""
        try:
            return {
                'external_id': f"bestbuy_{item.get('sku', '')}",
                'source': 'bestbuy_api',
                'title': item.get('name', ''),
                'description': item.get('description', ''),
                'brand': item.get('brand', item.get('manufacturer', '')),
                'model': item.get('modelNumber', ''),
                'sku': item.get('sku', ''),
                'price_value': float(item.get('salePrice', 0)),
                'price_currency': 'USD',
                'category': self._extract_category_from_path(item.get('categoryPath', 'Electronics')),
                'condition': 'New',
                'availability': 'In Stock',
                'seller_name': 'Best Buy',
                'seller_location': 'Online',
                'image_url': item.get('image', ''),
                'product_url': item.get('url', ''),
                'rating': None,  # Best Buy API doesn't provide ratings in search
                'review_count': None,
            }
        except Exception as e:
            logger.error(f"Error formatting Best Buy product: {e}")
            return None
    
    def _format_shopify_product(self, item: Dict, store_url: str) -> Optional[Dict]:
        """Format Shopify product data for database storage."""
        try:
            # Get the first variant for price
            variants = item.get('variants', [])
            price = 0
            if variants:
                price = float(variants[0].get('price', 0)) / 100  # Shopify prices in cents
            
            # Extract store name from URL
            store_name = store_url.split('//')[1].split('.')[0]
            
            return {
                'external_id': f"shopify_{item.get('id', '')}",
                'source': 'shopify_api',
                'title': item.get('title', ''),
                'description': item.get('body_html', ''),
                'brand': item.get('vendor', ''),
                'model': '',
                'sku': variants[0].get('sku', '') if variants else '',
                'price_value': price,
                'price_currency': 'USD',
                'category': item.get('product_type', 'General'),
                'condition': 'New',
                'availability': 'In Stock',
                'seller_name': store_name,
                'seller_location': 'Online',
                'image_url': item.get('images', [{}])[0].get('src', '') if item.get('images') else '',
                'product_url': f"{store_url}/products/{item.get('handle', '')}",
                'tags': json.dumps(item.get('tags', [])) if item.get('tags') else None,
                'rating': None,
                'review_count': None,
            }
        except Exception as e:
            logger.error(f"Error formatting Shopify product: {e}")
            return None
    
    def _extract_category_from_path(self, category_path: str) -> str:
        """Extract main category from Best Buy's categoryPath."""
        if not category_path:
            return 'Electronics'
        
        # Best Buy categoryPath format: "abcat > abcat0500000 > abcat0501000"
        categories = category_path.split(' > ')
        if categories:
            # Use the last category as it's usually the most specific
            return categories[-1].replace('abcat', '').replace('0', ' ').strip()
        
        return 'Electronics'
    
    def create_search_queries(self, queries: List[str]):
        """Create search query records in the database."""
        logger.info("📝 Creating search query records...")
        
        with self.db_manager.get_session() as session:
            created_count = 0
            
            for query_text in queries:
                # Check if query already exists
                existing = session.query(SearchQuery).filter_by(query_text=query_text).first()
                
                if not existing:
                    # Determine category and difficulty
                    category = self._categorize_query(query_text)
                    difficulty = self._assess_difficulty(query_text)
                    
                    search_query = SearchQuery(
                        query_text=query_text,
                        category=category,
                        difficulty=difficulty
                    )
                    session.add(search_query)
                    created_count += 1
            
            logger.info(f"✅ Created {created_count} new search queries")
    
    def _categorize_query(self, query: str) -> str:
        """Categorize search query based on content."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['iphone', 'samsung', 'phone', 'mobile']):
            return 'Mobile'
        elif any(word in query_lower for word in ['laptop', 'computer', 'pc', 'mac']):
            return 'Computers'
        elif any(word in query_lower for word in ['gaming', 'game', 'controller']):
            return 'Gaming'
        elif any(word in query_lower for word in ['audio', 'headphone', 'speaker']):
            return 'Audio'
        elif any(word in query_lower for word in ['smart', 'home', 'iot']):
            return 'Smart Home'
        else:
            return 'General'
    
    def _assess_difficulty(self, query: str) -> str:
        """Assess search query difficulty."""
        if len(query.split()) == 1:
            return 'Easy'
        elif len(query.split()) <= 3:
            return 'Medium'
        else:
            return 'Hard'
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get current database statistics."""
        with self.db_manager.get_session() as session:
            return self.db_manager.get_database_info()


def main():
    """Main function for database-based data collection."""
    print("🛒 Real E-commerce Database Collection")
    print("="*60)
    print("Collecting REAL product data and storing in SQL database")
    print("Perfect for large-scale research with hundreds of thousands of products!")
    print()
    
    # Initialize collector
    collector = DatabaseEcommerceCollector()
    
    # Define search queries for comprehensive data collection
    search_queries = [
        # Mobile & Electronics
        "iPhone", "Samsung Galaxy", "Google Pixel", "OnePlus",
        "wireless charger", "phone case", "screen protector",
        
        # Computers & Gaming
        "laptop", "MacBook", "gaming mouse", "mechanical keyboard",
        "gaming headset", "graphics card", "computer monitor",
        
        # Audio & Smart Home
        "Bluetooth headphones", "wireless earbuds", "smart speaker",
        "smart home", "smart light", "security camera",
        
        # General Electronics
        "tablet", "iPad", "smartwatch", "fitness tracker",
        "USB cable", "power bank", "external hard drive",
        
        # Gaming
        "gaming controller", "gaming laptop", "gaming desk",
        "RGB lighting", "gaming chair",
        
        # Home & Kitchen
        "smart thermostat", "robot vacuum", "air purifier",
        "blender", "coffee maker", "microwave",
    ]
    
    print(f"🔍 Will collect data for {len(search_queries)} search categories")
    print()
    
    # Create search query records
    collector.create_search_queries(search_queries)
    
    # Collect data from APIs
    total_collected = 0
    
    # Try Best Buy API
    bestbuy_count = collector.collect_from_bestbuy_api(search_queries[:10])  # Limit for demo
    total_collected += bestbuy_count
    
    # Try Shopify stores
    shopify_count = collector.collect_from_shopify_stores(search_queries[:5])  # Limit for demo
    total_collected += shopify_count
    
    # Show final statistics
    print("\n" + "="*60)
    print("🎉 Data Collection Complete!")
    print("="*60)
    print(f"📊 Total new products collected: {total_collected}")
    
    # Get database stats
    stats = collector.get_database_stats()
    print(f"📁 Database: {stats['database_type']}")
    print(f"🔗 Location: {stats['database_url']}")
    
    if 'stats' in stats:
        db_stats = stats['stats']
        print(f"\n📈 Database Statistics:")
        print(f"  Total Products: {db_stats.get('products', 0)}")
        print(f"  Search Queries: {db_stats.get('search_queries', 0)}")
        print(f"  Data Sources: {db_stats.get('unique_sources', 0)}")
        print(f"  Categories: {db_stats.get('unique_categories', 0)}")
        
        if 'price_range' in db_stats:
            price_range = db_stats['price_range']
            print(f"  Price Range: ${price_range.get('min', 0):.2f} - ${price_range.get('max', 0):.2f}")
    
    print("\n🎯 Next steps:")
    print("1. Run search algorithms on database:")
    print("   python run_database_search.py")
    print("2. Analyze results:")
    print("   python analyze_database_results.py")
    print("3. View database:")
    print("   python -c \"from database.db_manager import get_db_manager; print(get_db_manager().get_database_info())\"")


if __name__ == "__main__":
    main()
