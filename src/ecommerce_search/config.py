"""
Configuration management for E-commerce Search Algorithm Comparison
"""

import os


class Config:
    """Configuration class."""
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///data/ecommerce_research.db')
    
    # Algorithm configuration
    KEYWORD_MATCHING_CONFIG = {
        'case_sensitive': False,
        'exact_match_weight': 25.0
    }
    
    TFIDF_CONFIG = {
        'min_df': 2,
        'max_df': 0.6,
        'case_sensitive': False
    }
    
    # Web application configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Data configuration
    DEFAULT_PRODUCT_LIMIT = 1000
    MAX_PRODUCT_LIMIT = 10000


def get_config():
    """Get configuration."""
    return Config()