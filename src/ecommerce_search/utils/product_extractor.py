"""
Product Information Extraction Utilities

This module provides reusable product extraction functionality
to avoid code duplication across different scrapers.
"""

import re
import string
from typing import Dict, Any, List, Optional

# Constants for product extraction
PRODUCT_KEYWORDS = ['product', 'item', 'buy', 'purchase', 'review', 'recommend']
BRAND_PATTERNS = [r'\b(apple|samsung|sony|nike|adidas|microsoft|google|amazon)\b']
CATEGORY_PATTERNS = {
    'electronics': ['phone', 'laptop', 'computer', 'tablet', 'headphones'],
    'clothing': ['shirt', 'pants', 'shoes', 'dress', 'jacket'],
    'home': ['furniture', 'appliance', 'decor', 'kitchen']
}
PRICE_PATTERNS = [r'\$(\d+(?:\.\d{2})?)', r'(\d+(?:\.\d{2})?)\s*dollars?']
POSITIVE_WORDS = ['good', 'great', 'excellent', 'amazing', 'love', 'perfect']
NEGATIVE_WORDS = ['bad', 'terrible', 'awful', 'hate', 'worst', 'disappointed']
REVIEW_INDICATORS = ['review', 'rating', 'stars', 'opinion', 'experience']
RECOMMENDATION_INDICATORS = ['recommend', 'suggest', 'advise', 'should buy']
PRODUCT_TYPES = ['smartphone', 'laptop', 'headphones', 'shoes', 'book']


class ProductExtractor:
    """Reusable product information extraction using NLP techniques."""

    def __init__(self):
        """Initialize the product extractor with predefined patterns."""
        self._init_patterns()

    def _init_patterns(self):
        """Initialize all regex patterns and keyword lists."""
        # Use constants from the shared module
        self.product_keywords = PRODUCT_KEYWORDS
        self.brand_patterns = BRAND_PATTERNS
        self.category_patterns = CATEGORY_PATTERNS
        self.price_patterns = PRICE_PATTERNS
        self.positive_words = POSITIVE_WORDS
        self.negative_words = NEGATIVE_WORDS
        self.review_indicators = REVIEW_INDICATORS
        self.recommendation_indicators = RECOMMENDATION_INDICATORS
        self.product_types = PRODUCT_TYPES

    def extract_product_info(self, text: str) -> Dict[str, Any]:
        """
        Extract comprehensive product information from text.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary containing extracted product information
        """
        if not text or not text.strip():
            return self._empty_result()

        # Clean and normalize text
        text_lower = text.lower()

        # Extract all components
        brands = self._extract_brands(text_lower)
        category = self._extract_category(text_lower)
        prices = self._extract_prices(text_lower)
        product_name = self._extract_product_name(text, text_lower)
        sentiment = self._extract_sentiment(text_lower)
        is_review = self._is_review(text_lower)
        is_recommendation = self._is_recommendation(text_lower)
        tags = self._generate_tags(
            brands, category, prices, sentiment, is_review, is_recommendation
        )

        return {
            'product_name': product_name,
            'brand': brands[0] if brands else None,
            'category': category,
            'price_mentioned': prices[0] if prices else None,
            'sentiment_score': sentiment,
            'is_review': is_review,
            'is_recommendation': is_recommendation,
            'tags': tags
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            'product_name': None,
            'brand': None,
            'category': None,
            'price_mentioned': None,
            'sentiment_score': 0.0,
            'is_review': False,
            'is_recommendation': False,
            'tags': []
        }

    def _extract_brands(self, text_lower: str) -> List[str]:
        """Extract brand names from text."""
        brands = []
        for pattern in self.brand_patterns:
            matches = re.findall(pattern, text_lower)
            brands.extend(matches)
        return list(set(brands))  # Remove duplicates

    def _extract_category(self, text_lower: str) -> Optional[str]:
        """Extract product category from text."""
        for category, keywords in self.category_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        return None

    def _extract_prices(self, text_lower: str) -> List[float]:
        """Extract price information from text."""
        prices = []
        for pattern in self.price_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    # Clean the price string
                    price_str = match.replace('$', '').replace(',', '').strip()
                    if price_str and price_str.replace('.', '').isdigit():
                        price = float(price_str)
                        if price > 0:  # Only positive prices
                            prices.append(price)
                except (ValueError, AttributeError):
                    continue
        return prices

    def _extract_product_name(self, text: str, text_lower: str) -> Optional[str]:
        """Extract concise product name from text."""
        # Look for specific product types first
        for product_type in self.product_types:
            if product_type in text_lower:
                return product_type

        # Look for brand + product combinations
        for brand_pattern in self.brand_patterns:
            matches = re.findall(brand_pattern, text_lower)
            if matches:
                return matches[0]

        # Fallback to first meaningful word
        words = text.split()
        for word in words:
            if len(word) > 3 and word.isalpha():
                return word.lower()

        return None

    def _extract_sentiment(self, text_lower: str) -> float:
        """Extract sentiment score from text."""
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)

        total_words = len(text_lower.split())
        if total_words == 0:
            return 0.0

        # Calculate sentiment score (-1 to 1)
        sentiment = (positive_count - negative_count) / max(total_words, 1)
        return max(-1.0, min(1.0, sentiment))  # Clamp between -1 and 1

    def _is_review(self, text_lower: str) -> bool:
        """Check if text appears to be a product review."""
        return any(indicator in text_lower for indicator in self.review_indicators)

    def _is_recommendation(self, text_lower: str) -> bool:
        """Check if text appears to be a recommendation."""
        return any(indicator in text_lower for indicator in self.recommendation_indicators)

    def _generate_tags(self, brands: List[str], category: Optional[str],
                      prices: List[float], sentiment: float,
                      is_review: bool, is_recommendation: bool) -> List[str]:
        """Generate tags based on extracted information."""
        tags = []

        # Add brand tags
        tags.extend(brands)

        # Add category tag
        if category:
            tags.append(category)

        # Add price tag if found
        if prices:
            tags.append(f"price_{int(prices[0])}")

        # Add sentiment tag
        if sentiment > 0.1:
            tags.append("positive")
        elif sentiment < -0.1:
            tags.append("negative")
        else:
            tags.append("neutral")

        # Add review/recommendation tags
        if is_review:
            tags.append("review")
        if is_recommendation:
            tags.append("recommendation")

        return list(set(tags))  # Remove duplicates
