"""
Command Line Interface for Search Algorithm Comparison

This module provides an interactive CLI for testing and comparing search algorithms
on e-commerce product data.
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.keyword_matching import KeywordSearch
from algorithms.tfidf_search import TFIDFSearch
from evaluation.comparison import SearchComparison
from evaluation.metrics import RelevanceJudgment
from utils.preprocessing import ProductDataPreprocessor, DataLoader


class SearchCLI:
    """
    Command Line Interface for search algorithm comparison.
    """
    
    def __init__(self):
        self.products = []
        self.algorithms = {}
        self.relevance_judge = RelevanceJudgment()
        self.preprocessor = ProductDataPreprocessor()
    
    def load_sample_data(self):
        """Load sample product data for demonstration."""
        sample_products = [
            {
                'id': 1,
                'title': 'iPhone 15 Pro Max Case - Clear Transparent',
                'description': 'Premium clear case for iPhone 15 Pro Max with wireless charging support and drop protection',
                'category': 'Phone Cases',
                'price': {'value': '29.99', 'currency': 'USD'},
                'url': 'https://example.com/iphone-case',
                'condition': 'NEW',
                'seller': {'username': 'tech_store'},
                'location': 'New York'
            },
            {
                'id': 2,
                'title': 'Samsung Galaxy S24 Ultra Case - Black',
                'description': 'Protective case for Samsung Galaxy S24 Ultra with kickstand and camera protection',
                'category': 'Phone Cases',
                'price': {'value': '24.99', 'currency': 'USD'},
                'url': 'https://example.com/samsung-case',
                'condition': 'NEW',
                'seller': {'username': 'mobile_shop'},
                'location': 'Los Angeles'
            },
            {
                'id': 3,
                'title': 'iPhone 15 Screen Protector - Tempered Glass',
                'description': '9H hardness tempered glass screen protector for iPhone 15 with easy installation',
                'category': 'Screen Protectors',
                'price': {'value': '12.99', 'currency': 'USD'},
                'url': 'https://example.com/screen-protector',
                'condition': 'NEW',
                'seller': {'username': 'accessories_pro'},
                'location': 'Chicago'
            },
            {
                'id': 4,
                'title': 'Wireless Charger Pad - Fast Charging',
                'description': 'Universal wireless charging pad compatible with iPhone and Android phones',
                'category': 'Chargers',
                'price': {'value': '19.99', 'currency': 'USD'},
                'url': 'https://example.com/wireless-charger',
                'condition': 'NEW',
                'seller': {'username': 'tech_gadgets'},
                'location': 'Miami'
            },
            {
                'id': 5,
                'title': 'iPhone 14 Pro Case - Silicone',
                'description': 'Soft silicone case for iPhone 14 Pro with MagSafe compatibility',
                'category': 'Phone Cases',
                'price': {'value': '39.99', 'currency': 'USD'},
                'url': 'https://example.com/iphone14-case',
                'condition': 'NEW',
                'seller': {'username': 'apple_accessories'},
                'location': 'Seattle'
            },
            {
                'id': 6,
                'title': 'Samsung Galaxy S23 Case - Clear',
                'description': 'Transparent case for Samsung Galaxy S23 with anti-yellowing technology',
                'category': 'Phone Cases',
                'price': {'value': '18.99', 'currency': 'USD'},
                'url': 'https://example.com/s23-case',
                'condition': 'NEW',
                'seller': {'username': 'samsung_store'},
                'location': 'Austin'
            },
            {
                'id': 7,
                'title': 'iPad Air 5th Gen Case - Folio',
                'description': 'Premium folio case for iPad Air 5th generation with auto sleep/wake',
                'category': 'Tablet Cases',
                'price': {'value': '49.99', 'currency': 'USD'},
                'url': 'https://example.com/ipad-case',
                'condition': 'NEW',
                'seller': {'username': 'tablet_pro'},
                'location': 'Denver'
            },
            {
                'id': 8,
                'title': 'MacBook Pro 16-inch Case - Hard Shell',
                'description': 'Hard shell protective case for MacBook Pro 16-inch with precise cutouts',
                'category': 'Laptop Cases',
                'price': {'value': '79.99', 'currency': 'USD'},
                'url': 'https://example.com/macbook-case',
                'condition': 'NEW',
                'seller': {'username': 'mac_accessories'},
                'location': 'San Francisco'
            }
        ]
        
        self.products = sample_products
        print(f"Loaded {len(sample_products)} sample products")
    
    def initialize_algorithms(self):
        """Initialize search algorithms."""
        self.algorithms = {
            'keyword_matching': KeywordSearch(),
            'tfidf': TFIDFSearch()
        }
        print("Initialized search algorithms: keyword_matching, tfidf")
    
    def create_synthetic_judgments(self):
        """Create synthetic relevance judgments for evaluation."""
        test_queries = [
            "iPhone case",
            "Samsung phone case",
            "wireless charger",
            "screen protector iPhone",
            "iPad case",
            "MacBook case"
        ]
        
        self.relevance_judge.create_synthetic_judgments(test_queries, self.products)
        print(f"Created synthetic relevance judgments for {len(test_queries)} test queries")
    
    def interactive_search(self):
        """Interactive search mode."""
        print("\n" + "="*60)
        print("INTERACTIVE SEARCH MODE")
        print("="*60)
        print("Enter search queries to compare algorithms. Type 'quit' to exit.")
        
        while True:
            query = input("\nEnter search query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            print(f"\nSearching for: '{query}'")
            print("-" * 50)
            
            # Search with both algorithms
            for algo_name, algorithm in self.algorithms.items():
                print(f"\n{algo_name.upper()} Results:")
                print("-" * 30)
                
                results = algorithm.search(query, self.products, limit=3)
                
                if results:
                    for i, product in enumerate(results, 1):
                        print(f"{i}. {product['title']}")
                        print(f"   Price: ${product['price']['value']} {product['price']['currency']}")
                        print(f"   Score: {product['relevance_score']:.4f}")
                        if product.get('matched_terms'):
                            print(f"   Matched: {', '.join(product['matched_terms'])}")
                        print()
                else:
                    print("No results found.")
    
    def run_comparison(self):
        """Run comprehensive algorithm comparison."""
        print("\n" + "="*60)
        print("ALGORITHM COMPARISON")
        print("="*60)
        
        # Test queries
        test_queries = [
            "iPhone case",
            "Samsung phone case", 
            "wireless charger",
            "screen protector iPhone",
            "iPad case",
            "MacBook case"
        ]
        
        print(f"Running comparison on {len(test_queries)} test queries...")
        
        # Initialize comparison framework
        comparison = SearchComparison(self.algorithms, self.relevance_judge)
        
        # Run comparison
        results = comparison.compare_multiple_queries(test_queries, self.products)
        
        # Print detailed report
        comparison.print_comparison_report()
        
        # Export results
        output_file = 'results/comparison_results.json'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        comparison.export_results(output_file)
        print(f"\nResults exported to: {output_file}")
    
    def load_custom_data(self, filename: str):
        """Load custom product data from file."""
        try:
            if filename.endswith('.json'):
                products = DataLoader.load_from_json(filename)
            elif filename.endswith('.csv'):
                products = DataLoader.load_from_csv(filename)
            else:
                print("Unsupported file format. Use .json or .csv files.")
                return False
            
            # Preprocess the data
            cleaned_products = self.preprocessor.clean_product_data(products)
            
            if cleaned_products:
                self.products = cleaned_products
                print(f"Loaded and cleaned {len(cleaned_products)} products from {filename}")
                
                # Print data statistics
                self.preprocessor.print_statistics()
                return True
            else:
                print("No valid products found in the file.")
                return False
                
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def run_demo(self):
        """Run a complete demonstration."""
        print("Search Algorithm Comparison - Demo Mode")
        print("="*60)
        
        # Load sample data
        self.load_sample_data()
        
        # Initialize algorithms
        self.initialize_algorithms()
        
        # Create relevance judgments
        self.create_synthetic_judgments()
        
        # Run comparison
        self.run_comparison()
        
        # Interactive search
        self.interactive_search()
    
    def run(self):
        """Main CLI runner."""
        parser = argparse.ArgumentParser(description='Search Algorithm Comparison CLI')
        parser.add_argument('--mode', choices=['demo', 'interactive', 'compare'], 
                          default='demo', help='Run mode')
        parser.add_argument('--data', type=str, help='Path to custom data file')
        parser.add_argument('--output', type=str, default='results/', 
                          help='Output directory for results')
        
        args = parser.parse_args()
        
        # Create output directory
        os.makedirs(args.output, exist_ok=True)
        
        if args.data:
            if self.load_custom_data(args.data):
                self.initialize_algorithms()
                self.create_synthetic_judgments()
            else:
                return
        
        if args.mode == 'demo':
            self.run_demo()
        elif args.mode == 'interactive':
            self.load_sample_data()
            self.initialize_algorithms()
            self.interactive_search()
        elif args.mode == 'compare':
            self.load_sample_data()
            self.initialize_algorithms()
            self.create_synthetic_judgments()
            self.run_comparison()


def main():
    """Main entry point."""
    cli = SearchCLI()
    cli.run()


if __name__ == "__main__":
    main()
