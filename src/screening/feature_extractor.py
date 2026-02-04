import re
from typing import Dict, Any, List
from datetime import date, datetime

from ..models.resume_schema import Resume, EducationLevel
from ..models.job_schema import JobDescription
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class FeatureExtractor:
    """Extract structured features from resumes and job descriptions"""
    
    def __init__(self, config=None):
        self.config = config or {}
        logger.info("Feature extractor initialized")
    
    def extract_resume_features(self, resume: Resume) -> Dict[str, Any]:
        """Extract numerical and categorical features from resume"""
        features = {}
        
        # Basic counts
        features['total_skills'] = sum(len(skills) for skills in resume.skills.values())
        features['skill_categories'] = len(resume.skills)
        features['total_experience_roles'] = len(resume.experience)
        features['total_education'] = len(resume.education)
        features['total_projects'] = len(resume.projects)
        features['total_certifications'] = len(resume.certifications)
        features['total_languages'] = len(resume.languages)
        
        # Experience analysis
        features['years_experience'] = self._calculate_years_experience(resume.experience)
        features['has_current_role'] = any(exp.end_date is None for exp in resume.experience)
        features['average_role_duration'] = self._calculate_average_role_duration(resume.experience)
        
        # Education features
        features['highest_education_level'] = self._get_highest_education_level(resume.education)
        features['has_relevant_degree'] = self._has_relevant_degree(resume.education)
        features['has_advanced_degree'] = any(edu.level.value in ['master', 'doctorate'] for edu in resume.education)
        
        # Content analysis
        features['summary_length'] = len(resume.summary or '') 
        features['has_quantified_achievements'] = self._has_quantified_achievements(resume)
        features['total_description_length'] = sum(len(' '.join(exp.description)) for exp in resume.experience)
        
        # Skill analysis
        features['technical_skills'] = len(resume.skills.get('technical', [])) + len(resume.skills.get('programming', []))
        features['soft_skills'] = len(resume.skills.get('soft_skills', []))
        
        # Project analysis
        features['avg_technologies_per_project'] = (sum(len(proj.technologies) for proj in resume.projects) / len(resume.projects)) if resume.projects else 0
        features['has_project_urls'] = sum(1 for proj in resume.projects if proj.url) / max(len(resume.projects), 1)
        
        return features
    
    def extract_job_features(self, job_description: JobDescription) -> Dict[str, Any]:
        """Extract features from job description"""
        features = {}
        
        # Basic counts
        features['total_requirements'] = len(job_description.requirements)
        features['total_preferred_qualifications'] = len(job_description.preferred_qualifications)
        features['total_responsibilities'] = len(job_description.responsibilities)
        features['total_required_skills'] = len(job_description.required_skills)
        features['total_preferred_skills'] = len(job_description.preferred_skills)
        
        # Job characteristics
        features['experience_level_numeric'] = self._experience_level_to_numeric(job_description.experience_level.value)
        features['is_remote'] = job_description.job_type.value == 'remote'
        features['has_salary_range'] = job_description.salary_range is not None
        features['total_benefits'] = len(job_description.benefits)
        
        # Text analysis
        features['description_length'] = len(job_description.description)
        features['total_text_length'] = (len(job_description.description) + 
                                       sum(len(req) for req in job_description.requirements) +
                                       sum(len(resp) for resp in job_description.responsibilities))
        
        # Requirements analysis
        features['requires_degree'] = self._requires_degree(job_description.requirements)
        features['requires_experience'] = self._extract_required_experience_years(job_description.requirements)
        features['mentions_remote'] = 'remote' in job_description.description.lower()
        
        return features
    
    def _calculate_years_experience(self, experience_list) -> float:
        """Calculate total years of work experience"""
        if not experience_list:
            return 0.0
        
        total_days = 0
        current_date = date.today()
        
        for exp in experience_list:
            start_date = exp.start_date
            end_date = exp.end_date or current_date
            
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            duration = (end_date - start_date).days
            total_days += max(duration, 0)
        
        return round(total_days / 365.25, 1)  # Convert to years
    
    def _calculate_average_role_duration(self, experience_list) -> float:
        """Calculate average duration per role in years"""
        if not experience_list:
            return 0.0
        
        total_years = self._calculate_years_experience(experience_list)
        return round(total_years / len(experience_list), 1)
    
    def _get_highest_education_level(self, education_list) -> int:
        """Get highest education level as numeric value"""
        if not education_list:
            return 0
        
        level_mapping = {
            'high_school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'doctorate': 5,
            'certificate': 1
        }
        
        highest_level = max(level_mapping.get(edu.level.value, 0) for edu in education_list)
        return highest_level
    
    def _has_relevant_degree(self, education_list) -> bool:
        """Check if has relevant technical degree"""
        relevant_fields = [
            'computer science', 'software engineering', 'data science',
            'information technology', 'engineering', 'mathematics',
            'statistics', 'physics'
        ]
        
        for edu in education_list:
            major = (edu.major or '').lower()
            degree = (edu.degree or '').lower()
            
            if any(field in major or field in degree for field in relevant_fields):
                return True
        
        return False
    
    def _has_quantified_achievements(self, resume: Resume) -> bool:
        """Check if resume contains quantified achievements"""
        # Look for numbers, percentages, dollar amounts in experience descriptions
        number_pattern = r'\d+[%$]?|\$\d+|\d+\+'
        
        all_text = resume.summary or ''
        for exp in resume.experience:
            all_text += ' '.join(exp.description)
        
        return bool(re.search(number_pattern, all_text))
    
    def _experience_level_to_numeric(self, level: str) -> int:
        """Convert experience level to numeric value"""
        mapping = {
            'entry': 1,
            'mid': 2,
            'senior': 3,
            'lead': 4,
            'executive': 5
        }
        return mapping.get(level.lower(), 2)
    
    def _requires_degree(self, requirements: List[str]) -> bool:
        """Check if job requires a degree"""
        degree_keywords = ['bachelor', 'master', 'doctorate', 'degree', 'diploma']
        requirements_text = ' '.join(requirements).lower()
        
        return any(keyword in requirements_text for keyword in degree_keywords)
    
    def _extract_required_experience_years(self, requirements: List[str]) -> int:
        """Extract required years of experience from job requirements"""
        requirements_text = ' '.join(requirements).lower()
        
        # Look for patterns like "3+ years", "5-7 years", "minimum 2 years"
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'minimum\s*(?:of\s*)?(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, requirements_text)
            if match:
                return int(match.group(1))
        
        return 0  # Default if no experience requirement found