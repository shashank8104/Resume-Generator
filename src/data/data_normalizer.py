import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..models.resume_schema import Resume, ContactInfo, WorkExperience, Education, Project
from ..models.job_schema import JobDescription
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class DataNormalizer:
    """Normalize and clean resume and job description data"""
    
    def __init__(self):
        self.skill_mappings = self._load_skill_mappings()
        self.company_mappings = self._load_company_mappings()
    
    def normalize_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize resume data to standard format"""
        logger.info("Normalizing resume data")
        
        normalized = resume_data.copy()
        
        # Normalize contact information
        if "contact_info" in normalized:
            normalized["contact_info"] = self._normalize_contact_info(normalized["contact_info"])
        
        # Normalize skills
        if "skills" in normalized:
            normalized["skills"] = self._normalize_skills(normalized["skills"])
        
        # Normalize work experience
        if "experience" in normalized:
            normalized["experience"] = [
                self._normalize_work_experience(exp) for exp in normalized["experience"]
            ]
        
        # Normalize education
        if "education" in normalized:
            normalized["education"] = [
                self._normalize_education(edu) for edu in normalized["education"]
            ]
        
        # Normalize projects
        if "projects" in normalized:
            normalized["projects"] = [
                self._normalize_project(proj) for proj in normalized["projects"]
            ]
        
        # Clean text fields
        normalized = self._clean_text_fields(normalized)
        
        logger.info("Resume data normalization completed")
        return normalized
    
    def normalize_job_description(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize job description data to standard format"""
        logger.info("Normalizing job description data")
        
        normalized = job_data.copy()
        
        # Normalize title
        if "title" in normalized:
            normalized["title"] = self._normalize_job_title(normalized["title"])
        
        # Normalize company name
        if "company" in normalized:
            normalized["company"] = self._normalize_company_name(normalized["company"])
        
        # Normalize location
        if "location" in normalized:
            normalized["location"] = self._normalize_location(normalized["location"])
        
        # Normalize skills
        if "required_skills" in normalized:
            normalized["required_skills"] = self._normalize_skill_list(normalized["required_skills"])
        
        if "preferred_skills" in normalized:
            normalized["preferred_skills"] = self._normalize_skill_list(normalized["preferred_skills"])
        
        # Clean text fields
        normalized = self._clean_text_fields(normalized)
        
        # Extract additional skills from description
        if "description" in normalized:
            extracted_skills = self._extract_skills_from_text(normalized["description"])
            existing_skills = set(normalized.get("required_skills", []))
            new_skills = [skill for skill in extracted_skills if skill not in existing_skills]
            if new_skills:
                normalized.setdefault("extracted_skills", []).extend(new_skills)
        
        logger.info("Job description data normalization completed")
        return normalized
    
    def _normalize_contact_info(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize contact information"""
        normalized = contact.copy()
        
        # Clean phone number
        if "phone" in normalized and normalized["phone"]:
            phone = re.sub(r'[^\d+]', '', normalized["phone"])
            if not phone.startswith('+'):
                phone = '+1' + phone[-10:]  # Assume US number
            normalized["phone"] = phone
        
        # Clean email
        if "email" in normalized:
            normalized["email"] = normalized["email"].lower().strip()
        
        # Normalize name
        if "full_name" in normalized:
            normalized["full_name"] = self._normalize_name(normalized["full_name"])
        
        # Clean URLs
        for url_field in ["linkedin", "github", "website"]:
            if url_field in normalized and normalized[url_field]:
                normalized[url_field] = self._normalize_url(normalized[url_field])
        
        return normalized
    
    def _normalize_skills(self, skills: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Normalize and categorize skills"""
        normalized_skills = {}
        
        for category, skill_list in skills.items():
            # Normalize category name
            normalized_category = self._normalize_skill_category(category)
            
            # Normalize individual skills
            normalized_skill_list = self._normalize_skill_list(skill_list)
            
            if normalized_skill_list:
                normalized_skills[normalized_category] = normalized_skill_list
        
        return normalized_skills
    
    def _normalize_work_experience(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize work experience entry"""
        normalized = experience.copy()
        
        # Normalize company name
        if "company" in normalized:
            normalized["company"] = self._normalize_company_name(normalized["company"])
        
        # Normalize position title
        if "position" in normalized:
            normalized["position"] = self._normalize_job_title(normalized["position"])
        
        # Clean description bullets
        if "description" in normalized:
            normalized["description"] = [
                self._clean_text(desc) for desc in normalized["description"]
            ]
        
        # Normalize skills
        if "skills" in normalized:
            normalized["skills"] = self._normalize_skill_list(normalized["skills"])
        
        return normalized
    
    def _normalize_education(self, education: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize education entry"""
        normalized = education.copy()
        
        # Normalize institution name
        if "institution" in normalized:
            normalized["institution"] = self._normalize_institution_name(normalized["institution"])
        
        # Normalize degree
        if "degree" in normalized:
            normalized["degree"] = self._normalize_degree(normalized["degree"])
        
        # Normalize major
        if "major" in normalized:
            normalized["major"] = self._normalize_major(normalized["major"])
        
        return normalized
    
    def _normalize_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize project entry"""
        normalized = project.copy()
        
        # Clean project name
        if "name" in normalized:
            normalized["name"] = self._clean_text(normalized["name"])
        
        # Clean description
        if "description" in normalized:
            normalized["description"] = self._clean_text(normalized["description"])
        
        # Normalize technologies
        if "technologies" in normalized:
            normalized["technologies"] = self._normalize_skill_list(normalized["technologies"])
        
        return normalized
    
    def _normalize_skill_list(self, skills: List[str]) -> List[str]:
        """Normalize a list of skills"""
        normalized_skills = []
        
        for skill in skills:
            if not skill or not skill.strip():
                continue
                
            # Clean the skill
            cleaned_skill = self._clean_skill(skill)
            
            # Apply skill mappings
            normalized_skill = self.skill_mappings.get(cleaned_skill.lower(), cleaned_skill)
            
            # Avoid duplicates
            if normalized_skill and normalized_skill not in normalized_skills:
                normalized_skills.append(normalized_skill)
        
        return sorted(normalized_skills)
    
    def _clean_skill(self, skill: str) -> str:
        """Clean individual skill name"""
        # Remove extra whitespace and special characters
        cleaned = re.sub(r'[^\w\s\.\+\#\-]', '', skill.strip())
        
        # Normalize common variations
        replacements = {
            'javascript': 'JavaScript',
            'python': 'Python',
            'java': 'Java',
            'c++': 'C++',
            'c#': 'C#',
            'html': 'HTML',
            'css': 'CSS',
            'sql': 'SQL',
            'aws': 'AWS',
            'gcp': 'Google Cloud Platform',
            'azure': 'Microsoft Azure'
        }
        
        return replacements.get(cleaned.lower(), cleaned)
    
    def _normalize_skill_category(self, category: str) -> str:
        """Normalize skill category names"""
        category_mappings = {
            'programming languages': 'programming',
            'programming_languages': 'programming',
            'languages': 'programming',
            'tech skills': 'technical',
            'technical skills': 'technical',
            'soft skills': 'soft_skills',
            'frameworks': 'frameworks',
            'libraries': 'frameworks',
            'databases': 'databases',
            'tools': 'tools',
            'platforms': 'tools'
        }
        
        normalized = category.lower().replace(' ', '_')
        return category_mappings.get(normalized, normalized)
    
    def _normalize_company_name(self, company: str) -> str:
        """Normalize company names"""
        # Clean the company name
        cleaned = self._clean_text(company)
        
        # Apply company mappings
        return self.company_mappings.get(cleaned.lower(), cleaned)
    
    def _normalize_job_title(self, title: str) -> str:
        """Normalize job titles"""
        # Clean the title
        cleaned = self._clean_text(title)
        
        # Standardize common variations
        title_mappings = {
            'software engineer': 'Software Engineer',
            'software developer': 'Software Developer',
            'full stack developer': 'Full Stack Developer',
            'data scientist': 'Data Scientist',
            'data analyst': 'Data Analyst',
            'product manager': 'Product Manager',
            'project manager': 'Project Manager',
            'marketing manager': 'Marketing Manager'
        }
        
        return title_mappings.get(cleaned.lower(), cleaned)
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location strings"""
        # Clean the location
        cleaned = self._clean_text(location)
        
        # Standardize common locations
        location_mappings = {
            'sf': 'San Francisco, CA',
            'san francisco': 'San Francisco, CA',
            'san francisco, california': 'San Francisco, CA',
            'nyc': 'New York, NY',
            'new york city': 'New York, NY',
            'new york, new york': 'New York, NY',
            'la': 'Los Angeles, CA',
            'los angeles': 'Los Angeles, CA'
        }
        
        return location_mappings.get(cleaned.lower(), cleaned)
    
    def _normalize_institution_name(self, institution: str) -> str:
        """Normalize educational institution names"""
        # Clean the name
        cleaned = self._clean_text(institution)
        
        # Standardize common institutions
        institution_mappings = {
            'uc berkeley': 'University of California, Berkeley',
            'ucb': 'University of California, Berkeley',
            'stanford': 'Stanford University',
            'mit': 'Massachusetts Institute of Technology'
        }
        
        return institution_mappings.get(cleaned.lower(), cleaned)
    
    def _normalize_degree(self, degree: str) -> str:
        """Normalize degree names"""
        # Clean the degree
        cleaned = self._clean_text(degree)
        
        # Standardize common degrees
        degree_mappings = {
            'bs': 'Bachelor of Science',
            'ba': 'Bachelor of Arts',
            'ms': 'Master of Science',
            'ma': 'Master of Arts',
            'mba': 'Master of Business Administration',
            'phd': 'Doctor of Philosophy'
        }
        
        return degree_mappings.get(cleaned.lower(), cleaned)
    
    def _normalize_major(self, major: str) -> str:
        """Normalize major/field of study"""
        # Clean the major
        cleaned = self._clean_text(major)
        
        # Standardize common majors
        major_mappings = {
            'cs': 'Computer Science',
            'computer science': 'Computer Science',
            'data science': 'Data Science',
            'business administration': 'Business Administration',
            'marketing': 'Marketing'
        }
        
        return major_mappings.get(cleaned.lower(), cleaned)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize person names"""
        # Remove extra whitespace and title case
        return ' '.join(word.capitalize() for word in name.strip().split())
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URLs"""
        url = url.strip()
        
        # Add https if no protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    def _clean_text(self, text: str) -> str:
        """Clean text fields"""
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s\.\,\;\:\(\)\-\+\#\&\/]', '', cleaned)
        
        return cleaned.strip()
    
    def _clean_text_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively clean text fields in nested data"""
        cleaned = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = self._clean_text(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    self._clean_text(item) if isinstance(item, str) else item
                    for item in value
                ]
            elif isinstance(value, dict):
                cleaned[key] = self._clean_text_fields(value)
            else:
                cleaned[key] = value
        
        return cleaned
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract technical skills from text description"""
        # Common technical skills to look for
        common_skills = {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'ruby',
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'nodejs', 'express',
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'git', 'linux', 'machine learning', 'data science', 'tensorflow', 'pytorch'
        }
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill in text_lower:
                # Find the proper case version
                pattern = re.compile(re.escape(skill), re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    found_skills.append(match.group())
        
        return found_skills
    
    def _load_skill_mappings(self) -> Dict[str, str]:
        """Load skill normalization mappings"""
        return {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'py': 'Python',
            'cpp': 'C++',
            'c++': 'C++',
            'csharp': 'C#',
            'c#': 'C#',
            'node': 'Node.js',
            'nodejs': 'Node.js',
            'react.js': 'React',
            'reactjs': 'React',
            'vue.js': 'Vue',
            'vuejs': 'Vue',
            'postgres': 'PostgreSQL',
            'postgresql': 'PostgreSQL',
            'mongo': 'MongoDB',
            'mongodb': 'MongoDB'
        }
    
    def _load_company_mappings(self) -> Dict[str, str]:
        """Load company name normalization mappings"""
        return {
            'google inc': 'Google',
            'google llc': 'Google',
            'amazon inc': 'Amazon',
            'amazon.com': 'Amazon',
            'microsoft corp': 'Microsoft',
            'microsoft corporation': 'Microsoft',
            'apple inc': 'Apple',
            'facebook inc': 'Meta',
            'meta platforms': 'Meta'
        }