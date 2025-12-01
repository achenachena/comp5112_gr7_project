#!/usr/bin/env python3
"""
Generate real performance comparison chart from database data.
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_search.algorithms.keyword_matching import KeywordSearch
from ecommerce_search.algorithms.tfidf_search import TFIDFSearch
from ecommerce_search.database.db_manager import get_db_manager
from ecommerce_search.database.models import Product, SocialMediaProduct
from ecommerce_search.evaluation.algorithm_comparison import UltraSimpleComparison
from ecommerce_search.evaluation.metrics import RelevanceJudgment

def generate_chart():
    print("Loading data from database...")
    db_manager = get_db_manager()
    
    # Load a sample of products for evaluation (balanced mix)
    limit = 2000
    search_products = []
    
    with db_manager.get_session() as session:
        # API Products
        products = session.query(Product).limit(limit).all()
        for product in products:
            search_products.append({
                'id': product.external_id,
                'title': product.title,
                'description': product.description or '',
                'category': product.category,
                'brand': product.brand or '',
                'source': product.source
            })
            
        # Social Media Products
        social_products = session.query(SocialMediaProduct).limit(limit).all()
        for product in social_products:
            search_products.append({
                'id': product.post_id,
                'title': product.title,
                'description': product.content or '',
                'category': product.category or '',
                'brand': product.brand or '',
                'source': 'social_media'
            })
            
    print(f"Loaded {len(search_products)} products.")

    # Define test queries
    queries = [
        "iphone case", "running shoes", "gaming laptop", "wireless headphones",
        "coffee maker", "skin care", "winter jacket", "yoga mat",
        "bluetooth speaker", "smart watch"
    ]

    # Initialize algorithms
    algorithms = {
        'Keyword Matching': KeywordSearch(),
        'TF-IDF': TFIDFSearch()
    }

    # Run comparison
    print("Running comparison (this may take a moment)...")
    relevance_judge = RelevanceJudgment()
    comparison = UltraSimpleComparison(algorithms, relevance_judge)
    results = comparison.compare_simple(queries, search_products)

    # Extract metrics
    metrics = ['P@5', 'R@5', 'F1@5', 'NDCG@10', 'MAP']
    
    kw_metrics = results['algorithms']['Keyword Matching']['metrics']
    tfidf_metrics = results['algorithms']['TF-IDF']['metrics']
    
    kw_scores = [
        kw_metrics['precision@5'],
        kw_metrics['recall@5'],
        kw_metrics['f1@5'],
        kw_metrics['ndcg@10'],
        kw_metrics['map']
    ]
    
    tfidf_scores = [
        tfidf_metrics['precision@5'],
        tfidf_metrics['recall@5'],
        tfidf_metrics['f1@5'],
        tfidf_metrics['ndcg@10'],
        tfidf_metrics['map']
    ]

    # Plotting
    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, kw_scores, width, label='Keyword Matching', color='#3498db')
    rects2 = ax.bar(x + width/2, tfidf_scores, width, label='TF-IDF', color='#2ecc71')

    ax.set_ylabel('Score')
    ax.set_title('Real-World Performance Comparison (Database Results)')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 1.0)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Add labels
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    
    output_file = 'real_performance_comparison.png'
    plt.savefig(output_file, dpi=300)
    print(f"Chart saved to {output_file}")
    
    # Print results table for report text
    print("\nResults Table:")
    print("-" * 50)
    print(f"{'Metric':<10} | {'Keyword':<15} | {'TF-IDF':<15}")
    print("-" * 50)
    for i, metric in enumerate(metrics):
        print(f"{metric:<10} | {kw_scores[i]:<15.4f} | {tfidf_scores[i]:<15.4f}")
    print("-" * 50)

if __name__ == "__main__":
    generate_chart()

