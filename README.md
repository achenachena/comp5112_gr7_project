# E-commerce Search Algorithm Comparison Project

A comprehensive framework for comparing search algorithms (Keyword Matching vs TF-IDF) using real e-commerce and social media data.

## 🚀 Quick Start

### 1. Installation
```bash
git clone <repository-url>
cd comp5112_gr7_project
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Local Setup

### 1. Database Initialization
The database is not included in the repository. Initialize it locally:

```bash
# Create database and tables
python scripts/utilities/init_database.py
```

### 2. Generate Sample Data (Optional)
For testing without API keys:

```bash
# Generate synthetic product data
python scripts/utilities/generate_dataset.py
```

### 3. Collect Real Data (Requires API Keys)
```bash
# Collect from Shopify stores (no API key needed)
python scripts/data_collection/collect_real_ecommerce.py

# Collect social media data (requires API keys)
python scripts/data_collection/real_social_media_scraper.py
```

### 4. Environment Configuration
Copy the template and add your credentials:

```bash
cp env.template .env
# Edit .env with your API keys
```

**Important**: Never commit the `.env` file or `data/*.db` files to the repository.

### 5. Run the Application
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

# Then open http://localhost:5000 in your browser
```

## 📁 Project Structure

```
comp5112_gr7_project/
├── 📊 data/                          # Data storage
│   ├── ecommerce_research.db         # Main SQLite database
│   ├── checkpoints/                  # Scraping checkpoints
│   ├── exports/                      # Data exports
│   └── results/                      # Analysis results
│
├── 🔧 scripts/                       # Scripts organized by purpose
│   ├── data_collection/              # Data collection scripts
│   │   ├── real_social_media_scraper.py
│   │   ├── collect_real_ecommerce.py
│   ├── analysis/                     # Analysis and comparison scripts
│   │   ├── extract_product_info.py
│   │   ├── compare_datasets.py
│   │   └── run_database_search.py
│   ├── testing/                      # Testing and evaluation scripts
│   │   ├── simple_algorithm_comparison.py
│   │   └── final_ndcg_test.py
│   └── utilities/                    # Utility scripts
│       ├── init_database.py
│       └── generate_dataset.py
│
├── 🏗️ src/ecommerce_search/          # Core application code
│   ├── algorithms/                   # Search algorithms
│   │   ├── keyword_matching.py
│   │   └── tfidf_search.py
│   ├── database/                     # Database management
│   │   ├── db_manager.py
│   │   └── models.py
│   ├── evaluation/                   # Evaluation metrics
│   │   ├── comparison.py
│   │   ├── metrics.py
│   │   └── ultra_simple_comparison.py
│   ├── utils/                        # Utilities
│   │   ├── preprocessing.py
│   │   └── visualizations.py
│   ├── web/                          # Web interface
│   │   ├── app.py
│   │   ├── routes.py
│   │   ├── static/
│   │   └── templates/
│   ├── cli.py
│   ├── config.py
│   └── logging_config.py
│
├── 🧪 tests/                         # Test files
│   └── unit/
│       └── test_algorithms.py
│
└── 📚 docs/                          # Documentation
    ├── PROJECT_SUMMARY.md
    ├── USAGE_GUIDE.md
    ├── SOCIAL_MEDIA_SCRAPER_GUIDE.md
    ├── WEB_GUI_GUIDE.md
    └── RESEARCH_METHODOLOGY.md
```

## 🎯 Key Features

### Search Algorithms
- **Keyword Matching**: Exact and partial keyword matching with configurable weights
- **TF-IDF**: Term Frequency-Inverse Document Frequency with vector similarity

### Evaluation Metrics
- Precision@K, Recall@K, F1@K
- NDCG@K (Normalized Discounted Cumulative Gain)
- MAP (Mean Average Precision)
- MRR (Mean Reciprocal Rank)

### Data Sources
- **Generated Data**: Synthetic e-commerce products for testing
- **Real API Data**: 200+ Shopify stores (43,226 products)
- **Social Media Data**: Reddit posts (9,000+ posts) with product discussions
- **Database Storage**: SQLite database for scalable data management

### User Interfaces
- **Web Application**: Modern browser-based interface
- **Command Line**: Programmatic access and automation
- **Python API**: Library for integration with other projects

## 📊 Data Collection

### Generated Data
```bash
python scripts/utilities/generate_dataset.py
```

### Real API Data
```bash
# Best Buy API (requires API key)
python scripts/data_collection/collect_real_ecommerce.py

```

### Social Media Data
```bash
# Reddit and Twitter (requires API keys)
python scripts/data_collection/real_social_media_scraper.py
```

## 🔍 Analysis and Testing

### Extract Product Information
```bash
# Extract product info from social media posts
python scripts/analysis/extract_product_info.py --update --limit 1000
```

### Run Algorithm Comparison
```bash
# Compare algorithms on different datasets
python scripts/analysis/compare_datasets.py
```

### Test Algorithms
```bash
# Simple algorithm comparison
python scripts/testing/simple_algorithm_comparison.py
```

## 🌐 Web Interface

The web interface provides:
- **Data Management**: Load products from database
- **Algorithm Comparison**: Run side-by-side algorithm comparisons
- **Interactive Search**: Test search queries in real-time
- **Performance Metrics**: View detailed evaluation results

Access at: **http://localhost:5000**

## 📚 Documentation

- **[Complete Setup and Usage Guide](docs/USAGE_GUIDE.md)** - Detailed setup and usage instructions
- **[Social Media Scraper Guide](docs/SOCIAL_MEDIA_SCRAPER_GUIDE.md)** - How to collect social media data
- **[Web GUI Guide](docs/WEB_GUI_GUIDE.md)** - Using the web interface
- **[Research Methodology](docs/RESEARCH_METHODOLOGY.md)** - Academic research approach
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Comprehensive project overview

## 🛠️ Configuration

### Environment Variables
Create a `.env` file with your configuration:

```bash
# Copy the template
cp env.template .env

# Edit with your settings
nano .env
```

Key variables:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Web application secret key
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### API Keys (Optional)
For real data collection, you'll need API keys:
- **Best Buy**: https://developer.bestbuy.com/
- **Target**: https://developer.target.com/
- **Reddit**: https://www.reddit.com/prefs/apps
- **Twitter**: https://developer.twitter.com/

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Check code quality
flake8 src/ tests/
```

## 🔧 Troubleshooting

### Common Issues

1. **Database not found**: Run `python scripts/utilities/init_database.py`
2. **No data**: Run `python scripts/utilities/generate_dataset.py`
3. **Import errors**: Ensure virtual environment is activated
4. **Port already in use**: Change port in web app configuration

### Getting Help

- Check the logs in `logs/` directory
- Run tests: `pytest tests/`
- Check code quality: `flake8 src/ tests/`

## 📈 Research Applications

This system is designed for:
- **Academic Research**: Algorithm comparison studies
- **Industry Applications**: E-commerce search optimization
- **Educational Purposes**: Learning about search algorithms
- **Benchmarking**: Performance evaluation frameworks

## 🏗️ Technical Specifications

- **Python 3.8+**: Modern Python features
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM
- **scikit-learn**: Machine learning algorithms

## 📄 License

MIT License - see LICENSE file for details.

## 👥 Authors

COMP5112 Group 7 - E-commerce Search Algorithm Comparison Project