"""
Configuration constants for E-commerce Search Project.

This module centralizes all magical numbers and configuration values
in a simple, maintainable way.
"""

# Database Configuration
class DatabaseConfig:
    """Database-related constants."""

    # String field lengths
    EXTERNAL_ID_LENGTH = 100
    SOURCE_LENGTH = 50
    BRAND_LENGTH = 100
    MODEL_LENGTH = 100
    SKU_LENGTH = 100
    PRICE_CURRENCY_LENGTH = 10
    CATEGORY_LENGTH = 100
    SUBCATEGORY_LENGTH = 100
    CONDITION_LENGTH = 50
    AVAILABILITY_LENGTH = 50
    SELLER_NAME_LENGTH = 100
    SELLER_LOCATION_LENGTH = 100

    # Social media field lengths
    POST_ID_LENGTH = 100
    PLATFORM_LENGTH = 50
    SUBREDDIT_LENGTH = 100
    AUTHOR_LENGTH = 100

    # Search query field lengths
    QUERY_TEXT_LENGTH = 500
    QUERY_CATEGORY_LENGTH = 100
    DIFFICULTY_LENGTH = 20

    # Collection log field lengths
    API_SOURCE_LENGTH = 50
    COLLECTION_QUERY_LENGTH = 500

    # Display truncation
    TITLE_TRUNCATE_LENGTH = 50
    PRODUCT_NAME_TRUNCATE_LENGTH = 30

    # Default values
    DEFAULT_UPVOTES = 0
    DEFAULT_DOWNVOTES = 0
    DEFAULT_COMMENTS_COUNT = 0
    DEFAULT_ENGAGEMENT_SCORE = 0.0
    DEFAULT_PRODUCTS_COLLECTED = 0
    DEFAULT_SUCCESSFUL_REQUESTS = 0
    DEFAULT_FAILED_REQUESTS = 0


# Algorithm Configuration
class AlgorithmConfig:
    """Search algorithm constants."""

    # Keyword matching
    DEFAULT_EXACT_MATCH_WEIGHT = 2.0
    DEFAULT_PARTIAL_MATCH_WEIGHT = 0.5
    DEFAULT_SEARCH_LIMIT = 10
    DEFAULT_CASE_SENSITIVE = False

    # TF-IDF
    DEFAULT_MAX_FEATURES = 1000
    DEFAULT_NGRAM_RANGE = (1, 2)
    DEFAULT_MIN_DF = 1
    DEFAULT_MAX_DF = 0.95

    # Evaluation
    DEFAULT_K_VALUES = [1, 3, 5, 10]
    MAX_K_VALUE = 10
    METRICS_TO_ANALYZE = ['map', 'mrr', 'f1@5', 'ndcg@10']
    TOP_RESULTS_STORAGE = 5

    # Default metric values
    DEFAULT_PRECISION = 0.0
    DEFAULT_RECALL = 0.0
    DEFAULT_F1 = 0.0
    DEFAULT_NDCG = 0.0
    DEFAULT_MAP = 0.0
    DEFAULT_MRR = 0.0


# Scraping Configuration
class ScrapingConfig:
    """Data collection constants."""

    # Rate limiting
    DEFAULT_DELAY_RANGE = (0.5, 1.5)  # seconds
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_TIMEOUT = 30  # seconds

    # Batch processing
    DEFAULT_BATCH_SIZE = 50
    DEFAULT_MAX_WORKERS = 3

    # Reddit configuration
    DEFAULT_NUM_REDDIT_APPS = 3
    DEFAULT_POSTS_PER_SUBREDDIT = 100
    DEFAULT_POSTS_PER_ENDPOINT_DIVISOR = 3  # Divide between hot, new, top
    DEFAULT_POSTS_PER_SUBREDDIT_DIVISOR = 10

    # Reddit-specific limits
    REDDIT_MAX_POSTS_PER_SUBREDDIT = 1000
    REDDIT_MAX_POSTS_PER_ENDPOINT = 100


# Web Application Configuration
class WebConfig:
    """Web application constants."""

    # Flask configuration
    DEFAULT_SECRET_KEY = 'dev-secret-key-change-in-production'
    DEFAULT_HOST = '127.0.0.1'
    DEFAULT_PORT = 5000
    DEFAULT_DEBUG = False

    # Production server
    GUNICORN_WORKERS = 4
    WAITRESS_HOST = '127.0.0.1'
    WAITRESS_PORT = 5000


# File and Path Configuration
class FileConfig:
    """File and path constants."""

    # Database files
    DATABASE_FILENAME = 'ecommerce_research.db'

    # Data directories
    DATA_DIR = 'data'
    CHECKPOINTS_DIR = 'data/checkpoints'
    EXPORTS_DIR = 'data/exports'
    RESULTS_DIR = 'data/results'

    # Configuration files
    ENV_TEMPLATE = 'env.template'
    SUBREDDITS_CONFIG = 'config/subreddits.json'

    # Output files
    SOCIAL_MEDIA_SUMMARY = 'data/real_social_media_summary.json'
    REAL_ECOMMERCE_PRODUCTS = 'data/real_ecommerce_products.json'
    REAL_ECOMMERCE_SUMMARY = 'data/real_ecommerce_summary.txt'


# API Configuration
class APIConfig:
    """API-related constants."""

    # User agents
    DEFAULT_USER_AGENT = 'EcommerceSearchBot/1.0'
    REDDIT_USER_AGENT = 'EcommerceSearchBot/1.0'

    # Reddit API endpoints (no external API endpoints needed)

    # Request headers
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }


# Environment Configuration
class EnvironmentConfig:
    """Environment variable names and defaults."""

    # Database
    DATABASE_URL = 'DATABASE_URL'
    DEFAULT_DATABASE_URL = 'sqlite:///data/ecommerce_research.db'

    # Flask
    SECRET_KEY = 'SECRET_KEY'
    FLASK_DEBUG = 'FLASK_DEBUG'

    # Reddit API
    REDDIT_CLIENT_ID = 'REDDIT_CLIENT_ID'
    REDDIT_CLIENT_SECRET = 'REDDIT_CLIENT_SECRET'
    REDDIT_USER_AGENT = 'REDDIT_USER_AGENT'

    # Only Reddit API credentials needed


# Default Values
class DefaultValues:
    """Default values for various operations."""

    # Currency
    DEFAULT_CURRENCY = 'USD'

    # Product condition
    DEFAULT_CONDITION = 'New'
    DEFAULT_AVAILABILITY = 'In Stock'

    # Sentiment range
    SENTIMENT_MIN = -1.0
    SENTIMENT_MAX = 1.0

    # Platform names
    PLATFORM_REDDIT = 'reddit'

    # Source names
    SOURCE_SHOPIFY_API = 'shopify_api'
    SOURCE_REDDIT = 'reddit'


# Validation Constants
class ValidationConfig:
    """Validation-related constants."""

    # Minimum values
    MIN_POSTS_PER_PLATFORM = 1
    MIN_DELAY_SECONDS = 0.1
    MIN_BATCH_SIZE = 1
    MIN_MAX_WORKERS = 1

    # Maximum values
    MAX_POSTS_PER_PLATFORM = 100000
    MAX_DELAY_SECONDS = 10.0
    MAX_BATCH_SIZE = 1000
    MAX_MAX_WORKERS = 20
    MAX_RETRIES = 10
    MAX_TIMEOUT = 300  # 5 minutes
