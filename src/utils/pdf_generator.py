"""PDF generation utilities for resume exports"""

import io
from typing import Dict, Any
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import black, darkblue, grey
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class PDFGenerator:
    """Generate PDF resumes from resume data"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Name style (large, bold)
        self.styles.add(ParagraphStyle(
            name='Name',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=darkblue
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='Contact',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            textColor=darkblue,
            borderWidth=1,
            borderColor=grey,
            borderPadding=2
        ))
        
        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=6,
            spaceAfter=2,
            fontName='Helvetica-Bold'
        ))
        
        # Company style
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            textColor=grey
        ))
    
    def generate_resume_pdf(self, resume_data: Dict[str, Any]) -> bytes:
        """Generate a PDF resume from resume data"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, 
                                  topMargin=72, bottomMargin=18)
            
            # Build the document content
            story = []
            
            # Header with name and contact info
            self._add_header(story, resume_data.get('contact_info', {}))
            
            # Professional summary
            if resume_data.get('summary'):
                self._add_section(story, 'Professional Summary', resume_data['summary'])
            
            # Skills
            if resume_data.get('skills'):
                self._add_skills_section(story, resume_data['skills'])
            
            # Experience
            if resume_data.get('experience'):
                self._add_experience_section(story, resume_data['experience'])
            
            # Education
            if resume_data.get('education'):
                self._add_education_section(story, resume_data['education'])
            
            # Build PDF
            doc.build(story)
            
            # Get the value of the BytesIO buffer
            pdf_data = buffer.getvalue()
            buffer.close()
            
            logger.info("PDF resume generated successfully")
            return pdf_data
            
        except Exception as e:
            logger.error(f"Error generating PDF resume: {str(e)}")
            raise
    
    def _add_header(self, story, contact_info):
        """Add header with name and contact information"""
        if contact_info.get('full_name'):
            story.append(Paragraph(contact_info['full_name'], self.styles['Name']))
        
        # Contact details
        contact_parts = []
        if contact_info.get('email'):
            contact_parts.append(contact_info['email'])
        if contact_info.get('phone'):
            contact_parts.append(contact_info['phone'])
        if contact_info.get('location'):
            contact_parts.append(contact_info['location'])
        
        if contact_parts:
            contact_text = ' • '.join(contact_parts)
            story.append(Paragraph(contact_text, self.styles['Contact']))
        
        story.append(Spacer(1, 12))
    
    def _add_section(self, story, title, content):
        """Add a section with title and content"""
        story.append(Paragraph(title.upper(), self.styles['SectionHeading']))
        story.append(Paragraph(content, self.styles['Normal']))
        story.append(Spacer(1, 12))
    
    def _add_skills_section(self, story, skills):
        """Add skills section"""
        story.append(Paragraph('SKILLS', self.styles['SectionHeading']))
        
        for category, skill_list in skills.items():
            if isinstance(skill_list, list):
                skills_text = f"<b>{category.title()}:</b> {', '.join(skill_list)}"
                story.append(Paragraph(skills_text, self.styles['Normal']))
        
        story.append(Spacer(1, 12))
    
    def _add_experience_section(self, story, experience):
        """Add work experience section"""
        story.append(Paragraph('PROFESSIONAL EXPERIENCE', self.styles['SectionHeading']))
        
        for job in experience:
            # Job title and company
            title_text = f"{job.get('position', '')} at {job.get('company', '')}"
            story.append(Paragraph(title_text, self.styles['JobTitle']))
            
            # Dates
            start_date = job.get('start_date', '')
            end_date = job.get('end_date', 'Present')
            date_text = f"{start_date} - {end_date}"
            story.append(Paragraph(date_text, self.styles['Company']))
            
            # Job descriptions
            if job.get('description'):
                descriptions = job['description']
                if isinstance(descriptions, list):
                    for desc in descriptions:
                        story.append(Paragraph(f"• {desc}", self.styles['Normal']))
                else:
                    story.append(Paragraph(f"• {descriptions}", self.styles['Normal']))
            
            story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 4))
    
    def _add_education_section(self, story, education):
        """Add education section"""
        story.append(Paragraph('EDUCATION', self.styles['SectionHeading']))
        
        for edu in education:
            # Degree and institution
            edu_text = f"<b>{edu.get('degree', '')}</b>"
            if edu.get('institution'):
                edu_text += f" - {edu['institution']}"
            if edu.get('graduation_date'):
                edu_text += f" ({edu['graduation_date']})"
            
            story.append(Paragraph(edu_text, self.styles['Normal']))
            
            if edu.get('gpa'):
                story.append(Paragraph(f"GPA: {edu['gpa']}", self.styles['Normal']))
        
        story.append(Spacer(1, 12))

def generate_resume_pdf(resume_data: Dict[str, Any]) -> bytes:
    """Convenience function to generate PDF resume"""
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")
    
    generator = PDFGenerator()
    return generator.generate_resume_pdf(resume_data)