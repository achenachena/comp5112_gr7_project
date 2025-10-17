#!/usr/bin/env python3
"""
Social Media Scraping System for E-commerce Product Data

This module implements scraping from Reddit and Twitter/X to collect
product-related posts and reviews for algorithm comparison.
"""

import os
import sys
import json
import time
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import get_db_manager
from database.models import SocialMediaProduct

# Social media scraping libraries
try:
    import praw  # Reddit API
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False
    praw = None
    print("⚠️  PRAW not installed. Install with: pip install praw")

try:
    import tweepy  # Twitter API
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    tweepy = None
    print("⚠️  Tweepy not installed. Install with: pip install tweepy")

# NLP libraries for text processing
try:
    from textblob import TextBlob  # Sentiment analysis
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    TextBlob = None
    print("⚠️  TextBlob not installed. Install with: pip install textblob")

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None
    BeautifulSoup = None
    print("⚠️  Requests/BeautifulSoup not installed. "
          "Install with: pip install requests beautifulsoup4")


@dataclass
class ScrapingConfig:
    """Configuration for social media scraping."""
    
    # Reddit settings
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "E-commerce Research Bot 1.0"
    
    # Twitter settings
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    
    # Scraping parameters
    max_posts_per_subreddit: int = 1000
    max_tweets: int = 5000
    delay_between_requests: float = 1.0
    
    # Content filtering
    min_content_length: int = 50
    min_engagement_score: float = 0.1
    
    # Target subreddits for product discussions
    target_subreddits: List[str] = None
    
    def __post_init__(self):
        if self.target_subreddits is None:
            # Load subreddits from environment variable for privacy
            import os
            subreddits_env = os.getenv('REDDIT_SUBREDDITS')
            if subreddits_env:
                # Split by comma and clean up
                self.target_subreddits = [sub.strip() for sub in subreddits_env.split(',') if sub.strip()]
            else:
                # Fallback to a minimal demo set
                self.target_subreddits = [
                    'BuyItForLife', 'GoodValue', 'Reviews', 'Shopping', 'Tech'
                ]


class SocialMediaScraper:
    """Main class for scraping social media product data."""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.db_manager = get_db_manager()
        self.logger = self._setup_logging()
        
        # Initialize APIs
        self.reddit = self._init_reddit()
        self.twitter = self._init_twitter()
        
        # Product-related keywords for filtering
        self.product_keywords = [
            'review', 'recommend', 'buy', 'purchase', 'best', 'worst',
            'quality', 'durable', 'worth', 'value', 'price', 'cheap',
            'expensive', 'sale', 'deal', 'discount', 'bought', 'ordered',
            'received', 'shipped', 'delivered', 'return', 'refund',
            'amazon', 'ebay', 'walmart', 'target', 'best buy', 'costco',
            'product', 'item', 'thing', 'stuff', 'gadget', 'tool'
        ]
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the scraper."""
        logger = logging.getLogger('social_media_scraper')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_reddit(self):
        """Initialize Reddit API client."""
        if not REDDIT_AVAILABLE or not self.config.reddit_client_id:
            self.logger.warning("Reddit API not available or not configured")
            return None
        
        try:
            reddit = praw.Reddit(
                client_id=self.config.reddit_client_id,
                client_secret=self.config.reddit_client_secret,
                user_agent=self.config.reddit_user_agent
            )
            # Test connection
            reddit.read_only = True
            _ = reddit.subreddit('test').display_name
            self.logger.info("✅ Reddit API initialized successfully")
            return reddit
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Reddit API: {e}")
            return None
    
    def _init_twitter(self):
        """Initialize Twitter API client."""
        if not TWITTER_AVAILABLE or not self.config.twitter_bearer_token:
            self.logger.warning("Twitter API not available or not configured")
            return None
        
        try:
            import tweepy
            client = tweepy.Client(bearer_token=self.config.twitter_bearer_token)
            # Test connection
            _ = client.get_me()
            self.logger.info("✅ Twitter API initialized successfully")
            return client
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Twitter API: {e}")
            return None
    
    def extract_product_info(self, text: str) -> Dict[str, Any]:
        """Extract product information from social media text."""
        # Initialize result
        product_info = {
            'product_name': '',
            'brand': '',
            'category': '',
            'price_mentioned': None,
            'is_review': False,
            'is_recommendation': False,
            'is_complaint': False,
            'sentiment_score': 0.0,
            'tags': []
        }
        
        text_lower = text.lower()
        
        # Detect review indicators
        review_indicators = ['review', 'reviewed', 'opinion', 'thoughts', 'experience']
        product_info['is_review'] = any(indicator in text_lower for indicator in review_indicators)
        
        # Detect recommendation indicators
        rec_indicators = ['recommend', 'suggest', 'best', 'great', 'love', 'amazing']
        product_info['is_recommendation'] = any(
            indicator in text_lower for indicator in rec_indicators
        )
        
        # Detect complaint indicators
        complaint_indicators = ['terrible', 'awful', 'hate', 'worst', 'disappointed', 'regret']
        product_info['is_complaint'] = any(
            indicator in text_lower for indicator in complaint_indicators
        )
        
        # Extract price information
        price_pattern = r'\$(\d+(?:\.\d{2})?)'
        price_matches = re.findall(price_pattern, text)
        if price_matches:
            try:
                product_info['price_mentioned'] = float(price_matches[0])
            except ValueError:
                pass
        
        # Basic sentiment analysis
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                product_info['sentiment_score'] = blob.sentiment.polarity
            except:
                pass
        
        # Extract common product categories
        categories = {
            'electronics': ['phone', 'laptop', 'computer', 'headphones', 'speaker', 'camera'],
            'clothing': ['shirt', 'pants', 'shoes', 'dress', 'jacket', 'hoodie'],
            'beauty': ['skincare', 'makeup', 'shampoo', 'lotion', 'cream', 'serum'],
            'home': ['furniture', 'appliance', 'kitchen', 'bed', 'sofa', 'table'],
            'sports': ['gym', 'fitness', 'running', 'bike', 'yoga', 'workout'],
            'books': ['book', 'novel', 'ebook', 'kindle', 'audiobook'],
            'automotive': ['car', 'tire', 'oil', 'battery', 'brake', 'engine']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                product_info['category'] = category
                break
        
        # Extract tags
        words = re.findall(r'\b\w+\b', text_lower)
        product_info['tags'] = [
            word for word in words 
            if len(word) > 3 and word not in [
                'this', 'that', 'with', 'from', 'they', 'have', 'been', 'were'
            ]
        ]
        
        return product_info
    
    def scrape_reddit_posts(self) -> int:
        """Scrape product-related posts from Reddit."""
        if not self.reddit:
            self.logger.warning("Reddit API not available, skipping Reddit scraping")
            return 0
        
        total_scraped = 0
        
        for subreddit_name in self.config.target_subreddits:
            try:
                self.logger.info(f"🕷️  Scraping r/{subreddit_name}...")
                subreddit = self.reddit.subreddit(subreddit_name)
                
                posts_scraped = 0
                for submission in subreddit.hot(limit=self.config.max_posts_per_subreddit):
                    try:
                        # Check if post is relevant to products
                        content = f"{submission.title} {submission.selftext}"
                        if len(content) < self.config.min_content_length:
                            continue
                        
                        # Check for product-related keywords
                        if not any(
                            keyword in content.lower() for keyword in self.product_keywords
                        ):
                            continue
                        
                        # Extract product information
                        product_info = self.extract_product_info(content)
                        
                        # Calculate engagement score
                        engagement_score = (
                            submission.score + submission.num_comments * 0.5
                        ) / max(1, submission.created_utc)
                        
                        if engagement_score < self.config.min_engagement_score:
                            continue
                        
                        # Create social media product record
                        social_product = SocialMediaProduct(
                            post_id=submission.id,
                            platform='reddit',
                            subreddit=subreddit_name,
                            title=submission.title,
                            content=content,
                            author=str(submission.author) if submission.author else 'deleted',
                            post_date=datetime.fromtimestamp(submission.created_utc),
                            product_name=product_info['product_name'],
                            product_description=product_info.get('product_description', ''),
                            brand=product_info['brand'],
                            category=product_info['category'],
                            price_mentioned=product_info['price_mentioned'],
                            upvotes=submission.score,
                            downvotes=0,  # Reddit doesn't provide downvotes in API
                            comments_count=submission.num_comments,
                            engagement_score=engagement_score,
                            sentiment_score=product_info['sentiment_score'],
                            is_review=product_info['is_review'],
                            is_recommendation=product_info['is_recommendation'],
                            is_complaint=product_info['is_complaint'],
                            url=f"https://reddit.com{submission.permalink}",
                            tags=json.dumps(product_info['tags'])
                        )
                        
                        # Save to database
                        with self.db_manager.get_session() as session:
                            # Check if post already exists
                            existing = session.query(SocialMediaProduct).filter_by(
                                post_id=submission.id
                            ).first()
                            
                            if not existing:
                                session.add(social_product)
                                session.commit()
                                posts_scraped += 1
                                total_scraped += 1
                        
                        if posts_scraped >= self.config.max_posts_per_subreddit:
                            break
                        
                        # Rate limiting
                        time.sleep(self.config.delay_between_requests)
                        
                    except Exception as e:
                        self.logger.warning(f"Error processing Reddit post: {e}")
                        continue
                
                self.logger.info(f"✅ Scraped {posts_scraped} posts from r/{subreddit_name}")
                
            except Exception as e:
                self.logger.error(f"❌ Error scraping r/{subreddit_name}: {e}")
                continue
        
        return total_scraped
    
    def scrape_twitter_posts(self) -> int:
        """Scrape product-related tweets from Twitter."""
        if not self.twitter:
            self.logger.warning("Twitter API not available, skipping Twitter scraping")
            return 0
        
        # Note: Twitter API v2 requires academic research access for full historical data
        # This is a simplified version for demonstration
        self.logger.info("🕷️  Twitter scraping requires academic research access")
        self.logger.info("   For now, we'll use Reddit data which provides similar insights")
        return 0
    
    def scrape_all_platforms(self) -> Dict[str, int]:
        """Scrape from all available platforms."""
        self.logger.info("🚀 Starting social media scraping...")
        
        results = {}
        
        # Scrape Reddit
        reddit_count = self.scrape_reddit_posts()
        results['reddit'] = reddit_count
        
        # Scrape Twitter (if available)
        twitter_count = self.scrape_twitter_posts()
        results['twitter'] = twitter_count
        
        total_scraped = sum(results.values())
        self.logger.info("✅ Scraping completed! Total posts scraped: %d", total_scraped)
        
        return results
    
    def get_scraping_stats(self) -> Dict[str, Any]:
        """Get statistics about scraped data."""
        with self.db_manager.get_session() as session:
            total_posts = session.query(SocialMediaProduct).count()
            
            platform_stats = {}
            for platform in ['reddit', 'twitter']:
                count = session.query(SocialMediaProduct).filter_by(
                    platform=platform
                ).count()
                platform_stats[platform] = count
            
            category_stats = {}
            categories = session.query(SocialMediaProduct.category).distinct().all()
            for category_tuple in categories:
                category = category_tuple[0]
                if category:
                    count = session.query(SocialMediaProduct).filter_by(
                        category=category
                    ).count()
                    category_stats[category] = count
            
            return {
                'total_posts': total_posts,
                'platform_breakdown': platform_stats,
                'category_breakdown': category_stats,
                'avg_engagement': session.query(SocialMediaProduct.engagement_score).all()
            }


def load_scraping_config() -> ScrapingConfig:
    """Load scraping configuration from environment variables."""
    return ScrapingConfig(
        reddit_client_id=os.getenv('REDDIT_CLIENT_ID'),
        reddit_client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        twitter_bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
        max_posts_per_subreddit=int(os.getenv('MAX_POSTS_PER_SUBREDDIT', '1000')),
        max_tweets=int(os.getenv('MAX_TWEETS', '5000')),
        delay_between_requests=float(os.getenv('SCRAPING_DELAY', '1.0'))
    )


def main():
    """Main function to run social media scraping."""
    print("🕷️  Social Media Scraping System")
    print("=" * 50)
    
    # Load configuration
    config = load_scraping_config()
    
    # Check if APIs are configured
    if not config.reddit_client_id:
        print("⚠️  Reddit API credentials not found!")
        print("   Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables")
        print("   Get credentials at: https://www.reddit.com/prefs/apps")
        return
    
    # Initialize scraper
    scraper = SocialMediaScraper(config)
    
    # Run scraping
    results = scraper.scrape_all_platforms()
    
    # Show statistics
    stats = scraper.get_scraping_stats()
    print(f"\n📊 Scraping Statistics:")
    print(f"   Total posts: {stats['total_posts']}")
    print(f"   Platform breakdown: {stats['platform_breakdown']}")
    print(f"   Top categories: {dict(list(stats['category_breakdown'].items())[:5])}")
    
    print("\n✅ Social media scraping completed!")


if __name__ == "__main__":
    main()
