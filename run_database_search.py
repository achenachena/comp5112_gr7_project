#!/usr/bin/env python3
"""
Database-Based Search Algorithm Evaluation

This script runs search algorithms on the database-stored e-commerce data
and stores the results for large-scale evaluation.
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import get_db_manager, get_session
from database.models import Product, SearchQuery, SearchResult, EvaluationMetrics
from algorithms.keyword_matching import KeywordSearch
from algorithms.tfidf_search import TFIDFSearch
from evaluation.metrics import SearchMetrics, RelevanceJudgment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseSearchEvaluator:
    """Evaluate search algorithms on database-stored products."""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        
        # Initialize algorithms with different parameters for comparison
        self.algorithms = {
            'keyword_matching': KeywordSearch(
                case_sensitive=False,
                exact_match_weight=25.0  # High weight for exact matches
            ),
            'tfidf': TFIDFSearch(
                min_df=2,        # Require terms in at least 2 documents
                max_df=0.6,      # Exclude very common terms
                case_sensitive=False
            )
        }
        
        # Initialize evaluation metrics
        self.metrics_calculator = SearchMetrics()
        self.relevance_judge = RelevanceJudgment()
    
    def load_products_from_database(self, limit: int = None) -> List[Dict]:
        """Load products from database for search evaluation."""
        logger.info("📦 Loading products from database...")
        
        with self.db_manager.get_session() as session:
            query = session.query(Product)
            if limit:
                query = query.limit(limit)
            
            products = query.all()
            
            # Convert to format expected by search algorithms
            product_dicts = []
            for product in products:
                product_dict = {
                    'id': product.external_id,
                    'title': product.title,
                    'description': product.description or '',
                    'category': product.category,
                    'price': {
                        'value': str(product.price_value), 
                        'currency': product.price_currency
                    },
                    'brand': product.brand or '',
                    'model': product.model or '',
                    'sku': product.sku or '',
                    'condition': product.condition,
                    'seller': {'username': product.seller_name or ''},
                    'location': product.seller_location or '',
                    'url': product.product_url or '',
                    'image_url': product.image_url or '',
                    'tags': product.tags or '',
                    'rating': product.rating,
                    'review_count': product.review_count
                }
                product_dicts.append(product_dict)
            
            logger.info("✅ Loaded %d products from database", len(product_dicts))
            return product_dicts
    
    def load_search_queries_from_database(self) -> List[str]:
        """Load search queries from database."""
        logger.info("🔍 Loading search queries from database...")
        
        with self.db_manager.get_session() as session:
            queries = session.query(SearchQuery).all()
            query_texts = [query.query_text for query in queries]
            
            logger.info("✅ Loaded %d search queries", len(query_texts))
            return query_texts
    
    def create_relevance_judgments(self, products: List[Dict], queries: List[str]):
        """Create relevance judgments for evaluation."""
        logger.info("⚖️ Creating relevance judgments...")
        
        # Create synthetic relevance judgments
        self.relevance_judge.create_synthetic_judgments(queries, products)
        
        logger.info("✅ Created relevance judgments for %d queries", len(queries))
    
    def run_search_algorithms(self, products: List[Dict], queries: List[str]):
        """Run search algorithms and store results in database."""
        logger.info("🚀 Running search algorithms on database products...")
        
        total_results = 0
        
        with self.db_manager.get_session() as session:
            for query_text in queries:
                logger.info("  Processing query: '%s'", query_text)
                
                for algo_name, algorithm in self.algorithms.items():
                    start_time = time.time()
                    
                    try:
                        # Run search
                        results = algorithm.search(query_text, products, limit=20)
                        search_time_ms = (time.time() - start_time) * 1000
                        
                        # Store results in database
                        query_record = session.query(SearchQuery).filter_by(
                            query_text=query_text
                        ).first()
                        
                        if query_record:
                            for rank, result in enumerate(results, 1):
                                # Find product in database
                                product_record = session.query(Product).filter_by(
                                    external_id=result['id']
                                ).first()
                                
                                if product_record:
                                    search_result = SearchResult(
                                        product_id=product_record.id,
                                        query_id=query_record.id,
                                        algorithm_name=algo_name,
                                        algorithm_version='1.0',
                                        relevance_score=result.get('relevance_score', 0.0),
                                        rank_position=rank,
                                        matched_terms=','.join(result.get('matched_terms', [])),
                                        search_time_ms=search_time_ms
                                    )
                                    session.add(search_result)
                                    total_results += 1
                        
                        logger.info("    %s: %d results in %.2fms", 
                                   algo_name, len(results), search_time_ms)
                        
                    except Exception as e:
                        logger.error("    Error with %s: %s", algo_name, e)
                        continue
        
        logger.info("✅ Stored %d search results in database", total_results)
    
    def calculate_evaluation_metrics(self, queries: List[str]):
        """Calculate and store evaluation metrics in database."""
        logger.info("📊 Calculating evaluation metrics...")
        
        with self.db_manager.get_session() as session:
            for query_text in queries:
                query_record = session.query(SearchQuery).filter_by(
                    query_text=query_text
                ).first()
                
                if not query_record:
                    continue
                
                for algo_name in self.algorithms.keys():
                    # Get search results for this query and algorithm
                    search_results = session.query(SearchResult).filter_by(
                        query_id=query_record.id,
                        algorithm_name=algo_name
                    ).order_by(SearchResult.rank_position).all()
                    
                    if not search_results:
                        continue
                    
                    # Get relevance judgments
                    relevant_items = self.relevance_judge.get_relevant_items(
                        query_text, threshold=0.3
                    )
                    
                    # Convert to format expected by metrics calculator
                    retrieved_items = [sr.product.external_id for sr in search_results]
                    relevance_scores = self.relevance_judge.get_relevance_scores(query_text)
                    
                    # Calculate metrics
                    metrics = self.metrics_calculator.calculate_comprehensive_metrics(
                        relevant_items, retrieved_items, [1, 3, 5, 10], relevance_scores
                    )
                    
                    # Calculate average search time
                    avg_search_time = (
                        sum(sr.search_time_ms for sr in search_results) / 
                        len(search_results)
                    )
                    
                    # Store metrics in database
                    evaluation_metrics = EvaluationMetrics(
                        query_id=query_record.id,
                        algorithm_name=algo_name,
                        precision_at_1=metrics.get('precision@1', 0.0),
                        precision_at_3=metrics.get('precision@3', 0.0),
                        precision_at_5=metrics.get('precision@5', 0.0),
                        precision_at_10=metrics.get('precision@10', 0.0),
                        recall_at_1=metrics.get('recall@1', 0.0),
                        recall_at_3=metrics.get('recall@3', 0.0),
                        recall_at_5=metrics.get('recall@5', 0.0),
                        recall_at_10=metrics.get('recall@10', 0.0),
                        f1_score_at_1=metrics.get('f1@1', 0.0),
                        f1_score_at_3=metrics.get('f1@3', 0.0),
                        f1_score_at_5=metrics.get('f1@5', 0.0),
                        f1_score_at_10=metrics.get('f1@10', 0.0),
                        ndcg_at_1=metrics.get('ndcg@1', 0.0),
                        ndcg_at_3=metrics.get('ndcg@3', 0.0),
                        ndcg_at_5=metrics.get('ndcg@5', 0.0),
                        ndcg_at_10=metrics.get('ndcg@10', 0.0),
                        map_score=metrics.get('map', 0.0),
                        mrr_score=metrics.get('mrr', 0.0),
                        avg_search_time_ms=avg_search_time,
                        total_results_returned=len(search_results)
                    )
                    session.add(evaluation_metrics)
        
        logger.info("✅ Calculated and stored evaluation metrics")
    
    def generate_comparison_report(self):
        """Generate a comparison report from database metrics."""
        logger.info("📋 Generating comparison report...")
        
        with self.db_manager.get_session() as session:
            # Get all metrics
            metrics = session.query(EvaluationMetrics).all()
            
            if not metrics:
                logger.warning("No evaluation metrics found in database")
                return
            
            # Group by algorithm
            algorithm_metrics = {}
            for metric in metrics:
                algo_name = metric.algorithm_name
                if algo_name not in algorithm_metrics:
                    algorithm_metrics[algo_name] = []
                algorithm_metrics[algo_name].append(metric)
            
            # Calculate averages
            report = {}
            for algo_name, algo_metrics in algorithm_metrics.items():
                report[algo_name] = {
                    'total_queries': len(algo_metrics),
                    'avg_precision@5': (
                        sum(m.precision_at_5 for m in algo_metrics) / 
                        len(algo_metrics)
                    ),
                    'avg_recall@5': sum(m.recall_at_5 for m in algo_metrics) / len(algo_metrics),
                    'avg_f1@5': sum(m.f1_score_at_5 for m in algo_metrics) / len(algo_metrics),
                    'avg_map': sum(m.map_score for m in algo_metrics) / len(algo_metrics),
                    'avg_mrr': sum(m.mrr_score for m in algo_metrics) / len(algo_metrics),
                    'avg_search_time_ms': (
                        sum(m.avg_search_time_ms for m in algo_metrics) / 
                        len(algo_metrics)
                    ),
                }
            
            # Print report
            print("\n" + "="*60)
            print("SEARCH ALGORITHM COMPARISON REPORT")
            print("="*60)
            
            for algo_name, stats in report.items():
                print(f"\n{algo_name.upper()} Performance:")
                print(f"  Queries Evaluated: {stats['total_queries']}")
                print(f"  Average Precision@5: {stats['avg_precision@5']:.4f}")
                print(f"  Average Recall@5: {stats['avg_recall@5']:.4f}")
                print(f"  Average F1@5: {stats['avg_f1@5']:.4f}")
                print(f"  Average MAP: {stats['avg_map']:.4f}")
                print(f"  Average MRR: {stats['avg_mrr']:.4f}")
                print(f"  Average Search Time: {stats['avg_search_time_ms']:.2f}ms")
            
            # Find best performing algorithm
            best_map_algo = max(report.keys(), key=lambda x: report[x]['avg_map'])
            best_speed_algo = min(report.keys(), key=lambda x: report[x]['avg_search_time_ms'])
            
            print(f"\n🏆 Best Overall Performance (MAP): {best_map_algo}")
            print(f"⚡ Fastest Algorithm: {best_speed_algo}")
            
            return report
    
    def run_full_evaluation(self, product_limit: int = 1000):
        """Run complete evaluation pipeline."""
        logger.info("🚀 Starting full database-based evaluation...")
        
        # Load data
        products = self.load_products_from_database(product_limit)
        queries = self.load_search_queries_from_database()
        
        if not products:
            logger.error("No products found in database!")
            return
        
        if not queries:
            logger.error("No search queries found in database!")
            return
        
        # Create relevance judgments
        self.create_relevance_judgments(products, queries)
        
        # Run search algorithms
        self.run_search_algorithms(products, queries)
        
        # Calculate metrics
        self.calculate_evaluation_metrics(queries)
        
        # Generate report
        self.generate_comparison_report()
        
        logger.info("✅ Full evaluation complete!")


def main():
    """Main function."""
    print("🔍 Database-Based Search Algorithm Evaluation")
    print("="*60)
    print("Running search algorithms on database-stored e-commerce data")
    print("Perfect for large-scale research evaluation!")
    print()
    
    # Initialize evaluator
    evaluator = DatabaseSearchEvaluator()
    
    # Get database info
    db_info = evaluator.db_manager.get_database_info()
    print(f"📁 Database: {db_info['database_type']}")
    print(f"📊 Products: {db_info['stats'].get('products', 0)}")
    print(f"🔍 Queries: {db_info['stats'].get('search_queries', 0)}")
    print()
    
    # Run evaluation
    try:
        evaluator.run_full_evaluation(product_limit=1000)  # Limit for demo
        
        print("\n🎯 Next steps:")
        print("1. Analyze detailed results:")
        print("   python analyze_database_results.py")
        print("2. Export results to JSON:")
        print("   python export_database_results.py")
        print("3. View database directly:")
        print("   sqlite3 data/ecommerce_research.db")
        
    except Exception as e:
        logger.error("Evaluation failed: %s", e)
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
