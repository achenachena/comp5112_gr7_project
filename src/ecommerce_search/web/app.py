#!/usr/bin/env python3
"""
Web application factory for E-commerce Search Algorithm Comparison
"""

import os
import sys
from flask import Flask

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_search.algorithms import KeywordSearch, TFIDFSearch
from ecommerce_search.database import get_db_manager
from ecommerce_search.evaluation import RelevanceJudgment, UltraSimpleComparison


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Initialize global variables
    app.products = []
    app.algorithms = {
        'keyword_matching': KeywordSearch(),
        'tfidf': TFIDFSearch()
    }
    app.relevance_judge = RelevanceJudgment()
    app.db_manager = get_db_manager()
    
    # Register blueprints
    from ecommerce_search.web.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("Starting Web-based GUI...")
    print("Open your browser and go to: http://localhost:5000")
    print("This web GUI avoids all tkinter/GIL issues!")
    print("Press Ctrl+C to stop the server")
    print()
    
    app.run(debug=False, host='0.0.0.0', port=5000)
