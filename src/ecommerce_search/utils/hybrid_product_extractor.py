"""
Hybrid Product Information Extraction Utilities

This module provides advanced NLP-based product extraction functionality
using multiple approaches: POS tagging, NER, context-aware extraction,
and machine learning for robust product name identification.
"""

import re
import string
import logging
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter

# Optional imports for advanced NLP
try:
    import nltk
    from nltk import pos_tag, word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

# Constants for product extraction
PRODUCT_KEYWORDS = ['product', 'item', 'buy', 'purchase', 'review', 'recommend']
BRAND_PATTERNS = [r'\b(apple|samsung|sony|nike|adidas|microsoft|google|amazon|breville|dyson|kitchenaid)\b']
CATEGORY_PATTERNS = {
    'electronics': ['phone', 'laptop', 'computer', 'tablet', 'headphones', 'speaker', 'camera'],
    'clothing': ['shirt', 'pants', 'shoes', 'dress', 'jacket', 'hoodie', 'sweater'],
    'home': ['furniture', 'appliance', 'decor', 'kitchen', 'coffee', 'maker', 'blender', 'toaster'],
    'beauty': ['skincare', 'makeup', 'shampoo', 'lotion', 'cream'],
    'sports': ['gym', 'fitness', 'running', 'yoga', 'equipment']
}
PRICE_PATTERNS = [r'\$(\d+(?:\.\d{2})?)', r'(\d+(?:\.\d{2})?)\s*dollars?']
POSITIVE_WORDS = ['good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'fantastic', 'wonderful']
NEGATIVE_WORDS = ['bad', 'terrible', 'awful', 'hate', 'worst', 'disappointed', 'horrible', 'useless']
REVIEW_INDICATORS = ['review', 'rating', 'stars', 'opinion', 'experience', 'tested', 'tried']
RECOMMENDATION_INDICATORS = ['recommend', 'suggest', 'advise', 'should buy', 'worth it', 'must have']

# Product context indicators
PRODUCT_CONTEXTS = [
    'bought', 'purchased', 'ordered', 'got', 'received', 'bought this',
    'review', 'recommend', 'suggest', 'love', 'hate', 'worth', 'value',
    'quality', 'price', 'cost', 'amazing', 'terrible', 'perfect'
]

# Product indicators for POS tagging
PRODUCT_INDICATORS = [
    'maker', 'machine', 'device', 'tool', 'appliance', 'gadget', 
    'equipment', 'gear', 'item', 'product', 'phone', 'laptop', 
    'headphones', 'shoes', 'book', 'coffee', 'blender', 'toaster'
]

logger = logging.getLogger(__name__)


class HybridProductExtractor:
    """Advanced product information extraction using multiple NLP approaches."""

    def __init__(self):
        """Initialize the hybrid product extractor."""
        self._init_patterns()
        self._init_nlp_models()

    def _init_patterns(self):
        """Initialize all regex patterns and keyword lists."""
        self.product_keywords = PRODUCT_KEYWORDS
        self.brand_patterns = BRAND_PATTERNS
        self.category_patterns = CATEGORY_PATTERNS
        self.price_patterns = PRICE_PATTERNS
        self.positive_words = POSITIVE_WORDS
        self.negative_words = NEGATIVE_WORDS
        self.review_indicators = REVIEW_INDICATORS
        self.recommendation_indicators = RECOMMENDATION_INDICATORS
        self.product_contexts = PRODUCT_CONTEXTS
        self.product_indicators = PRODUCT_INDICATORS

    def _init_nlp_models(self):
        """Initialize NLP models."""
        self.nlp_spacy = None
        self.nltk_available = NLTK_AVAILABLE
        self.spacy_available = SPACY_AVAILABLE
        
        if self.spacy_available:
            try:
                self.nlp_spacy = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except OSError:
                logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
                self.spacy_available = False
        
        if self.nltk_available:
            try:
                # Download required NLTK data
                nltk.download('punkt', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                nltk.download('stopwords', quiet=True)
                logger.info("NLTK models loaded successfully")
            except Exception as e:
                logger.warning(f"NLTK initialization failed: {e}")
                self.nltk_available = False

    def extract_product_info(self, text: str) -> Dict[str, Any]:
        """
        Extract comprehensive product information using hybrid approach.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary containing extracted product information
        """
        if not text or not text.strip():
            return self._empty_result()

        # Clean and normalize text
        text_lower = text.lower()

        # Extract all components using hybrid approach
        product_name = self._extract_product_name_hybrid(text, text_lower)
        brands = self._extract_brands(text_lower)
        category = self._extract_category(text_lower)
        prices = self._extract_prices(text_lower)
        sentiment = self._extract_sentiment(text_lower)
        is_review = self._is_review(text_lower)
        is_recommendation = self._is_recommendation(text_lower)
        tags = self._generate_tags(
            brands, category, prices, sentiment, is_review, is_recommendation
        )

        return {
            'product_name': product_name,
            'brand': brands[0] if brands else None,
            'category': category,
            'price_mentioned': prices[0] if prices else None,
            'sentiment_score': sentiment,
            'is_review': is_review,
            'is_recommendation': is_recommendation,
            'tags': tags
        }

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
        
        # Method 4: Pattern-based (fallback)
        pattern_result = self._extract_product_name_patterns(text_lower)
        if pattern_result:
            candidates.append(('pattern', pattern_result, 0.6))
        
        # Select best candidate based on confidence scores
        if candidates:
            best_method, best_name, best_score = max(candidates, key=lambda x: x[2])
            logger.debug(f"Selected product name '{best_name}' using {best_method} method (score: {best_score})")
            return best_name
        
        return None

    def _extract_product_name_pos(self, text: str) -> Optional[str]:
        """Extract product name using POS tagging."""
        try:
            tokens = word_tokenize(text.lower())
            pos_tags = pos_tag(tokens)
            
            # Look for noun phrases
            product_candidates = []
            for i, (word, pos) in enumerate(pos_tags):
                if pos in ['NN', 'NNS', 'NNP', 'NNPS']:  # Nouns
                    if self._is_product_noun(word):
                        # Try to get compound nouns
                        compound = self._extract_compound_noun(pos_tags, i)
                        if compound:
                            product_candidates.append(compound)
                        else:
                            product_candidates.append(word)
            
            # Return the most likely product name
            return self._select_best_product_name(product_candidates, text)
            
        except Exception as e:
            logger.warning(f"POS tagging failed: {e}")
            return None

    def _extract_product_name_ner(self, text: str) -> Optional[str]:
        """Extract product name using Named Entity Recognition."""
        try:
            doc = self.nlp_spacy(text)
            
            # Look for PRODUCT entities or noun phrases
            for ent in doc.ents:
                if ent.label_ in ['PRODUCT', 'ORG', 'WORK_OF_ART']:
                    if self._is_likely_product(ent.text):
                        return ent.text.lower()
            
            # Fallback to noun phrase extraction
            for chunk in doc.noun_chunks:
                if self._is_likely_product(chunk.text):
                    return chunk.text.lower()
            
            return None
            
        except Exception as e:
            logger.warning(f"NER extraction failed: {e}")
            return None

    def _extract_product_name_context(self, text: str, text_lower: str) -> Optional[str]:
        """Extract product name using contextual clues."""
        # Find sentences with product context
        sentences = text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence contains product context
            has_context = any(context in sentence_lower for context in self.product_contexts)
            if not has_context:
                continue
            
            # Extract potential product names from this sentence
            product_name = self._extract_from_sentence(sentence)
            if product_name:
                return product_name
        
        return None

    def _extract_from_sentence(self, sentence: str) -> Optional[str]:
        """Extract product name from a single sentence."""
        sentence_lower = sentence.lower()
        
        # Look for compound product names
        compound_patterns = [
            r'\b(coffee\s+maker)\b',
            r'\b(blender\s+machine)\b',
            r'\b(gaming\s+headset)\b',
            r'\b(running\s+shoes)\b',
            r'\b(phone\s+case)\b',
            r'\b(laptop\s+bag)\b',
            r'\b(bluetooth\s+speaker)\b'
        ]
        
        for pattern in compound_patterns:
            matches = re.findall(pattern, sentence_lower)
            if matches:
                return matches[0]
        
        # Look for single product words
        words = sentence_lower.split()
        for word in words:
            if self._is_product_noun(word):
                return word
        
        return None

    def _extract_product_name_patterns(self, text_lower: str) -> Optional[str]:
        """Extract product name using pattern-based approach (original method)."""
        # Look for specific product types first
        for product_type in self.product_indicators:
            if product_type in text_lower:
                return product_type
        
        # Look for brand + product combinations
        for brand_pattern in self.brand_patterns:
            matches = re.findall(brand_pattern, text_lower)
            if matches:
                return matches[0]
        
        # Fallback to first meaningful word
        words = text_lower.split()
        for word in words:
            if len(word) > 3 and word.isalpha():
                return word
        
        return None

    def _is_product_noun(self, word: str) -> bool:
        """Check if a noun is likely to be a product."""
        return any(indicator in word for indicator in self.product_indicators)

    def _is_likely_product(self, text: str) -> bool:
        """Determine if text is likely a product name."""
        text_lower = text.lower()
        
        # Product indicators
        has_product_word = any(word in text_lower for word in self.product_indicators)
        
        # Brand indicators
        brand_indicators = ['co', 'corp', 'inc', 'ltd', 'brand', 'company']
        has_brand_indicator = any(indicator in text_lower for indicator in brand_indicators)
        
        # Length and structure heuristics
        words = text_lower.split()
        is_compound = len(words) >= 2
        is_reasonable_length = 2 <= len(text) <= 50
        
        return (has_product_word or has_brand_indicator) and is_compound and is_reasonable_length

    def _extract_compound_noun(self, pos_tags, start_idx):
        """Extract compound nouns like 'coffee maker'."""
        compound = []
        for i in range(start_idx, len(pos_tags)):
            word, pos = pos_tags[i]
            if pos in ['NN', 'NNS', 'NNP', 'NNPS']:
                compound.append(word)
            else:
                break
        return ' '.join(compound) if len(compound) > 1 else None

    def _select_best_product_name(self, candidates: List[str], original_text: str) -> Optional[str]:
        """Select the best product name from candidates."""
        if not candidates:
            return None
        
        # Score candidates based on various factors
        scored_candidates = []
        for candidate in candidates:
            score = self._score_product_candidate(candidate, original_text)
            scored_candidates.append((candidate, score))
        
        # Return the highest scoring candidate
        best_candidate, best_score = max(scored_candidates, key=lambda x: x[1])
        return best_candidate if best_score > 0.3 else None

    def _score_product_candidate(self, candidate: str, original_text: str) -> float:
        """Score a product name candidate."""
        score = 0.0
        candidate_lower = candidate.lower()
        
        # Length preference (not too short, not too long)
        if 3 <= len(candidate) <= 30:
            score += 0.3
        
        # Product indicator words
        if any(indicator in candidate_lower for indicator in self.product_indicators):
            score += 0.4
        
        # Brand patterns
        if any(re.search(pattern, candidate_lower) for pattern in self.brand_patterns):
            score += 0.3
        
        # Compound nouns (prefer compound over single words)
        if ' ' in candidate:
            score += 0.2
        
        # Avoid common words
        common_words = ['the', 'this', 'that', 'just', 'bought', 'got', 'amazing']
        if not any(word in candidate_lower for word in common_words):
            score += 0.1
        
        return score

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            'product_name': None,
            'brand': None,
            'category': None,
            'price_mentioned': None,
            'sentiment_score': 0.0,
            'is_review': False,
            'is_recommendation': False,
            'tags': []
        }

    def _extract_brands(self, text_lower: str) -> List[str]:
        """Extract brand names from text."""
        brands = []
        for pattern in self.brand_patterns:
            matches = re.findall(pattern, text_lower)
            brands.extend(matches)
        return list(set(brands))

    def _extract_category(self, text_lower: str) -> Optional[str]:
        """Extract product category from text."""
        for category, keywords in self.category_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        return None

    def _extract_prices(self, text_lower: str) -> List[float]:
        """Extract price information from text."""
        prices = []
        for pattern in self.price_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    price_str = match.replace('$', '').replace(',', '').strip()
                    if price_str and price_str.replace('.', '').isdigit():
                        price = float(price_str)
                        if price > 0:
                            prices.append(price)
                except (ValueError, AttributeError):
                    continue
        return prices

    def _extract_sentiment(self, text_lower: str) -> float:
        """Extract sentiment score from text."""
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        total_words = len(text_lower.split())
        if total_words == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / max(total_words, 1)
        return max(-1.0, min(1.0, sentiment))

    def _is_review(self, text_lower: str) -> bool:
        """Check if text appears to be a product review."""
        return any(indicator in text_lower for indicator in self.review_indicators)

    def _is_recommendation(self, text_lower: str) -> bool:
        """Check if text appears to be a recommendation."""
        return any(indicator in text_lower for indicator in self.recommendation_indicators)

    def _generate_tags(self, brands: List[str], category: Optional[str],
                      prices: List[float], sentiment: float,
                      is_review: bool, is_recommendation: bool) -> List[str]:
        """Generate tags based on extracted information."""
        tags = []
        
        # Add brand tags
        tags.extend(brands)
        
        # Add category tag
        if category:
            tags.append(category)
        
        # Add price tag if found
        if prices:
            tags.append(f"price_{int(prices[0])}")
        
        # Add sentiment tag
        if sentiment > 0.1:
            tags.append("positive")
        elif sentiment < -0.1:
            tags.append("negative")
        else:
            tags.append("neutral")
        
        # Add review/recommendation tags
        if is_review:
            tags.append("review")
        if is_recommendation:
            tags.append("recommendation")
        
        return list(set(tags))
