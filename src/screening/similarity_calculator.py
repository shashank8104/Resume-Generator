import numpy as np
from typing import Union, List
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

# Suppress sklearn warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

class SimilarityCalculator:
    """Calculate various similarity metrics between embeddings and texts"""
    
    def __init__(self, config=None):
        self.config = config or {}
        logger.info("Similarity calculator initialized")
    
    def calculate_cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Ensure embeddings are 2D for sklearn
            if embedding1.ndim == 1:
                embedding1 = embedding1.reshape(1, -1)
            if embedding2.ndim == 1:
                embedding2 = embedding2.reshape(1, -1)
            
            # Handle zero vectors
            if np.allclose(embedding1, 0) or np.allclose(embedding2, 0):
                return 0.0
            
            similarity = cosine_similarity(embedding1, embedding2)[0][0]
            return float(np.clip(similarity, 0.0, 1.0))
            
        except Exception as e:
            logger.warning(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Calculate TF-IDF based similarity between two texts"""
        try:
            if not text1.strip() or not text2.strip():
                return 0.0
            
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(np.clip(similarity, 0.0, 1.0))
            
        except Exception as e:
            logger.warning(f"Error calculating TF-IDF similarity: {e}")
            return 0.0
    
    def calculate_jaccard_similarity(self, set1: set, set2: set) -> float:
        """Calculate Jaccard similarity between two sets"""
        try:
            if not set1 and not set2:
                return 1.0  # Both empty sets are identical
            
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            return float(intersection / union) if union > 0 else 0.0
            
        except Exception as e:
            logger.warning(f"Error calculating Jaccard similarity: {e}")
            return 0.0
    
    def calculate_weighted_similarity(
        self, 
        similarities: List[float], 
        weights: List[float]
    ) -> float:
        """Calculate weighted average of multiple similarity scores"""
        try:
            if len(similarities) != len(weights):
                logger.warning("Mismatch between similarities and weights length")
                return 0.0
            
            if not similarities:
                return 0.0
            
            # Normalize weights
            total_weight = sum(weights)
            if total_weight == 0:
                return 0.0
            
            normalized_weights = [w / total_weight for w in weights]
            
            # Calculate weighted average
            weighted_sum = sum(s * w for s, w in zip(similarities, normalized_weights))
            return float(np.clip(weighted_sum, 0.0, 1.0))
            
        except Exception as e:
            logger.warning(f"Error calculating weighted similarity: {e}")
            return 0.0
    
    def calculate_batch_similarities(
        self, 
        base_embedding: np.ndarray, 
        other_embeddings: List[np.ndarray]
    ) -> List[float]:
        """Calculate similarity between one embedding and multiple others"""
        similarities = []
        
        for embedding in other_embeddings:
            similarity = self.calculate_cosine_similarity(base_embedding, embedding)
            similarities.append(similarity)
        
        return similarities
    
    def find_most_similar(
        self, 
        query_embedding: np.ndarray, 
        candidate_embeddings: List[np.ndarray]
    ) -> tuple:
        """Find the most similar embedding from candidates"""
        if not candidate_embeddings:
            return -1, 0.0
        
        similarities = self.calculate_batch_similarities(query_embedding, candidate_embeddings)
        max_index = np.argmax(similarities)
        max_similarity = similarities[max_index]
        
        return int(max_index), float(max_similarity)