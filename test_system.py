"""
Simple test script to verify the Resume Intelligence System works end-to-end
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.synthetic_data_generator import SyntheticDataGenerator
from src.data.data_storage import DataStorage
from src.generation.resume_generator import ResumeGenerator
from src.screening.screening_pipeline import ScreeningPipeline
from src.evaluation.metrics_calculator import MetricsCalculator
from src.models.resume_schema import ExperienceLevel
from src.models.job_schema import JobLevel
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def test_data_generation():
    """Test synthetic data generation"""
    print("🔄 Testing synthetic data generation...")
    
    try:
        generator = SyntheticDataGenerator()
        
        # Generate a single resume
        resume = generator.generate_resume("software_engineer", ExperienceLevel.MID)
        print(f"✅ Generated resume for: {resume.contact_info.full_name}")
        
        # Generate a single job description
        job = generator.generate_job_description("software_engineer", JobLevel.MID)
        print(f"✅ Generated job: {job.title} at {job.company}")
        
        # Generate a small dataset
        dataset = generator.generate_dataset(5, 3)
        print(f"✅ Generated dataset: {len(dataset['resumes'])} resumes, {len(dataset['job_descriptions'])} jobs")
        
        return True, resume, job, dataset
    
    except Exception as e:
        print(f"❌ Data generation failed: {e}")
        return False, None, None, None

def test_data_storage(dataset):
    """Test data storage functionality"""
    print("\n🔄 Testing data storage...")
    
    try:
        storage = DataStorage()
        
        # Store dataset
        result = storage.bulk_save_dataset(dataset)
        print(f"✅ Stored {len(result['resume_ids'])} resumes and {len(result['job_ids'])} jobs")
        
        # Get statistics
        stats = storage.get_dataset_stats()
        print(f"✅ Dataset stats: {stats['total_resumes']} resumes, {stats['total_job_descriptions']} jobs")
        
        return True
    
    except Exception as e:
        print(f"❌ Data storage failed: {e}")
        return False

def test_resume_generation(sample_resume, sample_job):
    """Test resume generation"""
    print("\n🔄 Testing resume generation...")
    
    try:
        generator = ResumeGenerator()
        
        # Prepare base info from sample resume
        base_info = {
            "role": "software_engineer",
            "experience_level": ExperienceLevel.MID,
            "contact_info": sample_resume.contact_info.dict(),
            "skills": sample_resume.skills,
            "experience": [exp.dict() for exp in sample_resume.experience],
            "education": [edu.dict() for edu in sample_resume.education],
            "projects": [proj.dict() for proj in sample_resume.projects]
        }
        
        # Generate enhanced resume
        enhanced_resume, metadata = generator.generate_resume(
            base_info=base_info,
            target_job=sample_job,
            iterative_improvement=True
        )
        
        print(f"✅ Enhanced resume generated with {metadata['iterations']} improvement iterations")
        print(f"✅ ATS compliance score: {metadata['ats_compliance_score']:.2f}")
        
        return True, enhanced_resume
    
    except Exception as e:
        print(f"❌ Resume generation failed: {e}")
        return False, None

def test_resume_screening(resume, job):
    """Test resume screening"""
    print("\n🔄 Testing resume screening...")
    
    try:
        pipeline = ScreeningPipeline()
        
        # Screen resume against job
        result = pipeline.screen_resume(resume, job, explain=True)
        
        print(f"✅ Overall match score: {result.overall_score:.3f}")
        print(f"✅ Skill gaps identified: {len(result.skill_gaps)}")
        print(f"✅ Recommendations generated: {len(result.recommendations)}")
        
        # Print section scores
        for section, score in result.section_scores.items():
            print(f"  - {section}: {score.score:.3f}")
        
        return True, result
    
    except Exception as e:
        print(f"❌ Resume screening failed: {e}")
        return False, None

def test_evaluation_system():
    """Test evaluation system"""
    print("\n🔄 Testing evaluation system...")
    
    try:
        calculator = MetricsCalculator()
        
        # Run comprehensive evaluation
        eval_results = calculator.run_comprehensive_evaluation()
        
        print(f"✅ Evaluation completed in {eval_results['total_evaluation_time']:.2f}s")
        print(f"✅ Models evaluated: {len(eval_results['models_evaluated'])}")
        print(f"✅ Recommendations: {len(eval_results['recommendations'])}")
        
        return True
    
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return False

def test_api_imports():
    """Test API module imports"""
    print("\n🔄 Testing API imports...")
    
    try:
        from src.api.main import app
        from src.api.middleware import setup_middleware
        from src.api.session_manager import SessionManager
        
        print("✅ FastAPI app imported successfully")
        print("✅ Middleware imported successfully")
        print("✅ Session manager imported successfully")
        
        return True
    
    except Exception as e:
        print(f"❌ API imports failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Resume Intelligence System Tests\n")
    
    all_tests_passed = True
    
    # Test 1: Data Generation
    success, sample_resume, sample_job, dataset = test_data_generation()
    if not success:
        all_tests_passed = False
    
    # Test 2: Data Storage
    if success and dataset:
        success = test_data_storage(dataset)
        if not success:
            all_tests_passed = False
    
    # Test 3: Resume Generation
    if success and sample_resume and sample_job:
        success, enhanced_resume = test_resume_generation(sample_resume, sample_job)
        if not success:
            all_tests_passed = False
        else:
            sample_resume = enhanced_resume  # Use enhanced version for screening
    
    # Test 4: Resume Screening
    if success and sample_resume and sample_job:
        success, screening_result = test_resume_screening(sample_resume, sample_job)
        if not success:
            all_tests_passed = False
    
    # Test 5: Evaluation System
    success = test_evaluation_system()
    if not success:
        all_tests_passed = False
    
    # Test 6: API Imports
    success = test_api_imports()
    if not success:
        all_tests_passed = False
    
    # Final Results
    print("\n" + "="*50)
    if all_tests_passed:
        print("🎉 All tests passed! Resume Intelligence System is working correctly.")
        print("\nNext steps:")
        print("1. Run the API server: python -m uvicorn src.api.main:app --reload")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Test the endpoints using the interactive docs")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    print("="*50)

if __name__ == "__main__":
    main()