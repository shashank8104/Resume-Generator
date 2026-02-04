"""FastAPI backend for the resume intelligence system"""

import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import uvicorn

from ..models.resume_schema import Resume
from ..models.job_schema import JobDescription
from ..models.api_schema import (
    ScreeningResult, GenerationRequest, ContentGenerationRequest, 
    APIResponse, HealthCheck
)
from ..data.synthetic_data_generator import SyntheticDataGenerator
from ..data.data_storage import DataStorage
from ..generation.resume_generator import ResumeGenerator
from ..generation.content_generator import ContentGenerator
from ..screening.screening_pipeline import ScreeningPipeline
from ..explainability.explainer import ExplainerEngine
from ..evaluation.metrics_calculator import MetricsCalculator
from ..utils.config_loader import load_config, get_api_config
from ..utils.logging_utils import get_logger
from ..utils.latex_generator import LaTeXResumeGenerator, LATEX_TEMPLATES, COLOR_SCHEMES
from ..utils.pdf_extractor import create_pdf_extractor
from .middleware import setup_middleware, log_requests
from .session_manager import SessionManager
from .validators import validate_resume_data, validate_job_data

logger = get_logger(__name__)

# Global instances
app_instances = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Resume Intelligence API...")
    
    # Load configuration
    config = load_config()
    
    # Initialize core components
    app_instances["data_storage"] = DataStorage()
    app_instances["resume_generator"] = ResumeGenerator(config)
    app_instances["content_generator"] = ContentGenerator(config)
    app_instances["screening_pipeline"] = ScreeningPipeline(config)
    app_instances["explainer"] = ExplainerEngine(config)
    app_instances["metrics_calculator"] = MetricsCalculator(config)
    app_instances["session_manager"] = SessionManager()
    app_instances["synthetic_generator"] = SyntheticDataGenerator()
    app_instances["latex_generator"] = LaTeXResumeGenerator()
    
    logger.info("Resume Intelligence API startup complete")
    
    yield
    
    logger.info("Shutting down Resume Intelligence API...")

# Create FastAPI application
app = FastAPI(
    title="Resume Intelligence API",
    description="Production-grade ML-driven resume intelligence system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup middleware
setup_middleware(app)

# Dependency injection helpers
def get_data_storage() -> DataStorage:
    return app_instances["data_storage"]

def get_resume_generator() -> ResumeGenerator:
    return app_instances["resume_generator"]

def get_content_generator() -> ContentGenerator:
    return app_instances["content_generator"]

def get_screening_pipeline() -> ScreeningPipeline:
    return app_instances["screening_pipeline"]

def get_explainer() -> ExplainerEngine:
    return app_instances["explainer"]

def get_metrics_calculator() -> MetricsCalculator:
    return app_instances["metrics_calculator"]

def get_session_manager() -> SessionManager:
    return app_instances["session_manager"]

def get_synthetic_generator() -> SyntheticDataGenerator:
    return app_instances["synthetic_generator"]

def get_latex_generator() -> LaTeXResumeGenerator:
    """Dependency to get LaTeX generator instance"""
    return app_instances["latex_generator"]

# API Routes

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Resume Intelligence API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    dependencies = {
        "data_storage": "healthy",
        "resume_generator": "healthy",
        "screening_pipeline": "healthy",
        "content_generator": "healthy"
    }
    
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        dependencies=dependencies
    )

# Resume Generation Endpoints

@app.post("/api/v1/generate/resume", response_model=APIResponse)
async def generate_resume(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    resume_generator: ResumeGenerator = Depends(get_resume_generator),
    data_storage: DataStorage = Depends(get_data_storage)
):
    """Generate a tailored resume based on user input and job description"""
    start_time = time.time()
    
    try:
        logger.info(f"Resume generation request for role: {request.target_role}")
        
        # Validate request
        if not request.target_role:
            raise HTTPException(status_code=400, detail="Target role is required")
        
        # Convert experience level string to enum
        from ..models.resume_schema import ExperienceLevel
        try:
            experience_level = ExperienceLevel(request.experience_level)
        except ValueError:
            experience_level = ExperienceLevel.MID  # Default fallback
        
        # Prepare base information (simplified for demo)
        base_info = {
            "role": request.target_role,
            "experience_level": experience_level,
            "contact_info": {
                "full_name": "John Doe",  # In production, get from user input
                "email": "john.doe@example.com",
                "location": "San Francisco, CA"
            },
            "skills": {
                "programming": ["Python", "JavaScript", "Java"],
                "frameworks": ["React", "Django", "Flask"],
                "tools": ["Git", "Docker", "AWS"]
            },
            "experience": [
                {
                    "company": "Tech Corp",
                    "position": "Software Engineer",
                    "start_date": "2021-01-01",
                    "description": ["Developed web applications", "Collaborated with team"],
                    "skills": ["Python", "React", "PostgreSQL"]
                }
            ],
            "education": [
                {
                    "institution": "University of California",
                    "degree": "Bachelor of Science in Computer Science",
                    "level": "bachelor",
                    "major": "Computer Science",
                    "graduation_date": "2020-05-01"
                }
            ]
        }
        
        # Parse job description if provided
        target_job = None
        if request.job_description:
            # In production, parse job description into JobDescription object
            pass
        
        # Generate resume
        resume, metadata = resume_generator.generate_resume(
            base_info=base_info,
            target_job=target_job,
            template_preference=request.template_preference,
            iterative_improvement=True
        )
        
        # Store generated resume in background
        background_tasks.add_task(
            _store_generated_resume, 
            data_storage, 
            resume.dict(), 
            metadata
        )
        
        execution_time = time.time() - start_time
        
        return APIResponse(
            success=True,
            data={
                "resume": resume.dict(),
                "metadata": metadata,
                "format": "json"
            },
            message="Resume generated successfully",
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error generating resume: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Failed to generate resume",
            errors=[str(e)],
            execution_time=time.time() - start_time
        )

@app.post("/api/v1/generate/resume/pdf")
async def generate_resume_pdf(
    resume_data: Dict[str, Any]
):
    """Generate a downloadable resume file (PDF if available, otherwise formatted text)"""
    try:
        logger.info("Resume download request received")
        from fastapi.responses import Response
        
        # Always use text fallback for now since reportlab installation is problematic
        logger.info("Generating formatted text resume")
        
        # Generate text version
        text_content = _generate_text_resume(resume_data)
        
        # Create filename
        name = resume_data.get('contact_info', {}).get('full_name', 'resume')
        filename = f"{name.replace(' ', '_')}.txt"
        
        return Response(
            content=text_content.encode('utf-8'),
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating resume file: {str(e)}")
        # Return a simple error response instead of raising HTTPException
        error_content = f"Error generating resume: {str(e)}"
        return Response(
            content=error_content.encode('utf-8'),
            media_type="text/plain",
            headers={
                "Content-Disposition": 'attachment; filename="resume_error.txt"',
                "Content-Type": "text/plain; charset=utf-8"
            }
        )

def _generate_text_resume(resume_data: Dict[str, Any]) -> str:
    """Generate a well-formatted text version of the resume"""
    lines = []
    
    try:
        # Header
        contact_info = resume_data.get('contact_info', {})
        name = contact_info.get('full_name', 'Resume')
        if name and name != 'Resume':
            lines.append(name.upper())
            lines.append('=' * len(name))
            lines.append('')
        
        # Contact details
        contact_parts = []
        if contact_info.get('email'):
            contact_parts.append(f"Email: {contact_info['email']}")
        if contact_info.get('phone'):
            contact_parts.append(f"Phone: {contact_info['phone']}")
        if contact_info.get('location'):
            contact_parts.append(f"Location: {contact_info['location']}")
        
        if contact_parts:
            lines.extend(contact_parts)
            lines.append('')
        
        # Professional Summary
        summary = resume_data.get('summary')
        if summary and summary.strip():
            lines.append('PROFESSIONAL SUMMARY')
            lines.append('-' * 20)
            lines.append(summary.strip())
            lines.append('')
        
        # Skills
        skills = resume_data.get('skills', {})
        if skills:
            lines.append('SKILLS')
            lines.append('-' * 6)
            for category, skill_list in skills.items():
                if isinstance(skill_list, list) and skill_list:
                    lines.append(f"{category.replace('_', ' ').title()}: {', '.join(skill_list)}")
                elif isinstance(skill_list, str) and skill_list.strip():
                    lines.append(f"{category.replace('_', ' ').title()}: {skill_list}")
            lines.append('')
        
        # Experience
        experience = resume_data.get('experience', [])
        if experience:
            lines.append('PROFESSIONAL EXPERIENCE')
            lines.append('-' * 23)
            for job in experience:
                if not isinstance(job, dict):
                    continue
                    
                position = job.get('position', '')
                company = job.get('company', '')
                if position or company:
                    job_title = f"{position} at {company}" if position and company else position or company
                    lines.append(job_title)
                
                start_date = job.get('start_date', '')
                end_date = job.get('end_date', 'Present')
                if start_date:
                    lines.append(f"{start_date} - {end_date}")
                
                description = job.get('description', [])
                if isinstance(description, list):
                    for desc in description:
                        if desc and desc.strip():
                            lines.append(f"• {desc.strip()}")
                elif isinstance(description, str) and description.strip():
                    lines.append(f"• {description.strip()}")
                
                lines.append('')
        
        # Education
        education = resume_data.get('education', [])
        if education:
            lines.append('EDUCATION')
            lines.append('-' * 9)
            for edu in education:
                if not isinstance(edu, dict):
                    continue
                    
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                graduation_date = edu.get('graduation_date', '')
                
                edu_line_parts = []
                if degree:
                    edu_line_parts.append(degree)
                if institution:
                    edu_line_parts.append(institution)
                if graduation_date:
                    edu_line_parts.append(f"({graduation_date})")
                
                if edu_line_parts:
                    lines.append(' - '.join(edu_line_parts))
                
                gpa = edu.get('gpa')
                if gpa:
                    lines.append(f"GPA: {gpa}")
            lines.append('')
        
        # If no content was generated, add a basic message
        if len(lines) <= 3:  # Only headers
            lines.extend([
                'RESUME',
                '======',
                '',
                'No resume data available to display.',
                'Please generate a resume first using the form.'
            ])
        
        return '\n'.join(lines)
        
    except Exception as e:
        logger.error(f"Error in text resume generation: {str(e)}")
        return f"""RESUME GENERATION ERROR
=======================

An error occurred while formatting the resume:
{str(e)}

Raw resume data:
{str(resume_data)}
"""

@app.post("/api/v1/generate/content", response_model=APIResponse)
async def generate_content(
    request: ContentGenerationRequest,
    content_generator: ContentGenerator = Depends(get_content_generator)
):
    """Generate professional content (emails, cover letters, etc.)"""
    start_time = time.time()
    
    try:
        logger.info(f"Content generation request: {request.content_type} for {request.target_role}")
        
        # Generate content based on type
        if request.content_type == "email":
            content = content_generator.generate_email(
                target_role=request.target_role,
                company_name=request.company_name,
                tone=request.tone,
                context=request.additional_context
            )
        elif request.content_type == "cover_letter":
            content = content_generator.generate_cover_letter(
                target_role=request.target_role,
                company_name=request.company_name,
                tone=request.tone,
                context=request.additional_context
            )
        elif request.content_type == "linkedin_prompt":
            content = content_generator.generate_linkedin_prompt(
                target_role=request.target_role,
                company_name=request.company_name,
                context=request.additional_context
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported content type: {request.content_type}")
        
        execution_time = time.time() - start_time
        
        return APIResponse(
            success=True,
            data={
                "content": content,
                "content_type": request.content_type,
                "target_role": request.target_role,
                "company_name": request.company_name,
                "tone": request.tone
            },
            message="Content generated successfully",
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Failed to generate content",
            errors=[str(e)],
            execution_time=time.time() - start_time
        )

# Resume Screening Endpoints

@app.post("/api/v1/screen/resume", response_model=APIResponse)
async def screen_resume(
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
    explain: bool = True,
    screening_pipeline: ScreeningPipeline = Depends(get_screening_pipeline),
    explainer: ExplainerEngine = Depends(get_explainer)
):
    """Screen a resume against a job description with detailed analysis"""
    start_time = time.time()
    
    try:
        logger.info("Resume screening request received")
        
        # Validate input data
        resume = Resume(**resume_data)
        job_description = JobDescription(**job_data)
        
        # Perform screening
        screening_result = screening_pipeline.screen_resume(
            resume=resume,
            job_description=job_description,
            explain=explain
        )
        
        # Generate additional explanations if requested
        if explain:
            detailed_explanation = explainer.explain_screening_result(
                resume=resume,
                job_description=job_description,
                screening_result=screening_result
            )
            screening_result_dict = screening_result.dict()
            screening_result_dict["detailed_explanation"] = detailed_explanation
        else:
            screening_result_dict = screening_result.dict()
        
        execution_time = time.time() - start_time
        
        return APIResponse(
            success=True,
            data=screening_result_dict,
            message="Resume screening completed successfully",
            execution_time=execution_time
        )
        
    except ValidationError as e:
        logger.error(f"Validation error in resume screening: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Invalid input data format",
            errors=[str(e)],
            execution_time=time.time() - start_time
        )
    except Exception as e:
        logger.error(f"Error screening resume: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Failed to screen resume",
            errors=[str(e)],
            execution_time=time.time() - start_time
        )

@app.post("/api/v1/screen/pdf", response_model=APIResponse)
async def screen_resume_pdf(
    resume_pdf: UploadFile = File(...),
    job_description: str = "",
    explain: bool = True,
    screening_pipeline: ScreeningPipeline = Depends(get_screening_pipeline),
    explainer: ExplainerEngine = Depends(get_explainer)
):
    """Screen a resume PDF against a job description with ATS scoring"""
    start_time = time.time()
    
    try:
        logger.info(f"PDF screening request received for file: {resume_pdf.filename}")
        
        # Validate file type
        if not resume_pdf.filename.lower().endswith('.pdf'):
            return APIResponse(
                success=False,
                data=None,
                message="Only PDF files are supported",
                errors=["Invalid file type"],
                execution_time=time.time() - start_time
            )
        
        # Read PDF content
        pdf_content = await resume_pdf.read()
        
        # Extract text from PDF
        pdf_extractor = create_pdf_extractor()
        extraction_result = pdf_extractor.extract_text_and_analyze(pdf_content)
        
        if not extraction_result["analysis"]["extraction_successful"]:
            return APIResponse(
                success=False,
                data=None,
                message="Failed to extract text from PDF",
                errors=[extraction_result["analysis"].get("error", "Unknown extraction error")],
                execution_time=time.time() - start_time
            )
        
        resume_text = extraction_result["text"]
        
        if not resume_text.strip():
            return APIResponse(
                success=False,
                data=None,
                message="No text content found in the PDF",
                errors=["Empty or unreadable PDF"],
                execution_time=time.time() - start_time
            )
        
        # Enhanced text-based analysis for PDF content
        # Clean and normalize text
        resume_text_clean = resume_text.lower()
        job_description_clean = job_description.lower()
        
        # Define important skill categories and keywords
        technical_skills = [
            'python', 'sql', 'r', 'excel', 'tableau', 'powerbi', 'power bi', 
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
            'machine learning', 'data analysis', 'data science', 'statistics',
            'data visualization', 'analytics', 'database', 'etl'
        ]
        
        soft_skills = [
            'communication', 'problem solving', 'analytical', 'leadership',
            'teamwork', 'presentation', 'critical thinking', 'detail oriented'
        ]
        
        domain_skills = [
            'business intelligence', 'reporting', 'dashboard', 'kpi',
            'data mining', 'predictive modeling', 'forecasting'
        ]
        
        all_key_skills = technical_skills + soft_skills + domain_skills
        
        # Count skill matches with balanced criteria
        skill_matches = 0
        matched_skills = []
        missing_skills = []
        
        for skill in all_key_skills:
            skill_in_resume = skill in resume_text_clean
            skill_in_job = skill in job_description_clean
            
            if skill_in_resume and skill_in_job:
                # Perfect match - skill in both resume and job
                skill_matches += 1
                matched_skills.append(skill)
            elif skill_in_resume and not skill_in_job:
                # Resume has skill but job doesn't require it - still valuable
                skill_matches += 0.3
                matched_skills.append(skill)
            elif skill_in_job and not skill_in_resume:
                # Job requires skill but resume doesn't have it
                missing_skills.append(skill)
        
        # Calculate keyword overlap (basic matching)
        resume_words = set(word.strip('.,!?;:()[]{}') for word in resume_text_clean.split() if len(word.strip('.,!?;:()[]{}')) > 2)
        job_words = set(word.strip('.,!?;:()[]{}') for word in job_description_clean.split() if len(word.strip('.,!?;:()[]{}')) > 2)
        
        common_words = resume_words.intersection(job_words)
        # Filter out very common words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'have', 'let', 'put', 'say', 'she', 'too', 'use'}
        meaningful_matches = common_words - stop_words
        
        # SIMPLE AND EFFECTIVE ATS SCORING
        
        # Step 1: Count EXACT skill matches (skills that appear in BOTH resume AND job)
        exact_skill_matches = 0
        matched_skills = []
        missing_skills = []
        
        for skill in all_key_skills:
            if skill in resume_text_clean and skill in job_description_clean:
                exact_skill_matches += 1
                matched_skills.append(skill)
            elif skill in job_description_clean and skill not in resume_text_clean:
                missing_skills.append(skill)
        
        # Step 2: Simple scoring based on exact matches
        if exact_skill_matches == 0:
            # NO relevant skills found - very poor match
            ats_score = 15 + min(10, len(meaningful_matches))  # 15-25 range
        elif exact_skill_matches == 1:
            # Only 1 skill match - poor match
            ats_score = 30 + min(15, len(meaningful_matches) * 2)  # 30-45 range
        elif exact_skill_matches == 2:
            # 2 skill matches - fair match
            ats_score = 50 + min(15, len(meaningful_matches) * 2)  # 50-65 range
        elif exact_skill_matches == 3:
            # 3 skill matches - good match
            ats_score = 65 + min(15, len(meaningful_matches) * 2)  # 65-80 range
        else:
            # 4+ skill matches - excellent match
            ats_score = 75 + min(20, len(meaningful_matches) * 2)  # 75-95 range
        
        # Step 3: Quality bonus (only for decent matches)
        if exact_skill_matches >= 2:
            resume_word_count = len(resume_text.split())
            if resume_word_count >= 200:
                ats_score += 5
            if any(word in resume_text_clean for word in ['experience', 'project', 'year', 'years']):
                ats_score += 3
        
        # Final score
        ats_score = max(10, min(100, ats_score))
        
        # Create simple, clear results
        screening_result_dict = {
            "overall_score": ats_score / 100,
            "ats_score": round(ats_score, 1),
            "overall_rating": "excellent" if ats_score >= 75 else "good" if ats_score >= 55 else "fair" if ats_score >= 35 else "poor",
            "summary": f"Found {exact_skill_matches} exact skill matches and {len(meaningful_matches)} keyword matches with the job requirements.",
            "skills_analysis": {
                "matched_skills": matched_skills,
                "missing_skills": missing_skills[:10],
                "additional_skills": []
            },
            "recommendations": [
                f"Excellent! {exact_skill_matches} key skills match perfectly with the job requirements." if exact_skill_matches >= 4
                else f"Good match with {exact_skill_matches} relevant skills found." if exact_skill_matches >= 2
                else f"Poor match - only {exact_skill_matches} relevant skills. Add: {', '.join(missing_skills[:5])}" if missing_skills
                else "Very poor match. This resume doesn't align with the job requirements.",
                "Add specific examples and quantifiable achievements.",
                "Use exact keywords and phrases from the job posting.",
                "Highlight experience with the tools and technologies mentioned in the job."
            ],
            "explanation": f"ATS Score: {ats_score:.1f}/100. Based on {exact_skill_matches} exact skill matches. {len(meaningful_matches)} supporting keywords found. {'Strong' if exact_skill_matches >= 3 else 'Weak' if exact_skill_matches <= 1 else 'Moderate'} alignment detected.",
            "pdf_analysis": extraction_result["analysis"],
            "source": "pdf_upload",
            "filename": resume_pdf.filename
        }
        
        execution_time = time.time() - start_time
        
        return APIResponse(
            success=True,
            data=screening_result_dict,
            message=f"PDF resume screening completed successfully. ATS Score: {ats_score:.1f}/100",
            execution_time=execution_time
        )
        
    except ValidationError as e:
        logger.error(f"Validation error in PDF screening: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Invalid input data format",
            errors=[str(e)],
            execution_time=time.time() - start_time
        )
    except Exception as e:
        logger.error(f"Error screening PDF resume: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Failed to screen PDF resume",
            errors=[str(e)],
            execution_time=time.time() - start_time
        )

@app.post("/api/v1/screen/batch", response_model=APIResponse)
async def batch_screen_resumes(
    resumes_data: List[Dict[str, Any]],
    job_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    explain: bool = False,
    screening_pipeline: ScreeningPipeline = Depends(get_screening_pipeline)
):
    """Batch screen multiple resumes against a job description"""
    start_time = time.time()
    
    try:
        logger.info(f"Batch screening request for {len(resumes_data)} resumes")
        
        # Validate input data
        resumes = [Resume(**resume_data) for resume_data in resumes_data]
        job_description = JobDescription(**job_data)
        
        # Perform batch screening
        screening_results = screening_pipeline.batch_screen_resumes(
            resumes=resumes,
            job_description=job_description,
            explain=explain
        )
        
        # Process results in background for analytics
        background_tasks.add_task(
            _process_batch_results, 
            screening_results, 
            job_description.title
        )
        
        execution_time = time.time() - start_time
        
        return APIResponse(
            success=True,
            data={
                "results": [result.dict() for result in screening_results],
                "total_processed": len(screening_results),
                "job_title": job_description.title
            },
            message=f"Batch screening completed for {len(screening_results)} resumes",
            execution_time=execution_time
        )
        
    except ValidationError as e:
        logger.error(f"Validation error in batch screening: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Invalid input data format",
            errors=[str(e)],
            execution_time=time.time() - start_time
        )
    except Exception as e:
        logger.error(f"Error in batch screening: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Failed to perform batch screening",
            errors=[str(e)],
            execution_time=time.time() - start_time
        )

# Data Management Endpoints

@app.get("/api/v1/data/stats", response_model=APIResponse)
async def get_data_stats(
    data_storage: DataStorage = Depends(get_data_storage)
):
    """Get statistics about stored dataset"""
    try:
        stats = data_storage.get_dataset_stats()
        
        return APIResponse(
            success=True,
            data=stats,
            message="Dataset statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving data stats: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Failed to retrieve dataset statistics",
            errors=[str(e)]
        )

@app.post("/api/v1/data/generate", response_model=APIResponse)
async def generate_synthetic_data(
    background_tasks: BackgroundTasks,
    num_resumes: int = 100,
    num_jobs: int = 50,
    synthetic_generator: SyntheticDataGenerator = Depends(get_synthetic_generator),
    data_storage: DataStorage = Depends(get_data_storage)
):
    """Generate synthetic training data"""
    start_time = time.time()
    
    try:
        logger.info(f"Generating synthetic data: {num_resumes} resumes, {num_jobs} jobs")
        
        # Generate dataset
        dataset = synthetic_generator.generate_dataset(num_resumes, num_jobs)
        
        # Store dataset in background
        background_tasks.add_task(
            _store_synthetic_dataset,
            data_storage,
            dataset
        )
        
        execution_time = time.time() - start_time
        
        return APIResponse(
            success=True,
            data={
                "resumes_generated": len(dataset["resumes"]),
                "jobs_generated": len(dataset["job_descriptions"])
            },
            message="Synthetic data generation initiated",
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error generating synthetic data: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Failed to generate synthetic data",
            errors=[str(e)],
            execution_time=time.time() - start_time
        )

# Evaluation Endpoints

@app.get("/api/v1/evaluate/models", response_model=APIResponse)
async def evaluate_models(
    background_tasks: BackgroundTasks,
    metrics_calculator: MetricsCalculator = Depends(get_metrics_calculator)
):
    """Evaluate model performance metrics"""
    try:
        # Run evaluation in background
        background_tasks.add_task(_run_model_evaluation, metrics_calculator)
        
        return APIResponse(
            success=True,
            data={"status": "evaluation_started"},
            message="Model evaluation initiated in background"
        )
        
    except Exception as e:
        logger.error(f"Error starting model evaluation: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Failed to start model evaluation",
            errors=[str(e)]
        )

# Session Management Endpoints

@app.post("/api/v1/session/create")
async def create_session(
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Create a new user session"""
    try:
        session_id = session_manager.create_session()
        
        return APIResponse(
            success=True,
            data={"session_id": session_id},
            message="Session created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Failed to create session",
            errors=[str(e)]
        )

@app.get("/api/v1/session/{session_id}/history")
async def get_session_history(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get session request history"""
    try:
        history = session_manager.get_session_history(session_id)
        
        return APIResponse(
            success=True,
            data={"history": history},
            message="Session history retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving session history: {e}")
        return APIResponse(
            success=False,
            data=None,
            message="Failed to retrieve session history",
            errors=[str(e)]
        )

# LaTeX Resume Generation Endpoints
@app.post("/api/v1/generate/resume/latex", response_model=APIResponse)
async def generate_latex_resume(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    resume_generator: ResumeGenerator = Depends(get_resume_generator),
    latex_generator: LaTeXResumeGenerator = Depends(get_latex_generator),
    data_storage: DataStorage = Depends(get_data_storage)
):
    """Generate LaTeX resume with downloadable source"""
    start_time = time.time()
    
    try:
        logger.info(f"LaTeX resume generation request for role: {request.target_role}")
        
        # Validate request
        if not request.target_role:
            raise HTTPException(status_code=400, detail="Target role is required")

        # Convert experience level string to enum
        from ..models.resume_schema import ExperienceLevel
        try:
            experience_level = ExperienceLevel(request.experience_level)
        except ValueError:
            experience_level = ExperienceLevel.MID

        # Prepare base information
        base_info = {
            "role": request.target_role,
            "experience_level": experience_level,
            "contact_info": {
                "full_name": "John Doe",  
                "email": "john.doe@example.com",
                "phone": "+1 (555) 123-4567",
                "location": "San Francisco, CA",
                "linkedin": "https://linkedin.com/in/johndoe",
                "github": "https://github.com/johndoe"
            }
        }

        # Handle job description if provided
        target_job = None
        if request.job_description:
            pass

        # Generate resume data first
        resume, metadata = resume_generator.generate_resume(
            base_info=base_info,
            target_job=target_job,
            template_preference=request.template_preference,
            iterative_improvement=True
        )

        # Transform data for analyst template if needed
        template_style = request.preferences.latex_template if request.preferences else 'modern'
        resume_data = resume.dict()
        
        if template_style == 'analyst':
            # Check if custom analyst data was provided in the request
            if (request.personal_info or request.education or request.technical_skills or 
                request.projects or request.internships or request.achievements):
                # Use custom analyst data from request
                resume_data = {
                    'personal_info': request.personal_info or {},
                    'education': request.education or {},
                    'technical_skills': request.technical_skills or {},
                    'projects': request.projects or [],
                    'internships': request.internships or [],
                    'achievements': request.achievements or []
                }
            else:
                # Transform standard resume data to analyst template format (fallback)
                resume_data = {
                    'personal_info': {
                        'full_name': resume_data.get('contact_info', {}).get('full_name', 'Your Name'),
                        'phone': resume_data.get('contact_info', {}).get('phone', '+1-xxx-xxx-xxxx'),
                        'email': resume_data.get('contact_info', {}).get('email', 'email@example.com'),
                        'linkedin': resume_data.get('contact_info', {}).get('linkedin', '#'),
                        'github': resume_data.get('contact_info', {}).get('github', '#'),
                    },
                    'education': {
                        'university': resume_data.get('education', [{}])[0].get('institution', 'University Name') if resume_data.get('education') else 'University Name',
                        'graduation_date': resume_data.get('education', [{}])[0].get('graduation_date', 'Expected May 2026') if resume_data.get('education') else 'Expected May 2026',
                        'degree': resume_data.get('education', [{}])[0].get('degree', 'Bachelor of Technology') if resume_data.get('education') else 'Bachelor of Technology',
                        'major': resume_data.get('education', [{}])[0].get('major', 'Computer Science') if resume_data.get('education') else 'Computer Science'
                    },
                    'technical_skills': {
                        'programming_languages': ', '.join(resume_data.get('skills', {}).get('programming', ['Python', 'JavaScript'])),
                        'data_libraries': ', '.join(resume_data.get('skills', {}).get('frameworks', ['pandas', 'NumPy'])),
                        'tools_platforms': ', '.join(resume_data.get('skills', {}).get('tools', ['Excel', 'Power BI'])),
                        'core_skills': ', '.join(resume_data.get('skills', {}).get('databases', ['Data Analysis', 'Machine Learning'])),
                        'soft_skills': 'Analytical Reasoning, Communication'
                    },
                    'projects': [
                        {
                            'name': proj.get('name', 'Project'),
                            'technologies': ', '.join(proj.get('skills', [])) if proj.get('skills') else 'Technologies',
                            'github_link': proj.get('url', '#'),
                            'date': 'Recent',
                            'description': proj.get('achievements', [proj.get('description', 'Project description')])
                        }
                        for proj in resume_data.get('projects', [])
                    ],
                    'internships': [
                        {
                            'company': exp.get('company', 'Company'),
                            'location': 'Location',
                            'position': exp.get('position', 'Position'),
                            'dates': f"{exp.get('start_date', 'Start')} - {exp.get('end_date', 'End')}",
                            'description': exp.get('description', ['Experience description'])
                        }
                        for exp in resume_data.get('experience', [])
                    ],
                    'achievements': [
                        {
                            'name': cert,
                            'issuer': 'Organization',
                            'date': 'Date',
                            'link': '#'
                        }
                        for cert in resume_data.get('certifications', [])
                    ]
                }

        # Generate LaTeX code
        latex_code = latex_generator.generate_latex_resume(
            resume_data=resume_data,
            template_style=template_style,
            color_scheme=request.preferences.color_scheme if request.preferences else 'blue'
        )

        # Store generated resume in background
        background_tasks.add_task(
            _store_generated_resume, 
            data_storage, 
            resume.dict(), 
            metadata
        )

        execution_time = time.time() - start_time

        return APIResponse(
            success=True,
            data={
                "latex_source": latex_code,
                "resume_data": resume.dict(),
                "metadata": metadata,
                "template_info": LATEX_TEMPLATES.get(
                    request.preferences.latex_template if request.preferences else 'modern'
                )
            },
            message="LaTeX resume generated successfully",
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"LaTeX generation error: {str(e)}")
        return APIResponse(
            success=False,
            data=None,
            message="Failed to generate LaTeX resume",
            errors=[str(e)],
            execution_time=time.time() - start_time
        )

@app.post("/api/v1/generate/resume/latex/download")
async def download_latex_source(
    request: Dict[str, Any],
    latex_generator: LaTeXResumeGenerator = Depends(get_latex_generator)
):
    """Download LaTeX source file"""
    try:
        from fastapi.responses import Response
        
        latex_code = request.get('latex_code', '')
        if not latex_code:
            raise HTTPException(status_code=400, detail="LaTeX code is required")

        filename = f"resume_latex_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex"
        
        return Response(
            content=latex_code,
            media_type="application/x-tex",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/x-tex; charset=utf-8"
            }
        )
        
    except Exception as e:
        logger.error(f"LaTeX download error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download LaTeX file")

@app.post("/api/v1/generate/resume/latex/compile")
async def compile_latex_to_pdf(
    request: Dict[str, Any],
    latex_generator: LaTeXResumeGenerator = Depends(get_latex_generator)
):
    """Compile LaTeX code to PDF"""
    try:
        from fastapi.responses import Response, FileResponse
        
        latex_code = request.get('latex_code', '')
        if not latex_code:
            raise HTTPException(status_code=400, detail="LaTeX code is required")
        
        # Try to compile to PDF
        pdf_path = latex_generator.compile_latex_to_pdf(latex_code)
        
        if pdf_path and os.path.exists(pdf_path):
            return FileResponse(
                path=pdf_path,
                media_type='application/pdf',
                filename=f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
        else:
            # Fallback: return the LaTeX source as text file
            return Response(
                content=latex_code.encode('utf-8'),
                media_type="text/plain",
                headers={
                    "Content-Disposition": f'attachment; filename="resume_{datetime.now().strftime("%Y%m%d_%H%M%S")}.tex"',
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )
            
    except Exception as e:
        logger.error(f"PDF compilation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compile PDF")

@app.get("/api/v1/templates/latex")
async def get_latex_templates():
    """Get available LaTeX templates and color schemes"""
    return APIResponse(
        success=True,
        data={
            "templates": LATEX_TEMPLATES,
            "color_schemes": COLOR_SCHEMES
        },
        message="LaTeX templates retrieved successfully"
    )

@app.post("/api/v1/parse/latex")
async def parse_latex_resume(
    request: Dict[str, Any],
    latex_generator: LaTeXResumeGenerator = Depends(get_latex_generator)
):
    """Parse existing LaTeX resume"""
    try:
        latex_content = request.get('latex_content', '')
        if not latex_content:
            raise HTTPException(status_code=400, detail="LaTeX content is required")
        
        parsed_data = latex_generator.parse_existing_latex(latex_content)
        
        return APIResponse(
            success=True,
            data=parsed_data,
            message="LaTeX resume parsed successfully"
        )
        
    except Exception as e:
        logger.error(f"LaTeX parsing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse LaTeX resume")

# Background Task Functions

async def _store_generated_resume(
    data_storage: DataStorage, 
    resume_data: Dict[str, Any], 
    metadata: Dict[str, Any]
):
    """Store generated resume in background"""
    try:
        resume_data["metadata"] = metadata
        resume_id = data_storage.save_resume(resume_data, anonymize=False)
        logger.info(f"Stored generated resume with ID: {resume_id}")
    except Exception as e:
        logger.error(f"Error storing generated resume: {e}")

async def _process_batch_results(
    results: List[ScreeningResult], 
    job_title: str
):
    """Process batch screening results for analytics"""
    try:
        scores = [result.overall_score for result in results]
        avg_score = sum(scores) / len(scores)
        
        logger.info(f"Batch processing complete for {job_title}: {len(results)} resumes, avg score: {avg_score:.3f}")
    except Exception as e:
        logger.error(f"Error processing batch results: {e}")

async def _store_synthetic_dataset(
    data_storage: DataStorage,
    dataset: Dict[str, List[Dict[str, Any]]]
):
    """Store synthetic dataset in background"""
    try:
        result = data_storage.bulk_save_dataset(dataset)
        logger.info(f"Stored synthetic dataset: {len(result['resume_ids'])} resumes, {len(result['job_ids'])} jobs")
    except Exception as e:
        logger.error(f"Error storing synthetic dataset: {e}")

async def _run_model_evaluation(metrics_calculator: MetricsCalculator):
    """Run model evaluation in background"""
    try:
        evaluation_results = metrics_calculator.run_comprehensive_evaluation()
        logger.info(f"Model evaluation completed: {evaluation_results}")
    except Exception as e:
        logger.error(f"Error in model evaluation: {e}")

# Error Handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "errors": [exc.detail]
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": [str(error) for error in exc.errors()]
        }
    )

# Development server
if __name__ == "__main__":
    config = get_api_config()
    uvicorn.run(
        "src.api.main:app",
        host=config.get("host", "0.0.0.0"),
        port=config.get("port", 8000),
        reload=True,
        log_level=config.get("log_level", "info").lower()
    )