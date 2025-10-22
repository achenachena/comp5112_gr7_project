#!/usr/bin/env python3
"""
Advanced Product Information Extraction Script

This script processes existing social media posts in the database and extracts
enhanced product information using advanced NLP techniques.

Usage:
    python scripts/extract_product_info.py [--update] [--limit N]
"""

import os
import sys
import sqlite3
import json
import re
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ecommerce_search.database.db_manager import get_db_manager
from ecommerce_search.database.models import SocialMediaProduct


class AdvancedProductExtractor:
    """Advanced product information extraction using NLP techniques."""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        
        # Enhanced product detection keywords
        self.product_keywords = [
            'product', 'review', 'recommend', 'buy', 'purchase', 'deal', 'sale',
            'upgrade', 'best', 'amazing', 'incredible', 'fantastic', 'love',
            'worth', 'value', 'quality', 'performance', 'experience'
        ]
        
        # Brand detection patterns (FIXED - separate brands from product types)
        self.brand_patterns = [
            r'\b(apple|samsung|sony|microsoft|google|amazon|nike|adidas|tesla|bmw|audi|mercedes)\b',
            r'\b(airpods|beats|bose|jbl|sennheiser|audio-technica)\b',
            r'\b(puma|under armour|lululemon|patagonia)\b'
        ]
        
        # Product types (not brands) - these should be treated as products, not brands
        self.product_types_only = [
            'iphone', 'ipad', 'macbook', 'galaxy', 'pixel', 'surface', 'xbox', 'playstation', 'nintendo'
        ]
        
        # Common brand name patterns (capitalized words, proper nouns)
        self.brand_name_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized words (e.g., "Ballsy Brew", "gomi")
        ]
        
        # Product category patterns
        self.category_patterns = {
            'electronics': ['phone', 'laptop', 'tablet', 'headphones', 'speaker', 'camera', 'gaming', 'audio', 'security cameras', 'coffee maker', 'macropad'],
            'clothing': ['shirt', 'dress', 'pants', 'shoes', 'jacket', 'sweater', 'jeans'],
            'beauty': ['skincare', 'makeup', 'sunscreen', 'moisturizer', 'serum', 'foundation'],
            'automotive': ['car', 'truck', 'suv', 'sedan', 'vehicle', 'automobile'],
            'home': ['furniture', 'appliance', 'kitchen', 'bedroom', 'living room'],
            'sports': ['fitness', 'gym', 'running', 'cycling', 'yoga', 'workout']
        }
        
        # Specific product types to extract (priority list)
        self.product_types = [
            'security cameras', 'coffee maker', 'headphones', 'laptop', 'smartphone', 'tablet', 'watch', 
            'speaker', 'camera', 'macropad', 'shoes', 'dress', 'shirt', 'pants', 'jacket', 'sweater', 
            'jeans', 'socks', 'underwear', 'bra', 'panty', 'lingerie', 'makeup', 'skincare', 'moisturizer', 
            'sunscreen', 'serum', 'foundation', 'car', 'truck', 'suv', 'sedan', 'vehicle', 'automobile', 
            'furniture', 'appliance', 'kitchen', 'bedroom', 'living room', 'fitness', 'gym', 'running', 
            'cycling', 'yoga', 'workout', 'app', 'software', 'ai', 'chatgpt', 'windows', 'linux', 'openai', 
            'roblox', 'duolingo', 'fortnite', 'snapchat', 'robinhood', 'trip', 'travel', 'vacation', 
            'destination', 'hotel', 'flight'
        ]
        
        # Price extraction patterns (ENHANCED)
        self.price_patterns = [
            r'\$[\d,]+\.?\d*',  # $50, $1,234.56
            r'USD\s*[\d,]+\.?\d*',  # USD 50, USD 1,234.56
            r'USD[\d,]+\.?\d*',  # USD50, USD1,234.56
            r'(\d+)\s*(dollars?|bucks?)',  # 50 dollars, 100 bucks
            r'price[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # price: $50
            r'cost[:\s]*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # cost: $50
            r'(\d+)\s*(?:USD|usd)',  # 50 USD
            r'around\s*\$?(\d+)',  # around $50
            r'about\s*\$?(\d+)',  # about $50
            r'roughly\s*\$?(\d+)',  # roughly $50
            r'(\d+)\s*(?:bucks?|dollars?)',  # 50 bucks, 100 dollars
        ]
        
        # Sentiment analysis words
        self.positive_words = ['amazing', 'incredible', 'fantastic', 'love', 'best', 'excellent', 'perfect', 'great']
        self.negative_words = ['terrible', 'awful', 'hate', 'worst', 'bad', 'disappointed', 'poor']
    
    def extract_product_info(self, text: str) -> Dict[str, Any]:
        """Extract enhanced product information from text."""
        if not text:
            return {}
        
        # Clean and normalize text
        text_lower = text.lower()
        
        # Extract brands (FIXED - much simpler and more effective approach)
        brands = []
        
        # First, extract known major brands
        for pattern in self.brand_patterns:
            try:
                matches = re.findall(pattern, text_lower)
                brands.extend(matches)
            except re.error:
                continue
        
        # Then, look for specific brand patterns in the text
        # Look for patterns like "Brand Name -" or "Brand Name product" or "Brand Name made"
        brand_context_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*-\s*',  # "Brand Name -"
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:made|product|coffee|speaker)',  # "Brand Name made/product/coffee/speaker"
            r'\b([a-z]+)\s+(?:speaker|made|product)',  # "gomi speaker", "brand made", etc.
        ]
        
        for pattern in brand_context_patterns:
            try:
                matches = re.findall(pattern, text)
                for match in matches:
                    if (len(match) > 2 and len(match.split()) <= 2 and
                        match.lower() not in self.product_types_only and
                        match.lower() not in ['the', 'and', 'or', 'but', 'for', 'with', 'from', 'this', 'that', 'these', 'those', 'here', 'there', 'where', 'when', 'what', 'how', 'why', 'who', 'which']):
                        brands.append(match)
            except re.error:
                continue
        
        # Extract categories
        detected_category = None
        for category, keywords in self.category_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_category = category
                break
        
        # Enhanced price extraction (FIXED)
        prices = []
        for pattern in self.price_patterns:
            try:
                matches = re.findall(pattern, text_lower)
                for match in matches:
                    if isinstance(match, tuple):
                        prices.append(match[0])
                    else:
                        prices.append(match)
            except re.error:
                continue
        
        # Clean and convert prices (IMPROVED)
        clean_prices = []
        for price in prices:
            # Remove all non-numeric characters except decimal point
            clean_price = re.sub(r'[^\d.]', '', str(price))
            if clean_price and '.' in clean_price:
                try:
                    price_value = float(clean_price)
                    if price_value > 0:  # Only accept positive prices
                        clean_prices.append(price_value)
                except ValueError:
                    continue
            elif clean_price and clean_price.isdigit():
                try:
                    price_value = float(clean_price)
                    if price_value > 0:  # Only accept positive prices
                        clean_prices.append(price_value)
                except ValueError:
                    continue
        
        # Extract product name (FIXED - prioritize specific product types)
        product_name = None
        
        # Priority 1: Extract specific product types (most important)
        for product_type in self.product_types:
            if product_type in text_lower:
                product_name = product_type.title()
                break
        
        # Priority 2: Extract product types that were previously treated as brands
        if not product_name:
            for product_type in self.product_types_only:
                if product_type in text_lower:
                    product_name = product_type.title()
                    break
        
        # Priority 3: Extract brand names if no specific product type found
        if not product_name and brands:
            product_name = brands[0].title()
        
        # Priority 4: Extract first meaningful word (1-2 words max) if no product type or brand found
        if not product_name:
            words = text.split()
            for i in range(min(2, len(words))):
                phrase = ' '.join(words[:i+1])
                if len(phrase) > 3 and len(phrase) < 20 and not any(word in phrase.lower() for word in ['why', 'how', 'what', 'when', 'where', 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'my', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'that', 'this', 'these', 'those']):
                    product_name = phrase.title()
                    break
        
        # Enhanced sentiment analysis
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment_score = 0.7 + (positive_count * 0.1)
        elif negative_count > positive_count:
            sentiment_score = 0.3 - (negative_count * 0.1)
        else:
            sentiment_score = 0.5
        
        # Determine if it's a review or recommendation
        is_review = any(keyword in text_lower for keyword in ['review', 'reviewed', 'tried', 'tested', 'used'])
        is_recommendation = any(keyword in text_lower for keyword in ['recommend', 'suggest', 'should', 'must', 'worth'])
        
        # Enhanced tagging system
        tags = []
        if brands:
            tags.extend(brands)
        if product_name:
            tags.append(product_name.lower())
        if detected_category:
            tags.append(detected_category)
        if clean_prices:
            tags.append(f"${max(clean_prices):.0f}")
        if is_review:
            tags.append("review")
        if is_recommendation:
            tags.append("recommendation")
        
        # Add sentiment-based tags
        if sentiment_score > 0.7:
            tags.append("positive")
        elif sentiment_score < 0.3:
            tags.append("negative")
        else:
            tags.append("neutral")
        
        return {
            'product_name': product_name,
            'brand': brands[0] if brands else None,
            'category': detected_category or ('products' if any(keyword in text_lower for keyword in self.product_keywords) else None),
            'price_mentioned': max(clean_prices) if clean_prices else None,
            'price_currency': 'USD',
            'is_review': is_review,
            'is_recommendation': is_recommendation,
            'sentiment_score': min(max(sentiment_score, 0.0), 1.0),
            'tags': list(set(tags)) if tags else []
        }
    
    def process_posts(self, limit: Optional[int] = None, update: bool = False) -> Dict[str, int]:
        """Process posts from the database and extract enhanced product information."""
        print("🔍 Advanced Product Information Extraction")
        print("=" * 50)
        
        # Get posts from database
        with self.db_manager.get_session() as session:
            query = session.query(SocialMediaProduct)
            if limit:
                query = query.limit(limit)
            
            posts = query.all()
            total_posts = len(posts)
            
            print(f"📊 Processing {total_posts} posts...")
            
            processed = 0
            updated = 0
            errors = 0
            
            for i, post in enumerate(posts, 1):
                try:
                    # Combine title and content for extraction
                    full_text = f"{post.title} {post.content or ''}"
                    
                    # Extract enhanced product information
                    extracted_info = self.extract_product_info(full_text)
                    
                    if update:
                        # Update the post with extracted information
                        post.product_name = extracted_info.get('product_name')
                        post.brand = extracted_info.get('brand')
                        post.category = extracted_info.get('category')
                        post.price_mentioned = extracted_info.get('price_mentioned')
                        post.price_currency = extracted_info.get('price_currency', 'USD')
                        post.is_review = extracted_info.get('is_review', False)
                        post.is_recommendation = extracted_info.get('is_recommendation', False)
                        post.sentiment_score = extracted_info.get('sentiment_score', 0.0)
                        post.tags = json.dumps(extracted_info.get('tags', []))
                        
                        updated += 1
                    
                    processed += 1
                    
                    # Show progress
                    if i % 100 == 0 or i == total_posts:
                        print(f"📈 Progress: {i}/{total_posts} ({i/total_posts*100:.1f}%)")
                    
                    # Show sample results
                    if i <= 5:
                        print(f"\n📝 Sample #{i}: {post.title[:50]}...")
                        print(f"   🛍️  Product: {extracted_info.get('product_name', 'None')}")
                        print(f"   🏷️  Brand: {extracted_info.get('brand', 'None')}")
                        print(f"   📂 Category: {extracted_info.get('category', 'None')}")
                        print(f"   💰 Price: {extracted_info.get('price_mentioned', 'None')}")
                        print(f"   ⭐ Review: {extracted_info.get('is_review', False)}")
                        print(f"   👍 Recommendation: {extracted_info.get('is_recommendation', False)}")
                        print(f"   😊 Sentiment: {extracted_info.get('sentiment_score', 0.0):.2f}")
                        print(f"   🏷️  Tags: {extracted_info.get('tags', [])}")
                
                except Exception as e:
                    errors += 1
                    print(f"❌ Error processing post {post.post_id}: {e}")
            
            if update:
                session.commit()
                print(f"\n✅ Database updated with enhanced product information!")
            
            return {
                'total_posts': total_posts,
                'processed': processed,
                'updated': updated,
                'errors': errors
            }
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze the extraction results."""
        print("\n📊 EXTRACTION ANALYSIS")
        print("=" * 30)
        
        with self.db_manager.get_session() as session:
            # Get statistics
            total_posts = session.query(SocialMediaProduct).count()
            posts_with_product_name = session.query(SocialMediaProduct).filter(
                SocialMediaProduct.product_name.isnot(None)
            ).count()
            posts_with_brand = session.query(SocialMediaProduct).filter(
                SocialMediaProduct.brand.isnot(None)
            ).count()
            posts_with_category = session.query(SocialMediaProduct).filter(
                SocialMediaProduct.category.isnot(None)
            ).count()
            posts_with_price = session.query(SocialMediaProduct).filter(
                SocialMediaProduct.price_mentioned.isnot(None)
            ).count()
            
            # Get top brands
            from sqlalchemy import func
            brand_counts = session.query(
                SocialMediaProduct.brand,
                func.count(SocialMediaProduct.brand).label('count')
            ).filter(
                SocialMediaProduct.brand.isnot(None)
            ).group_by(SocialMediaProduct.brand).order_by(func.count(SocialMediaProduct.brand).desc()).limit(10).all()
            
            # Get top categories
            category_counts = session.query(
                SocialMediaProduct.category,
                func.count(SocialMediaProduct.category).label('count')
            ).filter(
                SocialMediaProduct.category.isnot(None)
            ).group_by(SocialMediaProduct.category).order_by(func.count(SocialMediaProduct.category).desc()).limit(10).all()
            
            print(f"📈 Total Posts: {total_posts:,}")
            print(f"🛍️  Posts with Product Names: {posts_with_product_name:,} ({posts_with_product_name/total_posts*100:.1f}%)")
            print(f"🏷️  Posts with Brands: {posts_with_brand:,} ({posts_with_brand/total_posts*100:.1f}%)")
            print(f"📂 Posts with Categories: {posts_with_category:,} ({posts_with_category/total_posts*100:.1f}%)")
            print(f"💰 Posts with Prices: {posts_with_price:,} ({posts_with_price/total_posts*100:.1f}%)")
            
            print(f"\n🏆 TOP BRANDS:")
            for brand, count in brand_counts:
                print(f"   {brand}: {count} posts")
            
            print(f"\n📂 TOP CATEGORIES:")
            for category, count in category_counts:
                print(f"   {category}: {count} posts")
            
            return {
                'total_posts': total_posts,
                'posts_with_product_name': posts_with_product_name,
                'posts_with_brand': posts_with_brand,
                'posts_with_category': posts_with_category,
                'posts_with_price': posts_with_price,
                'top_brands': brand_counts,
                'top_categories': category_counts
            }


def main():
    """Main function to run the product extraction script."""
    parser = argparse.ArgumentParser(description='Extract enhanced product information from social media posts')
    parser.add_argument('--update', action='store_true', help='Update the database with extracted information')
    parser.add_argument('--limit', type=int, help='Limit the number of posts to process')
    parser.add_argument('--analyze', action='store_true', help='Analyze extraction results')
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = AdvancedProductExtractor()
    
    if args.analyze:
        # Analyze results
        extractor.analyze_results()
    else:
        # Process posts
        results = extractor.process_posts(limit=args.limit, update=args.update)
        
        print(f"\n🎯 EXTRACTION COMPLETE")
        print(f"📊 Total Posts: {results['total_posts']:,}")
        print(f"✅ Processed: {results['processed']:,}")
        if args.update:
            print(f"🔄 Updated: {results['updated']:,}")
        print(f"❌ Errors: {results['errors']:,}")
        
        if args.update:
            print(f"\n📈 Analyzing results...")
            extractor.analyze_results()


if __name__ == "__main__":
    main()
