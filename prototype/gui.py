"""
Graphical User Interface for Search Algorithm Comparison

This module provides a GUI interface for testing and comparing search algorithms
using tkinter.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
import sys
import pandas as pd
# from typing import List, Dict, Any  # Currently unused

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.keyword_matching import KeywordSearch  # pylint: disable=wrong-import-position
from algorithms.tfidf_search import TFIDFSearch  # pylint: disable=wrong-import-position
from evaluation.comparison import SearchComparison  # pylint: disable=wrong-import-position
from evaluation.metrics import RelevanceJudgment  # pylint: disable=wrong-import-position
from utils.preprocessing import ProductDataPreprocessor, DataLoader  # pylint: disable=wrong-import-position


class SearchGUI:
    """
    GUI application for search algorithm comparison.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("E-commerce Search Algorithm Comparison")
        self.root.geometry("1200x800")

        # Initialize data
        self.products = []
        self.algorithms = {}
        self.relevance_judge = RelevanceJudgment()
        self.preprocessor = ProductDataPreprocessor()

        # Initialize GUI components
        self.search_entry = None
        self.search_button = None
        self.algorithm_var = None
        self.results_tree = None
        self.compare_button = None
        self.export_button = None
        self.comparison_text = None
        self.data_tree = None
        self.results_text = None

        self.setup_gui()
        self.load_sample_data()
        self.initialize_algorithms()

    def setup_gui(self):
        """Set up the GUI layout."""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.setup_search_tab()
        self.setup_comparison_tab()
        self.setup_data_tab()
        self.setup_results_tab()

    def setup_search_tab(self):
        """Set up the interactive search tab."""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Interactive Search")

        # Search input section
        input_frame = ttk.LabelFrame(search_frame, text="Search Query", padding=10)
        input_frame.pack(fill='x', padx=5, pady=5)

        self.search_entry = ttk.Entry(input_frame, font=('Arial', 12))
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.perform_search())

        self.search_button = ttk.Button(input_frame, text="Search", command=self.perform_search)
        self.search_button.pack(side='right')

        # Algorithm selection
        algo_frame = ttk.LabelFrame(search_frame, text="Search Algorithm", padding=10)
        algo_frame.pack(fill='x', padx=5, pady=5)

        self.algorithm_var = tk.StringVar(value="keyword_matching")
        ttk.Radiobutton(algo_frame, text="Keyword Matching", variable=self.algorithm_var,
                       value="keyword_matching").pack(side='left', padx=(0, 20))
        ttk.Radiobutton(algo_frame, text="TF-IDF", variable=self.algorithm_var,
                       value="tfidf").pack(side='left')

        # Results display
        results_frame = ttk.LabelFrame(search_frame, text="Search Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create treeview for results
        columns = ('Rank', 'Title', 'Price', 'Score', 'Algorithm')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)

        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', 
                                          command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)

        self.results_tree.pack(side='left', fill='both', expand=True)
        results_scrollbar.pack(side='right', fill='y')

        # Bind double-click event
        self.results_tree.bind('<Double-1>', self.show_product_details)

    def setup_comparison_tab(self):
        """Set up the algorithm comparison tab."""
        comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(comparison_frame, text="Algorithm Comparison")

        # Comparison controls
        controls_frame = ttk.LabelFrame(comparison_frame, text="Comparison Controls", padding=10)
        controls_frame.pack(fill='x', padx=5, pady=5)

        self.compare_button = ttk.Button(controls_frame, text="Run Comparison",
                                       command=self.run_comparison)
        self.compare_button.pack(side='left', padx=(0, 10))

        self.export_button = ttk.Button(controls_frame, text="Export Results",
                                      command=self.export_comparison_results)
        self.export_button.pack(side='left')

        # Comparison results
        results_frame = ttk.LabelFrame(comparison_frame, text="Comparison Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.comparison_text = scrolledtext.ScrolledText(results_frame, height=20, width=80)
        self.comparison_text.pack(fill='both', expand=True)

    def setup_data_tab(self):
        """Set up the data management tab."""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="Data Management")

        # Data controls
        controls_frame = ttk.LabelFrame(data_frame, text="Data Controls", padding=10)
        controls_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(controls_frame, text="Load Sample Data",
                  command=self.load_sample_data).pack(side='left', padx=(0, 10))

        ttk.Button(controls_frame, text="Load Custom Data",
                  command=self.load_custom_data).pack(side='left', padx=(0, 10))

        ttk.Button(controls_frame, text="Show Data Statistics",
                  command=self.show_data_statistics).pack(side='left')

        # Data display
        display_frame = ttk.LabelFrame(data_frame, text="Product Data", padding=10)
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create treeview for data
        data_columns = ('ID', 'Title', 'Category', 'Price', 'Condition')
        self.data_tree = ttk.Treeview(display_frame, columns=data_columns, 
                                      show='headings', height=15)

        for col in data_columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=200)

        # Scrollbar for data
        data_scrollbar = ttk.Scrollbar(display_frame, orient='vertical', 
                                       command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=data_scrollbar.set)

        self.data_tree.pack(side='left', fill='both', expand=True)
        data_scrollbar.pack(side='right', fill='y')

        # Bind double-click event
        self.data_tree.bind('<Double-1>', self.show_data_details)

    def setup_results_tab(self):
        """Set up the results analysis tab."""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results Analysis")

        # Results controls
        controls_frame = ttk.LabelFrame(results_frame, text="Analysis Controls", padding=10)
        controls_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(controls_frame, text="Generate Report",
                  command=self.generate_report).pack(side='left', padx=(0, 10))

        ttk.Button(controls_frame, text="Export Data",
                  command=self.export_data).pack(side='left')

        # Results display
        display_frame = ttk.LabelFrame(results_frame, text="Analysis Results", padding=10)
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.results_text = scrolledtext.ScrolledText(display_frame, height=20, width=80)
        self.results_text.pack(fill='both', expand=True)

    def load_sample_data(self):
        """Load sample product data."""
        sample_products = [
            {
                'id': 1,
                'title': 'iPhone 15 Pro Max Case - Clear Transparent',
                'description': ('Premium clear case for iPhone 15 Pro Max with wireless charging '
                                 'support and drop protection'),
                'category': 'Phone Cases & Accessories',
                'price': {'value': '29.99', 'currency': 'USD'},
                'condition': 'NEW'
            },
            {
                'id': 2,
                'title': 'Samsung Galaxy S24 Ultra Case - Black',
                'description': ('Protective case for Samsung Galaxy S24 Ultra with kickstand '
                                 'and camera protection'),
                'category': 'Phone Cases & Accessories',
                'price': {'value': '24.99', 'currency': 'USD'},
                'condition': 'NEW'
            },
            {
                'id': 3,
                'title': 'iPhone 15 Screen Protector - Tempered Glass',
                'description': ('9H hardness tempered glass screen protector for iPhone 15 '
                                 'with easy installation'),
                'category': 'Screen Protectors',
                'price': {'value': '12.99', 'currency': 'USD'},
                'condition': 'NEW'
            },
            {
                'id': 4,
                'title': 'Wireless Charger Pad - Fast Charging',
                'description': ('Universal wireless charging pad compatible with iPhone '
                                 'and Android phones'),
                'category': 'Chargers',
                'price': {'value': '19.99', 'currency': 'USD'},
                'condition': 'NEW'
            },
            {
                'id': 5,
                'title': 'Premium Leather Wallet Case for iPhone 15 Pro Max with Card Slots',
                'description': ('Handcrafted genuine leather case with RFID blocking technology '
                                 'and multiple card slots'),
                'category': 'Phone Cases & Accessories',
                'price': {'value': '79.99', 'currency': 'USD'},
                'condition': 'NEW'
            },
            {
                'id': 6,
                'title': 'Samsung Galaxy S24 Ultra Camera Lens Protector Kit',
                'description': ('Tempered glass lens protectors for all camera modules '
                                 'with precise cutouts'),
                'category': 'Camera Accessories',
                'price': {'value': '15.99', 'currency': 'USD'},
                'condition': 'NEW'
            },
            {
                'id': 7,
                'title': 'Universal Wireless Charging Stand with LED Display',
                'description': ('Adjustable charging stand compatible with all smartphones '
                                 'and smartwatches'),
                'category': 'Chargers',
                'price': {'value': '45.99', 'currency': 'USD'},
                'condition': 'NEW'
            },
            {
                'id': 8,
                'title': 'iPhone 15 Pro Max MagSafe Compatible Case',
                'description': 'Magnetic case with wireless charging support and strong magnets',
                'category': 'Phone Cases & Accessories',
                'price': {'value': '39.99', 'currency': 'USD'},
                'condition': 'NEW'
            },
            {
                'id': 9,
                'title': 'Samsung Galaxy S24 Ultra S Pen Replacement',
                'description': ('Original S Pen stylus for Galaxy S24 Ultra '
                                 'with pressure sensitivity'),
                'category': 'Stylus & Accessories',
                'price': {'value': '59.99', 'currency': 'USD'},
                'condition': 'NEW'
            },
            {
                'id': 10,
                'title': 'Multi-Device Wireless Charging Pad',
                'description': ('Charge iPhone, Samsung, and AirPods simultaneously '
                                 'with fast charging'),
                'category': 'Chargers',
                'price': {'value': '89.99', 'currency': 'USD'},
                'condition': 'NEW'
            },
            {
                'id': 11,
                'title': 'iPad Air 5th Gen Case - Folio',
                'description': ('Premium folio case for iPad Air 5th generation '
                                 'with auto sleep/wake'),
                'category': 'Tablet Cases',
                'price': {'value': '49.99', 'currency': 'USD'},
                'condition': 'NEW'
            },
            {
                'id': 12,
                'title': 'MacBook Pro 16-inch Case - Hard Shell',
                'description': ('Hard shell protective case for MacBook Pro 16-inch '
                                 'with precise cutouts'),
                'category': 'Laptop Cases',
                'price': {'value': '79.99', 'currency': 'USD'},
                'condition': 'NEW'
            }
        ]

        self.products = sample_products
        self.update_data_display()
        messagebox.showinfo("Success", f"Loaded {len(sample_products)} sample products")

    def initialize_algorithms(self):
        """Initialize search algorithms with different parameters for distinct results."""
        self.algorithms = {
            'keyword_matching': KeywordSearch(
                case_sensitive=False,
                exact_match_weight=25.0  # Very high weight for exact matches
            ),
            'tfidf': TFIDFSearch(
                min_df=2,        # Require terms to appear in at least 2 documents
                max_df=0.6,      # Exclude terms that appear in more than 60% of documents
                case_sensitive=False
            )
        }

    def perform_search(self):
        """Perform search using selected algorithm."""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return

        algorithm_name = self.algorithm_var.get()
        algorithm = self.algorithms[algorithm_name]

        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Perform search
        results = algorithm.search(query, self.products, limit=10)

        # Display results
        for i, product in enumerate(results, 1):
            price = f"${product['price']['value']} {product['price']['currency']}"
            score = f"{product['relevance_score']:.4f}"

            self.results_tree.insert('', 'end', values=(
                i, product['title'][:50] + '...' if len(product['title']) > 50 else product['title'],
                price, score, algorithm_name
            ))

    def show_product_details(self, _event=None):
        """Show detailed product information."""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            title = item['values'][1]

            # Find the actual product
            for product in self.products:
                if product['title'].startswith(title.replace('...', '')):
                    details = f"Title: {product['title']}\n"
                    details += f"Description: {product.get('description', 'N/A')}\n"
                    details += f"Category: {product.get('category', 'N/A')}\n"
                    details += f"Price: ${product['price']['value']} {product['price']['currency']}\n"
                    details += f"Condition: {product.get('condition', 'N/A')}"

                    messagebox.showinfo("Product Details", details)
                    break

    def run_comparison(self):
        """Run algorithm comparison in a separate thread."""
        def comparison_thread():
            try:
                # Create test queries
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
                    "tempered glass protector",       # Material + function
                    "clear transparent case",          # Descriptive, specific
                    "fast charging pad",              # Feature-based
                    "iPhone 15 Pro Max",              # Specific model
                    "Galaxy S24 Ultra",              # Specific model
                    "MacBook Pro case",               # Laptop case
                    "protective case",                # Generic term
                    "charging stand",                 # Specific feature
                    "lens protector",                 # Technical term
                    "case iPhone",                    # Reversed order
                    "charger wireless"                # Reversed order
                ]

                # Create synthetic relevance judgments
                self.relevance_judge.create_synthetic_judgments(test_queries, self.products)

                # Run comparison
                comparison = SearchComparison(self.algorithms, self.relevance_judge)
                results = comparison.compare_multiple_queries(test_queries, self.products)

                # Update GUI in main thread
                self.root.after(0, self.display_comparison_results, results)

            except (ValueError, KeyError, AttributeError, ConnectionError) as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Comparison failed: {e}"))

        # Start comparison in separate thread
        threading.Thread(target=comparison_thread, daemon=True).start()

        # Show progress message
        self.comparison_text.delete(1.0, tk.END)
        self.comparison_text.insert(tk.END, "Running comparison... Please wait.")

    def display_comparison_results(self, results):
        """Display comparison results in the GUI."""
        self.comparison_text.delete(1.0, tk.END)

        # Format and display results
        summary = results['summary']
        aggregated = results['aggregated']

        report = "Search Algorithm Comparison Report\n"
        report += "=" * 50 + "\n\n"

        report += f"Total Queries: {aggregated['total_queries']}\n"
        report += f"Algorithms Compared: {', '.join(self.algorithms.keys())}\n\n"

        report += "Performance Metrics (Average):\n"
        report += "-" * 40 + "\n"
        report += f"{'Algorithm':<20} {'MAP':<8} {'MRR':<8} {'F1@5':<8}\n"
        report += "-" * 40 + "\n"

        for algo_name in summary['performance_ranking']:
            algo_data = aggregated['algorithms'][algo_name]
            metrics = algo_data['metrics']
            report += f"{algo_name:<20} {metrics['map']:<8.4f} {metrics['mrr']:<8.4f} {metrics['f1@5']:<8.4f}\n"

        report += "\nBest Performing Algorithms:\n"
        report += "-" * 30 + "\n"
        for metric, info in summary['best_algorithms'].items():
            report += f"{metric}: {info['algorithm']} ({info['score']:.4f})\n"

        report += "\nKey Insights:\n"
        report += "-" * 15 + "\n"
        for insight in summary['key_insights']:
            report += f"• {insight}\n"

        self.comparison_text.insert(tk.END, report)

    def load_custom_data(self):
        """Load custom data from file."""
        filename = filedialog.askopenfilename(
            title="Select data file",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            try:
                if filename.endswith('.json'):
                    products = DataLoader.load_from_json(filename)
                elif filename.endswith('.csv'):
                    products = DataLoader.load_from_csv(filename)
                else:
                    messagebox.showerror("Error", "Unsupported file format")
                    return

                # Preprocess the data
                cleaned_products = self.preprocessor.clean_product_data(products)

                if cleaned_products:
                    self.products = cleaned_products
                    self.update_data_display()
                    messagebox.showinfo("Success", f"Loaded {len(cleaned_products)} products")
                else:
                    messagebox.showerror("Error", "No valid products found")

            except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

    def update_data_display(self):
        """Update the data display treeview."""
        # Clear existing items
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)

        # Add products to treeview
        for product in self.products:
            price = f"${product['price']['value']} {product['price']['currency']}"
            self.data_tree.insert('', 'end', values=(
                product['id'],
                product['title'][:50] + '...' if len(product['title']) > 50 else product['title'],
                product.get('category', 'N/A'),
                price,
                product.get('condition', 'N/A')
            ))

    def show_data_statistics(self):
        """Show data statistics."""
        if not self.products:
            messagebox.showwarning("Warning", "No data loaded")
            return

        # Calculate statistics
        stats = self.preprocessor.get_statistics()

        stats_text = "Data Statistics\n"
        stats_text += "=" * 20 + "\n\n"
        stats_text += f"Total Products: {stats['total_products']}\n"
        stats_text += f"Average Title Length: {stats['average_title_length']:.1f} characters\n"
        stats_text += f"Average Description Length: {stats['average_description_length']:.1f} characters\n\n"

        stats_text += "Category Distribution:\n"
        for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_products']) * 100
            stats_text += f"  {category}: {count} ({percentage:.1f}%)\n"

        messagebox.showinfo("Data Statistics", stats_text)

    def show_data_details(self, _event=None):
        """Show detailed data information."""
        selection = self.data_tree.selection()
        if selection:
            item = self.data_tree.item(selection[0])
            product_id = item['values'][0]

            # Find the product
            for product in self.products:
                if str(product['id']) == str(product_id):
                    details = f"ID: {product['id']}\n"
                    details += f"Title: {product['title']}\n"
                    details += f"Description: {product.get('description', 'N/A')}\n"
                    details += f"Category: {product.get('category', 'N/A')}\n"
                    price_value = product['price']['value']
                    price_currency = product['price']['currency']
                    details += f"Price: ${price_value} {price_currency}\n"
                    details += f"Condition: {product.get('condition', 'N/A')}"

                    messagebox.showinfo("Product Details", details)
                    break

    def export_comparison_results(self):
        """Export comparison results to file."""
        filename = filedialog.asksaveasfilename(
            title="Save comparison results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                if filename.endswith('.json'):
                    # Export as JSON (would need to store results)
                    messagebox.showinfo("Info", "JSON export not implemented yet")
                else:
                    # Export as text
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(self.comparison_text.get(1.0, tk.END))
                    messagebox.showinfo("Success", f"Results exported to {filename}")
            except (OSError, PermissionError, ValueError) as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    def generate_report(self):
        """Generate a comprehensive analysis report."""
        if not self.products:
            messagebox.showwarning("Warning", "No data available for analysis")
            return

        report = "E-commerce Search Algorithm Analysis Report\n"
        report += "=" * 50 + "\n\n"

        # Data overview
        report += "Data Overview:\n"
        report += f"  Total Products: {len(self.products)}\n"
        report += f"  Algorithms: {', '.join(self.algorithms.keys())}\n\n"

        # Product categories
        categories = {}
        for product in self.products:
            category = product.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1

        report += "Product Categories:\n"
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.products)) * 100
            report += f"  {category}: {count} ({percentage:.1f}%)\n"

        report += "\nPrice Analysis:\n"
        prices = []
        for product in self.products:
            try:
                price = float(product['price']['value'])
                prices.append(price)
            except ValueError:
                continue

        if prices:
            report += f"  Average Price: ${sum(prices)/len(prices):.2f}\n"
            report += f"  Min Price: ${min(prices):.2f}\n"
            report += f"  Max Price: ${max(prices):.2f}\n"

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, report)

    def export_data(self):
        """Export current data to file."""
        filename = filedialog.asksaveasfilename(
            title="Save data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.products, f, indent=2, ensure_ascii=False)
                elif filename.endswith('.csv'):
                    df_data = []
                    for product in self.products:
                        row = {
                            'id': product.get('id'),
                            'title': product.get('title'),
                            'description': product.get('description'),
                            'category': product.get('category'),
                            'price': product.get('price', {}).get('value'),
                            'condition': product.get('condition')
                        }
                        df_data.append(row)

                    df = pd.DataFrame(df_data)
                    df.to_csv(filename, index=False, encoding='utf-8')

                messagebox.showinfo("Success", f"Data exported to {filename}")
            except (OSError, PermissionError, ValueError, ImportError) as e:
                messagebox.showerror("Error", f"Export failed: {e}")


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    SearchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
