"""
E-commerce Search Algorithm Comparison

A comprehensive system for comparing and evaluating different search algorithms
on e-commerce product data.
"""

__version__ = "1.0.0"
__author__ = "COMP5112 Group 7"
__email__ = "group7@comp5112.edu"

from .algorithms import KeywordSearch, TFIDFSearch
from .database import get_db_manager
from .evaluation import SearchMetrics, RelevanceJudgment

__all__ = [
    "KeywordSearch",
    "TFIDFSearch", 
    "get_db_manager",
    "SearchMetrics",
    "RelevanceJudgment"
]
