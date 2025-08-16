"""
Skill Analyzer Agent for DevCareerCompass Phase 3.
Specializes in extracting and analyzing skills from various sources.
"""

from typing import Dict, Any, List, Optional
import json
import re

from src.agents.base_agent import BaseAgent
from src.llm.llm_client import BaseLLMClient
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class SkillAnalyzerAgent(BaseAgent):
    """Agent specialized in skill extraction and analysis."""
    
    def __init__(self, llm_client: BaseLLMClient, **kwargs):
        """
        Initialize the skill analyzer agent.
        
        Args:
            llm_client: LLM client for text generation
            **kwargs: Additional configuration
        """
        super().__init__("SkillAnalyzer", llm_client, **kwargs)
        
        # Skill categories and patterns
        self.skill_categories = {
            'programming_languages': [
                'python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'swift', 'kotlin',
                'typescript', 'php', 'ruby', 'scala', 'r', 'matlab', 'perl', 'bash', 'shell'
            ],
            'frameworks': [
                'react', 'vue', 'angular', 'django', 'flask', 'express', 'spring', 'laravel',
                'rails', 'asp.net', 'fastapi', 'gin', 'echo', 'fiber', 'actix', 'rocket'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
                'dynamodb', 'sqlite', 'oracle', 'sql server', 'neo4j', 'influxdb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'digitalocean', 'heroku', 'vercel', 'netlify',
                'firebase', 'supabase', 'railway', 'render'
            ],
            'devops_tools': [
                'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions', 'terraform',
                'ansible', 'prometheus', 'grafana', 'elk stack', 'splunk'
            ]
        }
    
    def get_capabilities(self) -> List[str]:
        """Get the agent's capabilities."""
        return [
            "Extract skills from commit messages",
            "Analyze repository languages and technologies",
            "Identify skill proficiency levels",
            "Categorize skills by domain",
            "Detect emerging technologies",
            "Assess skill market demand",
            "Generate skill recommendations"
        ]
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process skill analysis tasks.
        
        Args:
            task_data: Task data containing text, commits, repositories, etc.
            
        Returns:
            Skill analysis results
        """
        try:
            task_type = task_data.get('task_type', 'general_analysis')
            
            if task_type == 'commit_analysis':
                return await self._analyze_commits(task_data)
            elif task_type == 'repository_analysis':
                return await self._analyze_repository(task_data)
            elif task_type == 'profile_analysis':
                return await self._analyze_profile(task_data)
            elif task_type == 'skill_extraction':
                return await self._extract_skills(task_data)
            else:
                return await self._general_skill_analysis(task_data)
                
        except Exception as e:
            logger.error(f"Error processing task in SkillAnalyzerAgent: {e}")
            return {"error": str(e)}
    
    async def _analyze_commits(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skills from commit messages."""
        commits = task_data.get('commits', [])
        if not commits:
            return {"error": "No commits provided"}
        
        # Combine all commit messages
        all_messages = " ".join([commit.get('message', '') for commit in commits])
        
        # Extract skills using LLM
        skills_analysis = await self.analyze_with_llm(all_messages, 'skills')
        
        # Additional pattern-based extraction
        pattern_skills = self._extract_skills_by_patterns(all_messages)
        
        # Combine results
        combined_skills = self._combine_skill_results(skills_analysis, pattern_skills)
        
        return {
            'task_type': 'commit_analysis',
            'commits_analyzed': len(commits),
            'skills_found': combined_skills,
            'llm_analysis': skills_analysis,
            'pattern_analysis': pattern_skills
        }
    
    async def _analyze_repository(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skills from repository data."""
        repository = task_data.get('repository', {})
        if not repository:
            return {"error": "No repository data provided"}
        
        # Extract information from repository
        languages = repository.get('languages', {})
        topics = repository.get('topics', [])
        description = repository.get('description', '')
        readme = repository.get('readme', '')
        
        # Combine all text for analysis
        combined_text = f"{description} {' '.join(topics)} {readme}"
        
        # Analyze with LLM
        llm_analysis = await self.analyze_with_llm(combined_text, 'skills')
        
        # Analyze languages
        language_skills = self._analyze_languages(languages)
        
        # Analyze topics
        topic_skills = self._analyze_topics(topics)
        
        return {
            'task_type': 'repository_analysis',
            'repository_name': repository.get('name', ''),
            'languages_analysis': language_skills,
            'topics_analysis': topic_skills,
            'llm_analysis': llm_analysis,
            'combined_skills': self._combine_skill_results(llm_analysis, {
                'languages': language_skills,
                'topics': topic_skills
            })
        }
    
    async def _analyze_profile(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skills from developer profile."""
        profile = task_data.get('profile', {})
        if not profile:
            return {"error": "No profile data provided"}
        
        # Extract profile information
        bio = profile.get('bio', '')
        company = profile.get('company', '')
        location = profile.get('location', '')
        
        # Combine profile text
        profile_text = f"{bio} {company} {location}"
        
        # Analyze with LLM
        skills_analysis = await self.analyze_with_llm(profile_text, 'skills')
        interests_analysis = await self.analyze_with_llm(profile_text, 'interests')
        
        return {
            'task_type': 'profile_analysis',
            'profile_username': profile.get('username', ''),
            'skills_analysis': skills_analysis,
            'interests_analysis': interests_analysis,
            'combined_insights': {
                'skills': skills_analysis.get('skills', []),
                'interests': interests_analysis.get('interests', []),
                'focus_areas': interests_analysis.get('focus_areas', [])
            }
        }
    
    async def _extract_skills(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract skills from raw text."""
        text = task_data.get('text', '')
        if not text:
            return {"error": "No text provided"}
        
        # Use LLM for skill extraction
        skills_analysis = await self.analyze_with_llm(text, 'skills')
        
        # Use pattern matching as backup
        pattern_skills = self._extract_skills_by_patterns(text)
        
        return {
            'task_type': 'skill_extraction',
            'text_length': len(text),
            'llm_extraction': skills_analysis,
            'pattern_extraction': pattern_skills,
            'combined_skills': self._combine_skill_results(skills_analysis, pattern_skills)
        }
    
    async def _general_skill_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform general skill analysis."""
        text = task_data.get('text', '')
        
        # Multiple analysis types
        skills_analysis = await self.analyze_with_llm(text, 'skills')
        career_level = await self.analyze_with_llm(text, 'career_level')
        interests = await self.analyze_with_llm(text, 'interests')
        
        return {
            'task_type': 'general_analysis',
            'skills': skills_analysis,
            'career_level': career_level,
            'interests': interests,
            'summary': {
                'total_skills': len(skills_analysis.get('skills', [])),
                'career_stage': career_level.get('career_level', 'unknown'),
                'focus_areas': interests.get('focus_areas', [])
            }
        }
    
    def _extract_skills_by_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract skills using pattern matching."""
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills in self.skill_categories.items():
            category_skills = []
            for skill in skills:
                if skill.lower() in text_lower:
                    category_skills.append(skill)
            if category_skills:
                found_skills[category] = category_skills
        
        return found_skills
    
    def _analyze_languages(self, languages: Dict[str, int]) -> Dict[str, Any]:
        """Analyze programming languages from repository data."""
        if not languages:
            return {"languages": [], "primary_language": None, "language_count": 0}
        
        # Sort by usage
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "languages": [lang for lang, _ in sorted_languages],
            "primary_language": sorted_languages[0][0] if sorted_languages else None,
            "language_count": len(languages),
            "usage_stats": dict(sorted_languages)
        }
    
    def _analyze_topics(self, topics: List[str]) -> Dict[str, Any]:
        """Analyze repository topics."""
        if not topics:
            return {"topics": [], "topic_count": 0}
        
        # Categorize topics
        categorized_topics = {}
        for topic in topics:
            category = self._categorize_topic(topic)
            if category not in categorized_topics:
                categorized_topics[category] = []
            categorized_topics[category].append(topic)
        
        return {
            "topics": topics,
            "topic_count": len(topics),
            "categorized_topics": categorized_topics
        }
    
    def _categorize_topic(self, topic: str) -> str:
        """Categorize a topic based on its content."""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['api', 'rest', 'graphql']):
            return 'api'
        elif any(word in topic_lower for word in ['web', 'frontend', 'backend']):
            return 'web_development'
        elif any(word in topic_lower for word in ['ai', 'ml', 'machine-learning', 'deep-learning']):
            return 'ai_ml'
        elif any(word in topic_lower for word in ['mobile', 'ios', 'android']):
            return 'mobile'
        elif any(word in topic_lower for word in ['devops', 'ci', 'cd', 'deployment']):
            return 'devops'
        elif any(word in topic_lower for word in ['database', 'db', 'sql', 'nosql']):
            return 'database'
        else:
            return 'other'
    
    def _combine_skill_results(self, llm_results: Dict[str, Any], pattern_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine LLM and pattern-based skill extraction results."""
        combined = {
            'skills': [],
            'technologies': [],
            'tools': [],
            'categories': {}
        }
        
        # Add LLM results
        if isinstance(llm_results, dict):
            combined['skills'].extend(llm_results.get('skills', []))
            combined['technologies'].extend(llm_results.get('technologies', []))
            combined['tools'].extend(llm_results.get('tools', []))
        
        # Add pattern results
        if isinstance(pattern_results, dict):
            for category, skills in pattern_results.items():
                if category not in combined['categories']:
                    combined['categories'][category] = []
                combined['categories'][category].extend(skills)
                combined['skills'].extend(skills)
        
        # Remove duplicates
        combined['skills'] = list(set(combined['skills']))
        combined['technologies'] = list(set(combined['technologies']))
        combined['tools'] = list(set(combined['tools']))
        
        return combined 