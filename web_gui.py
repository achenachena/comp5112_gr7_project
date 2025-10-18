#!/usr/bin/env python3
"""
Web-based GUI for E-commerce Search Algorithm Comparison

A simple Flask-based web interface that avoids tkinter/GIL issues.
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify
import threading
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluation.ultra_simple_comparison import UltraSimpleComparison
from algorithms.keyword_matching import KeywordSearch
from algorithms.tfidf_search import TFIDFSearch
from evaluation.metrics import RelevanceJudgment
from database.db_manager import get_db_manager
from database.models import Product

app = Flask(__name__)

# Global variables
products = []
algorithms = {
    'keyword_matching': KeywordSearch(),
    'tfidf': TFIDFSearch()
}
relevance_judge = RelevanceJudgment()
db_manager = get_db_manager()

# Template folder is already set up for Flask

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load_data', methods=['POST'])
def load_data():
    try:
        global products
        data = request.get_json()
        limit = data.get('limit', 1000)
        
        with db_manager.get_session() as session:
            if limit:
                db_products = session.query(Product).limit(limit).all()
            else:
                db_products = session.query(Product).all()
            
            products = []
            for product in db_products:
                products.append({
                    'id': product.external_id,
                    'title': product.title,
                    'description': product.description or '',
                    'category': product.category,
                    'price': {
                        'value': str(product.price_value),
                        'currency': product.price_currency
                    },
                    'brand': product.brand or '',
                    'condition': product.condition
                })
        
        db_info = db_manager.get_database_info()
        
        return jsonify({
            'success': True,
            'count': len(products),
            'db_info': db_info
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/run_comparison', methods=['POST'])
def run_comparison():
    try:
        if not products:
            return jsonify({'success': False, 'error': 'No products loaded. Please load data first.'})
        
        # Create test queries
        test_queries = [
            "wool shoes", "natural white shoes", "merino blend hoodie",
            "crew sock natural", "ankle sock grey", "women shoes navy",
            "rugged beige hoodie", "natural grey heather", "blizzard sole shoes",
            "deep navy shoes", "premium quality shoes", "comfortable running shoes",
            "durable outdoor apparel", "sustainable fashion items",
            "breathable fabric clothing", "stony beige lux liberty",
            "natural white blizzard sole", "medium grey deep navy",
            "casual everyday footwear", "outdoor adventure gear"
        ]
        
        # Run comparison
        start_time = time.time()
        comparison = UltraSimpleComparison(algorithms, relevance_judge)
        results = comparison.compare_simple(test_queries, products)
        end_time = time.time()
        
        results['total_time'] = end_time - start_time
        
        return jsonify({
            'success': True,
            'results': results,
            'time': results['total_time']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/search', methods=['POST'])
def search():
    try:
        if not products:
            return jsonify({'success': False, 'error': 'No products loaded. Please load data first.'})
        
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'success': False, 'error': 'Empty query'})
        
        results = {}
        for algo_name, algorithm in algorithms.items():
            start_time = time.time()
            search_results = algorithm.search(query, products, limit=10)
            search_time = time.time() - start_time
            
            results[algo_name] = {
                'results': search_results,
                'search_time': search_time
            }
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Starting Web-based GUI...")
    print("Open your browser and go to: http://localhost:5000")
    print("This web GUI avoids all tkinter/GIL issues!")
    print("Press Ctrl+C to stop the server")
    print()
    
    app.run(debug=False, host='0.0.0.0', port=5000)
