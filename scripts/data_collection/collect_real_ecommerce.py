#!/usr/bin/env python3
"""
Real E-commerce API Data Collection

This script collects REAL product data from genuine e-commerce APIs:
- Shopify Store APIs (various categories) - PRIMARY SOURCE
- Best Buy API (electronics, appliances) - OPTIONAL
- Target API (general merchandise) - OPTIONAL
- Newegg API (tech products) - OPTIONAL

Note: Current dataset is entirely from 200+ Shopify stores across multiple categories.
No fake/test APIs - only real marketplace data.
"""

import json
import requests
import time
import os
from typing import List, Dict, Any, Optional


class RealEcommerceCollector:
    """Collect real product data from genuine e-commerce APIs."""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.collected_products = []
        self.product_ids = set()

    def collect_from_bestbuy_api(
        self, search_queries: List[str], max_per_query: int = 10
    ) -> List[Dict]:
        """
        Collect from Best Buy API - REAL electronics and appliances.
        Get your free API key at: https://developer.bestbuy.com/
        """
        print("🛒 Collecting from Best Buy API (Real Electronics)...")

        api_key = os.getenv('BESTBUY_API_KEY')
        if not api_key:
            print("❌ BESTBUY_API_KEY not found!")
            print("   Get your free API key at: https://developer.bestbuy.com/")
            print("   Add to .env file: BESTBUY_API_KEY=your_key_here")
            return []

        products = []
        base_url = "https://api.bestbuy.com/v1/products"

        for query in search_queries:
            try:
                print(f"  Searching: {query}")

                # Best Buy API search endpoint
                search_url = f"{base_url}(search={query})"
                params = {
                    'apiKey': api_key,
                    'format': 'json',
                    'show': ('sku,name,salePrice,description,image,url,'
                            'categoryPath,brand,manufacturer'),
                    'pageSize': min(max_per_query, 25),
                    'sort': 'salePrice.asc'
                }

                response = requests.get(
                    search_url, params=params, headers=self.headers, timeout=15
                )

                if response.status_code == 200:
                    data = response.json()

                    for item in data.get('products', []):
                        product = self._format_bestbuy_product(item)
                        if product and product['id'] not in self.product_ids:
                            products.append(product)
                            self.product_ids.add(product['id'])

                    print(f"    ✅ Found {len(data.get('products', []))} products")
                else:
                    print(f"    ❌ Error {response.status_code}: {response.text[:100]}")

                time.sleep(2)  # Rate limiting

            except Exception as e:
                print(f"    ❌ Error with query '{query}': {e}")
                continue

        print(f"✅ Collected {len(products)} products from Best Buy API")
        return products

    def collect_from_target_api(
        self, search_queries: List[str], max_per_query: int = 10
    ) -> List[Dict]:
        """
        Collect from Target API - REAL retail products.
        Get your free API key at: https://developer.target.com/
        """
        print("🎯 Collecting from Target API (Real Retail Products)...")

        api_key = os.getenv('TARGET_API_KEY')
        if not api_key:
            print("❌ TARGET_API_KEY not found!")
            print("   Get your free API key at: https://developer.target.com/")
            print("   Add to .env file: TARGET_API_KEY=your_key_here")
            return []

        products = []

        for query in search_queries:
            try:
                print(f"  Searching: {query}")

                # Target API is more complex - would need product IDs
                # For now, we'll skip and focus on Best Buy
                print(f"    ⚠️  Target API requires product IDs - skipping")
                continue

            except Exception as e:
                print(f"    ❌ Error with query '{query}': {e}")
                continue

        print(f"✅ Collected {len(products)} products from Target API")
        return products

    def collect_from_newegg_api(
        self, search_queries: List[str], max_per_query: int = 10
    ) -> List[Dict]:
        """
        Collect from Newegg API - REAL tech products.
        Get your free API key at: https://developer.newegg.com/
        """
        print("💻 Collecting from Newegg API (Real Tech Products)...")

        api_key = os.getenv('NEWEGG_API_KEY')
        if not api_key:
            print("❌ NEWEGG_API_KEY not found!")
            print("   Get your free API key at: https://developer.newegg.com/")
            print("   Add to .env file: NEWEGG_API_KEY=your_key_here")
            return []

        products = []

        for query in search_queries:
            try:
                print(f"  Searching: {query}")
                print(f"    ⚠️  Newegg API implementation needed")
                continue

            except Exception as e:
                print(f"    ❌ Error with query '{query}': {e}")
                continue

        print(f"✅ Collected {len(products)} products from Newegg API")
        return products


    def collect_from_shopify_stores(
        self, max_per_query: int = 10
    ) -> List[Dict]:
        """
        Collect from public Shopify stores - REAL e-commerce data.
        No API key required for public stores.
        """
        print("🛍️ Collecting from Shopify Stores (Real E-commerce)...")

        # Example public Shopify stores (you can add more)
        shopify_stores = [
            'https://shop.polymer80.com',  # Firearms accessories
            'https://www.allbirds.com',    # Shoes
            'https://www.gymshark.com',    # Fitness apparel
        ]

        products = []

        for store_url in shopify_stores:
            try:
                print(f"  Checking store: {store_url}")

                # Shopify stores expose products via /products.json
                products_url = f"{store_url}/products.json"
                response = requests.get(products_url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    for item in data.get('products', [])[:max_per_query]:
                        product = self._format_shopify_product(item, store_url)
                        if product and product['id'] not in self.product_ids:
                            products.append(product)
                            self.product_ids.add(product['id'])
 
                    print(f"    ✅ Found {len(data.get('products', []))} products")
                else:
                    print(f"    ❌ Error {response.status_code}")

                time.sleep(2)  # Be respectful

            except Exception as e:
                print(f"    ❌ Error with store {store_url}: {e}")
                continue

        print(f"✅ Collected {len(products)} products from Shopify stores")
        return products

    def _format_bestbuy_product(self, item: Dict) -> Dict:
        """Format Best Buy product data."""
        try:
            return {
                'id': f"BESTBUY_{item.get('sku', '')}",
                'title': item.get('name', ''),
                'description': item.get('description', ''),
                'price': {
                    'value': f"{item.get('salePrice', 0):.2f}",
                    'currency': 'USD'
                },
                'category': item.get('categoryPath', 'Electronics'),
                'condition': 'New',
                'seller': {'username': 'Best Buy'},
                'location': 'Online',
                'url': item.get('url', ''),
                'image_url': item.get('image', ''),
                'brand': item.get('brand', item.get('manufacturer', '')),
                'source': 'bestbuy_api',
                'sku': item.get('sku', ''),
                'model': item.get('modelNumber', '')
            }
        except Exception as e:
            print(f"    Error formatting Best Buy product: {e}")
            return None

    def _format_shopify_product(self, item: Dict, store_url: str) -> Dict:
        """Format Shopify product data."""
        try:
            # Get the first variant for price
            variants = item.get('variants', [])
            price = 0
            if variants:
                price = float(variants[0].get('price', 0)) / 100  # Shopify prices in cents

            return {
                'id': f"SHOPIFY_{item.get('id', '')}",
                'title': item.get('title', ''),
                'description': item.get('body_html', ''),
                'price': {
                    'value': f"{price:.2f}",
                    'currency': 'USD'
                },
                'category': item.get('product_type', 'General'),
                'condition': 'New',
                'seller': {'username': store_url.split('//')[1].split('.')[0]},
                'location': 'Online',
                'url': f"{store_url}/products/{item.get('handle', '')}",
                'image_url': item.get('images', [{}])[0].get('src', ''),
                'brand': item.get('vendor', ''),
                'source': 'shopify_api',
                'tags': item.get('tags', ''),
                'variants_count': len(variants)
            }
        except Exception as e:
            print(f"    Error formatting Shopify product: {e}")
            return None


    def collect_all_real_apis(self, search_queries: List[str]) -> List[Dict]:
        """Collect from all available real e-commerce APIs."""
        print("🚀 Starting REAL e-commerce API data collection...")
        print("="*60)
        print("Collecting from genuine e-commerce APIs only!")
        print("No fake/test APIs - only real marketplace data.")
        print()

        all_products = []

        # Try Best Buy API first (most reliable)
        bestbuy_products = self.collect_from_bestbuy_api(search_queries)
        all_products.extend(bestbuy_products)


        # Try Target API
        target_products = self.collect_from_target_api(search_queries)
        all_products.extend(target_products)

        # Try Newegg API
        newegg_products = self.collect_from_newegg_api(search_queries)
        all_products.extend(newegg_products)

        # Try Shopify stores
        shopify_products = self.collect_from_shopify_stores()
        all_products.extend(shopify_products)

        print(f"\n🎉 Total REAL e-commerce products collected: {len(all_products)}")
        return all_products


def setup_api_keys():
    """Guide user through setting up API keys for real e-commerce APIs."""
    print("🔑 Real E-commerce API Setup Guide")
    print("="*50)
    print()
    print("To collect REAL e-commerce data, get API keys from these providers:")
    print()

    apis = [
        {
            'name': 'Best Buy API',
            'url': 'https://developer.bestbuy.com/',
            'description': 'Electronics, appliances, computers',
            'rate_limit': '5,000 requests/day',
            'difficulty': 'Easy',
            'recommended': '⭐ BEST OPTION'
        },
        {
            'description': 'General merchandise, electronics, groceries',
            'rate_limit': '5,000 requests/day',
            'difficulty': 'Easy',
            'recommended': '⭐ EXCELLENT OPTION'
        },
        {
            'name': 'Target API',
            'url': 'https://developer.target.com/',
            'description': 'General merchandise, retail products',
            'rate_limit': 'Varies by endpoint',
            'difficulty': 'Medium',
            'recommended': ''
        },
        {
            'name': 'Newegg API',
            'url': 'https://developer.newegg.com/',
            'description': 'Tech products, gaming, electronics',
            'rate_limit': 'Limited',
            'difficulty': 'Medium',
            'recommended': ''
        },
        {
            'name': 'Shopify Stores',
            'url': 'Public store APIs',
            'description': 'Various e-commerce stores',
            'rate_limit': 'No limit',
            'difficulty': 'Easy',
            'recommended': '⭐ NO API KEY NEEDED'
        }
    ]

    for api in apis:
        print(f"📌 {api['name']} {api['recommended']}")
        print(f"   URL: {api['url']}")
        print(f"   Products: {api['description']}")
        print(f"   Rate Limit: {api['rate_limit']}")
        print(f"   Difficulty: {api['difficulty']}")
        print()

    print("📝 Setup Instructions:")
    print("1. Get API keys from the websites above")
    print("2. Create .env file in your project root")
    print("3. Add your API keys:")
    print("   BESTBUY_API_KEY=your_key_here")
    print("   TARGET_API_KEY=your_key_here")
    print("   NEWEGG_API_KEY=your_key_here")
    print("4. Run: python collect_real_ecommerce.py")
    print()
    print("💡 RECOMMENDATION: Start with Best Buy API - "
          "it's free and has great data!")


def main():
    """Main function."""
    print("🛒 Real E-commerce API Data Collection")
    print("="*60)
    print("Collecting REAL product data from genuine e-commerce APIs")
    print("No fake/test APIs - only real marketplace data!")
    print()

    # Check for API keys
    api_keys = {
        'bestbuy': os.getenv('BESTBUY_API_KEY'),
        'target': os.getenv('TARGET_API_KEY'),
        'newegg': os.getenv('NEWEGG_API_KEY')
    }

    available_apis = [name for name, key in api_keys.items() if key]

    if not available_apis:
        print("❌ No API keys found!")
        print()
        setup_api_keys()
        return

    print(f"✅ Found API keys for: {', '.join(available_apis)}")
    print()

    # Define search queries for real e-commerce data
    search_queries = [
        # Electronics
        "iPhone",
        "Samsung Galaxy",
        "laptop",
        "tablet",
        "headphones",

        # Gaming
        "gaming mouse",
        "mechanical keyboard",
        "gaming headset",
        "gaming controller",

        # Home & Kitchen
        "smart speaker",
        "wireless charger",
        "bluetooth speaker",
        "smart home",

        # Computers
        "graphics card",
        "computer monitor",
        "webcam",
        "external hard drive"
    ]

    print(f"🔍 Will search for {len(search_queries)} product categories")
    print()

    # Collect data
    collector = RealEcommerceCollector()
    products = collector.collect_all_real_apis(search_queries)

    if products:
        # Save results
        os.makedirs('data', exist_ok=True)

        dataset = {
            'total_products': len(products),
            'source': 'real_ecommerce_apis',
            'description': 'Real product data from genuine e-commerce APIs',
            'apis_used': available_apis,
            'search_queries': search_queries,
            'products': products
        }

        output_file = 'data/real_ecommerce_products.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Real e-commerce data saved to: {output_file}")
        print(f"📊 Total products: {len(products)}")

        # Create summary
        sources = {}
        categories = {}

        for product in products:
            # Source breakdown
            source = product.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1

            # Category breakdown
            category = product.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1

        summary_file = 'data/real_ecommerce_summary.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Real E-commerce API Data Collection Summary\n")
            f.write("="*60 + "\n\n")
            f.write(f"Total Products: {len(products)}\n")
            f.write(f"Source: Real E-commerce APIs\n")
            f.write(f"Output File: {output_file}\n\n")

            f.write("APIs Used:\n")
            for source, count in sources.items():
                f.write(f"  - {source}: {count} products\n")

            f.write(f"\nCategories:\n")
            for cat, count in sorted(categories.items()):
                f.write(f"  - {cat}: {count} products\n")

        print(f"📊 Summary saved to: {summary_file}")

        # Show sample products
        print("\n📋 Sample REAL products:")
        for i, product in enumerate(products[:5], 1):
            print(f"  {i}. {product['title']}")
            print(f"     Price: ${product['price']['value']}")
            print(f"     Category: {product['category']}")
            print(f"     Source: {product['source']}")
            print()

        print("🎯 Next steps:")
        print("1. Test with your algorithms:")
        print(f"   python src/ecommerce_search/cli.py compare")
        print("2. Use web interface:")
        print("   python src/ecommerce_search/web/app.py")
        print("3. Load your real e-commerce dataset in the GUI")

    else:
        print("\n❌ No products collected!")
        print("This might be due to:")
        print("- Missing API keys")
        print("- Network issues")
        print("- API rate limits")
        print()
        print("Try getting a Best Buy API key first - it's the easiest to set up!")


if __name__ == "__main__":
    main()
