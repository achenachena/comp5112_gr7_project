#!/usr/bin/env python3
"""
E-commerce Dataset Generator

This script automatically generates a comprehensive e-commerce dataset
for your search algorithm research by loading data from JSON files.
"""

import json
import os
import random
from typing import List, Dict, Any


def load_mock_data():
    """Load mock data from JSON files."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mock_data_dir = os.path.join(script_dir, 'data', 'mock_datasets')

    # Load products data
    with open(os.path.join(mock_data_dir, 'products.json'), 'r', encoding='utf-8') as f:
        products_data = json.load(f)

    # Load sellers data
    with open(os.path.join(mock_data_dir, 'sellers.json'), 'r', encoding='utf-8') as f:
        sellers = json.load(f)

    # Load locations data
    with open(os.path.join(mock_data_dir, 'locations.json'), 'r', encoding='utf-8') as f:
        locations = json.load(f)

    # Load conditions data
    with open(os.path.join(mock_data_dir, 'conditions.json'), 'r', encoding='utf-8') as f:
        conditions = json.load(f)
    
    # Load configuration
    with open(os.path.join(mock_data_dir, 'config.json'), 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return products_data, sellers, locations, conditions, config


def generate_comprehensive_dataset() -> List[Dict[str, Any]]:
    """Generate a comprehensive e-commerce dataset."""
    print("📦 Generating comprehensive e-commerce dataset...")

    # Load mock data from files
    products_data, sellers, locations, conditions, config = load_mock_data()

    # Convert to the format expected by our search algorithms
    products = []

    for item in products_data:
        product = {
            'id': item['id'],
            'title': item['title'],
            'description': config['description_template'].format(
                category=item['category'].lower(),
                brand=item['brand']
            ),
            'price': {'value': item['price'], 'currency': config['currency']},
            'category': item['category'],
            'condition': random.choice(conditions),
            'seller': {'username': random.choice(sellers)},
            'location': random.choice(locations),
            'brand': item['brand'],
            'rating': round(random.uniform(
                config['rating_range']['min'],
                config['rating_range']['max']
            ), 1),
            'review_count': random.randint(
                config['review_count_range']['min'],
                config['review_count_range']['max']
            ),
            'stock': random.randint(
                config['stock_range']['min'],
                config['stock_range']['max']
            ),
            'tags': [
                item['category'].lower().replace(' ', '-'),
                item['brand'].lower(),
                'electronics',
                'accessories'
            ]
        }
        products.append(product)

    print(f"✅ Generated {len(products)} products")
    return products


def save_dataset(products: List[Dict[str, Any]], filename='data/generated_products.json'):
    """Save the dataset to JSON file."""
    os.makedirs('data', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Dataset saved to {filename}")


def create_dataset_summary(products: List[Dict[str, Any]]):
    """Create a summary of the generated dataset."""
    categories = {}
    brands = {}
    total_value = 0
    
    for product in products:
        # Count categories
        category = product['category']
        categories[category] = categories.get(category, 0) + 1
        
        # Count brands
        brand = product['brand']
        brands[brand] = brands.get(brand, 0) + 1
        
        # Sum total value
        total_value += float(product['price']['value'])
    
    summary = {
        'total_products': len(products),
        'total_categories': len(categories),
        'total_brands': len(brands),
        'total_value': round(total_value, 2),
        'average_price': round(total_value / len(products), 2),
        'categories': categories,
        'brands': brands
    }
    
    # Save summary
    with open('data/generated_products_summary.txt', 'w', encoding='utf-8') as f:
        f.write("📊 E-commerce Dataset Summary\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Total Products: {summary['total_products']}\n")
        f.write(f"Total Categories: {summary['total_categories']}\n")
        f.write(f"Total Brands: {summary['total_brands']}\n")
        f.write(f"Total Value: ${summary['total_value']}\n")
        f.write(f"Average Price: ${summary['average_price']}\n\n")
        
        f.write("Categories:\n")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {category}: {count} products\n")
        
        f.write("\nBrands:\n")
        for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {brand}: {count} products\n")
    
    print(f"📈 Dataset summary saved to data/generated_products_summary.txt")
    return summary


def main():
    """Main function to generate the dataset."""
    print("🚀 E-commerce Dataset Generator")
    print("=" * 40)
    
    # Generate dataset
    products = generate_comprehensive_dataset()
    
    # Save dataset
    save_dataset(products)
    
    # Create summary
    summary = create_dataset_summary(products)
    
    print("\n🎯 Dataset Generation Complete!")
    print(f"✅ Generated {summary['total_products']} products")
    print(f"✅ {summary['total_categories']} categories")
    print(f"✅ {summary['total_brands']} brands")
    print(f"✅ Total value: ${summary['total_value']}")
    print(f"✅ Average price: ${summary['average_price']}")
    
    print("\n📁 Files created:")
    print("  • data/generated_products.json - Full dataset")
    print("  • data/generated_products_summary.txt - Dataset summary")
    
    print("\n🔍 Next steps:")
    print("1. Test with search algorithms:")
    print("   python prototype/cli.py --mode compare")
    print("2. Run GUI interface:")
    print("   python web_gui.py")


if __name__ == "__main__":
    main()
