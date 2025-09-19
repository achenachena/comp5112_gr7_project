# eBay API Product Data Collection Setup Guide

This project allows you to collect product data from eBay's API by querying for products and receiving JSON results directly.

## Prerequisites

1. **eBay Developer Account**: Sign up at [eBay Developers Program](https://developer.ebay.com/)
2. **Python 3.7+**: Make sure you have Python installed on your system

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. eBay API Credentials Setup

1. **Register for eBay Developer Program**:
   - Go to [eBay Developers Program](https://developer.ebay.com/)
   - Create an account and sign in

2. **Create an Application**:
   - Navigate to "My Account" > "Applications"
   - Click "Create an App Key"
   - Fill in the required information:
     - App Title: "Product Data Collector" (or any name you prefer)
     - App Purpose: "Research and Development"
     - App Type: "Web Application"
   - Note down your **Client ID** and **Client Secret**

3. **Obtain OAuth Token**:
   - For testing purposes, you can use eBay's OAuth Token Generator
   - Go to [OAuth Token Generator](https://developer.ebay.com/api-docs/static/oauth-tokens.html)
   - Select your application and environment (Sandbox for testing)
   - Generate a token and copy it

### 3. Environment Configuration

1. **Create Environment File**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your credentials:
   ```
   EBAY_APP_ID=your_app_id_here
   EBAY_CLIENT_ID=your_client_id_here
   EBAY_CLIENT_SECRET=your_client_secret_here
   EBAY_REDIRECT_URI=your_redirect_uri_here
   EBAY_OAUTH_TOKEN=your_oauth_token_here
   EBAY_ENVIRONMENT=sandbox
   ```

### 4. Test the Setup

Run the example script to test your setup:

```bash
python example_usage.py
```

## Usage Examples

### Basic Product Search

```python
from ebay_client import EbayAPIClient

client = EbayAPIClient()

# Search for iPhone cases
results = client.search_and_format(
    query="iPhone case",
    limit=10,
    sort="PricePlusShippingLowest"
)

print(f"Found {results['total_results']} results")
for product in results['products']:
    print(f"- {product['title']}: {product['price']['value']} {product['price']['currency']}")
```

### Search with Filters

```python
# Search with price and condition filters
results = client.search_and_format(
    query="laptop",
    limit=5,
    filters={
        'price_max': '500',
        'condition': 'NEW'
    }
)
```

### Get Detailed Product Information

```python
# Get detailed info for a specific product
details = client.get_product_details("item_id_here")
```

## API Endpoints Used

- **Search Products**: `GET /buy/browse/v1/item_summary/search`
- **Product Details**: `GET /buy/browse/v1/item/{itemId}`

## Response Format

The API returns JSON responses with the following structure:

```json
{
  "query": "iPhone case",
  "total_results": 1000,
  "products": [
    {
      "item_id": "v1|1234567890|0",
      "title": "iPhone 12 Case - Black",
      "price": {
        "value": "12.99",
        "currency": "USD"
      },
      "url": "https://www.ebay.com/itm/1234567890",
      "image_url": "https://i.ebayimg.com/images/g/abc123/s-l1600.jpg",
      "condition": "NEW",
      "seller": {
        "username": "seller123"
      },
      "location": "New York"
    }
  ],
  "metadata": {
    "limit": 10,
    "offset": 0,
    "sort": "PricePlusShippingLowest"
  }
}
```

## Important Notes

1. **Rate Limits**: eBay has API rate limits. Be mindful of how many requests you make.

2. **Sandbox vs Production**:
   - Use `EBAY_ENVIRONMENT=sandbox` for testing
   - Use `EBAY_ENVIRONMENT=production` for live data

3. **OAuth Tokens**: Tokens expire and need to be refreshed periodically.

4. **Error Handling**: The client includes error handling for common issues like network problems and API errors.

## Troubleshooting

### Common Issues

1. **Authentication Error**: Make sure your OAuth token is valid and not expired
2. **Rate Limit Exceeded**: Wait before making more requests
3. **Invalid Query**: Check that your search query is properly formatted

### Getting Help

- Check the [eBay API Documentation](https://developer.ebay.com/api-docs/)
- Review the [OAuth Guide](https://developer.ebay.com/api-docs/static/oauth-tokens.html)
- Check your application status in the eBay Developer Portal
