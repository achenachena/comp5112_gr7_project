#!/usr/bin/env python3
"""
Walmart Open API Data Collection

This script collects REAL product data from Walmart's Open API.
NO API KEY REQUIRED for basic usage (limited requests).
"""

import json
import requests
import time
import os
from typing import List, Dict, Any


class WalmartAPICollector:
    """Collect real product data from Walmart Open API."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.collected_products = []
        self.product_ids = set()
    
    def search_products(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for products on Walmart using their Open API.
        
        Args:
            query: Search term (e.g., "iPhone case")
            max_results: Maximum number of results to return
            
        Returns:
            List of product dictionaries
        """
        print(f"🔍 Searching Walmart for: '{query}'")
        
        # Walmart Open API endpoint
        base_url = "https://developer.api.walmartlabs.com/v1/search"
        
        # Optional: Get a free API key from https://developer.walmartlabs.com/
        # This will give you more requests per minute
        api_key = os.getenv('WALMART_API_KEY', '')
        
        params = {
            'query': query,
            'format': 'json',
            'numItems': min(max_results, 25)  # Walmart limits to 25 per request
        }
        
        if api_key:
            params['apiKey'] = api_key
            print("  ✅ Using API key (higher rate limit)")
        else:
            print("  ⚠️  No API key (limited to 20 requests/minute)")
        
        try:
            response = requests.get(base_url, params=params, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                products = []
                
                for item in data.get('items', []):
                    product = self._format_product(item, query)
                    if product and product['id'] not in self.product_ids:
                        products.append(product)
                        self.product_ids.add(product['id'])
                
                print(f"  ✅ Found {len(products)} products")
                return products
                
            elif response.status_code == 429:
                print("  ⏰ Rate limit exceeded, waiting 60 seconds...")
                time.sleep(60)
                return self.search_products(query, max_results)  # Retry
                
            else:
                print(f"  ❌ Error {response.status_code}: {response.text[:100]}")
                return []
                
        except requests.exceptions.Timeout:
            print("  ⏰ Request timed out, trying again...")
            time.sleep(5)
            return []
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []
    
    def _format_product(self, item: Dict, search_query: str) -> Dict:
        """Format Walmart product data to our standard format."""
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
                'review_count': item.get('numReviews', 0)
            }
        except Exception as e:
            print(f"    Error formatting product: {e}")
            return None
    
    def collect_comprehensive_data(self, queries: List[str]) -> List[Dict]:
        """Collect data for multiple search queries."""
        print("🛒 Starting comprehensive Walmart data collection...")
        print("="*60)
        
        all_products = []
        
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Processing: '{query}'")
            
            products = self.search_products(query, max_results=15)
            all_products.extend(products)
            
            # Be respectful to the API
            if i < len(queries):  # Don't sleep after the last query
                print("  ⏳ Waiting 3 seconds before next search...")
                time.sleep(3)
        
        print(f"\n🎉 Collection complete!")
        print(f"📊 Total unique products: {len(all_products)}")
        
        return all_products


def main():
    """Main function to collect Walmart data."""
    print("🛒 Walmart Open API Data Collection")
    print("="*50)
    print()
    print("This script collects REAL product data from Walmart's Open API.")
    print("No API key required for basic usage (limited requests).")
    print()
    
    # Check if user wants to get an API key
    api_key = os.getenv('WALMART_API_KEY')
    if not api_key:
        print("💡 TIP: Get a free API key for higher rate limits:")
        print("   1. Go to: https://developer.walmartlabs.com/")
        print("   2. Sign up for a free account")
        print("   3. Create an app and get your API key")
        print("   4. Add to .env file: WALMART_API_KEY=your_key_here")
        print()
    
    # Define search queries for diverse product categories
    search_queries = [
        # Phone Accessories
        "iPhone case",
        "Samsung phone case",
        "phone screen protector",
        "wireless charger",
        "phone stand",
        
        # Electronics
        "Bluetooth headphones",
        "USB cable",
        "power bank",
        "laptop stand",
        "computer mouse",
        
        # Gaming
        "gaming headset",
        "gaming mouse",
        "mechanical keyboard",
        
        # Smart Home
        "smart speaker",
        "smart light bulb",
        
        # Fitness
        "fitness tracker",
        "smart watch"
    ]
    
    print(f"🔍 Will search for {len(search_queries)} product categories")
    print()
    
    # Collect data
    collector = WalmartAPICollector()
    products = collector.collect_comprehensive_data(search_queries)
    
    if products:
        # Save results
        os.makedirs('data', exist_ok=True)
        
        dataset = {
            'total_products': len(products),
            'source': 'walmart_open_api',
            'description': 'Real product data from Walmart Open API',
            'api_key_used': bool(api_key),
            'search_queries': search_queries,
            'products': products
        }
        
        output_file = 'data/walmart_products.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Data saved to: {output_file}")
        
        # Create summary
        categories = {}
        for product in products:
            cat = product['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        summary_file = 'data/walmart_summary.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Walmart API Data Collection Summary\n")
            f.write("="*50 + "\n\n")
            f.write(f"Total Products: {len(products)}\n")
            f.write(f"Source: Walmart Open API\n")
            f.write(f"API Key Used: {'Yes' if api_key else 'No'}\n")
            f.write(f"Output File: {output_file}\n\n")
            f.write("Categories:\n")
            for cat, count in sorted(categories.items()):
                f.write(f"  - {cat}: {count} products\n")
        
        print(f"📊 Summary saved to: {summary_file}")
        
        # Show sample products
        print("\n📋 Sample products:")
        for i, product in enumerate(products[:5], 1):
            print(f"  {i}. {product['title']}")
            print(f"     Price: ${product['price']['value']}")
            print(f"     Category: {product['category']}")
            print(f"     Brand: {product['brand']}")
            print()
        
        print("🎯 Next steps:")
        print("1. Test with your algorithms:")
        print(f"   python prototype/cli.py --mode compare --data {output_file}")
        print("2. Use in GUI:")
        print("   python web_gui.py")
        print("3. Load your Walmart dataset in the GUI")
        
    else:
        print("\n❌ No products collected!")
        print("This might be due to:")
        print("- Rate limiting (wait and try again)")
        print("- Network issues")
        print("- API changes")


if __name__ == "__main__":
    main()
