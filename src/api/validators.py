from typing import Dict, Any, List, Optional
from pydantic import ValidationError

from ..models.resume_schema import Resume
from ..models.job_schema import JobDescription
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

def validate_resume_data(resume_data: Dict[str, Any]) -> tuple:
    """Validate resume data and return validation result"""
    try:
        resume = Resume(**resume_data)
        return True, resume, None
    except ValidationError as e:
        logger.warning(f"Resume validation failed: {e}")
        return False, None, str(e)
    except Exception as e:
        logger.error(f"Unexpected error in resume validation: {e}")
        return False, None, f"Validation error: {str(e)}"

def validate_job_data(job_data: Dict[str, Any]) -> tuple:
    """Validate job description data and return validation result"""
    try:
        job_description = JobDescription(**job_data)
        return True, job_description, None
    except ValidationError as e:
        logger.warning(f"Job description validation failed: {e}")
        return False, None, str(e)
    except Exception as e:
        logger.error(f"Unexpected error in job validation: {e}")
        return False, None, f"Validation error: {str(e)}"

def validate_batch_data(data_list: List[Dict[str, Any]], data_type: str) -> tuple:
    """Validate batch data and return validation results"""
    validated_items = []
    errors = []
    
    for i, item_data in enumerate(data_list):
        try:
            if data_type == "resume":
                item = Resume(**item_data)
            elif data_type == "job":
                item = JobDescription(**item_data)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            validated_items.append(item)
            
        except ValidationError as e:
            error_msg = f"Item {i}: {str(e)}"
            errors.append(error_msg)
            logger.warning(f"Batch validation failed for item {i}: {e}")
        except Exception as e:
            error_msg = f"Item {i}: Validation error: {str(e)}"
            errors.append(error_msg)
            logger.error(f"Unexpected error in batch validation for item {i}: {e}")
    
    success = len(validated_items) > 0
    return success, validated_items, errors