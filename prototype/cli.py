"""
Command Line Interface for Search Algorithm Comparison

This module provides an interactive CLI for testing and comparing search algorithms
on e-commerce product data.
"""

import os
import sys
import json
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.keyword_matching import KeywordSearch  # pylint: disable=wrong-import-position
from algorithms.tfidf_search import TFIDFSearch  # pylint: disable=wrong-import-position
from evaluation.comparison import SearchComparison  # pylint: disable=wrong-import-position
from evaluation.metrics import RelevanceJudgment  # pylint: disable=wrong-import-position
from utils.preprocessing import ProductDataPreprocessor, DataLoader  # pylint: disable=wrong-import-position


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
                'description': ('Premium clear case for iPhone 15 Pro Max with wireless charging '
                                 'support '
                                 'and drop protection'),
                'category': 'Phone Cases & Accessories',
                'price': {'value': '29.99', 'currency': 'USD'},
                'url': 'https://example.com/iphone-case',
                'condition': 'NEW',
                'seller': {'username': 'tech_store'},
                'location': 'New York'
            },
            {
                'id': 2,
                'title': 'Samsung Galaxy S24 Ultra Case - Black',
                'description': ('Protective case for Samsung Galaxy S24 Ultra with kickstand '
                                 'and camera protection'),
                'category': 'Phone Cases & Accessories',
                'price': {'value': '24.99', 'currency': 'USD'},
                'url': 'https://example.com/samsung-case',
                'condition': 'NEW',
                'seller': {'username': 'mobile_shop'},
                'location': 'Los Angeles'
            },
            {
                'id': 3,
                'title': 'iPhone 15 Screen Protector - Tempered Glass',
                'description': ('9H hardness tempered glass screen protector for iPhone 15 '
                                 'with easy installation'),
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
                'description': ('Universal wireless charging pad compatible with iPhone '
                                 'and Android phones'),
                'category': 'Chargers',
                'price': {'value': '19.99', 'currency': 'USD'},
                'url': 'https://example.com/wireless-charger',
                'condition': 'NEW',
                'seller': {'username': 'tech_gadgets'},
                'location': 'Miami'
            },
            {
                'id': 5,
                'title': 'Premium Leather Wallet Case for iPhone 15 Pro Max with Card Slots',
                'description': ('Handcrafted genuine leather case with RFID blocking technology '
                                 'and multiple card slots'),
                'category': 'Phone Cases & Accessories',
                'price': {'value': '79.99', 'currency': 'USD'},
                'url': 'https://example.com/leather-wallet-case',
                'condition': 'NEW',
                'seller': {'username': 'premium_accessories'},
                'location': 'Boston'
            },
            {
                'id': 6,
                'title': 'Samsung Galaxy S24 Ultra Camera Lens Protector Kit',
                'description': ('Tempered glass lens protectors for all camera modules '
                                 'with precise cutouts'),
                'category': 'Camera Accessories',
                'price': {'value': '15.99', 'currency': 'USD'},
                'url': 'https://example.com/camera-protector',
                'condition': 'NEW',
                'seller': {'username': 'camera_pro'},
                'location': 'Phoenix'
            },
            {
                'id': 7,
                'title': 'Universal Wireless Charging Stand with LED Display',
                'description': ('Adjustable charging stand compatible with all smartphones '
                                 'and smartwatches'),
                'category': 'Chargers',
                'price': {'value': '45.99', 'currency': 'USD'},
                'url': 'https://example.com/charging-stand',
                'condition': 'NEW',
                'seller': {'username': 'charging_solutions'},
                'location': 'Dallas'
            },
            {
                'id': 8,
                'title': 'iPhone 15 Pro Max MagSafe Compatible Case',
                'description': ('Magnetic case with wireless charging support '
                                 'and strong magnets'),
                'category': 'Phone Cases & Accessories',
                'price': {'value': '39.99', 'currency': 'USD'},
                'url': 'https://example.com/magsafe-case',
                'condition': 'NEW',
                'seller': {'username': 'magnetic_accessories'},
                'location': 'Portland'
            },
            {
                'id': 9,
                'title': 'Samsung Galaxy S24 Ultra S Pen Replacement',
                'description': ('Original S Pen stylus for Galaxy S24 Ultra '
                                 'with pressure sensitivity'),
                'category': 'Stylus & Accessories',
                'price': {'value': '59.99', 'currency': 'USD'},
                'url': 'https://example.com/s-pen',
                'condition': 'NEW',
                'seller': {'username': 'samsung_official'},
                'location': 'Houston'
            },
            {
                'id': 10,
                'title': 'Multi-Device Wireless Charging Pad',
                'description': ('Charge iPhone, Samsung, and AirPods simultaneously '
                                 'with fast charging'),
                'category': 'Chargers',
                'price': {'value': '89.99', 'currency': 'USD'},
                'url': 'https://example.com/multi-charger',
                'condition': 'NEW',
                'seller': {'username': 'multi_device_tech'},
                'location': 'Atlanta'
            },
            {
                'id': 11,
                'title': 'iPad Air 5th Gen Case - Folio',
                'description': ('Premium folio case for iPad Air 5th generation '
                                 'with auto sleep/wake'),
                'category': 'Tablet Cases',
                'price': {'value': '49.99', 'currency': 'USD'},
                'url': 'https://example.com/ipad-case',
                'condition': 'NEW',
                'seller': {'username': 'tablet_pro'},
                'location': 'Denver'
            },
            {
                'id': 12,
                'title': 'MacBook Pro 16-inch Case - Hard Shell',
                'description': ('Hard shell protective case for MacBook Pro 16-inch '
                                 'with precise cutouts'),
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
        """Initialize search algorithms with different parameters for distinct results."""
        self.algorithms = {
            'keyword_matching': KeywordSearch(
                case_sensitive=False,
                exact_match_weight=3.0  # Higher weight for exact matches
            ),
            'tfidf': TFIDFSearch(
                min_df=2,        # Require terms to appear in at least 2 documents
                max_df=0.8,      # Exclude terms that appear in more than 80% of documents
                case_sensitive=False
            )
        }
        print("Initialized search algorithms with different parameters:")
        print("  - keyword_matching: Higher exact match weight")
        print("  - tfidf: Filtered vocabulary (min_df=2, max_df=0.8)")

    def create_synthetic_judgments(self):
        """Create synthetic relevance judgments for evaluation."""
        test_queries = [
            "iPhone case",                    # Simple, exact match
            "Samsung phone case",             # Multi-word, brand-specific
            "wireless charger",               # Category-based
            "screen protector iPhone",        # Multi-word with brand
            "leather wallet case",            # Descriptive, specific
            "camera lens protector",          # Technical, specific
            "magnetic charging case",         # Feature-based
            "S Pen replacement",              # Brand-specific accessory
            "multi device charger",           # Descriptive, multi-word
            "tempered glass protector"        # Material + function
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
                        price = product['price']['value']
                        currency = product['price']['currency']
                        print(f"   Price: ${price} {currency}")
                        print(f"   Score: {product['relevance_score']:.4f}")
                        matched_terms = ', '.join(product.get('matched_terms', []))
                        print(f"   Matched: {matched_terms}")
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
        _ = comparison.compare_multiple_queries(test_queries, self.products)

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

        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
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
