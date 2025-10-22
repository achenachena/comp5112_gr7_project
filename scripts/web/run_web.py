#!/usr/bin/env python3
"""
Flask Web Application Entry Point

This is the proper way to run the Flask application for development and production.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent  # Go up to project root
sys.path.insert(0, str(project_root))

# Project imports
from src.ecommerce_search.web.app import create_app  # pylint: disable=wrong-import-position

def main():
    """Main entry point for the Flask application."""

    # Create Flask app
    app = create_app()

    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '127.0.0.1')  # Default to localhost for security
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    print("Starting Flask application...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"URL: http://{host}:{port}")
    print()

    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True  # Enable threading for better performance
    )

if __name__ == '__main__':
    main()
