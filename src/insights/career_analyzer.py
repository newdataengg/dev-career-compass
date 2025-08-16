"""
Career Analyzer for DevCareerCompass Phase 2.
Provides career insights and recommendations based on the knowledge graph.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import networkx as nx

from src.database.models import Developer, Repository, Skill, DeveloperSkill
from src.knowledge_graph.graph_builder import knowledge_graph_builder
from src.embeddings.embedding_generator import embedding_generator
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class CareerAnalyzer:
    """Analyzes career patterns and provides insights."""
    
    def __init__(self):
        """Initialize the career analyzer."""
        self.graph = None
        self._insights_cache = {}
    
    async def initialize(self):
        """Initialize the career analyzer."""
        logger.info("Career analyzer initialized")
        return True
    
    def set_graph(self, graph: nx.MultiDiGraph):
        """Set the knowledge graph for analysis."""
        self.graph = graph
        self._insights_cache.clear()
    
    def analyze_developer_profile(self, developer_id: int) -> Dict[str, Any]:
        """
        Analyze a developer's profile and provide comprehensive insights.
        
        Args:
            developer_id: ID of the developer to analyze
            
        Returns:
            Dictionary containing career insights
        """
        try:
            if not self.graph:
                logger.error("No knowledge graph set for analysis")
                return {}
            
            developer_node = f"developer_{developer_id}"
            if developer_node not in self.graph.nodes:
                logger.error(f"Developer {developer_id} not found in graph")
                return {}
            
            # Get developer data
            dev_data = self.graph.nodes[developer_node]
            
            # Get developer's skills
            skills = self._get_developer_skills(developer_id)
            
            # Get developer's repositories
            repositories = self._get_developer_repositories(developer_id)
            
            # Generate insights
            insights = {
                'developer_info': {
                    'id': developer_id,
                    'username': dev_data['username'],
                    'name': dev_data['name'],
                    'bio': dev_data['bio'],
                    'location': dev_data['location'],
                    'company': dev_data['company'],
                    'followers': dev_data['followers'],
                    'public_repos': dev_data['public_repos']
                },
                'skill_analysis': self._analyze_skills(skills),
                'repository_analysis': self._analyze_repositories(repositories),
                'career_recommendations': self._generate_career_recommendations(developer_id, skills, repositories),
                'market_insights': self._analyze_market_position(developer_id, skills),
                'growth_opportunities': self._identify_growth_opportunities(developer_id, skills)
            }
            
            # Cache the insights
            self._insights_cache[developer_id] = insights
            
            logger.info(f"Generated career insights for developer {developer_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing developer profile {developer_id}: {e}")
            return {}
    
    def _get_developer_skills(self, developer_id: int) -> List[Dict[str, Any]]:
        """Get skills for a developer with detailed information."""
        try:
            developer_node = f"developer_{developer_id}"
            skills = []
            
            for neighbor in self.graph.neighbors(developer_node):
                if self.graph.nodes[neighbor]['type'] == 'skill':
                    edge_data = self.graph.get_edge_data(developer_node, neighbor)
                    for edge_key, edge_attrs in edge_data.items():
                        if edge_attrs['type'] == 'has_skill':
                            skill_data = self.graph.nodes[neighbor]
                            skills.append({
                                'skill_id': skill_data['id'],
                                'skill_name': skill_data['name'],
                                'category': skill_data['category'],
                                'description': skill_data['description'],
                                'proficiency_level': edge_attrs['proficiency_level'],
                                'usage_frequency': edge_attrs['usage_frequency'],
                                'weight': edge_attrs['weight'],
                                'popularity_score': skill_data.get('popularity_score', 0),
                                'market_demand_score': skill_data.get('market_demand_score', 0)
                            })
                            break
            
            return skills
            
        except Exception as e:
            logger.error(f"Error getting developer skills: {e}")
            return []
    
    def _get_developer_repositories(self, developer_id: int) -> List[Dict[str, Any]]:
        """Get repositories for a developer."""
        try:
            developer_node = f"developer_{developer_id}"
            repositories = []
            
            for neighbor in self.graph.neighbors(developer_node):
                if self.graph.nodes[neighbor]['type'] == 'repository':
                    edge_data = self.graph.get_edge_data(developer_node, neighbor)
                    for edge_key, edge_attrs in edge_data.items():
                        if edge_attrs['type'] == 'owns_repository':
                            repo_data = self.graph.nodes[neighbor]
                            repositories.append({
                                'repository_id': repo_data['id'],
                                'name': repo_data['name'],
                                'full_name': repo_data['full_name'],
                                'description': repo_data['description'],
                                'language': repo_data['language'],
                                'languages': repo_data.get('languages', {}),
                                'topics': repo_data.get('topics', []),
                                'stargazers_count': repo_data['stargazers_count'],
                                'forks_count': repo_data['forks_count'],
                                'weight': edge_attrs['weight'],
                                'is_fork': edge_attrs['is_fork'],
                                'is_private': edge_attrs['is_private']
                            })
                            break
            
            return repositories
            
        except Exception as e:
            logger.error(f"Error getting developer repositories: {e}")
            return []
    
    def _analyze_skills(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze developer's skills."""
        try:
            if not skills:
                return {'message': 'No skills found'}
            
            # Skill categories
            categories = {}
            for skill in skills:
                category = skill['category'] or 'uncategorized'
                if category not in categories:
                    categories[category] = []
                categories[category].append(skill)
            
            # Proficiency distribution
            proficiency_levels = {}
            for skill in skills:
                level = skill['proficiency_level']
                proficiency_levels[level] = proficiency_levels.get(level, 0) + 1
            
            # Top skills by weight
            top_skills = sorted(skills, key=lambda x: x['weight'], reverse=True)[:5]
            
            # Market demand analysis
            high_demand_skills = [s for s in skills if s.get('market_demand_score', 0) > 7.0]
            popular_skills = [s for s in skills if s.get('popularity_score', 0) > 7.0]
            
            return {
                'total_skills': len(skills),
                'categories': categories,
                'proficiency_distribution': proficiency_levels,
                'top_skills': top_skills,
                'high_demand_skills': high_demand_skills,
                'popular_skills': popular_skills,
                'average_proficiency': np.mean([self._proficiency_to_numeric(s['proficiency_level']) for s in skills]),
                'skill_diversity_score': len(categories) / max(len(skills), 1)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing skills: {e}")
            return {}
    
    def _analyze_repositories(self, repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze developer's repositories."""
        try:
            if not repositories:
                return {'message': 'No repositories found'}
            
            # Repository metrics
            total_stars = sum(r['stargazers_count'] for r in repositories)
            total_forks = sum(r['forks_count'] for r in repositories)
            public_repos = [r for r in repositories if not r['is_private']]
            original_repos = [r for r in repositories if not r['is_fork']]
            
            # Language distribution
            languages = {}
            for repo in repositories:
                if repo['language']:
                    languages[repo['language']] = languages.get(repo['language'], 0) + 1
            
            # Top repositories
            top_repos = sorted(repositories, key=lambda x: x['stargazers_count'], reverse=True)[:5]
            
            return {
                'total_repositories': len(repositories),
                'public_repositories': len(public_repos),
                'original_repositories': len(original_repos),
                'total_stars': total_stars,
                'total_forks': total_forks,
                'average_stars': total_stars / len(repositories) if repositories else 0,
                'languages': languages,
                'top_repositories': top_repos,
                'repository_impact_score': self._calculate_repository_impact(repositories)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing repositories: {e}")
            return {}
    
    def _generate_career_recommendations(self, developer_id: int, skills: List[Dict[str, Any]], repositories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate career recommendations for the developer."""
        try:
            recommendations = []
            
            # Skill gap analysis
            skill_gaps = self._identify_skill_gaps(developer_id, skills)
            if skill_gaps:
                recommendations.append({
                    'type': 'skill_gap',
                    'title': 'Develop Missing Skills',
                    'description': 'Consider learning these high-demand skills to expand your career opportunities',
                    'items': skill_gaps,
                    'priority': 'high'
                })
            
            # Career path suggestions
            career_paths = self._suggest_career_paths(developer_id, skills)
            if career_paths:
                recommendations.append({
                    'type': 'career_path',
                    'title': 'Career Path Opportunities',
                    'description': 'Based on your current skills, consider these career directions',
                    'items': career_paths,
                    'priority': 'medium'
                })
            
            # Repository improvement suggestions
            repo_improvements = self._suggest_repository_improvements(repositories)
            if repo_improvements:
                recommendations.append({
                    'type': 'repository',
                    'title': 'Repository Enhancement',
                    'description': 'Ways to improve your repository visibility and impact',
                    'items': repo_improvements,
                    'priority': 'medium'
                })
            
            # Networking opportunities
            networking = self._suggest_networking_opportunities(developer_id, skills)
            if networking:
                recommendations.append({
                    'type': 'networking',
                    'title': 'Networking Opportunities',
                    'description': 'Connect with developers who share similar interests',
                    'items': networking,
                    'priority': 'low'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating career recommendations: {e}")
            return []
    
    def _analyze_market_position(self, developer_id: int, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze developer's position in the market."""
        try:
            if not skills:
                return {'message': 'No skills to analyze'}
            
            # Calculate market demand score
            demand_scores = [s.get('market_demand_score', 0) for s in skills]
            avg_demand = np.mean(demand_scores) if demand_scores else 0
            
            # Calculate popularity score
            popularity_scores = [s.get('popularity_score', 0) for s in skills]
            avg_popularity = np.mean(popularity_scores) if popularity_scores else 0
            
            # Market positioning
            if avg_demand > 7.0 and avg_popularity > 7.0:
                position = "High-Demand Specialist"
            elif avg_demand > 7.0:
                position = "Emerging Specialist"
            elif avg_popularity > 7.0:
                position = "Popular Generalist"
            else:
                position = "Generalist"
            
            return {
                'market_position': position,
                'average_demand_score': avg_demand,
                'average_popularity_score': avg_popularity,
                'demand_trend': self._analyze_demand_trend(skills),
                'competitive_advantage': self._identify_competitive_advantage(skills)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market position: {e}")
            return {}
    
    def _identify_growth_opportunities(self, developer_id: int, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify growth opportunities for the developer."""
        try:
            opportunities = []
            
            # Skill advancement opportunities
            for skill in skills:
                if skill['proficiency_level'] in ['beginner', 'intermediate']:
                    opportunities.append({
                        'type': 'skill_advancement',
                        'skill_name': skill['skill_name'],
                        'current_level': skill['proficiency_level'],
                        'next_level': self._get_next_proficiency_level(skill['proficiency_level']),
                        'description': f"Advance your {skill['skill_name']} skills from {skill['proficiency_level']} to {self._get_next_proficiency_level(skill['proficiency_level'])}"
                    })
            
            # New skill opportunities
            similar_skills = self._find_related_skills(developer_id, skills)
            for skill in similar_skills[:3]:  # Top 3 recommendations
                opportunities.append({
                    'type': 'new_skill',
                    'skill_name': skill['skill_name'],
                    'category': skill['category'],
                    'similarity_score': skill['similarity_score'],
                    'description': f"Learn {skill['skill_name']} which is similar to your existing skills"
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error identifying growth opportunities: {e}")
            return []
    
    def _identify_skill_gaps(self, developer_id: int, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify skill gaps for the developer."""
        try:
            # Get all skills in the graph
            all_skills = []
            for node, attrs in self.graph.nodes(data=True):
                if attrs.get('type') == 'skill':
                    all_skills.append(attrs)
            
            # Find high-demand skills the developer doesn't have
            developer_skill_names = {s['skill_name'] for s in skills}
            gaps = []
            
            for skill in all_skills:
                if (skill['name'] not in developer_skill_names and 
                    skill.get('market_demand_score', 0) > 7.0):
                    gaps.append({
                        'skill_name': skill['name'],
                        'category': skill['category'],
                        'market_demand_score': skill['market_demand_score'],
                        'description': skill.get('description', '')
                    })
            
            # Sort by market demand and return top 5
            gaps.sort(key=lambda x: x['market_demand_score'], reverse=True)
            return gaps[:5]
            
        except Exception as e:
            logger.error(f"Error identifying skill gaps: {e}")
            return []
    
    def _suggest_career_paths(self, developer_id: int, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest career paths based on current skills."""
        try:
            # Define career paths and their required skills
            career_paths = {
                'Full-Stack Developer': ['JavaScript', 'Python', 'React', 'Node.js', 'SQL'],
                'Data Scientist': ['Python', 'R', 'SQL', 'Machine Learning', 'Statistics'],
                'DevOps Engineer': ['Docker', 'Kubernetes', 'AWS', 'Linux', 'CI/CD'],
                'Mobile Developer': ['Swift', 'Kotlin', 'React Native', 'Flutter', 'iOS/Android'],
                'Backend Developer': ['Java', 'Python', 'Node.js', 'SQL', 'Microservices'],
                'Frontend Developer': ['JavaScript', 'React', 'Vue.js', 'CSS', 'HTML']
            }
            
            developer_skill_names = {s['skill_name'] for s in skills}
            path_scores = {}
            
            for path, required_skills in career_paths.items():
                matching_skills = sum(1 for skill in required_skills if skill in developer_skill_names)
                score = matching_skills / len(required_skills)
                path_scores[path] = score
            
            # Return top 3 career paths
            sorted_paths = sorted(path_scores.items(), key=lambda x: x[1], reverse=True)
            return [
                {
                    'career_path': path,
                    'match_score': score,
                    'description': f"Your skills match {score*100:.1f}% of the requirements for {path}"
                }
                for path, score in sorted_paths[:3]
            ]
            
        except Exception as e:
            logger.error(f"Error suggesting career paths: {e}")
            return []
    
    def _suggest_repository_improvements(self, repositories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest improvements for repositories."""
        try:
            improvements = []
            
            for repo in repositories:
                if repo['stargazers_count'] < 10:
                    improvements.append({
                        'repository': repo['name'],
                        'suggestion': 'Add a comprehensive README.md to increase visibility',
                        'priority': 'high'
                    })
                
                if not repo['topics']:
                    improvements.append({
                        'repository': repo['name'],
                        'suggestion': 'Add relevant topics to improve discoverability',
                        'priority': 'medium'
                    })
                
                if not repo['description']:
                    improvements.append({
                        'repository': repo['name'],
                        'suggestion': 'Add a clear description of your project',
                        'priority': 'medium'
                    })
            
            return improvements[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting repository improvements: {e}")
            return []
    
    def _suggest_networking_opportunities(self, developer_id: int, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest networking opportunities."""
        try:
            opportunities = []
            
            # Find developers with similar skills
            for skill in skills[:3]:  # Top 3 skills
                similar_developers = self._find_developers_with_skill(skill['skill_id'])
                for dev in similar_developers[:2]:  # Top 2 developers per skill
                    opportunities.append({
                        'developer_username': dev['username'],
                        'developer_name': dev['name'],
                        'common_skill': skill['skill_name'],
                        'proficiency_level': dev['proficiency_level'],
                        'description': f"Connect with {dev['username']} who also specializes in {skill['skill_name']}"
                    })
            
            return opportunities[:5]  # Limit to 5 opportunities
            
        except Exception as e:
            logger.error(f"Error suggesting networking opportunities: {e}")
            return []
    
    def _find_developers_with_skill(self, skill_id: int) -> List[Dict[str, Any]]:
        """Find developers who have a specific skill."""
        try:
            skill_node = f"skill_{skill_id}"
            developers = []
            
            for neighbor in self.graph.predecessors(skill_node):
                if self.graph.nodes[neighbor]['type'] == 'developer':
                    edge_data = self.graph.get_edge_data(neighbor, skill_node)
                    for edge_key, edge_attrs in edge_data.items():
                        if edge_attrs['type'] == 'has_skill':
                            dev_data = self.graph.nodes[neighbor]
                            developers.append({
                                'username': dev_data['username'],
                                'name': dev_data['name'],
                                'proficiency_level': edge_attrs['proficiency_level'],
                                'weight': edge_attrs['weight']
                            })
                            break
            
            return sorted(developers, key=lambda x: x['weight'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding developers with skill: {e}")
            return []
    
    def _find_related_skills(self, developer_id: int, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find skills related to the developer's current skills."""
        try:
            related_skills = []
            
            for skill in skills:
                skill_node = f"skill_{skill['skill_id']}"
                for neighbor in self.graph.neighbors(skill_node):
                    if self.graph.nodes[neighbor]['type'] == 'skill':
                        edge_data = self.graph.get_edge_data(skill_node, neighbor)
                        for edge_key, edge_attrs in edge_data.items():
                            if edge_attrs['type'] == 'similar_to':
                                neighbor_data = self.graph.nodes[neighbor]
                                related_skills.append({
                                    'skill_name': neighbor_data['name'],
                                    'category': neighbor_data['category'],
                                    'similarity_score': edge_attrs['similarity_score']
                                })
                                break
            
            # Remove duplicates and sort by similarity
            unique_skills = {}
            for skill in related_skills:
                if skill['skill_name'] not in unique_skills:
                    unique_skills[skill['skill_name']] = skill
                elif skill['similarity_score'] > unique_skills[skill['skill_name']]['similarity_score']:
                    unique_skills[skill['skill_name']] = skill
            
            return sorted(unique_skills.values(), key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding related skills: {e}")
            return []
    
    def _proficiency_to_numeric(self, proficiency: str) -> float:
        """Convert proficiency level to numeric value."""
        proficiency_map = {
            'beginner': 1.0,
            'intermediate': 2.0,
            'advanced': 3.0,
            'expert': 4.0
        }
        return proficiency_map.get(proficiency, 2.0)
    
    def _get_next_proficiency_level(self, current_level: str) -> str:
        """Get the next proficiency level."""
        level_progression = ['beginner', 'intermediate', 'advanced', 'expert']
        try:
            current_index = level_progression.index(current_level)
            if current_index < len(level_progression) - 1:
                return level_progression[current_index + 1]
            return current_level
        except ValueError:
            return 'intermediate'
    
    def _calculate_repository_impact(self, repositories: List[Dict[str, Any]]) -> float:
        """Calculate repository impact score."""
        if not repositories:
            return 0.0
        
        total_impact = 0
        for repo in repositories:
            # Weight by stars, forks, and whether it's original
            impact = repo['stargazers_count'] * 0.6 + repo['forks_count'] * 0.4
            if not repo['is_fork']:
                impact *= 1.2  # Bonus for original work
            total_impact += impact
        
        return total_impact / len(repositories)
    
    def _analyze_demand_trend(self, skills: List[Dict[str, Any]]) -> str:
        """Analyze demand trend for skills."""
        if not skills:
            return "No skills to analyze"
        
        high_demand_count = sum(1 for s in skills if s.get('market_demand_score', 0) > 7.0)
        total_skills = len(skills)
        
        if high_demand_count / total_skills > 0.7:
            return "High demand skills dominate your profile"
        elif high_demand_count / total_skills > 0.4:
            return "Good mix of high and moderate demand skills"
        else:
            return "Consider adding more high-demand skills"
    
    def _identify_competitive_advantage(self, skills: List[Dict[str, Any]]) -> str:
        """Identify competitive advantage."""
        if not skills:
            return "No skills to analyze"
        
        # Look for unique combinations or high expertise
        expert_skills = [s for s in skills if s['proficiency_level'] == 'expert']
        high_demand_expert = [s for s in expert_skills if s.get('market_demand_score', 0) > 8.0]
        
        if high_demand_expert:
            return f"Expert-level expertise in high-demand skills: {', '.join(s['skill_name'] for s in high_demand_expert)}"
        elif expert_skills:
            return f"Deep expertise in: {', '.join(s['skill_name'] for s in expert_skills)}"
        else:
            return "Focus on developing expert-level skills in your areas of interest"


# Global career analyzer instance
career_analyzer = CareerAnalyzer() 