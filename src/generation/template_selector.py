from typing import Dict, Any, Optional
from ..models.resume_schema import ExperienceLevel
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class TemplateSelector:
    """Select appropriate resume templates based on role and experience level"""
    
    def __init__(self):
        self.templates = self._load_templates()
        
    def select_template(self, role: str, experience_level: ExperienceLevel, preference: Optional[str] = None) -> Dict[str, Any]:
        """Select the best template for given parameters"""
        
        # Get role-specific templates
        role_templates = self.templates.get(role, self.templates["default"])
        
        # Select based on experience level
        template_key = f"{experience_level.value}_level"
        if template_key in role_templates:
            selected_template = role_templates[template_key]
        else:
            selected_template = role_templates["default"]
            
        selected_template["name"] = f"{role}_{experience_level.value}"
        return selected_template
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load resume templates"""
        return {
            "software_engineer": {
                "entry_level": {
                    "summary_template": "Motivated {role} with {years} years of experience...",
                    "focus_areas": ["technical_skills", "projects", "education"]
                },
                "mid_level": {
                    "summary_template": "Experienced {role} with {years} years of expertise...",
                    "focus_areas": ["technical_skills", "experience", "projects"]
                },
                "default": {
                    "summary_template": "Professional {role} with {years} years of experience...",
                    "focus_areas": ["experience", "technical_skills", "leadership"]
                }
            },
            "default": {
                "default": {
                    "summary_template": "Experienced professional with {years} years in {role}...",
                    "focus_areas": ["experience", "skills", "achievements"]
                }
            }
        }