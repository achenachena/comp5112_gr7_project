# Usage Guide: Database-Based E-commerce Search Algorithm Research

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd comp5112_gr7_project

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Initialize SQL database
python init_database.py
```

### 3. Collect Real Data

```bash
# Option A: Best Buy API (recommended)
# Get free API key: https://developer.bestbuy.com/
# Add to .env: BESTBUY_API_KEY=your_key_here
python collect_to_database.py

# Option B: Shopify stores (no API key needed)
python collect_to_database.py
```

### 4. Run Search Evaluation

```bash
# Run comprehensive evaluation on database
python run_database_search.py
```

### 5. Interactive Tools

#### Command Line Interface (CLI)

```bash
# Run demo with sample data
python prototype/cli.py --mode demo

# Interactive search mode
python prototype/cli.py --mode interactive

# Run comparison only
python prototype/cli.py --mode compare

# Load custom data
python prototype/cli.py --data data/my_products.json
```

#### Graphical User Interface (GUI)

```bash
# Launch GUI application
python prototype/gui.py
```

## 📊 Database Usage

### Database Schema

The system uses **5 main tables** for comprehensive data storage:

- **`products`** - Store e-commerce product data
- **`search_queries`** - Store test queries for evaluation  
- **`search_results`** - Store algorithm search results
- **`evaluation_metrics`** - Store performance metrics
- **`data_collection_logs`** - Track data collection activities

### Database Operations

```python
from database.db_manager import get_db_manager
from database.models import Product, SearchQuery, SearchResult

# Get database manager
db = get_db_manager()

# Query products
with db.get_session() as session:
    products = session.query(Product).limit(1000).all()
    
# Get database statistics
stats = db.get_database_info()
print(f"Total products: {stats['stats']['products']}")
```

### Using Custom Data

#### Prepare Your Data

Your product data should be in JSON format with the following structure:

```json
[
  {
    "id": "unique_id",
    "title": "Product Title",
    "description": "Product description",
    "category": "Product Category",
    "price": {
      "value": "29.99",
      "currency": "USD"
    },
    "condition": "NEW",
    "url": "https://example.com/product",
    "seller": {
      "username": "seller_name"
    },
    "location": "City, State"
  }
]
```

#### Load and Test

```bash
# Load your data
python prototype/cli.py --data your_products.json --mode compare
```

## Detailed Usage

### Command Line Options

```bash
python prototype/cli.py [OPTIONS]

Options:
  --mode {demo,interactive,compare}
                        Run mode (default: demo)
  --data PATH           Path to custom data file
  --output PATH         Output directory for results (default: results/)
  --help               Show help message
```

### GUI Features

The GUI application provides four main tabs:

#### 1. Interactive Search
- Enter search queries
- Select algorithm (Keyword Matching or TF-IDF)
- View ranked results with relevance scores
- Double-click results for detailed product information

#### 2. Algorithm Comparison
- Run comprehensive comparison across multiple test queries
- View detailed performance metrics
- Export comparison results to JSON

#### 3. Data Management
- Load sample or custom data
- View data statistics and distributions
- Browse product catalog
- Export data in various formats

#### 4. Results Analysis
- Generate comprehensive analysis reports
- View performance metrics and insights
- Export analysis results

### Programmatic Usage

#### Database-Based Search

```python
from database.db_manager import get_db_manager
from database.models import Product
from algorithms.keyword_matching import KeywordSearch
from algorithms.tfidf_search import TFIDFSearch

# Initialize database and algorithms
db = get_db_manager()
keyword_search = KeywordSearch()
tfidf_search = TFIDFSearch()

# Load products from database
with db.get_session() as session:
    products = session.query(Product).limit(1000).all()
    # Convert to format expected by algorithms
    product_dicts = [{
        'id': p.external_id,
        'title': p.title,
        'description': p.description or '',
        'category': p.category,
        'price': {'value': str(p.price_value), 'currency': p.price_currency},
        'brand': p.brand or '',
        'model': p.model or '',
        'condition': p.condition,
        'seller': {'username': p.seller_name or ''},
        'location': p.seller_location or '',
        'url': p.product_url or '',
        'image_url': p.image_url or '',
    } for p in products]

# Search with keyword matching
keyword_results = keyword_search.search("iPhone case", product_dicts, limit=10)

# Search with TF-IDF
tfidf_results = tfidf_search.search("iPhone case", product_dicts, limit=10)
```

#### Database-Based Evaluation

```python
from run_database_search import DatabaseSearchEvaluator

# Initialize evaluator
evaluator = DatabaseSearchEvaluator()

# Run full evaluation on database
evaluator.run_full_evaluation(product_limit=10000)

# Generate comparison report
report = evaluator.generate_comparison_report()
```

#### Real API Data Collection

```python
from collect_to_database import DatabaseEcommerceCollector

# Initialize collector
collector = DatabaseEcommerceCollector()

# Collect from Best Buy API
search_queries = ["iPhone", "Samsung Galaxy", "laptop", "gaming mouse"]
products_collected = collector.collect_from_bestbuy_api(search_queries)

print(f"Collected {products_collected} products from Best Buy")

# Collect from Shopify stores
shopify_collected = collector.collect_from_shopify_stores(search_queries[:2])
print(f"Collected {shopify_collected} products from Shopify stores")
```

#### Data Preprocessing

```python
from utils.preprocessing import ProductDataPreprocessor, DataLoader

# Load raw data
products = DataLoader.load_from_json('raw_data.json')

# Clean and preprocess
preprocessor = ProductDataPreprocessor()
cleaned_products = preprocessor.clean_product_data(products)

# Export cleaned data
preprocessor.export_cleaned_data('cleaned_data.json')
```

## Configuration

### Algorithm Parameters

#### Keyword Matching
```python
keyword_search = KeywordSearch(
    case_sensitive=False,      # Case sensitivity
    exact_match_weight=2.0     # Weight for exact matches
)
```

#### TF-IDF
```python
tfidf_search = TFIDFSearch(
    min_df=1,                  # Minimum document frequency
    max_df=0.95,              # Maximum document frequency
    case_sensitive=False       # Case sensitivity
)
```

### Evaluation Settings

```python
# Custom K values for evaluation
k_values = [1, 3, 5, 10, 20]

# Custom relevance threshold
relevance_threshold = 0.5
```

## Output and Results

### Comparison Results Format

```json
{
  "queries": [...],
  "aggregated": {
    "algorithms": {
      "keyword_matching": {
        "metrics": {
          "map": 0.75,
          "mrr": 0.85,
          "precision@5": 0.80,
          "recall@5": 0.70,
          "f1@5": 0.75,
          "ndcg@5": 0.78
        },
        "avg_search_time": 0.05
      },
      "tfidf": {
        "metrics": {...},
        "avg_search_time": 0.08
      }
    }
  },
  "summary": {
    "best_algorithms": {...},
    "performance_ranking": [...],
    "key_insights": [...]
  }
}
```

### Understanding Metrics

- **MAP (Mean Average Precision)**: Overall relevance across all queries
- **MRR (Mean Reciprocal Rank)**: How quickly relevant results appear
- **Precision@K**: Accuracy of top-K results
- **Recall@K**: Coverage of relevant items in top-K
- **F1@K**: Balance between precision and recall
- **NDCG@K**: Ranking quality considering position

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Make sure you're in the project directory
cd /path/to/comp5112_gr7_project

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Missing Dependencies
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### Data Format Issues
- Ensure your JSON data is properly formatted
- Check that required fields (id, title) are present
- Validate numeric fields (price values)

#### Performance Issues
- Reduce dataset size for testing
- Use smaller K values for evaluation
- Consider using sample data for initial testing

### Getting Help

1. **Check the logs**: Look for error messages in the console output
2. **Verify data format**: Ensure your data matches the expected structure
3. **Test with sample data**: Use the built-in sample data to verify functionality
4. **Check algorithm parameters**: Adjust parameters if results are unexpected

## Advanced Usage

### Custom Evaluation Metrics

```python
from evaluation.metrics import SearchMetrics

# Calculate custom metrics
metrics = SearchMetrics.calculate_comprehensive_metrics(
    relevant_items, retrieved_items,
    k_values=[1, 5, 10, 20],
    relevance_scores=custom_scores
)
```

### Batch Processing

```python
# Process multiple datasets
datasets = ['dataset1.json', 'dataset2.json', 'dataset3.json']

for dataset in datasets:
    products = DataLoader.load_from_json(dataset)
    # Run comparison and save results
    comparison.export_results(f'results/{dataset}_comparison.json')
```

### Database Query Operations

```python
from database.db_manager import get_db_manager
from database.models import Product

# Get database manager
db = get_db_manager()

# Query products by category
with db.get_session() as session:
    electronics = session.query(Product).filter_by(category='Electronics').limit(100).all()
    
# Query products by price range
with db.get_session() as session:
    affordable_products = session.query(Product).filter(
        Product.price_value < 50.0
    ).all()
    
# Get database statistics
stats = db.get_database_info()
print(f"Total products: {stats['stats']['products']}")
print(f"Data sources: {stats['stats']['unique_sources']}")
```

This guide provides comprehensive instructions for using the database-based search algorithm comparison tool. For additional help or questions, refer to the documentation in `DATABASE_SETUP_GUIDE.md` or `REAL_ECOMMERCE_SETUP.md`.
