# Complete Setup and Usage Guide

## First-Time Setup

### Prerequisites

- Python 3.8+
- Git

### Step 1: Clone and Install

```bash
git clone <repository-url>
cd comp5112_gr7_project
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Initialize Database

```bash
python scripts/utilities/database_initializer.py
```

This creates an empty database with the correct schema.

### Step 3: Configure Environment (Optional)

Only needed if collecting real data:

```bash
cp env.template .env
# Edit .env with your API keys
```

### Step 4: Choose Data Source

- **Quick Start**: Generate synthetic data (no API keys needed)
- **Real Data**: Follow API setup instructions below

### Step 5: Customize Subreddit Configuration (Optional)

The scraper uses a configuration file for subreddits. You can customize it:

```bash
# Copy the template and edit as needed
cp config/subreddits.json.template config/subreddits.json
# Edit config/subreddits.json to add/remove subreddits
```

The configuration file allows you to:

- Add or remove subreddits
- Organize by categories
- Include metadata (subscriber count, description)

## Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd comp5112_gr7_project
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Initialize database
python scripts/utilities/database_initializer.py

# Collect real data (optional)
python scripts/data_collection/ecommerce_api_collector.py
python scripts/data_collection/social_media_scraper.py
```

### 3. Run the Application

```bash
# Web interface (recommended)
python -c "
import sys
import os
sys.path.append(os.getcwd())
from src.ecommerce_search.web.app import create_app
app = create_app()
app.run(host='0.0.0.0', port=5000, debug=False)
"

# Command line interface
python src/ecommerce_search/cli.py --help
```

## Command Line Interface

### Search Commands

```bash
# Search for products
python src/ecommerce_search/cli.py search "blue t-shirt"

# Search with specific algorithm
python src/ecommerce_search/cli.py search "blue t-shirt" --algorithm keyword

# Search with limit
python src/ecommerce_search/cli.py search "blue t-shirt" --limit 5
```

### Comparison Commands

```bash
# Compare all algorithms
python src/ecommerce_search/cli.py compare

# Compare with custom queries
python src/ecommerce_search/cli.py compare --queries "shoes" "clothing" "electronics"
```

### Database Commands

```bash
# Show database information
python src/ecommerce_search/cli.py db info

# Show database statistics
python src/ecommerce_search/cli.py db stats
```

## Web Interface

### Starting the Web Application

```bash
python src/ecommerce_search/web/app.py
```

Then open <http://localhost:5000> in your browser.

### Features

- **Data Management**: Load products from database
- **Algorithm Comparison**: Run side-by-side algorithm comparisons
- **Interactive Search**: Test search queries in real-time
- **Performance Metrics**: View detailed evaluation results

## Python API

### Basic Usage

```python
from ecommerce_search import KeywordSearch, TFIDFSearch

# Initialize algorithms
keyword_search = KeywordSearch()
tfidf_search = TFIDFSearch()

# Search products
results = keyword_search.search("blue t-shirt", products, limit=10)
```

### Advanced Usage

```python
from ecommerce_search.database import get_db_manager
from ecommerce_search.evaluation import SearchMetrics

# Load products from database
db_manager = get_db_manager()
with db_manager.get_session() as session:
    products = session.query(Product).all()

# Run evaluation
metrics = SearchMetrics()
results = metrics.evaluate_algorithms([keyword_search, tfidf_search], products)
```

## Data Collection

### Real Data Collection

```bash
# Collect from Shopify stores (no API key needed)
python scripts/data_collection/ecommerce_api_collector.py

# Collect social media data (requires API keys)
python scripts/data_collection/social_media_scraper.py
```

### Real API Data

```bash
# Shopify Stores API (no API key required - public endpoints)
python scripts/data_collection/ecommerce_api_collector.py

# Social Media Data (requires API keys)
python scripts/data_collection/social_media_scraper.py
```

### Optional API Data (Not Currently Used)

```bash
python scripts/data_collection/collect_real_ecommerce.py

# Walmart API (requires API key) - Available but not used in current dataset
# Note: walmart_api_collection.py has been removed as it's not used
```

### API Key Setup

1. Get API keys from:

   - Reddit: <https://www.reddit.com/prefs/apps>
   - Twitter: <https://developer.twitter.com/>

2. Add to `.env` file:

```bash
REDDIT_CLIENT_ID_1=your_key_here
REDDIT_CLIENT_SECRET_1=your_secret_here
TWITTER_BEARER_TOKEN=your_token_here
```

## Configuration

### Environment Variables

Create a `.env` file with your configuration:

```bash
# Database
DATABASE_URL=sqlite:///data/ecommerce_research.db

# Web Application
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Logging
LOG_LEVEL=INFO
```

### Algorithm Configuration

```python
# Keyword Matching
keyword_search = KeywordSearch(
    case_sensitive=False,
    exact_match_weight=25.0
)

# TF-IDF
tfidf_search = TFIDFSearch(
    min_df=2,
    max_df=0.6,
    case_sensitive=False
)
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated
2. **Database not found**: Run `python scripts/utilities/database_initializer.py`
3. **No data**: Run the data collection scripts to gather real data
4. **Port already in use**: Change port in web app configuration

### Getting Help

- Check logs in `logs/` directory
- Run tests: `pytest tests/`
- Check code quality: `flake8 src/ tests/`

## Data Not Included in Repository

The following files are excluded from Git for size and privacy reasons:

- `data/ecommerce_research.db` - Main database (can be large)
- `data/checkpoints/*.json` - Scraping progress checkpoints
- `data/exports/*` - Exported data files
- `data/results/*` - Analysis results

To recreate the dataset:

1. Run database initialization (see above)
2. Either generate sample data OR collect real data with API keys
3. The database will be created locally in `data/` directory
