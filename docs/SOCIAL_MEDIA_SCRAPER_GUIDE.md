# Social Media Scraper Guide

This guide explains how to use the social media scraper to collect product data from Reddit and Twitter.

## Overview

The social media scraper collects product-related posts from Reddit and Twitter to create a noisy, realistic dataset for research purposes. It targets ~50,000 posts across both platforms using multiple Reddit apps for faster collection.

**Current Status**: 9,000+ Reddit posts collected, Twitter collection limited due to API changes.

## Quick Start

### 1. Setup API Credentials

First, set up your API credentials in a `.env` file:

```bash
# Copy the template
cp env.template .env

# Edit with your credentials
nano .env
```

Required credentials:
- **Reddit**: Client ID and Secret (get from https://www.reddit.com/prefs/apps)
- **Twitter**: Bearer Token (get from https://developer.twitter.com/)

### 2. Run the Scraper

```bash
python scripts/data_collection/real_social_media_scraper.py
```

## Configuration

The scraper is configured to collect:
- **Reddit**: 40,000 posts from product-related subreddits using multiple apps
- **Twitter**: 10,000 tweets with product hashtags
- **Total Target**: ~50,000 posts across both platforms

## Data Collection

### Reddit
- **Subreddits**: r/BuyItForLife, r/ProductPorn, r/deals, r/consumerism, etc.
- **Content**: Product discussions, reviews, recommendations
- **Method**: Uses old.reddit.com for easier scraping

### X (Twitter)
- **Hashtags**: #deals, #products, #shopping, #review, etc.
- **Content**: Product tweets, deals, reviews
- **Method**: Uses nitter.net instances (Twitter frontend without API)

### TikTok
- **Hashtags**: #tiktokmademebuyt, #productreview, #shopping, etc.
- **Content**: Product videos, reviews, shopping content
- **Method**: Uses Playwright for dynamic content loading

### Instagram
- **Hashtags**: #shopping, #products, #review, etc.
- **Content**: Shopping posts, product tags, reviews
- **Method**: Uses Playwright for Instagram web interface

## Output

### Database
All data is saved to the `social_media_products` table with fields:
- `post_id`: Unique identifier for the post
- `platform`: reddit, twitter, tiktok, instagram
- `title`: Post title or first 100 characters
- `content`: Full post content
- `author`: Post author
- `upvotes`: Number of upvotes/likes
- `comments_count`: Number of comments
- `product_name`: Extracted product name
- `brand`: Extracted brand
- `category`: Detected product category
- `price_mentioned`: Extracted price if mentioned
- `is_review`: Whether post is a review
- `is_recommendation`: Whether post is a recommendation

### Files
- `data/social_media_products.json`: JSON backup of all collected data
- `data/social_media_summary.txt`: Collection summary and statistics
- `data/{platform}_checkpoint.json`: Progress checkpoints for resuming

## Rate Limiting

The scraper includes built-in rate limiting:
- **Delays**: 2-5 seconds between requests (randomized)
- **User Agent Rotation**: Different user agents to avoid detection
- **Error Handling**: Retries and skips blocked sources
- **Checkpoints**: Saves progress every 1000 posts

## Troubleshooting

### Common Issues

1. **Rate Limiting**: If you get 429 errors, increase delays in the config
2. **Nitter Instances**: Some nitter instances may be down, the scraper will try alternatives
3. **Database Errors**: Ensure the database is initialized with `python scripts/init_database.py`

### Platform-Specific Issues

- **Reddit**: May get 403 errors due to rate limiting
- **Twitter**: Nitter instances may be unreliable
- **TikTok**: Requires Playwright browser, may be slow
- **Instagram**: May require login for some content

## Monitoring Progress

The scraper provides detailed logging:
- Progress updates for each platform
- Error messages for failed requests
- Database save confirmations
- Final summary statistics

## Data Quality

The scraper includes data quality features:
- **Product Detection**: Identifies product-related content
- **Brand Extraction**: Extracts brand names from text
- **Category Classification**: Detects product categories
- **Price Extraction**: Finds mentioned prices
- **Sentiment Analysis**: Identifies reviews vs recommendations

## Resuming Interrupted Scraping

If scraping is interrupted, you can resume by running the same command. The scraper will:
1. Load existing checkpoints
2. Skip already collected posts
3. Continue from where it left off

## Expected Results

After completion, you should have:
- ~100,000 social media posts in the database
- Diverse product categories and brands
- Realistic, noisy data with typos and slang
- Both positive and negative product mentions
- Various engagement levels and post types

This creates a comprehensive dataset for testing search algorithms on social media content.
