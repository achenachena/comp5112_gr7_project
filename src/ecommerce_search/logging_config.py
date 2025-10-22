"""
Logging configuration for E-commerce Search Algorithm Comparison
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_level=None, log_file=None):
    """Set up logging configuration."""
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
    
    if log_file is None:
        log_file = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)
