"""
API Configuration Module

This module handles all API keys and configuration settings
from environment variables to keep sensitive data secure.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class APIConfig:
    """Centralized API configuration management."""
    
    # API Keys
    BESTBUY_API_KEY = os.getenv('BESTBUY_API_KEY')
    TARGET_API_KEY = os.getenv('TARGET_API_KEY')
    NEWEGG_API_KEY = os.getenv('NEWEGG_API_KEY')
    WALMART_API_KEY = os.getenv('WALMART_API_KEY')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/ecommerce_research.db')
    
    # Rate Limiting
    API_DELAY = float(os.getenv('API_DELAY', '1'))
    
    # Collection Limits
    MAX_PRODUCTS_PER_SOURCE = int(os.getenv('MAX_PRODUCTS_PER_SOURCE', '10000'))
    
    # Shopify Store Lists (loaded from environment variables for privacy)
    @classmethod
    def get_shopify_stores(cls):
        """Get Shopify stores from environment variable."""
        stores_env = os.getenv('SHOPIFY_STORES')
        if stores_env:
            # Split by comma and clean up URLs
            stores = [store.strip() for store in stores_env.split(',')]
            return [store for store in stores if store.startswith('http')]
        else:
            # Fallback to a minimal set for demo purposes
            return [
                'https://www.allbirds.com',
                'https://www.tentree.com',
                'https://colourpop.com',
                'https://www.brooklinen.com',
                'https://www.parachutehome.com',
                'https://www.nomadgoods.com',
                'https://www.ridge.com',
                'https://www.dollskill.com',
                'https://www.meshki.us',
                'https://www.beginningboutique.com'
            ]
    
    # Legacy property for backward compatibility
    @property
    def SHOPIFY_STORES(self):
        return self.get_shopify_stores()
    
    # All store URLs have been moved to environment variables for privacy
    # Add your store URLs to the .env file as SHOPIFY_STORES=url1,url2,url3...
    
    @classmethod
    def validate_api_keys(cls):
        """Validate that required API keys are present."""
        missing_keys = []
        
        if not cls.BESTBUY_API_KEY:
            missing_keys.append('BESTBUY_API_KEY')
        if not cls.WALMART_API_KEY:
            missing_keys.append('WALMART_API_KEY')
        if not cls.TARGET_API_KEY:
            missing_keys.append('TARGET_API_KEY')
        if not cls.NEWEGG_API_KEY:
            missing_keys.append('NEWEGG_API_KEY')
            
        return missing_keys
    
    @classmethod
    def get_api_info(cls):
        """Get information about available APIs."""
        return {
            'bestbuy': {
                'name': 'Best Buy API',
                'url': 'https://developer.bestbuy.com/',
                'description': 'Electronics, appliances, computers',
                'rate_limit': '5,000 requests/day',
                'has_key': bool(cls.BESTBUY_API_KEY)
            },
            'target': {
                'name': 'Target API',
                'url': 'https://developer.target.com/',
                'description': 'General merchandise, retail products',
                'rate_limit': 'Varies by endpoint',
                'has_key': bool(cls.TARGET_API_KEY)
            },
            'newegg': {
                'name': 'Newegg API',
                'url': 'https://developer.newegg.com/',
                'description': 'Tech products, gaming, electronics',
                'rate_limit': 'Limited',
                'has_key': bool(cls.NEWEGG_API_KEY)
            },
            'walmart': {
                'name': 'Walmart API',
                'url': 'https://developer.walmartlabs.com/',
                'description': 'General merchandise, electronics, groceries',
                'rate_limit': '5,000 requests/day',
                'has_key': bool(cls.WALMART_API_KEY)
            }
        }
