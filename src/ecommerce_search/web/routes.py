"""
Web application routes
"""

import time
from flask import Blueprint, render_template, request, jsonify, current_app

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)


@main_bp.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@api_bp.route('/load_data', methods=['POST'])
def load_data():
    """Load data from database."""
    try:
        data = request.get_json()
        limit = data.get('limit', 1000)
        dataset = data.get('dataset', 'api')  # Default to API dataset
        
        with current_app.db_manager.get_session() as session:
            if dataset == 'api':
                from ecommerce_search.database.models import Product
                
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
                        'condition': product.condition,
                        'source': product.source
                    })
            else:  # social media dataset
                from ecommerce_search.database.models import SocialMediaProduct
                
                if limit:
                    db_products = session.query(SocialMediaProduct).limit(limit).all()
                else:
                    db_products = session.query(SocialMediaProduct).all()
                
                products = []
                for product in db_products:
                    products.append({
                        'id': product.post_id,
                        'title': product.title,
                        'description': product.content or '',
                        'category': product.category or '',
                        'price': {
                            'value': str(product.price_mentioned or 0),
                            'currency': 'USD'
                        },
                        'brand': product.brand or '',
                        'platform': product.platform,
                        'subreddit': product.subreddit,
                        'upvotes': product.upvotes,
                        'comments_count': product.comments_count,
                        'post_date': product.post_date.isoformat() if product.post_date else None
                    })
        
        current_app.products = products
        current_app.current_dataset = dataset
        db_info = current_app.db_manager.get_database_info()
        
        return jsonify({
            'success': True,
            'count': len(products),
            'dataset': dataset,
            'db_info': db_info
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@api_bp.route('/run_comparison', methods=['POST'])
def run_comparison():
    """Run algorithm comparison."""
    try:
        if not current_app.products:
            return jsonify({'success': False, 'error': 'No products loaded. Please load data first.'})
        
        # Create test queries based on dataset
        dataset = getattr(current_app, 'current_dataset', 'api')
        if dataset == 'api':
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
        else:  # social media dataset
            test_queries = [
                "amazing product", "worth it", "highly recommend",
                "best purchase", "incredible gadget", "fantastic tool",
                "love this", "game changer", "must have", "perfect",
                "excellent quality", "great value", "top rated",
                "customer favorite", "bestseller", "premium",
                "outstanding", "exceptional", "outstanding quality",
                "highly rated", "customer choice"
            ]
        
        # Create relevance judgments for social media dataset
        if dataset == 'social_media':
            print("Creating synthetic relevance judgments for social media dataset...")
            current_app.relevance_judge.create_synthetic_judgments(test_queries, current_app.products)
        
        # Run comparison
        start_time = time.time()
        from ecommerce_search.evaluation.ultra_simple_comparison import UltraSimpleComparison
        comparison = UltraSimpleComparison(current_app.algorithms, current_app.relevance_judge)
        results = comparison.compare_simple(test_queries, current_app.products)
        end_time = time.time()
        
        results['total_time'] = end_time - start_time
        
        return jsonify({
            'success': True,
            'results': results,
            'time': results['total_time']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@api_bp.route('/search', methods=['POST'])
def search():
    """Perform search with algorithms."""
    try:
        if not current_app.products:
            return jsonify({'success': False, 'error': 'No products loaded. Please load data first.'})
        
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'success': False, 'error': 'Empty query'})
        
        results = {}
        for algo_name, algorithm in current_app.algorithms.items():
            start_time = time.time()
            search_results = algorithm.search(query, current_app.products, limit=10)
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
