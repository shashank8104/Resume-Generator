import numpy as np
from typing import Dict, Any, Optional, List
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings

from ..models.resume_schema import Resume
from ..models.job_schema import JobDescription
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

# Suppress sklearn warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

class EmbeddingGenerator:
    """Generate embeddings for resumes and job descriptions"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=self.config.get('tfidf_max_features', 1000),
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        # Flag to track if vectorizer is fitted
        self.vectorizer_fitted = False
        
        logger.info("Embedding generator initialized")
    
    def generate_resume_embeddings(self, resume: Resume) -> Dict[str, np.ndarray]:
        """Generate embeddings for different resume sections"""
        embeddings = {}
        
        # Skills embedding
        skills_text = ' '.join([skill for skills in resume.skills.values() for skill in skills])
        embeddings['skills'] = self._generate_text_embedding(skills_text)
        
        # Experience embedding
        experience_text = ' '.join([' '.join(exp.description) for exp in resume.experience])
        embeddings['experience'] = self._generate_text_embedding(experience_text)
        
        # Education embedding
        education_text = ' '.join([f"{edu.degree} {edu.major or ''}" for edu in resume.education])
        embeddings['education'] = self._generate_text_embedding(education_text)
        
        # Projects embedding
        projects_text = ' '.join([f"{proj.name} {proj.description}" for proj in resume.projects])
        embeddings['projects'] = self._generate_text_embedding(projects_text)
        
        # Full resume embedding
        full_text = f"{resume.summary or ''} {skills_text} {experience_text} {education_text} {projects_text}"
        embeddings['full_resume'] = self._generate_text_embedding(full_text)
        
        return embeddings
    
    def generate_job_embeddings(self, job_description: JobDescription) -> Dict[str, np.ndarray]:
        """Generate embeddings for different job description sections"""
        embeddings = {}
        
        # Skills embedding
        skills_text = ' '.join(job_description.required_skills + job_description.preferred_skills)
        embeddings['skills'] = self._generate_text_embedding(skills_text)
        
        # Requirements embedding
        requirements_text = ' '.join(job_description.requirements + job_description.preferred_qualifications)
        embeddings['requirements'] = self._generate_text_embedding(requirements_text)
        
        # Responsibilities embedding
        responsibilities_text = ' '.join(job_description.responsibilities)
        embeddings['responsibilities'] = self._generate_text_embedding(responsibilities_text)
        
        # Full job embedding
        full_text = f"{job_description.description} {skills_text} {requirements_text} {responsibilities_text}"
        embeddings['full_job'] = self._generate_text_embedding(full_text)
        
        return embeddings
    
    def _generate_text_embedding(self, text: str) -> np.ndarray:
        """Generate TF-IDF embedding for text"""
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.config.get('tfidf_max_features', 1000))
        
        try:
            if not self.vectorizer_fitted:
                # For first use, fit and transform
                embedding = self.tfidf_vectorizer.fit_transform([text]).toarray()[0]
                self.vectorizer_fitted = True
            else:
                # For subsequent uses, just transform
                embedding = self.tfidf_vectorizer.transform([text]).toarray()[0]
            
            return embedding
            
        except Exception as e:
            logger.warning(f"Error generating embedding: {e}")
            # Return zero vector on error
            return np.zeros(self.config.get('tfidf_max_features', 1000))
    
    def batch_generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts efficiently"""
        if not texts:
            return []
        
        try:
            if not self.vectorizer_fitted:
                embeddings = self.tfidf_vectorizer.fit_transform(texts).toarray()
                self.vectorizer_fitted = True
            else:
                embeddings = self.tfidf_vectorizer.transform(texts).toarray()
            
            return [emb for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Error in batch embedding generation: {e}")
            # Return zero vectors on error
            zero_vector = np.zeros(self.config.get('tfidf_max_features', 1000))
            return [zero_vector for _ in texts]
    
    def get_embedding_dimensions(self) -> int:
        """Get the dimensionality of generated embeddings"""
        return self.config.get('tfidf_max_features', 1000)
    
    def reset_vectorizer(self):
        """Reset the TF-IDF vectorizer (useful for testing)"""
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=self.config.get('tfidf_max_features', 1000),
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.vectorizer_fitted = False
        logger.info("Vectorizer reset")