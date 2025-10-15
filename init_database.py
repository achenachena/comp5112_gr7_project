#!/usr/bin/env python3
"""
Database Initialization Script

This script initializes the SQL database for the e-commerce search algorithm research project.
"""

import os
import sys
import logging
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import initialize_database, get_db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize the database for the research project."""
    print("🗄️ E-commerce Research Database Initialization")
    print("="*60)
    print()
    
    # Check for custom database URL
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"Using custom database: {database_url}")
    else:
        print("Using default SQLite database: data/ecommerce_research.db")
    
    print()
    
    try:
        # Initialize database
        print("Initializing database...")
        db_manager = initialize_database(database_url, reset=False)
        
        # Get database information
        print("\n📊 Database Information:")
        info = db_manager.get_database_info()
        
        print(f"  Type: {info['database_type']}")
        print(f"  Location: {info['database_url']}")
        print(f"  Tables Created: {info['tables_created']}")
        
        # Show current statistics
        if 'stats' in info:
            stats = info['stats']
            print(f"\n📈 Current Statistics:")
            print(f"  Products: {stats.get('products', 0)}")
            print(f"  Search Queries: {stats.get('search_queries', 0)}")
            print(f"  Search Results: {stats.get('search_results', 0)}")
            print(f"  Evaluation Metrics: {stats.get('evaluation_metrics', 0)}")
            print(f"  Collection Logs: {stats.get('collection_logs', 0)}")
            
            if stats.get('unique_sources'):
                print(f"  Data Sources: {stats['unique_sources']}")
            if stats.get('unique_categories'):
                print(f"  Categories: {stats['unique_categories']}")
        
        # Check database health
        print(f"\n🏥 Database Health Check:")
        health = db_manager.check_database_health()
        print(f"  Status: {health['status']}")
        print(f"  Connection: {'✅ OK' if health['connection_test'] else '❌ Failed'}")
        print(f"  Tables: {'✅ OK' if health['tables_exist'] else '❌ Missing'}")
        
        if health['status'] == 'healthy':
            print(f"\n✅ Database initialization successful!")
            print(f"\n🎯 Next steps:")
            print(f"1. Collect data:")
            print(f"   python collect_to_database.py")
            print(f"2. Run search evaluation:")
            print(f"   python run_database_search.py")
            print(f"3. Analyze results:")
            print(f"   python analyze_database_results.py")
        else:
            print(f"\n❌ Database initialization had issues")
            if 'error' in health:
                print(f"   Error: {health['error']}")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        print(f"\n❌ Error: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Check if you have write permissions in the project directory")
        print(f"2. Ensure SQLite is available (usually included with Python)")
        print(f"3. For PostgreSQL, ensure the database server is running")
        print(f"4. Check your DATABASE_URL environment variable")


if __name__ == "__main__":
    main()
