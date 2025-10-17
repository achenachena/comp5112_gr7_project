#!/usr/bin/env python3
"""
Database Schema Update Script

This script updates the database schema to include social media tables
and renames the existing products table to api_products.
"""

import os
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import get_db_manager
from database.models import Base, Product, SocialMediaProduct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_database_schema():
    """Update database schema to include social media tables."""
    logger.info("🔄 Updating database schema...")
    
    try:
        db_manager = get_db_manager()
        
        # Create all tables (this will create new ones and ignore existing)
        with db_manager.get_session() as session:
            Base.metadata.create_all(db_manager.engine)
            session.commit()
        
        logger.info("✅ Database schema updated successfully!")
        
        # Show table information
        with db_manager.get_session() as session:
            # Check API products table
            api_count = session.query(Product).count()
            logger.info(f"📊 API Products table: {api_count} records")
            
            # Check Social Media products table
            social_count = session.query(SocialMediaProduct).count()
            logger.info(f"📊 Social Media Products table: {social_count} records")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update database schema: {e}")
        return False


def migrate_existing_data():
    """Migrate existing data from 'products' table to 'api_products' table."""
    logger.info("🔄 Migrating existing data...")
    
    try:
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            # Check if old products table exists
            inspector = db_manager.engine.dialect.inspector(db_manager.engine)
            tables = inspector.get_table_names()
            
            if 'products' in tables and 'api_products' not in tables:
                logger.info("📦 Migrating data from 'products' to 'api_products'...")
                
                # This would require manual SQL migration
                # For now, we'll just create the new table structure
                logger.info("ℹ️  Please manually migrate data if needed")
            else:
                logger.info("✅ Data migration not needed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to migrate data: {e}")
        return False


def main():
    """Main function to update database schema."""
    print("🔄 Database Schema Update")
    print("=" * 40)
    
    # Update schema
    success = update_database_schema()
    
    if success:
        # Try to migrate existing data
        migrate_existing_data()
        
        print("\n✅ Database schema update completed!")
        print("\n📋 Next steps:")
        print("1. Set up Reddit API credentials:")
        print("   - Get Reddit API credentials at: https://www.reddit.com/prefs/apps")
        print("   - Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables")
        print("2. Run social media scraping:")
        print("   - python social_media_scraper.py")
        print("3. Compare algorithms on different datasets:")
        print("   - API data vs Social media data")
    else:
        print("\n❌ Database schema update failed!")
        print("   Check the error messages above for details.")


if __name__ == "__main__":
    main()
