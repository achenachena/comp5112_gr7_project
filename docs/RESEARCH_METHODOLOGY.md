# Research Methodology: Database-Based Comparative Study of Search Algorithms in E-commerce

## Research Question

**How do keyword matching and TF-IDF search algorithms compare in terms of effectiveness for large-scale e-commerce product search using real marketplace data?**

## Objectives

1. **Primary Objective**: Compare the performance of keyword matching vs TF-IDF algorithms for e-commerce product search using real API data
2. **Secondary Objectives**:
   - Evaluate search relevance and accuracy metrics on large-scale datasets
   - Analyze performance differences across different product categories and query types
   - Demonstrate scalability with hundreds of thousands of products
   - Provide insights for improving search algorithms in real-world e-commerce applications
   - Establish a database-backed framework for large-scale search algorithm research

## Methodology

### 1. Algorithm Implementation

#### Keyword Matching Algorithm
- **Approach**: Traditional exact and partial keyword matching
- **Features**:
  - Tokenization and text preprocessing
  - Stop word removal
  - Exact match weighting (configurable)
  - Partial match scoring (substring matching)
  - Normalization by query and document length

#### TF-IDF Algorithm
- **Approach**: Term Frequency-Inverse Document Frequency statistical method
- **Features**:
  - Document frequency calculation across product corpus
  - TF-IDF vectorization
  - Cosine similarity for relevance scoring
  - Configurable min/max document frequency thresholds

### 2. Database Architecture

#### Database Schema
- **Products Table**: Store e-commerce product data with indexing for fast search
- **Search Queries Table**: Store test queries with categorization and difficulty assessment
- **Search Results Table**: Store algorithm results with relevance scores and rankings
- **Evaluation Metrics Table**: Store comprehensive performance metrics
- **Data Collection Logs Table**: Track API collection activities and performance

#### Scalability Features
- **Indexed Fields**: Fast search on title, category, brand, price
- **Batch Operations**: Efficient insertion of thousands of products
- **Connection Pooling**: Optimized database access for concurrent operations
- **Performance Tracking**: Monitor search times and result counts

### 3. Real Data Collection

#### API Integration
- **Shopify Stores**: Real e-commerce products from various stores

#### Data Quality Assurance
- **Real Pricing**: Actual marketplace prices from live APIs
- **Authentic Descriptions**: Genuine product descriptions and specifications
- **Category Classification**: Real e-commerce category systems
- **Brand Verification**: Authentic brand names and model numbers

### 4. Evaluation Framework

#### Metrics Used
1. **Precision@K**: Accuracy of top-K results (K=1,3,5,10)
2. **Recall@K**: Coverage of relevant items in top-K results
3. **F1-Score@K**: Harmonic mean of precision and recall
4. **NDCG@K**: Normalized Discounted Cumulative Gain for ranking quality
5. **MAP**: Mean Average Precision across all queries
6. **MRR**: Mean Reciprocal Rank for first relevant result timing

#### Ground Truth Creation
- **Synthetic Relevance Judgments**: Created using keyword overlap and exact match criteria
- **Threshold-based Relevance**: Items with relevance score ≥ 0.3 considered relevant
- **Query-specific Judgments**: Individual relevance scores for each query-item pair
- **Category-aware Scoring**: Relevance scoring considers product categories

### 5. Data Collection (Legacy Information)

#### Data Sources
- **Primary**: Shopify stores (200+ stores across multiple categories)
- **Secondary**: Synthetic product data for testing and validation
- **Database Storage**: SQL database for scalable data management

#### Data Preprocessing
- Text cleaning and normalization
- HTML tag removal
- Special character handling
- Price and metadata standardization
- Category classification

### 4. Experimental Design

#### Test Queries
- **Product-specific**: "iPhone case", "Samsung phone case"
- **Category-based**: "wireless charger", "screen protector"
- **Brand-focused**: "iPad case", "MacBook case"

#### Evaluation Protocol
1. **Single Query Evaluation**: Individual algorithm performance per query
2. **Aggregated Evaluation**: Average performance across all queries
3. **Statistical Analysis**: Performance comparison with significance testing
4. **Runtime Analysis**: Computational efficiency comparison

### 5. Performance Analysis

#### Quantitative Metrics
- **Relevance Metrics**: Precision, Recall, F1-Score, NDCG
- **Efficiency Metrics**: Search time, indexing time
- **Statistical Significance**: Performance differences between algorithms

#### Qualitative Analysis
- **Result Quality**: Relevance of top results
- **Query Understanding**: Algorithm behavior for different query types
- **Error Analysis**: Common failure cases and edge cases

## Expected Outcomes

### Research Hypotheses

1. **H1**: TF-IDF will outperform keyword matching for queries with multiple terms
2. **H2**: Keyword matching will be faster but less accurate than TF-IDF
3. **H3**: Both algorithms will perform better on specific product queries than general category queries

### Anticipated Results

1. **Performance Comparison**:
   - TF-IDF expected to have higher MAP and NDCG scores
   - Keyword matching expected to be faster for simple queries
   - Trade-off between accuracy and computational efficiency

2. **Query Type Analysis**:
   - Single-word queries: Similar performance
   - Multi-word queries: TF-IDF advantage
   - Ambiguous queries: TF-IDF better at disambiguation

3. **Scalability Analysis**:
   - Keyword matching: Linear scaling with corpus size
   - TF-IDF: Better scaling for large corpora due to statistical weighting

## Limitations

1. **Data Limitations**:
   - Synthetic relevance judgments may not reflect real user preferences
   - Dependent on API availability and rate limits
   - Product catalog variations across different e-commerce platforms

2. **Algorithm Limitations**:
   - No semantic understanding (word embeddings, neural networks)
   - No user personalization or context awareness
   - No query expansion or suggestion mechanisms

3. **Evaluation Limitations**:
   - No real user feedback or click-through data
   - Binary relevance judgments (relevant/not relevant)
   - Limited query diversity

## Future Work

1. **Enhanced Algorithms**:
   - Implement BM25 (Best Matching 25) algorithm
   - Add semantic search using word embeddings
   - Include query expansion techniques

2. **Advanced Evaluation**:
   - User study with real e-commerce scenarios
   - A/B testing with actual search traffic
   - Multi-level relevance judgments

3. **Real-world Integration**:
   - Deploy on live e-commerce platform
   - Collect user interaction data
   - Implement adaptive ranking based on user behavior

## Conclusion

This research provides a systematic comparison of traditional search algorithms in e-commerce contexts, establishing a foundation for understanding algorithm trade-offs and informing future search system development.
