# Project Summary

## Overview

This project implements a comprehensive framework for comparing search algorithms (Keyword Matching vs TF-IDF) using real e-commerce data. The system provides both theoretical foundations and practical implementations for evaluating search algorithm effectiveness at scale.

## Key Features

### Search Algorithms
- **Keyword Matching**: Exact and partial keyword matching with configurable weights
- **TF-IDF**: Term Frequency-Inverse Document Frequency with vector similarity

### Evaluation Metrics
- Precision@K, Recall@K, F1@K
- NDCG@K (Normalized Discounted Cumulative Gain)
- MAP (Mean Average Precision)
- MRR (Mean Reciprocal Rank)

### Data Sources
- **Real API Data**: 200+ Shopify stores (43,226 products)
- **Social Media Data**: Reddit posts (9,000+ posts) with product discussions
- **Database Storage**: SQLite database for scalable data management

### User Interfaces
- **Web Application**: Modern browser-based interface
- **Command Line**: Programmatic access and automation
- **Python API**: Library for integration with other projects

## Repository Setup

This repository does not include:
- Database files (large, regenerable)
- API credentials (.env file)
- Collected data checkpoints

After cloning, run `python scripts/utilities/database_initializer.py` to create the database locally.

## System Architecture

```
comp5112_gr7_project/
├── src/ecommerce_search/     # Main package
│   ├── algorithms/           # Search algorithms
│   ├── database/             # Database models
│   ├── evaluation/           # Evaluation metrics
│   ├── web/                  # Web application
│   └── cli.py                # Command line interface
├── scripts/                  # Organized scripts
│   ├── data_collection/      # Data scraping scripts
│   ├── utilities/            # Setup and utility scripts
│   └── web/                  # Web application scripts
├── data/                     # Data storage
│   └── ecommerce_research.db # Main SQLite database
└── docs/                     # Documentation
```

## Quick Start

```bash
# Installation
git clone <repository-url>
cd comp5112_gr7_project
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Database setup
python scripts/utilities/database_initializer.py

# Collect real data (optional)
python scripts/data_collection/ecommerce_api_collector.py
python scripts/data_collection/social_media_scraper.py

# Run application
python -c "
import sys
import os
sys.path.append(os.getcwd())
from src.ecommerce_search.web.app import create_app
app = create_app()
app.run(host='0.0.0.0', port=5000, debug=False)
"
```

## Research Applications

This system is designed for:
- **Academic Research**: Algorithm comparison studies
- **Industry Applications**: E-commerce search optimization
- **Educational Purposes**: Learning about search algorithms
- **Benchmarking**: Performance evaluation frameworks

## Technical Specifications

- **Python 3.8+**: Modern Python features
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM
- **scikit-learn**: Machine learning algorithms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Authors

COMP5112 Group 7 - E-commerce Search Algorithm Comparison Project