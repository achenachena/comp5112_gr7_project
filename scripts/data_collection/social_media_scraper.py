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
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
except ImportError:
    # Fallback for older Python versions
    from multiprocessing.pool import ThreadPool as ThreadPoolExecutor
    from multiprocessing import as_completed

import threading

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually load .env file
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ecommerce_search.utils.product_extractor import ProductExtractor
from ecommerce_search.utils.base_scraper import BaseScraper, RedditScraperMixin
from ecommerce_search.utils.database_operations import DatabaseOperations
from ecommerce_search.config import ScrapingConfig as ScrapingConstants

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_subreddits_from_config(config_path: str = "config/subreddits.json") -> List[str]:
    """Load subreddit list from configuration file."""
    try:
        # Get absolute path relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_config_path = os.path.join(project_root, config_path)
        
        with open(full_config_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            subreddits = [sub['name'] for sub in config['subreddits']]
            logger.info("Loaded %d subreddits from %s", len(subreddits), config_path)
            return subreddits
    except FileNotFoundError:
        logger.warning("Config file %s not found. Using default subreddits.", config_path)
        return [
            'AskReddit', 'gaming', 'technology', 'BuyItForLife', 'ProductPorn',
            'deals', 'consumerism', 'gadgets', 'fashion', 'malefashionadvice',
            'homeimprovement', 'DIY', 'cooking', 'skincareaddiction', 'fitness'
        ]
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Error loading subreddits from config: %s", str(e))
        return [
            'AskReddit', 'gaming', 'technology', 'BuyItForLife', 'ProductPorn',
            'deals', 'consumerism', 'gadgets', 'fashion', 'malefashionadvice',
            'homeimprovement', 'DIY', 'cooking', 'skincareaddiction', 'fitness'
        ]

@dataclass
class ScrapingConfig:
    """Configuration for real social media scraping."""
    max_posts_per_platform: Dict[str, int]
    delay_range: tuple = None  # Will be loaded from config
    max_retries: int = None  # Will be loaded from config
    data_dir: str = "data"
    resume_from_checkpoint: bool = True
    max_workers: int = None  # Will be loaded from config
    batch_size: int = None  # Will be loaded from config
    rate_limit_respect: bool = True
    num_reddit_apps: int = None  # Will be loaded from config

    def __post_init__(self):
        """Load configuration values after initialization."""
        if self.delay_range is None:
            self.delay_range = ScrapingConstants.DEFAULT_DELAY_RANGE
        if self.max_retries is None:
            self.max_retries = ScrapingConstants.DEFAULT_MAX_RETRIES
        if self.max_workers is None:
            self.max_workers = ScrapingConstants.DEFAULT_MAX_WORKERS
        if self.batch_size is None:
            self.batch_size = ScrapingConstants.DEFAULT_BATCH_SIZE
        if self.num_reddit_apps is None:
            self.num_reddit_apps = ScrapingConstants.DEFAULT_NUM_REDDIT_APPS

class RealRedditScraper(BaseScraper, RedditScraperMixin):
    """Real Reddit scraper using PRAW API."""
    
    def __init__(self, config: ScrapingConfig):
        super().__init__(config)
        self.product_extractor = ProductExtractor()
        self.db_operations = DatabaseOperations()
        
        # Reddit API credentials (you need to get these)
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.reddit_user_agent = os.getenv(
            'REDDIT_USER_AGENT', 'EcommerceSearchBot/1.0'
        )
        
        if not all([self.reddit_client_id, self.reddit_client_secret]):
            logger.warning(
                "Reddit API credentials not found. Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET"
            )
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
        
        logger.info("Scraping r/%s for %d posts...", subreddit_name, max_posts)
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
                post_data.update(self.product_extractor.extract_product_info(post.title + " " + post.selftext))
                
                posts.append(post_data)
                self.scraped_ids.add(post.id)
                
                # Respect rate limits
                if self.config.rate_limit_respect:
                    time.sleep(random.uniform(*self.config.delay_range))
                
                if len(posts) >= max_posts:
                    break
                    
        except (AttributeError, KeyError) as e:
            logger.error("Error scraping r/%s: %s", subreddit_name, str(e))
        
        logger.info("Scraped %d posts from r/%s", len(posts), subreddit_name)
        return posts
    
class MultiAppRedditScraper(BaseScraper, RedditScraperMixin):
    """Reddit scraper that uses multiple API apps in parallel."""
    
    def __init__(self, config: ScrapingConfig):
        super().__init__(config)
        self.product_extractor = ProductExtractor()
        self.db_operations = DatabaseOperations()
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
                    logger.info(
                        "Reddit API %d initialized successfully", i
                    )
                except (ImportError, AttributeError) as e:
                    logger.error(
                        "Failed to initialize Reddit API %d: %s", i, str(e)
                    )
        
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
                except (AttributeError, KeyError) as e:
                    logger.error("Error in parallel scraping: %s", str(e))
        
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
                            'endpoint': endpoint_name,  # Track endpoint
                            'title': post.title,
                            'content': post.selftext,
                            'author': str(post.author),
                            'post_date': datetime.fromtimestamp(post.created_utc),
                            'upvotes': post.score,
                            'comments_count': post.num_comments,
                            'url': f"https://reddit.com{post.permalink}",
                            'created_at': datetime.utcnow()
                        }
                        
                        post_data.update(
                            self.product_extractor.extract_product_info(
                                post.title + " " + post.selftext
                            )
                        )
                        posts.append(post_data)
                        
                        if self.config.rate_limit_respect:
                            time.sleep(random.uniform(*self.config.delay_range))
                        
                        if len(posts) >= max_posts:
                            break
                            
                except (AttributeError, KeyError) as e:
                    logger.warning("Error with %s endpoint for r/%s: %s", endpoint_name, subreddit_name, str(e))
                    continue
                
                if len(posts) >= max_posts:
                    break
                    
        except (AttributeError, KeyError) as e:
            logger.error("Error scraping r/%s: %s", subreddit_name, str(e))
        
        return posts
    
    def scrape_subreddit(self, subreddit_name: str, max_posts: int = 100) -> List[Dict[str, Any]]:
        """Scrape subreddit using multiple Reddit apps in parallel."""
        return self.scrape_subreddit_parallel(subreddit_name, max_posts)

    def scrape_platform(self, max_posts: int) -> List[Dict[str, Any]]:
        """Scrape Reddit platform using multiple apps."""
        posts = []
        posts_per_subreddit = max_posts // len(self.config.subreddits) if hasattr(self.config, 'subreddits') else max_posts // 10

        for subreddit in getattr(self.config, 'subreddits', ['AskReddit', 'gaming', 'technology']):
            subreddit_posts = self.scrape_subreddit_parallel(subreddit, posts_per_subreddit)
            posts.extend(subreddit_posts)
            if len(posts) >= max_posts:
                break
        
        return posts[:max_posts]




class RealSocialMediaScraper(BaseScraper):
    """Main scraper for real social media data collection."""
    
    def __init__(self, config: ScrapingConfig):
        super().__init__(config)
        self.db_operations = DatabaseOperations()
        
        # Initialize Reddit scraper only
        self.reddit_scraper = MultiAppRedditScraper(config)
        
        # Load subreddits from configuration file
        self.subreddits = load_subreddits_from_config()
    
    def scrape_all_platforms(self) -> Dict[str, int]:
        """Scrape Reddit platform and return counts."""
        logger.info("Starting Reddit data collection...")
        
        results = {
            'reddit': 0
        }
        
        # Scrape Reddit
        if self.reddit_scraper.reddit_instances:
            logger.info(
                "Scraping Reddit with %d apps...", 
                len(self.reddit_scraper.reddit_instances)
            )
            reddit_posts = []
            
            posts_per_subreddit = (
                self.config.max_posts_per_platform['reddit'] // len(self.subreddits)
            )
            logger.info(
                "Optimized scraping: %d subreddits, %d posts each", 
                len(self.subreddits), posts_per_subreddit
            )
            logger.info(
                "Using multiple endpoints (hot, new, top) for maximum content coverage"
            )
            
            for subreddit in self.subreddits:
                logger.info(
                    "Scraping r/%s (%d posts via hot/new/top)", 
                    subreddit, posts_per_subreddit
                )
                posts = self.reddit_scraper.scrape_subreddit_parallel(subreddit, posts_per_subreddit)
                reddit_posts.extend(posts)
                
                # Save in batches
                if len(reddit_posts) >= self.config.batch_size:
                    self._save_posts(reddit_posts[-self.config.batch_size:], 'reddit')
                
                logger.info(
                    "Total collected: %d/%d", 
                    len(reddit_posts), 
                    self.config.max_posts_per_platform['reddit']
                )
            
            self._save_posts(reddit_posts, 'reddit')
            results['reddit'] = len(reddit_posts)
        
        # Only Reddit scraping - other platforms removed
        
        return results
    
    def _save_posts(self, posts: List[Dict[str, Any]], platform: str):
        """Save posts to database."""
        if not posts:
            return
        
        logger.info("Saving %d %s posts to database...", len(posts), platform)

        try:
            saved_count = self.db_operations.save_social_media_posts(posts, platform)
            logger.info("Successfully saved %d/%d %s posts", saved_count, len(posts), platform)

        except (ValueError, KeyError) as e:
            logger.error("Error saving %s posts: %s", platform, str(e))

    def scrape_platform(self, max_posts: int) -> List[Dict[str, Any]]:
        """Scrape Reddit platform and return posts."""
        results = self.scrape_all_platforms()
        all_posts = []

        # Reddit posts are already saved in scrape_all_platforms
        return all_posts[:max_posts]

def setup_api_credentials():
    """Guide user through setting up API credentials."""
    print("No Reddit API credentials found!")
    print("Setup: Create 3 Reddit apps at https://www.reddit.com/prefs/apps")
    print("Add to .env: REDDIT_CLIENT_ID_1, REDDIT_CLIENT_SECRET_1, etc.")
    print("See README.md for detailed instructions")

def main():
    """Main function for real social media scraping."""
    print("Reddit Data Collection")
    print("="*60)
    print("Collecting REAL data from Reddit")
    print()
    
    # Check for API credentials - Reddit apps only (flexible)
    reddit_credentials = []
    for i in range(1, 4):  # Check for 3 apps
        client_id = os.getenv(f'REDDIT_CLIENT_ID_{i}')
        client_secret = os.getenv(f'REDDIT_CLIENT_SECRET_{i}')
        if client_id and client_secret:
            reddit_credentials.append(f'REDDIT_APP_{i}')
    
    if not reddit_credentials:
        print("No Reddit API credentials found!")
        print()
        setup_api_credentials()
        return
    
    print(f"Found credentials for: {len(reddit_credentials)} Reddit apps")
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
    try:
        results = scraper.scrape_all_platforms()
        
        print("\nReal social media data collection complete!")
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
        
        with open('data/real_social_media_summary.json', 'w', encoding='utf-8') as summary_file:
            json.dump(summary, summary_file, indent=2)
    except KeyboardInterrupt:
        print("\nCollection stopped by user")
    except (ValueError, KeyError, OSError) as e:
        print(f"\nError during collection: {e}")

if __name__ == "__main__":
    main()
