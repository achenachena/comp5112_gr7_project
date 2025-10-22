# E-commerce Search Algorithm Comparison Project

A comprehensive framework for comparing search algorithms (Keyword Matching vs TF-IDF) using real e-commerce and social media data.

## Quick Start

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
python scripts/utilities/database_initializer.py
```

### 2. Collect Real Data
```bash
# Collect from Shopify stores (no API key needed)
python scripts/data_collection/ecommerce_api_collector.py

# Collect social media data (requires API keys)
python scripts/data_collection/social_media_scraper.py
```

### 3. Environment Configuration
Copy the template and add your credentials:

```bash
cp env.template .env
# Edit .env with your API keys
```

**Important**: Never commit the `.env` file or `data/*.db` files to the repository.

### 4. Run the Application

#### Option A: Quick Start (Recommended)
```bash
# Use the startup script
./scripts/web/start_web.sh
```

#### Option B: Manual Start
```bash
# Development mode
python scripts/web/run_web.py

# Or using Flask CLI
export FLASK_APP=scripts/web/run_web.py
export FLASK_ENV=development
flask run --host=127.0.0.1 --port=5000
```

#### Option C: Production Mode
```bash
# Using Gunicorn (install: pip install gunicorn)
gunicorn -w 4 -b 127.0.0.1:5000 scripts.web.wsgi:application

# Using Waitress (install: pip install waitress)
waitress-serve --host=127.0.0.1 --port=5000 scripts.web.wsgi:application
```

**Then open http://127.0.0.1:5000 in your browser**

## 📁 Project Structure

```
comp5112_gr7_project/
├── data/                          # Data storage
│   └── ecommerce_research.db         # Main SQLite database
│
├── scripts/                       # Scripts organized by purpose
│   ├── data_collection/              # Data collection scripts
│   │   ├── social_media_scraper.py
│   │   └── ecommerce_api_collector.py
│   ├── utilities/                    # Utility scripts
│   │   └── database_initializer.py
│   └── web/                          # Web application scripts
│       ├── run_web.py                # Development server entry point
│       ├── wsgi.py                   # Production WSGI entry point
│       ├── start_web.sh              # Automated startup script
│       └── start_web_simple.sh       # Simple startup script
│
├── src/ecommerce_search/          # Core application code
│   ├── algorithms/                   # Search algorithms
│   │   ├── keyword_matching.py
│   │   └── tfidf_search.py
│   ├── database/                     # Database management
│   │   ├── db_manager.py
│   │   └── models.py
│   ├── evaluation/                   # Evaluation metrics
│   │   ├── comparison.py
│   │   ├── metrics.py
│   │   └── algorithm_comparison.py
│   ├── utils/                        # Utilities
│   │   ├── product_extractor.py
│   │   ├── base_scraper.py
│   │   └── database_operations.py
│   ├── web/                          # Web interface
│   │   ├── app.py
│   │   ├── routes.py
│   │   ├── static/
│   │   └── templates/
│   └── cli.py
│
└── 📚 docs/                          # Documentation
    ├── PROJECT_SUMMARY.md
    ├── USAGE_GUIDE.md
    ├── PRESENTATION_OUTLINE.md
    └── RESEARCH_METHODOLOGY.md
```

## Key Features

### Search Algorithms
- **Keyword Matching**: Exact and partial keyword matching with configurable weights
- **TF-IDF**: Term Frequency-Inverse Document Frequency with vector similarity

### Evaluation Metrics
- Precision@K, Recall@K, F1@K
- NDCG@K (Normalized Discounted Cumulative Gain)
- MAP (Mean Average Precision)
- MRR (Mean Reciprocal Rank)

### Data Sources
- **Real API Data**: 200+ Shopify stores (43,226 products)
- **Social Media Data**: Reddit posts (9,000+ posts) with product discussions
- **Database Storage**: SQLite database for scalable data management

### User Interfaces
- **Web Application**: Modern browser-based interface
- **Command Line**: Programmatic access and automation
- **Python API**: Library for integration with other projects

## Data Collection

### Real API Data
```bash
python scripts/data_collection/collect_real_ecommerce.py

```

### Social Media Data
```bash
# Reddit and Twitter (requires API keys)
python scripts/data_collection/real_social_media_scraper.py
```

## Analysis and Testing

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
- **[Research Methodology](docs/RESEARCH_METHODOLOGY.md)** - Academic research approach
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Comprehensive project overview
- **[Presentation Outline](docs/PRESENTATION_OUTLINE.md)** - PowerPoint presentation structure

## Configuration

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
- **Reddit**: https://www.reddit.com/prefs/apps
- **Twitter**: https://developer.twitter.com/

## 🧪 Testing

```bash
# Check code quality
flake8 src/
```

## Troubleshooting

### Common Issues

1. **Database not found**: Run `python scripts/utilities/database_initializer.py`
2. **No data**: Run the data collection scripts to gather real data
3. **Import errors**: Ensure virtual environment is activated
4. **Port already in use**: Change port in web app configuration

### Getting Help

- Check the logs in `logs/` directory
- Check code quality: `flake8 src/`

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