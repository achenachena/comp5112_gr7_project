"""
Database Operations Utilities

This module provides reusable database operations
to reduce code duplication across different modules.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from ..database.db_manager import get_db_manager
from ..database.models import SocialMediaProduct, Product


class DatabaseOperations:
    """Utility class for common database operations."""

    def __init__(self):
        """Initialize database operations."""
        self.db_manager = get_db_manager()
        self.logger = logging.getLogger(self.__class__.__name__)

    def save_social_media_posts(self, posts: List[Dict[str, Any]],
                               skip_duplicates: bool = True) -> Tuple[int, int]:
        """
        Save social media posts to database.

        Args:
            posts: List of post dictionaries
            skip_duplicates: Whether to skip duplicate posts

        Returns:
            Tuple of (saved_count, skipped_count)
        """
        if not posts:
            return 0, 0

        saved_count = 0
        skipped_count = 0

        try:
            with self.db_manager.get_session() as session:
                for post_data in posts:
                    try:
                        # Check for duplicates if requested
                        if skip_duplicates:
                            existing = session.query(SocialMediaProduct).filter_by(
                                post_id=post_data['post_id']
                            ).first()

                            if existing:
                                skipped_count += 1
                                continue

                        # Create product object
                        product = SocialMediaProduct(
                            post_id=post_data['post_id'],
                            platform=post_data['platform'],
                            subreddit=post_data.get('subreddit'),
                            hashtag=post_data.get('hashtag'),
                            title=post_data['title'],
                            content=post_data['content'],
                            author=post_data['author'],
                            post_date=post_data['post_date'],
                            upvotes=post_data['upvotes'],
                            comments_count=post_data['comments_count'],
                            url=post_data.get('url'),
                            created_at=post_data['created_at'],
                            # Product information
                            product_name=post_data.get('product_name'),
                            brand=post_data.get('brand'),
                            category=post_data.get('category'),
                            price_mentioned=post_data.get('price_mentioned'),
                            sentiment_score=post_data.get('sentiment_score', 0.0),
                            is_review=post_data.get('is_review', False),
                            is_recommendation=post_data.get('is_recommendation', False),
                            tags=post_data.get('tags')
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
                return saved_count, skipped_count

        except (ValueError, KeyError, TypeError) as e:
            self.logger.error("Error saving posts: %s", str(e))
            return 0, len(posts)

    def get_posts_count(self, platform: Optional[str] = None) -> int:
        """
        Get total count of social media posts.

        Args:
            platform: Optional platform filter

        Returns:
            Total count of posts
        """
        try:
            with self.db_manager.get_session() as session:
                query = session.query(SocialMediaProduct)
                if platform:
                    query = query.filter_by(platform=platform)
                return query.count()
        except (AttributeError, KeyError, ValueError) as e:
            self.logger.error("Error getting posts count: %s", str(e))
            return 0

    def get_products_count(self) -> int:
        """Get total count of e-commerce products."""
        try:
            with self.db_manager.get_session() as session:
                return session.query(Product).count()
        except (AttributeError, KeyError, ValueError) as e:
            self.logger.error("Error getting products count: %s", str(e))
            return 0

    def get_posts_by_platform(self, platform: str, limit: int = 100) -> List[SocialMediaProduct]:
        """
        Get posts by platform.

        Args:
            platform: Platform name
            limit: Maximum number of posts to return

        Returns:
            List of SocialMediaProduct objects
        """
        try:
            with self.db_manager.get_session() as session:
                return session.query(SocialMediaProduct).filter_by(
                    platform=platform
                ).limit(limit).all()
        except (AttributeError, KeyError, ValueError) as e:
            self.logger.error("Error getting posts by platform: %s", str(e))
            return []

    def get_posts_by_subreddit(self, subreddit: str, limit: int = 100) -> List[SocialMediaProduct]:
        """
        Get posts by subreddit.

        Args:
            subreddit: Subreddit name
            limit: Maximum number of posts to return

        Returns:
            List of SocialMediaProduct objects
        """
        try:
            with self.db_manager.get_session() as session:
                return session.query(SocialMediaProduct).filter_by(
                    subreddit=subreddit
                ).limit(limit).all()
        except (AttributeError, KeyError, ValueError) as e:
            self.logger.error("Error getting posts by subreddit: %s", str(e))
            return []

    def get_posts_with_products(self, limit: int = 100) -> List[SocialMediaProduct]:
        """
        Get posts that have product information.

        Args:
            limit: Maximum number of posts to return

        Returns:
            List of SocialMediaProduct objects with product information
        """
        try:
            with self.db_manager.get_session() as session:
                return session.query(SocialMediaProduct).filter(
                    SocialMediaProduct.product_name.isnot(None)
                ).limit(limit).all()
        except (AttributeError, KeyError, ValueError) as e:
            self.logger.error("Error getting posts with products: %s", str(e))
            return []

    def get_posts_by_category(self, category: str, limit: int = 100) -> List[SocialMediaProduct]:
        """
        Get posts by product category.

        Args:
            category: Product category
            limit: Maximum number of posts to return

        Returns:
            List of SocialMediaProduct objects
        """
        try:
            with self.db_manager.get_session() as session:
                return session.query(SocialMediaProduct).filter_by(
                    category=category
                ).limit(limit).all()
        except (AttributeError, KeyError, ValueError) as e:
            self.logger.error("Error getting posts by category: %s", str(e))
            return []

    def get_posts_by_brand(self, brand: str, limit: int = 100) -> List[SocialMediaProduct]:
        """
        Get posts by brand.

        Args:
            brand: Brand name
            limit: Maximum number of posts to return

        Returns:
            List of SocialMediaProduct objects
        """
        try:
            with self.db_manager.get_session() as session:
                return session.query(SocialMediaProduct).filter_by(
                    brand=brand
                ).limit(limit).all()
        except (AttributeError, KeyError, ValueError) as e:
            self.logger.error("Error getting posts by brand: %s", str(e))
            return []

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.

        Returns:
            Dictionary containing database statistics
        """
        try:
            with self.db_manager.get_session() as session:
                stats = {
                    'total_social_posts': session.query(SocialMediaProduct).count(),
                    'total_products': session.query(Product).count(),
                    'reddit_posts': session.query(SocialMediaProduct).filter_by(
                        platform='reddit'
                    ).count(),
                    'twitter_posts': session.query(SocialMediaProduct).filter_by(
                        platform='twitter'
                    ).count(),
                    'posts_with_products': session.query(SocialMediaProduct).filter(
                        SocialMediaProduct.product_name.isnot(None)
                    ).count(),
                    'posts_with_reviews': session.query(SocialMediaProduct).filter_by(
                        is_review=True
                    ).count(),
                    'posts_with_recommendations': session.query(SocialMediaProduct).filter_by(
                        is_recommendation=True
                    ).count(),
                }

                # Get category distribution
                category_stats = {}
                categories = session.query(SocialMediaProduct.category).filter(
                    SocialMediaProduct.category.isnot(None)
                ).distinct().all()

                for category in categories:
                    if category[0]:
                        count = session.query(SocialMediaProduct).filter_by(
                            category=category[0]
                        ).count()
                        category_stats[category[0]] = count

                stats['category_distribution'] = category_stats

                return stats

        except (AttributeError, KeyError, ValueError) as e:
            self.logger.error("Error getting database stats: %s", str(e))
            return {}

    def cleanup_old_posts(self, days_old: int = 30) -> int:
        """
        Clean up old posts from database.

        Args:
            days_old: Number of days old to consider for cleanup

        Returns:
            Number of posts deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)

            with self.db_manager.get_session() as session:
                old_posts = session.query(SocialMediaProduct).filter(
                    SocialMediaProduct.created_at < cutoff_date
                ).all()

                count = len(old_posts)
                for post in old_posts:
                    session.delete(post)

                session.commit()
                return count

        except (AttributeError, KeyError, ValueError) as e:
            self.logger.error("Error cleaning up old posts: %s", str(e))
            return 0
