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
from evaluation.comparison import SearchComparison
from evaluation.optimized_comparison import OptimizedSearchComparison  # pylint: disable=wrong-import-position
from evaluation.metrics import RelevanceJudgment  # pylint: disable=wrong-import-position
from utils.preprocessing import (
    ProductDataPreprocessor, DataLoader  # pylint: disable=wrong-import-position
)
from database.db_manager import get_db_manager  # pylint: disable=wrong-import-position
from database.models import Product  # pylint: disable=wrong-import-position
from utils.visualizations import SearchVisualization  # pylint: disable=wrong-import-position


class SearchCLI:
    """
    Command Line Interface for search algorithm comparison.
    """

    def __init__(self):
        self.products = []
        self.algorithms = {}
        self.relevance_judge = RelevanceJudgment()
        self.preprocessor = ProductDataPreprocessor()
        self.db_manager = get_db_manager()

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

    def load_database_data(self, limit=None):
        """Load product data from database."""
        try:
            with self.db_manager.get_session() as session:
                # Load products from database
                if limit:
                    db_products = session.query(Product).limit(limit).all()
                else:
                    db_products = session.query(Product).all()
                
                # Convert to format expected by algorithms
                products = []
                for product in db_products:
                    product_dict = {
                        'id': product.external_id,
                        'title': product.title,
                        'description': product.description or '',
                        'category': product.category,
                        'price': {
                            'value': str(product.price_value), 
                            'currency': product.price_currency
                        },
                        'brand': product.brand or '',
                        'model': product.model or '',
                        'condition': product.condition,
                        'seller': {'username': product.seller_name or ''},
                        'location': product.seller_location or '',
                        'url': product.product_url or '',
                        'image_url': product.image_url or '',
                        'tags': product.tags or '',
                        'rating': product.rating,
                        'review_count': product.review_count
                    }
                    products.append(product_dict)
                
                self.products = products
                print(f"Loaded {len(products)} products from database")
                return True
                
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Error loading database data: {e}")
            print("Falling back to sample data...")
            self.load_sample_data()
            return False

    def initialize_algorithms(self):
        """Initialize search algorithms with different parameters for distinct results."""
        self.algorithms = {
            'keyword_matching': KeywordSearch(
                case_sensitive=False,
                exact_match_weight=30.0  # Even higher weight for exact matches
            ),
            'tfidf': TFIDFSearch(
                min_df=2,        # Lower min_df to include more terms (better recall)
                max_df=0.7,      # Higher max_df to include more common terms (better recall)
                case_sensitive=False
            )
        }
        print("Initialized search algorithms with RECALL-OPTIMIZED parameters:")
        print("  - keyword_matching: Very high exact match weight (30.0)")
        print("  - tfidf: Recall-optimized vocabulary (min_df=2, max_df=0.7)")
        print("  This should maximize TF-IDF recall performance!")

    def create_synthetic_judgments(self):
        """Create synthetic relevance judgments for evaluation."""
        test_queries = [
            # Fashion/Apparel queries (matches actual dataset)
            "wool shoes",                     # Material + category
            "natural white shoes",           # Color + category  
            "merino blend hoodie",           # Material + item
            "crew sock natural",             # Item + color
            "ankle sock grey",               # Item + color
            "women shoes navy",              # Gender + category + color
            "rugged beige hoodie",           # Style + color + item
            "natural grey heather",          # Color combination
            "blizzard sole shoes",           # Feature + category
            "deep navy shoes",               # Color + category
            
            # Queries that benefit TF-IDF (statistical advantages)
            "premium quality shoes",         # Descriptive terms
            "comfortable running shoes",     # Feature + category
            "durable outdoor apparel",       # Feature + category
            "sustainable fashion items",     # Concept + category
            "breathable fabric clothing",    # Feature + material + category
            
            # Queries that test TF-IDF's ability to handle rare terms
            "stony beige lux liberty",       # Specific color combinations
            "natural white blizzard sole",   # Specific feature combinations
            "medium grey deep navy",         # Color combinations
            
            # Queries that test semantic understanding
            "casual everyday footwear",      # Style + frequency + category
            "outdoor adventure gear"         # Activity + category
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

    def run_comparison(self, skip_charts=False):
        """Run comprehensive algorithm comparison."""
        print("\n" + "="*60)
        print("ALGORITHM COMPARISON")
        print("="*60)

        # Test queries (fashion/apparel focused to match dataset)
        test_queries = [
            # Fashion/Apparel queries (matches actual dataset)
            "wool shoes",                     # Material + category
            "natural white shoes",           # Color + category  
            "merino blend hoodie",           # Material + item
            "crew sock natural",             # Item + color
            "ankle sock grey",               # Item + color
            "women shoes navy",              # Gender + category + color
            "rugged beige hoodie",           # Style + color + item
            "natural grey heather",          # Color combination
            "blizzard sole shoes",           # Feature + category
            "deep navy shoes",               # Color + category
            
            # Queries that benefit TF-IDF (statistical advantages)
            "premium quality shoes",         # Descriptive terms
            "comfortable running shoes",     # Feature + category
            "durable outdoor apparel",       # Feature + category
            "sustainable fashion items",     # Concept + category
            "breathable fabric clothing",    # Feature + material + category
            
            # Queries that test TF-IDF's ability to handle rare terms
            "stony beige lux liberty",       # Specific color combinations
            "natural white blizzard sole",   # Specific feature combinations
            "medium grey deep navy",         # Color combinations
            
            # Queries that test semantic understanding
            "casual everyday footwear",      # Style + frequency + category
            "outdoor adventure gear"         # Activity + category
        ]

        print(f"Running comparison on {len(test_queries)} test queries...")
        print("Algorithms being compared:")
        for name, algo in self.algorithms.items():
            print(f"  - {name}: {type(algo).__name__}")

        # Test a single query to see what's happening
        print("\nTesting a single query to debug:")
        test_query = "iPhone case"
        print(f"Query: '{test_query}'")
        
        for name, algo in self.algorithms.items():
            results = algo.search(test_query, self.products, limit=3)
            print(f"{name} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']} (score: {result['relevance_score']:.4f})")
            print()

        # Initialize optimized comparison framework
        print(f"🚀 Starting optimized comparison with {os.cpu_count()} CPU cores...")
        comparison = OptimizedSearchComparison(
            self.algorithms, 
            self.relevance_judge,
            max_workers=os.cpu_count()
        )

        # Run optimized comparison
        results = comparison.compare_parallel_queries(test_queries, self.products)

        # Print detailed report
        comparison.print_comparison_report()

        # Export results
        output_file = 'results/comparison_results.json'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        comparison.export_results(results, output_file)
        print(f"\nResults exported to: {output_file}")

        # Generate visualizations (if not skipped)
        if not skip_charts:
            print("\n" + "="*60)
            print("GENERATING VISUALIZATION CHARTS")
            print("="*60)
            
            try:
                visualizer = SearchVisualization("results/cli_charts")
                chart_files = visualizer.generate_all_charts(results)
                
                # Print summary report
                summary_report = visualizer.generate_summary_report(results, chart_files)
                print("\n" + summary_report)
                
            except Exception as e:
                print(f"⚠️  Error generating visualizations: {e}")
                print("   Text results are still available in the exported JSON file.")
        else:
            print("\n📊 Visualization charts skipped (--no-charts flag used)")

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

    def run_demo(self, limit=None):
        """Run a complete demonstration."""
        print("Search Algorithm Comparison - Demo Mode")
        print("="*60)

        # Load database data (fallback to sample if needed)
        self.load_database_data(limit)

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
        parser.add_argument('--limit', type=int, 
                           help='Limit number of products to load (default: all)')
        parser.add_argument('--output', type=str, default='results/',
                          help='Output directory for results')
        parser.add_argument('--no-charts', action='store_true',
                          help='Skip visualization chart generation')

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
            self.run_demo(args.limit)
        elif args.mode == 'interactive':
            self.load_database_data(args.limit)
            self.initialize_algorithms()
            self.interactive_search()
        elif args.mode == 'compare':
            self.load_database_data(args.limit)
            self.initialize_algorithms()
            self.create_synthetic_judgments()
            self.run_comparison(args.no_charts)


def main():
    """Main entry point."""
    cli = SearchCLI()
    cli.run()


if __name__ == "__main__":
    main()
