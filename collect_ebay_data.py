#!/usr/bin/env python3
"""
Script to collect product data from eBay API for search algorithm research.
This script collects products for various categories and saves them to JSON files.
"""

import json
import os
import time
from data_collection.ebay_client import EbayAPIClient


def collect_data_for_queries(client, queries, products_per_query=20, output_dir='data'):
    """
    Collect product data for multiple search queries.
    
    Args:
        client: EbayAPIClient instance
        queries: List of search queries
        products_per_query: Number of products to collect per query
        output_dir: Directory to save collected data
    """
    os.makedirs(output_dir, exist_ok=True)
    
    all_products = []
    product_ids = set()  # Track unique product IDs to avoid duplicates
    
    print("="*60)
    print("eBay Product Data Collection")
    print("="*60)
    print(f"Queries: {len(queries)}")
    print(f"Products per query: {products_per_query}")
    print()
    
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Collecting data for: '{query}'")
        
        try:
            # Search for products
            results = client.search_and_format(
                query=query,
                limit=products_per_query,
                sort="BestMatch"
            )
            
            # Extract products
            products = results.get('products', [])
            
            # Add unique products
            new_products = 0
            for product in products:
                product_id = product.get('item_id')
                if product_id and product_id not in product_ids:
                    # Add query metadata
                    product['source_query'] = query
                    all_products.append(product)
                    product_ids.add(product_id)
                    new_products += 1
            
            print(f"  ✓ Found {len(products)} products ({new_products} unique)")
            
            # Be nice to the API - add delay between requests
            time.sleep(1)
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue
    
    print()
    print("="*60)
    print(f"Total unique products collected: {len(all_products)}")
    print("="*60)
    
    # Save all products to JSON file
    output_file = os.path.join(output_dir, 'ebay_products.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_products': len(all_products),
            'queries': queries,
            'products': all_products
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Data saved to: {output_file}")
    
    # Save summary statistics
    summary_file = os.path.join(output_dir, 'collection_summary.txt')
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("eBay Product Data Collection Summary\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total Products Collected: {len(all_products)}\n")
        f.write(f"Total Queries: {len(queries)}\n")
        f.write(f"Products per Query (target): {products_per_query}\n\n")
        f.write("Queries:\n")
        for query in queries:
            f.write(f"  - {query}\n")
    
    print(f"✓ Summary saved to: {summary_file}")
    
    return all_products


def main():
    """Main function to run data collection."""
    
    # Initialize eBay API client
    print("Initializing eBay API client...")
    client = EbayAPIClient()
    
    # Check if OAuth token is available
    if not client.oauth_token:
        print("\n" + "="*60)
        print("ERROR: eBay OAuth token not found!")
        print("="*60)
        print("\nTo collect data from eBay API, you need to:")
        print("1. Create an eBay Developer account at https://developer.ebay.com/")
        print("2. Create an application and get your credentials")
        print("3. Generate an OAuth token")
        print("4. Create a .env file with your credentials")
        print("\nSee setup_guide.md for detailed instructions.")
        print("\nAlternatively, you can use the sample data already in the project.")
        return
    
    print("✓ OAuth token found\n")
    
    # Define search queries for diverse product categories
    search_queries = [
        # Phone accessories
        "iPhone case",
        "Samsung Galaxy case",
        "phone screen protector",
        "wireless charger",
        
        # Electronics
        "laptop case",
        "MacBook accessories",
        "iPad case",
        "tablet stand",
        
        # Mobile accessories
        "USB-C cable",
        "phone holder car",
        "power bank",
        "Bluetooth headphones",
        
        # Specialized accessories
        "Apple Watch band",
        "AirPods case",
        "gaming controller",
        "portable speaker"
    ]
    
    # Collect data
    products = collect_data_for_queries(
        client=client,
        queries=search_queries,
        products_per_query=20,
        output_dir='data'
    )
    
    # Print sample products
    if products:
        print("\n" + "="*60)
        print("Sample Products (first 3):")
        print("="*60)
        for i, product in enumerate(products[:3], 1):
            print(f"\n{i}. {product.get('title', 'N/A')}")
            price = product.get('price', {})
            print(f"   Price: {price.get('value', 'N/A')} {price.get('currency', '')}")
            print(f"   Source Query: {product.get('source_query', 'N/A')}")
            print(f"   Condition: {product.get('condition', 'N/A')}")


if __name__ == "__main__":
    main()


