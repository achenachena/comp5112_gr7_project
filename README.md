# Comparative Study of Search Algorithms in E-commerce

A research project comparing **Keyword Matching** vs **TF-IDF** search algorithms using eBay product data.

## Research Objectives

- Compare effectiveness of keyword matching vs TF-IDF algorithms
- Evaluate search relevance and accuracy metrics
- Analyze performance differences in e-commerce product search
- Provide insights for improving search algorithms

## Features

- **Data Collection**: Automated eBay product data gathering
- **Keyword Matching**: Traditional keyword-based search algorithm
- **TF-IDF Algorithm**: Term Frequency-Inverse Document Frequency search
- **Evaluation Metrics**: Precision, Recall, F1-Score, NDCG
- **Comparison Framework**: Side-by-side algorithm performance analysis
- **Interactive Prototype**: GUI for testing and comparison

## Project Structure

```
├── data/                    # Collected product data
├── algorithms/              # Search algorithm implementations
│   ├── keyword_matching.py
│   └── tfidf_search.py
├── evaluation/              # Performance evaluation tools
│   ├── metrics.py
│   └── comparison.py
├── data_collection/         # eBay data collection
│   └── ebay_client.py
├── prototype/               # Interactive prototype
│   ├── gui.py
│   └── cli.py
├── utils/                   # Utility functions
│   └── preprocessing.py
└── results/                 # Analysis results
```

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up eBay API credentials** (see `setup_guide.md`):
   - Create a `.env` file with your eBay API credentials

3. **Run the prototype**:
   ```bash
   python prototype/cli.py
   ```

## Usage Example

```python
from algorithms.keyword_matching import KeywordSearch
from algorithms.tfidf_search import TFIDFSearch
from evaluation.comparison import SearchComparison

# Initialize search algorithms
keyword_search = KeywordSearch()
tfidf_search = TFIDFSearch()

# Compare search results
comparison = SearchComparison(keyword_search, tfidf_search)
results = comparison.compare("iPhone case", dataset)

# Analyze performance metrics
print(f"Keyword Matching F1-Score: {results['keyword']['f1_score']}")
print(f"TF-IDF F1-Score: {results['tfidf']['f1_score']}")
```

## Files

- `algorithms/` - Search algorithm implementations
- `evaluation/` - Performance metrics and comparison tools
- `data_collection/` - eBay API integration
- `prototype/` - Interactive testing interface
- `utils/` - Data preprocessing utilities

## Documentation

See `setup_guide.md` for complete setup instructions and API documentation.

---

This repo is created for students at MsC Program in Computer science at Lakehead University. This is to be used for COMP5112 Group 7's project
