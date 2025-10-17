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

from config.api_config import APIConfig

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
        
        api_key = APIConfig.BESTBUY_API_KEY
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
                    logger.info("  Searching: %s", query)
                    
                    # Best Buy API search
                    search_url = f"{base_url}(search={query})"
                    params = {
                        'apiKey': api_key,
                        'format': 'json',
                        'show': ('sku,name,salePrice,description,image,url,'
                                'categoryPath,brand,manufacturer,modelNumber'),
                        'pageSize': min(max_per_query, 25),
                        'sort': 'salePrice.asc'
                    }
                    
                    response = requests.get(
                        search_url, params=params, headers=self.headers, timeout=15
                    )
                    
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
                        
                        logger.info("    ✅ Found %d products, %d new", 
                                   len(data.get('products', [])), products_in_query)
                        
                    else:
                        failed_requests += 1
                        logger.error("    ❌ Error %d", response.status_code)
                    
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
                    
                    time.sleep(APIConfig.API_DELAY)  # Rate limiting
                    
                except Exception as e:
                    failed_requests += 1
                    logger.error("    ❌ Error with query '%s': %s", query, e)
                    
                    # Log error
                    log_entry = DataCollectionLog(
                        api_source='bestbuy_api',
                        search_query=query,
                        products_collected=0,
                        successful_requests=0,
                        failed_requests=failed_requests,
                        error_message=str(e),
                        collection_time_seconds=(
                            datetime.utcnow() - collection_start
                        ).total_seconds()
                    )
                    session.add(log_entry)
                    continue
        
        logger.info("✅ Collected %d new products from Best Buy API", products_collected)
        return products_collected
    
    def collect_from_walmart_api(self, search_queries: List[str], max_per_query: int = 25) -> int:
        """
        Collect from Walmart Open API and store in database.
        Returns number of products collected.
        """
        logger.info("🛒 Starting Walmart API collection...")
        
        api_key = APIConfig.WALMART_API_KEY
        if not api_key:
            logger.info("❌ WALMART_API_KEY not found - skipping Walmart collection")
            return 0
        
        products_collected = 0
        base_url = "https://marketplace.walmartapis.com/v3/items"
        
        for query in search_queries:
            try:
                logger.info("  Searching Walmart for: %s", query)
                collection_start = datetime.utcnow()
                
                params = {
                    'query': query,
                    'format': 'json',
                    'numItems': min(max_per_query, 25),
                    'apiKey': api_key
                }
                
                response = requests.get(base_url, params=params, headers=self.headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    with self.db_manager.get_session() as session:
                        for item in items:
                            try:
                                # Check if product already exists
                                existing_product = session.query(Product).filter_by(
                                    external_id=f"WALMART_{item.get('itemId', '')}"
                                ).first()
                                
                                if existing_product:
                                    continue
                                
                                # Format product data
                                product = self._format_walmart_product(item, query)
                                if not product:
                                    continue
                                
                                # Create database product
                                db_product = Product(
                                    external_id=product['id'],
                                    title=product['title'],
                                    description=product['description'],
                                    category=product['category'],
                                    price_value=float(product['price']['value']),
                                    price_currency=product['price']['currency'],
                                    brand=product['brand'],
                                    model=product['model'],
                                    condition=product['condition'],
                                    seller_name=product['seller']['username'],
                                    seller_location=product['location'],
                                    product_url=product['url'],
                                    image_url=product['image_url'],
                                    source=product['source'],
                                    rating=product.get('rating', 0),
                                    review_count=product.get('review_count', 0),
                                    tags=product.get('tags', ''),
                                    created_at=datetime.utcnow()
                                )
                                
                                session.add(db_product)
                                products_collected += 1
                                
                            except Exception as e:
                                logger.warning("    Error processing Walmart product: %s", e)
                                continue
                        
                        session.commit()
                        
                        # Log collection
                        log_entry = DataCollectionLog(
                            source='walmart_api',
                            query=query,
                            products_collected=len(items),
                            success=True,
                            error_message=None,
                            collection_time_seconds=(
                                datetime.utcnow() - collection_start
                            ).total_seconds()
                        )
                        session.add(log_entry)
                        session.commit()
                    
                    logger.info("    ✅ Found %d products", len(items))
                    
                elif response.status_code == 429:
                    logger.warning("    ⏰ Rate limit exceeded, waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    logger.warning("    ❌ Error %d: %s", response.status_code, response.text[:100])
                    continue
                
                time.sleep(APIConfig.API_DELAY)
                
            except Exception as e:
                logger.error("    ❌ Error with query '%s': %s", query, e)
                # Log failed collection
                try:
                    with self.db_manager.get_session() as session:
                        log_entry = DataCollectionLog(
                            source='walmart_api',
                            query=query,
                            products_collected=0,
                            success=False,
                            error_message=str(e),
                            collection_time_seconds=(
                                datetime.utcnow() - collection_start
                            ).total_seconds()
                        )
                        session.add(log_entry)
                        session.commit()
                except Exception:
                    pass
                continue
        
        logger.info("✅ Collected %d new products from Walmart API", products_collected)
        return products_collected
    
    def collect_from_shopify_stores(
        self, search_queries: List[str], max_per_store: int = 1000
    ) -> int:
        """
        Collect from public Shopify stores and store in database.
        Returns number of products collected.
        
        Note: This method will attempt pagination to collect more products from each store.
        """
        logger.info("🛍️ Collecting from Shopify Stores with Pagination...")
        
        # Extensive list of Shopify stores for 100K+ product collection
        # Organized by category for maximum diversity
        shopify_stores = APIConfig.get_shopify_stores()
    
        products_collected = 0

        with self.db_manager.get_session() as session:
            for store_url in shopify_stores:
                collection_start = datetime.utcnow()
                successful_requests = 0
                failed_requests = 0
                products_in_store = 0

                try:
                    logger.info("  Checking store: %s", store_url)

                    # Shopify pagination - collect products page by page
                    page = 1
                    total_found = 0

                    while products_in_store < max_per_store:
                        # Shopify stores expose products via /products.json with pagination
                        products_url = f"{store_url}/products.json?page={page}&limit=250"
                        response = requests.get(products_url, headers=self.headers, timeout=10)

                        if response.status_code == 200:
                            data = response.json()
                            products_list = data.get('products', [])

                            if not products_list:
                                # No more products, exit pagination
                                break

                            successful_requests += 1
                            total_found += len(products_list)

                            for item in products_list:
                                if products_in_store >= max_per_store:
                                    break

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
                            
                            # If we got fewer than 250 products, this is the last page
                            if len(products_list) < 250:
                                break

                            page += 1
                            # Delay between pages to avoid rate limiting
                            time.sleep(APIConfig.API_DELAY)

                        else:
                            failed_requests += 1
                            logger.error("    ❌ Error %d", response.status_code)
                            break

                    if products_in_store > 0:
                        logger.info("    ✅ Found %d products across %d page(s), %d new", 
                                   total_found, page, products_in_store)

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

                    # Longer delay between stores for 100K collection
                    time.sleep(APIConfig.API_DELAY * 3)

                except Exception as e:
                    failed_requests += 1
                    logger.error("    ❌ Error with store %s: %s", store_url, e)
       
                    # Log error
                    log_entry = DataCollectionLog(
                        api_source='shopify_api',
                        search_query=store_url,
                        products_collected=0,
                        successful_requests=0,
                        failed_requests=failed_requests,
                        error_message=str(e),
                        collection_time_seconds=(datetime.utcnow()
                         - collection_start).total_seconds()
                    )
                    session.add(log_entry)
                    continue
        
        logger.info("✅ Collected %d new products from Shopify stores", products_collected)
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
                'category': self._extract_category_from_path(
                    item.get('categoryPath', 'Electronics')
                ),
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
            logger.error("Error formatting Best Buy product: %s", e)
            return None

    def _format_walmart_product(self, item: Dict, search_query: str) -> Optional[Dict]:
        """Format Walmart product data for database storage."""
        try:
            # Extract price information
            sale_price = item.get('salePrice', 0)
            msrp = item.get('msrp', 0)
            price = sale_price if sale_price > 0 else msrp

            # Extract category
            category_path = item.get('categoryPath', '')
            if 'Electronics' in category_path:
                category = 'Electronics'
            elif 'Cell Phones' in category_path:
                category = 'Phone Accessories'
            elif 'Computers' in category_path:
                category = 'Computer Accessories'
            elif 'Gaming' in category_path:
                category = 'Gaming'
            elif 'Smart Home' in category_path:
                category = 'Smart Home'
            else:
                category = 'General'

            return {
                'id': f"WALMART_{item.get('itemId', '')}",
                'title': item.get('name', ''),
                'description': item.get('shortDescription', ''),
                'price': {
                    'value': f"{price:.2f}",
                    'currency': 'USD'
                },
                'category': category,
                'condition': 'New',
                'seller': {'username': 'Walmart'},
                'location': item.get('city', 'Online'),
                'url': item.get('productUrl', ''),
                'image_url': item.get('largeImage', ''),
                'brand': item.get('brandName', ''),
                'source': 'walmart_api',
                'search_query': search_query,
                'rating': item.get('customerRating', 0),
                'review_count': item.get('numReviews', 0),
                'model': item.get('modelNumber', ''),
                'sku': item.get('itemId', ''),
                'tags': f"walmart,{search_query},{category.lower()}"
            }
        except Exception as e:
            logger.error("Error formatting Walmart product: %s", e)
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
                'image_url': (
                    item.get('images', [{}])[0].get('src', '') 
                    if item.get('images') else ''
                ),
                'product_url': f"{store_url}/products/{item.get('handle', '')}",
                'tags': json.dumps(item.get('tags', [])) if item.get('tags') else None,
                'rating': None,
                'review_count': None,
            }
        except Exception as e:
            logger.error("Error formatting Shopify product: %s", e)
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

            logger.info("✅ Created %d new search queries", created_count)

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
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='E-commerce Data Collection Tool')
    parser.add_argument('--mode', choices=['api', 'social', 'both'], default='api',
                       help='Collection mode: api (API-based), social (social media), both')
    parser.add_argument('--api-sources', nargs='+', choices=['walmart', 'shopify'], 
                       default=['walmart', 'shopify'],
                       help='API sources to use (default: walmart shopify)')
    parser.add_argument('--social-sources', nargs='+', choices=['reddit', 'twitter'], 
                       default=['reddit'],
                       help='Social media sources to use (default: reddit)')
    parser.add_argument('--max-products', type=int, default=50000,
                       help='Maximum products to collect (default: 50000)')
    
    args = parser.parse_args()
    
    print("🛒 E-commerce Database Collection")
    print("="*60)
    print("Collecting REAL product data and storing in SQL database")
    print("Perfect for large-scale research with hundreds of thousands of products!")
    print(f"📋 Collection Mode: {args.mode.upper()}")
    print(f"🎯 Target: {args.max_products:,} products")
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

    # Collect data based on selected mode
    total_collected = 0
    
    if args.mode in ['api', 'both']:
        print("🔌 Starting API-based data collection...")
        api_collected = 0
        
        if 'walmart' in args.api_sources:
            print("  🛒 Collecting from Walmart API...")
            walmart_count = collector.collect_from_walmart_api(search_queries)
            api_collected += walmart_count
            print(f"    ✅ Walmart: {walmart_count:,} products")
        
        if 'shopify' in args.api_sources:
            print("  🛍️ Collecting from Shopify stores...")
            shopify_count = collector.collect_from_shopify_stores(search_queries)
            api_collected += shopify_count
            print(f"    ✅ Shopify: {shopify_count:,} products")
        
        total_collected += api_collected
        print(f"  📊 API Collection Total: {api_collected:,} products")
    
    if args.mode in ['social', 'both']:
        print("\n📱 Starting Social Media scraping...")
        try:
            from social_media_scraper import SocialMediaScraper, ScrapingConfig
            
            # Initialize social media scraper with default config
            config = ScrapingConfig()
            social_collector = SocialMediaScraper(config)
            social_collected = 0
            
            if 'reddit' in args.social_sources:
                print("  🔴 Collecting from Reddit...")
                reddit_count = social_collector.scrape_reddit_posts()
                social_collected += reddit_count
                print(f"    ✅ Reddit: {reddit_count:,} posts")
            
            if 'twitter' in args.social_sources:
                print("  🐦 Collecting from Twitter...")
                twitter_count = social_collector.scrape_twitter_posts()
                social_collected += twitter_count
                print(f"    ✅ Twitter: {twitter_count:,} posts")
            
            total_collected += social_collected
            print(f"  📊 Social Media Total: {social_collected:,} posts")
            
        except ImportError as e:
            print(f"  ⚠️  Social media scraping not available: {e}")
            print("  💡 Install required packages: pip install praw tweepy textblob")
    
    # Check if we've reached the target
    if total_collected >= args.max_products:
        print(f"\n🎯 Target reached! Collected {total_collected:,} products (target: {args.max_products:,})")
    else:
        print(f"\n📈 Progress: {total_collected:,}/{args.max_products:,} products ({total_collected/args.max_products*100:.1f}%)")

    # Show final statistics
    print("\n" + "="*60)
    print("🎉 Data Collection Complete!")
    print("="*60)
    print(f"📋 Mode: {args.mode.upper()}")
    print(f"📊 Total new items collected: {total_collected:,}")

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
            print(f"  Price Range: ${price_range.get('min', 0):.2f} - "
                  f"${price_range.get('max', 0):.2f}")

    print("\n🎯 Next steps:")
    print("1. Run search algorithms on database:")
    print("   python run_database_search.py")
    print("2. Analyze results:")
    print("   python analyze_database_results.py")
    print("3. View database:")
    print("   python -c \"from database.db_manager import get_db_manager; "
          "print(get_db_manager().get_database_info())\"")


if __name__ == "__main__":
    main()
