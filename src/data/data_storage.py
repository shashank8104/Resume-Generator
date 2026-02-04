import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..models.resume_schema import Resume
from ..models.job_schema import JobDescription
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class DataStorage:
    """Handle structured storage and retrieval of resume and job data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.resumes_dir = self.data_dir / "resumes"
        self.jobs_dir = self.data_dir / "job_descriptions"
        self.metadata_dir = self.data_dir / "metadata"
        
        # Create directories
        self.resumes_dir.mkdir(parents=True, exist_ok=True)
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Data storage initialized at {self.data_dir}")
    
    def save_resume(self, resume: Dict[str, Any], anonymize: bool = True) -> str:
        """Save a resume to structured storage"""
        if anonymize:
            resume = self._anonymize_resume(resume)
        
        # Generate unique ID
        resume_id = self._generate_id(resume)
        resume["id"] = resume_id
        resume["stored_at"] = datetime.now().isoformat()
        
        # Save to JSON
        file_path = self.resumes_dir / f"{resume_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(resume, f, indent=2, default=str)
        
        # Update metadata
        self._update_resume_metadata(resume_id, resume)
        
        logger.info(f"Resume saved with ID: {resume_id}")
        return resume_id
    
    def save_job_description(self, job_description: Dict[str, Any]) -> str:
        """Save a job description to structured storage"""
        # Generate unique ID
        job_id = self._generate_id(job_description)
        job_description["id"] = job_id
        job_description["stored_at"] = datetime.now().isoformat()
        
        # Save to JSON
        file_path = self.jobs_dir / f"{job_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(job_description, f, indent=2, default=str)
        
        # Update metadata
        self._update_job_metadata(job_id, job_description)
        
        logger.info(f"Job description saved with ID: {job_id}")
        return job_id
    
    def load_resume(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """Load a resume by ID"""
        file_path = self.resumes_dir / f"{resume_id}.json"
        
        if not file_path.exists():
            logger.warning(f"Resume not found: {resume_id}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                resume = json.load(f)
            logger.info(f"Resume loaded: {resume_id}")
            return resume
        except Exception as e:
            logger.error(f"Error loading resume {resume_id}: {e}")
            return None
    
    def load_job_description(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Load a job description by ID"""
        file_path = self.jobs_dir / f"{job_id}.json"
        
        if not file_path.exists():
            logger.warning(f"Job description not found: {job_id}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                job_description = json.load(f)
            logger.info(f"Job description loaded: {job_id}")
            return job_description
        except Exception as e:
            logger.error(f"Error loading job description {job_id}: {e}")
            return None
    
    def list_resumes(self, role: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List resumes with optional filtering"""
        metadata = self._load_resume_metadata()
        
        resumes = list(metadata.values())
        
        # Filter by role if specified
        if role:
            resumes = [r for r in resumes if r.get("role") == role]
        
        # Apply limit if specified
        if limit:
            resumes = resumes[:limit]
        
        logger.info(f"Listed {len(resumes)} resumes")
        return resumes
    
    def list_job_descriptions(self, role: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List job descriptions with optional filtering"""
        metadata = self._load_job_metadata()
        
        jobs = list(metadata.values())
        
        # Filter by role if specified
        if role:
            jobs = [j for j in jobs if j.get("role") == role]
        
        # Apply limit if specified
        if limit:
            jobs = jobs[:limit]
        
        logger.info(f"Listed {len(jobs)} job descriptions")
        return jobs
    
    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get statistics about the stored dataset"""
        resume_metadata = self._load_resume_metadata()
        job_metadata = self._load_job_metadata()
        
        # Resume statistics
        resume_roles = {}
        resume_experience_levels = {}
        for resume in resume_metadata.values():
            role = resume.get("role", "unknown")
            exp_level = resume.get("experience_level", "unknown")
            resume_roles[role] = resume_roles.get(role, 0) + 1
            resume_experience_levels[exp_level] = resume_experience_levels.get(exp_level, 0) + 1
        
        # Job description statistics
        job_roles = {}
        job_levels = {}
        for job in job_metadata.values():
            role = job.get("role", "unknown")
            job_level = job.get("experience_level", "unknown")
            job_roles[role] = job_roles.get(role, 0) + 1
            job_levels[job_level] = job_levels.get(job_level, 0) + 1
        
        stats = {
            "total_resumes": len(resume_metadata),
            "total_job_descriptions": len(job_metadata),
            "resume_roles": resume_roles,
            "resume_experience_levels": resume_experience_levels,
            "job_roles": job_roles,
            "job_levels": job_levels,
            "data_directory": str(self.data_dir),
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info("Generated dataset statistics")
        return stats
    
    def bulk_save_dataset(self, dataset: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[str]]:
        """Save a bulk dataset and return IDs"""
        resume_ids = []
        job_ids = []
        
        # Save resumes
        for resume_data in dataset.get("resumes", []):
            resume_id = self.save_resume(resume_data, anonymize=True)
            resume_ids.append(resume_id)
        
        # Save job descriptions
        for job_data in dataset.get("job_descriptions", []):
            job_id = self.save_job_description(job_data)
            job_ids.append(job_id)
        
        logger.info(f"Bulk saved {len(resume_ids)} resumes and {len(job_ids)} job descriptions")
        
        return {
            "resume_ids": resume_ids,
            "job_ids": job_ids
        }
    
    def _anonymize_resume(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize personal information in resume"""
        anonymized = resume.copy()
        
        if "contact_info" in anonymized:
            contact = anonymized["contact_info"]
            # Replace with anonymized versions
            name_parts = contact.get("full_name", "John Doe").split()
            contact["full_name"] = f"{name_parts[0][0]}*** {name_parts[-1][0]}***"
            contact["email"] = f"user{self._generate_hash(contact.get('email', ''))[:6]}@email.com"
            contact["phone"] = "+1-XXX-XXX-XXXX"
            if "linkedin" in contact:
                contact["linkedin"] = "https://linkedin.com/in/anonymous"
            if "github" in contact:
                contact["github"] = "https://github.com/anonymous"
        
        return anonymized
    
    def _generate_id(self, data: Dict[str, Any]) -> str:
        """Generate a unique ID for data"""
        # Create a hash of key fields
        key_data = {
            "timestamp": datetime.now().isoformat(),
            "content": str(data)
        }
        return self._generate_hash(str(key_data))[:12]
    
    def _generate_hash(self, content: str) -> str:
        """Generate hash for content"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _update_resume_metadata(self, resume_id: str, resume: Dict[str, Any]):
        """Update resume metadata index"""
        metadata = self._load_resume_metadata()
        
        metadata[resume_id] = {
            "id": resume_id,
            "role": resume.get("role"),
            "experience_level": resume.get("experience_level"),
            "stored_at": resume.get("stored_at"),
            "skills_count": len(resume.get("skills", {})),
            "experience_count": len(resume.get("experience", [])),
            "education_count": len(resume.get("education", [])),
            "projects_count": len(resume.get("projects", []))
        }
        
        self._save_resume_metadata(metadata)
    
    def _update_job_metadata(self, job_id: str, job_description: Dict[str, Any]):
        """Update job description metadata index"""
        metadata = self._load_job_metadata()
        
        metadata[job_id] = {
            "id": job_id,
            "title": job_description.get("title"),
            "company": job_description.get("company"),
            "role": job_description.get("role"),
            "experience_level": job_description.get("experience_level"),
            "job_type": job_description.get("job_type"),
            "location": job_description.get("location"),
            "stored_at": job_description.get("stored_at"),
            "requirements_count": len(job_description.get("requirements", [])),
            "skills_count": len(job_description.get("required_skills", []))
        }
        
        self._save_job_metadata(metadata)
    
    def _load_resume_metadata(self) -> Dict[str, Any]:
        """Load resume metadata"""
        metadata_file = self.metadata_dir / "resumes_metadata.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading resume metadata: {e}")
        
        return {}
    
    def _load_job_metadata(self) -> Dict[str, Any]:
        """Load job description metadata"""
        metadata_file = self.metadata_dir / "jobs_metadata.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading job metadata: {e}")
        
        return {}
    
    def _save_resume_metadata(self, metadata: Dict[str, Any]):
        """Save resume metadata"""
        metadata_file = self.metadata_dir / "resumes_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    def _save_job_metadata(self, metadata: Dict[str, Any]):
        """Save job description metadata"""
        metadata_file = self.metadata_dir / "jobs_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)