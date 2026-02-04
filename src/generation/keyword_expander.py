from typing import List, Dict, Set
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class KeywordExpander:
    """Expand keywords using similarity-based matching"""
    
    def __init__(self):
        self.skill_synonyms = self._load_skill_synonyms()
        
    def expand_skills(self, base_skills: List[str], target_skills: List[str]) -> List[str]:
        """Expand skills list based on target requirements"""
        expanded_skills = base_skills.copy()
        
        for target_skill in target_skills:
            if target_skill not in base_skills:
                # Find similar skills
                similar_skills = self._find_similar_skills(target_skill, base_skills)
                if similar_skills:
                    expanded_skills.append(target_skill)
                    
        return list(set(expanded_skills))
    
    def _find_similar_skills(self, target: str, available: List[str]) -> List[str]:
        """Find similar skills using synonym matching"""
        target_lower = target.lower()
        similar = []
        
        for skill in available:
            if self._are_similar_skills(target_lower, skill.lower()):
                similar.append(skill)
                
        return similar
    
    def _are_similar_skills(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are similar"""
        # Direct match
        if skill1 == skill2:
            return True
            
        # Check synonyms
        synonyms1 = self.skill_synonyms.get(skill1, set())
        synonyms2 = self.skill_synonyms.get(skill2, set())
        
        return bool(synonyms1 & synonyms2) or skill2 in synonyms1 or skill1 in synonyms2
    
    def _load_skill_synonyms(self) -> Dict[str, Set[str]]:
        """Load skill synonyms dictionary"""
        return {
            'python': {'py', 'python3', 'python programming'},
            'javascript': {'js', 'node.js', 'nodejs', 'ecmascript'},
            'react': {'reactjs', 'react.js', 'react framework'},
            'machine learning': {'ml', 'artificial intelligence', 'ai', 'data science'},
            'aws': {'amazon web services', 'amazon aws', 'cloud computing'},
            'docker': {'containerization', 'containers', 'docker containers'}
        }