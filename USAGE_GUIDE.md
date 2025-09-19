# Usage Guide: Search Algorithm Comparison Tool

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd comp5112_gr7_project

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

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

### 3. Using Custom Data

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

#### Using Individual Algorithms

```python
from algorithms.keyword_matching import KeywordSearch
from algorithms.tfidf_search import TFIDFSearch

# Initialize algorithms
keyword_search = KeywordSearch()
tfidf_search = TFIDFSearch()

# Load your product data
products = [...]  # Your product data

# Search with keyword matching
results = keyword_search.search("iPhone case", products, limit=10)

# Search with TF-IDF
results = tfidf_search.search("iPhone case", products, limit=10)
```

#### Running Comparisons

```python
from evaluation.comparison import SearchComparison
from evaluation.metrics import RelevanceJudgment

# Create relevance judgments
relevance_judge = RelevanceJudgment()
relevance_judge.create_synthetic_judgments(queries, products)

# Initialize comparison
algorithms = {
    'keyword_matching': KeywordSearch(),
    'tfidf': TFIDFSearch()
}
comparison = SearchComparison(algorithms, relevance_judge)

# Run comparison
results = comparison.compare_multiple_queries(queries, products)

# Print results
comparison.print_comparison_report()
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

### Integration with eBay API

```python
from data_collection.ebay_client import EbayAPIClient

# Set up eBay API credentials in .env file
client = EbayAPIClient()

# Collect real product data
results = client.search_and_format("iPhone case", limit=100)

# Use collected data for algorithm comparison
products = results['products']
```

This guide provides comprehensive instructions for using the search algorithm comparison tool. For additional help or questions, refer to the source code documentation or create an issue in the repository.
