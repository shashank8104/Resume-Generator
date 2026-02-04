from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class SectionScore(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Section similarity score")
    matched_keywords: List[str] = Field(..., description="Keywords that matched")
    missing_keywords: List[str] = Field(..., description="Important missing keywords")
    feedback: str = Field(..., description="Section-specific feedback")

class ScreeningResult(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall match score")
    section_scores: Dict[str, SectionScore] = Field(..., description="Per-section scores")
    skill_gaps: List[str] = Field(..., description="Missing critical skills")
    recommendations: List[str] = Field(..., description="Improvement recommendations")
    match_explanation: str = Field(..., description="Detailed explanation of the match")
    processed_at: datetime = Field(default_factory=datetime.now, description="Processing timestamp")
    model_version: str = Field(default="1.0", description="Model version used")

class LaTeXPreferences(BaseModel):
    latex_template: str = Field("modern", description="LaTeX template to use")
    color_scheme: str = Field("blue", description="Color scheme for the resume")

class AnalystResumeData(BaseModel):
    """Custom data structure for analyst template"""
    personal_info: Optional[Dict[str, Any]] = Field(None, description="Personal information")
    education: Optional[Dict[str, Any]] = Field(None, description="Education details")
    technical_skills: Optional[Dict[str, Any]] = Field(None, description="Technical skills")
    projects: Optional[List[Dict[str, Any]]] = Field(None, description="Projects list")
    internships: Optional[List[Dict[str, Any]]] = Field(None, description="Internships list")
    achievements: Optional[List[Dict[str, Any]]] = Field(None, description="Achievements list")

class GenerationRequest(BaseModel):
    target_role: str = Field(..., description="Target job role")
    job_description: Optional[str] = Field(None, description="Job description to tailor towards")
    template_preference: Optional[str] = Field(None, description="Preferred template style")
    experience_level: str = Field("mid", description="Experience level for generation")
    preferences: Optional[LaTeXPreferences] = Field(None, description="LaTeX-specific preferences")
    
    # Add analyst template specific fields
    personal_info: Optional[Dict[str, Any]] = Field(None, description="Personal information for analyst template")
    education: Optional[Dict[str, Any]] = Field(None, description="Education for analyst template")
    technical_skills: Optional[Dict[str, Any]] = Field(None, description="Technical skills for analyst template")
    projects: Optional[List[Dict[str, Any]]] = Field(None, description="Projects for analyst template")
    internships: Optional[List[Dict[str, Any]]] = Field(None, description="Internships for analyst template")
    achievements: Optional[List[Dict[str, Any]]] = Field(None, description="Achievements for analyst template")
    
class ContentGenerationRequest(BaseModel):
    content_type: str = Field(..., pattern="^(email|cover_letter|linkedin_prompt)$", description="Type of content to generate")
    target_role: str = Field(..., description="Target job role")
    company_name: str = Field(..., description="Target company name")
    tone: str = Field("professional", pattern="^(professional|friendly|formal)$", description="Tone of content")
    additional_context: Optional[str] = Field(None, description="Additional context or requirements")

class APIResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Optional[Any] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    errors: Optional[List[str]] = Field(None, description="Error messages if any")
    execution_time: Optional[float] = Field(None, description="Processing time in seconds")

class HealthCheck(BaseModel):
    status: str = Field(..., description="Health check status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: str = Field(..., description="API version")
    dependencies: Dict[str, str] = Field(..., description="Dependency status")