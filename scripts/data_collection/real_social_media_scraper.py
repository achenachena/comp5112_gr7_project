#!/usr/bin/env python3
"""
Real Social Media Scraper
Collects authentic data from Reddit, Twitter, Instagram, and TikTok
"""

import sys
import os
import json
import time
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually load .env file
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ecommerce_search.database.db_manager import get_db_manager
from ecommerce_search.database.models import SocialMediaProduct

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_subreddits_from_config(config_path: str = "config/subreddits.json") -> List[str]:
    """Load subreddit list from configuration file."""
    try:
        # Get absolute path relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_config_path = os.path.join(project_root, config_path)
        
        with open(full_config_path, 'r') as f:
            config = json.load(f)
            subreddits = [sub['name'] for sub in config['subreddits']]
            logger.info(f"Loaded {len(subreddits)} subreddits from {config_path}")
            return subreddits
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found. Using default subreddits.")
        return [
            'AskReddit', 'gaming', 'technology', 'BuyItForLife', 'ProductPorn',
            'deals', 'consumerism', 'gadgets', 'fashion', 'malefashionadvice',
            'homeimprovement', 'DIY', 'cooking', 'skincareaddiction', 'fitness'
        ]
    except Exception as e:
        logger.error(f"Error loading subreddits from config: {e}")
        return [
            'AskReddit', 'gaming', 'technology', 'BuyItForLife', 'ProductPorn',
            'deals', 'consumerism', 'gadgets', 'fashion', 'malefashionadvice',
            'homeimprovement', 'DIY', 'cooking', 'skincareaddiction', 'fitness'
        ]

@dataclass
class ScrapingConfig:
    """Configuration for real social media scraping."""
    max_posts_per_platform: Dict[str, int]
    delay_range: tuple = (0.5, 1.5)  # Balanced: faster but safe
    max_retries: int = 3
    data_dir: str = "data"
    resume_from_checkpoint: bool = True
    max_workers: int = 3  # One worker per Reddit app
    batch_size: int = 50  # Larger batches
    rate_limit_respect: bool = True
    num_reddit_apps: int = 3  # Number of Reddit apps available

class RealRedditScraper:
    """Real Reddit scraper using PRAW API."""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.db_manager = get_db_manager()
        self.scraped_ids: set = set()
        
        # Reddit API credentials (you need to get these)
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.reddit_user_agent = os.getenv('REDDIT_USER_AGENT', 'EcommerceSearchBot/1.0')
        
        if not all([self.reddit_client_id, self.reddit_client_secret]):
            logger.warning("Reddit API credentials not found. Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
            self.reddit = None
        else:
            try:
                import praw
                self.reddit = praw.Reddit(
                    client_id=self.reddit_client_id,
                    client_secret=self.reddit_client_secret,
                    user_agent=self.reddit_user_agent
                )
                logger.info("Reddit API initialized successfully")
            except ImportError:
                logger.error("PRAW not installed. Run: pip install praw")
                self.reddit = None
    
    def scrape_subreddit(self, subreddit_name: str, max_posts: int = 100) -> List[Dict[str, Any]]:
        """Scrape real posts from a subreddit."""
        if not self.reddit:
            logger.error("Reddit API not initialized")
            return []
        
        logger.info(f"Scraping r/{subreddit_name} for {max_posts} posts...")
        posts = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get hot posts
            for post in subreddit.hot(limit=max_posts):
                if post.id in self.scraped_ids:
                    continue
                
                post_data = {
                    'post_id': f"reddit_{post.id}",
                    'platform': 'reddit',
                    'subreddit': subreddit_name,
                    'title': post.title,
                    'content': post.selftext,
                    'author': str(post.author),
                    'post_date': datetime.fromtimestamp(post.created_utc),
                    'upvotes': post.score,
                    'downvotes': 0,  # Reddit doesn't provide downvotes
                    'comments_count': post.num_comments,
                    'url': f"https://reddit.com{post.permalink}",
                    'created_at': datetime.utcnow()
                }
                
                # Extract product information
                post_data.update(self._extract_product_info(post.title + " " + post.selftext))
                
                posts.append(post_data)
                self.scraped_ids.add(post.id)
                
                # Respect rate limits
                if self.config.rate_limit_respect:
                    time.sleep(random.uniform(*self.config.delay_range))
                
                if len(posts) >= max_posts:
                    break
                    
        except Exception as e:
            logger.error(f"Error scraping r/{subreddit_name}: {e}")
        
        logger.info(f"Scraped {len(posts)} posts from r/{subreddit_name}")
        return posts
    
    def _extract_product_info(self, text: str) -> Dict[str, Any]:
        """Advanced product information extraction using NLP techniques."""
        import re
        import string
        
        # Clean and normalize text
        text_lower = text.lower()
        
        # Enhanced product detection keywords
        product_keywords = [
            'product', 'review', 'recommend', 'buy', 'purchase', 'deal', 'sale',
            'upgrade', 'best', 'amazing', 'incredible', 'fantastic', 'love',
            'worth', 'value', 'quality', 'performance', 'experience'
        ]
        
        # Brand detection patterns
        brand_patterns = [
            r'\b(apple|samsung|sony|microsoft|google|amazon|nike|adidas|tesla|bmw|audi|mercedes)\b',
            r'\b(iphone|ipad|macbook|galaxy|pixel|surface|xbox|playstation|nintendo)\b',
            r'\b(airpods|beats|bose|jbl|sennheiser|audio-technica)\b',
            r'\b(nike|adidas|puma|under armour|lululemon|patagonia)\b'
        ]
        
        # Product category patterns
        category_patterns = {
            'electronics': ['phone', 'laptop', 'tablet', 'headphones', 'speaker', 'camera', 'gaming'],
            'clothing': ['shirt', 'dress', 'pants', 'shoes', 'jacket', 'sweater', 'jeans'],
            'beauty': ['skincare', 'makeup', 'sunscreen', 'moisturizer', 'serum', 'foundation'],
            'automotive': ['car', 'truck', 'suv', 'sedan', 'vehicle', 'automobile'],
            'home': ['furniture', 'appliance', 'kitchen', 'bedroom', 'living room'],
            'sports': ['fitness', 'gym', 'running', 'cycling', 'yoga', 'workout']
        }
        
        # Extract brands
        brands = []
        for pattern in brand_patterns:
            matches = re.findall(pattern, text_lower)
            brands.extend(matches)
        
        # Extract categories
        detected_category = None
        for category, keywords in category_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_category = category
                break
        
        # Enhanced price extraction
        price_patterns = [
            r'\$[\d,]+\.?\d*',
            r'USD\s*[\d,]+\.?\d*',
            r'USD[\d,]+\.?\d*',
            r'(\d+)\s*(dollars?|bucks?)',
            r'price[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text_lower)
            prices.extend(matches)
        
        # Clean and convert prices
        clean_prices = []
        for price in prices:
            if isinstance(price, tuple):
                price = price[0]
            clean_price = re.sub(r'[^\d.]', '', str(price))
            if clean_price and '.' in clean_price:
                try:
                    clean_prices.append(float(clean_price))
                except ValueError:
                    continue
        
        # Extract product name (improved)
        product_name = None
        if any(keyword in text_lower for keyword in product_keywords):
            # Try to extract meaningful product name
            sentences = re.split(r'[.!?]', text)
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in product_keywords):
                    # Clean up the sentence
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 10 and len(clean_sentence) < 100:
                        product_name = clean_sentence
                        break
        
        # Enhanced sentiment analysis
        positive_words = ['amazing', 'incredible', 'fantastic', 'love', 'best', 'excellent', 'perfect', 'great']
        negative_words = ['terrible', 'awful', 'hate', 'worst', 'bad', 'disappointed', 'poor']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment_score = 0.7 + (positive_count * 0.1)
        elif negative_count > positive_count:
            sentiment_score = 0.3 - (negative_count * 0.1)
        else:
            sentiment_score = 0.5
        
        # Determine if it's a review or recommendation
        is_review = any(keyword in text_lower for keyword in ['review', 'reviewed', 'tried', 'tested', 'used'])
        is_recommendation = any(keyword in text_lower for keyword in ['recommend', 'suggest', 'should', 'must', 'worth'])
        
        return {
            'product_name': product_name,
            'brand': brands[0] if brands else None,
            'category': detected_category or ('products' if any(keyword in text_lower for keyword in product_keywords) else None),
            'price_mentioned': max(clean_prices) if clean_prices else None,
            'price_currency': 'USD',
            'is_review': is_review,
            'is_recommendation': is_recommendation,
            'sentiment_score': min(max(sentiment_score, 0.0), 1.0),
            'tags': list(set(brands)) if brands else []
        }

class MultiAppRedditScraper:
    """Reddit scraper that uses multiple API apps in parallel."""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.db_manager = get_db_manager()
        self.scraped_ids = set()
        self.lock = threading.Lock()
        
        # Initialize multiple Reddit instances
        self.reddit_instances = []
        for i in range(1, config.num_reddit_apps + 1):
            client_id = os.getenv(f'REDDIT_CLIENT_ID_{i}')
            client_secret = os.getenv(f'REDDIT_CLIENT_SECRET_{i}')
            user_agent = os.getenv('REDDIT_USER_AGENT', 'EcommerceSearchBot/1.0')
            
            if client_id and client_secret:
                try:
                    import praw
                    reddit = praw.Reddit(
                        client_id=client_id,
                        client_secret=client_secret,
                        user_agent=user_agent
                    )
                    self.reddit_instances.append(reddit)
                    logger.info(f"Reddit API {i} initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Reddit API {i}: {e}")
        
        if not self.reddit_instances:
            logger.error("No Reddit API instances available")
    
    def scrape_subreddit_parallel(self, subreddit_name: str, max_posts: int) -> List[Dict[str, Any]]:
        """Scrape subreddit using multiple Reddit apps in parallel."""
        posts = []
        posts_per_app = max_posts // len(self.reddit_instances)
        
        with ThreadPoolExecutor(max_workers=len(self.reddit_instances)) as executor:
            futures = []
            for reddit_instance in self.reddit_instances:
                future = executor.submit(
                    self._scrape_with_instance,
                    reddit_instance,
                    subreddit_name,
                    posts_per_app
                )
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    posts.extend(result)
                except Exception as e:
                    logger.error(f"Error in parallel scraping: {e}")
        
        return posts
    
    def _scrape_with_instance(self, reddit, subreddit_name: str, max_posts: int) -> List[Dict[str, Any]]:
        """Scrape posts using a single Reddit instance with multiple endpoints."""
        posts = []
        posts_per_endpoint = max_posts // 3  # Divide between hot, new, top
        
        try:
            subreddit = reddit.subreddit(subreddit_name)
            
            # Try multiple endpoints to get more content
            endpoints = [
                ('hot', subreddit.hot),
                ('new', subreddit.new), 
                ('top', subreddit.top)
            ]
            
            for endpoint_name, endpoint_func in endpoints:
                try:
                    for post in endpoint_func(limit=posts_per_endpoint):
                        with self.lock:
                            if post.id in self.scraped_ids:
                                continue
                            self.scraped_ids.add(post.id)
                        
                        post_data = {
                            'post_id': f"reddit_{post.id}",
                            'platform': 'reddit',
                            'subreddit': subreddit_name,
                            'endpoint': endpoint_name,  # Track which endpoint
                            'title': post.title,
                            'content': post.selftext,
                            'author': str(post.author),
                            'post_date': datetime.fromtimestamp(post.created_utc),
                            'upvotes': post.score,
                            'comments_count': post.num_comments,
                            'url': f"https://reddit.com{post.permalink}",
                            'created_at': datetime.utcnow()
                        }
                        
                        post_data.update(self._extract_product_info(post.title + " " + post.selftext))
                        posts.append(post_data)
                        
                        if self.config.rate_limit_respect:
                            time.sleep(random.uniform(*self.config.delay_range))
                        
                        if len(posts) >= max_posts:
                            break
                            
                except Exception as e:
                    logger.warning(f"Error with {endpoint_name} endpoint for r/{subreddit_name}: {e}")
                    continue
                
                if len(posts) >= max_posts:
                    break
                    
        except Exception as e:
            logger.error(f"Error scraping r/{subreddit_name}: {e}")
        
        return posts
    
    def _extract_product_info(self, text: str) -> Dict[str, Any]:
        """Advanced product information extraction using NLP techniques."""
        import re
        import string
        
        # Clean and normalize text
        text_lower = text.lower()
        
        # Enhanced product detection keywords
        product_keywords = [
            'product', 'review', 'recommend', 'buy', 'purchase', 'deal', 'sale',
            'upgrade', 'best', 'amazing', 'incredible', 'fantastic', 'love',
            'worth', 'value', 'quality', 'performance', 'experience'
        ]
        
        # Brand detection patterns
        brand_patterns = [
            r'\b(apple|samsung|sony|microsoft|google|amazon|nike|adidas|tesla|bmw|audi|mercedes)\b',
            r'\b(iphone|ipad|macbook|galaxy|pixel|surface|xbox|playstation|nintendo)\b',
            r'\b(airpods|beats|bose|jbl|sennheiser|audio-technica)\b',
            r'\b(nike|adidas|puma|under armour|lululemon|patagonia)\b'
        ]
        
        # Product category patterns
        category_patterns = {
            'electronics': ['phone', 'laptop', 'tablet', 'headphones', 'speaker', 'camera', 'gaming'],
            'clothing': ['shirt', 'dress', 'pants', 'shoes', 'jacket', 'sweater', 'jeans'],
            'beauty': ['skincare', 'makeup', 'sunscreen', 'moisturizer', 'serum', 'foundation'],
            'automotive': ['car', 'truck', 'suv', 'sedan', 'vehicle', 'automobile'],
            'home': ['furniture', 'appliance', 'kitchen', 'bedroom', 'living room'],
            'sports': ['fitness', 'gym', 'running', 'cycling', 'yoga', 'workout']
        }
        
        # Extract brands
        brands = []
        for pattern in brand_patterns:
            matches = re.findall(pattern, text_lower)
            brands.extend(matches)
        
        # Extract categories
        detected_category = None
        for category, keywords in category_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_category = category
                break
        
        # Enhanced price extraction
        price_patterns = [
            r'\$[\d,]+\.?\d*',
            r'USD\s*[\d,]+\.?\d*',
            r'USD[\d,]+\.?\d*',
            r'(\d+)\s*(dollars?|bucks?)',
            r'price[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text_lower)
            prices.extend(matches)
        
        # Clean and convert prices
        clean_prices = []
        for price in prices:
            if isinstance(price, tuple):
                price = price[0]
            clean_price = re.sub(r'[^\d.]', '', str(price))
            if clean_price and '.' in clean_price:
                try:
                    clean_prices.append(float(clean_price))
                except ValueError:
                    continue
        
        # Extract product name (improved)
        product_name = None
        if any(keyword in text_lower for keyword in product_keywords):
            # Try to extract meaningful product name
            sentences = re.split(r'[.!?]', text)
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in product_keywords):
                    # Clean up the sentence
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 10 and len(clean_sentence) < 100:
                        product_name = clean_sentence
                        break
        
        # Enhanced sentiment analysis
        positive_words = ['amazing', 'incredible', 'fantastic', 'love', 'best', 'excellent', 'perfect', 'great']
        negative_words = ['terrible', 'awful', 'hate', 'worst', 'bad', 'disappointed', 'poor']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment_score = 0.7 + (positive_count * 0.1)
        elif negative_count > positive_count:
            sentiment_score = 0.3 - (negative_count * 0.1)
        else:
            sentiment_score = 0.5
        
        # Determine if it's a review or recommendation
        is_review = any(keyword in text_lower for keyword in ['review', 'reviewed', 'tried', 'tested', 'used'])
        is_recommendation = any(keyword in text_lower for keyword in ['recommend', 'suggest', 'should', 'must', 'worth'])
        
        return {
            'product_name': product_name,
            'brand': brands[0] if brands else None,
            'category': detected_category or ('products' if any(keyword in text_lower for keyword in product_keywords) else None),
            'price_mentioned': max(clean_prices) if clean_prices else None,
            'price_currency': 'USD',
            'is_review': is_review,
            'is_recommendation': is_recommendation,
            'sentiment_score': min(max(sentiment_score, 0.0), 1.0),
            'tags': list(set(brands)) if brands else []
        }

class RealTwitterScraper:
    """Real Twitter scraper using official API."""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.db_manager = get_db_manager()
        self.scraped_ids: set = set()
        
        # Twitter API credentials
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        if not self.bearer_token:
            logger.warning("Twitter API credentials not found. Please set TWITTER_BEARER_TOKEN")
            self.api_available = False
        else:
            self.api_available = True
            self.headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json'
            }
    
    def scrape_hashtag(self, hashtag: str, max_tweets: int = 100) -> List[Dict[str, Any]]:
        """Scrape real tweets with hashtag."""
        if not self.api_available:
            logger.error("Twitter API not available")
            return []
        
        logger.info(f"Scraping Twitter for #{hashtag} - {max_tweets} tweets...")
        tweets = []
        
        try:
            # Use Twitter API v2
            url = "https://api.twitter.com/2/tweets/search/recent"
            params = {
                'query': f'#{hashtag} -is:retweet lang:en',
                'max_results': min(max_tweets, 100),  # API limit
                'tweet.fields': 'created_at,public_metrics,author_id,text'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                for tweet in data.get('data', []):
                    if tweet['id'] in self.scraped_ids:
                        continue
                    
                    tweet_data = {
                        'post_id': f"twitter_{tweet['id']}",
                        'platform': 'twitter',
                        'title': tweet['text'][:200],
                        'content': tweet['text'],
                        'author': tweet.get('author_id', 'unknown'),
                        'post_date': datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00')),
                        'upvotes': tweet['public_metrics'].get('like_count', 0),
                        'comments_count': tweet['public_metrics'].get('reply_count', 0),
                        'url': f"https://twitter.com/user/status/{tweet['id']}",
                        'created_at': datetime.utcnow()
                    }
                    
                    # Extract product information
                    tweet_data.update(self._extract_product_info(tweet['text']))
                    
                    tweets.append(tweet_data)
                    self.scraped_ids.add(tweet['id'])
                    
                    # Respect rate limits
                    if self.config.rate_limit_respect:
                        time.sleep(random.uniform(*self.config.delay_range))
                        
            else:
                logger.error(f"Twitter API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error scraping Twitter #{hashtag}: {e}")
        
        logger.info(f"Scraped {len(tweets)} tweets for #{hashtag}")
        return tweets
    
    def _extract_product_info(self, text: str) -> Dict[str, Any]:
        """Advanced product information extraction using NLP techniques."""
        import re
        import string
        
        # Clean and normalize text
        text_lower = text.lower()
        
        # Enhanced product detection keywords
        product_keywords = [
            'product', 'review', 'recommend', 'buy', 'purchase', 'deal', 'sale',
            'upgrade', 'best', 'amazing', 'incredible', 'fantastic', 'love',
            'worth', 'value', 'quality', 'performance', 'experience'
        ]
        
        # Brand detection patterns
        brand_patterns = [
            r'\b(apple|samsung|sony|microsoft|google|amazon|nike|adidas|tesla|bmw|audi|mercedes)\b',
            r'\b(iphone|ipad|macbook|galaxy|pixel|surface|xbox|playstation|nintendo)\b',
            r'\b(airpods|beats|bose|jbl|sennheiser|audio-technica)\b',
            r'\b(nike|adidas|puma|under armour|lululemon|patagonia)\b'
        ]
        
        # Product category patterns
        category_patterns = {
            'electronics': ['phone', 'laptop', 'tablet', 'headphones', 'speaker', 'camera', 'gaming'],
            'clothing': ['shirt', 'dress', 'pants', 'shoes', 'jacket', 'sweater', 'jeans'],
            'beauty': ['skincare', 'makeup', 'sunscreen', 'moisturizer', 'serum', 'foundation'],
            'automotive': ['car', 'truck', 'suv', 'sedan', 'vehicle', 'automobile'],
            'home': ['furniture', 'appliance', 'kitchen', 'bedroom', 'living room'],
            'sports': ['fitness', 'gym', 'running', 'cycling', 'yoga', 'workout']
        }
        
        # Extract brands
        brands = []
        for pattern in brand_patterns:
            matches = re.findall(pattern, text_lower)
            brands.extend(matches)
        
        # Extract categories
        detected_category = None
        for category, keywords in category_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_category = category
                break
        
        # Enhanced price extraction
        price_patterns = [
            r'\$[\d,]+\.?\d*',
            r'USD\s*[\d,]+\.?\d*',
            r'USD[\d,]+\.?\d*',
            r'(\d+)\s*(dollars?|bucks?)',
            r'price[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text_lower)
            prices.extend(matches)
        
        # Clean and convert prices
        clean_prices = []
        for price in prices:
            if isinstance(price, tuple):
                price = price[0]
            clean_price = re.sub(r'[^\d.]', '', str(price))
            if clean_price and '.' in clean_price:
                try:
                    clean_prices.append(float(clean_price))
                except ValueError:
                    continue
        
        # Extract product name (improved)
        product_name = None
        if any(keyword in text_lower for keyword in product_keywords):
            # Try to extract meaningful product name
            sentences = re.split(r'[.!?]', text)
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in product_keywords):
                    # Clean up the sentence
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 10 and len(clean_sentence) < 100:
                        product_name = clean_sentence
                        break
        
        # Enhanced sentiment analysis
        positive_words = ['amazing', 'incredible', 'fantastic', 'love', 'best', 'excellent', 'perfect', 'great']
        negative_words = ['terrible', 'awful', 'hate', 'worst', 'bad', 'disappointed', 'poor']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment_score = 0.7 + (positive_count * 0.1)
        elif negative_count > positive_count:
            sentiment_score = 0.3 - (negative_count * 0.1)
        else:
            sentiment_score = 0.5
        
        # Determine if it's a review or recommendation
        is_review = any(keyword in text_lower for keyword in ['review', 'reviewed', 'tried', 'tested', 'used'])
        is_recommendation = any(keyword in text_lower for keyword in ['recommend', 'suggest', 'should', 'must', 'worth'])
        
        return {
            'product_name': product_name,
            'brand': brands[0] if brands else None,
            'category': detected_category or ('products' if any(keyword in text_lower for keyword in product_keywords) else None),
            'price_mentioned': max(clean_prices) if clean_prices else None,
            'price_currency': 'USD',
            'is_review': is_review,
            'is_recommendation': is_recommendation,
            'sentiment_score': min(max(sentiment_score, 0.0), 1.0),
            'tags': list(set(brands)) if brands else []
        }

class RealInstagramScraper:
    """Real Instagram scraper using official API."""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.db_manager = get_db_manager()
        self.scraped_ids: set = set()
        
        # Instagram API credentials
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        
        if not self.access_token:
            logger.warning("Instagram API credentials not found. Please set INSTAGRAM_ACCESS_TOKEN")
            self.api_available = False
        else:
            self.api_available = True
    
    def scrape_hashtag(self, hashtag: str, max_posts: int = 100) -> List[Dict[str, Any]]:
        """Scrape real Instagram posts with hashtag."""
        if not self.api_available:
            logger.error("Instagram API not available")
            return []
        
        logger.info(f"Scraping Instagram for #{hashtag} - {max_posts} posts...")
        posts = []
        
        try:
            # Use Instagram Basic Display API
            url = f"https://graph.instagram.com/v18.0/me/media"
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
                'access_token': self.access_token,
                'limit': min(max_posts, 25)  # API limit
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                for post in data.get('data', []):
                    if post['id'] in self.scraped_ids:
                        continue
                    
                    post_data = {
                        'post_id': f"instagram_{post['id']}",
                        'platform': 'instagram',
                        'title': post.get('caption', '')[:200] if post.get('caption') else '',
                        'content': post.get('caption', ''),
                        'author': 'instagram_user',  # API doesn't provide author info
                        'post_date': datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00')),
                        'upvotes': post.get('like_count', 0),
                        'comments_count': post.get('comments_count', 0),
                        'url': post.get('permalink', ''),
                        'image_url': post.get('media_url', ''),
                        'created_at': datetime.utcnow()
                    }
                    
                    # Extract product information
                    post_data.update(self._extract_product_info(post.get('caption', '')))
                    
                    posts.append(post_data)
                    self.scraped_ids.add(post['id'])
                    
                    # Respect rate limits
                    if self.config.rate_limit_respect:
                        time.sleep(random.uniform(*self.config.delay_range))
                        
            else:
                logger.error(f"Instagram API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error scraping Instagram #{hashtag}: {e}")
        
        logger.info(f"Scraped {len(posts)} posts for #{hashtag}")
        return posts
    
    def _extract_product_info(self, text: str) -> Dict[str, Any]:
        """Advanced product information extraction using NLP techniques."""
        if not text:
            return {}
            
        import re
        import string
        
        # Clean and normalize text
        text_lower = text.lower()
        
        # Enhanced product detection keywords
        product_keywords = [
            'product', 'review', 'recommend', 'buy', 'purchase', 'deal', 'sale',
            'upgrade', 'best', 'amazing', 'incredible', 'fantastic', 'love',
            'worth', 'value', 'quality', 'performance', 'experience', 'obsessed'
        ]
        
        # Brand detection patterns
        brand_patterns = [
            r'\b(apple|samsung|sony|microsoft|google|amazon|nike|adidas|tesla|bmw|audi|mercedes)\b',
            r'\b(iphone|ipad|macbook|galaxy|pixel|surface|xbox|playstation|nintendo)\b',
            r'\b(airpods|beats|bose|jbl|sennheiser|audio-technica)\b',
            r'\b(nike|adidas|puma|under armour|lululemon|patagonia)\b'
        ]
        
        # Product category patterns
        category_patterns = {
            'electronics': ['phone', 'laptop', 'tablet', 'headphones', 'speaker', 'camera', 'gaming'],
            'clothing': ['shirt', 'dress', 'pants', 'shoes', 'jacket', 'sweater', 'jeans'],
            'beauty': ['skincare', 'makeup', 'sunscreen', 'moisturizer', 'serum', 'foundation'],
            'automotive': ['car', 'truck', 'suv', 'sedan', 'vehicle', 'automobile'],
            'home': ['furniture', 'appliance', 'kitchen', 'bedroom', 'living room'],
            'sports': ['fitness', 'gym', 'running', 'cycling', 'yoga', 'workout']
        }
        
        # Extract brands
        brands = []
        for pattern in brand_patterns:
            matches = re.findall(pattern, text_lower)
            brands.extend(matches)
        
        # Extract categories
        detected_category = None
        for category, keywords in category_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_category = category
                break
        
        # Enhanced price extraction
        price_patterns = [
            r'\$[\d,]+\.?\d*',
            r'USD\s*[\d,]+\.?\d*',
            r'USD[\d,]+\.?\d*',
            r'(\d+)\s*(dollars?|bucks?)',
            r'price[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text_lower)
            prices.extend(matches)
        
        # Clean and convert prices
        clean_prices = []
        for price in prices:
            if isinstance(price, tuple):
                price = price[0]
            clean_price = re.sub(r'[^\d.]', '', str(price))
            if clean_price and '.' in clean_price:
                try:
                    clean_prices.append(float(clean_price))
                except ValueError:
                    continue
        
        # Extract product name (improved)
        product_name = None
        if any(keyword in text_lower for keyword in product_keywords):
            # Try to extract meaningful product name
            sentences = re.split(r'[.!?]', text)
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in product_keywords):
                    # Clean up the sentence
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 10 and len(clean_sentence) < 100:
                        product_name = clean_sentence
                        break
        
        # Enhanced sentiment analysis
        positive_words = ['amazing', 'incredible', 'fantastic', 'love', 'best', 'excellent', 'perfect', 'great', 'obsessed']
        negative_words = ['terrible', 'awful', 'hate', 'worst', 'bad', 'disappointed', 'poor']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment_score = 0.8 + (positive_count * 0.1)  # Instagram tends to be more positive
        elif negative_count > positive_count:
            sentiment_score = 0.3 - (negative_count * 0.1)
        else:
            sentiment_score = 0.6  # Default higher for Instagram
        
        # Determine if it's a review or recommendation
        is_review = any(keyword in text_lower for keyword in ['review', 'reviewed', 'tried', 'tested', 'used'])
        is_recommendation = any(keyword in text_lower for keyword in ['recommend', 'suggest', 'should', 'must', 'worth'])
        
        return {
            'product_name': product_name,
            'brand': brands[0] if brands else None,
            'category': detected_category or ('products' if any(keyword in text_lower for keyword in product_keywords) else None),
            'price_mentioned': max(clean_prices) if clean_prices else None,
            'price_currency': 'USD',
            'is_review': is_review,
            'is_recommendation': is_recommendation,
            'sentiment_score': min(max(sentiment_score, 0.0), 1.0),
            'tags': list(set(brands)) if brands else []
        }

class RealTikTokScraper:
    """Real TikTok scraper using web scraping."""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.db_manager = get_db_manager()
        self.scraped_ids: set = set()
        
        # TikTok scraping is more complex and may require browser automation
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            self.selenium_available = True
        except ImportError:
            logger.warning("Selenium not installed. TikTok scraping will be limited.")
            self.selenium_available = False
    
    def scrape_hashtag(self, hashtag: str, max_posts: int = 100) -> List[Dict[str, Any]]:
        """Scrape real TikTok posts with hashtag."""
        logger.info(f"Scraping TikTok for #{hashtag} - {max_posts} posts...")
        posts = []
        
        # TikTok scraping is complex and may require browser automation
        # For now, we'll create a placeholder that explains the requirements
        logger.warning("TikTok scraping requires browser automation and may be rate-limited")
        logger.info("Consider using TikTok Research API for academic purposes")
        
        # Placeholder implementation
        for i in range(min(max_posts, 10)):  # Limited for demo
            post_data = {
                'post_id': f"tiktok_placeholder_{i}",
                'platform': 'tiktok',
                'title': f'TikTok video about {hashtag}',
                'content': f'This is a placeholder for TikTok content about {hashtag}',
                'author': 'tiktok_user',
                'post_date': datetime.utcnow(),
                'upvotes': random.randint(10, 1000),
                'comments_count': random.randint(0, 100),
                'url': f'https://tiktok.com/@{hashtag}/video/{i}',
                'created_at': datetime.utcnow(),
                'product_name': f'Product related to {hashtag}',
                'category': 'products',
                'is_review': True,
                'is_recommendation': True,
                'sentiment_score': 0.7
            }
            posts.append(post_data)
            
            if self.config.rate_limit_respect:
                time.sleep(random.uniform(*self.config.delay_range))
        
        logger.info(f"Created {len(posts)} placeholder TikTok posts for #{hashtag}")
        return posts

class RealSocialMediaScraper:
    """Main scraper for real social media data collection."""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.db_manager = get_db_manager()
        
        # Initialize scrapers
        self.reddit_scraper = MultiAppRedditScraper(config)
        self.twitter_scraper = RealTwitterScraper(config)
        self.instagram_scraper = RealInstagramScraper(config)
        self.tiktok_scraper = RealTikTokScraper(config)
        
        # Target subreddits and hashtags
        # Load subreddits from configuration file
        self.subreddits = load_subreddits_from_config()
        
        self.hashtags = [
            'productreview', 'recommendation', 'amazingproduct', 'worthit',
            'bestpurchase', 'incredible', 'fantastic', 'loveit',
            'gamechanger', 'musthave', 'perfect', 'excellent',
            'greatvalue', 'toprated', 'customerfavorite', 'bestseller'
        ]
    
    def scrape_all_platforms(self) -> Dict[str, int]:
        """Scrape all platforms and return counts."""
        logger.info("Starting real social media data collection...")
        
        results = {
            'reddit': 0,
            'twitter': 0
        }
        
        # Scrape Reddit
        if self.reddit_scraper.reddit_instances:
            logger.info(f"Scraping Reddit with {len(self.reddit_scraper.reddit_instances)} apps...")
            reddit_posts = []
            
            posts_per_subreddit = self.config.max_posts_per_platform['reddit'] // len(self.subreddits)
            logger.info(f"Optimized scraping: {len(self.subreddits)} subreddits, {posts_per_subreddit} posts each")
            logger.info(f"Using multiple endpoints (hot, new, top) for maximum content coverage")
            
            for subreddit in self.subreddits:
                logger.info(f"Scraping r/{subreddit} ({posts_per_subreddit} posts via hot/new/top)")
                posts = self.reddit_scraper.scrape_subreddit_parallel(subreddit, posts_per_subreddit)
                reddit_posts.extend(posts)
                
                # Save in batches
                if len(reddit_posts) >= self.config.batch_size:
                    self._save_posts(reddit_posts[-self.config.batch_size:], 'reddit')
                
                logger.info(f"Total collected: {len(reddit_posts)}/{self.config.max_posts_per_platform['reddit']}")
            
            self._save_posts(reddit_posts, 'reddit')
            results['reddit'] = len(reddit_posts)
        
        # Scrape Twitter
        if self.twitter_scraper.api_available:
            logger.info("Scraping Twitter...")
            twitter_posts = []
            for hashtag in self.hashtags[:5]:  # Limit for demo
                posts = self.twitter_scraper.scrape_hashtag(
                    hashtag,
                    self.config.max_posts_per_platform['twitter'] // 5
                )
                twitter_posts.extend(posts)
                time.sleep(5)  # Be respectful
            
            self._save_posts(twitter_posts, 'twitter')
            results['twitter'] = len(twitter_posts)
        
        # Instagram and TikTok removed - focusing on Reddit and Twitter only
        
        return results
    
    def _save_posts(self, posts: List[Dict[str, Any]], platform: str):
        """Save posts to database."""
        if not posts:
            return
        
        logger.info(f"Saving {len(posts)} {platform} posts to database...")
        
        try:
            with self.db_manager.get_session() as session:
                saved_count = 0
                for post_data in posts:
                    # Check if post already exists
                    existing = session.query(SocialMediaProduct).filter_by(
                        post_id=post_data['post_id']
                    ).first()
                    
                    if existing:
                        continue  # Skip duplicate posts
                    
                    # Create SocialMediaProduct instance
                    product = SocialMediaProduct(
                        post_id=post_data['post_id'],
                        platform=post_data['platform'],
                        subreddit=post_data.get('subreddit'),
                        title=post_data['title'],
                        content=post_data['content'],
                        author=post_data['author'],
                        post_date=post_data['post_date'],
                        upvotes=post_data['upvotes'],
                        downvotes=post_data.get('downvotes', 0),
                        comments_count=post_data['comments_count'],
                        url=post_data.get('url'),
                        image_url=post_data.get('image_url'),
                        product_name=post_data.get('product_name'),
                        brand=post_data.get('brand'),
                        category=post_data.get('category'),
                        price_mentioned=post_data.get('price_mentioned'),
                        price_currency=post_data.get('price_currency', 'USD'),
                        tags=json.dumps(post_data.get('tags', [])),
                        is_review=post_data.get('is_review', False),
                        is_recommendation=post_data.get('is_recommendation', False),
                        sentiment_score=post_data.get('sentiment_score', 0.0)
                    )
                    
                    session.add(product)
                    saved_count += 1
                
                session.commit()
                logger.info(f"Successfully saved {saved_count}/{len(posts)} {platform} posts")
                
        except Exception as e:
            logger.error(f"Error saving {platform} posts: {e}")

def setup_api_credentials():
    """Guide user through setting up API credentials."""
    print("🔑 Real Social Media API Setup Guide")
    print("="*50)
    print()
    print("To collect REAL social media data, you need API credentials:")
    print()
    
    apis = [
        {
            'name': 'Reddit API (3 Apps)',
            'url': 'https://www.reddit.com/prefs/apps',
            'description': 'Reddit posts and comments using 3 parallel apps',
            'credentials': ['REDDIT_CLIENT_ID_1', 'REDDIT_CLIENT_SECRET_1', 'REDDIT_CLIENT_ID_2', 'REDDIT_CLIENT_SECRET_2', 'REDDIT_CLIENT_ID_3', 'REDDIT_CLIENT_SECRET_3', 'REDDIT_USER_AGENT'],
            'difficulty': 'Easy',
            'recommended': '⭐ BEST OPTION'
        }
    ]
    
    for api in apis:
        print(f"📌 {api['name']} {api['recommended']}")
        print(f"   URL: {api['url']}")
        print(f"   Description: {api['description']}")
        print(f"   Credentials: {', '.join(api['credentials'])}")
        print(f"   Difficulty: {api['difficulty']}")
        print()
    
    print("📝 Setup Instructions:")
    print("1. Create 3 Reddit apps at https://www.reddit.com/prefs/apps")
    print("2. Create .env file in your project root")
    print("3. Add your 3 Reddit app credentials:")
    print("   REDDIT_CLIENT_ID_1=your_first_app_id")
    print("   REDDIT_CLIENT_SECRET_1=your_first_app_secret")
    print("   REDDIT_CLIENT_ID_2=your_second_app_id")
    print("   REDDIT_CLIENT_SECRET_2=your_second_app_secret")
    print("   REDDIT_CLIENT_ID_3=your_third_app_id")
    print("   REDDIT_CLIENT_SECRET_3=your_third_app_secret")
    print("   REDDIT_USER_AGENT=EcommerceSearchBot/1.0")
    print("4. Run: python scripts/real_social_media_scraper.py")
    print()
    print("💡 RECOMMENDATION: Use 3 Reddit apps for 3x faster collection!")

def main():
    """Main function for real social media scraping."""
    print("🌐 Real Social Media Data Collection")
    print("="*60)
    print("Collecting REAL data from social media platforms")
    print()
    
    # Check for API credentials - Reddit apps only (flexible)
    reddit_credentials = []
    for i in range(1, 4):  # Check for 3 apps
        client_id = os.getenv(f'REDDIT_CLIENT_ID_{i}')
        client_secret = os.getenv(f'REDDIT_CLIENT_SECRET_{i}')
        if client_id and client_secret:
            reddit_credentials.append(f'REDDIT_APP_{i}')
    
    if not reddit_credentials:
        print("❌ No Reddit API credentials found!")
        print()
        setup_api_credentials()
        return
    
    print(f"✅ Found credentials for: {len(reddit_credentials)} Reddit apps")
    print()
    
    # Configuration - Reddit only with available apps for 50,000 posts
    num_apps = len(reddit_credentials)
    config = ScrapingConfig(
        max_posts_per_platform={
            'reddit': 50000
        },
        delay_range=(0.5, 1.5),  # Balanced delays
        max_workers=num_apps,    # One per Reddit app
        batch_size=50,          # Larger batches
        num_reddit_apps=num_apps # Number of Reddit apps available
    )
    
    # Initialize scraper
    scraper = RealSocialMediaScraper(config)
    
    # Start scraping
    print("🚀 Starting real social media data collection...")
    print("This may take several hours due to rate limiting...")
    print()
    
    try:
        results = scraper.scrape_all_platforms()
        
        print("\n🎉 Real social media data collection complete!")
        print("="*50)
        for platform, count in results.items():
            print(f"{platform.title()}: {count} posts")
        
        total = sum(results.values())
        print(f"\nTotal posts collected: {total}")
        
        # Save summary
        summary = {
            'total_posts': total,
            'platforms': results,
            'collection_date': datetime.now().isoformat(),
            'data_type': 'real_social_media'
        }
        
        with open('data/real_social_media_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Summary saved to: data/real_social_media_summary.json")
        print("\n🎯 Next steps:")
        print("1. Check database for new data:")
        print("   python src/ecommerce_search/cli.py db stats")
        print("2. Test search with social media dataset:")
        print("   python src/ecommerce_search/cli.py search 'amazing product' --dataset social")
        print("3. Run algorithm comparison:")
        print("   python src/ecommerce_search/cli.py compare --dataset social")
        
    except KeyboardInterrupt:
        print("\n⏹️ Collection stopped by user")
        print("Data collected so far has been saved to database")
    except Exception as e:
        print(f"\n❌ Error during collection: {e}")
        print("Check your API credentials and try again")

if __name__ == "__main__":
    main()
