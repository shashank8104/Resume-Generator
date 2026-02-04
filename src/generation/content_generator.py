from typing import Dict, Any, Optional
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class ContentGenerator:
    """Generate professional content like emails and cover letters"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.templates = self._load_templates()
        
    def generate_email(self, target_role: str, company_name: str, tone: str = "professional", context: Optional[str] = None) -> str:
        """Generate professional email"""
        template = self.templates["email"][tone]
        
        return template.format(
            role=target_role,
            company=company_name,
            context=context or "your recent job posting"
        )
    
    def generate_cover_letter(self, target_role: str, company_name: str, tone: str = "professional", context: Optional[str] = None) -> str:
        """Generate cover letter"""
        template = self.templates["cover_letter"][tone]
        
        return template.format(
            role=target_role,
            company=company_name,
            context=context or "this exciting opportunity"
        )
    
    def generate_linkedin_prompt(self, target_role: str, company_name: str, context: Optional[str] = None) -> str:
        """Generate LinkedIn outreach message"""
        template = self.templates["linkedin"]
        
        return template.format(
            role=target_role,
            company=company_name,
            context=context or "your company's innovative work"
        )
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load content templates"""
        return {
            "email": {
                "professional": "Subject: Application for {role} Position\n\nDear Hiring Manager,\n\nI am writing to express my interest in the {role} position at {company}. I noticed {context} and believe my skills align well with your requirements.\n\nI would welcome the opportunity to discuss how I can contribute to your team.\n\nBest regards,\n[Your Name]",
                "friendly": "Hi there!\n\nI hope this email finds you well. I'm excited about the {role} opportunity at {company} and would love to learn more about {context}.\n\nI'd be thrilled to chat about how I can help your team succeed!\n\nCheers,\n[Your Name]",
                "formal": "Dear Sir/Madam,\n\nI am formally applying for the {role} position at {company}. Having reviewed {context}, I am confident in my ability to contribute meaningfully to your organization.\n\nI look forward to your consideration.\n\nSincerely,\n[Your Name]"
            },
            "cover_letter": {
                "professional": "Dear Hiring Manager,\n\nI am writing to apply for the {role} position at {company}. With my background in technology and passion for innovation, I am excited about {context}.\n\nThroughout my career, I have developed strong skills in software development, problem-solving, and team collaboration. I am particularly drawn to {company}'s mission and would be honored to contribute to your success.\n\nI have attached my resume for your review and would welcome the opportunity to discuss my qualifications further.\n\nThank you for your consideration.\n\nSincerely,\n[Your Name]",
                "friendly": "Hello!\n\nI'm thrilled to apply for the {role} role at {company}! Your team's work on {context} really resonates with me, and I'd love to be part of it.\n\nI bring a combination of technical skills and creative problem-solving that I think would be a great fit for your team. I'm excited about the possibility of contributing to your innovative projects.\n\nI'd love to chat more about how I can help {company} achieve its goals!\n\nBest,\n[Your Name]",
                "formal": "To Whom It May Concern,\n\nI hereby submit my application for the position of {role} at {company}. After careful consideration of {context}, I believe my qualifications align with your requirements.\n\nMy professional experience and technical competencies position me well to contribute to your organization's objectives. I would be honored to discuss my candidacy in detail.\n\nI thank you for your time and consideration.\n\nRespectfully,\n[Your Name]"
            },
            "linkedin": "Hi [Name],\n\nI noticed you work at {company} and I'm really impressed by {context}. I'm currently exploring opportunities in {role} and would love to learn more about the culture and challenges at {company}.\n\nWould you be open to a brief chat about your experience there?\n\nThanks!\n[Your Name]"
        }