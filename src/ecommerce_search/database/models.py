"""
Database Models for E-commerce Search Algorithm Research

This module defines the SQLAlchemy models for storing e-commerce product data,
search queries, and algorithm evaluation results.
"""

from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text,
    DateTime, Boolean, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ecommerce_search.config import DatabaseConfig

Base = declarative_base()


class Product(Base):
    """Model for storing API-based e-commerce products."""

    __tablename__ = 'api_products'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Product identification
    external_id = Column(
        String(DatabaseConfig.EXTERNAL_ID_LENGTH), 
        unique=True, nullable=False, index=True
    )
    source = Column(
        String(DatabaseConfig.SOURCE_LENGTH), 
        nullable=False, index=True
    )  # shopify_api, reddit, twitter, etc.

    # Basic product information
    title = Column(Text, nullable=False, index=True)
    description = Column(Text)
    brand = Column(String(DatabaseConfig.BRAND_LENGTH), index=True)
    model = Column(String(DatabaseConfig.MODEL_LENGTH))
    sku = Column(String(DatabaseConfig.SKU_LENGTH), index=True)

    # Pricing
    price_value = Column(Float, nullable=False, index=True)
    price_currency = Column(String(DatabaseConfig.PRICE_CURRENCY_LENGTH), default='USD')

    # Classification
    category = Column(String(DatabaseConfig.CATEGORY_LENGTH), nullable=False, index=True)
    subcategory = Column(String(DatabaseConfig.SUBCATEGORY_LENGTH))

    # Product details
    condition = Column(String(DatabaseConfig.CONDITION_LENGTH), default='New')
    availability = Column(String(DatabaseConfig.AVAILABILITY_LENGTH), default='In Stock')

    # Seller information
    seller_name = Column(String(DatabaseConfig.SELLER_NAME_LENGTH))
    seller_location = Column(String(DatabaseConfig.SELLER_LOCATION_LENGTH))

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
    post_id = Column(
        String(DatabaseConfig.POST_ID_LENGTH), 
        unique=True, nullable=False, index=True
    )
    platform = Column(
        String(DatabaseConfig.PLATFORM_LENGTH), 
        nullable=False, index=True
    )  # reddit, twitter, instagram
    subreddit = Column(String(DatabaseConfig.SUBREDDIT_LENGTH), index=True)  # for Reddit posts

    # Content information
    title = Column(Text, nullable=False, index=True)
    content = Column(Text, nullable=False)
    author = Column(String(DatabaseConfig.AUTHOR_LENGTH), index=True)
    post_date = Column(DateTime, index=True)

    # Product information (extracted from social media content)
    product_name = Column(Text, index=True)
    product_description = Column(Text)
    brand = Column(String(DatabaseConfig.BRAND_LENGTH), index=True)
    category = Column(String(DatabaseConfig.CATEGORY_LENGTH), index=True)
    price_mentioned = Column(Float, index=True)
    price_currency = Column(String(DatabaseConfig.PRICE_CURRENCY_LENGTH), default='USD')

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
    query_text = Column(
        String(DatabaseConfig.QUERY_TEXT_LENGTH), 
        nullable=False, unique=True, index=True
    )
    category = Column(String(DatabaseConfig.QUERY_CATEGORY_LENGTH))  # electronics, clothing, etc.
    difficulty = Column(String(DatabaseConfig.DIFFICULTY_LENGTH))  # easy, medium, hard
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships

    def __repr__(self):
        return f"<SearchQuery(id={self.id}, query='{self.query_text}')>"




class DataCollectionLog(Base):
    """Model for tracking data collection activities."""

    __tablename__ = 'data_collection_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Collection details
    api_source = Column(String(DatabaseConfig.API_SOURCE_LENGTH), nullable=False, index=True)
    search_query = Column(String(DatabaseConfig.COLLECTION_QUERY_LENGTH), nullable=False)
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
