"""
Database Models for E-commerce Search Algorithm Research

This module defines the SQLAlchemy models for storing e-commerce product data,
search queries, and algorithm evaluation results.
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text, 
    DateTime, Boolean, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional, List

Base = declarative_base()


class Product(Base):
    """Model for storing API-based e-commerce products."""
    
    __tablename__ = 'api_products'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Product identification
    external_id = Column(String(100), unique=True, nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)  # bestbuy_api, target_api, etc.
    
    # Basic product information
    title = Column(Text, nullable=False, index=True)
    description = Column(Text)
    brand = Column(String(100), index=True)
    model = Column(String(100))
    sku = Column(String(100), index=True)
    
    # Pricing
    price_value = Column(Float, nullable=False, index=True)
    price_currency = Column(String(10), default='USD')
    
    # Classification
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100))
    
    # Product details
    condition = Column(String(50), default='New')
    availability = Column(String(50), default='In Stock')
    
    # Seller information
    seller_name = Column(String(100))
    seller_location = Column(String(100))
    
    # Media and links
    image_url = Column(Text)
    product_url = Column(Text)
    
    # Additional metadata
    tags = Column(Text)  # JSON string of tags
    specifications = Column(Text)  # JSON string of specs
    rating = Column(Float)
    review_count = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    search_results = relationship("SearchResult", back_populates="product")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_products_source_category', 'source', 'category'),
        Index('idx_products_price_range', 'price_value'),
        Index('idx_products_title_search', 'title'),
        Index('idx_products_brand_model', 'brand', 'model'),
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title[:50]}...', price=${self.price_value})>"


class SocialMediaProduct(Base):
    """Model for storing social media scraped product data."""
    
    __tablename__ = 'social_media_products'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Social media identification
    post_id = Column(String(100), unique=True, nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)  # reddit, twitter, instagram
    subreddit = Column(String(100), index=True)  # for Reddit posts
    
    # Content information
    title = Column(Text, nullable=False, index=True)
    content = Column(Text, nullable=False)
    author = Column(String(100), index=True)
    post_date = Column(DateTime, index=True)
    
    # Product information (extracted from social media content)
    product_name = Column(Text, index=True)
    product_description = Column(Text)
    brand = Column(String(100), index=True)
    category = Column(String(100), index=True)
    price_mentioned = Column(Float, index=True)
    price_currency = Column(String(10), default='USD')
    
    # Social media metrics
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    
    # Sentiment and quality
    sentiment_score = Column(Float)  # -1 to 1
    is_review = Column(Boolean, default=False)
    is_recommendation = Column(Boolean, default=False)
    is_complaint = Column(Boolean, default=False)
    
    # Metadata
    url = Column(Text)
    image_url = Column(Text)
    tags = Column(Text)  # JSON string of extracted tags
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return (f"<SocialMediaProduct(id={self.id}, platform='{self.platform}', "
                f"title='{self.title[:50]}...', product='{self.product_name[:30]}...')>")


class SearchQuery(Base):
    """Model for storing search queries used in evaluation."""
    
    __tablename__ = 'search_queries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(String(500), nullable=False, unique=True, index=True)
    category = Column(String(100))  # electronics, clothing, etc.
    difficulty = Column(String(20))  # easy, medium, hard
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    search_results = relationship("SearchResult", back_populates="query")
    
    def __repr__(self):
        return f"<SearchQuery(id={self.id}, query='{self.query_text}')>"


class SearchResult(Base):
    """Model for storing search algorithm results."""
    
    __tablename__ = 'search_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    product_id = Column(Integer, ForeignKey('api_products.id'), nullable=False, index=True)
    query_id = Column(Integer, ForeignKey('search_queries.id'), nullable=False, index=True)
    
    # Algorithm information
    algorithm_name = Column(String(50), nullable=False, index=True)  # keyword_matching, tfidf
    algorithm_version = Column(String(20))
    
    # Search metrics
    relevance_score = Column(Float, nullable=False, index=True)
    rank_position = Column(Integer, nullable=False, index=True)
    
    # Additional metadata
    matched_terms = Column(Text)  # JSON string of matched terms
    search_time_ms = Column(Float)  # Search execution time in milliseconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="search_results")
    query = relationship("SearchQuery", back_populates="search_results")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_search_results_query_algorithm', 'query_id', 'algorithm_name'),
        Index('idx_search_results_score_rank', 'relevance_score', 'rank_position'),
        Index('idx_search_results_product_query', 'product_id', 'query_id'),
    )
    
    def __repr__(self):
        return (f"<SearchResult(product_id={self.product_id}, "
                f"algorithm='{self.algorithm_name}', score={self.relevance_score})>")


class EvaluationMetrics(Base):
    """Model for storing algorithm evaluation metrics."""
    
    __tablename__ = 'evaluation_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Query and algorithm
    query_id = Column(Integer, ForeignKey('search_queries.id'), nullable=False, index=True)
    algorithm_name = Column(String(50), nullable=False, index=True)
    
    # Metrics at different K values
    precision_at_1 = Column(Float)
    precision_at_3 = Column(Float)
    precision_at_5 = Column(Float)
    precision_at_10 = Column(Float)
    
    recall_at_1 = Column(Float)
    recall_at_3 = Column(Float)
    recall_at_5 = Column(Float)
    recall_at_10 = Column(Float)
    
    f1_score_at_1 = Column(Float)
    f1_score_at_3 = Column(Float)
    f1_score_at_5 = Column(Float)
    f1_score_at_10 = Column(Float)
    
    ndcg_at_1 = Column(Float)
    ndcg_at_3 = Column(Float)
    ndcg_at_5 = Column(Float)
    ndcg_at_10 = Column(Float)
    
    # Overall metrics
    map_score = Column(Float)
    mrr_score = Column(Float)
    
    # Performance metrics
    avg_search_time_ms = Column(Float)
    total_results_returned = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_metrics_query_algorithm', 'query_id', 'algorithm_name'),
        Index('idx_metrics_algorithm_performance', 'algorithm_name', 'map_score'),
    )
    
    def __repr__(self):
        return (f"<EvaluationMetrics(query_id={self.query_id}, "
                f"algorithm='{self.algorithm_name}', map={self.map_score})>")


class DataCollectionLog(Base):
    """Model for tracking data collection activities."""
    
    __tablename__ = 'data_collection_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Collection details
    api_source = Column(String(50), nullable=False, index=True)
    search_query = Column(String(500), nullable=False)
    collection_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Results
    products_collected = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    
    # Error tracking
    error_message = Column(Text)
    api_response_code = Column(Integer)
    
    # Performance
    collection_time_seconds = Column(Float)
    
    def __repr__(self):
        return (f"<DataCollectionLog(source='{self.api_source}', "
                f"query='{self.search_query}', products={self.products_collected})>")


# Database utility functions
def create_database_engine(database_url: str):
    """Create a SQLAlchemy engine for the database."""
    return create_engine(database_url, echo=False)


def create_session(engine):
    """Create a database session."""
    Session = sessionmaker(bind=engine)
    return Session()


def create_tables(engine):
    """Create all database tables."""
    Base.metadata.create_all(engine)


def get_database_stats(session):
    """Get statistics about the database contents."""
    stats = {}
    
    # Count records in each table
    stats['products'] = session.query(Product).count()
    stats['search_queries'] = session.query(SearchQuery).count()
    stats['search_results'] = session.query(SearchResult).count()
    stats['evaluation_metrics'] = session.query(EvaluationMetrics).count()
    stats['collection_logs'] = session.query(DataCollectionLog).count()
    
    # Product statistics
    if stats['products'] > 0:
        stats['unique_sources'] = session.query(Product.source).distinct().count()
        stats['unique_categories'] = session.query(Product.category).distinct().count()
        stats['price_range'] = {
            'min': (session.query(Product.price_value)
                   .order_by(Product.price_value.asc()).first()[0]),
            'max': (session.query(Product.price_value)
                   .order_by(Product.price_value.desc()).first()[0])
        }
    
    return stats
