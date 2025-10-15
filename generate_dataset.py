#!/usr/bin/env python3
"""
Generate E-commerce Dataset - No API Keys Required!

This script automatically generates a comprehensive e-commerce dataset
for your search algorithm research.
"""

import json
import os
import random
from typing import List, Dict, Any


def generate_comprehensive_dataset() -> List[Dict[str, Any]]:
    """Generate a comprehensive e-commerce dataset."""
    print("📦 Generating comprehensive e-commerce dataset...")
    
    # Comprehensive product data
    products_data = [
        # Phone Accessories - iPhone
        {"id": "P001", "title": "iPhone 15 Pro Max Case - Clear Transparent", "category": "Phone Cases", "price": "29.99", "brand": "iPhone"},
        {"id": "P002", "title": "iPhone 15 Pro Max Case - Black Silicone", "category": "Phone Cases", "price": "39.99", "brand": "iPhone"},
        {"id": "P003", "title": "iPhone 15 Screen Protector - Tempered Glass", "category": "Screen Protectors", "price": "12.99", "brand": "iPhone"},
        {"id": "P004", "title": "iPhone 15 Pro Max MagSafe Case", "category": "Phone Cases", "price": "49.99", "brand": "iPhone"},
        {"id": "P005", "title": "iPhone 15 Pro Max Leather Case", "category": "Phone Cases", "price": "59.99", "brand": "iPhone"},
        
        # Phone Accessories - Samsung
        {"id": "P006", "title": "Samsung Galaxy S24 Ultra Case - Clear", "category": "Phone Cases", "price": "24.99", "brand": "Samsung"},
        {"id": "P007", "title": "Samsung Galaxy S24 Ultra Case - Black", "category": "Phone Cases", "price": "22.99", "brand": "Samsung"},
        {"id": "P008", "title": "Samsung Galaxy S24 Screen Protector", "category": "Screen Protectors", "price": "14.99", "brand": "Samsung"},
        {"id": "P009", "title": "Samsung Galaxy S24 Ultra S Pen Case", "category": "Phone Cases", "price": "34.99", "brand": "Samsung"},
        {"id": "P010", "title": "Samsung Galaxy S24 Ultra Camera Lens Protector", "category": "Camera Accessories", "price": "15.99", "brand": "Samsung"},
        
        # Chargers
        {"id": "P011", "title": "Wireless Charging Pad - Fast Charging", "category": "Chargers", "price": "19.99", "brand": "Universal"},
        {"id": "P012", "title": "USB-C Cable 6ft - High Speed", "category": "Chargers", "price": "14.99", "brand": "Universal"},
        {"id": "P013", "title": "Wireless Charging Stand - Adjustable", "category": "Chargers", "price": "45.99", "brand": "Universal"},
        {"id": "P014", "title": "Car Charger - Dual Port QC 3.0", "category": "Car Accessories", "price": "18.99", "brand": "Universal"},
        {"id": "P015", "title": "Portable Power Bank - 20000mAh", "category": "Chargers", "price": "39.99", "brand": "Universal"},
        
        # Audio
        {"id": "P016", "title": "Bluetooth Headphones - Noise Canceling", "category": "Audio", "price": "79.99", "brand": "AudioPro"},
        {"id": "P017", "title": "Wireless Earbuds - True Wireless", "category": "Audio", "price": "69.99", "brand": "AudioPro"},
        {"id": "P018", "title": "Gaming Headset - RGB Wireless", "category": "Gaming", "price": "89.99", "brand": "GameTech"},
        {"id": "P019", "title": "Bluetooth Speaker - Portable", "category": "Audio", "price": "49.99", "brand": "AudioPro"},
        {"id": "P020", "title": "AirPods Pro Case - Protective", "category": "Audio Accessories", "price": "19.99", "brand": "Apple"},
        
        # Gaming
        {"id": "P021", "title": "Gaming Mouse - RGB Wireless", "category": "Gaming", "price": "59.99", "brand": "GameTech"},
        {"id": "P022", "title": "Mechanical Keyboard - RGB Backlit", "category": "Gaming", "price": "89.99", "brand": "GameTech"},
        {"id": "P023", "title": "Gaming Controller - Wireless", "category": "Gaming", "price": "69.99", "brand": "GameTech"},
        {"id": "P024", "title": "Gaming Mouse Pad - RGB", "category": "Gaming", "price": "29.99", "brand": "GameTech"},
        {"id": "P025", "title": "Gaming Headset Stand - RGB", "category": "Gaming", "price": "39.99", "brand": "GameTech"},
        
        # Laptop Accessories
        {"id": "P026", "title": "Laptop Stand - Adjustable Aluminum", "category": "Laptop Accessories", "price": "39.99", "brand": "LaptopPro"},
        {"id": "P027", "title": "MacBook Pro 16-inch Case", "category": "Laptop Cases", "price": "49.99", "brand": "Apple"},
        {"id": "P028", "title": "USB Hub 7-Port - USB 3.0", "category": "Computer Accessories", "price": "34.99", "brand": "TechHub"},
        {"id": "P029", "title": "Laptop Cooling Pad - RGB", "category": "Laptop Accessories", "price": "29.99", "brand": "CoolTech"},
        {"id": "P030", "title": "Laptop Sleeve - Neoprene", "category": "Laptop Cases", "price": "24.99", "brand": "LaptopPro"},
        
        # Smart Home
        {"id": "P031", "title": "Smart Speaker - Voice Control", "category": "Smart Home", "price": "99.99", "brand": "SmartHome"},
        {"id": "P032", "title": "Smart Light Bulb - WiFi RGB", "category": "Smart Home", "price": "19.99", "brand": "SmartHome"},
        {"id": "P033", "title": "Security Camera - Wireless", "category": "Smart Home", "price": "79.99", "brand": "SecureCam"},
        {"id": "P034", "title": "Smart Doorbell - WiFi", "category": "Smart Home", "price": "149.99", "brand": "SecureCam"},
        {"id": "P035", "title": "Smart Thermostat - WiFi", "category": "Smart Home", "price": "199.99", "brand": "ClimateControl"},
        
        # Fitness & Wearables
        {"id": "P036", "title": "Fitness Tracker - Waterproof", "category": "Fitness", "price": "49.99", "brand": "FitTech"},
        {"id": "P037", "title": "Smart Watch - Fitness Tracking", "category": "Wearables", "price": "129.99", "brand": "SmartWatch"},
        {"id": "P038", "title": "Yoga Mat - Premium Non-Slip", "category": "Fitness", "price": "34.99", "brand": "FitTech"},
        {"id": "P039", "title": "Resistance Bands Set - 12 Pieces", "category": "Fitness", "price": "24.99", "brand": "FitTech"},
        {"id": "P040", "title": "Apple Watch Band - Sport", "category": "Wearables", "price": "39.99", "brand": "Apple"},
        
        # Car Accessories
        {"id": "P041", "title": "Car Phone Mount - Magnetic", "category": "Car Accessories", "price": "24.99", "brand": "CarTech"},
        {"id": "P042", "title": "Car Charger - Wireless", "category": "Car Accessories", "price": "34.99", "brand": "CarTech"},
        {"id": "P043", "title": "Car Phone Holder - Dashboard", "category": "Car Accessories", "price": "19.99", "brand": "CarTech"},
        {"id": "P044", "title": "Car USB Adapter - Dual Port", "category": "Car Accessories", "price": "14.99", "brand": "CarTech"},
        {"id": "P045", "title": "Car Phone Stand - Vent Mount", "category": "Car Accessories", "price": "16.99", "brand": "CarTech"},
        
        # Computer Accessories
        {"id": "P046", "title": "Webcam HD 1080p - USB", "category": "Computer Accessories", "price": "49.99", "brand": "WebCamPro"},
        {"id": "P047", "title": "Monitor Stand - Adjustable", "category": "Computer Accessories", "price": "29.99", "brand": "MonitorPro"},
        {"id": "P048", "title": "Desk Lamp - LED USB", "category": "Computer Accessories", "price": "39.99", "brand": "LightTech"},
        {"id": "P049", "title": "External Hard Drive - 1TB", "category": "Computer Accessories", "price": "59.99", "brand": "StoragePro"},
        {"id": "P050", "title": "WiFi Router - AC1200", "category": "Computer Accessories", "price": "79.99", "brand": "NetworkPro"},
        
        # Tablets
        {"id": "P051", "title": "iPad Air 5th Gen Case - Folio", "category": "Tablet Cases", "price": "49.99", "brand": "Apple"},
        {"id": "P052", "title": "iPad Pro 12.9 Case - Keyboard", "category": "Tablet Cases", "price": "149.99", "brand": "Apple"},
        {"id": "P053", "title": "Samsung Galaxy Tab Case", "category": "Tablet Cases", "price": "29.99", "brand": "Samsung"},
        {"id": "P054", "title": "Tablet Stand - Adjustable", "category": "Tablet Accessories", "price": "24.99", "brand": "TabletPro"},
        {"id": "P055", "title": "iPad Screen Protector - Glass", "category": "Screen Protectors", "price": "19.99", "brand": "Apple"},
        
        # Camera Accessories
        {"id": "P056", "title": "Phone Camera Lens Kit", "category": "Camera Accessories", "price": "39.99", "brand": "CameraPro"},
        {"id": "P057", "title": "Phone Tripod - Adjustable", "category": "Camera Accessories", "price": "29.99", "brand": "CameraPro"},
        {"id": "P058", "title": "Phone Gimbal - Stabilizer", "category": "Camera Accessories", "price": "89.99", "brand": "CameraPro"},
        {"id": "P059", "title": "Phone Ring Light - LED", "category": "Camera Accessories", "price": "24.99", "brand": "LightTech"},
        {"id": "P060", "title": "Phone Selfie Stick - Bluetooth", "category": "Camera Accessories", "price": "19.99", "brand": "SelfiePro"}
    ]
    
    # Convert to the format expected by our search algorithms
    products = []
    sellers = ["TechStore", "ElectronicsPro", "MobileAccessories", "GadgetHub", "TechWorld", "DigitalStore", "TechMart", "ElectroShop"]
    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    conditions = ["New", "Used - Like New", "Refurbished"]
    
    for item in products_data:
        product = {
            'id': item['id'],
            'title': item['title'],
            'description': f"High-quality {item['category'].lower()} with excellent features and durability. Perfect for {item['brand']} devices and everyday use.",
            'price': {'value': item['price'], 'currency': 'USD'},
            'category': item['category'],
            'condition': random.choice(conditions),
            'seller': {'username': random.choice(sellers)},
            'location': random.choice(locations),
            'url': f"https://example-store.com/product/{item['id']}",
            'brand': item['brand']
        }
        products.append(product)
    
    print(f"✅ Generated {len(products)} comprehensive e-commerce products")
    return products


def create_search_queries():
    """Create diverse search queries for testing."""
    return [
        # Phone related
        "iPhone case",
        "Samsung phone case", 
        "wireless charger",
        "screen protector",
        "phone stand",
        "iPhone 15 case",
        "Galaxy S24 case",
        "phone charger",
        "magnetic case",
        
        # Electronics
        "Bluetooth headphones",
        "laptop stand",
        "gaming mouse",
        "mechanical keyboard",
        "USB cable",
        "wireless earbuds",
        "gaming headset",
        "laptop case",
        
        # Smart home
        "smart speaker",
        "smart light",
        "security camera",
        "smart home",
        "smart thermostat",
        
        # Fitness
        "fitness tracker",
        "yoga mat",
        "resistance bands",
        "workout equipment",
        "smart watch",
        
        # General
        "power bank",
        "car mount",
        "webcam",
        "tablet case",
        "camera lens",
        
        # Brand specific
        "Apple case",
        "Samsung accessory",
        "iPhone 15 Pro Max",
        "Galaxy S24 Ultra",
        
        # Feature specific
        "wireless charging",
        "magnetic mount",
        "RGB lighting",
        "waterproof case",
        "tempered glass"
    ]


def save_dataset(products, filename='data/generated_products.json'):
    """Save the dataset to JSON file."""
    os.makedirs('data', exist_ok=True)
    
    dataset = {
        'total_products': len(products),
        'source': 'generated_dataset',
        'description': 'Comprehensive e-commerce products for search algorithm research',
        'products': products,
        'search_queries': create_search_queries()
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved dataset to {filename}")
    
    # Create detailed summary
    categories = {}
    brands = {}
    conditions = {}
    
    for product in products:
        # Category breakdown
        cat = product['category']
        categories[cat] = categories.get(cat, 0) + 1
        
        # Brand breakdown
        brand = product.get('brand', 'Unknown')
        brands[brand] = brands.get(brand, 0) + 1
        
        # Condition breakdown
        cond = product['condition']
        conditions[cond] = conditions.get(cond, 0) + 1
    
    summary_file = filename.replace('.json', '_summary.txt')
    with open(summary_file, 'w') as f:
        f.write("Generated E-commerce Dataset Summary\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total Products: {len(products)}\n")
        f.write(f"Source: Generated Dataset\n")
        f.write(f"File: {filename}\n\n")
        
        f.write("Categories:\n")
        for cat, count in sorted(categories.items()):
            f.write(f"  - {cat}: {count} products\n")
        
        f.write(f"\nBrands:\n")
        for brand, count in sorted(brands.items()):
            f.write(f"  - {brand}: {count} products\n")
        
        f.write(f"\nConditions:\n")
        for cond, count in sorted(conditions.items()):
            f.write(f"  - {cond}: {count} products\n")
        
        f.write(f"\nSearch Queries: {len(create_search_queries())} predefined queries\n")
    
    print(f"📊 Detailed summary saved to {summary_file}")


def main():
    """Main function."""
    print("🚀 Generating E-commerce Dataset")
    print("="*50)
    
    # Generate comprehensive dataset
    products = generate_comprehensive_dataset()
    
    # Save dataset
    save_dataset(products)
    
    print("\n" + "="*50)
    print("✅ Dataset Generation Complete!")
    print("="*50)
    print(f"📦 Total products: {len(products)}")
    print(f"📁 File: data/generated_products.json")
    print(f"🔍 Search queries: {len(create_search_queries())}")
    print()
    print("🎯 Next steps:")
    print("1. Test your dataset:")
    print("   python prototype/cli.py --mode compare --data data/generated_products.json")
    print("2. Use GUI:")
    print("   python prototype/gui.py")
    print("3. Load your dataset in the GUI")
    print()
    print("📋 Sample products:")
    for i, product in enumerate(products[:5], 1):
        print(f"  {i}. {product['title']} - ${product['price']['value']}")


if __name__ == "__main__":
    main()
