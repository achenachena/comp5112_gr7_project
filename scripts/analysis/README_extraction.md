# Advanced Product Information Extraction

This script provides advanced product information extraction for existing social media posts in your database.

## Features

- **Enhanced Product Detection**: Detects products using advanced NLP techniques
- **Brand Recognition**: Automatically identifies major brands (Apple, Samsung, Nike, etc.)
- **Category Classification**: Categorizes products (electronics, clothing, beauty, etc.)
- **Price Extraction**: Extracts prices from various formats ($9.00, USD 9.00, etc.)
- **Sentiment Analysis**: Analyzes sentiment of product mentions
- **Review Detection**: Identifies review and recommendation posts

## Usage

### Basic Usage (Test Mode)
```bash
# Test extraction on 5 posts without updating database
python scripts/extract_product_info.py --limit 5

# Test extraction on 10 posts without updating database
python scripts/extract_product_info.py --limit 10
```

### Update Database
```bash
# Update database with enhanced product information
python scripts/extract_product_info.py --update

# Update only first 100 posts
python scripts/extract_product_info.py --update --limit 100
```

### Analyze Results
```bash
# Analyze extraction results and show statistics
python scripts/extract_product_info.py --analyze
```

## Examples

### Test Extraction (No Database Changes)
```bash
python scripts/extract_product_info.py --limit 3
```

Output:
```
🔍 Advanced Product Information Extraction
==================================================
📊 Processing 3 posts...

📝 Sample #1: Best $9.00 audio upgrade
   🛍️  Product: Best $9.00 audio upgrade - Even more important that the speakers
   🏷️  Brand: None
   📂 Category: electronics
   💰 Price: 9.0
   ⭐ Review: False
   👍 Recommendation: False
   😊 Sentiment: 0.80
   🏷️  Tags: []
```

### Update Database
```bash
python scripts/extract_product_info.py --update --limit 50
```

### Analyze Results
```bash
python scripts/extract_product_info.py --analyze
```

Output:
```
📊 EXTRACTION ANALYSIS
==============================
📈 Total Posts: 2,824
🛍️  Posts with Product Names: 501 (17.7%)
🏷️  Posts with Brands: 31 (1.1%)
📂 Posts with Categories: 812 (28.8%)
💰 Posts with Prices: 290 (10.3%)

🏆 TOP BRANDS:
   Apple: 10 posts
   Samsung: 6 posts
   Amazon: 5 posts
   Microsoft: 3 posts
   Google: 2 posts
```

## What Gets Extracted

### Product Information
- **Product Name**: Meaningful product descriptions
- **Brand**: Major brands (Apple, Samsung, Nike, etc.)
- **Category**: Electronics, clothing, beauty, automotive, home, sports
- **Price**: Extracted from various price formats
- **Sentiment**: Positive/negative sentiment scoring
- **Review Status**: Whether it's a review or recommendation
- **Tags**: List of detected brands

### Supported Brands
- **Tech**: Apple, Samsung, Sony, Microsoft, Google, Amazon
- **Audio**: AirPods, Beats, Bose, JBL, Sennheiser, Audio-Technica
- **Fashion**: Nike, Adidas, Puma, Under Armour, Lululemon, Patagonia
- **Automotive**: Tesla, BMW, Audi, Mercedes

### Categories
- **Electronics**: phone, laptop, tablet, headphones, speaker, camera, gaming, audio
- **Clothing**: shirt, dress, pants, shoes, jacket, sweater, jeans
- **Beauty**: skincare, makeup, sunscreen, moisturizer, serum, foundation
- **Automotive**: car, truck, SUV, sedan, vehicle, automobile
- **Home**: furniture, appliance, kitchen, bedroom, living room
- **Sports**: fitness, gym, running, cycling, yoga, workout

## Database Schema

The script updates these fields in the `social_media_products` table:
- `product_name`: Extracted product name
- `brand`: Detected brand
- `category`: Product category
- `price_mentioned`: Extracted price
- `price_currency`: Currency (USD)
- `is_review`: Whether it's a review
- `is_recommendation`: Whether it's a recommendation
- `sentiment_score`: Sentiment score (0.0-1.0)
- `tags`: JSON array of detected brands

## Performance

- **Processing Speed**: ~100-200 posts per second
- **Memory Usage**: Low memory footprint
- **Database Impact**: Only updates existing records, doesn't create new ones
- **Error Handling**: Continues processing even if individual posts fail

## Best Practices

1. **Test First**: Always test with `--limit` before running on full dataset
2. **Backup Database**: Backup your database before running `--update`
3. **Monitor Progress**: The script shows progress every 100 posts
4. **Analyze Results**: Use `--analyze` to see extraction statistics
5. **Incremental Processing**: Use `--limit` for large datasets

## Troubleshooting

### Common Issues
- **Database Connection**: Ensure database is accessible
- **Memory Issues**: Use `--limit` for large datasets
- **Permission Errors**: Ensure write permissions for database

### Error Messages
- `Database session error`: Database connection issue
- `Error processing post`: Individual post processing failed (continues with others)
- `AttributeError`: Database schema issue

## Examples for Your Presentation

After running the extraction, you can get enhanced examples:

```bash
# Get examples with better product information
python -c "
import sqlite3
conn = sqlite3.connect('data/ecommerce_research.db')
cursor = conn.cursor()
cursor.execute('''
SELECT post_id, title, product_name, brand, category, price_mentioned, sentiment_score
FROM social_media_products 
WHERE product_name IS NOT NULL AND brand IS NOT NULL
ORDER BY sentiment_score DESC
LIMIT 5
''')
for row in cursor.fetchall():
    print(f'Post: {row[1][:50]}...')
    print(f'Product: {row[2]}')
    print(f'Brand: {row[3]}')
    print(f'Category: {row[4]}')
    print(f'Price: ${row[5]}')
    print(f'Sentiment: {row[6]:.2f}')
    print('---')
"
```

This will give you much better examples for your presentation with proper product names, brands, and categories!
