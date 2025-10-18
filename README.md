# Comparative Study of Search Algorithms in E-commerce

A comprehensive research project comparing **Keyword Matching** vs **TF-IDF** search algorithms using **real e-commerce data** from multiple APIs, stored in a **SQL database** for large-scale evaluation.

## 🎯 Research Objectives

- **Compare effectiveness** of keyword matching vs TF-IDF algorithms on real e-commerce data
- **Collect real product data** from multiple APIs (Best Buy, Target, Shopify, etc.)
- **Store data in SQL database** for handling hundreds of thousands of products
- **Evaluate comprehensive metrics**: Precision, Recall, F1-Score, MAP, MRR, NDCG
- **Analyze performance differences** across different product categories and query types
- **Provide insights** for improving search algorithms in real-world scenarios

## 🚀 Features

- **🗄️ Database Architecture**: SQL database for scalable data storage
- **🛒 Real API Integration**: Best Buy, Target, Shopify, Newegg APIs
- **🔍 Search Algorithms**: Keyword Matching vs TF-IDF comparison
- **📊 Comprehensive Metrics**: Precision@K, Recall@K, F1@K, MAP, MRR, NDCG
- **⚡ Performance Tracking**: Search times, result counts, algorithm efficiency
- **🔒 Security First**: No sensitive data in repository, environment-based configuration
- **📈 Scalable Evaluation**: Handle hundreds of thousands of products
- **🎛️ Interactive Tools**: CLI and GUI interfaces for testing

## 📁 Project Structure

```
├── database/                # SQL database models and management
│   ├── models.py           # SQLAlchemy database models
│   ├── db_manager.py       # Database connection and utilities
│   └── __init__.py
├── algorithms/              # Search algorithm implementations
│   ├── keyword_matching.py # Keyword-based search algorithm
│   └── tfidf_search.py     # TF-IDF search algorithm
├── evaluation/              # Performance evaluation tools
│   ├── metrics.py          # Evaluation metrics (Precision, Recall, F1, etc.)
│   └── comparison.py       # Algorithm comparison framework
├── data_collection/         # API data collection (legacy directory)
├── prototype/               # Interactive testing interfaces
│   ├── gui.py              # Graphical user interface
│   └── cli.py              # Command-line interface
├── utils/                   # Utility functions
│   └── preprocessing.py    # Data preprocessing tools
├── data/                    # Database and collected data
│   └── ecommerce_research.db # SQLite database
├── results/                 # Analysis results and reports
├── collect_to_database.py   # Real API data collection script
├── run_database_search.py   # Database-based search evaluation
├── init_database.py         # Database initialization script
└── requirements.txt         # Python dependencies
```

## 🔒 Security & Privacy

This repository is **security-first** and **publication-ready**:

- ✅ **No sensitive data** in repository
- ✅ **No API keys** or secrets in code
- ✅ **No database files** or generated data
- ✅ **Environment-based configuration** only
- ✅ **Comprehensive .gitignore** protection
- ✅ **Mock data only** for examples
- ✅ **See [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md)** for details

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set Up Environment Variables**
```bash
# Creates .env file from template
python setup_environment.py

# Edit .env file with your API keys:
# BESTBUY_API_KEY=your_key_here
# TARGET_API_KEY=your_key_here
# NEWEGG_API_KEY=your_key_here
```

### **3. Initialize Database**
```bash
python init_database.py
```

### **4. Collect Real Data**
```bash
python collect_to_database.py

# Option B: Use Shopify stores (no API key needed)
python collect_to_database.py
```

### **4. Run Search Evaluation**
```bash
python run_database_search.py
```

### **5. Use Interactive Tools**
```bash
# Command-line interface
python prototype/cli.py

# Graphical interface
python web_gui.py
```

## 💻 Usage Examples

### **Database-Based Search**
```python
from database.db_manager import get_db_manager
from algorithms.keyword_matching import KeywordSearch
from algorithms.tfidf_search import TFIDFSearch

# Initialize database and algorithms
db = get_db_manager()
keyword_search = KeywordSearch()
tfidf_search = TFIDFSearch()

# Load products from database
with db.get_session() as session:
    products = session.query(Product).limit(1000).all()

# Run search algorithms
keyword_results = keyword_search.search("iPhone case", products)
tfidf_results = tfidf_search.search("iPhone case", products)

# Compare results
print(f"Keyword Matching: {len(keyword_results)} results")
print(f"TF-IDF: {len(tfidf_results)} results")
```

### **Real API Data Collection**
```python
from collect_to_database import DatabaseEcommerceCollector

# Initialize collector
collector = DatabaseEcommerceCollector()

# Collect from Best Buy API
search_queries = ["iPhone", "Samsung Galaxy", "laptop"]
products_collected = collector.collect_from_bestbuy_api(search_queries)

print(f"Collected {products_collected} products")
```

### **Performance Evaluation**
```python
from run_database_search import DatabaseSearchEvaluator

# Run comprehensive evaluation
evaluator = DatabaseSearchEvaluator()
evaluator.run_full_evaluation(product_limit=10000)

# Generate comparison report
report = evaluator.generate_comparison_report()
```

## 📚 Documentation

- **[DATABASE_SETUP_GUIDE.md](DATABASE_SETUP_GUIDE.md)** - Complete database setup and configuration
- **[REAL_ECOMMERCE_SETUP.md](REAL_ECOMMERCE_SETUP.md)** - Real e-commerce API integration guide
- **[RESEARCH_METHODOLOGY.md](RESEARCH_METHODOLOGY.md)** - Research methodology and approach
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Detailed usage instructions
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview and achievements

## 🗂️ Key Components

- **`database/`** - SQL database models and management
- **`algorithms/`** - Search algorithm implementations (Keyword Matching, TF-IDF)
- **`evaluation/`** - Performance metrics and comparison tools
- **`prototype/`** - Interactive CLI and GUI interfaces
- **`collect_to_database.py`** - Real API data collection script
- **`run_database_search.py`** - Database-based search evaluation
- **`init_database.py`** - Database initialization script

## 🎓 Academic Context

This repository is created for students in the **MSc Program in Computer Science** at **Lakehead University** for **COMP5112 Group 7's project**.

### **Research Scope:**
- **Large-scale evaluation** with hundreds of thousands of products
- **Real e-commerce data** from multiple API sources
- **Comprehensive performance analysis** using industry-standard metrics
- **Scalable architecture** for academic research and practical applications

---

**Ready for large-scale e-commerce search algorithm research!** 🚀
