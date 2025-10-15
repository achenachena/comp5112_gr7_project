# Database Setup Guide for Large-Scale E-commerce Research

## 🎯 Perfect for Hundreds of Thousands of Products!

This guide helps you set up a SQL database for your e-commerce search algorithm research, designed to handle large-scale data collection and evaluation.

---

## 🗄️ Database Architecture

### **Database Schema**

The system uses **5 main tables** designed for scalability:

1. **`products`** - Store e-commerce product data
2. **`search_queries`** - Store test queries for evaluation  
3. **`search_results`** - Store algorithm search results
4. **`evaluation_metrics`** - Store performance metrics
5. **`data_collection_logs`** - Track data collection activities

### **Key Features**

- ✅ **Optimized for Scale** - Handles hundreds of thousands of products
- ✅ **Indexed Fields** - Fast search on title, category, price, brand
- ✅ **Relationship Tracking** - Links products to search results and metrics
- ✅ **Performance Monitoring** - Tracks search times and collection stats
- ✅ **Flexible Storage** - Supports multiple data sources (Best Buy, Target, etc.)

---

## 🚀 Quick Start

### **Step 1: Initialize Database**

```bash
# Initialize the database (creates tables)
python init_database.py
```

### **Step 2: Collect Real Data**

```bash
# Collect from Best Buy API (requires API key)
python collect_to_database.py

# Or collect from Shopify stores (no API key needed)
python collect_to_database.py
```

### **Step 3: Run Search Evaluation**

```bash
# Run algorithms on database data
python run_database_search.py
```

---

## 📊 Database Tables

### **Products Table**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE,  -- bestbuy_123, shopify_456
    source VARCHAR(50),               -- bestbuy_api, shopify_api
    title TEXT,                       -- Product name
    description TEXT,                 -- Product description
    brand VARCHAR(100),               -- Brand name
    price_value FLOAT,                -- Price in USD
    category VARCHAR(100),            -- Electronics, Clothing, etc.
    condition VARCHAR(50),            -- New, Used, etc.
    seller_name VARCHAR(100),         -- Seller/store name
    image_url TEXT,                   -- Product image
    product_url TEXT,                 -- Link to product
    rating FLOAT,                     -- User rating
    review_count INTEGER,             -- Number of reviews
    created_at DATETIME,              -- When added
    updated_at DATETIME               -- Last updated
);
```

### **Search Queries Table**
```sql
CREATE TABLE search_queries (
    id INTEGER PRIMARY KEY,
    query_text VARCHAR(500) UNIQUE,   -- "iPhone case"
    category VARCHAR(100),            -- Mobile, Electronics, etc.
    difficulty VARCHAR(20),           -- Easy, Medium, Hard
    created_at DATETIME
);
```

### **Search Results Table**
```sql
CREATE TABLE search_results (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,               -- Links to products table
    query_id INTEGER,                 -- Links to search_queries table
    algorithm_name VARCHAR(50),       -- keyword_matching, tfidf
    relevance_score FLOAT,            -- Algorithm's score
    rank_position INTEGER,            -- Position in results
    matched_terms TEXT,               -- Terms that matched
    search_time_ms FLOAT,             -- How long search took
    created_at DATETIME
);
```

### **Evaluation Metrics Table**
```sql
CREATE TABLE evaluation_metrics (
    id INTEGER PRIMARY KEY,
    query_id INTEGER,                 -- Links to search_queries
    algorithm_name VARCHAR(50),       -- Which algorithm
    precision_at_1 FLOAT,             -- Precision@1
    precision_at_3 FLOAT,             -- Precision@3
    precision_at_5 FLOAT,             -- Precision@5
    precision_at_10 FLOAT,            -- Precision@10
    recall_at_1 FLOAT,                -- Recall@1
    recall_at_3 FLOAT,                -- Recall@3
    recall_at_5 FLOAT,                -- Recall@5
    recall_at_10 FLOAT,               -- Recall@10
    f1_score_at_1 FLOAT,              -- F1@1
    f1_score_at_3 FLOAT,              -- F1@3
    f1_score_at_5 FLOAT,              -- F1@5
    f1_score_at_10 FLOAT,             -- F1@10
    ndcg_at_1 FLOAT,                  -- NDCG@1
    ndcg_at_3 FLOAT,                  -- NDCG@3
    ndcg_at_5 FLOAT,                  -- NDCG@5
    ndcg_at_10 FLOAT,                 -- NDCG@10
    map_score FLOAT,                  -- Mean Average Precision
    mrr_score FLOAT,                  -- Mean Reciprocal Rank
    avg_search_time_ms FLOAT,         -- Average search time
    total_results_returned INTEGER,   -- How many results
    created_at DATETIME
);
```

---

## 🔧 Database Configuration

### **Default: SQLite (Recommended for Development)**

```bash
# Uses: data/ecommerce_research.db
# No setup required - works out of the box
python init_database.py
```

### **Production: PostgreSQL (Recommended for Large Scale)**

```bash
# Set environment variable
export DATABASE_URL="postgresql://username:password@localhost:5432/ecommerce_research"

# Initialize with PostgreSQL
python init_database.py
```

### **MySQL Support**

```bash
# Set environment variable
export DATABASE_URL="mysql://username:password@localhost:3306/ecommerce_research"

# Initialize with MySQL
python init_database.py
```

---

## 📈 Performance Features

### **Database Indexes**

The system automatically creates indexes for fast queries:

- **Product Search**: `title`, `category`, `brand`, `price_value`
- **Search Results**: `algorithm_name`, `relevance_score`, `rank_position`
- **Evaluation**: `query_id`, `algorithm_name`, `map_score`

### **Optimization Settings**

- **SQLite**: WAL mode, optimized cache, memory temp storage
- **PostgreSQL**: Automatic VACUUM, ANALYZE for performance
- **Connection Pooling**: Efficient connection management

### **Scalability Features**

- **Batch Operations**: Insert thousands of products efficiently
- **Pagination**: Handle large result sets
- **Memory Management**: Stream large datasets
- **Concurrent Access**: Multiple processes can work simultaneously

---

## 🛒 Data Collection APIs

### **Best Buy API (Recommended)**

```bash
# Get free API key: https://developer.bestbuy.com/
export BESTBUY_API_KEY="your_key_here"

# Collect real electronics data
python collect_to_database.py
```

**Features:**
- ✅ Real Best Buy products and prices
- ✅ 5,000 requests/day free
- ✅ Electronics, appliances, gaming
- ✅ Detailed product specifications

### **Shopify Stores (No API Key Required)**

```bash
# Collects from public Shopify stores
python collect_to_database.py
```

**Features:**
- ✅ Real e-commerce store products
- ✅ No rate limits
- ✅ Various categories
- ✅ No authentication needed

### **Target API**

```bash
# Get free API key: https://developer.target.com/
export TARGET_API_KEY="your_key_here"
```

### **Newegg API**

```bash
# Get free API key: https://developer.newegg.com/
export NEWEGG_API_KEY="your_key_here"
```

---

## 🔍 Search Algorithm Integration

### **Database-Based Search**

The search algorithms work directly with database data:

```python
# Load products from database
products = load_products_from_database(limit=10000)

# Run search algorithms
results = algorithm.search("iPhone case", products)

# Store results in database
store_search_results(query_id, algorithm_name, results)
```

### **Performance Tracking**

Every search is tracked:

- **Search Time**: Milliseconds per search
- **Result Count**: Number of results returned
- **Relevance Scores**: Algorithm confidence scores
- **Matched Terms**: Which terms triggered matches

---

## 📊 Analytics and Reporting

### **Real-Time Statistics**

```python
# Get current database stats
stats = db_manager.get_database_stats()

print(f"Products: {stats['products']}")
print(f"Categories: {stats['unique_categories']}")
print(f"Price Range: ${stats['price_range']['min']} - ${stats['price_range']['max']}")
```

### **Performance Comparison**

```python
# Compare algorithms
python run_database_search.py

# Generates report:
# - Average Precision@5 for each algorithm
# - Average Recall@5 for each algorithm
# - Average MAP scores
# - Search speed comparison
```

### **Data Collection Monitoring**

```python
# Track collection activities
logs = session.query(DataCollectionLog).all()

for log in logs:
    print(f"{log.api_source}: {log.products_collected} products in {log.collection_time_seconds}s")
```

---

## 🎯 Expected Scale

### **Small Scale (Testing)**
- **Products**: 1,000 - 10,000
- **Queries**: 50 - 200
- **Database Size**: 10 - 100 MB
- **Search Time**: < 1 second per query

### **Medium Scale (Research)**
- **Products**: 10,000 - 100,000
- **Queries**: 200 - 1,000
- **Database Size**: 100 MB - 1 GB
- **Search Time**: 1 - 5 seconds per query

### **Large Scale (Production)**
- **Products**: 100,000 - 1,000,000+
- **Queries**: 1,000 - 10,000+
- **Database Size**: 1 GB - 10 GB+
- **Search Time**: 5 - 30 seconds per query

---

## 🚀 Usage Examples

### **Collect 10,000 Products**

```bash
# Initialize database
python init_database.py

# Collect from Best Buy (requires API key)
export BESTBUY_API_KEY="your_key"
python collect_to_database.py

# Expected: ~500-1000 products per hour
```

### **Run Large-Scale Evaluation**

```bash
# Run search algorithms on all products
python run_database_search.py

# Expected results:
# - 50+ search queries tested
# - 2 algorithms compared
# - 1000+ search results stored
# - Performance metrics calculated
```

### **Analyze Results**

```python
from database.db_manager import get_db_manager

db = get_db_manager()
with db.get_session() as session:
    # Get top performing algorithm
    best_algorithm = session.query(EvaluationMetrics)\
        .order_by(EvaluationMetrics.map_score.desc())\
        .first()
    
    print(f"Best algorithm: {best_algorithm.algorithm_name}")
    print(f"MAP score: {best_algorithm.map_score}")
```

---

## 🔧 Troubleshooting

### **Database Connection Issues**

```bash
# Check database health
python -c "from database.db_manager import get_db_manager; print(get_db_manager().check_database_health())"
```

### **Performance Issues**

```bash
# Optimize database
python -c "from database.db_manager import get_db_manager; get_db_manager().optimize_database()"
```

### **Storage Issues**

```bash
# Check database size
ls -lh data/ecommerce_research.db

# Backup database
python -c "from database.db_manager import get_db_manager; get_db_manager().backup_database('backup.db')"
```

---

## 🏆 Success Metrics

You'll know the database setup is working when:

1. **Database Initialization**: ✅ Tables created successfully
2. **Data Collection**: ✅ Products stored with real prices and descriptions
3. **Search Performance**: ✅ Algorithms return results in < 5 seconds
4. **Evaluation Metrics**: ✅ Precision, Recall, F1-scores calculated
5. **Scalability**: ✅ Can handle 10,000+ products without issues

---

## 🎉 Ready for Large-Scale Research!

Your database is now ready to handle:

- ✅ **Hundreds of thousands of products**
- ✅ **Real e-commerce data from multiple APIs**
- ✅ **Comprehensive search algorithm evaluation**
- ✅ **Performance tracking and analytics**
- ✅ **Scalable architecture for research growth**

**Perfect for your "Comparative Study of Search Algorithms in E-commerce" research!** 🚀
