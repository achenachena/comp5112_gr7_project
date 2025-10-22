"""
Base Scraper Classes

This module provides base classes for social media scrapers
to reduce code duplication and improve maintainability.
"""

import os
import time
import random
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

from ..database.db_manager import get_db_manager
from ..database.models import SocialMediaProduct
from .product_extractor import ProductExtractor

# Optional imports for platform-specific functionality
try:
    import praw
except ImportError:
    praw = None

try:
    import tweepy
except ImportError:
    tweepy = None


class BaseScraper(ABC):
    """Base class for social media scrapers."""

    def __init__(self, config):
        """Initialize the base scraper."""
        self.config = config
        self.db_manager = get_db_manager()
        self.product_extractor = ProductExtractor()
        self.scraped_ids: set = set()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def scrape_platform(self, max_posts: int) -> List[Dict[str, Any]]:
        """Scrape posts from the platform. Must be implemented by subclasses."""
        pass

    def save_posts(self, posts: List[Dict[str, Any]], platform: str) -> int:
        """
        Save posts to database with duplicate checking.

        Args:
            posts: List of post dictionaries
            platform: Platform name (e.g., 'reddit', 'twitter')

        Returns:
            Number of posts successfully saved
        """
        if not posts:
            return 0

        try:
            with self.db_manager.get_session() as session:
                saved_count = 0
                for post_data in posts:
                    try:
                        # Check if post already exists
                        existing = session.query(SocialMediaProduct).filter_by(
                            post_id=post_data['post_id']
                        ).first()

                        if existing:
                            continue  # Skip duplicates

                        # Extract product information
                        product_info = self.product_extractor.extract_product_info(
                            f"{post_data.get('title', '')} {post_data.get('content', '')}"
                        )

                        # Create product object
                        product = SocialMediaProduct(
                            post_id=post_data['post_id'],
                            platform=post_data['platform'],
                            subreddit=post_data.get('subreddit'),
                            title=post_data['title'],
                            content=post_data['content'],
                            author=post_data['author'],
                            post_date=post_data['post_date'],
                            upvotes=post_data['upvotes'],
                            comments_count=post_data['comments_count'],
                            url=post_data.get('url'),
                            created_at=post_data['created_at'],
                            # Product information
                            product_name=product_info['product_name'],
                            brand=product_info['brand'],
                            category=product_info['category'],
                            price_mentioned=product_info['price_mentioned'],
                            sentiment_score=product_info['sentiment_score'],
                            is_review=product_info['is_review'],
                            is_recommendation=product_info['is_recommendation'],
                            tags=','.join(product_info['tags']) if product_info['tags'] else None
                        )

                        session.add(product)
                        saved_count += 1

                    except (ValueError, KeyError, TypeError) as e:
                        self.logger.warning(
                            "Error saving post %s: %s", 
                            post_data.get('post_id', 'unknown'), str(e)
                        )
                        continue

                session.commit()
                return saved_count

        except (ValueError, KeyError, TypeError) as e:
            self.logger.error("Error saving posts: %s", str(e))
            return 0

    def apply_rate_limiting(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Apply rate limiting between requests."""
        if self.config.rate_limit_respect:
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)

    def log_progress(self, current: int, total: int, platform: str):
        """Log scraping progress."""
        percentage = (current / total) * 100 if total > 0 else 0
        self.logger.info(
            "Scraped %d/%d posts from %s (%.1f%%)", 
            current, total, platform, percentage
        )


class RedditScraperMixin:
    """Mixin class for Reddit-specific functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reddit_apis = []
        self._init_reddit_apis()

    def _init_reddit_apis(self):
        """Initialize Reddit API connections."""
        for i in range(1, 4):  # Support up to 3 Reddit apps
            client_id = os.getenv(f'REDDIT_CLIENT_ID_{i}')
            client_secret = os.getenv(f'REDDIT_CLIENT_SECRET_{i}')
            if client_id and client_secret:
                try:
                    if praw is None:
                        self.logger.error("PRAW not installed. Run: pip install praw")
                        break
                    reddit = praw.Reddit(
                        client_id=client_id,
                        client_secret=client_secret,
                        user_agent=os.getenv('REDDIT_USER_AGENT', 'EcommerceSearchBot/1.0')
                    )
                    self.reddit_apis.append(reddit)
                    self.logger.info("Reddit API %d initialized successfully", i)
                except (AttributeError, KeyError, ValueError) as e:
                    self.logger.warning("Failed to initialize Reddit API %d: %s", i, str(e))

        if not self.reddit_apis:
            self.logger.warning("No Reddit API credentials found")

    def get_reddit_api(self):
        """Get a random Reddit API instance for load balancing."""
        if not self.reddit_apis:
            raise RuntimeError("No Reddit APIs available")
        return random.choice(self.reddit_apis)

    def scrape_subreddit(self, subreddit_name: str, max_posts: int = 100) -> List[Dict[str, Any]]:
        """Scrape posts from a specific subreddit."""
        if not self.reddit_apis:
            self.logger.error("Reddit API not initialized")
            return []

        reddit_api = self.get_reddit_api()
        posts = []

        try:
            subreddit = reddit_api.subreddit(subreddit_name)

            # Try different endpoints for variety
            endpoints = [
                ('hot', subreddit.hot),
                ('new', subreddit.new),
                ('top', lambda limit: subreddit.top(limit=limit, time_filter='week'))
            ]

            posts_per_endpoint = max_posts // len(endpoints)

            for endpoint_name, endpoint_func in endpoints:
                try:
                    submissions = endpoint_func(limit=posts_per_endpoint)

                    for post in submissions:
                        try:
                            post_data = {
                                'post_id': f'reddit_{post.id}',
                                'platform': 'reddit',
                                'subreddit': subreddit_name,
                                'title': post.title,
                                'content': post.selftext,
                                'author': str(post.author) if post.author else 'Unknown',
                                'post_date': datetime.fromtimestamp(post.created_utc),
                                'upvotes': post.score,
                                'comments_count': post.num_comments,
                                'url': f"https://reddit.com{post.permalink}",
                                'created_at': datetime.now()
                            }
                            posts.append(post_data)

                        except (AttributeError, KeyError, ValueError) as e:
                            self.logger.warning(
                                "Error processing post: %s", str(e)
                            )
                            continue

                except (AttributeError, KeyError, ValueError) as e:
                    self.logger.warning(
                        "Error with %s endpoint for r/%s: %s", 
                        endpoint_name, subreddit_name, str(e)
                    )
                    continue

        except (AttributeError, KeyError, ValueError) as e:
            self.logger.error("Error accessing r/%s: %s", subreddit_name, str(e))

        return posts


class TwitterScraperMixin:
    """Mixin class for Twitter-specific functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.twitter_api = None
        self._init_twitter_api()

    def _init_twitter_api(self):
        """Initialize Twitter API connection."""
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not bearer_token:
            self.logger.warning("Twitter API credentials not found")
            return

        try:
            if tweepy is None:
                self.logger.error("Tweepy not installed. Run: pip install tweepy")
                return
            self.twitter_api = tweepy.Client(bearer_token=bearer_token)
            self.logger.info("Twitter API initialized successfully")
        except (AttributeError, KeyError, ValueError) as e:
            self.logger.error("Failed to initialize Twitter API: %s", str(e))

    def scrape_hashtags(self, hashtags: List[str], max_posts: int = 100) -> List[Dict[str, Any]]:
        """Scrape posts from Twitter hashtags."""
        if not self.twitter_api:
            self.logger.error("Twitter API not initialized")
            return []

        posts = []
        posts_per_hashtag = max_posts // len(hashtags) if hashtags else max_posts

        for hashtag in hashtags:
            try:
                tweets = self.twitter_api.search_recent_tweets(
                    query=f"#{hashtag}",
                    max_results=min(posts_per_hashtag, 100),
                    tweet_fields=['created_at', 'public_metrics', 'author_id']
                )

                if tweets.data:
                    for tweet in tweets.data:
                        try:
                            post_data = {
                                'post_id': f'twitter_{tweet.id}',
                                'platform': 'twitter',
                                'hashtag': hashtag,
                                'title': '',  # Twitter doesn't have titles
                                'content': tweet.text,
                                'author': str(tweet.author_id),
                                'post_date': tweet.created_at,
                                'upvotes': tweet.public_metrics.get('like_count', 0),
                                'comments_count': tweet.public_metrics.get('reply_count', 0),
                                'url': f"https://twitter.com/user/status/{tweet.id}",
                                'created_at': datetime.now()
                            }
                            posts.append(post_data)

                        except (AttributeError, KeyError, ValueError) as e:
                            self.logger.warning("Error processing tweet: %s", str(e))
                            continue

            except (AttributeError, KeyError, ValueError) as e:
                self.logger.warning("Error scraping hashtag #%s: %s", hashtag, str(e))
                continue

        return posts
