# Quick Start: Database-Based E-commerce Search Research

## 🚀 Fast Track (5 minutes)

### 1. Initialize Database
```bash
python init_database.py
```

### 2. Collect Real Data
```bash
# Option A: Get Best Buy API key (recommended)
# Go to: https://developer.bestbuy.com/
# Add to .env: BESTBUY_API_KEY=your_key_here
python collect_to_database.py

# Option B: Use Shopify stores (no API key needed)
python collect_to_database.py
```

### 3. Run Search Evaluation
```bash
python run_database_search.py
```

### 4. Check Results
Look for: `data/ecommerce_research.db` (SQLite database)

---

## 📋 What You Need

1. **Best Buy API Key** (recommended): https://developer.bestbuy.com/
2. **Python Environment**: Already set up with `requirements.txt`
3. **Internet Connection**: For API data collection

---

## 🔧 If Something Goes Wrong

### "No API keys found"
→ Get Best Buy API key: https://developer.bestbuy.com/

### "Database connection failed"
→ Run `python init_database.py` to initialize database

### "No products collected"
→ Check internet connection and API key validity

### "Rate limit exceeded"
→ Wait before making more API requests

---

## 💡 Tips

- **Start with Best Buy API** - easiest to set up and has great data
- **Use Shopify stores** if you don't want to get API keys
- **Database scales** - can handle hundreds of thousands of products
- **Real marketplace data** - actual prices and product descriptions
- **Output location**: `data/ecommerce_research.db`

---

## 📊 After Collection

Use your database for search algorithm research:

```bash
# Run comprehensive evaluation
python run_database_search.py

# CLI mode with sample data
python prototype/cli.py --mode compare

# GUI mode
python web_gui.py
```

Your real e-commerce data is now stored in the SQL database and ready for large-scale research!


