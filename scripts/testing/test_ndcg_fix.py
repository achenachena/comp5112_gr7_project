#!/usr/bin/env python3
"""
Test NDCG Fix for Social Media Dataset
"""

import sqlite3
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.ecommerce_search.algorithms.tfidf_search import TFIDFSearch
from src.ecommerce_search.algorithms.keyword_matching import KeywordSearch
from src.ecommerce_search.evaluation.metrics import RelevanceJudgment, SearchMetrics

def test_ndcg_calculation():
    """Test NDCG calculation with proper relevance judgments."""
    
    print('🔬 TESTING NDCG CALCULATION FIX')
    print('=' * 50)
    
    # Load social media products
    conn = sqlite3.connect('data/ecommerce_research.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        post_id,
        title,
        content,
        product_name,
        brand,
        category
    FROM social_media_products 
    WHERE product_name IS NOT NULL 
    AND LENGTH(product_name) > 3
    LIMIT 20
    ''')
    
    results = cursor.fetchall()
    products = []
    
    for i, result in enumerate(results):
        post_id, title, content, product_name, brand, category = result
        products.append({
            'id': post_id,
            'title': title or '',
            'description': content or '',
            'product_name': product_name or '',
            'brand': brand or '',
            'category': category or ''
        })
    
    conn.close()
    
    print(f'📊 Loaded {len(products)} social media products')
    
    # Test queries
    test_queries = ['gaming', 'laptop', 'headphones', 'camera']
    
    # Initialize algorithms
    tfidf = TFIDFSearch(min_df=1, max_df=0.8)
    keyword = KeywordSearch()
    
    # Create relevance judgments
    relevance_judge = RelevanceJudgment()
    relevance_judge.create_synthetic_judgments(test_queries, products)
    
    print('\\n📈 NDCG CALCULATION TEST:')
    print('=' * 50)
    
    for query in test_queries:
        print(f'\\n🔍 Query: "{query}"')
        print('-' * 30)
        
        # Get relevant items
        relevant_items = relevance_judge.get_relevant_items(query)
        print(f'Relevant items: {len(relevant_items)}')
        
        if len(relevant_items) > 0:
            # Test TF-IDF
            tfidf_results = tfidf.search(query, products, limit=10)
            tfidf_retrieved = [result['id'] for result in tfidf_results]
            
            # Test Keyword
            keyword_results = keyword.search(query, products, limit=10)
            keyword_retrieved = [result['id'] for result in keyword_results]
            
            # Calculate NDCG for different K values
            print('NDCG Values:')
            for k in [1, 3, 5, 10]:
                tfidf_ndcg = SearchMetrics.ndcg_at_k(relevant_items, tfidf_retrieved, k)
                keyword_ndcg = SearchMetrics.ndcg_at_k(relevant_items, keyword_retrieved, k)
                
                print(f'  K={k:2d}: TF-IDF={tfidf_ndcg:.4f}, Keyword={keyword_ndcg:.4f}')
        else:
            print('  No relevant items found for this query')
    
    print('\\n✅ NDCG calculation test completed!')
    print('\\n🎯 Key Points:')
    print('- NDCG values should now vary across different K values')
    print('- Different algorithms should show different NDCG patterns')
    print('- Values should be realistic (not constant 0.76)')

if __name__ == "__main__":
    test_ndcg_calculation()
