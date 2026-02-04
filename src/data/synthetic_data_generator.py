import random
import json
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

from ..models.resume_schema import (
    Resume, ContactInfo, WorkExperience, Education, Project,
    ExperienceLevel, EducationLevel
)
from ..models.job_schema import JobDescription, JobLevel, JobType
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class SyntheticDataGenerator:
    """Generate synthetic resume and job description data for training and testing"""
    
    def __init__(self):
        self.role_templates = self._load_role_templates()
        self.skill_database = self._load_skill_database()
        self.company_names = self._load_company_names()
        
    def _load_role_templates(self) -> Dict[str, Any]:
        """Load role-specific templates"""
        templates = {
            "software_engineer": {
                "skills": {
                    "programming": ["Python", "JavaScript", "Java", "C++", "Go", "Rust"],
                    "frameworks": ["React", "Angular", "Vue", "Django", "Flask", "Spring", "Node.js"],
                    "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch"],
                    "tools": ["Git", "Docker", "Kubernetes", "Jenkins", "AWS", "Azure"]
                },
                "responsibilities": [
                    "Developed and maintained web applications using {framework}",
                    "Implemented RESTful APIs with {programming} and {database}",
                    "Collaborated with cross-functional teams on feature development",
                    "Optimized application performance and reduced load times by {percentage}%",
                    "Led code reviews and mentored junior developers",
                    "Deployed applications using {deployment_tool}"
                ],
                "projects": [
                    "E-commerce Platform",
                    "Real-time Chat Application",
                    "Task Management System",
                    "Data Analytics Dashboard",
                    "Mobile App Backend"
                ]
            },
            "data_scientist": {
                "skills": {
                    "programming": ["Python", "R", "SQL", "Scala", "Julia"],
                    "ml_frameworks": ["scikit-learn", "TensorFlow", "PyTorch", "Keras", "XGBoost"],
                    "visualization": ["Matplotlib", "Seaborn", "Plotly", "Tableau", "Power BI"],
                    "tools": ["Jupyter", "Git", "Docker", "Airflow", "Spark", "Hadoop"]
                },
                "responsibilities": [
                    "Built machine learning models to predict {outcome} with {accuracy}% accuracy",
                    "Analyzed large datasets using {tool} and identified key insights",
                    "Created data pipelines for automated {process}",
                    "Collaborated with stakeholders to define business requirements",
                    "Presented findings to executive leadership",
                    "Optimized model performance and reduced inference time by {percentage}%"
                ],
                "projects": [
                    "Customer Churn Prediction Model",
                    "Recommendation System",
                    "Fraud Detection Pipeline",
                    "Sales Forecasting Model",
                    "NLP Sentiment Analysis Tool"
                ]
            },
            "marketing_manager": {
                "skills": {
                    "digital_marketing": ["SEO", "SEM", "Social Media", "Email Marketing", "Content Marketing"],
                    "analytics": ["Google Analytics", "Facebook Ads", "HubSpot", "Salesforce"],
                    "design": ["Photoshop", "Canva", "Figma", "Adobe Creative Suite"],
                    "tools": ["CRM", "Marketing Automation", "A/B Testing", "Campaign Management"]
                },
                "responsibilities": [
                    "Developed and executed marketing campaigns that increased {metric} by {percentage}%",
                    "Managed social media presence across {platforms} with {followers}K+ followers",
                    "Optimized SEO strategy resulting in {percentage}% increase in organic traffic",
                    "Led cross-functional teams to launch {number} successful product campaigns",
                    "Analyzed campaign performance and provided actionable insights",
                    "Managed marketing budget of ${budget}K+"
                ],
                "projects": [
                    "Brand Awareness Campaign",
                    "Product Launch Strategy",
                    "Customer Acquisition Program",
                    "Content Marketing Initiative",
                    "Influencer Partnership Program"
                ]
            }
        }
        return templates
    
    def _load_skill_database(self) -> Dict[str, List[str]]:
        """Load comprehensive skill database"""
        return {
            "programming": ["Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin"],
            "frameworks": ["React", "Angular", "Vue", "Django", "Flask", "Spring", "Express", "Laravel", "Rails"],
            "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra", "DynamoDB", "Elasticsearch"],
            "cloud": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CloudFormation"],
            "ml_tools": ["TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn"],
            "soft_skills": ["Leadership", "Communication", "Problem Solving", "Team Collaboration", "Project Management"]
        }
    
    def _load_company_names(self) -> List[str]:
        """Load list of company names for synthetic data"""
        return [
            "TechCorp Solutions", "DataVision Inc", "CloudTech Systems", "InnovateLab",
            "NextGen Software", "DigitalEdge", "SmartAnalytics", "FutureTech",
            "CodeCraft Studios", "DataFlow Technologies", "CloudNine Solutions",
            "TechPioneer", "IntelliSoft", "CyberTech", "QuantumLeap"
        ]
    
    def generate_resume(self, role: str, experience_level: ExperienceLevel) -> Resume:
        """Generate a synthetic resume for a given role and experience level"""
        logger.info(f"Generating synthetic resume for {role} - {experience_level}")
        
        # Generate contact info
        contact = self._generate_contact_info()
        
        # Generate skills based on role
        skills = self._generate_skills(role)
        
        # Generate work experience
        experience = self._generate_work_experience(role, experience_level)
        
        # Generate education
        education = self._generate_education()
        
        # Generate projects
        projects = self._generate_projects(role)
        
        # Generate summary
        summary = self._generate_summary(role, experience_level)
        
        resume = Resume(
            contact_info=contact,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=self._generate_certifications(role),
            languages=["English"] + random.choices(["Spanish", "French", "German", "Mandarin"], k=random.randint(0, 2)),
            interests=random.choices(["Machine Learning", "Open Source", "Startups", "AI Ethics"], k=random.randint(1, 3))
        )
        
        return resume
    
    def generate_job_description(self, role: str, experience_level: JobLevel) -> JobDescription:
        """Generate a synthetic job description"""
        logger.info(f"Generating job description for {role} - {experience_level}")
        
        template = self.role_templates.get(role, self.role_templates["software_engineer"])
        company = random.choice(self.company_names)
        
        # Generate requirements based on experience level
        requirements = self._generate_jd_requirements(role, experience_level)
        
        # Generate responsibilities
        responsibilities = self._generate_jd_responsibilities(template)
        
        # Generate skills
        required_skills = random.choices(
            [skill for skills in template["skills"].values() for skill in skills],
            k=random.randint(5, 8)
        )
        preferred_skills = random.choices(
            [skill for skills in template["skills"].values() for skill in skills],
            k=random.randint(3, 5)
        )
        
        job_description = JobDescription(
            title=f"{experience_level.value.title()} {role.replace('_', ' ').title()}",
            company=company,
            location=random.choice(["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Remote"]),
            job_type=random.choice(list(JobType)),
            experience_level=experience_level,
            description=f"We are seeking a {experience_level.value} {role.replace('_', ' ')} to join our growing team...",
            requirements=requirements,
            preferred_qualifications=self._generate_preferred_qualifications(role),
            responsibilities=responsibilities,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            industry="Technology",
            salary_range=self._generate_salary_range(experience_level),
            benefits=["Health insurance", "401k", "PTO", "Remote work options"]
        )
        
        return job_description
    
    def _generate_contact_info(self) -> ContactInfo:
        """Generate synthetic contact information"""
        first_names = ["John", "Jane", "Mike", "Sarah", "David", "Lisa", "Chris", "Emma", "Ryan", "Anna"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        return ContactInfo(
            full_name=f"{first_name} {last_name}",
            email=f"{first_name.lower()}.{last_name.lower()}@email.com",
            phone=f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            location=random.choice(["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Boston, MA"]),
            linkedin=f"https://linkedin.com/in/{first_name.lower()}{last_name.lower()}",
            github=f"https://github.com/{first_name.lower()}{last_name.lower()}"
        )
    
    def _generate_skills(self, role: str) -> Dict[str, List[str]]:
        """Generate role-appropriate skills"""
        template = self.role_templates.get(role, self.role_templates["software_engineer"])
        skills = {}
        
        for category, skill_list in template["skills"].items():
            skills[category] = random.choices(skill_list, k=random.randint(3, 6))
            
        return skills
    
    def _generate_work_experience(self, role: str, experience_level: ExperienceLevel) -> List[WorkExperience]:
        """Generate work experience based on role and level"""
        experience_count = {
            ExperienceLevel.ENTRY: 1,
            ExperienceLevel.MID: random.randint(2, 3),
            ExperienceLevel.SENIOR: random.randint(3, 4),
            ExperienceLevel.LEAD: random.randint(4, 5),
            ExperienceLevel.EXECUTIVE: random.randint(5, 7)
        }
        
        experiences = []
        current_date = date.today()
        
        for i in range(experience_count.get(experience_level, 2)):
            # Calculate dates
            years_ago = i * random.randint(2, 4)
            start_date = current_date - timedelta(days=years_ago * 365 + random.randint(0, 365))
            end_date = None if i == 0 else start_date + timedelta(days=random.randint(365, 1095))
            
            company = random.choice(self.company_names)
            position = f"{random.choice(['Junior', 'Senior', 'Lead', 'Principal'])} {role.replace('_', ' ').title()}"
            
            # Generate responsibilities
            template = self.role_templates.get(role, self.role_templates["software_engineer"])
            responsibilities = random.choices(template["responsibilities"], k=random.randint(3, 5))
            
            # Fill in template placeholders
            filled_responsibilities = []
            for resp in responsibilities:
                filled_resp = resp.format(
                    framework=random.choice(template["skills"].get("frameworks", ["React"])),
                    programming=random.choice(template["skills"].get("programming", ["Python"])),
                    database=random.choice(template["skills"].get("databases", ["PostgreSQL"])),
                    percentage=random.randint(10, 50),
                    deployment_tool=random.choice(template["skills"].get("tools", ["Docker"]))
                )
                filled_responsibilities.append(filled_resp)
            
            experience = WorkExperience(
                company=company,
                position=position,
                start_date=start_date,
                end_date=end_date,
                description=filled_responsibilities,
                skills=random.choices([skill for skills in template["skills"].values() for skill in skills], k=5)
            )
            experiences.append(experience)
        
        return experiences
    
    def _generate_education(self) -> List[Education]:
        """Generate educational background"""
        institutions = ["University of California", "Stanford University", "MIT", "Carnegie Mellon", "Georgia Tech"]
        degrees = ["Computer Science", "Data Science", "Software Engineering", "Information Systems"]
        
        education = Education(
            institution=random.choice(institutions),
            degree=f"Bachelor of Science in {random.choice(degrees)}",
            level=EducationLevel.BACHELOR,
            major=random.choice(degrees),
            graduation_date=date.today() - timedelta(days=random.randint(365, 3650)),
            gpa=round(random.uniform(3.2, 4.0), 1),
            relevant_courses=["Algorithms", "Database Systems", "Software Engineering", "Machine Learning"]
        )
        
        return [education]
    
    def _generate_projects(self, role: str) -> List[Project]:
        """Generate role-appropriate projects"""
        template = self.role_templates.get(role, self.role_templates["software_engineer"])
        project_names = template.get("projects", ["Generic Project"])
        
        projects = []
        for i in range(random.randint(2, 4)):
            project_name = random.choice(project_names)
            technologies = random.choices(
                [skill for skills in template["skills"].values() for skill in skills],
                k=random.randint(3, 6)
            )
            
            project = Project(
                name=f"{project_name} {i+1}",
                description=f"Developed a {project_name.lower()} using modern technologies",
                technologies=technologies,
                start_date=date.today() - timedelta(days=random.randint(30, 730)),
                end_date=date.today() - timedelta(days=random.randint(0, 30)),
                url=f"https://github.com/user/project-{i+1}",
                achievements=[
                    f"Implemented {random.choice(technologies)} integration",
                    f"Improved performance by {random.randint(20, 80)}%"
                ]
            )
            projects.append(project)
        
        return projects
    
    def _generate_summary(self, role: str, experience_level: ExperienceLevel) -> str:
        """Generate professional summary"""
        experience_years = {
            ExperienceLevel.ENTRY: "1-2",
            ExperienceLevel.MID: "3-5",
            ExperienceLevel.SENIOR: "5-8",
            ExperienceLevel.LEAD: "8-12",
            ExperienceLevel.EXECUTIVE: "12+"
        }
        
        years = experience_years.get(experience_level, "3-5")
        role_title = role.replace('_', ' ').title()
        
        return f"Experienced {role_title} with {years} years of expertise in developing scalable solutions and leading technical initiatives. Proven track record of delivering high-quality projects and collaborating with cross-functional teams."
    
    def _generate_certifications(self, role: str) -> List[str]:
        """Generate role-appropriate certifications"""
        cert_map = {
            "software_engineer": ["AWS Certified Developer", "Google Cloud Professional", "Certified Kubernetes Administrator"],
            "data_scientist": ["AWS Machine Learning Specialty", "Google Cloud ML Engineer", "Microsoft Azure AI Engineer"],
            "marketing_manager": ["Google Ads Certified", "HubSpot Content Marketing", "Facebook Blueprint"]
        }
        
        certs = cert_map.get(role, ["Professional Certification"])
        return random.choices(certs, k=random.randint(1, 2))
    
    def _generate_jd_requirements(self, role: str, experience_level: JobLevel) -> List[str]:
        """Generate job description requirements"""
        base_requirements = [
            f"{experience_level.value.title()} level experience in {role.replace('_', ' ')}",
            "Bachelor's degree in relevant field or equivalent experience",
            "Strong problem-solving and analytical skills",
            "Excellent communication and teamwork abilities"
        ]
        
        # Add role-specific requirements
        role_specific = {
            "software_engineer": [
                "Proficiency in modern programming languages",
                "Experience with version control systems",
                "Understanding of software development lifecycle"
            ],
            "data_scientist": [
                "Strong statistical and mathematical background",
                "Experience with machine learning frameworks",
                "Proficiency in data visualization tools"
            ],
            "marketing_manager": [
                "Experience with digital marketing platforms",
                "Strong understanding of marketing analytics",
                "Creative thinking and brand management skills"
            ]
        }
        
        specific_reqs = role_specific.get(role, role_specific["software_engineer"])
        return base_requirements + random.choices(specific_reqs, k=2)
    
    def _generate_jd_responsibilities(self, template: Dict[str, Any]) -> List[str]:
        """Generate job description responsibilities"""
        return random.choices(template["responsibilities"], k=random.randint(4, 6))
    
    def _generate_preferred_qualifications(self, role: str) -> List[str]:
        """Generate preferred qualifications for job description"""
        return [
            "Master's degree preferred",
            "Experience in startup/fast-paced environment",
            "Previous leadership or mentoring experience",
            "Industry certifications"
        ]
    
    def _generate_salary_range(self, experience_level: JobLevel) -> Dict[str, int]:
        """Generate salary range based on experience level"""
        salary_ranges = {
            JobLevel.ENTRY: {"min": 70000, "max": 100000},
            JobLevel.MID: {"min": 100000, "max": 140000},
            JobLevel.SENIOR: {"min": 140000, "max": 180000},
            JobLevel.LEAD: {"min": 180000, "max": 220000},
            JobLevel.EXECUTIVE: {"min": 220000, "max": 300000}
        }
        
        return salary_ranges.get(experience_level, salary_ranges[JobLevel.MID])
    
    def generate_dataset(self, num_resumes: int, num_job_descriptions: int) -> Dict[str, List[Dict]]:
        """Generate a complete dataset of resumes and job descriptions"""
        logger.info(f"Generating dataset: {num_resumes} resumes, {num_job_descriptions} job descriptions")
        
        roles = ["software_engineer", "data_scientist", "marketing_manager"]
        experience_levels = list(ExperienceLevel)
        job_levels = list(JobLevel)
        
        # Generate resumes
        resumes = []
        for _ in range(num_resumes):
            role = random.choice(roles)
            exp_level = random.choice(experience_levels)
            resume = self.generate_resume(role, exp_level)
            
            resume_dict = resume.dict()
            resume_dict["role"] = role
            resume_dict["generated_at"] = datetime.now().isoformat()
            resumes.append(resume_dict)
        
        # Generate job descriptions
        job_descriptions = []
        for _ in range(num_job_descriptions):
            role = random.choice(roles)
            job_level = random.choice(job_levels)
            jd = self.generate_job_description(role, job_level)
            
            jd_dict = jd.dict()
            jd_dict["role"] = role
            jd_dict["generated_at"] = datetime.now().isoformat()
            job_descriptions.append(jd_dict)
        
        return {
            "resumes": resumes,
            "job_descriptions": job_descriptions
        }