#!/usr/bin/env python3
"""
Social Media Data Update Script

This script provides various options for updating existing social media data:
1. Add new data (incremental update)
2. Reprocess existing data with improved NLP
3. Clean and filter existing data
4. Update specific fields
"""

import sys
import os
import argparse
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ecommerce_search.database.db_manager import get_db_manager
from src.ecommerce_search.database.models import SocialMediaProduct
from src.ecommerce_search.utils.product_extractor import ProductExtractor
from src.ecommerce_search.utils.hybrid_product_extractor import HybridProductExtractor


def add_new_data(max_posts: int = 1000):
    """Add new social media data to the database."""
    print(f"Adding {max_posts} new social media posts...")
    
    # Import and run the scraper
    from scripts.data_collection.social_media_scraper import main as run_scraper
    
    # Modify the scraper to collect fewer posts
    original_config = None
    try:
        # This would require modifying the scraper config
        print("Running social media scraper for new data...")
        run_scraper()
    except Exception as e:
        print(f"Error running scraper: {e}")


def reprocess_existing_data():
    """Reprocess existing social media data with improved NLP."""
    print("Reprocessing existing social media data with improved NLP...")
    
    db_manager = get_db_manager()
    hybrid_extractor = HybridProductExtractor()
    
    updated_count = 0
    
    try:
        with db_manager.get_session() as session:
            # Get all social media products
            products = session.query(SocialMediaProduct).all()
            total_products = len(products)
            
            print(f"Found {total_products} social media products to reprocess...")
            
            for i, product in enumerate(products):
                if i % 100 == 0:
                    print(f"Processing {i}/{total_products} products...")
                
                # Combine title and content for reprocessing
                text = f"{product.title} {product.content or ''}"
                
                # Extract improved product information
                extracted_info = hybrid_extractor.extract_product_info(text)
                
                # Update product with improved information
                product.product_name = extracted_info.get('product_name')
                product.brand = extracted_info.get('brand')
                product.category = extracted_info.get('category')
                product.price_mentioned = extracted_info.get('price_mentioned')
                product.sentiment_score = extracted_info.get('sentiment_score')
                product.is_review = extracted_info.get('is_review', False)
                product.is_recommendation = extracted_info.get('is_recommendation', False)
                
                # Update tags
                tags = extracted_info.get('tags', [])
                if tags:
                    product.tags = ','.join(tags)
                
                updated_count += 1
            
            # Commit all changes
            session.commit()
            print(f"Successfully updated {updated_count} products with improved NLP extraction")
            
    except Exception as e:
        print(f"Error reprocessing data: {e}")


def clean_and_filter_data():
    """Clean and filter existing social media data."""
    print("Cleaning and filtering social media data...")
    
    db_manager = get_db_manager()
    
    try:
        with db_manager.get_session() as session:
            # Remove posts with very low engagement
            low_engagement = session.query(SocialMediaProduct).filter(
                SocialMediaProduct.upvotes < 1,
                SocialMediaProduct.comments_count < 1
            ).delete()
            
            # Remove posts with no content
            no_content = session.query(SocialMediaProduct).filter(
                SocialMediaProduct.content.is_(None) | 
                (SocialMediaProduct.content == '') |
                (SocialMediaProduct.title == '')
            ).delete()

            # Remove very old posts (older than 2 years)
            cutoff_date = datetime.now() - timedelta(days=730)
            old_posts = session.query(SocialMediaProduct).filter(
                SocialMediaProduct.post_date < cutoff_date
            ).delete()

            session.commit()

            print(f"Cleaned data:")
            print(f"  - Removed {low_engagement} low engagement posts")
            print(f"  - Removed {no_content} posts with no content")
            print(f"  - Removed {old_posts} very old posts")
            
    except Exception as e:
        print(f"Error cleaning data: {e}")


def update_specific_fields():
    """Update specific fields in existing data."""
    print("Updating specific fields in social media data...")
    
    db_manager = get_db_manager()
    
    try:
        with db_manager.get_session() as session:
            # Update engagement scores
            products = session.query(SocialMediaProduct).all()
            
            for product in products:
                # Calculate engagement score
                engagement_score = 0
                if product.upvotes:
                    engagement_score += product.upvotes * 0.5
                if product.comments_count:
                    engagement_score += product.comments_count * 0.3
                
                product.engagement_score = engagement_score
            
            session.commit()
            print(f"Updated engagement scores for {len(products)} products")
            
    except Exception as e:
        print(f"Error updating fields: {e}")


def show_database_stats():
    """Show current database statistics."""
    print("Current Social Media Database Statistics:")
    print("=" * 50)
    
    db_manager = get_db_manager()
    
    try:
        with db_manager.get_session() as session:
            # Total posts
            total_posts = session.query(SocialMediaProduct).count()
            print(f"Total posts: {total_posts:,}")
            
            # Posts by platform
            from sqlalchemy import func
            platforms = session.query(
                SocialMediaProduct.platform, 
                func.count(SocialMediaProduct.id)
            ).group_by(SocialMediaProduct.platform).all()
            
            print("\nPosts by platform:")
            for platform, count in platforms:
                print(f"  {platform}: {count:,}")
            
            # Posts by subreddit (top 10)
            subreddits = session.query(
                SocialMediaProduct.subreddit,
                func.count(SocialMediaProduct.id)
            ).group_by(SocialMediaProduct.subreddit).order_by(
                func.count(SocialMediaProduct.id).desc()
            ).limit(10).all()
            
            print("\nTop 10 subreddits:")
            for subreddit, count in subreddits:
                if subreddit:
                    print(f"  r/{subreddit}: {count:,}")
            
            # Posts with product information
            with_products = session.query(SocialMediaProduct).filter(
                SocialMediaProduct.product_name.isnot(None)
            ).count()
            
            with_brands = session.query(SocialMediaProduct).filter(
                SocialMediaProduct.brand.isnot(None)
            ).count()
            
            with_categories = session.query(SocialMediaProduct).filter(
                SocialMediaProduct.category.isnot(None)
            ).count()
            
            print(f"\nProduct information extraction:")
            print(f"  Posts with product names: {with_products:,}")
            print(f"  Posts with brands: {with_brands:,}")
            print(f"  Posts with categories: {with_categories:,}")
            
            # Recent posts
            recent_cutoff = datetime.now() - timedelta(days=7)
            recent_posts = session.query(SocialMediaProduct).filter(
                SocialMediaProduct.post_date >= recent_cutoff
            ).count()
            
            print(f"\nRecent activity:")
            print(f"  Posts from last 7 days: {recent_posts:,}")
            
    except Exception as e:
        print(f"Error getting database stats: {e}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Update social media data")
    parser.add_argument('action', choices=[
        'add_new', 'reprocess', 'clean', 'update_fields', 'stats'
    ], help='Action to perform')
    parser.add_argument('--max-posts', type=int, default=1000,
                       help='Maximum posts to add (for add_new action)')
    
    args = parser.parse_args()
    
    print("Social Media Data Update Tool")
    print("=" * 50)
    
    if args.action == 'add_new':
        add_new_data(args.max_posts)
    elif args.action == 'reprocess':
        reprocess_existing_data()
    elif args.action == 'clean':
        clean_and_filter_data()
    elif args.action == 'update_fields':
        update_specific_fields()
    elif args.action == 'stats':
        show_database_stats()
    
    print("\nUpdate complete!")


if __name__ == "__main__":
    main()
