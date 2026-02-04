from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Union
from datetime import date
from enum import Enum

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"

class EducationLevel(str, Enum):
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    CERTIFICATE = "certificate"

class WorkExperience(BaseModel):
    company: str = Field(..., description="Company name")
    position: str = Field(..., description="Job title/position")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date (None if current)")
    description: List[str] = Field(..., description="List of accomplishments/responsibilities")
    skills: List[str] = Field(default_factory=list, description="Skills used in this role")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class Education(BaseModel):
    institution: str = Field(..., description="Educational institution")
    degree: str = Field(..., description="Degree/certification name")
    level: EducationLevel = Field(..., description="Education level")
    major: Optional[str] = Field(None, description="Major/field of study")
    graduation_date: Optional[date] = Field(None, description="Graduation date")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="GPA if applicable")
    relevant_courses: List[str] = Field(default_factory=list, description="Relevant courses")

class Project(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    technologies: List[str] = Field(..., description="Technologies used")
    start_date: Optional[date] = Field(None, description="Project start date")
    end_date: Optional[date] = Field(None, description="Project end date")
    url: Optional[str] = Field(None, description="Project URL/repository")
    achievements: List[str] = Field(default_factory=list, description="Key achievements")

class ContactInfo(BaseModel):
    full_name: str = Field(..., description="Full name")
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: str = Field(..., description="City, State/Country")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    website: Optional[str] = Field(None, description="Personal website URL")

class Resume(BaseModel):
    contact_info: ContactInfo = Field(..., description="Contact information")
    summary: Optional[str] = Field(None, description="Professional summary")
    skills: Dict[str, List[str]] = Field(..., description="Categorized skills")
    experience: List[WorkExperience] = Field(..., description="Work experience")
    education: List[Education] = Field(..., description="Education background")
    projects: List[Project] = Field(default_factory=list, description="Projects")
    certifications: List[str] = Field(default_factory=list, description="Certifications")
    languages: List[str] = Field(default_factory=list, description="Languages spoken")
    interests: List[str] = Field(default_factory=list, description="Professional interests")
    
    class Config:
        json_schema_extra = {
            "example": {
                "contact_info": {
                    "full_name": "John Doe",
                    "email": "john.doe@email.com",
                    "phone": "+1-555-0123",
                    "location": "San Francisco, CA",
                    "linkedin": "https://linkedin.com/in/johndoe",
                    "github": "https://github.com/johndoe"
                },
                "summary": "Experienced software engineer with 5+ years in full-stack development",
                "skills": {
                    "programming": ["Python", "JavaScript", "Java"],
                    "frameworks": ["React", "Node.js", "Django"],
                    "databases": ["PostgreSQL", "MongoDB"],
                    "tools": ["Git", "Docker", "AWS"]
                },
                "experience": [
                    {
                        "company": "Tech Corp",
                        "position": "Senior Software Engineer",
                        "start_date": "2021-03-01",
                        "end_date": None,
                        "description": [
                            "Led development of microservices architecture",
                            "Mentored 3 junior developers"
                        ],
                        "skills": ["Python", "Docker", "Kubernetes"]
                    }
                ],
                "education": [
                    {
                        "institution": "University of California",
                        "degree": "Bachelor of Science in Computer Science",
                        "level": "bachelor",
                        "major": "Computer Science",
                        "graduation_date": "2018-05-01",
                        "gpa": 3.7
                    }
                ]
            }
        }