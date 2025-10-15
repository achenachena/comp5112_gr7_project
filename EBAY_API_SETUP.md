# eBay API Setup Instructions for Data Collection

## Quick Start Guide

Follow these steps to collect real product data from eBay's API.

---

## Step 1: Get eBay API Credentials

### 1.1 Create eBay Developer Account
1. Go to [eBay Developers Program](https://developer.ebay.com/)
2. Click **"Register"** or **"Sign In"** if you have an account
3. Complete the registration process

### 1.2 Create an Application
1. After logging in, go to **"My Account"** → **"Applications"**
2. Click **"Create an App Key"** or **"Create Application"**
3. Fill in the application details:
   - **App Title**: "E-commerce Search Research" (or any name)
   - **App Purpose**: "Research and Development"
   - **App Type**: "Web Application"
4. After creation, you'll receive:
   - **App ID (Client ID)**
   - **Cert ID (Client Secret)**

### 1.3 Generate OAuth Token
1. In your application dashboard, find the **"OAuth Tokens"** section
2. For **Sandbox environment** (recommended for testing):
   - Click **"Generate Token"** under Sandbox
   - Select scopes: `buy.item` (minimum required)
   - Copy the generated token
3. For **Production environment** (real data):
   - Follow the same process under Production section
   - Note: Production has rate limits and quotas

---

## Step 2: Configure Your Environment

### 2.1 Create `.env` file
In your project root directory, create a file named `.env` (note the dot at the beginning):

```bash
# On Mac/Linux
touch .env

# Or just create it in your text editor
```

### 2.2 Add Your Credentials to `.env`

Open `.env` and add the following (replace with your actual credentials):

```bash
# eBay API Credentials
EBAY_APP_ID=YourAppID
EBAY_CLIENT_ID=YourClientID
EBAY_CLIENT_SECRET=YourClientSecret
EBAY_REDIRECT_URI=Your_Redirect_URI
EBAY_OAUTH_TOKEN=v^1.1#i^1#...your_long_token_here...
EBAY_ENVIRONMENT=sandbox
```

**Important Notes:**
- The OAuth token is very long (hundreds of characters) - copy it completely
- Use `sandbox` for testing first, then switch to `production` for real data
- Never commit the `.env` file to Git (it's already in `.gitignore`)

---

## Step 3: Test Your Setup

Run the example script to test if your credentials work:

```bash
python example_usage.py
```

If successful, you should see product search results printed to the console.

---

## Step 4: Collect Dataset

Run the data collection script:

```bash
python collect_ebay_data.py
```

This will:
1. Query eBay API for 16 different product categories
2. Collect ~20 products per category (~320 total products)
3. Save results to `data/ebay_products.json`
4. Generate a summary in `data/collection_summary.txt`

### Customize Data Collection

Edit `collect_ebay_data.py` to customize:
- **Search queries**: Modify the `search_queries` list
- **Products per query**: Change `products_per_query` parameter
- **Output location**: Change `output_dir` parameter

Example:
```python
search_queries = [
    "your custom query 1",
    "your custom query 2",
    # ... add more
]

products = collect_data_for_queries(
    client=client,
    queries=search_queries,
    products_per_query=50,  # Collect 50 per query
    output_dir='my_data'    # Save to my_data/
)
```

---

## Step 5: Use Collected Data in Your Research

Once you have collected data, you can use it in your search algorithm comparison:

```python
# Load your collected data
import json

with open('data/ebay_products.json', 'r') as f:
    data = json.load(f)
    products = data['products']

# Use in your algorithms
from algorithms.keyword_matching import KeywordSearch
from algorithms.tfidf_search import TFIDFSearch

keyword_search = KeywordSearch()
tfidf_search = TFIDFSearch()

# Search with your real data
results_kw = keyword_search.search("iPhone case", products)
results_tfidf = tfidf_search.search("iPhone case", products)
```

---

## Troubleshooting

### Issue: "OAuth token not found"
**Solution**: Make sure your `.env` file is in the project root and contains `EBAY_OAUTH_TOKEN=...`

### Issue: "Authentication failed" or 401 error
**Solution**: 
- Your OAuth token may have expired (they expire after a few hours)
- Generate a new token from eBay Developer Portal
- Update your `.env` file with the new token

### Issue: "Rate limit exceeded"
**Solution**:
- You've made too many requests too quickly
- Wait a few minutes before trying again
- Consider using sandbox environment for testing
- Add delays between requests (already implemented in script)

### Issue: "No results found"
**Solution**:
- Check if you're using sandbox vs production environment
- Sandbox has limited test data
- Try different search queries
- Switch to production environment for real data

---

## API Rate Limits

### Sandbox Environment
- Limited to test data only
- Good for testing your code
- Fewer rate limits

### Production Environment
- Access to real eBay listings
- **Rate Limits**: 
  - 5,000 calls per day for most apps
  - Can request increase if needed
- **Quota Management**: Monitor usage in developer portal

---

## Alternative: Use Sample Data

If you can't access the eBay API right now, the project includes sample data:

```bash
# Run with built-in sample data
python prototype/cli.py --mode compare

# Or use GUI with sample data
python prototype/gui.py
```

---

## Resources

- [eBay Developer Portal](https://developer.ebay.com/)
- [eBay Browse API Documentation](https://developer.ebay.com/api-docs/buy/browse/overview.html)
- [OAuth Token Guide](https://developer.ebay.com/api-docs/static/oauth-tokens.html)
- [API Rate Limits](https://developer.ebay.com/support/kb-article?KBid=4638)

---

## Security Best Practices

1. **Never commit `.env` file** to Git (it's ignored by default)
2. **Don't share your OAuth tokens** publicly
3. **Regenerate tokens regularly** for security
4. **Use sandbox for development**, production only when ready
5. **Monitor your API usage** in the developer portal

---

## Next Steps

After collecting your dataset:

1. ✓ Verify data quality by inspecting `data/ebay_products.json`
2. ✓ Update test queries in `prototype/cli.py` to match your dataset
3. ✓ Run comparison: `python prototype/cli.py --mode compare --data data/ebay_products.json`
4. ✓ Analyze results and prepare your research findings

Good luck with your research! 🚀


