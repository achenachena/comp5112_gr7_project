# E-commerce Search Algorithm Comparison Project

A comprehensive framework for comparing search algorithms (Keyword Matching vs
TF-IDF) using real e-commerce and social media data.

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

### 4. Run the Web Application

#### Option A: Direct Flask App (Recommended)

```bash
# Start the web application directly
python src/ecommerce_search/web/app.py
```

#### Option B: Using Flask CLI

```bash
# Set Flask environment variables
export FLASK_APP=src/ecommerce_search/web/app.py
export FLASK_ENV=development

# Run the application
flask run --host=127.0.0.1 --port=5000
```

#### Option C: Production Mode

```bash
# Using Gunicorn (install: pip install gunicorn)
gunicorn -w 4 -b 127.0.0.1:5000 src.ecommerce_search.web.app:app

# Using Waitress (install: pip install waitress)
waitress-serve --host=127.0.0.1 --port=5000 src.ecommerce_search.web.app:app
```

**🌐 Open <http://127.0.0.1:5000> in your browser**

## 📁 Project Structure

```text
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

- **Keyword Matching**: Exact and partial keyword matching with configurable
  weights
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

### Features Overview

The web interface provides a modern, interactive dashboard for:

#### **Data Management**

- **Load Database Data**: Import products from API and social media datasets
- **Dataset Selection**: Choose between API products or social media posts
- **Data Statistics**: View dataset size, categories, and source distribution
- **Real-time Status**: Monitor data loading progress

#### **Algorithm Comparison**

- **Side-by-Side Testing**: Compare Keyword Matching vs TF-IDF algorithms
- **Performance Metrics**: View Precision@K, Recall@K, F1@K, and NDCG@K
  results
- **Interactive Charts**: Beautiful line charts showing performance trends
  (K=1 to 10)
- **Statistical Analysis**: Comprehensive evaluation with multiple metrics

#### **Interactive Search**

- **Real-time Search**: Test search queries instantly
- **Algorithm Selection**: Choose specific algorithms to test
- **Result Comparison**: See results from different algorithms side-by-side
- **Query History**: Track and compare different search queries

#### **Performance Visualization**

- **F1-Score Trends**: Performance across different K values
- **Precision Analysis**: Accuracy of top-K results
- **Recall Metrics**: Coverage of relevant items
- **NDCG Rankings**: Quality of result rankings

### Quick Start Guide

1. **Start the Application**:

   ```bash
   python src/ecommerce_search/web/app.py
   ```

2. **Open Your Browser**: Navigate to <http://127.0.0.1:5000>

3. **Load Data**: Click "Load Database Data" to import your datasets

4. **Run Comparison**: Click "Run Comparison" to test algorithms

5. **Search Products**: Use the search box to test queries interactively

### Complete Workflow

#### **Step 1: Data Setup**

```bash
# Initialize database
python scripts/utilities/database_initializer.py

# Collect real data (optional - for fresh data)
python scripts/data_collection/ecommerce_api_collector.py
python scripts/data_collection/social_media_scraper.py
```

#### **Step 2: Start Web Interface**

```bash
# Start the web application
python src/ecommerce_search/web/app.py

# Open browser to <http://127.0.0.1:5000>
```

#### **Step 3: Load Data in Web Interface**

1. Select dataset type (API products or Social Media posts)
2. Set product limit (optional)
3. Click "Load Database Data"
4. Wait for data loading to complete

#### **Step 4: Run Algorithm Comparison**

1. Click "Run Comparison" button
2. Wait for algorithms to process
3. View performance metrics and charts
4. Analyze F1-Score, Precision, Recall, and NDCG trends

#### **Step 5: Interactive Search Testing**

1. Enter search query in the search box
2. Click "Search" to test algorithms
3. Compare results from different algorithms
4. Test various query types and formats

### Web Interface Screenshots

- **Dashboard**: Clean, modern interface with data management tools
- **Comparison Results**: Side-by-side algorithm performance with charts
- **Search Interface**: Real-time search with instant results
- **Performance Charts**: Interactive visualizations of algorithm metrics

**🌐 Access at: <http://127.0.0.1:5000>**

## 📚 Documentation

- **[Complete Setup and Usage Guide](docs/USAGE_GUIDE.md)** - Detailed setup
  and usage instructions
- **[Research Methodology](docs/RESEARCH_METHODOLOGY.md)** - Academic research
  approach
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Comprehensive project
  overview
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

- **Reddit**: <https://www.reddit.com/prefs/apps>
- **Twitter**: <https://developer.twitter.com/>

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

### Web Interface Issues

#### **Application Won't Start**

```bash
# Check if port 5000 is already in use
lsof -i :5000  # On macOS/Linux
netstat -ano | findstr :5000  # On Windows

# Use a different port
python src/ecommerce_search/web/app.py --port 5001
```

#### **No Data in Web Interface**

1. **Initialize Database**: `python scripts/utilities/database_initializer.py`
2. **Collect Data**: Run data collection scripts
3. **Load Data**: Use "Load Database Data" button in web interface

#### **Charts Not Displaying**

- **JavaScript Issues**: Check browser console for errors
- **Data Loading**: Ensure data is loaded before running comparisons
- **Browser Compatibility**: Use modern browsers (Chrome, Firefox, Safari)

#### **Search Not Working**

- **Algorithm Initialization**: Run algorithm comparison first
- **Data Availability**: Ensure products are loaded in database
- **Query Format**: Try simple queries like "phone" or "laptop"

### Getting Help

- **Check Logs**: Look for error messages in terminal output
- **Browser Console**: Check for JavaScript errors (F12 → Console)
- **Code Quality**: `flake8 src/` to check for syntax issues
- **Database Status**: Verify database exists and contains data

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
