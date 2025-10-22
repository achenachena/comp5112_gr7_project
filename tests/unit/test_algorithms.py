"""
Unit tests for search algorithms
"""

import pytest
from ecommerce_search.algorithms import KeywordSearch, TFIDFSearch


class TestKeywordSearch:
    """Test cases for KeywordSearch algorithm."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.algorithm = KeywordSearch()
        self.test_products = [
            {
                'id': '1',
                'title': 'Blue Cotton T-Shirt',
                'description': 'Comfortable cotton t-shirt in blue color',
                'category': 'clothing',
                'price': {'value': '19.99', 'currency': 'USD'},
                'brand': 'TestBrand',
                'condition': 'new'
            },
            {
                'id': '2',
                'title': 'Red Wool Sweater',
                'description': 'Warm wool sweater in red color',
                'category': 'clothing',
                'price': {'value': '49.99', 'currency': 'USD'},
                'brand': 'TestBrand',
                'condition': 'new'
            }
        ]
    
    def test_search_basic(self):
        """Test basic search functionality."""
        results = self.algorithm.search('blue t-shirt', self.test_products, limit=5)
        
        assert len(results) > 0
        assert results[0]['id'] == '1'  # Blue t-shirt should be first
        assert results[0]['score'] > 0
    
    def test_search_no_results(self):
        """Test search with no matching results."""
        results = self.algorithm.search('nonexistent product', self.test_products, limit=5)
        assert len(results) == 0
    
    def test_search_limit(self):
        """Test search result limit."""
        results = self.algorithm.search('clothing', self.test_products, limit=1)
        assert len(results) <= 1


class TestTFIDFSearch:
    """Test cases for TFIDFSearch algorithm."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.algorithm = TFIDFSearch()
        self.test_products = [
            {
                'id': '1',
                'title': 'Blue Cotton T-Shirt',
                'description': 'Comfortable cotton t-shirt in blue color',
                'category': 'clothing',
                'price': {'value': '19.99', 'currency': 'USD'},
                'brand': 'TestBrand',
                'condition': 'new'
            },
            {
                'id': '2',
                'title': 'Red Wool Sweater',
                'description': 'Warm wool sweater in red color',
                'category': 'clothing',
                'price': {'value': '49.99', 'currency': 'USD'},
                'brand': 'TestBrand',
                'condition': 'new'
            }
        ]
    
    def test_search_basic(self):
        """Test basic search functionality."""
        results = self.algorithm.search('blue t-shirt', self.test_products, limit=5)
        
        assert len(results) > 0
        assert results[0]['id'] == '1'  # Blue t-shirt should be first
        assert results[0]['score'] > 0
    
    def test_search_no_results(self):
        """Test search with no matching results."""
        results = self.algorithm.search('nonexistent product', self.test_products, limit=5)
        assert len(results) == 0
    
    def test_search_limit(self):
        """Test search result limit."""
        results = self.algorithm.search('clothing', self.test_products, limit=1)
        assert len(results) <= 1
