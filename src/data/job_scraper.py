import requests
import time
import random
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from ..models.job_schema import JobDescription, JobLevel, JobType
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class JobScraper:
    """Scrape job descriptions from public sources (educational/research purposes)"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting
        self.request_delay = 2  # seconds between requests
        
    def scrape_sample_jobs(self, roles: List[str], max_per_role: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape sample job descriptions for given roles
        Note: This is a simplified implementation for educational purposes
        In production, use proper APIs and respect robots.txt
        """
        logger.info(f"Scraping sample jobs for roles: {roles}")
        
        all_jobs = []
        
        for role in roles:
            logger.info(f"Scraping jobs for role: {role}")
            
            try:
                # Generate sample job descriptions instead of actual scraping
                # to avoid legal/ethical issues with web scraping
                jobs = self._generate_realistic_job_samples(role, max_per_role)
                all_jobs.extend(jobs)
                
                # Rate limiting
                time.sleep(self.request_delay)
                
            except Exception as e:
                logger.error(f"Error scraping jobs for {role}: {e}")
                continue
        
        logger.info(f"Scraped {len(all_jobs)} job descriptions")
        return all_jobs
    
    def _generate_realistic_job_samples(self, role: str, count: int) -> List[Dict[str, Any]]:
        """
        Generate realistic job description samples based on role
        This simulates what would be scraped from job boards
        """
        jobs = []
        
        # Role-specific job description templates
        templates = self._get_job_templates()
        role_template = templates.get(role, templates["software_engineer"])
        
        companies = [
            "TechStart Inc.", "InnovateNow", "DataFlow Corp", "CloudTech Solutions",
            "AI Dynamics", "DevOps Pro", "ScaleUp Technologies", "NextGen Software",
            "DigitalEdge", "SmartSystems"
        ]
        
        locations = [
            "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
            "Boston, MA", "Denver, CO", "Remote", "Chicago, IL", "Los Angeles, CA"
        ]
        
        for i in range(count):
            # Vary experience levels
            experience_levels = list(JobLevel)
            experience_level = random.choice(experience_levels)
            
            # Build job description
            job_data = {
                "title": f"{experience_level.value.title()} {role.replace('_', ' ').title()}",
                "company": random.choice(companies),
                "location": random.choice(locations),
                "job_type": random.choice(list(JobType)),
                "experience_level": experience_level,
                "description": self._build_job_description(role_template, experience_level),
                "requirements": self._build_requirements(role_template, experience_level),
                "preferred_qualifications": role_template["preferred_qualifications"],
                "responsibilities": random.choices(role_template["responsibilities"], k=random.randint(4, 6)),
                "required_skills": random.choices(role_template["required_skills"], k=random.randint(5, 8)),
                "preferred_skills": random.choices(role_template["preferred_skills"], k=random.randint(3, 5)),
                "industry": "Technology",
                "salary_range": self._generate_salary_range(experience_level),
                "benefits": [
                    "Health, dental, and vision insurance",
                    "401(k) with company match",
                    "Flexible PTO",
                    "Remote work options",
                    "Professional development budget"
                ],
                "role": role,
                "source": "synthetic_sample",  # Mark as generated data
                "scraped_at": time.time()
            }
            
            jobs.append(job_data)
        
        return jobs
    
    def _get_job_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get job description templates for different roles"""
        return {
            "software_engineer": {
                "description_template": "We are seeking a talented {level} Software Engineer to join our dynamic team. You will be responsible for developing scalable web applications, collaborating with cross-functional teams, and contributing to our technical architecture decisions.",
                "requirements": [
                    "Bachelor's degree in Computer Science or related field",
                    "Strong programming skills in modern languages",
                    "Experience with version control systems",
                    "Understanding of software development lifecycle",
                    "Strong problem-solving and analytical skills",
                    "Excellent communication and teamwork abilities"
                ],
                "preferred_qualifications": [
                    "Master's degree in Computer Science",
                    "Experience with cloud platforms",
                    "Knowledge of DevOps practices",
                    "Open source contributions",
                    "Previous startup experience"
                ],
                "responsibilities": [
                    "Design and develop scalable web applications",
                    "Write clean, maintainable, and efficient code",
                    "Collaborate with product managers and designers",
                    "Participate in code reviews and technical discussions",
                    "Troubleshoot and debug applications",
                    "Stay up-to-date with emerging technologies",
                    "Mentor junior developers",
                    "Contribute to technical documentation"
                ],
                "required_skills": [
                    "Python", "JavaScript", "React", "Node.js", "PostgreSQL",
                    "Git", "RESTful APIs", "Agile development", "Testing frameworks"
                ],
                "preferred_skills": [
                    "Docker", "Kubernetes", "AWS", "GraphQL", "TypeScript",
                    "Redis", "Elasticsearch", "CI/CD", "Microservices"
                ]
            },
            "data_scientist": {
                "description_template": "We are looking for a {level} Data Scientist to join our analytics team. You will work with large datasets to extract insights, build predictive models, and drive data-driven decision making across the organization.",
                "requirements": [
                    "Bachelor's degree in Statistics, Mathematics, Computer Science, or related field",
                    "Strong analytical and statistical skills",
                    "Experience with machine learning algorithms",
                    "Proficiency in Python or R",
                    "Experience with data visualization tools",
                    "Strong communication skills"
                ],
                "preferred_qualifications": [
                    "Master's or PhD in quantitative field",
                    "Experience with big data technologies",
                    "Knowledge of deep learning frameworks",
                    "Business domain expertise",
                    "Publication record in relevant fields"
                ],
                "responsibilities": [
                    "Analyze large datasets to identify trends and patterns",
                    "Build and deploy machine learning models",
                    "Create data visualizations and reports",
                    "Collaborate with stakeholders to define business problems",
                    "Design and conduct A/B tests",
                    "Maintain and optimize data pipelines",
                    "Present findings to executive leadership"
                ],
                "required_skills": [
                    "Python", "SQL", "Pandas", "NumPy", "scikit-learn",
                    "Matplotlib", "Jupyter", "Statistics", "Machine Learning"
                ],
                "preferred_skills": [
                    "TensorFlow", "PyTorch", "Spark", "Tableau", "R",
                    "Airflow", "Docker", "AWS", "Deep Learning"
                ]
            },
            "marketing_manager": {
                "description_template": "We are seeking a {level} Marketing Manager to develop and execute comprehensive marketing strategies. You will lead campaigns, analyze performance metrics, and drive customer acquisition and engagement.",
                "requirements": [
                    "Bachelor's degree in Marketing, Business, or related field",
                    "Experience in digital marketing",
                    "Strong analytical and project management skills",
                    "Knowledge of marketing automation tools",
                    "Excellent written and verbal communication",
                    "Creative thinking and problem-solving abilities"
                ],
                "preferred_qualifications": [
                    "MBA or advanced marketing degree",
                    "Experience in B2B/SaaS marketing",
                    "Google Ads and Facebook Ads certifications",
                    "Experience with marketing attribution",
                    "Previous team leadership experience"
                ],
                "responsibilities": [
                    "Develop and execute marketing campaigns",
                    "Manage social media presence and content strategy",
                    "Analyze campaign performance and ROI",
                    "Collaborate with sales team on lead generation",
                    "Manage marketing budget and vendor relationships",
                    "Conduct market research and competitive analysis",
                    "Create marketing collateral and content"
                ],
                "required_skills": [
                    "Digital Marketing", "Google Analytics", "SEO", "SEM",
                    "Content Marketing", "Social Media", "Email Marketing", "CRM"
                ],
                "preferred_skills": [
                    "Marketing Automation", "A/B Testing", "Salesforce",
                    "HubSpot", "Photoshop", "Video Marketing", "Influencer Marketing"
                ]
            }
        }
    
    def _build_job_description(self, template: Dict[str, Any], experience_level: JobLevel) -> str:
        """Build complete job description from template"""
        base_description = template["description_template"].format(level=experience_level.value)
        
        additional_context = {
            JobLevel.ENTRY: "This is an excellent opportunity for a recent graduate or early-career professional to grow their skills in a supportive environment.",
            JobLevel.MID: "We're looking for someone with proven experience who can take ownership of projects and contribute to team success.",
            JobLevel.SENIOR: "This role requires a seasoned professional who can lead technical initiatives and mentor other team members.",
            JobLevel.LEAD: "We need an experienced leader who can guide technical direction and build high-performing teams.",
            JobLevel.EXECUTIVE: "This executive role involves strategic planning, stakeholder management, and organization-wide impact."
        }
        
        context = additional_context.get(experience_level, "")
        return f"{base_description} {context}"
    
    def _build_requirements(self, template: Dict[str, Any], experience_level: JobLevel) -> List[str]:
        """Build requirements list based on experience level"""
        base_requirements = template["requirements"].copy()
        
        # Add experience-specific requirements
        experience_requirements = {
            JobLevel.ENTRY: ["0-2 years of relevant experience", "Strong learning attitude and adaptability"],
            JobLevel.MID: ["3-5 years of relevant experience", "Proven track record of project delivery"],
            JobLevel.SENIOR: ["5-8 years of relevant experience", "Leadership and mentoring capabilities"],
            JobLevel.LEAD: ["8+ years of experience with team leadership", "Strategic thinking and planning skills"],
            JobLevel.EXECUTIVE: ["10+ years with senior leadership experience", "Proven ability to scale teams and processes"]
        }
        
        specific_reqs = experience_requirements.get(experience_level, [])
        return base_requirements + specific_reqs
    
    def _generate_salary_range(self, experience_level: JobLevel) -> Dict[str, int]:
        """Generate realistic salary ranges by experience level"""
        salary_ranges = {
            JobLevel.ENTRY: {"min": 70000, "max": 100000},
            JobLevel.MID: {"min": 100000, "max": 140000},
            JobLevel.SENIOR: {"min": 140000, "max": 180000},
            JobLevel.LEAD: {"min": 180000, "max": 220000},
            JobLevel.EXECUTIVE: {"min": 220000, "max": 300000}
        }
        
        base_range = salary_ranges.get(experience_level, salary_ranges[JobLevel.MID])
        
        # Add some variation
        variation = random.randint(-10000, 10000)
        return {
            "min": max(base_range["min"] + variation, 50000),
            "max": base_range["max"] + variation
        }
    
    def validate_scraped_data(self, job_data: Dict[str, Any]) -> bool:
        """Validate scraped job description data"""
        required_fields = [
            "title", "company", "location", "job_type", 
            "experience_level", "description", "requirements"
        ]
        
        for field in required_fields:
            if field not in job_data or not job_data[field]:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate data types
        if not isinstance(job_data.get("requirements", []), list):
            logger.warning("Requirements field must be a list")
            return False
        
        if not isinstance(job_data.get("required_skills", []), list):
            logger.warning("Required skills field must be a list")
            return False
        
        return True
    
    def clean_scraped_text(self, text: str) -> str:
        """Clean text scraped from web sources"""
        if not text:
            return ""
        
        # Remove HTML tags
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common unwanted phrases
        unwanted_phrases = [
            "Apply now", "Click here", "Learn more", "See full job description",
            "Equal opportunity employer", "We are an equal opportunity"
        ]
        
        for phrase in unwanted_phrases:
            text = text.replace(phrase, "")
        
        return text.strip()
    
    def get_job_urls(self, search_terms: List[str], max_urls: int = 50) -> List[str]:
        """
        Get job URLs from job boards (placeholder implementation)
        In practice, this would use job board APIs or careful scraping
        """
        logger.info(f"Getting job URLs for search terms: {search_terms}")
        
        # Placeholder - return empty list to avoid actual scraping
        # In production, implement proper API integrations
        return []
    
    def scrape_job_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape individual job description from URL
        Placeholder implementation to avoid actual web scraping
        """
        logger.info(f"Scraping job from URL: {url}")
        
        # Placeholder - return None to avoid actual scraping
        # In production, implement proper scraping with respect to robots.txt
        return None