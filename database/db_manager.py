"""
Database Manager for E-commerce Search Algorithm Research

This module provides database connection management, initialization,
and utility functions for the research project.
"""

import os
import logging
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from .models import Base, get_database_stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection URL. If None, uses default.
        """
        self.database_url = database_url or self._get_default_database_url()
        self.engine = None
        self.Session = None
        self._initialize_database()
    
    def _get_default_database_url(self) -> str:
        """Get default database URL from environment or use SQLite."""
        # Try PostgreSQL first (for production)
        postgres_url = os.getenv('DATABASE_URL')
        if postgres_url:
            logger.info("Using PostgreSQL database from DATABASE_URL")
            return postgres_url
        
        # Try SQLite (for development)
        sqlite_path = os.getenv('SQLITE_PATH', 'data/ecommerce_research.db')
        logger.info(f"Using SQLite database at: {sqlite_path}")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        
        return f"sqlite:///{sqlite_path}"
    
    def _initialize_database(self):
        """Initialize database engine and session factory."""
        try:
            self.engine = create_engine(
                self.database_url,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections every hour
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database connection initialized successfully")
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)."""
        try:
            Base.metadata.drop_all(self.engine)
            logger.warning("All database tables dropped")
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    def reset_database(self):
        """Reset database by dropping and recreating all tables."""
        logger.warning("Resetting database - all data will be lost!")
        self.drop_tables()
        self.create_tables()
        logger.info("Database reset complete")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database."""
        try:
            with self.get_session() as session:
                stats = get_database_stats(session)
                
                # Get database URL (masked for security)
                masked_url = self._mask_database_url(self.database_url)
                
                return {
                    'database_url': masked_url,
                    'database_type': self._get_database_type(),
                    'stats': stats,
                    'tables_created': len(Base.metadata.tables)
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {'error': str(e)}
    
    def _mask_database_url(self, url: str) -> str:
        """Mask sensitive information in database URL."""
        if '@' in url:
            # Mask password in URL
            parts = url.split('@')
            if len(parts) == 2:
                user_pass = parts[0].split('//')[-1]
                if ':' in user_pass:
                    user = user_pass.split(':')[0]
                    masked_url = url.replace(user_pass, f"{user}:***")
                    return masked_url
        return url
    
    def _get_database_type(self) -> str:
        """Get the type of database being used."""
        if self.database_url.startswith('postgresql'):
            return 'PostgreSQL'
        elif self.database_url.startswith('sqlite'):
            return 'SQLite'
        elif self.database_url.startswith('mysql'):
            return 'MySQL'
        else:
            return 'Unknown'
    
    def optimize_database(self):
        """Optimize database performance."""
        try:
            if self.database_url.startswith('sqlite'):
                # SQLite-specific optimizations
                with self.get_session() as session:
                    session.execute(text("PRAGMA journal_mode=WAL"))
                    session.execute(text("PRAGMA synchronous=NORMAL"))
                    session.execute(text("PRAGMA cache_size=10000"))
                    session.execute(text("PRAGMA temp_store=MEMORY"))
                    logger.info("SQLite database optimized")
            
            elif self.database_url.startswith('postgresql'):
                # PostgreSQL-specific optimizations
                with self.get_session() as session:
                    session.execute(text("VACUUM ANALYZE"))
                    logger.info("PostgreSQL database optimized")
            
        except Exception as e:
            logger.error(f"Failed to optimize database: {e}")
    
    def backup_database(self, backup_path: str):
        """Create a backup of the database."""
        try:
            if self.database_url.startswith('sqlite'):
                import shutil
                db_path = self.database_url.replace('sqlite:///', '')
                shutil.copy2(db_path, backup_path)
                logger.info(f"SQLite database backed up to: {backup_path}")
            
            else:
                logger.warning("Backup not implemented for this database type")
                
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
    
    def check_database_health(self) -> Dict[str, Any]:
        """Check database health and performance."""
        health_info = {
            'status': 'unknown',
            'connection_test': False,
            'tables_exist': False,
            'performance_metrics': {}
        }
        
        try:
            # Test connection
            with self.get_session() as session:
                result = session.execute(text("SELECT 1")).fetchone()
                health_info['connection_test'] = result[0] == 1
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            expected_tables = ['products', 'search_queries', 'search_results', 'evaluation_metrics']
            health_info['tables_exist'] = all(table in tables for table in expected_tables)
            
            # Get basic performance metrics
            with self.get_session() as session:
                stats = get_database_stats(session)
                health_info['performance_metrics'] = stats
            
            health_info['status'] = 'healthy' if health_info['connection_test'] and health_info['tables_exist'] else 'unhealthy'
            
        except Exception as e:
            health_info['status'] = 'error'
            health_info['error'] = str(e)
            logger.error(f"Database health check failed: {e}")
        
        return health_info


# Global database manager instance
db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager


def initialize_database(database_url: Optional[str] = None, reset: bool = False):
    """Initialize the database for the research project."""
    global db_manager
    
    db_manager = DatabaseManager(database_url)
    
    if reset:
        db_manager.reset_database()
    else:
        db_manager.create_tables()
    
    # Optimize database for performance
    db_manager.optimize_database()
    
    logger.info("Database initialized successfully")
    return db_manager


def get_session():
    """Get a database session using the global manager."""
    return get_db_manager().get_session()


if __name__ == "__main__":
    # Test database initialization
    try:
        db = initialize_database()
        
        # Print database info
        info = db.get_database_info()
        print("Database Information:")
        print(f"  Type: {info['database_type']}")
        print(f"  URL: {info['database_url']}")
        print(f"  Tables: {info['tables_created']}")
        
        # Print stats
        if 'stats' in info:
            stats = info['stats']
            print("\nDatabase Statistics:")
            for table, count in stats.items():
                if isinstance(count, dict):
                    print(f"  {table}:")
                    for key, value in count.items():
                        print(f"    {key}: {value}")
                else:
                    print(f"  {table}: {count}")
        
        # Check health
        health = db.check_database_health()
        print(f"\nDatabase Health: {health['status']}")
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
