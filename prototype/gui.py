"""
Graphical User Interface for Search Algorithm Comparison

This module provides a GUI interface for testing and comparing search algorithms
using tkinter.
"""

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    tk = None
    ttk = None
    scrolledtext = None
    messagebox = None
    filedialog = None
    print("⚠️  tkinter not available. GUI mode will be disabled.")
    print("   On macOS: tkinter is usually included with Python")
    print("   On Ubuntu: sudo apt-get install python3-tk")
    print("   On Windows: tkinter should be included with Python")
# Only import other modules if tkinter is available
if TKINTER_AVAILABLE:
    import threading
    import json
    import os
    import sys
    import pandas as pd
    # import matplotlib.backends.backend_tkagg as tkagg  # Currently unused
    # import seaborn as sns  # Currently unused
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    # from typing import List, Dict, Any  # Currently unused

    # Add parent directory to path for imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from algorithms.keyword_matching import KeywordSearch  # pylint: disable=wrong-import-position
    from algorithms.tfidf_search import TFIDFSearch  # pylint: disable=wrong-import-position
    from evaluation.comparison import SearchComparison  # pylint: disable=wrong-import-position
    from evaluation.optimized_comparison import OptimizedSearchComparison  # pylint: disable=wrong-import-position
    from evaluation.gui_optimized_comparison import GUIOptimizedComparison  # pylint: disable=wrong-import-position
    from evaluation.metrics import RelevanceJudgment  # pylint: disable=wrong-import-position
    from utils.preprocessing import (
        ProductDataPreprocessor, DataLoader  # pylint: disable=wrong-import-position
    )
    from database.db_manager import get_db_manager  # pylint: disable=wrong-import-position
    from database.models import Product  # pylint: disable=wrong-import-position
    from utils.visualizations import SearchVisualization  # pylint: disable=wrong-import-position
else:
    # Define dummy classes to prevent import errors when tkinter is not available
    class threading:
        Thread = None
    class json:
        @staticmethod
        def loads(*args, **kwargs):
            return {}
        @staticmethod
        def dumps(*args, **kwargs):
            return "{}"
    class os:
        path = None
    class sys:
        @staticmethod
        def exit(*args, **kwargs):
            pass
    class pd:
        DataFrame = None
    class np:
        array = None
    class plt:
        @staticmethod
        def figure(*args, **kwargs):
            return None
    class Figure:
        pass
    class FigureCanvasTkAgg:
        def __init__(self, *args, **kwargs):
            pass
    class KeywordSearch:
        def __init__(self, *args, **kwargs):
            pass
    class TFIDFSearch:
        def __init__(self, *args, **kwargs):
            pass
    class SearchComparison:
        def __init__(self, *args, **kwargs):
            pass
    class RelevanceJudgment:
        pass
    class ProductDataPreprocessor:
        pass
    class DataLoader:
        pass
    class get_db_manager:
        @staticmethod
        def __call__(*args, **kwargs):
            return None
    class Product:
        pass
    class SearchVisualization:
        def __init__(self, *args, **kwargs):
            pass


class SearchGUI:
    """
    GUI application for search algorithm comparison.
    """

    def __init__(self, root):
        if not TKINTER_AVAILABLE:
            raise ImportError("tkinter is not available. Cannot create GUI.")
        self.root = root
        self.root.title("E-commerce Search Algorithm Comparison")
        self.root.geometry("1200x800")

        # Initialize data
        self.products = []
        self.algorithms = {}
        self.relevance_judge = RelevanceJudgment()
        self.preprocessor = ProductDataPreprocessor()
        self.db_manager = get_db_manager()

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
        
        # Enhanced GUI components
        self.limit_var = None
        self.limit_entry = None
        self.comparison_notebook = None
        self.charts_notebook = None
        self.chart_frames = None
        self.chart_figures = None
        self.chart_canvases = None
        self.metrics_tree = None
        self.data_notebook = None
        self.data_figure = None
        self.data_canvas = None

        self.setup_gui()
        # Load a reasonable amount of data initially (not all 43K products)
        self.load_database_data(limit=1000)  # Start with 1K products for GUI responsiveness
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
        self.results_tree = ttk.Treeview(
            results_frame, columns=columns, show='headings', height=15
        )

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
        self.export_button.pack(side='left', padx=(0, 10))

        # Add limit control
        ttk.Label(controls_frame, text="Product Limit:").pack(side='left', padx=(20, 5))
        self.limit_var = tk.StringVar(value="")
        self.limit_entry = ttk.Entry(controls_frame, textvariable=self.limit_var, width=10)
        self.limit_entry.pack(side='left', padx=(0, 5))
        ttk.Label(controls_frame, text="(empty = all products)").pack(side='left')

        # Create notebook for comparison results
        self.comparison_notebook = ttk.Notebook(comparison_frame)
        self.comparison_notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Text results tab
        text_frame = ttk.Frame(self.comparison_notebook)
        self.comparison_notebook.add(text_frame, text="Text Results")
        
        self.comparison_text = scrolledtext.ScrolledText(text_frame, height=15, width=80)
        self.comparison_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Charts tab
        charts_frame = ttk.Frame(self.comparison_notebook)
        self.comparison_notebook.add(charts_frame, text="Visual Charts")
        
        # Charts notebook for separate charts
        self.charts_notebook = ttk.Notebook(charts_frame)
        self.charts_notebook.pack(fill='both', expand=True)
        
        # Create separate tabs for each chart
        self.chart_frames = {}
        self.chart_figures = {}
        self.chart_canvases = {}
        
        chart_names = [
            ("Performance Comparison", "performance_comparison"),
            ("Precision & Recall Trends", "precision_recall_trends"),
            ("F1-Score Trends", "f1_score_trends")
        ]
        
        for display_name, chart_key in chart_names:
            # Create frame for each chart
            chart_frame = ttk.Frame(self.charts_notebook)
            self.charts_notebook.add(chart_frame, text=display_name)
            self.chart_frames[chart_key] = chart_frame
            
            # Create separate matplotlib figure for each chart
            chart_figure = Figure(figsize=(10, 6), dpi=100)
            chart_canvas = FigureCanvasTkAgg(chart_figure, chart_frame)
            chart_canvas.get_tk_widget().pack(fill='both', expand=True)
            
            self.chart_figures[chart_key] = chart_figure
            self.chart_canvases[chart_key] = chart_canvas

        # Metrics table tab
        metrics_frame = ttk.Frame(self.comparison_notebook)
        self.comparison_notebook.add(metrics_frame, text="Detailed Metrics")
        
        # Create treeview for detailed metrics
        metrics_columns = ('Metric', 'K', 'Algorithm', 'Value')
        self.metrics_tree = ttk.Treeview(
            metrics_frame, columns=metrics_columns, show='headings', height=20
        )
        
        for col in metrics_columns:
            self.metrics_tree.heading(col, text=col)
            self.metrics_tree.column(col, width=150)
        
        # Add scrollbar for metrics
        metrics_scrollbar = ttk.Scrollbar(
            metrics_frame, orient='vertical', command=self.metrics_tree.yview
        )
        self.metrics_tree.configure(yscrollcommand=metrics_scrollbar.set)
        
        self.metrics_tree.pack(side='left', fill='both', expand=True)
        metrics_scrollbar.pack(side='right', fill='y')

    def setup_data_tab(self):
        """Set up the data management tab."""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="Data Management")

        # Data controls
        controls_frame = ttk.LabelFrame(data_frame, text="Data Controls", padding=10)
        controls_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(controls_frame, text="Load Database Data",
                  command=self.load_database_data).pack(side='left', padx=(0, 10))

        ttk.Button(controls_frame, text="Load Sample Data",
                  command=self.load_sample_data).pack(side='left', padx=(0, 10))

        ttk.Button(controls_frame, text="Load Custom Data",
                  command=self.load_custom_data).pack(side='left', padx=(0, 10))

        ttk.Button(controls_frame, text="Show Data Statistics",
                  command=self.show_data_statistics).pack(side='left', padx=(0, 10))

        ttk.Button(controls_frame, text="Generate Visualizations",
                  command=self.generate_data_visualizations).pack(side='left')

        # Create notebook for data display
        self.data_notebook = ttk.Notebook(data_frame)
        self.data_notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Data table tab
        table_frame = ttk.Frame(self.data_notebook)
        self.data_notebook.add(table_frame, text="Product Data Table")
        
        # Create treeview for data
        data_columns = ('ID', 'Title', 'Category', 'Price', 'Condition')
        self.data_tree = ttk.Treeview(table_frame, columns=data_columns, 
                                      show='headings', height=15)

        for col in data_columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=200)

        # Scrollbar for data
        data_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', 
                                       command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=data_scrollbar.set)

        self.data_tree.pack(side='left', fill='both', expand=True)
        data_scrollbar.pack(side='right', fill='y')

        # Bind double-click event
        self.data_tree.bind('<Double-1>', self.show_data_details)

        # Data visualizations tab
        viz_frame = ttk.Frame(self.data_notebook)
        self.data_notebook.add(viz_frame, text="Data Visualizations")
        
        # Create matplotlib figure for data visualizations
        self.data_figure = Figure(figsize=(12, 8), dpi=100)
        self.data_canvas = FigureCanvasTkAgg(self.data_figure, viz_frame)
        self.data_canvas.get_tk_widget().pack(fill='both', expand=True)

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

    def load_database_data(self, limit=None):
        """Load product data from database with progress indication."""
        try:
            print(f"📊 Loading database data (limit: {limit if limit else 'all'})...")
            
            with self.db_manager.get_session() as session:
                # Load products from database
                if limit:
                    print(f"  Loading first {limit:,} products...")
                    db_products = session.query(Product).limit(limit).all()
                else:
                    print(f"  Loading ALL products (this may take a while)...")
                    db_products = session.query(Product).all()

                print(f"  Converting {len(db_products):,} products to algorithm format...")
                
                # Convert to format expected by algorithms
                products = []
                for i, product in enumerate(db_products):
                    if i % 1000 == 0 and i > 0:
                        print(f"    Converted {i:,}/{len(db_products):,} products...")
                    
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
                print(f"✅ Successfully loaded {len(products):,} products from database")
                self.update_data_display()
                
                # Show success message with database info
                total_products = len(products)
                db_info = self.db_manager.get_database_info()
                messagebox.showinfo(
                    "Database Loaded Successfully", 
                    f"Loaded {total_products:,} products from database\n"
                    f"Database: {db_info['database_type']}\n"
                    f"Location: {db_info['database_url']}"
                )
                
        except (ImportError, AttributeError, ValueError, ConnectionError) as e:
            messagebox.showerror("Database Error", f"Failed to load database: {e}")
            # Fallback to sample data
            self.load_sample_data()

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
                i, (product['title'][:50] + '...' 
                    if len(product['title']) > 50 
                    else product['title']),
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
                    details += (f"Price: ${product['price']['value']} "
                               f"{product['price']['currency']}\n")
                    details += f"Condition: {product.get('condition', 'N/A')}"

                    messagebox.showinfo("Product Details", details)
                    break

    def run_comparison(self):
        """Run algorithm comparison in a separate thread."""
        def comparison_thread():
            try:
                # Get limit from GUI
                limit_text = self.limit_var.get().strip()
                limit = int(limit_text) if limit_text else None
                
                # Load data with limit if needed
                if not self.products:
                    self.load_database_data(limit or 1000)  # Default to 1K if no limit specified
                elif limit and len(self.products) != limit:
                    print(f"🔄 Reloading data with limit {limit}...")
                    self.load_database_data(limit)
                # Create test queries
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

                # Create synthetic relevance judgments
                self.relevance_judge.create_synthetic_judgments(test_queries, self.products)

                # Run GUI-optimized comparison (threading-based, no multiprocessing issues)
                print(f"🚀 Starting GUI-optimized comparison...")
                comparison = GUIOptimizedComparison(
                    self.algorithms, 
                    self.relevance_judge,
                    max_workers=4  # Conservative for GUI stability
                )
                results = comparison.compare_algorithms_fast(test_queries, self.products)

                # Update GUI in main thread
                self.root.after(0, self.display_comparison_results, results)

            except (ValueError, KeyError, AttributeError, ConnectionError) as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", f"Comparison failed: {e}"
                ))

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

        # Enhanced metrics display
        report += "Performance Metrics (Average):\n"
        report += "-" * 80 + "\n"
        report += f"{'Algorithm':<20} {'MAP':<8} {'MRR':<8} {'F1@5':<8} {'NDCG@10':<10}\n"
        report += "-" * 65 + "\n"

        for algo_name in summary['performance_ranking']:
            algo_data = aggregated['algorithms'][algo_name]
            metrics = algo_data['metrics']
            ndcg = metrics.get('ndcg@10', 0)
            report += (f"{algo_name:<20} {metrics['map']:<8.4f} "
                      f"{metrics['mrr']:<8.4f} {metrics['f1@5']:<8.4f} "
                      f"{ndcg:<10.4f}\n")

        report += "\nBest Performing Algorithms:\n"
        report += "-" * 30 + "\n"
        for metric, info in summary['best_algorithms'].items():
            report += f"{metric}: {info['algorithm']} ({info['score']:.4f})\n"

        # Detailed metrics at different K values
        report += "\nDetailed Metrics at Different K Values:\n"
        report += "-" * 50 + "\n"

        k_values = [1, 3, 5, 10]
        for k in k_values:
            report += f"\nAt K={k}:\n"
            report += (f"{'Algorithm':<20} {'Precision':<10} {'Recall':<10} "
                       f"{'F1-Score':<10} {'NDCG':<8}\n")
            report += "-" * 60 + "\n"
            
            for algo_name in summary['performance_ranking']:
                algo_data = aggregated['algorithms'][algo_name]
                metrics = algo_data['metrics']

                precision = metrics.get(f'precision@{k}', 0)
                recall = metrics.get(f'recall@{k}', 0)
                f1 = metrics.get(f'f1@{k}', 0)
                ndcg = metrics.get(f'ndcg@{k}', 0)

                report += (f"{algo_name:<20} {precision:<10.4f} {recall:<10.4f} "
                          f"{f1:<10.4f} {ndcg:<8.4f}\n")

        report += "\nKey Insights:\n"
        report += "-" * 15 + "\n"
        for insight in summary['key_insights']:
            report += f"• {insight}\n"

        self.comparison_text.insert(tk.END, report)

        # Update detailed metrics table
        self.update_metrics_table(results)

        # Generate visualizations
        self.generate_comparison_charts(results)

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
        stats_text += (f"Average Description Length: "
                      f"{stats['average_description_length']:.1f} characters\n\n")

        stats_text += "Category Distribution:\n"
        for category, count in sorted(
            stats['categories'].items(), 
            key=lambda x: x[1], 
            reverse=True
        ):
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

    def update_metrics_table(self, results):
        """Update the detailed metrics table with comparison results."""
        # Clear existing items
        for item in self.metrics_tree.get_children():
            self.metrics_tree.delete(item)
        
        aggregated = results['aggregated']
        k_values = [1, 3, 5, 10]
        metrics_mapping = {
            'precision': 'Precision',
            'recall': 'Recall', 
            'f1_score': 'F1-Score',
            'ndcg': 'NDCG'
        }
        
        for algo_name, algo_data in aggregated['algorithms'].items():
            metrics = algo_data['metrics']
            
            for k in k_values:
                for metric_key, metric_name in metrics_mapping.items():
                    if metric_key == 'f1_score':
                        value = metrics.get(f'f1@{k}', 0)
                    elif metric_key == 'ndcg':
                        value = metrics.get(f'ndcg@{k}', 0)
                    else:
                        value = metrics.get(f'{metric_key}@{k}', 0)
                    
                    self.metrics_tree.insert('', 'end', values=(
                        metric_name,
                        f'K={k}',
                        algo_name,
                        f'{value:.4f}'
                    ))

    def generate_comparison_charts(self, results):
        """Generate separate visual charts for algorithm comparison."""
        aggregated = results['aggregated']
        algorithms = list(aggregated['algorithms'].keys())
        
        # 1. Performance Metrics Comparison Chart
        self._generate_performance_chart(results, aggregated, algorithms)
        
        # 2. Precision & Recall Trends Chart
        self._generate_precision_recall_chart(results, aggregated, algorithms)
        
        # 3. F1-Score Trends Chart
        self._generate_f1_score_chart(results, aggregated, algorithms)
        
        # Also generate separate chart files using the visualization module
        try:
            visualizer = SearchVisualization("results/gui_charts")
            _ = visualizer.generate_all_charts(results)
            print("📊 GUI charts also saved to: results/gui_charts")
        except (ImportError, AttributeError, ValueError) as e:
            print(f"⚠️  Could not save separate chart files: {e}")

    def _generate_performance_chart(self, _results, aggregated, algorithms):
        """Generate performance comparison chart."""
        fig = self.chart_figures['performance_comparison']
        fig.clear()
        
        ax = fig.add_subplot(111)
        metrics = ['map', 'mrr', 'f1@5', 'ndcg@10']
        x = np.arange(len(metrics))
        width = 0.35
        
        algo1_metrics = [
            aggregated['algorithms'][algorithms[0]]['metrics'].get(m, 0) 
            for m in metrics
        ]
        algo2_metrics = [
            aggregated['algorithms'][algorithms[1]]['metrics'].get(m, 0) 
            for m in metrics
        ] if len(algorithms) > 1 else []
        
        bars1 = ax.bar(x - width/2, algo1_metrics, width, 
                      label=algorithms[0], alpha=0.8, color='skyblue')
        bars_list = [bars1]
        
        if algo2_metrics:
            bars2 = ax.bar(x + width/2, algo2_metrics, width, 
                          label=algorithms[1], alpha=0.8, color='lightcoral')
            bars_list.append(bars2)
        
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Algorithm Performance Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['MAP', 'MRR', 'F1@5', 'NDCG@10'])
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.0)
        
        # Add value labels on bars
        for bars in bars_list:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{height:.3f}', ha='center', va='bottom', fontsize=9)
        
        fig.tight_layout()
        self.chart_canvases['performance_comparison'].draw()

    def _generate_precision_recall_chart(self, _results, aggregated, algorithms):
        """Generate precision & recall trends chart."""
        fig = self.chart_figures['precision_recall_trends']
        fig.clear()
        
        ax = fig.add_subplot(111)
        k_values = [1, 3, 5, 10]
        colors = ['blue', 'red']
        
        for i, algo_name in enumerate(algorithms):
            algo_data = aggregated['algorithms'][algo_name]
            algo_metrics = algo_data['metrics']
            
            precisions = []
            recalls = []
            
            for k in k_values:
                precisions.append(algo_metrics.get(f'precision@{k}', 0))
                recalls.append(algo_metrics.get(f'recall@{k}', 0))
            
            ax.plot(k_values, precisions, marker='o', linewidth=2,
                   label=f'{algo_name} Precision', color=colors[i])
            ax.plot(k_values, recalls, marker='s', linestyle='--', linewidth=2,
                   label=f'{algo_name} Recall', color=colors[i], alpha=0.7)
        
        ax.set_xlabel('K Values', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Precision & Recall vs K Values', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)
        
        # Set y-axis limits
        max_precision = max(aggregated['algorithms'][algo]['metrics'].get('precision@10', 0) 
                           for algo in algorithms)
        max_recall = max(aggregated['algorithms'][algo]['metrics'].get('recall@10', 0) 
                        for algo in algorithms)
        max_value = max(max_precision, max_recall)
        ax.set_ylim(0, max_value * 1.1 if max_value > 0 else 0.1)
        
        fig.tight_layout()
        self.chart_canvases['precision_recall_trends'].draw()


    def _generate_f1_score_chart(self, _results, aggregated, algorithms):
        """Generate F1-score trends chart."""
        fig = self.chart_figures['f1_score_trends']
        fig.clear()
        
        ax = fig.add_subplot(111)
        k_values = [1, 3, 5, 10]
        colors = ['blue', 'red', 'green', 'orange']
        
        for i, algo_name in enumerate(algorithms):
            algo_data = aggregated['algorithms'][algo_name]
            algo_metrics = algo_data['metrics']
            
            f1_scores = []
            for k in k_values:
                f1_scores.append(algo_metrics.get(f'f1@{k}', 0))
            
            ax.plot(k_values, f1_scores, marker='o', linewidth=3, markersize=8,
                   label=algo_name, color=colors[i])
        
        ax.set_xlabel('K Values', fontsize=12)
        ax.set_ylabel('F1-Score', fontsize=12)
        ax.set_title('F1-Score vs K Values', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Set y-axis limits
        max_f1 = max(aggregated['algorithms'][algo]['metrics'].get('f1@10', 0) 
                    for algo in algorithms)
        ax.set_ylim(0, max_f1 * 1.1 if max_f1 > 0 else 0.1)
        
        fig.tight_layout()
        self.chart_canvases['f1_score_trends'].draw()

    def generate_data_visualizations(self):
        """Generate visualizations for the dataset."""
        if not self.products:
            messagebox.showwarning("Warning", "No data loaded. Please load data first.")
            return
        
        # Clear previous plots
        self.data_figure.clear()
        
        # Convert to DataFrame for easier analysis
        df_data = []
        for product in self.products:
            df_data.append({
                'category': product.get('category', 'Unknown'),
                'price': float(product.get('price', {}).get('value', 0)),
                'condition': product.get('condition', 'Unknown'),
                'brand': product.get('brand', 'Unknown')
            })
        
        df = pd.DataFrame(df_data)
        
        # Create subplots
        fig = self.data_figure
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # 1. Category Distribution
        ax1 = fig.add_subplot(gs[0, 0])
        category_counts = df['category'].value_counts().head(10)
        category_counts.plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_title('Top 10 Product Categories')
        ax1.set_xlabel('Category')
        ax1.set_ylabel('Count')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Price Distribution
        ax2 = fig.add_subplot(gs[0, 1])
        df['price'].hist(bins=30, ax=ax2, color='lightgreen', alpha=0.7)
        ax2.set_title('Price Distribution')
        ax2.set_xlabel('Price ($)')
        ax2.set_ylabel('Frequency')
        
        # 3. Condition Distribution
        ax3 = fig.add_subplot(gs[1, 0])
        condition_counts = df['condition'].value_counts()
        condition_counts.plot(kind='pie', ax=ax3, autopct='%1.1f%%')
        ax3.set_title('Product Condition Distribution')
        ax3.set_ylabel('')
        
        # 4. Brand Distribution
        ax4 = fig.add_subplot(gs[1, 1])
        brand_counts = df['brand'].value_counts().head(8)
        brand_counts.plot(kind='barh', ax=ax4, color='lightcoral')
        ax4.set_title('Top 8 Brands')
        ax4.set_xlabel('Count')
        
        # Refresh the canvas
        self.data_canvas.draw()


def main():
    """Main entry point for the GUI application."""
    if not TKINTER_AVAILABLE:
        print("❌ Cannot start GUI: tkinter is not available.")
        print("   Please install tkinter to use the GUI interface.")
        print("   Use CLI mode instead: python prototype/cli.py")
        return
    
    root = tk.Tk()
    SearchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
