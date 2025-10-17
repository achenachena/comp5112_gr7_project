# Mock Datasets

This directory contains the mock data used by the e-commerce search algorithm project.

## Files

### `products.json`
Contains the base product data including:
- Product ID
- Title
- Category
- Price
- Brand

### `sellers.json`
List of seller/store names used for generating mock data.

### `locations.json`
List of geographic locations for seller addresses.

### `conditions.json`
List of product conditions (New, Used, Refurbished, etc.).

### `config.json`
Configuration settings for data generation including:
- Description template
- Default currency
- Rating ranges
- Review count ranges
- Stock ranges

## Usage

The `generate_dataset.py` script automatically loads data from these files to create comprehensive mock datasets for testing search algorithms.

## Customization

You can modify these JSON files to:
- Add new products
- Change seller names
- Update locations
- Modify product conditions
- Adjust configuration parameters

The changes will be automatically picked up the next time you run `generate_dataset.py`.

## Data Structure

### Products
```json
{
  "id": "P001",
  "title": "Product Name",
  "category": "Category Name",
  "price": "29.99",
  "brand": "Brand Name"
}
```

### Configuration
```json
{
  "description_template": "Template with {category} and {brand} placeholders",
  "currency": "USD",
  "rating_range": {"min": 3.5, "max": 5.0},
  "review_count_range": {"min": 10, "max": 500},
  "stock_range": {"min": 1, "max": 100}
}
```
