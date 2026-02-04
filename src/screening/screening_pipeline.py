import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import time

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from ..models.resume_schema import Resume
from ..models.job_schema import JobDescription
from ..models.api_schema import ScreeningResult, SectionScore
from ..utils.logging_utils import get_logger
from .embedding_generator import EmbeddingGenerator
from .feature_extractor import FeatureExtractor
from .similarity_calculator import SimilarityCalculator

logger = get_logger(__name__)

class ScreeningPipeline:
    """
    Complete ML-based resume screening pipeline with section-wise scoring
    and weighted score aggregation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize components
        self.embedding_generator = EmbeddingGenerator(config)
        self.feature_extractor = FeatureExtractor(config)
        self.similarity_calculator = SimilarityCalculator(config)
        
        # Section weights for final score calculation
        self.section_weights = self.config.get("similarity_weights", {
            "skills": 0.35,
            "experience": 0.25,
            "education": 0.15,
            "projects": 0.15,
            "keywords": 0.10
        })
        
        # Initialize ML models
        self.binary_classifier = None
        self.is_trained = False
        
        logger.info("Screening pipeline initialized")
    
    def screen_resume(
        self, 
        resume: Resume, 
        job_description: JobDescription,
        explain: bool = True
    ) -> ScreeningResult:
        """
        Screen a resume against a job description with detailed analysis
        
        Args:
            resume: Resume object to screen
            job_description: Target job description
            explain: Whether to provide detailed explanations
            
        Returns:
            ScreeningResult with scores and explanations
        """
        start_time = time.time()
        logger.info(f"Screening resume for position: {job_description.title}")
        
        # Extract features from both resume and job description
        resume_features = self.feature_extractor.extract_resume_features(resume)
        job_features = self.feature_extractor.extract_job_features(job_description)
        
        # Generate embeddings
        resume_embeddings = self.embedding_generator.generate_resume_embeddings(resume)
        job_embeddings = self.embedding_generator.generate_job_embeddings(job_description)
        
        # Calculate section-wise similarities
        section_scores = self._calculate_section_scores(
            resume, job_description, resume_features, job_features, 
            resume_embeddings, job_embeddings, explain
        )
        
        # Calculate overall score using weighted aggregation
        overall_score = self._calculate_weighted_score(section_scores)
        
        # Generate skill gap analysis
        skill_gaps = self._analyze_skill_gaps(resume, job_description)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(section_scores, skill_gaps)
        
        # Generate detailed explanation
        match_explanation = self._generate_match_explanation(
            section_scores, overall_score, skill_gaps
        ) if explain else ""
        
        # Binary classification prediction (if model is trained)
        binary_prediction = self._get_binary_prediction(
            resume_features, job_features
        ) if self.is_trained else None
        
        processing_time = time.time() - start_time
        
        result = ScreeningResult(
            overall_score=float(overall_score),
            section_scores=section_scores,
            skill_gaps=skill_gaps,
            recommendations=recommendations,
            match_explanation=match_explanation,
            processed_at=datetime.now(),
            model_version=self.config.get("model_version", "1.0")
        )
        
        logger.info(f"Resume screening completed in {processing_time:.2f}s. Score: {overall_score:.3f}")
        
        return result
    
    def batch_screen_resumes(
        self,
        resumes: List[Resume],
        job_description: JobDescription,
        explain: bool = False
    ) -> List[ScreeningResult]:
        """Screen multiple resumes against a job description"""
        logger.info(f"Batch screening {len(resumes)} resumes")
        
        results = []
        for i, resume in enumerate(resumes):
            try:
                result = self.screen_resume(resume, job_description, explain)
                results.append(result)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(resumes)} resumes")
                    
            except Exception as e:
                logger.error(f"Error screening resume {i}: {e}")
                # Create a default result for failed screening
                results.append(ScreeningResult(
                    overall_score=0.0,
                    section_scores={},
                    skill_gaps=[],
                    recommendations=["Resume screening failed - please check format"],
                    match_explanation="Error during processing",
                    processed_at=datetime.now(),
                    model_version=self.config.get("model_version", "1.0")
                ))
        
        logger.info(f"Batch screening completed. {len(results)} results generated")
        return results
    
    def _calculate_section_scores(
        self,
        resume: Resume,
        job_description: JobDescription,
        resume_features: Dict[str, Any],
        job_features: Dict[str, Any],
        resume_embeddings: Dict[str, np.ndarray],
        job_embeddings: Dict[str, np.ndarray],
        explain: bool
    ) -> Dict[str, SectionScore]:
        """Calculate similarity scores for each resume section"""
        
        section_scores = {}
        
        # Skills section scoring
        section_scores["skills"] = self._score_skills_section(
            resume, job_description, resume_embeddings, job_embeddings, explain
        )
        
        # Experience section scoring
        section_scores["experience"] = self._score_experience_section(
            resume, job_description, resume_embeddings, job_embeddings, explain
        )
        
        # Education section scoring
        section_scores["education"] = self._score_education_section(
            resume, job_description, resume_embeddings, job_embeddings, explain
        )
        
        # Projects section scoring
        section_scores["projects"] = self._score_projects_section(
            resume, job_description, resume_embeddings, job_embeddings, explain
        )
        
        # Keyword matching scoring
        section_scores["keywords"] = self._score_keyword_matching(
            resume, job_description, resume_features, job_features, explain
        )
        
        return section_scores
    
    def _score_skills_section(
        self,
        resume: Resume,
        job_description: JobDescription,
        resume_embeddings: Dict[str, np.ndarray],
        job_embeddings: Dict[str, np.ndarray],
        explain: bool
    ) -> SectionScore:
        """Score skills section match"""
        
        # Get all skills from resume
        resume_skills = [skill for skills in resume.skills.values() for skill in skills]
        job_skills = job_description.required_skills + job_description.preferred_skills
        
        # Direct skill matching
        matched_skills = list(set(resume_skills) & set(job_skills))
        missing_skills = list(set(job_skills) - set(resume_skills))
        
        # Calculate similarity using embeddings
        if "skills" in resume_embeddings and "skills" in job_embeddings:
            embedding_similarity = self.similarity_calculator.calculate_cosine_similarity(
                resume_embeddings["skills"], job_embeddings["skills"]
            )
        else:
            embedding_similarity = 0.0
        
        # Combine direct match with embedding similarity
        direct_match_score = len(matched_skills) / max(len(job_skills), 1) if job_skills else 0.0
        combined_score = 0.7 * direct_match_score + 0.3 * embedding_similarity
        
        # Generate feedback
        if explain:
            if matched_skills:
                feedback = f"Strong match in {len(matched_skills)} key skills: {', '.join(matched_skills[:5])}. "
            else:
                feedback = "Limited direct skill matches found. "
            
            if missing_skills:
                feedback += f"Consider adding: {', '.join(missing_skills[:3])}."
        else:
            feedback = f"Skills match: {len(matched_skills)}/{len(job_skills)}"
        
        return SectionScore(
            score=float(np.clip(combined_score, 0.0, 1.0)),
            matched_keywords=matched_skills[:10],  # Limit for readability
            missing_keywords=missing_skills[:10],
            feedback=feedback
        )
    
    def _score_experience_section(
        self,
        resume: Resume,
        job_description: JobDescription,
        resume_embeddings: Dict[str, np.ndarray],
        job_embeddings: Dict[str, np.ndarray],
        explain: bool
    ) -> SectionScore:
        """Score work experience relevance"""
        
        # Extract experience text
        experience_text = " ".join([
            " ".join(exp.description) for exp in resume.experience
        ])
        
        # Extract job responsibilities and requirements
        job_text = " ".join(job_description.responsibilities + job_description.requirements)
        
        # Calculate embedding similarity
        if "experience" in resume_embeddings and "responsibilities" in job_embeddings:
            embedding_similarity = self.similarity_calculator.calculate_cosine_similarity(
                resume_embeddings["experience"], job_embeddings["responsibilities"]
            )
        else:
            embedding_similarity = 0.0
        
        # TF-IDF based similarity
        tfidf_similarity = self.similarity_calculator.calculate_tfidf_similarity(
            experience_text, job_text
        )
        
        # Experience level matching
        experience_years = len(resume.experience) * 2  # Simplified calculation
        required_experience = self._extract_required_experience(job_description)
        experience_match = min(experience_years / max(required_experience, 1), 1.0)
        
        # Combined score
        combined_score = 0.4 * embedding_similarity + 0.4 * tfidf_similarity + 0.2 * experience_match
        
        # Keyword analysis
        matched_keywords = self._find_common_keywords(experience_text, job_text)
        missing_keywords = self._find_missing_keywords(experience_text, job_text)
        
        # Generate feedback
        if explain:
            feedback = f"Experience shows {experience_years} years in relevant roles. "
            if matched_keywords:
                feedback += f"Strong alignment in: {', '.join(matched_keywords[:3])}. "
            if missing_keywords:
                feedback += f"Consider highlighting: {', '.join(missing_keywords[:3])}."
        else:
            feedback = f"Experience relevance: {combined_score:.1%}"
        
        return SectionScore(
            score=float(np.clip(combined_score, 0.0, 1.0)),
            matched_keywords=matched_keywords[:10],
            missing_keywords=missing_keywords[:10],
            feedback=feedback
        )
    
    def _score_education_section(
        self,
        resume: Resume,
        job_description: JobDescription,
        resume_embeddings: Dict[str, np.ndarray],
        job_embeddings: Dict[str, np.ndarray],
        explain: bool
    ) -> SectionScore:
        """Score educational background relevance"""
        
        # Check for degree requirements
        education_score = 0.0
        matched_keywords = []
        missing_keywords = []
        
        if resume.education:
            # Check if education meets basic requirements
            has_bachelor = any(edu.level.value in ["bachelor", "master", "doctorate"] for edu in resume.education)
            if has_bachelor:
                education_score += 0.6
            
            # Check field relevance
            education_fields = [edu.major or edu.degree for edu in resume.education if edu.major or edu.degree]
            relevant_fields = ["computer science", "engineering", "data science", "mathematics", "technology"]
            
            field_match = any(
                any(field.lower() in (edu_field or "").lower() for field in relevant_fields)
                for edu_field in education_fields
            )
            
            if field_match:
                education_score += 0.3
                matched_keywords.extend([field for field in education_fields if field])
            
            # Check for advanced degrees
            has_advanced = any(edu.level.value in ["master", "doctorate"] for edu in resume.education)
            if has_advanced:
                education_score += 0.1
        
        # Identify missing educational requirements
        job_requirements_text = " ".join(job_description.requirements).lower()
        if "bachelor" in job_requirements_text and not any(edu.level.value == "bachelor" for edu in resume.education):
            missing_keywords.append("Bachelor's degree")
        if "master" in job_requirements_text and not any(edu.level.value == "master" for edu in resume.education):
            missing_keywords.append("Master's degree")
        
        # Generate feedback
        if explain:
            if resume.education:
                highest_degree = max(resume.education, key=lambda x: ["high_school", "associate", "bachelor", "master", "doctorate"].index(x.level.value))
                feedback = f"Education: {highest_degree.degree} from {highest_degree.institution}. "
                if field_match:
                    feedback += "Relevant field of study. "
                else:
                    feedback += "Consider highlighting relevant coursework. "
            else:
                feedback = "No education information provided. "
        else:
            feedback = f"Education match: {education_score:.1%}"
        
        return SectionScore(
            score=float(np.clip(education_score, 0.0, 1.0)),
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            feedback=feedback
        )
    
    def _score_projects_section(
        self,
        resume: Resume,
        job_description: JobDescription,
        resume_embeddings: Dict[str, np.ndarray],
        job_embeddings: Dict[str, np.ndarray],
        explain: bool
    ) -> SectionScore:
        """Score projects section relevance"""
        
        if not resume.projects:
            return SectionScore(
                score=0.0,
                matched_keywords=[],
                missing_keywords=["Personal projects", "Portfolio"],
                feedback="No projects listed. Consider adding relevant projects to showcase skills."
            )
        
        # Extract project technologies and descriptions
        project_technologies = [tech for proj in resume.projects for tech in proj.technologies]
        project_descriptions = " ".join([proj.description for proj in resume.projects])
        
        # Match with job requirements
        job_skills = job_description.required_skills + job_description.preferred_skills
        matched_technologies = list(set(project_technologies) & set(job_skills))
        
        # Calculate relevance score
        technology_match = len(matched_technologies) / max(len(job_skills), 1) if job_skills else 0.0
        
        # Description similarity
        job_text = " ".join(job_description.responsibilities + job_description.requirements)
        description_similarity = self.similarity_calculator.calculate_tfidf_similarity(
            project_descriptions, job_text
        )
        
        # Combined score
        combined_score = 0.6 * technology_match + 0.4 * description_similarity
        
        # Missing technologies
        missing_technologies = list(set(job_skills) - set(project_technologies))
        
        # Generate feedback
        if explain:
            feedback = f"Projects demonstrate {len(matched_technologies)} relevant technologies. "
            if matched_technologies:
                feedback += f"Strong alignment: {', '.join(matched_technologies[:3])}. "
            if missing_technologies:
                feedback += f"Consider projects with: {', '.join(missing_technologies[:2])}."
        else:
            feedback = f"Project relevance: {combined_score:.1%}"
        
        return SectionScore(
            score=float(np.clip(combined_score, 0.0, 1.0)),
            matched_keywords=matched_technologies[:10],
            missing_keywords=missing_technologies[:10],
            feedback=feedback
        )
    
    def _score_keyword_matching(
        self,
        resume: Resume,
        job_description: JobDescription,
        resume_features: Dict[str, Any],
        job_features: Dict[str, Any],
        explain: bool
    ) -> SectionScore:
        """Score overall keyword matching between resume and job"""
        
        # Extract all text from resume
        resume_text = self._extract_full_resume_text(resume)
        
        # Extract all text from job description
        job_text = f"{job_description.description} {' '.join(job_description.requirements)} {' '.join(job_description.responsibilities)}"
        
        # Calculate TF-IDF similarity
        tfidf_similarity = self.similarity_calculator.calculate_tfidf_similarity(
            resume_text, job_text
        )
        
        # Find common important keywords
        resume_keywords = self._extract_keywords(resume_text)
        job_keywords = self._extract_keywords(job_text)
        
        matched_keywords = list(set(resume_keywords) & set(job_keywords))
        missing_keywords = list(set(job_keywords) - set(resume_keywords))
        
        # Keyword density score
        keyword_density = len(matched_keywords) / max(len(job_keywords), 1) if job_keywords else 0.0
        
        # Combined score
        combined_score = 0.7 * tfidf_similarity + 0.3 * keyword_density
        
        # Generate feedback
        if explain:
            feedback = f"Keyword analysis shows {len(matched_keywords)} matches out of {len(job_keywords)} key terms. "
            if missing_keywords:
                feedback += f"Consider incorporating: {', '.join(missing_keywords[:5])}."
        else:
            feedback = f"Keyword match: {combined_score:.1%}"
        
        return SectionScore(
            score=float(np.clip(combined_score, 0.0, 1.0)),
            matched_keywords=matched_keywords[:15],
            missing_keywords=missing_keywords[:15],
            feedback=feedback
        )
    
    def _calculate_weighted_score(self, section_scores: Dict[str, SectionScore]) -> float:
        """Calculate weighted overall score from section scores"""
        
        total_score = 0.0
        total_weight = 0.0
        
        for section, weight in self.section_weights.items():
            if section in section_scores:
                total_score += section_scores[section].score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _analyze_skill_gaps(self, resume: Resume, job_description: JobDescription) -> List[str]:
        """Analyze critical skill gaps"""
        
        resume_skills = {skill.lower() for skills in resume.skills.values() for skill in skills}
        required_skills = {skill.lower() for skill in job_description.required_skills}
        
        # Identify missing required skills
        missing_required = [
            skill for skill in job_description.required_skills
            if skill.lower() not in resume_skills
        ]
        
        # Prioritize based on importance (simplified)
        critical_gaps = missing_required[:5]  # Top 5 missing skills
        
        return critical_gaps
    
    def _generate_recommendations(
        self, 
        section_scores: Dict[str, SectionScore],
        skill_gaps: List[str]
    ) -> List[str]:
        """Generate actionable recommendations based on scores"""
        
        recommendations = []
        
        # Skills recommendations
        if "skills" in section_scores and section_scores["skills"].score < 0.7:
            recommendations.append(
                f"Strengthen skills section by adding: {', '.join(skill_gaps[:3])}"
            )
        
        # Experience recommendations
        if "experience" in section_scores and section_scores["experience"].score < 0.6:
            recommendations.append(
                "Enhance experience descriptions with more specific achievements and metrics"
            )
        
        # Projects recommendations
        if "projects" in section_scores and section_scores["projects"].score < 0.5:
            recommendations.append(
                "Add relevant projects that demonstrate key skills mentioned in job requirements"
            )
        
        # Keyword recommendations
        if "keywords" in section_scores and section_scores["keywords"].score < 0.6:
            missing_keywords = section_scores["keywords"].missing_keywords[:3]
            recommendations.append(
                f"Incorporate key terms throughout resume: {', '.join(missing_keywords)}"
            )
        
        # General recommendations
        low_scores = [section for section, score in section_scores.items() if score.score < 0.5]
        if len(low_scores) > 2:
            recommendations.append(
                "Consider significant resume restructuring to better align with job requirements"
            )
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _generate_match_explanation(
        self,
        section_scores: Dict[str, SectionScore],
        overall_score: float,
        skill_gaps: List[str]
    ) -> str:
        """Generate detailed explanation of the matching analysis"""
        
        explanation_parts = []
        
        # Overall assessment
        if overall_score >= 0.8:
            explanation_parts.append("This resume shows excellent alignment with the job requirements.")
        elif overall_score >= 0.6:
            explanation_parts.append("This resume demonstrates good potential fit with some areas for improvement.")
        elif overall_score >= 0.4:
            explanation_parts.append("This resume shows moderate alignment with significant gaps to address.")
        else:
            explanation_parts.append("This resume requires substantial improvements to match job requirements.")
        
        # Section-by-section analysis
        for section, score in section_scores.items():
            section_name = section.replace("_", " ").title()
            if score.score >= 0.7:
                explanation_parts.append(f"{section_name}: Strong match ({score.score:.1%})")
            elif score.score >= 0.5:
                explanation_parts.append(f"{section_name}: Moderate match ({score.score:.1%})")
            else:
                explanation_parts.append(f"{section_name}: Needs improvement ({score.score:.1%})")
        
        # Skill gap analysis
        if skill_gaps:
            explanation_parts.append(f"Key missing skills: {', '.join(skill_gaps[:3])}")
        
        return " ".join(explanation_parts)
    
    def _extract_required_experience(self, job_description: JobDescription) -> int:
        """Extract required years of experience from job description"""
        requirements_text = " ".join(job_description.requirements).lower()
        
        # Look for experience patterns
        import re
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:relevant\s*)?experience',
            r'minimum\s*(?:of\s*)?(\d+)\s*years?'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, requirements_text)
            if match:
                return int(match.group(1))
        
        # Default based on job level
        level_defaults = {
            "entry": 1,
            "mid": 3,
            "senior": 5,
            "lead": 8,
            "executive": 10
        }
        
        return level_defaults.get(job_description.experience_level.value, 3)
    
    def _find_common_keywords(self, text1: str, text2: str) -> List[str]:
        """Find common keywords between two texts"""
        words1 = set(word.lower() for word in text1.split() if len(word) > 3)
        words2 = set(word.lower() for word in text2.split() if len(word) > 3)
        
        common = list(words1 & words2)
        return sorted(common)[:10]
    
    def _find_missing_keywords(self, resume_text: str, job_text: str) -> List[str]:
        """Find important keywords missing from resume"""
        job_keywords = self._extract_keywords(job_text)
        resume_words = set(word.lower() for word in resume_text.split())
        
        missing = [kw for kw in job_keywords if kw.lower() not in resume_words]
        return missing[:10]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction - in production, use more sophisticated NLP
        words = text.lower().split()
        
        # Filter out common words and keep important terms
        important_words = [
            word for word in words 
            if len(word) > 3 and word not in ['that', 'with', 'from', 'they', 'have', 'this', 'will', 'were', 'been']
        ]
        
        # Count frequency and return top keywords
        from collections import Counter
        word_counts = Counter(important_words)
        return [word for word, count in word_counts.most_common(20)]
    
    def _extract_full_resume_text(self, resume: Resume) -> str:
        """Extract all text content from resume"""
        text_parts = []
        
        if resume.summary:
            text_parts.append(resume.summary)
        
        # Skills
        for skills in resume.skills.values():
            text_parts.extend(skills)
        
        # Experience
        for exp in resume.experience:
            text_parts.extend(exp.description)
        
        # Education
        for edu in resume.education:
            text_parts.extend([edu.degree, edu.major or "", edu.institution])
        
        # Projects
        for proj in resume.projects:
            text_parts.extend([proj.name, proj.description])
            text_parts.extend(proj.technologies)
        
        return " ".join(filter(None, text_parts))
    
    def _get_binary_prediction(
        self,
        resume_features: Dict[str, Any],
        job_features: Dict[str, Any]
    ) -> Optional[bool]:
        """Get binary classification prediction (fit/not fit)"""
        if not self.is_trained or self.binary_classifier is None:
            return None
        
        try:
            # Prepare features for prediction
            feature_vector = self._prepare_feature_vector(resume_features, job_features)
            prediction = self.binary_classifier.predict([feature_vector])[0]
            return bool(prediction)
        except Exception as e:
            logger.error(f"Error in binary prediction: {e}")
            return None
    
    def _prepare_feature_vector(
        self, 
        resume_features: Dict[str, Any], 
        job_features: Dict[str, Any]
    ) -> np.ndarray:
        """Prepare feature vector for ML model"""
        # Simplified feature vector preparation
        features = []
        
        # Add basic numerical features
        features.extend([
            resume_features.get("years_experience", 0),
            len(resume_features.get("skills", [])),
            len(resume_features.get("education", [])),
            len(resume_features.get("projects", [])),
            resume_features.get("education_level", 0)
        ])
        
        return np.array(features)
    
    def train_binary_classifier(
        self,
        training_data: List[Tuple[Resume, JobDescription, bool]],
        model_type: str = "random_forest"
    ):
        """Train binary classifier for fit/not fit prediction"""
        logger.info(f"Training binary classifier with {len(training_data)} samples")
        
        # Prepare training data
        X = []
        y = []
        
        for resume, job, label in training_data:
            resume_features = self.feature_extractor.extract_resume_features(resume)
            job_features = self.feature_extractor.extract_job_features(job)
            feature_vector = self._prepare_feature_vector(resume_features, job_features)
            
            X.append(feature_vector)
            y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        # Train model
        if model_type == "random_forest":
            self.binary_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            self.binary_classifier = LogisticRegression(random_state=42)
        
        self.binary_classifier.fit(X, y)
        self.is_trained = True
        
        logger.info("Binary classifier training completed")