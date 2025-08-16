"""
Agent Orchestrator for DevCareerCompass Phase 3.
Coordinates multiple agents to provide comprehensive career guidance.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.agents.base_agent import BaseAgent
from src.agents.skill_analyzer_agent import SkillAnalyzerAgent
from src.agents.career_advisor_agent import CareerAdvisorAgent
from src.llm.llm_client import BaseLLMClient
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple agents for comprehensive career guidance."""
    
    def __init__(self, llm_client: BaseLLMClient = None):
        """
        Initialize the agent orchestrator.
        
        Args:
            llm_client: LLM client for all agents
        """
        self.llm_client = llm_client
        self.agents = {}
        self.conversation_history = []
        self.workflow_results = {}
        
        logger.info("Agent orchestrator initialized")
    
    async def initialize(self):
        """Initialize the agent orchestrator and all agents."""
        try:
            # Initialize agents
            self._initialize_agents()
            logger.info("Agent orchestrator initialized with all agents")
            return True
        except Exception as e:
            logger.error(f"Error initializing agent orchestrator: {e}")
            return False
    
    def _initialize_agents(self):
        """Initialize all available agents."""
        try:
            # Skill Analyzer Agent
            self.agents['skill_analyzer'] = SkillAnalyzerAgent(self.llm_client)
            
            # Career Advisor Agent
            self.agents['career_advisor'] = CareerAdvisorAgent(self.llm_client)
            
            logger.info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Error initializing agents: {e}")
    
    async def process_comprehensive_analysis(self, developer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process comprehensive career analysis using multiple agents.
        
        Args:
            developer_data: Complete developer data including profile, repositories, commits, etc.
            
        Returns:
            Comprehensive analysis results
        """
        try:
            logger.info("Starting comprehensive career analysis")
            
            # Step 1: Skill Analysis
            skill_analysis = await self._analyze_skills(developer_data)
            
            # Step 2: Career Path Analysis
            career_analysis = await self._analyze_career_paths(developer_data, skill_analysis)
            
            # Step 3: Learning Path Generation
            learning_path = await self._generate_learning_path(developer_data, skill_analysis, career_analysis)
            
            # Step 4: Market Analysis
            market_analysis = await self._analyze_market_demand(developer_data, skill_analysis)
            
            # Step 5: Generate Final Recommendations
            final_recommendations = await self._generate_final_recommendations(
                developer_data, skill_analysis, career_analysis, learning_path, market_analysis
            )
            
            # Compile comprehensive results
            comprehensive_results = {
                'timestamp': datetime.now().isoformat(),
                'developer_info': {
                    'username': developer_data.get('username', ''),
                    'name': developer_data.get('name', ''),
                    'location': developer_data.get('location', ''),
                    'company': developer_data.get('company', ''),
                    'followers': developer_data.get('followers', 0),
                    'public_repos': developer_data.get('public_repos', 0)
                },
                'skill_analysis': skill_analysis,
                'career_analysis': career_analysis,
                'learning_path': learning_path,
                'market_analysis': market_analysis,
                'final_recommendations': final_recommendations,
                'summary': self._generate_summary(skill_analysis, career_analysis, learning_path, market_analysis)
            }
            
            # Store results
            self.workflow_results[developer_data.get('username', 'unknown')] = comprehensive_results
            
            logger.info("Comprehensive career analysis completed")
            return comprehensive_results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e)}
    
    async def _analyze_skills(self, developer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze developer skills using the skill analyzer agent."""
        try:
            skill_analyzer = self.agents['skill_analyzer']
            
            # Prepare task data for skill analysis
            task_data = {
                'task_type': 'comprehensive_skill_analysis',
                'profile': {
                    'username': developer_data.get('username', ''),
                    'bio': developer_data.get('bio', ''),
                    'company': developer_data.get('company', ''),
                    'location': developer_data.get('location', '')
                },
                'repositories': developer_data.get('repositories', []),
                'commits': developer_data.get('commits', []),
                'languages': developer_data.get('languages', {}),
                'topics': developer_data.get('topics', [])
            }
            
            # Process skill analysis
            skill_results = await skill_analyzer.process_task(task_data)
            
            # Additional LLM-based skill extraction
            if developer_data.get('bio'):
                bio_skills = await skill_analyzer.analyze_with_llm(developer_data['bio'], 'skills')
                skill_results['bio_analysis'] = bio_skills
            
            return skill_results
            
        except Exception as e:
            logger.error(f"Error in skill analysis: {e}")
            return {"error": str(e)}
    
    async def _analyze_career_paths(self, developer_data: Dict[str, Any], skill_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze career paths using the career advisor agent."""
        try:
            career_advisor = self.agents['career_advisor']
            
            # Extract skills from skill analysis
            skills = skill_analysis.get('skills', {}).get('skills', [])
            if not skills and 'combined_skills' in skill_analysis:
                skills = skill_analysis['combined_skills'].get('skills', [])
            
            # Prepare task data for career analysis
            task_data = {
                'task_type': 'career_path_recommendation',
                'skills': skills,
                'experience_level': developer_data.get('experience_level', 'mid'),
                'interests': developer_data.get('interests', []),
                'goals': developer_data.get('career_goals', []),
                'location': developer_data.get('location', 'global')
            }
            
            # Process career analysis
            career_results = await career_advisor.process_task(task_data)
            
            return career_results
            
        except Exception as e:
            logger.error(f"Error in career path analysis: {e}")
            return {"error": str(e)}
    
    async def _generate_learning_path(self, developer_data: Dict[str, Any], skill_analysis: Dict[str, Any], career_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate learning path using the career advisor agent."""
        try:
            career_advisor = self.agents['career_advisor']
            
            # Extract target skills from career analysis
            target_skills = []
            if 'recommended_paths' in career_analysis:
                for path in career_analysis['recommended_paths'][:2]:  # Top 2 paths
                    missing_skills = path.get('required_skills', [])
                    target_skills.extend(missing_skills[:3])  # Top 3 missing skills per path
            
            # Remove duplicates
            target_skills = list(set(target_skills))
            
            if not target_skills:
                target_skills = ['Python', 'JavaScript', 'React']  # Default skills
            
            # Prepare task data for learning path
            task_data = {
                'task_type': 'learning_path',
                'target_skills': target_skills,
                'current_level': developer_data.get('experience_level', 'intermediate'),
                'learning_style': developer_data.get('learning_style', 'practical'),
                'time_available': developer_data.get('time_available', 'part_time')
            }
            
            # Process learning path generation
            learning_results = await career_advisor.process_task(task_data)
            
            return learning_results
            
        except Exception as e:
            logger.error(f"Error in learning path generation: {e}")
            return {"error": str(e)}
    
    async def _analyze_market_demand(self, developer_data: Dict[str, Any], skill_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market demand using the career advisor agent."""
        try:
            career_advisor = self.agents['career_advisor']
            
            # Extract skills from skill analysis
            skills = skill_analysis.get('skills', {}).get('skills', [])
            if not skills and 'combined_skills' in skill_analysis:
                skills = skill_analysis['combined_skills'].get('skills', [])
            
            # Prepare task data for market analysis
            task_data = {
                'task_type': 'market_analysis',
                'skills': skills,
                'location': developer_data.get('location', 'global')
            }
            
            # Process market analysis
            market_results = await career_advisor.process_task(task_data)
            
            return market_results
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return {"error": str(e)}
    
    async def _generate_final_recommendations(self, developer_data: Dict[str, Any], skill_analysis: Dict[str, Any], 
                                           career_analysis: Dict[str, Any], learning_path: Dict[str, Any], 
                                           market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final comprehensive recommendations."""
        try:
            # Use the LLM client to generate final recommendations
            recommendations_prompt = f"""
            Based on the following comprehensive analysis, provide final career recommendations:
            
            Developer Profile: {developer_data.get('username', '')} - {developer_data.get('bio', '')}
            
            Skill Analysis: {json.dumps(skill_analysis, indent=2)}
            Career Analysis: {json.dumps(career_analysis, indent=2)}
            Learning Path: {json.dumps(learning_path, indent=2)}
            Market Analysis: {json.dumps(market_analysis, indent=2)}
            
            Provide structured recommendations covering:
            1. Immediate Actions (next 30 days)
            2. Short-term Goals (3-6 months)
            3. Medium-term Goals (6-12 months)
            4. Long-term Vision (1-2 years)
            5. Priority Skills to Develop
            6. Career Path Recommendations
            7. Learning Resources
            8. Networking Opportunities
            9. Potential Challenges and Solutions
            10. Success Metrics
            """
            
            final_recommendations = await self.llm_client.generate_text(
                recommendations_prompt,
                temperature=0.7,
                max_tokens=1500
            )
            
            return {
                'recommendations': final_recommendations,
                'priority_actions': self._extract_priority_actions(skill_analysis, career_analysis, learning_path),
                'success_metrics': self._generate_success_metrics(career_analysis, learning_path)
            }
            
        except Exception as e:
            logger.error(f"Error generating final recommendations: {e}")
            return {"error": str(e)}
    
    def _extract_priority_actions(self, skill_analysis: Dict[str, Any], career_analysis: Dict[str, Any], learning_path: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract priority actions from analysis results."""
        priority_actions = []
        
        # Add skill development actions
        if 'missing_skills' in career_analysis:
            for skill_gap in career_analysis['missing_skills'][:3]:  # Top 3 gaps
                priority_actions.append({
                    'action': f"Learn {skill_gap['skill']}",
                    'priority': skill_gap['priority'],
                    'timeline': skill_gap['estimated_learning_time'],
                    'type': 'skill_development'
                })
        
        # Add learning path actions
        if 'structured_phases' in learning_path:
            for phase in learning_path['structured_phases'][:2]:  # First 2 phases
                priority_actions.append({
                    'action': f"Complete {phase['skill']} learning phase",
                    'priority': 'high',
                    'timeline': phase['duration'],
                    'type': 'learning'
                })
        
        # Add career path actions
        if 'recommended_paths' in career_analysis:
            top_path = career_analysis['recommended_paths'][0]
            priority_actions.append({
                'action': f"Focus on {top_path['title']} career path",
                'priority': 'high',
                'timeline': '6-12 months',
                'type': 'career_planning'
            })
        
        return priority_actions
    
    def _generate_success_metrics(self, career_analysis: Dict[str, Any], learning_path: Dict[str, Any]) -> Dict[str, Any]:
        """Generate success metrics for tracking progress."""
        metrics = {
            'skill_development': {
                'target_skills_acquired': 0,
                'skill_proficiency_levels': {},
                'certifications_earned': 0
            },
            'career_progression': {
                'career_path_progress': 0.0,
                'salary_increase': 0,
                'role_advancement': False
            },
            'learning_progress': {
                'phases_completed': 0,
                'projects_finished': 0,
                'learning_hours': 0
            },
            'market_position': {
                'job_interviews': 0,
                'job_offers': 0,
                'network_connections': 0
            }
        }
        
        # Set targets based on analysis
        if 'recommended_paths' in career_analysis:
            metrics['career_progression']['career_path_progress'] = career_analysis['recommended_paths'][0].get('match_score', 0.0)
        
        if 'structured_phases' in learning_path:
            metrics['learning_progress']['phases_completed'] = len(learning_path['structured_phases'])
        
        return metrics
    
    def _generate_summary(self, skill_analysis: Dict[str, Any], career_analysis: Dict[str, Any], 
                         learning_path: Dict[str, Any], market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of all analysis results."""
        summary = {
            'total_skills_identified': 0,
            'top_career_paths': [],
            'learning_duration': '',
            'high_demand_skills': [],
            'key_insights': []
        }
        
        # Extract skills count
        if 'skills' in skill_analysis and 'skills' in skill_analysis['skills']:
            summary['total_skills_identified'] = len(skill_analysis['skills']['skills'])
        
        # Extract top career paths
        if 'recommended_paths' in career_analysis:
            summary['top_career_paths'] = [
                path['title'] for path in career_analysis['recommended_paths'][:3]
            ]
        
        # Extract learning duration
        if 'estimated_duration' in learning_path:
            summary['learning_duration'] = learning_path['estimated_duration']
        
        # Extract high demand skills
        if 'high_demand_skills' in market_analysis:
            summary['high_demand_skills'] = market_analysis['high_demand_skills']
        
        # Generate key insights
        insights = []
        if summary['total_skills_identified'] > 0:
            insights.append(f"Identified {summary['total_skills_identified']} skills")
        
        if summary['top_career_paths']:
            insights.append(f"Top career path: {summary['top_career_paths'][0]}")
        
        if summary['high_demand_skills']:
            insights.append(f"High demand skills: {', '.join(summary['high_demand_skills'][:3])}")
        
        summary['key_insights'] = insights
        
        return summary
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {}
        for agent_name, agent in self.agents.items():
            status[agent_name] = {
                'name': agent.name,
                'capabilities': agent.get_capabilities(),
                'conversation_count': len(agent.get_conversation_history()),
                'task_count': len(agent.get_task_results())
            }
        return status
    
    def get_workflow_history(self) -> Dict[str, Any]:
        """Get history of workflow executions."""
        return self.workflow_results
    
    def clear_history(self):
        """Clear all conversation and workflow history."""
        for agent in self.agents.values():
            agent.clear_history()
        self.workflow_results.clear()
        self.conversation_history.clear()
        logger.info("Cleared all agent and orchestrator history")


# Global agent orchestrator instance
agent_orchestrator = None 