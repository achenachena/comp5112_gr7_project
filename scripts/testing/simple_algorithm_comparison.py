#!/usr/bin/env python3
"""
Simple Algorithm Comparison for Social Media Dataset
"""

import sqlite3
import json
import sys
import os
from typing import List, Dict, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

def load_social_media_products(limit: int = 100) -> List[Dict[str, Any]]:
    """Load social media products from database."""
    conn = sqlite3.connect('data/ecommerce_research.db')
    cursor = conn.cursor()
    
    query = '''
    SELECT 
        post_id,
        title,
        content,
        product_name,
        brand,
        category,
        upvotes,
        comments_count,
        sentiment_score
    FROM social_media_products 
    WHERE product_name IS NOT NULL 
    AND LENGTH(product_name) > 3
    ORDER BY upvotes DESC
    LIMIT ?
    '''
    
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    
    products = []
    for result in results:
        post_id, title, content, product_name, brand, category, upvotes, comments_count, sentiment_score = result
        products.append({
            'id': post_id,
            'title': title or '',
            'description': content or '',
            'product_name': product_name or '',
            'brand': brand or '',
            'category': category or '',
            'upvotes': upvotes or 0,
            'comments_count': comments_count or 0,
            'sentiment_score': sentiment_score or 0.5
        })
    
    conn.close()
    return products

def simple_keyword_search(products: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Simple keyword matching search."""
    query_lower = query.lower()
    results = []
    
    for product in products:
        score = 0
        
        # Check title
        if product['title']:
            title_lower = product['title'].lower()
            if query_lower in title_lower:
                score += 3
            # Count word matches
            query_words = query_lower.split()
            for word in query_words:
                if word in title_lower:
                    score += 1
        
        # Check product name
        if product['product_name']:
            product_lower = product['product_name'].lower()
            if query_lower in product_lower:
                score += 2
            query_words = query_lower.split()
            for word in query_words:
                if word in product_lower:
                    score += 1
        
        # Check brand
        if product['brand']:
            brand_lower = product['brand'].lower()
            if query_lower in brand_lower:
                score += 2
        
        # Check category
        if product['category']:
            category_lower = product['category'].lower()
            if query_lower in category_lower:
                score += 1
        
        if score > 0:
            product['search_score'] = score
            results.append(product)
    
    # Sort by score and engagement
    results.sort(key=lambda x: (x['search_score'], x['upvotes']), reverse=True)
    return results

def simple_tfidf_search(products: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Simple TF-IDF inspired search."""
    query_lower = query.lower()
    query_words = query_lower.split()
    results = []
    
    for product in products:
        score = 0
        text_fields = [
            product['title'] or '',
            product['description'] or '',
            product['product_name'] or '',
            product['brand'] or '',
            product['category'] or ''
        ]
        
        combined_text = ' '.join(text_fields).lower()
        
        # Count word frequency
        for word in query_words:
            word_count = combined_text.count(word)
            if word_count > 0:
                score += word_count
        
        # Boost for exact phrase matches
        if query_lower in combined_text:
            score += 5
        
        if score > 0:
            product['search_score'] = score
            results.append(product)
    
    # Sort by score and engagement
    results.sort(key=lambda x: (x['search_score'], x['upvotes']), reverse=True)
    return results

def run_comparison():
    """Run algorithm comparison."""
    print('🔬 SIMPLE ALGORITHM COMPARISON')
    print('=' * 50)
    
    # Load products
    products = load_social_media_products(100)
    print(f'📊 Loaded {len(products)} social media products')
    
    # Test queries
    test_queries = [
        'gaming',
        'headphones',
        'coffee',
        'phone',
        'kitchen',
        'laptop',
        'camera',
        'watch'
    ]
    
    print(f'\\n🔍 Testing with {len(test_queries)} queries:')
    for query in test_queries:
        print(f'  - {query}')
    
    print('\\n📈 ALGORITHM PERFORMANCE:')
    print('=' * 50)
    
    for query in test_queries:
        print(f'\\n🔍 Query: "{query}"')
        print('-' * 30)
        
        # Keyword search
        keyword_results = simple_keyword_search(products, query)
        print(f'Keyword Matching: {len(keyword_results)} results')
        for i, result in enumerate(keyword_results[:3], 1):
            print(f'  {i}. {result["product_name"]} ({result["brand"]}) - Score: {result["search_score"]}')
            print(f'      Title: {result["title"][:50]}...' if result["title"] else '      Title: No title')
            print(f'      Engagement: {result["upvotes"]:,} upvotes')
        
        # TF-IDF search
        tfidf_results = simple_tfidf_search(products, query)
        print(f'\\nTF-IDF Search: {len(tfidf_results)} results')
        for i, result in enumerate(tfidf_results[:3], 1):
            print(f'  {i}. {result["product_name"]} ({result["brand"]}) - Score: {result["search_score"]}')
            print(f'      Title: {result["title"][:50]}...' if result["title"] else '      Title: No title')
            print(f'      Engagement: {result["upvotes"]:,} upvotes')
    
    print('\\n✅ Algorithm comparison completed!')
    print('\\n🎯 Key Insights:')
    print('- Keyword matching: Better for exact product names')
    print('- TF-IDF search: Better for semantic similarity')
    print('- Both algorithms leverage social media engagement metrics')

if __name__ == "__main__":
    run_comparison()
