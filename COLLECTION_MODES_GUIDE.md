# Data Collection Modes Guide

## Overview
The data collection tool now supports multiple collection modes to give you full control over your dataset composition.

## Collection Modes

### 1. API-Based Collection (`--mode api`)
Collects structured product data from e-commerce APIs.

**Usage:**
```bash
# Collect from all API sources (default)
python collect_to_database.py --mode api

# Collect only from Walmart API
python collect_to_database.py --mode api --api-sources walmart

# Collect only from Shopify stores
python collect_to_database.py --mode api --api-sources shopify

# Collect from both with custom target
python collect_to_database.py --mode api --api-sources walmart shopify --max-products 100000
```

**Data Sources:**
- **Walmart API**: General merchandise, electronics, home goods
- **Shopify Stores**: Fashion, accessories, lifestyle products

### 2. Social Media Scraping (`--mode social`)
Collects product-related posts from social media platforms.

**Usage:**
```bash
# Collect from Reddit (default)
python collect_to_database.py --mode social

# Collect from Twitter
python collect_to_database.py --mode social --social-sources twitter

# Collect from both Reddit and Twitter
python collect_to_database.py --mode social --social-sources reddit twitter
```

**Data Sources:**
- **Reddit**: Product discussions, reviews, recommendations
- **Twitter**: Product mentions, reviews, trends

### 3. Combined Collection (`--mode both`)
Collects from both API sources and social media platforms.

**Usage:**
```bash
# Collect from all sources
python collect_to_database.py --mode both

# Custom combination
python collect_to_database.py --mode both --api-sources shopify --social-sources reddit
```

## Command Line Arguments

| Argument | Options | Default | Description |
|----------|---------|---------|-------------|
| `--mode` | `api`, `social`, `both` | `api` | Collection mode |
| `--api-sources` | `walmart`, `shopify` | `walmart shopify` | API sources to use |
| `--social-sources` | `reddit`, `twitter` | `reddit` | Social media sources |
| `--max-products` | integer | `50000` | Maximum items to collect |

## Examples

### Quick API Collection
```bash
python collect_to_database.py
```

### Large Scale API Collection
```bash
python collect_to_database.py --mode api --max-products 100000
```

### Social Media Research
```bash
python collect_to_database.py --mode social --social-sources reddit twitter
```

### Comprehensive Dataset
```bash
python collect_to_database.py --mode both --max-products 75000
```

### Shopify-Only Collection
```bash
python collect_to_database.py --mode api --api-sources shopify
```

## Data Storage

- **API Data**: Stored in `api_products` table
- **Social Media Data**: Stored in `social_media_products` table
- **Unified Access**: Both datasets can be queried together for analysis

## Prerequisites

### API Collection
- Walmart API key (optional, in `.env`)
- Shopify stores list (in `.env` as `SHOPIFY_STORES`)

### Social Media Collection
```bash
pip install praw tweepy textblob beautifulsoup4
```
- Reddit API credentials (in `.env`)
- Twitter API credentials (in `.env`)

## Tips

1. **Start Small**: Test with `--max-products 1000` first
2. **Monitor Progress**: The tool shows real-time collection statistics
3. **Use Both Modes**: API data provides structure, social media provides sentiment
4. **Customize Sources**: Choose sources that match your research focus
5. **Check Database**: Use database tools to verify collected data
