"""
Career Advisor Agent for DevCareerCompass Phase 3.
Provides personalized career guidance and recommendations.
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.llm.llm_client import BaseLLMClient
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class CareerAdvisorAgent(BaseAgent):
    """Agent specialized in career guidance and recommendations."""
    
    def __init__(self, llm_client: BaseLLMClient, **kwargs):
        """
        Initialize the career advisor agent.
        
        Args:
            llm_client: LLM client for text generation
            **kwargs: Additional configuration
        """
        super().__init__("CareerAdvisor", llm_client, **kwargs)
        
        # Career paths and their requirements
        self.career_paths = {
            'full_stack_developer': {
                'title': 'Full-Stack Developer',
                'description': 'Develop both frontend and backend applications',
                'required_skills': ['JavaScript', 'Python', 'React', 'Node.js', 'SQL'],
                'recommended_skills': ['TypeScript', 'Docker', 'AWS', 'GraphQL'],
                'salary_range': '$70,000 - $150,000',
                'growth_potential': 'High'
            },
            'data_scientist': {
                'title': 'Data Scientist',
                'description': 'Analyze data and build machine learning models',
                'required_skills': ['Python', 'R', 'SQL', 'Machine Learning', 'Statistics'],
                'recommended_skills': ['TensorFlow', 'PyTorch', 'Spark', 'Tableau'],
                'salary_range': '$80,000 - $160,000',
                'growth_potential': 'Very High'
            },
            'devops_engineer': {
                'title': 'DevOps Engineer',
                'description': 'Automate deployment and infrastructure management',
                'required_skills': ['Docker', 'Kubernetes', 'AWS', 'Linux', 'CI/CD'],
                'recommended_skills': ['Terraform', 'Ansible', 'Prometheus', 'Jenkins'],
                'salary_range': '$75,000 - $140,000',
                'growth_potential': 'High'
            },
            'mobile_developer': {
                'title': 'Mobile Developer',
                'description': 'Develop mobile applications for iOS and Android',
                'required_skills': ['Swift', 'Kotlin', 'React Native', 'Flutter'],
                'recommended_skills': ['iOS/Android', 'Firebase', 'App Store', 'UI/UX'],
                'salary_range': '$65,000 - $130,000',
                'growth_potential': 'Medium'
            },
            'backend_developer': {
                'title': 'Backend Developer',
                'description': 'Develop server-side applications and APIs',
                'required_skills': ['Java', 'Python', 'Node.js', 'SQL', 'Microservices'],
                'recommended_skills': ['Spring', 'Django', 'Express', 'PostgreSQL'],
                'salary_range': '$70,000 - $140,000',
                'growth_potential': 'High'
            },
            'frontend_developer': {
                'title': 'Frontend Developer',
                'description': 'Develop user interfaces and client-side applications',
                'required_skills': ['JavaScript', 'React', 'Vue.js', 'CSS', 'HTML'],
                'recommended_skills': ['TypeScript', 'Next.js', 'Tailwind CSS', 'Webpack'],
                'salary_range': '$60,000 - $120,000',
                'growth_potential': 'Medium'
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Get the agent's capabilities."""
        return [
            "Analyze career progression",
            "Recommend career paths",
            "Identify skill gaps",
            "Suggest learning paths",
            "Provide salary insights",
            "Assess market demand",
            "Generate personalized recommendations",
            "Create career development plans"
        ]
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process career advisory tasks.
        
        Args:
            task_data: Task data containing developer profile, skills, goals, etc.
            
        Returns:
            Career advisory results
        """
        try:
            task_type = task_data.get('task_type', 'general_advice')
            
            if task_type == 'career_path_recommendation':
                return await self._recommend_career_paths(task_data)
            elif task_type == 'skill_gap_analysis':
                return await self._analyze_skill_gaps(task_data)
            elif task_type == 'learning_path':
                return await self._create_learning_path(task_data)
            elif task_type == 'career_planning':
                return await self._create_career_plan(task_data)
            elif task_type == 'market_analysis':
                return await self._analyze_market_demand(task_data)
            else:
                return await self._provide_general_advice(task_data)
                
        except Exception as e:
            logger.error(f"Error processing task in CareerAdvisorAgent: {e}")
            return {"error": str(e)}
    
    async def _recommend_career_paths(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend career paths based on developer profile."""
        developer_skills = task_data.get('skills', [])
        experience_level = task_data.get('experience_level', 'mid')
        interests = task_data.get('interests', [])
        
        # Analyze current skills and interests
        skills_text = f"Skills: {', '.join(developer_skills)}. Interests: {', '.join(interests)}. Experience: {experience_level}"
        
        # Get LLM analysis
        career_analysis = await self.analyze_with_llm(skills_text, 'career_level')
        
        # Calculate career path matches
        path_matches = []
        for path_id, path_info in self.career_paths.items():
            match_score = self._calculate_career_path_match(
                developer_skills, path_info['required_skills'], path_info['recommended_skills']
            )
            
            if match_score > 0.3:  # Only include relevant paths
                path_matches.append({
                    'path_id': path_id,
                    'title': path_info['title'],
                    'description': path_info['description'],
                    'match_score': match_score,
                    'required_skills': path_info['required_skills'],
                    'recommended_skills': path_info['recommended_skills'],
                    'salary_range': path_info['salary_range'],
                    'growth_potential': path_info['growth_potential']
                })
        
        # Sort by match score
        path_matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return {
            'task_type': 'career_path_recommendation',
            'career_level_analysis': career_analysis,
            'recommended_paths': path_matches[:3],  # Top 3 recommendations
            'total_paths_analyzed': len(self.career_paths),
            'current_skills_count': len(developer_skills)
        }
    
    async def _analyze_skill_gaps(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skill gaps for career advancement."""
        current_skills = task_data.get('skills', [])
        target_role = task_data.get('target_role', '')
        experience_level = task_data.get('experience_level', 'mid')
        
        # Find target career path
        target_path = None
        for path_id, path_info in self.career_paths.items():
            if target_role.lower() in path_info['title'].lower():
                target_path = path_info
                break
        
        if not target_path:
            return {"error": f"Target role '{target_role}' not found"}
        
        # Identify missing skills
        required_skills = set(target_path['required_skills'])
        recommended_skills = set(target_path['recommended_skills'])
        current_skills_set = set(current_skills)
        
        missing_required = required_skills - current_skills_set
        missing_recommended = recommended_skills - current_skills_set
        
        # Prioritize skills based on importance and market demand
        prioritized_gaps = []
        
        for skill in missing_required:
            prioritized_gaps.append({
                'skill': skill,
                'priority': 'high',
                'type': 'required',
                'estimated_learning_time': '2-4 months'
            })
        
        for skill in missing_recommended:
            prioritized_gaps.append({
                'skill': skill,
                'priority': 'medium',
                'type': 'recommended',
                'estimated_learning_time': '1-3 months'
            })
        
        return {
            'task_type': 'skill_gap_analysis',
            'target_role': target_path['title'],
            'current_skills': list(current_skills_set),
            'missing_skills': prioritized_gaps,
            'skill_coverage': len(current_skills_set & required_skills) / len(required_skills),
            'total_gaps': len(prioritized_gaps)
        }
    
    async def _create_learning_path(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a personalized learning path."""
        target_skills = task_data.get('target_skills', [])
        current_level = task_data.get('current_level', 'intermediate')
        learning_style = task_data.get('learning_style', 'practical')
        time_available = task_data.get('time_available', 'part_time')
        
        # Create learning path using LLM
        learning_prompt = f"""
        Create a personalized learning path for a {current_level} level developer who wants to learn: {', '.join(target_skills)}.
        Learning style: {learning_style}
        Time available: {time_available}
        
        Provide a structured learning plan with:
        1. Prerequisites
        2. Learning phases
        3. Resources (courses, books, projects)
        4. Timeline
        5. Milestones
        """
        
        learning_plan = await self.generate_response(learning_prompt, temperature=0.7)
        
        # Generate structured learning phases
        learning_phases = []
        for i, skill in enumerate(target_skills):
            phase = {
                'phase': i + 1,
                'skill': skill,
                'duration': '4-6 weeks',
                'focus_areas': self._get_skill_focus_areas(skill),
                'projects': self._get_skill_projects(skill),
                'resources': self._get_skill_resources(skill)
            }
            learning_phases.append(phase)
        
        return {
            'task_type': 'learning_path',
            'target_skills': target_skills,
            'learning_plan': learning_plan,
            'structured_phases': learning_phases,
            'estimated_duration': f"{len(target_skills) * 5} weeks",
            'learning_style': learning_style
        }
    
    async def _create_career_plan(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive career development plan."""
        developer_profile = task_data.get('profile', {})
        current_skills = task_data.get('skills', [])
        career_goals = task_data.get('goals', [])
        timeline = task_data.get('timeline', '1-2 years')
        
        # Analyze current situation
        profile_text = f"Profile: {developer_profile.get('bio', '')} Skills: {', '.join(current_skills)} Goals: {', '.join(career_goals)}"
        career_analysis = await self.analyze_with_llm(profile_text, 'career_level')
        
        # Create career plan using LLM
        plan_prompt = f"""
        Create a comprehensive career development plan for a developer with:
        Current skills: {', '.join(current_skills)}
        Career goals: {', '.join(career_goals)}
        Timeline: {timeline}
        
        Include:
        1. Short-term goals (3-6 months)
        2. Medium-term goals (6-12 months)
        3. Long-term goals (1-2 years)
        4. Action items for each goal
        5. Success metrics
        6. Potential challenges and solutions
        """
        
        career_plan = await self.generate_response(plan_prompt, temperature=0.7)
        
        return {
            'task_type': 'career_planning',
            'career_analysis': career_analysis,
            'career_plan': career_plan,
            'timeline': timeline,
            'goals_count': len(career_goals),
            'current_skills_count': len(current_skills)
        }
    
    async def _analyze_market_demand(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market demand for skills and roles."""
        skills = task_data.get('skills', [])
        location = task_data.get('location', 'global')
        
        # Create market analysis prompt
        market_prompt = f"""
        Analyze the current market demand for these skills: {', '.join(skills)}
        Location focus: {location}
        
        Provide insights on:
        1. High-demand skills
        2. Salary trends
        3. Job market outlook
        4. Emerging technologies
        5. Industry trends
        """
        
        market_analysis = await self.generate_response(market_prompt, temperature=0.6)
        
        # Generate market demand scores
        demand_scores = {}
        for skill in skills:
            # Mock demand scoring (in real implementation, this would use market data)
            demand_scores[skill] = {
                'demand_level': 'high' if skill.lower() in ['python', 'javascript', 'react', 'aws'] else 'medium',
                'salary_impact': '+15%' if skill.lower() in ['python', 'aws', 'kubernetes'] else '+5%',
                'growth_trend': 'increasing' if skill.lower() in ['python', 'react', 'ai'] else 'stable'
            }
        
        return {
            'task_type': 'market_analysis',
            'location': location,
            'skills_analyzed': skills,
            'market_analysis': market_analysis,
            'demand_scores': demand_scores,
            'high_demand_skills': [skill for skill, data in demand_scores.items() if data['demand_level'] == 'high']
        }
    
    async def _provide_general_advice(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general career advice."""
        developer_info = task_data.get('developer_info', {})
        questions = task_data.get('questions', [])
        
        # Create advice prompt
        advice_prompt = f"""
        Provide career advice for a developer with the following profile:
        {json.dumps(developer_info, indent=2)}
        
        Questions/concerns: {', '.join(questions)}
        
        Provide comprehensive advice covering:
        1. Career direction
        2. Skill development
        3. Industry insights
        4. Personal growth
        5. Next steps
        """
        
        general_advice = await self.generate_response(advice_prompt, temperature=0.7)
        
        return {
            'task_type': 'general_advice',
            'advice': general_advice,
            'questions_addressed': len(questions),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_career_path_match(self, current_skills: List[str], required_skills: List[str], recommended_skills: List[str]) -> float:
        """Calculate match score for a career path."""
        current_skills_set = set(current_skills)
        required_skills_set = set(required_skills)
        recommended_skills_set = set(recommended_skills)
        
        # Calculate required skills match (weighted higher)
        required_match = len(current_skills_set & required_skills_set) / len(required_skills_set) if required_skills_set else 0
        
        # Calculate recommended skills match
        recommended_match = len(current_skills_set & recommended_skills_set) / len(recommended_skills_set) if recommended_skills_set else 0
        
        # Weighted score: 70% required, 30% recommended
        total_score = (required_match * 0.7) + (recommended_match * 0.3)
        
        return round(total_score, 3)
    
    def _get_skill_focus_areas(self, skill: str) -> List[str]:
        """Get focus areas for learning a specific skill."""
        focus_areas = {
            'python': ['Core Python', 'Data Structures', 'OOP', 'Libraries', 'Frameworks'],
            'javascript': ['ES6+', 'DOM Manipulation', 'Async Programming', 'Frameworks', 'Node.js'],
            'react': ['Components', 'Hooks', 'State Management', 'Routing', 'Testing'],
            'aws': ['EC2', 'S3', 'Lambda', 'RDS', 'CloudFormation'],
            'docker': ['Containers', 'Images', 'Dockerfile', 'Docker Compose', 'Orchestration']
        }
        
        return focus_areas.get(skill.lower(), ['Fundamentals', 'Advanced Concepts', 'Best Practices', 'Real-world Projects'])
    
    def _get_skill_projects(self, skill: str) -> List[str]:
        """Get project ideas for learning a specific skill."""
        projects = {
            'python': ['Web Scraper', 'API Development', 'Data Analysis Tool', 'Automation Script'],
            'javascript': ['Todo App', 'Weather App', 'E-commerce Site', 'Real-time Chat'],
            'react': ['Portfolio Website', 'Task Manager', 'Social Media Clone', 'Dashboard'],
            'aws': ['Static Website', 'Serverless API', 'Data Pipeline', 'Monitoring System'],
            'docker': ['Multi-container App', 'CI/CD Pipeline', 'Microservices', 'Development Environment']
        }
        
        return projects.get(skill.lower(), ['Basic Project', 'Intermediate Project', 'Advanced Project'])
    
    def _get_skill_resources(self, skill: str) -> Dict[str, List[str]]:
        """Get learning resources for a specific skill."""
        resources = {
            'python': {
                'courses': ['Python for Everybody', 'Complete Python Bootcamp'],
                'books': ['Python Crash Course', 'Fluent Python'],
                'platforms': ['Coursera', 'Udemy', 'freeCodeCamp']
            },
            'javascript': {
                'courses': ['JavaScript: The Complete Guide', 'Modern JavaScript'],
                'books': ['Eloquent JavaScript', 'You Don\'t Know JS'],
                'platforms': ['freeCodeCamp', 'The Odin Project', 'MDN Web Docs']
            },
            'react': {
                'courses': ['React - The Complete Guide', 'Modern React with Redux'],
                'books': ['Learning React', 'React Design Patterns'],
                'platforms': ['React Documentation', 'Egghead.io', 'Frontend Masters']
            }
        }
        
        return resources.get(skill.lower(), {
            'courses': ['Online Course'],
            'books': ['Technical Book'],
            'platforms': ['Learning Platform']
        }) 