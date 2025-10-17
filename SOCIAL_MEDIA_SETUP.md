# Social Media Scraping Setup Guide

This guide explains how to set up social media scraping to collect 100,000 product-related posts from Reddit and Twitter for algorithm comparison.

## 🎯 Overview

The social media scraping system collects real user-generated content about products, providing a noisy, authentic dataset that contrasts with the clean API-based data. This allows for comprehensive algorithm comparison across different data types.

## 📋 Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ and virtual environment activated
2. **Database**: SQLite database should be initialized
3. **API Keys**: Reddit and Twitter API credentials (see setup below)

## 🔑 API Setup

### Reddit API Setup

1. **Create Reddit App**:
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Choose "script" as the app type
   - Note down your `client_id` and `client_secret`

2. **Get Credentials**:
   - `client_id`: The string under your app name (e.g., "abc123def456")
   - `client_secret`: The secret key provided

### Twitter API Setup

1. **Apply for Developer Access**:
   - Go to https://developer.twitter.com/
   - Apply for a developer account
   - Create a new app in the developer portal

2. **Get Bearer Token**:
   - In your app settings, go to "Keys and Tokens"
   - Generate a Bearer Token for API v2 access

## ⚙️ Installation

### 1. Install Dependencies

```bash
# Install social media scraping dependencies
pip install praw tweepy textblob beautifulsoup4

# Or install all requirements
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add your API credentials to your `.env` file:

```bash
# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here

# Twitter API
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
```

### 3. Update Database Schema

```bash
# Update database to include social media tables
python update_database_schema.py
```

## 🕷️ Running the Scraper

### Basic Scraping

```bash
# Run the social media scraper
python social_media_scraper.py
```

### Advanced Configuration

You can customize the scraping behavior by setting environment variables:

```bash
# Maximum posts per subreddit (default: 1000)
MAX_POSTS_PER_SUBREDDIT=1000

# Delay between requests in seconds (default: 1.0)
SCRAPING_DELAY=1.0

# Maximum tweets to collect (default: 5000)
MAX_TWEETS=5000
```

## 📊 Expected Results

### Target: 100,000 Products

The scraper will target the following subreddits for product discussions:

**Technology & Gadgets:**
- `Tech`, `Gadgets`, `Headphones`, `MechanicalKeyboards`, `Gaming`, `PCGaming`
- `Laptop`, `Smartphone`, `iPhone`, `Android`, `Mac`, `Windows`

**Fashion & Beauty:**
- `Fashion`, `SkincareAddiction`, `MakeupAddiction`, `Skincare`, `Fragrance`, `Watches`

**Lifestyle & Home:**
- `Coffee`, `Tea`, `HomeImprovement`, `Tools`, `CampingGear`, `OutdoorGear`

**Reviews & Recommendations:**
- `BuyItForLife`, `GoodValue`, `BIFL`, `Reviews`, `Shopping`, `Deals`

### Data Quality

Each scraped post includes:

- **Content**: Title and full text
- **Metadata**: Author, date, platform, subreddit
- **Engagement**: Upvotes, comments, engagement score
- **Product Info**: Extracted product names, brands, categories
- **Sentiment**: Sentiment analysis score
- **Classification**: Review, recommendation, or complaint flags

## 🔍 Data Processing

### Automatic Product Extraction

The scraper automatically:

1. **Filters Content**: Only processes posts with product-related keywords
2. **Extracts Products**: Identifies product names, brands, categories
3. **Analyzes Sentiment**: Calculates sentiment scores using TextBlob
4. **Classifies Content**: Flags reviews, recommendations, complaints
5. **Calculates Engagement**: Measures post popularity and interaction

### Quality Filters

- **Minimum Content Length**: 50 characters
- **Minimum Engagement**: 0.1 engagement score
- **Product Keywords**: Must contain product-related terms
- **Duplicate Detection**: Prevents duplicate posts

## 📈 Monitoring Progress

### Check Scraping Status

```bash
# View database statistics
python -c "
from database.db_manager import get_db_manager
from database.models import SocialMediaProduct
db = get_db_manager()
with db.get_session() as session:
    count = session.query(SocialMediaProduct).count()
    print(f'Social Media Products: {count:,}')
"
```

### View Sample Data

```bash
# See sample scraped posts
python -c "
from database.db_manager import get_db_manager
from database.models import SocialMediaProduct
db = get_db_manager()
with db.get_session() as session:
    posts = session.query(SocialMediaProduct).limit(5).all()
    for post in posts:
        print(f'{post.platform}/{post.subreddit}: {post.title[:60]}...')
"
```

## 🔄 Running Comparisons

### Compare Dataset Types

```bash
# Compare API vs Social Media performance
python compare_datasets.py
```

This will:

1. **Load Both Datasets**: API products and social media posts
2. **Run Algorithm Tests**: Keyword Matching vs TF-IDF on each dataset
3. **Generate Reports**: Performance comparison across dataset types
4. **Save Results**: Detailed JSON reports and visualizations

### Expected Insights

- **API Data**: Clean, structured product information
- **Social Media Data**: Noisy, conversational, user-generated content
- **Algorithm Performance**: How each algorithm handles different data types
- **Dataset Characteristics**: Impact of data quality on search performance

## 🎯 Target Collection Strategy

### Phase 1: Reddit Collection (Primary)

- **Target**: 80,000+ posts from product-related subreddits
- **Method**: Systematic scraping across 40+ subreddits
- **Timeline**: 2-3 hours for full collection

### Phase 2: Twitter Collection (Secondary)

- **Target**: 20,000+ tweets with product mentions
- **Method**: Twitter API v2 search functionality
- **Timeline**: 1-2 hours (limited by API rate limits)

### Phase 3: Data Enhancement

- **Sentiment Analysis**: Enhanced sentiment scoring
- **Product Extraction**: Improved product name/brand detection
- **Quality Filtering**: Advanced content quality assessment

## 🚨 Troubleshooting

### Common Issues

1. **Reddit API Rate Limits**:
   - Increase `SCRAPING_DELAY` to 2-3 seconds
   - Reduce `MAX_POSTS_PER_SUBREDDIT` to 500

2. **Twitter API Access**:
   - Ensure you have academic research access for full historical data
   - Consider using Twitter API v1.1 for broader access

3. **Database Locking**:
   - Ensure no other processes are accessing the database
   - Use connection pooling for concurrent access

### Error Handling

The scraper includes comprehensive error handling:

- **API Failures**: Automatic retry with exponential backoff
- **Rate Limiting**: Automatic delays and retry logic
- **Data Validation**: Skips invalid or malformed posts
- **Duplicate Prevention**: Checks for existing posts before insertion

## 📊 Success Metrics

### Collection Targets

- ✅ **100,000 Total Posts**: Across all platforms
- ✅ **40+ Subreddits**: Comprehensive coverage
- ✅ **Multiple Platforms**: Reddit primary, Twitter secondary
- ✅ **Quality Filtering**: Only relevant, engaging content

### Data Quality Metrics

- **Engagement Score**: Average > 1.0
- **Content Length**: Average > 100 characters
- **Product Mentions**: > 80% of posts contain product information
- **Sentiment Distribution**: Balanced positive/negative/neutral

## 🔮 Next Steps

After successful collection:

1. **Run Algorithm Comparison**: `python compare_datasets.py`
2. **Analyze Results**: Review performance differences
3. **Generate Reports**: Create presentation materials
4. **Document Insights**: Record findings and recommendations

## 📚 Additional Resources

- **Reddit API Documentation**: https://praw.readthedocs.io/
- **Twitter API Documentation**: https://developer.twitter.com/en/docs
- **TextBlob Documentation**: https://textblob.readthedocs.io/
- **Database Schema**: See `database/models.py` for full schema

---

**Ready to start collecting 100,000 social media products? Run `python social_media_scraper.py` after setting up your API credentials!** 🚀
