"""
Web application routes
"""

import time
from flask import Blueprint, render_template, request, jsonify, current_app
from ecommerce_search.database.models import Product, SocialMediaProduct
from ecommerce_search.evaluation.algorithm_comparison import UltraSimpleComparison

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)


@main_bp.route('/')
def index():
    """Main page."""
    return render_template('index.html')


def _convert_api_product(product):
    """Convert API Product model to dict."""
    return {
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
    }


def _convert_social_product(product):
    """Convert SocialMediaProduct model to dict."""
    return {
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
    }


@api_bp.route('/load_data', methods=['POST'])
def load_data():
    """Load data from database."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
            
        limit = data.get('limit', 1000)
        dataset = data.get('dataset', 'api')  # Default to API dataset

        # Build products list inside the with block to ensure proper scoping
        result_products = []
        
        with current_app.db_manager.get_session() as session:
            if dataset == 'api':
                # Verify we're querying the correct table (api_products)
                # Product model maps to 'api_products' table
                if limit:
                    db_products = session.query(Product).limit(limit).all()
                else:
                    db_products = session.query(Product).all()

                result_products = [_convert_api_product(p) for p in db_products]
                
            elif dataset == 'social':  # social media dataset
                # Verify we're querying the correct table (social_media_products)
                # SocialMediaProduct model maps to 'social_media_products' table
                if limit:
                    db_products = session.query(SocialMediaProduct).limit(limit).all()
                else:
                    db_products = session.query(SocialMediaProduct).all()

                result_products = [_convert_social_product(p) for p in db_products]
                
            else:
                return jsonify({'success': False, 'error': f'Invalid dataset: {dataset}. Use "api" or "social".'})

        # Only set products if we successfully loaded them
        current_app.products = result_products
        current_app.current_dataset = dataset
        db_info = current_app.db_manager.get_database_info()

        return jsonify({
            'success': True,
            'count': len(result_products),
            'dataset': dataset,
            'db_info': db_info
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            'success': False, 
            'error': f'Error loading data: {str(e)}',
            'details': error_details
        })


@api_bp.route('/run_comparison', methods=['POST'])
def run_comparison():
    """Run algorithm comparison."""
    try:
        if not current_app.products:
            return jsonify({
                'success': False, 
                'error': 'No products loaded. Please load data first.'
            })

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

        # Create relevance judgments for both datasets
        current_app.relevance_judge.create_synthetic_judgments(test_queries, current_app.products)

        # Run comparison
        start_time = time.time()
        comparison = UltraSimpleComparison(current_app.algorithms, current_app.relevance_judge)
        results = comparison.compare_simple(test_queries, current_app.products)
        end_time = time.time()

        results['total_time'] = end_time - start_time

        return jsonify({
            'success': True,
            'results': results,
            'time': results['total_time']
        })

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({'success': False, 'error': str(e)})


@api_bp.route('/search', methods=['POST'])
def search():
    """Perform search with algorithms."""
    try:
        if not current_app.products:
            return jsonify({
                'success': False, 
                'error': 'No products loaded. Please load data first.'
            })

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

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({'success': False, 'error': str(e)})
