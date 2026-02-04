from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum

class JobLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"

class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    REMOTE = "remote"

class JobDescription(BaseModel):
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    job_type: JobType = Field(..., description="Type of employment")
    experience_level: JobLevel = Field(..., description="Required experience level")
    description: str = Field(..., description="Job description text")
    requirements: List[str] = Field(..., description="Required qualifications")
    preferred_qualifications: List[str] = Field(default_factory=list, description="Preferred qualifications")
    responsibilities: List[str] = Field(..., description="Key responsibilities")
    required_skills: List[str] = Field(..., description="Required technical skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills")
    industry: Optional[str] = Field(None, description="Industry sector")
    salary_range: Optional[Dict[str, int]] = Field(None, description="Salary range (min/max)")
    benefits: List[str] = Field(default_factory=list, description="Benefits offered")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Software Engineer",
                "company": "Tech Innovations Inc.",
                "location": "San Francisco, CA",
                "job_type": "full_time",
                "experience_level": "senior",
                "description": "We are seeking a Senior Software Engineer to join our growing team...",
                "requirements": [
                    "5+ years of software development experience",
                    "Bachelor's degree in Computer Science or related field",
                    "Strong proficiency in Python and JavaScript"
                ],
                "preferred_qualifications": [
                    "Master's degree in Computer Science",
                    "Experience with machine learning frameworks"
                ],
                "responsibilities": [
                    "Design and develop scalable software solutions",
                    "Mentor junior developers",
                    "Collaborate with cross-functional teams"
                ],
                "required_skills": [
                    "Python", "JavaScript", "React", "Node.js", "PostgreSQL"
                ],
                "preferred_skills": [
                    "Docker", "Kubernetes", "AWS", "Machine Learning"
                ],
                "industry": "Technology",
                "salary_range": {"min": 120000, "max": 180000},
                "benefits": ["Health insurance", "401k", "Remote work options"]
            }
        }