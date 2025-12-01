# Technical Report: Comparative Analysis of Search Algorithms for E-commerce

**Authors:**

* **Mingchen Liang** (ID: 1313746) - <mliang4@lakeheadu.ca>
* **Jun Chen** (ID: 1308752) - <jchen93@lakeheadu.ca>

**Course:**
COMP-5112-FB - Research Methodology
Department of Computer Science, Lakehead University
Fall Term, 2025

---

## 1. Executive Summary

This technical report details the implementation and evaluation of an E-commerce search system designed to compare two fundamental Information Retrieval (IR) algorithms: **Weighted Keyword Matching** and **Term Frequency-Inverse Document Frequency (TF-IDF)**.

The project addresses the challenge of retrieving relevant products from heterogeneous data sources:

1. **Structured Data**: Standard e-commerce product feeds (e.g., Shopify).
2. **Unstructured Data**: Social media discussions (e.g., Reddit posts) where product information is embedded in informal text.

Our system implements a complete pipeline including data collection from real APIs, a hybrid Natural Language Processing (NLP) module for product extraction, and a comparative evaluation framework using standard metrics (Precision@K, Recall@K, F1, NDCG).

**Repository URL**: [https://github.com/achenachena/comp5112_gr7_project.git](https://github.com/achenachena/comp5112_gr7_project.git)

---

## 2. System Architecture

The system follows a modular, layered architecture designed for scalability and separation of concerns.

### Project Structure

```text
comp5112_gr7_project/
├── data/                          # Data storage
│   └── ecommerce_research.db         # Main SQLite database
│
├── scripts/                       # Scripts organized by purpose
│   ├── analysis/                     # Analysis scripts
│   │   └── generate_real_results.py  # Result generation script
│   ├── data_collection/              # Data collection scripts
│   │   ├── social_media_scraper.py   # Reddit scraper (Multi-threaded)
│   │   └── ecommerce_api_collector.py # Shopify collector
│   ├── utilities/                    # Utility scripts
│   │   └── database_initializer.py   # Database setup
│   └── web/                          # Web application scripts
│       ├── run_web.py                # Development server entry point
│       └── start_web.sh              # Automated startup script
│
├── src/ecommerce_search/          # Core application code
│   ├── algorithms/                   # Search algorithms
│   │   ├── keyword_matching.py       # Weighted Keyword implementation
│   │   └── tfidf_search.py           # TF-IDF Vectorizer implementation
│   ├── database/                     # Database management
│   │   ├── db_manager.py             # DB session management
│   │   └── models.py                 # SQLAlchemy models
│   ├── evaluation/                   # Evaluation metrics
│   │   ├── comparison.py             # Comparison logic
│   │   ├── metrics.py                # NDCG, Precision, Recall calculations
│   │   └── algorithm_comparison.py   # Evaluation runner
│   ├── utils/                        # Utilities
│   │   ├── product_extractor.py      # Base extractor
│   │   ├── base_scraper.py           # Base scraper class
│   │   └── hybrid_product_extractor.py # Advanced NLP extraction logic
│   ├── web/                          # Web interface
│   │   ├── app.py                    # Flask app factory
│   │   ├── routes.py                 # API endpoints
│   │   ├── static/                   # CSS/JS
│   │   └── templates/                # HTML templates
│   └── cli.py                        # Command line interface
│
└── 📚 docs/                          # Documentation
    ├── PROJECT_SUMMARY.md
    ├── USAGE_GUIDE.md
    ├── PRESENTATION_OUTLINE.md
    └── RESEARCH_METHODOLOGY.md
```

### Architecture Components

* **Data Ingestion Layer**: Handles raw data acquisition from external APIs. It includes rate limiting and error handling.
* **Processing Layer**: The core innovation of this project. It uses NLP (POS tagging, NER) to transform unstructured social media text into structured product records.
* **Core Search Engine**: Python-based implementations of the search algorithms. It loads data from the SQLite database into memory for fast retrieval.
* **User Interface**: Provides both a visual Web GUI (Flask) for demonstrations and a CLI for automated testing.

---

## 3. Installation and Setup Guide

### Prerequisites

* Python 3.8 or higher
* Git
* (Optional) API Keys for Reddit (if collecting fresh social media data)

### Step-by-Step Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/achenachena/comp5112_gr7_project.git
    cd comp5112_gr7_project
    ```

2. **Set Up Virtual Environment**

    It is best practice to run Python projects in an isolated environment.

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

    *Note: This will install Flask, SQLAlchemy, NLTK, spaCy, and other required libraries.*

4. **Download NLP Models**

    The Hybrid Product Extractor requires specific NLTK and spaCy models to function.

    ```bash
    python -m spacy download en_core_web_sm
    python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('stopwords')"
    ```

5. **Initialize the Database**

    This script creates the SQLite database schema in `data/ecommerce_research.db`.

    ```python
    # scripts/utilities/database_initializer.py
    def main():
        print("Initializing database...")
        # Initializes tables defined in src/ecommerce_search/database/models.py
        db_manager = initialize_database(database_url, reset=False)
        
        info = db_manager.get_database_info()
        print(f"Tables Created: {info['tables_created']}")
    ```

    **Run command:**

    ```bash
    python scripts/utilities/database_initializer.py
    ```

6. **Generate Performance Results**

    To reproduce the results shown in this report, run the analysis script. This script loads real data from the database and evaluates both algorithms.

    ```bash
    python scripts/analysis/generate_real_results.py
    ```

    *This will output `real_performance_comparison.png` and print the metrics table.*

---

## 4. Data Collection Modules

### 4.1 Real E-commerce Data (Shopify)

We collect high-quality structured data from public Shopify store endpoints (`/products.json`). This data simulates a standard retailer inventory.

**Source Code Reference**: `scripts/data_collection/ecommerce_api_collector.py`

```python
class RealEcommerceCollector:
    def collect_from_shopify_stores(self, max_per_query: int = 10) -> List[Dict]:
        """
        Collect from public Shopify stores - REAL e-commerce data.
        No API key required for public stores.
        """
        shopify_stores = [
            'https://shop.polymer80.com',
            'https://www.allbirds.com',
            'https://www.gymshark.com',
        ]
        
        products = []
        for store_url in shopify_stores:
            try:
                products_url = f"{store_url}/products.json"
                response = requests.get(products_url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('products', [])[:max_per_query]:
                        product = self._format_shopify_product(item, store_url)
                        products.append(product)
            except Exception:
                continue
        return products
```

**To Run:**

```bash
python scripts/data_collection/ecommerce_api_collector.py
```

### 4.2 Social Media Data (Reddit)

We scrape Reddit to gather unstructured "in-the-wild" product discussions. This involves using the PRAW library to fetch posts from subreddits like `r/gadgets` and `r/BuyItForLife`. We implemented a **Multi-Threaded Scraper** to handle rate limits and maximize data throughput.

**Scraper Logic**: `scripts/data_collection/social_media_scraper.py`

```python
def scrape_subreddit(self, subreddit_name: str, max_posts: int = 100) -> List[Dict[str, Any]]:
    """Scrape real posts from a subreddit."""
    logger.info("Scraping r/%s for %d posts...", subreddit_name, max_posts)
    posts = []
    
    try:
        subreddit = self.reddit.subreddit(subreddit_name)
        
        # Get hot posts
        for post in subreddit.hot(limit=max_posts):
            if post.id in self.scraped_ids:
                continue
            
            post_data = {
                'post_id': f"reddit_{post.id}",
                'platform': 'reddit',
                'subreddit': subreddit_name,
                'title': post.title,
                'content': post.selftext,
                'upvotes': post.score,
                'comments_count': post.num_comments,
                'url': f"https://reddit.com{post.permalink}",
                'created_at': datetime.utcnow()
            }
            
            # Extract product information using NLP immediately
            post_data.update(self.product_extractor.extract_product_info(
                post.title + " " + post.selftext
            ))
            
            posts.append(post_data)
            self.scraped_ids.add(post.id)
            
            if len(posts) >= max_posts:
                break
                
    except (AttributeError, KeyError) as e:
        logger.error("Error scraping r/%s: %s", subreddit_name, str(e))
    
    return posts
```

**Database Model**: `src/ecommerce_search/database/models.py`

The collected data is stored in a dedicated `SocialMediaProduct` table:

```python
class SocialMediaProduct(Base):
    """Model for storing social media scraped product data."""

    __tablename__ = 'social_media_products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False, index=True)
    subreddit = Column(String(50), index=True)

    # Content information
    title = Column(Text, nullable=False, index=True)
    content = Column(Text, nullable=False)
    
    # Extracted Metadata (via NLP)
    product_name = Column(Text, index=True)
    brand = Column(String(100), index=True)
    sentiment_score = Column(Float)
    is_review = Column(Boolean, default=False)
```

**To Run:**

1. Create a `.env` file with your Reddit credentials (see `env.template`).
2. Execute the scraper:

    ```bash
    python scripts/data_collection/social_media_scraper.py
    ```

---

## 5. Data Processing: Hybrid Product Extractor

Social media posts are messy. To make them searchable, we implemented a **Hybrid Product Extractor** that uses four strategies to identify the "product" being discussed in a post.

**Strategies:**

1. **POS Tagging**: Identifies Noun Phrases using NLTK.
2. **Named Entity Recognition (NER)**: Uses spaCy to find `PRODUCT` or `ORG` entities.
3. **Contextual Analysis**: Looks for objects of verbs like "bought" or "review".
4. **Pattern Matching**: Fallback regex for known brands.

**Source Code Reference**: `src/ecommerce_search/utils/hybrid_product_extractor.py`

```python
def _extract_product_name_hybrid(self, text: str, text_lower: str) -> Optional[str]:
    """Extract product name using hybrid approach."""
    candidates = []
    
    # Method 1: POS Tagging
    if self.nltk_available:
        pos_result = self._extract_product_name_pos(text)
        if pos_result:
            candidates.append(('pos', pos_result, 0.8))
    
    # Method 2: NER
    if self.spacy_available and self.nlp_spacy:
        ner_result = self._extract_product_name_ner(text)
        if ner_result:
            candidates.append(('ner', ner_result, 0.9))
    
    # Method 3: Context-aware
    context_result = self._extract_product_name_context(text, text_lower)
    if context_result:
        candidates.append(('context', context_result, 0.7))
    
    # Select best candidate based on confidence scores
    if candidates:
        best_method, best_name, best_score = max(candidates, key=lambda x: x[2])
        return best_name
    
    return None
```

**POS Tagging Implementation Detail**:

```python
def _extract_product_name_pos(self, text: str) -> Optional[str]:
    """Extract product name using POS tagging."""
    tokens = word_tokenize(text.lower())
    pos_tags = pos_tag(tokens)
    
    # Look for noun phrases
    product_candidates = []
    for i, (word, pos) in enumerate(pos_tags):
        if pos in ['NN', 'NNS', 'NNP', 'NNPS']:  # Nouns
            if self._is_product_noun(word):
                # Try to get compound nouns (e.g., "coffee maker")
                compound = self._extract_compound_noun(pos_tags, i)
                if compound:
                    product_candidates.append(compound)
    
    return self._select_best_product_name(product_candidates, text)
```

---

## 6. Core Search Algorithms

### 6.1 Weighted Keyword Matching

This algorithm calculates a score based on the frequency of query terms in the document, with boosts for exact phrase matches and specific fields (Title vs Description).

**Key Features:**

* **Exact Match Boost**: Multiplier for finding the exact query string.
* **Partial Match**: Support for substring matching.
* **Length Normalization**: Penalizes very long documents to prevent bias.

**Source Code Reference**: `src/ecommerce_search/algorithms/keyword_matching.py`

```python
def preprocess_text(self, text: str) -> List[str]:
    """
    Preprocess text by tokenizing, removing punctuation, and filtering stop words.
    """
    if not text:
        return []

    # Convert to lowercase
    if not self.case_sensitive:
        text = text.lower()

    # Remove punctuation and split into tokens
    text = re.sub(r'[^\w\s]', ' ', text)
    tokens = text.split()

    # Remove stop words
    tokens = [token for token in tokens if token not in self.stop_words]

    return tokens

def calculate_keyword_score(self, query_tokens: List[str], product_tokens: List[str]) -> float:
    score = 0.0
    total_query_weight = 0.0

    for query_token, query_freq in query_counter.items():
        query_weight = query_freq

        # Check for exact matches
        if query_token in product_counter:
            exact_matches = product_counter[query_token]
            score += exact_matches * query_weight * self.exact_match_weight

    # Normalize by query weight and product length
    if total_query_weight > 0:
        score = score / (total_query_weight * math.log(len(product_tokens) + 1))

    return score
```

### 6.2 TF-IDF (Term Frequency - Inverse Document Frequency)

A statistical measure used to evaluate how important a word is to a document in a collection or corpus. It handles "stop words" and common terms much better than simple keyword matching.

**Implementation Details:**

* **TF**: Logarithmic scaling `1 + log(count)` to dampen the effect of high frequencies.
* **IDF**: Standard `log(N / df)` where rare terms get higher weights.
* **Similarity**: Cosine similarity between the Query Vector and Document Vector.

**Source Code Reference**: `src/ecommerce_search/algorithms/tfidf_search.py`

```python
def search(self, query: str, products: List[Dict[str, Any]], limit: int = 10):
    # 1. Preprocess Query
    query_tokens = self.preprocess_text(query)
    
    # 2. Calculate query TF-IDF Vector
    query_tfidf = self._calculate_tfidf(query_tokens)

    scored_products = []
    for product in products:
        # 3. Calculate product TF-IDF Vector
        product_tokens = self.preprocess_text(product_text)
        product_tfidf = self._calculate_tfidf(product_tokens)

        # 4. Calculate cosine similarity
        similarity_score = self._cosine_similarity(query_tfidf, product_tfidf)
        
        if similarity_score > 0:
            scored_products.append({
                'product': product,
                'score': similarity_score
            })

    # Sort by similarity score (descending)
    scored_products.sort(key=lambda x: x['score'], reverse=True)
    return scored_products[:limit]
```

---

## 7. Evaluation Framework

We evaluate the algorithms using standard Information Retrieval metrics. The `UltraSimpleComparison` class orchestrates the evaluation by running queries against both algorithms and calculating metrics.

**Research Methodology**: To strictly evaluate the algorithms, we generate **Synthetic Ground Truth** judgments. This simulates a human annotator marking documents as relevant or not based on term overlap and metadata.

**Ground Truth Generation**: `src/ecommerce_search/evaluation/metrics.py`

```python
def create_social_media_judgments(self, queries: List[str], products: List[Dict[str, Any]]):
    """
    Create synthetic relevance judgments specifically for social media content.
    This method accounts for the informal, conversational nature of social media posts.
    """
    for query in queries:
        query_lower = query.lower()
        
        for product in products:
            relevance = 0.0
            
            # 1. Exact phrase matching (highest priority for social media)
            if query_lower in post_text_lower:
                relevance += 0.6

            # 2. Product name matching (extracted via NLP)
            if 'product_name' in product and query_lower in product['product_name'].lower():
                relevance += 0.5

            # 3. Engagement-based relevance (Social Signals)
            upvotes = product.get('upvotes', 0)
            if upvotes > 50:
                relevance += 0.1
            
            # Cap at 1.0
            relevance = min(1.0, relevance)
            
            if relevance > 0.12:
                self.add_judgment(query, product_id, relevance)
```

**Metrics Implemented:**

1. **Precision@K**: Fraction of relevant items in the top K results.
2. **Recall@K**: Fraction of all relevant items found in the top K results.
3. **F1-Score**: Harmonic mean of Precision and Recall.
4. **NDCG**: Normalized Discounted Cumulative Gain (measures ranking quality).

**Metric Calculation**: `src/ecommerce_search/evaluation/metrics.py`

```python
@staticmethod
def ndcg_at_k(relevant_items: set, retrieved_items: List[Any], k: int, 
              relevance_scores: Dict[Any, float] = None) -> float:
    """Calculate Normalized Discounted Cumulative Gain (NDCG)@K."""
    top_k = retrieved_items[:k]

    # Calculate DCG
    dcg = 0.0
    for i, item in enumerate(top_k):
        relevance = relevance_scores.get(item, 0.0)
        if relevance > 0:
            dcg += relevance / math.log2(i + 2)

    # Calculate IDCG (Ideal DCG)
    ideal_relevances = sorted(
        [relevance_scores.get(item, 0.0) for item in relevant_items],
        reverse=True
    )[:k]
    idcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(ideal_relevances))

    return dcg / idcg if idcg > 0 else 0.0
```

---

## 8. Running the Application

### 8.1 Web Interface (Recommended)

The web interface provides a visual way to load data, run comparisons, and test search queries. It is built using Flask and serves REST endpoints for the frontend.

**Application Factory**: `src/ecommerce_search/web/app.py`

```python
def create_app():
    app = Flask(__name__)
    
    # Initialize global state
    app.products = []
    app.algorithms = {
        'keyword_matching': KeywordSearch(),
        'tfidf': TFIDFSearch()
    }
    
    # Register routes
    from ecommerce_search.web.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    
    return app
```

**Command:**

```bash
python src/ecommerce_search/web/app.py
```

**Usage:**

1. Open `http://127.0.0.1:5000` in your browser.
2. **Dashboard**: Click "Load Database Data" to ingest the collected JSON data into the SQLite database.
3. **Compare Algorithms**: Click "Run Comparison" to see charts of Precision, Recall, and F1 scores.
4. **Search**: Use the search bar to manually test queries like "wireless headphones" and see side-by-side results.

### 8.2 Command Line Interface (CLI)

For quick testing without the web UI.

**CLI Implementation**: `src/ecommerce_search/cli.py`

```python
def run_search(query: str, algorithm: str, dataset: str, limit: int):
    """Run search with specified algorithm and dataset."""
    
    # Initialize algorithms
    algorithms = {
        'keyword': KeywordSearch(),
        'tfidf': TFIDFSearch()
    }

    # Load products based on dataset choice
    db_manager = get_db_manager()
    with db_manager.get_session() as session:
        if dataset == 'api':
            products = session.query(Product).limit(1000).all()
            # ... convert to search format ...
            
    # Run search
    algo = algorithms[algorithm]
    results = algo.search(query, search_products, limit=limit)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['product']['title']} (Score: {result['score']:.4f})")
```

**Search Command:**

```bash
# Search for "blue t-shirt" using Keyword Matching
python src/ecommerce_search/cli.py search "blue t-shirt" --algorithm keyword

# Search using TF-IDF
python src/ecommerce_search/cli.py search "blue t-shirt" --algorithm tfidf
```

**Comparison Command:**

```bash
# Run the full evaluation suite
python src/ecommerce_search/cli.py compare
```

---

## 9. Results Summary

The following chart displays the actual performance metrics generated by running our evaluation framework on a random sample of 4,000 products (2,000 API, 2,000 Social Media) from our database.

![Real Performance Comparison](real_performance_comparison.png)

**Performance Metrics Table (Real Data):**

| Metric | Keyword Matching | TF-IDF |
| :--- | :--- | :--- |
| **Precision@5** | 0.8400 | **1.0000** |
| **Recall@5** | 0.0728 | **0.0947** |
| **F1-Score@5** | 0.1299 | **0.1678** |
| **NDCG@10** | 0.7380 | **1.0000** |
| **MAP** | 0.1017 | **0.1894** |

**Analysis:**

1. **Precision Dominance**: TF-IDF achieved a perfect Precision@5 of 1.0, meaning every single one of the top 5 results for our test queries was relevant. Keyword Matching was also strong (0.84) but returned some irrelevant results due to partial matches on common words.
2. **Ranking Quality (NDCG)**: TF-IDF's perfect NDCG score (1.0) indicates it not only found relevant items but ranked them in the optimal order. Keyword Matching (0.74) often ranked less relevant items higher because it relies purely on term frequency without considering term rarity (IDF).
3. **Recall Challenges**: Both algorithms showed low recall (< 0.10). This is expected given the large dataset (65,000+ items) and generic queries; there are likely hundreds of relevant items for "shoes", so retrieving only the top 10 naturally results in low recall. However, TF-IDF still outperformed Keyword Matching by ~30%.

## 10. Conclusion

This project demonstrates that while simple **Keyword Matching** is adequate for strictly structured databases, modern "Social Commerce" requires more sophisticated approaches. **TF-IDF**, combined with our **Hybrid NLP Extraction** pipeline, demonstrated superior performance across all key metrics, proving it is robust enough to handle the noise and ambiguity of user-generated content in a real-world e-commerce environment.
