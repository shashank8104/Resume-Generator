from typing import Dict, Any, List

from ..models.resume_schema import Resume
from ..models.job_schema import JobDescription
from ..models.api_schema import ScreeningResult
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class ExplainerEngine:
    """Provide detailed explanations for ML model decisions"""
    
    def __init__(self, config=None):
        self.config = config or {}
        logger.info("Explainer engine initialized")
    
    def explain_screening_result(
        self, 
        resume: Resume, 
        job_description: JobDescription, 
        screening_result: ScreeningResult
    ) -> Dict[str, Any]:
        """Provide detailed explanation of screening results"""
        
        explanation = {
            "overall_assessment": self._generate_overall_assessment(screening_result),
            "strengths": self._identify_strengths(resume, job_description, screening_result),
            "weaknesses": self._identify_weaknesses(resume, job_description, screening_result),
            "improvement_suggestions": self._generate_improvement_suggestions(screening_result),
            "match_reasoning": self._explain_match_reasoning(screening_result),
            "section_analysis": self._analyze_sections(screening_result)
        }
        
        return explanation
    
    def _generate_overall_assessment(self, result: ScreeningResult) -> str:
        """Generate overall assessment text"""
        score = result.overall_score
        
        if score >= 0.8:
            return f"Excellent match ({score:.1%}) - This candidate demonstrates strong alignment with the job requirements across multiple areas."
        elif score >= 0.6:
            return f"Good match ({score:.1%}) - This candidate shows solid potential with some areas that could be strengthened."
        elif score >= 0.4:
            return f"Moderate match ({score:.1%}) - This candidate has some relevant qualifications but significant gaps exist."
        else:
            return f"Limited match ({score:.1%}) - This candidate requires substantial development to meet the role requirements."
    
    def _identify_strengths(self, resume: Resume, job_description: JobDescription, result: ScreeningResult) -> List[str]:
        """Identify candidate strengths based on screening results"""
        strengths = []
        
        # Analyze section scores to find strengths
        for section, score_obj in result.section_scores.items():
            if score_obj.score >= 0.7:
                strengths.append(f"Strong {section} alignment ({score_obj.score:.1%})")
                if score_obj.matched_keywords:
                    strengths.append(f"Demonstrated expertise in: {', '.join(score_obj.matched_keywords[:3])}")
        
        # Additional strengths based on resume content
        if len(resume.experience) >= 3:
            strengths.append("Substantial work experience with multiple roles")
        
        if any(edu.level.value in ['master', 'doctorate'] for edu in resume.education):
            strengths.append("Advanced education credentials")
        
        if len(resume.projects) >= 2:
            strengths.append("Strong project portfolio demonstrating practical skills")
        
        return strengths[:5]  # Limit to top 5 strengths
    
    def _identify_weaknesses(self, resume: Resume, job_description: JobDescription, result: ScreeningResult) -> List[str]:
        """Identify areas for improvement"""
        weaknesses = []
        
        # Analyze low-scoring sections
        for section, score_obj in result.section_scores.items():
            if score_obj.score < 0.5:
                weaknesses.append(f"Limited {section} alignment ({score_obj.score:.1%})")
                if score_obj.missing_keywords:
                    weaknesses.append(f"Missing key {section}: {', '.join(score_obj.missing_keywords[:3])}")
        
        # Skill gaps
        if result.skill_gaps:
            weaknesses.append(f"Critical skill gaps: {', '.join(result.skill_gaps[:3])}")
        
        # Experience gaps
        if len(resume.experience) < 2:
            weaknesses.append("Limited professional work experience")
        
        return weaknesses[:5]  # Limit to top 5 weaknesses
    
    def _generate_improvement_suggestions(self, result: ScreeningResult) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        # Use the recommendations from screening result
        suggestions.extend(result.recommendations[:3])
        
        # Add specific suggestions based on section scores
        for section, score_obj in result.section_scores.items():
            if score_obj.score < 0.6 and score_obj.missing_keywords:
                suggestions.append(
                    f"Strengthen {section} section by highlighting: {', '.join(score_obj.missing_keywords[:2])}"
                )
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _explain_match_reasoning(self, result: ScreeningResult) -> str:
        """Explain the reasoning behind the match score"""
        reasoning_parts = []
        
        # Explain based on section performances
        high_scoring_sections = [section for section, score in result.section_scores.items() if score.score >= 0.7]
        low_scoring_sections = [section for section, score in result.section_scores.items() if score.score < 0.5]
        
        if high_scoring_sections:
            reasoning_parts.append(f"Strong performance in {', '.join(high_scoring_sections)} contributed positively to the overall score.")
        
        if low_scoring_sections:
            reasoning_parts.append(f"Lower scores in {', '.join(low_scoring_sections)} reduced the overall match rating.")
        
        # Add context about scoring methodology
        reasoning_parts.append("The overall score represents a weighted combination of skills (35%), experience (25%), education (15%), projects (15%), and keyword matching (10%).")
        
        return " ".join(reasoning_parts)
    
    def _analyze_sections(self, result: ScreeningResult) -> Dict[str, Dict[str, Any]]:
        """Provide detailed analysis of each section"""
        section_analysis = {}
        
        for section, score_obj in result.section_scores.items():
            analysis = {
                "score": score_obj.score,
                "performance_level": self._get_performance_level(score_obj.score),
                "matched_items": len(score_obj.matched_keywords),
                "missing_items": len(score_obj.missing_keywords),
                "key_matches": score_obj.matched_keywords[:3],
                "key_gaps": score_obj.missing_keywords[:3],
                "feedback": score_obj.feedback,
                "recommendations": self._get_section_recommendations(section, score_obj)
            }
            section_analysis[section] = analysis
        
        return section_analysis
    
    def _get_performance_level(self, score: float) -> str:
        """Get performance level description for a score"""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _get_section_recommendations(self, section: str, score_obj) -> List[str]:
        """Get specific recommendations for a section"""
        recommendations = []
        
        if score_obj.score < 0.6:
            if section == "skills":
                recommendations.append("Consider adding more relevant technical skills to your resume")
                if score_obj.missing_keywords:
                    recommendations.append(f"Focus on developing: {', '.join(score_obj.missing_keywords[:2])}")
            elif section == "experience":
                recommendations.append("Enhance experience descriptions with more specific achievements")
                recommendations.append("Include quantifiable results and impact metrics")
            elif section == "projects":
                recommendations.append("Add more projects that demonstrate relevant skills")
                recommendations.append("Include project URLs and detailed descriptions")
            elif section == "education":
                recommendations.append("Highlight relevant coursework and academic projects")
                recommendations.append("Consider pursuing additional certifications")
        
        return recommendations[:2]  # Limit to 2 recommendations per section