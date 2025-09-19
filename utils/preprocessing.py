"""
Data Preprocessing Utilities for E-commerce Search

This module provides utilities for cleaning, normalizing, and preparing
product data for search algorithm evaluation.
"""

import re
import json
import os
from typing import List, Dict, Any, Optional
import pandas as pd


class ProductDataPreprocessor:
    """
    Class for preprocessing product data from various sources.
    """
    
    def __init__(self):
        self.cleaned_data = []
        self.statistics = {}
    
    def clean_product_data(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and normalize product data.
        
        Args:
            products: List of raw product dictionaries
            
        Returns:
            List of cleaned product dictionaries
        """
        cleaned_products = []
        
        for product in products:
            cleaned_product = self._clean_single_product(product)
            if cleaned_product:  # Only include if cleaning was successful
                cleaned_products.append(cleaned_product)
        
        self.cleaned_data = cleaned_products
        self._calculate_statistics()
        
        return cleaned_products
    
    def _clean_single_product(self, product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Clean a single product dictionary.
        
        Args:
            product: Raw product dictionary
            
        Returns:
            Cleaned product dictionary or None if invalid
        """
        # Ensure required fields exist
        if not product or 'title' not in product:
            return None
        
        cleaned = {}
        
        # Clean and validate ID
        cleaned['id'] = self._clean_id(product.get('id', product.get('item_id')))
        if not cleaned['id']:
            return None
        
        # Clean title
        cleaned['title'] = self._clean_text(product['title'])
        if not cleaned['title']:
            return None
        
        # Clean description (optional)
        cleaned['description'] = self._clean_text(product.get('description', ''))
        
        # Clean category
        cleaned['category'] = self._clean_text(product.get('category', ''))
        
        # Clean price
        cleaned['price'] = self._clean_price(product.get('price', {}))
        
        # Clean URL
        cleaned['url'] = product.get('url', product.get('item_href', ''))
        
        # Clean image URL
        cleaned['image_url'] = product.get('image_url', '')
        
        # Clean condition
        cleaned['condition'] = self._clean_text(product.get('condition', ''))
        
        # Clean seller information
        cleaned['seller'] = self._clean_seller(product.get('seller', {}))
        
        # Clean location
        cleaned['location'] = self._clean_text(product.get('location', ''))
        
        # Add metadata
        cleaned['_metadata'] = {
            'original_data': product,
            'cleaned_at': pd.Timestamp.now().isoformat()
        }
        
        return cleaned
    
    def _clean_id(self, item_id: Any) -> Optional[str]:
        """Clean and validate product ID."""
        if item_id is None:
            return None
        
        # Convert to string and clean
        id_str = str(item_id).strip()
        
        # Remove common prefixes
        id_str = re.sub(r'^(v\d+\|)', '', id_str)
        
        # Validate ID format
        if not id_str or len(id_str) < 3:
            return None
        
        return id_str
    
    def _clean_text(self, text: str) -> str:
        """Clean text fields."""
        if not text:
            return ""
        
        # Convert to string
        text = str(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\&]', '', text)
        
        # Limit length
        if len(text) > 500:
            text = text[:500] + "..."
        
        return text
    
    def _clean_price(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean price information."""
        cleaned_price = {
            'value': '0.00',
            'currency': 'USD'
        }
        
        if isinstance(price_data, dict):
            # Extract value
            value = price_data.get('value', price_data.get('amount', '0'))
            if value:
                # Remove currency symbols and clean
                value_str = re.sub(r'[^\d\.]', '', str(value))
                try:
                    float(value_str)  # Validate it's a number
                    cleaned_price['value'] = value_str
                except ValueError:
                    pass
            
            # Extract currency
            currency = price_data.get('currency', 'USD')
            if currency and len(str(currency)) <= 3:
                cleaned_price['currency'] = str(currency).upper()
        
        return cleaned_price
    
    def _clean_seller(self, seller_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean seller information."""
        cleaned_seller = {}
        
        if isinstance(seller_data, dict):
            # Clean username
            username = seller_data.get('username', '')
            if username:
                cleaned_seller['username'] = self._clean_text(username)
            
            # Clean seller ID
            seller_id = seller_data.get('seller_id', '')
            if seller_id:
                cleaned_seller['seller_id'] = str(seller_id).strip()
        
        return cleaned_seller
    
    def _calculate_statistics(self):
        """Calculate statistics about the cleaned data."""
        if not self.cleaned_data:
            return
        
        stats = {
            'total_products': len(self.cleaned_data),
            'categories': {},
            'price_ranges': {'0-10': 0, '10-50': 0, '50-100': 0, '100+': 0},
            'conditions': {},
            'average_title_length': 0,
            'average_description_length': 0
        }
        
        title_lengths = []
        description_lengths = []
        
        for product in self.cleaned_data:
            # Category distribution
            category = product.get('category', 'Unknown')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Price ranges
            try:
                price = float(product.get('price', {}).get('value', 0))
                if price < 10:
                    stats['price_ranges']['0-10'] += 1
                elif price < 50:
                    stats['price_ranges']['10-50'] += 1
                elif price < 100:
                    stats['price_ranges']['50-100'] += 1
                else:
                    stats['price_ranges']['100+'] += 1
            except ValueError:
                pass
            
            # Condition distribution
            condition = product.get('condition', 'Unknown')
            stats['conditions'][condition] = stats['conditions'].get(condition, 0) + 1
            
            # Text length statistics
            title_lengths.append(len(product.get('title', '')))
            description_lengths.append(len(product.get('description', '')))
        
        # Calculate averages
        if title_lengths:
            stats['average_title_length'] = sum(title_lengths) / len(title_lengths)
        if description_lengths:
            stats['average_description_length'] = sum(description_lengths) / len(description_lengths)
        
        self.statistics = stats
    
    def export_cleaned_data(self, filename: str, format: str = 'json'):
        """
        Export cleaned data to file.
        
        Args:
            filename: Output filename
            format: Export format ('json' or 'csv')
        """
        if not self.cleaned_data:
            raise ValueError("No cleaned data to export. Run clean_product_data first.")
        
        if format.lower() == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.cleaned_data, f, indent=2, ensure_ascii=False)
        
        elif format.lower() == 'csv':
            # Convert to DataFrame for CSV export
            df_data = []
            for product in self.cleaned_data:
                row = {
                    'id': product.get('id'),
                    'title': product.get('title'),
                    'description': product.get('description'),
                    'category': product.get('category'),
                    'price_value': product.get('price', {}).get('value'),
                    'price_currency': product.get('price', {}).get('currency'),
                    'condition': product.get('condition'),
                    'url': product.get('url'),
                    'seller_username': product.get('seller', {}).get('username'),
                    'location': product.get('location')
                }
                df_data.append(row)
            
            df = pd.DataFrame(df_data)
            df.to_csv(filename, index=False, encoding='utf-8')
        
        else:
            raise ValueError("Unsupported format. Use 'json' or 'csv'.")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the cleaned data."""
        return self.statistics
    
    def print_statistics(self):
        """Print formatted statistics."""
        if not self.statistics:
            print("No statistics available. Run clean_product_data first.")
            return
        
        stats = self.statistics
        
        print("Data Preprocessing Statistics")
        print("=" * 40)
        print(f"Total Products: {stats['total_products']}")
        print(f"Average Title Length: {stats['average_title_length']:.1f} characters")
        print(f"Average Description Length: {stats['average_description_length']:.1f} characters")
        print()
        
        print("Category Distribution:")
        print("-" * 25)
        for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_products']) * 100
            print(f"{category}: {count} ({percentage:.1f}%)")
        
        print()
        
        print("Price Range Distribution:")
        print("-" * 30)
        for price_range, count in stats['price_ranges'].items():
            percentage = (count / stats['total_products']) * 100
            print(f"${price_range}: {count} ({percentage:.1f}%)")
        
        print()
        
        print("Condition Distribution:")
        print("-" * 25)
        for condition, count in sorted(stats['conditions'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_products']) * 100
            print(f"{condition}: {count} ({percentage:.1f}%)")


class DataLoader:
    """
    Utility class for loading product data from various sources.
    """
    
    @staticmethod
    def load_from_json(filename: str) -> List[Dict[str, Any]]:
        """
        Load product data from JSON file.
        
        Args:
            filename: Path to JSON file
            
        Returns:
            List of product dictionaries
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if 'products' in data:
                return data['products']
            elif 'itemSummaries' in data:  # eBay API format
                return data['itemSummaries']
            else:
                return [data]
        else:
            raise ValueError("Invalid JSON structure")
    
    @staticmethod
    def load_from_csv(filename: str) -> List[Dict[str, Any]]:
        """
        Load product data from CSV file.
        
        Args:
            filename: Path to CSV file
            
        Returns:
            List of product dictionaries
        """
        df = pd.read_csv(filename)
        return df.to_dict('records')
    
    @staticmethod
    def load_from_directory(directory: str, pattern: str = "*.json") -> List[Dict[str, Any]]:
        """
        Load product data from multiple files in a directory.
        
        Args:
            directory: Directory path
            pattern: File pattern to match
            
        Returns:
            Combined list of product dictionaries
        """
        import glob
        
        all_products = []
        files = glob.glob(os.path.join(directory, pattern))
        
        for file in files:
            try:
                if file.endswith('.json'):
                    products = DataLoader.load_from_json(file)
                elif file.endswith('.csv'):
                    products = DataLoader.load_from_csv(file)
                else:
                    continue
                
                all_products.extend(products)
            except Exception as e:
                print(f"Error loading {file}: {e}")
                continue
        
        return all_products


def demo_preprocessing():
    """Demonstrate the data preprocessing utilities."""
    # Sample raw data (similar to eBay API response)
    raw_products = [
        {
            'itemId': 'v1|1234567890|0',
            'title': 'iPhone 15 Pro Max Case - Clear Transparent <b>Premium</b>',
            'description': 'Premium clear case for iPhone 15 Pro Max with wireless charging support!!!',
            'category': 'Phone Cases & Accessories',
            'price': {'value': '29.99', 'currency': 'USD'},
            'itemHref': 'https://www.ebay.com/itm/1234567890',
            'condition': 'NEW',
            'seller': {'username': 'tech_store_2024'},
            'location': 'New York, NY'
        },
        {
            'itemId': 'v1|0987654321|0',
            'title': 'Samsung Galaxy S24 Ultra Case - Black',
            'description': 'Protective case for Samsung Galaxy S24 Ultra with kickstand feature.',
            'category': 'Phone Cases',
            'price': {'value': '24.99', 'currency': 'USD'},
            'condition': 'NEW',
            'seller': {'username': 'mobile_accessories'},
            'location': 'Los Angeles, CA'
        }
    ]
    
    print("Data Preprocessing Demo")
    print("=" * 40)
    
    # Initialize preprocessor
    preprocessor = ProductDataPreprocessor()
    
    # Clean the data
    print("Raw data sample:")
    print(f"- Product 1 title: {raw_products[0]['title']}")
    print(f"- Product 1 description: {raw_products[0]['description']}")
    print()
    
    cleaned_products = preprocessor.clean_product_data(raw_products)
    
    print("Cleaned data sample:")
    print(f"- Product 1 title: {cleaned_products[0]['title']}")
    print(f"- Product 1 description: {cleaned_products[0]['description']}")
    print()
    
    # Print statistics
    preprocessor.print_statistics()
    
    # Export cleaned data
    preprocessor.export_cleaned_data('data/cleaned_products.json')
    print(f"\nCleaned data exported to 'data/cleaned_products.json'")


if __name__ == "__main__":
    demo_preprocessing()
