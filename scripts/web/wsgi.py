#!/usr/bin/env python3
"""
WSGI Entry Point for Production Deployment

This file is used by production WSGI servers like Gunicorn, uWSGI, etc.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent  # Go up to project root
sys.path.insert(0, str(project_root))

# Project imports
from src.ecommerce_search.web.app import create_app  # pylint: disable=wrong-import-position

# Create Flask application instance
application = create_app()

if __name__ == '__main__':
    # This allows running with: python wsgi.py
    application.run(host='127.0.0.1', port=5000, debug=False)
