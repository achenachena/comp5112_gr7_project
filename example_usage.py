#!/usr/bin/env python3
"""
Example script demonstrating how to use the eBay API client
to collect product data and get JSON results.
"""

import json
from data_collection.ebay_client import EbayAPIClient


def search_iphone_cases():
    """Example: Search for iPhone cases and return JSON results."""
    client = EbayAPIClient()

    print("Searching for 'iPhone case' on eBay...")
    print("=" * 50)

    # Search for iPhone cases
    results = client.search_and_format(
        query="iPhone case",
        limit=5,
        sort="PricePlusShippingLowest"
    )

    # Print formatted results
    print(f"Found {results.get('total_results', 0)} total results")
    print(f"Showing {len(results.get('products', []))} products:")
    print()

    for i, product in enumerate(results.get('products', []), 1):
        print(f"Product {i}:")
        print(f"  Title: {product['title']}")
        price_value = product['price'].get('value', 'N/A')
        price_currency = product['price'].get('currency', '')
        print(f"  Price: {price_value} {price_currency}")
        print(f"  URL: {product['url']}")
        if product.get('condition'):
            print(f"  Condition: {product['condition']}")
        if product.get('image_url'):
            print(f"  Image: {product['image_url']}")
        print()

    # Save results to JSON file
    with open('iphone_cases_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Results saved to 'iphone_cases_results.json'")
    return results


def search_with_filters():
    """Example: Search with additional filters."""
    client = EbayAPIClient()

    print("\nSearching for 'laptop' with filters...")
    print("=" * 50)

    # Search with filters
    results = client.search_and_format(
        query="laptop",
        limit=3,
        sort="PricePlusShippingLowest",
        filters={
            'price_max': '500',
            'condition': 'NEW'
        }
    )

    print(f"Found {results.get('total_results', 0)} filtered results")
    print()

    for i, product in enumerate(results.get('products', []), 1):
        print(f"Laptop {i}:")
        print(f"  Title: {product['title']}")
        price_value = product['price'].get('value', 'N/A')
        price_currency = product['price'].get('currency', '')
        print(f"  Price: {price_value} {price_currency}")
        print(f"  Condition: {product.get('condition', 'N/A')}")
        print()

    return results


def get_product_details():
    """Example: Get detailed information about a specific product."""
    client = EbayAPIClient()

    # First, search for a product to get an item ID
    search_results = client.search_products("iPhone 15", limit=1)

    if 'error' in search_results:
        print(f"Error searching for products: {search_results['error']}")
        return None

    items = search_results.get('itemSummaries', [])
    if not items:
        print("No products found")
        return None

    item_id = items[0].get('itemId')
    if not item_id:
        print("No item ID found")
        return None

    print(f"\nGetting detailed information for item: {item_id}")
    print("=" * 50)

    # Get detailed product information
    details = client.get_product_details(item_id)

    if 'error' in details:
        print(f"Error getting product details: {details['error']}")
        return None

    # Print key details
    print(f"Title: {details.get('title', 'N/A')}")
    price_value = details.get('price', {}).get('value', 'N/A')
    price_currency = details.get('price', {}).get('currency', '')
    print(f"Price: {price_value} {price_currency}")
    description = details.get('description', 'N/A')[:200]
    print(f"Description: {description}...")
    print(f"Seller: {details.get('seller', {}).get('username', 'N/A')}")
    print(f"Location: {details.get('itemLocation', {}).get('city', 'N/A')}")

    # Save details to JSON file
    with open('product_details.json', 'w', encoding='utf-8') as f:
        json.dump(details, f, indent=2, ensure_ascii=False)

    print("\nDetailed product information saved to 'product_details.json'")
    return details


def main():
    """Run all examples."""
    print("eBay API Product Data Collection Examples")
    print("=" * 50)

    try:
        # Example 1: Basic search
        search_iphone_cases()

        # Example 2: Search with filters
        search_with_filters()

        # Example 3: Get product details
        get_product_details()

    except (ImportError, AttributeError, KeyError, ValueError, ConnectionError) as e:
        print(f"Error running examples: {e}")
        print("\nMake sure you have:")
        print("1. Created a .env file with your eBay API credentials")
        print("2. Installed required dependencies: pip install -r requirements.txt")
        print("3. Obtained a valid OAuth token from eBay")


if __name__ == "__main__":
    main()
