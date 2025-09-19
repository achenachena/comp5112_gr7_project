"""
eBay API Client for collecting product data.
Supports searching products and retrieving JSON results.
"""

import os
import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Product:
    """Data class for product information."""
    item_id: str
    title: str
    price: Dict[str, str]
    item_href: str
    image_url: Optional[str] = None
    condition: Optional[str] = None
    seller: Optional[Dict[str, str]] = None
    shipping_cost: Optional[Dict[str, str]] = None
    location: Optional[str] = None


class EbayAPIClient:
    """Client for interacting with eBay's Browse API."""
    
    def __init__(self):
        """Initialize the eBay API client with credentials from environment variables."""
        self.app_id = os.getenv('EBAY_APP_ID')
        self.client_id = os.getenv('EBAY_CLIENT_ID')
        self.client_secret = os.getenv('EBAY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('EBAY_REDIRECT_URI')
        self.oauth_token = os.getenv('EBAY_OAUTH_TOKEN')
        self.environment = os.getenv('EBAY_ENVIRONMENT', 'sandbox')
        
        # Set base URL based on environment
        if self.environment == 'sandbox':
            self.base_url = 'https://api.sandbox.ebay.com'
        else:
            self.base_url = 'https://api.ebay.com'
        
        self.browse_api_url = f"{self.base_url}/buy/browse/v1"
        
        # Validate required credentials
        if not self.oauth_token:
            print("Warning: EBAY_OAUTH_TOKEN not found in environment variables.")
            print("You may need to obtain an OAuth token for authentication.")
    
    def search_products(
        self, 
        query: str, 
        limit: int = 20, 
        offset: int = 0,
        sort: str = "BestMatch",
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for products on eBay.
        
        Args:
            query: Search query (e.g., "iPhone case")
            limit: Number of results to return (default: 20, max: 200)
            offset: Number of results to skip for pagination
            sort: Sort order ("BestMatch", "PricePlusShippingLowest", "PricePlusShippingHighest")
            filters: Additional filters (price range, condition, etc.)
        
        Returns:
            Dictionary containing search results and metadata
        """
        endpoint = f"{self.browse_api_url}/item_summary/search"
        
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {self.oauth_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Prepare query parameters
        params = {
            'q': query,
            'limit': min(limit, 200),  # eBay API max limit is 200
            'offset': offset,
            'sort': sort
        }
        
        # Add filters if provided
        if filters:
            for key, value in filters.items():
                params[key] = value
        
        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                'error': f'Request failed: {str(e)}',
                'status_code': getattr(response, 'status_code', None)
            }
        except json.JSONDecodeError as e:
            return {
                'error': f'Failed to parse JSON response: {str(e)}'
            }
    
    def get_product_details(self, item_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific product.
        
        Args:
            item_id: eBay item ID
        
        Returns:
            Dictionary containing detailed product information
        """
        endpoint = f"{self.browse_api_url}/item/{item_id}"
        
        headers = {
            'Authorization': f'Bearer {self.oauth_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                'error': f'Request failed: {str(e)}',
                'status_code': getattr(response, 'status_code', None)
            }
        except json.JSONDecodeError as e:
            return {
                'error': f'Failed to parse JSON response: {str(e)}'
            }
    
    def parse_search_results(self, search_response: Dict[str, Any]) -> List[Product]:
        """
        Parse search results into Product objects.
        
        Args:
            search_response: Raw JSON response from search_products
        
        Returns:
            List of Product objects
        """
        products = []
        
        if 'error' in search_response:
            print(f"Error in search response: {search_response['error']}")
            return products
        
        item_summaries = search_response.get('itemSummaries', [])
        
        for item in item_summaries:
            product = Product(
                item_id=item.get('itemId', ''),
                title=item.get('title', ''),
                price=item.get('price', {}),
                item_href=item.get('itemHref', ''),
                image_url=item.get('image', {}).get('imageUrl') if item.get('image') else None,
                condition=item.get('condition'),
                seller=item.get('seller', {}),
                shipping_cost=item.get('shippingOptions', [{}])[0].get('shippingCost') if item.get('shippingOptions') else None,
                location=item.get('itemLocation', {}).get('city') if item.get('itemLocation') else None
            )
            products.append(product)
        
        return products
    
    def search_and_format(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Search for products and return formatted results.
        
        Args:
            query: Search query
            **kwargs: Additional parameters for search_products
        
        Returns:
            Formatted dictionary with products and metadata
        """
        search_results = self.search_products(query, **kwargs)
        
        if 'error' in search_results:
            return search_results
        
        products = self.parse_search_results(search_results)
        
        return {
            'query': query,
            'total_results': search_results.get('total', 0),
            'products': [
                {
                    'item_id': p.item_id,
                    'title': p.title,
                    'price': p.price,
                    'url': p.item_href,
                    'image_url': p.image_url,
                    'condition': p.condition,
                    'seller': p.seller,
                    'shipping_cost': p.shipping_cost,
                    'location': p.location
                }
                for p in products
            ],
            'metadata': {
                'limit': kwargs.get('limit', 20),
                'offset': kwargs.get('offset', 0),
                'sort': kwargs.get('sort', 'BestMatch')
            }
        }


def main():
    """Example usage of the eBay API client."""
    client = EbayAPIClient()
    
    # Example search
    query = "iPhone case"
    results = client.search_and_format(
        query=query,
        limit=10,
        sort="PricePlusShippingLowest"
    )
    
    # Print results
    print(f"Search Results for '{query}':")
    print(f"Total results: {results.get('total_results', 0)}")
    print("-" * 50)
    
    for i, product in enumerate(results.get('products', []), 1):
        print(f"{i}. {product['title']}")
        print(f"   Price: {product['price'].get('value', 'N/A')} {product['price'].get('currency', '')}")
        print(f"   URL: {product['url']}")
        if product.get('condition'):
            print(f"   Condition: {product['condition']}")
        print()


if __name__ == "__main__":
    main()
