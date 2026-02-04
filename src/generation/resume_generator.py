import random
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from ..models.resume_schema import Resume, ContactInfo, WorkExperience, Education, Project, ExperienceLevel
from ..models.job_schema import JobDescription, JobLevel
from ..utils.logging_utils import get_logger
from .template_selector import TemplateSelector
from .keyword_expander import KeywordExpander

logger = get_logger(__name__)

class ResumeGenerator:
    """
    Hybrid rule-based + ML resume generator with iterative improvement
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.template_selector = TemplateSelector()
        self.keyword_expander = KeywordExpander()
        
        # Load generation templates and rules
        self.bullet_point_templates = self._load_bullet_point_templates()
        self.summary_templates = self._load_summary_templates()
        self.ats_rules = self._load_ats_rules()
        
        logger.info("Resume generator initialized")
    
    def generate_resume(
        self,
        base_info: Dict[str, Any],
        target_job: Optional[JobDescription] = None,
        template_preference: Optional[str] = None,
        iterative_improvement: bool = True
    ) -> Tuple[Resume, Dict[str, Any]]:
        """
        Generate an ATS-friendly resume with optional iterative improvement
        
        Args:
            base_info: Basic information (experience, education, skills, etc.)
            target_job: Target job description for tailoring
            template_preference: Preferred template style
            iterative_improvement: Whether to apply iterative improvement loop
            
        Returns:
            Tuple of (generated_resume, generation_metadata)
        """
        logger.info("Starting resume generation process")
        
        # Select appropriate template
        template = self.template_selector.select_template(
            base_info.get("role", "software_engineer"),
            base_info.get("experience_level", ExperienceLevel.MID),
            template_preference
        )
        
        # Generate initial resume
        resume = self._generate_base_resume(base_info, template, target_job)
        
        # Track generation metadata
        metadata = {
            "template_used": template["name"],
            "generation_timestamp": datetime.now().isoformat(),
            "target_job_provided": target_job is not None,
            "iterations": 0,
            "improvements": []
        }
        
        # Apply iterative improvement if enabled and target job provided
        if iterative_improvement and target_job:
            resume, improvement_data = self._iterative_improvement(resume, target_job)
            metadata["iterations"] = improvement_data["iterations"]
            metadata["improvements"] = improvement_data["improvements"]
            metadata["final_match_score"] = improvement_data["final_score"]
        
        # Final ATS compliance check
        ats_score = self._check_ats_compliance(resume)
        metadata["ats_compliance_score"] = ats_score
        
        logger.info(f"Resume generation completed. ATS score: {ats_score:.2f}")
        
        return resume, metadata
    
    def _generate_base_resume(
        self,
        base_info: Dict[str, Any],
        template: Dict[str, Any],
        target_job: Optional[JobDescription]
    ) -> Resume:
        """Generate the base resume structure"""
        
        # Generate contact information
        contact_info = self._generate_contact_info(base_info)
        
        # Generate professional summary
        summary = self._generate_summary(base_info, template, target_job)
        
        # Process and expand skills
        skills = self._process_skills(base_info.get("skills", {}), target_job)
        
        # Generate work experience with enhanced bullet points
        experience = self._generate_experience(base_info.get("experience", []), target_job, template)
        
        # Process education
        education = self._process_education(base_info.get("education", []))
        
        # Generate or enhance projects
        projects = self._generate_projects(base_info.get("projects", []), target_job)
        
        # Generate additional sections
        certifications = base_info.get("certifications", [])
        languages = base_info.get("languages", ["English"])
        interests = base_info.get("interests", [])
        
        resume = Resume(
            contact_info=contact_info,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=certifications,
            languages=languages,
            interests=interests
        )
        
        return resume
    
    def _generate_contact_info(self, base_info: Dict[str, Any]) -> ContactInfo:
        """Generate contact information section"""
        contact_data = base_info.get("contact_info", {})
        
        return ContactInfo(
            full_name=contact_data.get("full_name", "John Doe"),
            email=contact_data.get("email", "john.doe@email.com"),
            phone=contact_data.get("phone"),
            location=contact_data.get("location", "San Francisco, CA"),
            linkedin=contact_data.get("linkedin"),
            github=contact_data.get("github"),
            website=contact_data.get("website")
        )
    
    def _generate_summary(
        self,
        base_info: Dict[str, Any],
        template: Dict[str, Any],
        target_job: Optional[JobDescription]
    ) -> str:
        """Generate professional summary"""
        
        role = base_info.get("role", "software_engineer")
        experience_level = base_info.get("experience_level", ExperienceLevel.MID)
        
        # Get base template
        summary_template = template.get("summary_template", 
            "Experienced {role} with {years} years of expertise in {key_skills}. "
            "Proven track record of {achievements} and {impact}."
        )
        
        # Extract key information
        years_exp = self._calculate_years_experience(base_info.get("experience", []))
        key_skills = self._extract_top_skills(base_info.get("skills", {}), target_job, 3)
        
        # Generate achievements and impact statements
        achievements = self._generate_achievement_statement(base_info, target_job)
        impact = self._generate_impact_statement(base_info, target_job)
        
        # Fill template
        summary = summary_template.format(
            role=role.replace("_", " ").title(),
            years=years_exp,
            key_skills=", ".join(key_skills),
            achievements=achievements,
            impact=impact
        )
        
        # Ensure ATS-friendly length (3-4 sentences, ~150-200 words)
        return self._optimize_summary_length(summary)
    
    def _process_skills(
        self,
        base_skills: Dict[str, List[str]],
        target_job: Optional[JobDescription]
    ) -> Dict[str, List[str]]:
        """Process and expand skills based on target job"""
        
        processed_skills = {}
        
        for category, skill_list in base_skills.items():
            # Expand skills using keyword expander
            if target_job:
                expanded_skills = self.keyword_expander.expand_skills(
                    skill_list, 
                    target_job.required_skills + target_job.preferred_skills
                )
            else:
                expanded_skills = skill_list
            
            # Remove duplicates and sort
            processed_skills[category] = sorted(list(set(expanded_skills)))
        
        # Add missing categories if found in target job
        if target_job:
            self._add_missing_skill_categories(processed_skills, target_job)
        
        return processed_skills
    
    def _generate_experience(
        self,
        base_experience: List[Dict[str, Any]],
        target_job: Optional[JobDescription],
        template: Dict[str, Any]
    ) -> List[WorkExperience]:
        """Generate enhanced work experience with better bullet points"""
        
        enhanced_experience = []
        
        for exp_data in base_experience:
            # Generate enhanced bullet points
            enhanced_bullets = self._enhance_bullet_points(
                exp_data.get("description", []),
                exp_data.get("skills", []),
                target_job,
                template
            )
            
            experience = WorkExperience(
                company=exp_data["company"],
                position=exp_data["position"],
                start_date=exp_data["start_date"],
                end_date=exp_data.get("end_date"),
                description=enhanced_bullets,
                skills=exp_data.get("skills", [])
            )
            
            enhanced_experience.append(experience)
        
        return enhanced_experience
    
    def _enhance_bullet_points(
        self,
        original_bullets: List[str],
        role_skills: List[str],
        target_job: Optional[JobDescription],
        template: Dict[str, Any]
    ) -> List[str]:
        """Enhance bullet points with quantified achievements"""
        
        enhanced_bullets = []
        
        for bullet in original_bullets:
            # Apply enhancement rules
            enhanced_bullet = self._apply_bullet_point_rules(bullet, role_skills, target_job)
            enhanced_bullets.append(enhanced_bullet)
        
        # Generate additional bullets if needed
        min_bullets = self.config.get("min_bullets_per_role", 3)
        max_bullets = self.config.get("max_bullets_per_role", 5)
        
        while len(enhanced_bullets) < min_bullets:
            additional_bullet = self._generate_additional_bullet(role_skills, target_job, template)
            enhanced_bullets.append(additional_bullet)
        
        # Ensure we don't exceed maximum
        return enhanced_bullets[:max_bullets]
    
    def _apply_bullet_point_rules(
        self,
        bullet: str,
        skills: List[str],
        target_job: Optional[JobDescription]
    ) -> str:
        """Apply rules to improve bullet points"""
        
        enhanced = bullet
        
        # Rule 1: Start with action verbs
        enhanced = self._ensure_action_verb_start(enhanced)
        
        # Rule 2: Add quantification if missing
        enhanced = self._add_quantification(enhanced)
        
        # Rule 3: Include relevant skills
        enhanced = self._incorporate_relevant_skills(enhanced, skills, target_job)
        
        # Rule 4: Optimize for ATS keywords
        enhanced = self._optimize_for_ats_keywords(enhanced, target_job)
        
        return enhanced
    
    def _generate_projects(
        self,
        base_projects: List[Dict[str, Any]],
        target_job: Optional[JobDescription]
    ) -> List[Project]:
        """Generate or enhance project descriptions"""
        
        enhanced_projects = []
        
        for proj_data in base_projects:
            # Enhance project description with target job keywords
            enhanced_description = self._enhance_project_description(
                proj_data.get("description", ""),
                proj_data.get("technologies", []),
                target_job
            )
            
            # Enhance achievements
            enhanced_achievements = self._enhance_project_achievements(
                proj_data.get("achievements", []),
                target_job
            )
            
            project = Project(
                name=proj_data["name"],
                description=enhanced_description,
                technologies=proj_data.get("technologies", []),
                start_date=proj_data.get("start_date"),
                end_date=proj_data.get("end_date"),
                url=proj_data.get("url"),
                achievements=enhanced_achievements
            )
            
            enhanced_projects.append(project)
        
        return enhanced_projects
    
    def _iterative_improvement(
        self,
        resume: Resume,
        target_job: JobDescription,
        max_iterations: int = 3
    ) -> Tuple[Resume, Dict[str, Any]]:
        """Apply iterative improvement to increase job match score"""
        logger.info("Starting iterative improvement process")
        
        improvement_data = {
            "iterations": 0,
            "improvements": [],
            "scores": [],
            "final_score": 0.0
        }
        
        current_resume = resume
        min_score_threshold = self.config.get("min_match_threshold", 0.65)
        
        for iteration in range(max_iterations):
            # Score current resume against job
            match_score = self._score_resume_job_match(current_resume, target_job)
            improvement_data["scores"].append(match_score)
            
            logger.info(f"Iteration {iteration + 1}: Match score = {match_score:.3f}")
            
            # Check if we've reached the threshold
            if match_score >= min_score_threshold:
                logger.info(f"Reached target score threshold: {match_score:.3f}")
                break
            
            # Apply improvements
            improved_resume, improvements = self._apply_targeted_improvements(
                current_resume, target_job, match_score
            )
            
            improvement_data["improvements"].extend(improvements)
            improvement_data["iterations"] += 1
            current_resume = improved_resume
        
        # Final score
        final_score = self._score_resume_job_match(current_resume, target_job)
        improvement_data["final_score"] = final_score
        
        logger.info(f"Iterative improvement completed. Final score: {final_score:.3f}")
        
        return current_resume, improvement_data
    
    def _score_resume_job_match(self, resume: Resume, job: JobDescription) -> float:
        """Score how well resume matches job description (simplified version)"""
        # This is a simplified scoring - full implementation would be in screening module
        
        total_score = 0.0
        weights = {"skills": 0.4, "experience": 0.3, "keywords": 0.3}
        
        # Skills match
        resume_skills = [skill for skills in resume.skills.values() for skill in skills]
        required_skills = job.required_skills + job.preferred_skills
        skill_matches = len(set(resume_skills) & set(required_skills))
        skills_score = skill_matches / max(len(required_skills), 1)
        total_score += weights["skills"] * skills_score
        
        # Experience relevance (simplified)
        exp_score = min(len(resume.experience) / 3.0, 1.0)  # Assume 3 roles is ideal
        total_score += weights["experience"] * exp_score
        
        # Keyword presence (simplified)
        resume_text = f"{resume.summary} {' '.join([exp.description for exp in resume.experience])}"
        job_text = f"{job.description} {' '.join(job.requirements)}"
        
        # Simple keyword overlap
        resume_words = set(resume_text.lower().split())
        job_words = set(job_text.lower().split())
        keyword_overlap = len(resume_words & job_words) / max(len(job_words), 1)
        total_score += weights["keywords"] * keyword_overlap
        
        return min(total_score, 1.0)
    
    def _apply_targeted_improvements(
        self,
        resume: Resume,
        target_job: JobDescription,
        current_score: float
    ) -> Tuple[Resume, List[str]]:
        """Apply targeted improvements to increase match score"""
        
        improvements = []
        updated_resume = resume.copy(deep=True)
        
        # Improvement 1: Add missing critical skills
        missing_skills = self._identify_missing_skills(resume, target_job)
        if missing_skills:
            self._add_skills_to_resume(updated_resume, missing_skills)
            improvements.append(f"Added {len(missing_skills)} missing critical skills")
        
        # Improvement 2: Enhance bullet points with job keywords
        keyword_improvements = self._enhance_bullets_with_job_keywords(updated_resume, target_job)
        if keyword_improvements > 0:
            improvements.append(f"Enhanced {keyword_improvements} bullet points with job keywords")
        
        # Improvement 3: Optimize summary for job match
        if self._optimize_summary_for_job(updated_resume, target_job):
            improvements.append("Optimized professional summary for better job match")
        
        return updated_resume, improvements
    
    def _check_ats_compliance(self, resume: Resume) -> float:
        """Check resume compliance with ATS best practices"""
        
        score = 0.0
        total_checks = len(self.ats_rules)
        
        for rule in self.ats_rules:
            if self._apply_ats_rule(resume, rule):
                score += 1.0
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _apply_ats_rule(self, resume: Resume, rule: Dict[str, Any]) -> bool:
        """Apply individual ATS compliance rule"""
        
        rule_type = rule.get("type")
        
        if rule_type == "length_check":
            # Check section lengths
            if rule.get("section") == "summary":
                return 100 <= len(resume.summary or "") <= 300
            
        elif rule_type == "format_check":
            # Check formatting rules
            if rule.get("check") == "phone_format":
                return self._validate_phone_format(resume.contact_info.phone)
            elif rule.get("check") == "email_format":
                return "@" in resume.contact_info.email and "." in resume.contact_info.email
        
        elif rule_type == "content_check":
            # Check content requirements
            if rule.get("check") == "has_quantified_achievements":
                return self._has_quantified_achievements(resume)
        
        return True  # Default pass for unknown rules
    
    def _load_bullet_point_templates(self) -> Dict[str, List[str]]:
        """Load bullet point templates for different achievement types"""
        return {
            "performance_improvement": [
                "Improved {metric} by {percentage}% through {method}",
                "Optimized {process} resulting in {percentage}% reduction in {metric}",
                "Enhanced {system} performance, achieving {percentage}% faster {outcome}"
            ],
            "team_leadership": [
                "Led team of {number} {role} to deliver {project} on time and under budget",
                "Mentored {number} junior developers, improving team productivity by {percentage}%",
                "Managed cross-functional team of {number} members across {departments}"
            ],
            "technical_achievement": [
                "Architected and implemented {technology} solution handling {scale} {unit}",
                "Developed {system} using {technologies} serving {number} users",
                "Built scalable {application} processing {volume} {metric} daily"
            ],
            "business_impact": [
                "Generated ${amount} in revenue through {initiative}",
                "Reduced operational costs by ${amount} by implementing {solution}",
                "Increased customer satisfaction by {percentage}% via {improvement}"
            ]
        }
    
    def _load_summary_templates(self) -> Dict[str, str]:
        """Load professional summary templates by role"""
        return {
            "software_engineer": (
                "Results-driven Software Engineer with {years}+ years of experience developing "
                "scalable applications using {technologies}. Proven expertise in {specializations} "
                "with a track record of {achievements}. Passionate about {interests} and committed "
                "to delivering high-quality solutions."
            ),
            "data_scientist": (
                "Data-driven Data Scientist with {years}+ years of experience leveraging {tools} "
                "to extract actionable insights from complex datasets. Expertise in {techniques} "
                "with proven success in {applications}. Strong background in {domains} and "
                "passionate about using data to drive business decisions."
            ),
            "marketing_manager": (
                "Strategic Marketing Manager with {years}+ years of experience developing and "
                "executing comprehensive marketing campaigns. Proven track record in {channels} "
                "with expertise in {specializations}. Successfully {achievements} and passionate "
                "about driving growth through data-driven marketing strategies."
            )
        }
    
    def _load_ats_rules(self) -> List[Dict[str, Any]]:
        """Load ATS compliance rules"""
        return [
            {"type": "length_check", "section": "summary", "min": 100, "max": 300},
            {"type": "format_check", "check": "phone_format"},
            {"type": "format_check", "check": "email_format"},
            {"type": "content_check", "check": "has_quantified_achievements"},
            {"type": "content_check", "check": "uses_action_verbs"},
            {"type": "content_check", "check": "includes_relevant_keywords"},
            {"type": "format_check", "check": "consistent_date_format"},
            {"type": "length_check", "section": "bullet_points", "min": 20, "max": 100}
        ]
    
    # Helper methods (simplified implementations)
    def _calculate_years_experience(self, experience: List[Dict[str, Any]]) -> str:
        """Calculate total years of experience"""
        if not experience:
            return "2"
        
        # Simplified calculation
        return str(min(len(experience) * 2, 10))
    
    def _extract_top_skills(
        self, 
        skills: Dict[str, List[str]], 
        target_job: Optional[JobDescription], 
        count: int
    ) -> List[str]:
        """Extract top skills for summary"""
        all_skills = [skill for skill_list in skills.values() for skill in skill_list]
        
        if target_job:
            # Prioritize skills that match job requirements
            job_skills = set(target_job.required_skills + target_job.preferred_skills)
            matching_skills = [skill for skill in all_skills if skill in job_skills]
            return matching_skills[:count] if matching_skills else all_skills[:count]
        
        return all_skills[:count]
    
    def _generate_achievement_statement(
        self, 
        base_info: Dict[str, Any], 
        target_job: Optional[JobDescription]
    ) -> str:
        """Generate achievement statement for summary"""
        achievements = [
            "delivering high-quality software solutions",
            "leading cross-functional teams",
            "implementing scalable architectures",
            "optimizing system performance",
            "driving technical innovation"
        ]
        return random.choice(achievements)
    
    def _generate_impact_statement(
        self, 
        base_info: Dict[str, Any], 
        target_job: Optional[JobDescription]
    ) -> str:
        """Generate impact statement for summary"""
        impacts = [
            "measurable business results",
            "improved operational efficiency",
            "enhanced user experience",
            "increased system reliability",
            "accelerated product development"
        ]
        return random.choice(impacts)
    
    def _optimize_summary_length(self, summary: str, target_length: int = 200) -> str:
        """Optimize summary length for ATS compliance"""
        if len(summary) <= target_length:
            return summary
        
        # Simple truncation - in production, use more sophisticated methods
        sentences = summary.split('. ')
        optimized = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) + 1 <= target_length:
                optimized.append(sentence)
                current_length += len(sentence) + 1
            else:
                break
        
        return '. '.join(optimized) + '.'
    
    def _add_missing_skill_categories(
        self, 
        skills: Dict[str, List[str]], 
        target_job: JobDescription
    ):
        """Add missing skill categories based on job requirements"""
        # Simplified implementation
        if "tools" not in skills and any("docker" in skill.lower() for skill in target_job.required_skills):
            skills["tools"] = ["Docker", "Git"]
    
    def _ensure_action_verb_start(self, bullet: str) -> str:
        """Ensure bullet point starts with strong action verb"""
        action_verbs = [
            "Developed", "Implemented", "Led", "Managed", "Optimized", "Designed",
            "Built", "Created", "Improved", "Enhanced", "Delivered", "Achieved"
        ]
        
        if not any(bullet.startswith(verb) for verb in action_verbs):
            return f"Developed {bullet.lower()}"
        
        return bullet
    
    def _add_quantification(self, bullet: str) -> str:
        """Add quantification to bullet points if missing"""
        if any(char.isdigit() or char == '%' for char in bullet):
            return bullet  # Already has numbers
        
        # Add generic quantification
        quantifiers = ["20%", "3", "50%", "10+", "25%"]
        quantifier = random.choice(quantifiers)
        
        if "improved" in bullet.lower() or "increased" in bullet.lower():
            return bullet.replace("improved", f"improved by {quantifier}").replace("increased", f"increased by {quantifier}")
        
        return bullet
    
    def _incorporate_relevant_skills(
        self, 
        bullet: str, 
        skills: List[str], 
        target_job: Optional[JobDescription]
    ) -> str:
        """Incorporate relevant skills into bullet points"""
        if target_job:
            relevant_skills = set(skills) & set(target_job.required_skills + target_job.preferred_skills)
            if relevant_skills:
                skill = random.choice(list(relevant_skills))
                if skill.lower() not in bullet.lower():
                    return f"{bullet} using {skill}"
        
        return bullet
    
    def _optimize_for_ats_keywords(self, bullet: str, target_job: Optional[JobDescription]) -> str:
        """Optimize bullet points for ATS keywords"""
        # Simplified implementation
        return bullet
    
    def _enhance_project_description(
        self, 
        description: str, 
        technologies: List[str], 
        target_job: Optional[JobDescription]
    ) -> str:
        """Enhance project description with target job alignment"""
        if not description:
            return f"Developed comprehensive solution using {', '.join(technologies[:3])}"
        
        # Add target job technologies if relevant
        if target_job:
            relevant_techs = set(technologies) & set(target_job.required_skills)
            if relevant_techs:
                tech_list = ", ".join(list(relevant_techs)[:2])
                return f"{description} Implemented using {tech_list} to ensure scalability and performance."
        
        return description
    
    def _enhance_project_achievements(
        self, 
        achievements: List[str], 
        target_job: Optional[JobDescription]
    ) -> List[str]:
        """Enhance project achievements"""
        if not achievements:
            return [
                "Improved system performance by 25%",
                "Reduced deployment time by 40%"
            ]
        return achievements
    
    def _identify_missing_skills(self, resume: Resume, target_job: JobDescription) -> List[str]:
        """Identify critical missing skills"""
        resume_skills = {skill.lower() for skills in resume.skills.values() for skill in skills}
        required_skills = {skill.lower() for skill in target_job.required_skills}
        
        return [skill for skill in target_job.required_skills 
                if skill.lower() not in resume_skills][:3]  # Top 3 missing
    
    def _add_skills_to_resume(self, resume: Resume, skills: List[str]):
        """Add missing skills to appropriate categories"""
        if "technical" not in resume.skills:
            resume.skills["technical"] = []
        
        for skill in skills:
            if skill not in resume.skills["technical"]:
                resume.skills["technical"].append(skill)
    
    def _enhance_bullets_with_job_keywords(self, resume: Resume, target_job: JobDescription) -> int:
        """Enhance bullet points with job description keywords"""
        improvements = 0
        
        job_keywords = set(word.lower() for word in 
                          " ".join(target_job.requirements + target_job.responsibilities).split())
        
        for exp in resume.experience:
            for i, bullet in enumerate(exp.description):
                # Simple keyword enhancement
                if "developed" in bullet.lower() and "scalable" not in bullet.lower():
                    if "scalable" in job_keywords:
                        exp.description[i] = bullet.replace("developed", "developed scalable")
                        improvements += 1
        
        return improvements
    
    def _optimize_summary_for_job(self, resume: Resume, target_job: JobDescription) -> bool:
        """Optimize summary for better job matching"""
        if not resume.summary:
            return False
        
        # Add key job requirements to summary if missing
        key_requirements = target_job.required_skills[:2]
        for req in key_requirements:
            if req.lower() not in resume.summary.lower():
                resume.summary = f"{resume.summary.rstrip('.')} with expertise in {req}."
                return True
        
        return False
    
    def _validate_phone_format(self, phone: Optional[str]) -> bool:
        """Validate phone number format"""
        if not phone:
            return True  # Optional field
        
        # Simple validation
        return "+" in phone and len(phone.replace("+", "").replace("-", "")) >= 10
    
    def _has_quantified_achievements(self, resume: Resume) -> bool:
        """Check if resume has quantified achievements"""
        all_bullets = [bullet for exp in resume.experience for bullet in exp.description]
        
        return any(any(char.isdigit() or char == "%" for char in bullet) for bullet in all_bullets)
    
    def _generate_additional_bullet(
        self, 
        skills: List[str], 
        target_job: Optional[JobDescription],
        template: Dict[str, Any]
    ) -> str:
        """Generate additional bullet point when needed"""
        templates = [
            f"Collaborated with cross-functional teams to deliver {random.choice(['projects', 'solutions', 'features'])}",
            f"Implemented {random.choice(skills[:2])} solutions improving system reliability by 20%",
            f"Participated in code reviews and mentored junior team members"
        ]
        
        return random.choice(templates)
    
    def _process_education(self, base_education: List[Dict[str, Any]]) -> List[Education]:
        """Process education information"""
        processed_education = []
        
        for edu_data in base_education:
            education = Education(
                institution=edu_data["institution"],
                degree=edu_data["degree"],
                level=edu_data["level"],
                major=edu_data.get("major"),
                graduation_date=edu_data.get("graduation_date"),
                gpa=edu_data.get("gpa"),
                relevant_courses=edu_data.get("relevant_courses", [])
            )
            processed_education.append(education)
        
        return processed_education