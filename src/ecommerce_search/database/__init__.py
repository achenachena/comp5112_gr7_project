"""
Database models and management
"""

from .db_manager import get_db_manager
from .models import Product, SearchQuery

__all__ = ['get_db_manager', 'Product', 'SearchQuery']
