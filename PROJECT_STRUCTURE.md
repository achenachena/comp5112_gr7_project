# Project Structure

## 📁 Directory Organization

```
comp5112_gr7_project/
├── 📊 data/                          # Data storage
│   ├── ecommerce_research.db         # Main SQLite database
│   ├── ecommerce_research.db-shm     # SQLite shared memory
│   ├── ecommerce_research.db-wal     # SQLite write-ahead log
│   ├── checkpoints/                  # Scraping checkpoints
│   │   └── twitter_checkpoint.json
│   ├── exports/                      # Data exports
│   └── results/                      # Analysis results
│
├── 📚 docs/                          # Documentation
│   ├── PROJECT_SUMMARY.md
│   ├── REAL_SOCIAL_MEDIA_SETUP.md
│   ├── RESEARCH_METHODOLOGY.md
│   ├── SETUP_GUIDE.md
│   ├── SOCIAL_MEDIA_SCRAPER_GUIDE.md
│   ├── USAGE_GUIDE.md
│   └── WEB_GUI_GUIDE.md
│
├── 🔧 scripts/                       # Scripts organized by purpose
│   ├── data_collection/              # Data collection scripts
│   │   ├── real_social_media_scraper.py
│   │   ├── collect_real_ecommerce.py
│   ├── analysis/                     # Analysis and comparison scripts
│   │   ├── extract_product_info.py
│   │   ├── compare_datasets.py
│   │   ├── run_database_search.py
│   │   └── README_extraction.md
│   ├── testing/                      # Testing and evaluation scripts
│   │   ├── final_ndcg_test.py
│   │   ├── test_ndcg_fix.py
│   │   ├── simple_algorithm_comparison.py
│   │   └── fixed_algorithm_comparison.py
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
│   │   │   ├── script.js
│   │   │   └── style.css
│   │   └── templates/
│   │       └── index.html
│   ├── cli.py
│   ├── config.py
│   └── logging_config.py
│
├── 🧪 tests/                         # Test files
│   ├── unit/
│   │   └── test_algorithms.py
│   └── __init__.py
│
├── 📄 Configuration Files
│   ├── README.md
│   ├── requirements.txt
│   ├── env.template
│   └── PROJECT_STRUCTURE.md
```

## 🎯 Script Categories

### 📊 Data Collection (`scripts/data_collection/`)
- **Purpose**: Collect data from various sources
- **Scripts**:
  - `real_social_media_scraper.py` - Scrape Reddit/Twitter data
  - `collect_real_ecommerce.py` - Collect e-commerce API data

### 🔍 Analysis (`scripts/analysis/`)
- **Purpose**: Analyze and compare data
- **Scripts**:
  - `extract_product_info.py` - Extract product information from social media
  - `compare_datasets.py` - Compare different datasets
  - `run_database_search.py` - Run search algorithms on database
  - `README_extraction.md` - Documentation for extraction

### 🧪 Testing (`scripts/testing/`)
- **Purpose**: Test and evaluate algorithms
- **Scripts**:
  - `final_ndcg_test.py` - Test NDCG calculation
  - `test_ndcg_fix.py` - Test NDCG fixes
  - `simple_algorithm_comparison.py` - Simple algorithm comparison
  - `fixed_algorithm_comparison.py` - Fixed algorithm comparison

### 🛠️ Utilities (`scripts/utilities/`)
- **Purpose**: Utility and setup scripts
- **Scripts**:
  - `init_database.py` - Initialize database
  - `generate_dataset.py` - Generate mock datasets

## 🚀 Quick Start

1. **Setup**: `python scripts/utilities/init_database.py`
2. **Collect Data**: `python scripts/data_collection/real_social_media_scraper.py`
3. **Extract Info**: `python scripts/analysis/extract_product_info.py`
4. **Run Web Interface**: `python -m src.ecommerce_search.web.app`

## 📝 Notes

- All scripts are organized by their primary purpose
- Database files are kept in `data/` with proper subdirectories
- Documentation is centralized in `docs/`
- Core application code is in `src/ecommerce_search/`
- Test files are in `tests/` following Python conventions
