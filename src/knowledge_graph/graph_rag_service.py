#!/usr/bin/env python3
"""
Enhanced Graph RAG Service for DevCareerCompass
Combines knowledge graph traversal with vector search for advanced career insights
"""

import asyncio
import networkx as nx
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
import json
from collections import defaultdict, Counter

from src.knowledge_graph.graph_builder import knowledge_graph_builder
from src.vector_store.qdrant_client import QdrantVectorClient
from src.embeddings.embedding_generator import embedding_generator
from src.llm.llm_client import llm_client
from src.database.connection import db_manager
from src.database.models import Developer, Skill, Repository, JobPosting
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class GraphRAGService:
    """Enhanced Graph RAG service combining knowledge graph with vector search."""
    
    def __init__(self):
        """Initialize the Graph RAG service."""
        self.graph = None
        self.qdrant_client = None
        self.embedding_generator = None
        self.llm_client = None
        self._initialized = False
        self._cache = {}
        
        # Graph traversal parameters
        self.max_path_length = 3
        self.similarity_threshold = 0.7
        self.max_results = 10
        
        # Career path definitions with skill requirements
        self.career_paths = {
            'AI Engineer': {
                'core_skills': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch'],
                'advanced_skills': ['RAG', 'LLMs', 'Vector Databases', 'MCP', 'Prompt Engineering'],
                'tools': ['Jupyter', 'Git', 'Docker', 'AWS', 'Google Cloud'],
                'description': 'Build and deploy AI systems, including machine learning models and intelligent applications'
            },
            'Data Scientist': {
                'core_skills': ['Python', 'R', 'SQL', 'Statistics', 'Machine Learning'],
                'advanced_skills': ['Deep Learning', 'NLP', 'Computer Vision', 'Big Data', 'Data Visualization'],
                'tools': ['Pandas', 'NumPy', 'Scikit-learn', 'Tableau', 'Power BI'],
                'description': 'Analyze complex data to extract insights and build predictive models'
            },
            'Full-Stack Developer': {
                'core_skills': ['JavaScript', 'HTML', 'CSS', 'Python', 'SQL'],
                'advanced_skills': ['React', 'Node.js', 'Django', 'Flask', 'REST APIs'],
                'tools': ['Git', 'Docker', 'AWS', 'VSCode', 'Postman'],
                'description': 'Develop both frontend and backend components of web applications'
            },
            'DevOps Engineer': {
                'core_skills': ['Linux', 'Docker', 'Kubernetes', 'AWS', 'CI/CD'],
                'advanced_skills': ['Terraform', 'Ansible', 'Prometheus', 'Grafana', 'Microservices'],
                'tools': ['Jenkins', 'GitLab', 'GitHub Actions', 'ELK Stack', 'Splunk'],
                'description': 'Automate deployment, scaling, and monitoring of applications'
            },
            'Backend Developer': {
                'core_skills': ['Java', 'Python', 'Node.js', 'SQL', 'REST APIs'],
                'advanced_skills': ['Microservices', 'GraphQL', 'Message Queues', 'Caching', 'Security'],
                'tools': ['Spring Boot', 'Django', 'Express', 'PostgreSQL', 'Redis'],
                'description': 'Build server-side logic and APIs for web applications'
            },
            'Frontend Developer': {
                'core_skills': ['JavaScript', 'HTML', 'CSS', 'React', 'Vue.js'],
                'advanced_skills': ['TypeScript', 'Angular', 'Next.js', 'Webpack', 'Testing'],
                'tools': ['VSCode', 'Chrome DevTools', 'Figma', 'Storybook', 'Jest'],
                'description': 'Create user interfaces and interactive web experiences'
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize the Graph RAG service."""
        try:
            logger.info("Initializing Graph RAG service...")
            
            # Initialize components
            self.qdrant_client = QdrantVectorClient()
            self.embedding_generator = embedding_generator
            self.llm_client = llm_client
            
            # Build knowledge graph
            with db_manager.get_session() as session:
                self.graph = await knowledge_graph_builder.build_graph_from_database(session)
            
            if self.graph and self.graph.number_of_nodes() > 0:
                self._initialized = True
                logger.info(f"Graph RAG service initialized with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
                return True
            else:
                logger.error("Failed to build knowledge graph")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing Graph RAG service: {e}")
            return False
    
    async def graph_rag_query(self, query: str, query_type: str = "career_guidance") -> Dict[str, Any]:
        """
        Perform a Graph RAG query combining vector search with graph traversal.
        
        Args:
            query: User query
            query_type: Type of query (career_guidance, skill_analysis, networking, etc.)
            
        Returns:
            Enhanced response with graph-based insights
        """
        try:
            if not self._initialized:
                return {"error": "Graph RAG service not initialized"}
            
            # Generate query embedding
            query_embedding = self.embedding_generator._hash_based_embedding(query, 384).tolist()
            
            # Step 1: Vector search for relevant entities
            vector_results = await self._perform_vector_search(query_embedding, query_type)
            
            # Step 2: Graph traversal to find related entities
            graph_results = await self._perform_graph_traversal(vector_results, query_type)
            
            # Step 3: Path analysis for career insights
            path_insights = await self._analyze_career_paths(vector_results, graph_results)
            
            # Step 4: Generate contextual response
            response = await self._generate_contextual_response(query, vector_results, graph_results, path_insights)
            
            return {
                'query': query,
                'query_type': query_type,
                'vector_results': vector_results,
                'graph_insights': graph_results,
                'career_paths': path_insights,
                'response': response,
                'confidence': self._calculate_confidence(vector_results, graph_results)
            }
            
        except Exception as e:
            logger.error(f"Error in Graph RAG query: {e}")
            return {"error": str(e)}
    
    async def _perform_vector_search(self, query_embedding: List[float], query_type: str) -> Dict[str, Any]:
        """Perform vector search across different entity types."""
        try:
            results = {}
            
            # Search skills
            if query_type in ['career_guidance', 'skill_analysis', 'learning_path']:
                skills = self.qdrant_client.search_similar_skills(query_embedding, top_k=5)
                results['skills'] = skills
            
            # Search developers
            if query_type in ['networking', 'mentorship', 'collaboration']:
                developers = self.qdrant_client.search_similar_developers(query_embedding, top_k=5)
                results['developers'] = developers
            
            # Search repositories
            if query_type in ['project_ideas', 'code_examples', 'learning_resources']:
                repositories = self.qdrant_client.search_similar_repositories(query_embedding, top_k=5)
                results['repositories'] = repositories
            
            # Search job postings
            if query_type in ['career_guidance', 'job_market', 'salary_info']:
                jobs = self.qdrant_client.search_similar_job_postings(query_embedding, top_k=5)
                results['jobs'] = jobs
            
            return results
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return {}
    
    async def _perform_graph_traversal(self, vector_results: Dict[str, Any], query_type: str) -> Dict[str, Any]:
        """Perform graph traversal to find related entities."""
        try:
            insights = {}
            
            # Get relevant nodes from vector search
            relevant_nodes = self._extract_relevant_nodes(vector_results)
            
            if not relevant_nodes:
                return insights
            
            # Find connected entities based on query type
            if query_type == 'career_guidance':
                insights['skill_network'] = self._find_skill_network(relevant_nodes)
                insights['career_transitions'] = self._find_career_transitions(relevant_nodes)
                insights['learning_paths'] = self._find_learning_paths(relevant_nodes)
                insights['skill_gaps'] = self._find_skill_gaps(relevant_nodes)
                
            elif query_type == 'networking':
                insights['developer_network'] = self._find_developer_network(relevant_nodes)
                insights['similar_developers'] = self._find_similar_developers(relevant_nodes)
                insights['collaboration_opportunities'] = self._find_collaboration_opportunities(relevant_nodes)
                
            elif query_type == 'skill_analysis':
                insights['skill_relationships'] = self._find_skill_relationships(relevant_nodes)
                insights['co_occurring_skills'] = self._find_co_occurring_skills(relevant_nodes)
                insights['skill_evolution'] = self._find_skill_evolution(relevant_nodes)
                
            elif query_type == 'learning_path':
                insights['prerequisite_skills'] = self._find_prerequisite_skills(relevant_nodes)
                insights['learning_sequence'] = self._find_learning_sequence(relevant_nodes)
                insights['project_recommendations'] = self._find_project_recommendations(relevant_nodes)
                
            elif query_type == 'job_market':
                insights['market_demand'] = self._find_market_demand(relevant_nodes)
                insights['salary_trends'] = self._find_salary_trends(relevant_nodes)
                insights['job_opportunities'] = self._find_job_opportunities(relevant_nodes)
                
            elif query_type == 'project_ideas':
                insights['project_suggestions'] = self._find_project_suggestions(relevant_nodes)
                insights['technology_stack'] = self._find_technology_stack(relevant_nodes)
                insights['implementation_steps'] = self._find_implementation_steps(relevant_nodes)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error in graph traversal: {e}")
            return {}
    
    def _extract_relevant_nodes(self, vector_results: Dict[str, Any]) -> List[str]:
        """Extract relevant node IDs from vector search results."""
        nodes = []
        
        for entity_type, results in vector_results.items():
            if isinstance(results, list):
                for result in results:
                    if isinstance(result, dict) and 'id' in result:
                        nodes.append(f"{entity_type}_{result['id']}")
                    elif isinstance(result, dict) and 'payload' in result and 'id' in result['payload']:
                        nodes.append(f"{entity_type}_{result['payload']['id']}")
        
        return nodes
    
    def _find_skill_network(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find skill network connections."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"connections": 0, "network": []}
            
            network = []
            total_connections = 0
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    # Find connected skills
                    neighbors = list(self.graph.neighbors(skill_node))
                    connected_skills = []
                    
                    for neighbor in neighbors:
                        if neighbor.startswith('skill_') and neighbor in self.graph.nodes:
                            neighbor_data = self.graph.nodes[neighbor]
                            connected_skills.append({
                                'skill': neighbor_data.get('name', 'Unknown'),
                                'relationship': 'related',
                                'strength': 0.8
                            })
                    
                    if connected_skills:
                        skill_data = self.graph.nodes[skill_node]
                        network.append({
                            'skill': skill_data.get('name', 'Unknown'),
                            'connections': len(connected_skills),
                            'related_skills': connected_skills
                        })
                        total_connections += len(connected_skills)
            
            return {
                "connections": total_connections,
                "network": network,
                "central_skills": self._find_central_skills(skill_nodes)
            }
            
        except Exception as e:
            logger.error(f"Error finding skill network: {e}")
            return {"connections": 0, "network": []}
    
    def _find_career_transitions(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find career transition paths."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"paths": 0, "transitions": []}
            
            transitions = []
            
            # Analyze skill combinations for career paths
            for career_path, requirements in self.career_paths.items():
                current_skills = set()
                for skill_node in skill_nodes:
                    if skill_node in self.graph:
                        skill_name = self.graph.nodes[skill_node].get('name', '')
                        current_skills.add(skill_name)
                
                # Calculate skill overlap
                required_skills = set(requirements['core_skills'] + requirements['advanced_skills'])
                overlap = current_skills.intersection(required_skills)
                overlap_percentage = len(overlap) / len(required_skills) if required_skills else 0
                
                if overlap_percentage > 0.2:  # At least 20% overlap
                    missing_skills = required_skills - current_skills
                    transitions.append({
                        'target_role': career_path,
                        'current_skills': list(current_skills),
                        'required_skills': list(required_skills),
                        'overlap_percentage': round(overlap_percentage * 100, 1),
                        'missing_skills': list(missing_skills)[:5],  # Top 5 missing skills
                        'difficulty': self._calculate_transition_difficulty(overlap_percentage),
                        'estimated_time': self._estimate_transition_time(len(missing_skills)),
                        'description': requirements['description']
                    })
            
            # Sort by overlap percentage
            transitions.sort(key=lambda x: x['overlap_percentage'], reverse=True)
            
            return {
                "paths": len(transitions),
                "transitions": transitions[:5]  # Top 5 transitions
            }
            
        except Exception as e:
            logger.error(f"Error finding career transitions: {e}")
            return {"paths": 0, "transitions": []}
    
    def _find_learning_paths(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find learning paths and recommendations."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"paths": 0, "recommendations": []}
            
            recommendations = []
            
            # Find skills that frequently co-occur
            co_occurring = self._find_co_occurring_skills(skill_nodes)
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_name = self.graph.nodes[skill_node].get('name', '')
                    
                    # Find related skills for learning path
                    related_skills = []
                    if skill_node in self.graph:
                        neighbors = list(self.graph.neighbors(skill_node))
                        for neighbor in neighbors:
                            if neighbor.startswith('skill_') and neighbor in self.graph.nodes:
                                neighbor_name = self.graph.nodes[neighbor].get('name', '')
                                related_skills.append(neighbor_name)
                    
                    recommendations.append({
                        'skill': skill_name,
                        'learning_path': related_skills[:3],  # Top 3 related skills
                        'difficulty': 'Intermediate',
                        'estimated_time': '2-4 months',
                        'resources': self._get_learning_resources(skill_name)
                    })
            
            return {
                "paths": len(recommendations),
                "recommendations": recommendations[:5]  # Top 5 recommendations
            }
            
        except Exception as e:
            logger.error(f"Error finding learning paths: {e}")
            return {"paths": 0, "recommendations": []}
    
    def _find_developer_network(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find developer network connections."""
        try:
            developer_nodes = [node for node in relevant_nodes if node.startswith('developer_')]
            if not developer_nodes:
                return {"connections": 0, "network": []}
            
            network = []
            total_connections = 0
            
            for dev_node in developer_nodes:
                if dev_node in self.graph:
                    # Find developers with similar skills
                    neighbors = list(self.graph.neighbors(dev_node))
                    similar_developers = []
                    
                    for neighbor in neighbors:
                        if neighbor.startswith('developer_') and neighbor in self.graph.nodes:
                            neighbor_data = self.graph.nodes[neighbor]
                            similar_developers.append({
                                'username': neighbor_data.get('username', 'Unknown'),
                                'name': neighbor_data.get('name', 'Unknown'),
                                'location': neighbor_data.get('location', 'Unknown'),
                                'skills': self._get_developer_skills(neighbor),
                                'similarity': 0.85
                            })
                    
                    if similar_developers:
                        dev_data = self.graph.nodes[dev_node]
                        network.append({
                            'developer': dev_data.get('username', 'Unknown'),
                            'name': dev_data.get('name', 'Unknown'),
                            'connections': len(similar_developers),
                            'similar_developers': similar_developers[:3]  # Top 3
                        })
                        total_connections += len(similar_developers)
            
            return {
                "connections": total_connections,
                "network": network[:5]  # Top 5 developers
            }
            
        except Exception as e:
            logger.error(f"Error finding developer network: {e}")
            return {"connections": 0, "network": []}
    
    def _find_skill_gaps(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find skill gaps for career advancement."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"gaps": 0, "missing_skills": []}
            
            current_skills = set()
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_name = self.graph.nodes[skill_node].get('name', '')
                    current_skills.add(skill_name)
            
            # Find gaps for AI Engineer role (most relevant for this project)
            ai_engineer_skills = set(self.career_paths['AI Engineer']['core_skills'] + 
                                   self.career_paths['AI Engineer']['advanced_skills'])
            
            missing_skills = ai_engineer_skills - current_skills
            
            gaps = []
            for skill in list(missing_skills)[:5]:  # Top 5 missing skills
                gaps.append({
                    'skill': skill,
                    'importance': 'High' if skill in self.career_paths['AI Engineer']['core_skills'] else 'Medium',
                    'learning_time': '3-6 months',
                    'resources': self._get_learning_resources(skill)
                })
            
            return {
                "gaps": len(gaps),
                "missing_skills": gaps
            }
            
        except Exception as e:
            logger.error(f"Error finding skill gaps: {e}")
            return {"gaps": 0, "missing_skills": []}
    
    def _find_co_occurring_skills(self, skill_nodes: List[str]) -> List[Dict[str, Any]]:
        """Find skills that frequently co-occur."""
        try:
            co_occurring = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    neighbors = list(self.graph.neighbors(skill_node))
                    skill_counts = {}
                    
                    for neighbor in neighbors:
                        if neighbor.startswith('skill_') and neighbor in self.graph.nodes:
                            neighbor_name = self.graph.nodes[neighbor].get('name', '')
                            skill_counts[neighbor_name] = skill_counts.get(neighbor_name, 0) + 1
                    
                    # Sort by frequency
                    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
                    
                    if sorted_skills:
                        skill_name = self.graph.nodes[skill_node].get('name', '')
                        co_occurring.append({
                            'skill': skill_name,
                            'co_occurring_skills': [{'skill': s[0], 'frequency': s[1]} for s in sorted_skills[:3]]
                        })
            
            return co_occurring[:5]  # Top 5
            
        except Exception as e:
            logger.error(f"Error finding co-occurring skills: {e}")
            return []
    
    def _find_central_skills(self, skill_nodes: List[str]) -> List[str]:
        """Find central skills in the network."""
        try:
            if not self.graph:
                return []
            
            # Calculate centrality for skill nodes
            centrality = nx.degree_centrality(self.graph)
            
            # Filter for skill nodes and sort by centrality
            skill_centrality = {node: centrality.get(node, 0) for node in skill_nodes if node in centrality}
            sorted_skills = sorted(skill_centrality.items(), key=lambda x: x[1], reverse=True)
            
            # Return top 3 central skills
            return [self.graph.nodes[node].get('name', 'Unknown') for node, _ in sorted_skills[:3]]
            
        except Exception as e:
            logger.error(f"Error finding central skills: {e}")
            return []
    
    def _get_developer_skills(self, developer_node: str) -> List[str]:
        """Get skills for a developer node."""
        try:
            if developer_node not in self.graph:
                return []
            
            skills = []
            neighbors = list(self.graph.neighbors(developer_node))
            
            for neighbor in neighbors:
                if neighbor.startswith('skill_') and neighbor in self.graph.nodes:
                    skill_name = self.graph.nodes[neighbor].get('name', '')
                    skills.append(skill_name)
            
            return skills[:5]  # Top 5 skills
            
        except Exception as e:
            logger.error(f"Error getting developer skills: {e}")
            return []
    
    def _get_learning_resources(self, skill: str) -> List[str]:
        """Get learning resources for a skill."""
        resources = {
            'Python': ['Python.org', 'Real Python', 'Codecademy Python'],
            'Machine Learning': ['Coursera ML', 'Fast.ai', 'Kaggle Courses'],
            'Deep Learning': ['Deep Learning Specialization', 'PyTorch Tutorials', 'TensorFlow Tutorials'],
            'RAG': ['LangChain Documentation', 'OpenAI Cookbook', 'Vector Database Guides'],
            'LLMs': ['Hugging Face Courses', 'OpenAI API Docs', 'Anthropic Claude Docs'],
            'Vector Databases': ['Qdrant Documentation', 'Pinecone Guides', 'Weaviate Tutorials'],
            'MCP': ['Microsoft MCP Documentation', 'MCP Protocol Specs', 'MCP Examples'],
            'Prompt Engineering': ['OpenAI Prompt Engineering', 'Anthropic Prompt Library', 'LangChain Prompts'],
            'React': ['React Documentation', 'React Tutorial', 'Create React App'],
            'JavaScript': ['MDN Web Docs', 'Eloquent JavaScript', 'You Don\'t Know JS'],
            'Docker': ['Docker Documentation', 'Docker Tutorial', 'Docker Compose Guide'],
            'AWS': ['AWS Documentation', 'AWS Training', 'AWS Solutions Architect'],
            'Git': ['Git Documentation', 'GitHub Guides', 'Atlassian Git Tutorial']
        }
        
        return resources.get(skill, ['Online Documentation', 'YouTube Tutorials', 'Community Forums'])
    
    def _calculate_transition_difficulty(self, overlap_percentage: float) -> str:
        """Calculate difficulty of career transition."""
        if overlap_percentage >= 0.7:
            return "Easy"
        elif overlap_percentage >= 0.4:
            return "Moderate"
        else:
            return "Challenging"
    
    def _estimate_transition_time(self, missing_skills_count: int) -> str:
        """Estimate time needed for career transition."""
        if missing_skills_count <= 2:
            return "3-6 months"
        elif missing_skills_count <= 5:
            return "6-12 months"
        else:
            return "12-18 months"
    
    async def _analyze_career_paths(self, vector_results: Dict[str, Any], graph_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze career paths based on vector and graph results."""
        try:
            career_analysis = {}
            
            # Extract skills from vector results
            skills = vector_results.get('skills', [])
            if skills:
                career_analysis['skill_based_paths'] = self._analyze_skill_based_paths(skills)
                career_analysis['skill_gaps'] = self._analyze_skill_gaps(skills)
            
            # Map graph results to expected format
            career_analysis['career_transitions'] = graph_results.get('career_transitions', {})
            career_analysis['learning_paths'] = graph_results.get('learning_paths', {})
            career_analysis['market_demand'] = graph_results.get('market_demand', {})
            
            # Analyze career transitions from graph results
            transitions = graph_results.get('career_transitions', [])
            if transitions:
                career_analysis['recommended_transitions'] = transitions[:3]
                career_analysis['transition_roadmap'] = self._create_transition_roadmap(transitions)
            
            return career_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing career paths: {e}")
            return {}
    
    def _analyze_skill_based_paths(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze career paths based on current skills."""
        try:
            # Handle both Qdrant payload format and direct skill format
            skill_names = set()
            for skill in skills:
                if isinstance(skill, dict):
                    if 'payload' in skill and 'name' in skill['payload']:
                        skill_names.add(skill['payload']['name'])
                    elif 'name' in skill:
                        skill_names.add(skill['name'])
                    elif 'skill' in skill:
                        skill_names.add(skill['skill'])
            
            path_analysis = []
            
            for career_path, requirements in self.career_paths.items():
                core_skills = set(requirements['core_skills'])
                advanced_skills = set(requirements['advanced_skills'])
                
                matching_core = skill_names & core_skills
                matching_advanced = skill_names & advanced_skills
                
                if matching_core or matching_advanced:
                    path_analysis.append({
                        'career_path': career_path,
                        'description': requirements['description'],
                        'matching_core_skills': list(matching_core),
                        'matching_advanced_skills': list(matching_advanced),
                        'missing_core_skills': list(core_skills - skill_names),
                        'missing_advanced_skills': list(advanced_skills - skill_names),
                        'match_percentage': len(matching_core) / len(core_skills) * 100 if core_skills else 0
                    })
            
            # Sort by match percentage
            path_analysis.sort(key=lambda x: x['match_percentage'], reverse=True)
            return path_analysis[:5]
            
        except Exception as e:
            logger.error(f"Error analyzing skill-based paths: {e}")
            return []
    
    def _analyze_skill_gaps(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze skill gaps for career advancement."""
        try:
            # Handle both Qdrant payload format and direct skill format
            skill_names = set()
            for skill in skills:
                if isinstance(skill, dict):
                    if 'payload' in skill and 'name' in skill['payload']:
                        skill_names.add(skill['payload']['name'])
                    elif 'name' in skill:
                        skill_names.add(skill['name'])
                    elif 'skill' in skill:
                        skill_names.add(skill['skill'])
            
            gaps = []
            
            for career_path, requirements in self.career_paths.items():
                core_skills = set(requirements['core_skills'])
                advanced_skills = set(requirements['advanced_skills'])
                
                missing_core = core_skills - skill_names
                missing_advanced = advanced_skills - skill_names
                
                if missing_core or missing_advanced:
                    gaps.append({
                        'career_path': career_path,
                        'missing_core_skills': list(missing_core),
                        'missing_advanced_skills': list(missing_advanced),
                        'priority_skills': list(missing_core)[:3]  # Top 3 missing core skills
                    })
            
            return gaps[:5]
            
        except Exception as e:
            logger.error(f"Error analyzing skill gaps: {e}")
            return []
    
    def _create_transition_roadmap(self, transitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a roadmap for career transitions."""
        try:
            roadmap = []
            
            for transition in transitions[:3]:  # Top 3 transitions
                steps = []
                
                # Step 1: Learn missing core skills
                if transition['missing_core_skills']:
                    steps.append({
                        'step': 1,
                        'title': 'Learn Core Skills',
                        'description': f"Master these essential skills: {', '.join(transition['missing_core_skills'][:3])}",
                        'estimated_time': '3-6 months',
                        'priority': 'high'
                    })
                
                # Step 2: Build projects
                steps.append({
                    'step': 2,
                    'title': 'Build Portfolio Projects',
                    'description': f"Create projects that demonstrate {transition['target_role']} skills",
                    'estimated_time': '2-4 months',
                    'priority': 'high'
                })
                
                # Step 3: Learn advanced skills
                if transition['missing_advanced_skills']:
                    steps.append({
                        'step': 3,
                        'title': 'Develop Advanced Skills',
                        'description': f"Learn advanced concepts: {', '.join(transition['missing_advanced_skills'][:3])}",
                        'estimated_time': '4-8 months',
                        'priority': 'medium'
                    })
                
                roadmap.append({
                    'target_career': transition['target_role'],
                    'steps': steps,
                    'total_estimated_time': transition['estimated_time']
                })
            
            return roadmap
            
        except Exception as e:
            logger.error(f"Error creating transition roadmap: {e}")
            return []
    
    async def _generate_contextual_response(self, query: str, vector_results: Dict[str, Any], graph_results: Dict[str, Any], path_insights: Dict[str, Any]) -> str:
        """Generate intelligent, contextual response based on query type and insights."""
        try:
            query_lower = query.lower()
            
            # Determine response type based on query content and type
            if 'networking' in query_lower or 'similar' in query_lower or 'connect' in query_lower:
                return self._generate_networking_response(query, vector_results, graph_results)
            elif 'transition' in query_lower or 'career' in query_lower or 'become' in query_lower:
                return self._generate_career_transition_response(query, vector_results, graph_results)
            elif 'skill' in query_lower and ('learn' in query_lower or 'need' in query_lower):
                return self._generate_skill_learning_response(query, vector_results, graph_results)
            elif 'learning path' in query_lower or 'path' in query_lower:
                return self._generate_learning_path_response(query, vector_results, graph_results)
            elif 'salary' in query_lower or 'market' in query_lower or 'trend' in query_lower:
                return self._generate_market_response(query, vector_results, graph_results)
            elif 'project' in query_lower or 'build' in query_lower or 'create' in query_lower:
                return self._generate_project_response(query, vector_results, graph_results)
            else:
                return self._generate_general_response(query, vector_results, graph_results)
                
        except Exception as e:
            logger.error(f"Error generating contextual response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try rephrasing your question."
    
    def _generate_networking_response(self, query: str, vector_results: Dict[str, Any], graph_results: Dict[str, Any]) -> str:
        """Generate networking-focused response."""
        response_parts = []
        
        # Add developer network insights
        if graph_results.get('developer_network', {}).get('connections', 0) > 0:
            network = graph_results['developer_network']
            response_parts.append(f"Based on the developer network analysis, I found {network['connections']} potential connections.")
            
            if network.get('network'):
                top_devs = network['network'][:3]
                response_parts.append("Top developers for networking:")
                for dev in top_devs:
                    response_parts.append(f"• {dev.get('name', dev.get('developer', 'Unknown'))} - {dev.get('connections', 0)} connections")
        
        # Add similar developers
        if graph_results.get('similar_developers', {}).get('developers', 0) > 0:
            similar = graph_results['similar_developers']
            response_parts.append(f"\nI identified {similar['developers']} developers with similar skill profiles:")
            
            if similar.get('similarities'):
                for dev in similar['similarities'][:3]:
                    skills = ', '.join(dev.get('skills', [])[:3])
                    response_parts.append(f"• {dev.get('name', dev.get('developer', 'Unknown'))} - Skills: {skills}")
        
        # Add collaboration opportunities
        if graph_results.get('collaboration_opportunities', {}).get('opportunities', 0) > 0:
            collab = graph_results['collaboration_opportunities']
            response_parts.append(f"\nCollaboration opportunities: {collab['opportunities']} potential partnerships identified.")
        
        if not response_parts:
            response_parts.append("I found some developers in the network, but need more specific information about your skills to provide targeted networking recommendations.")
        
        return "\n".join(response_parts)
    
    def _generate_career_transition_response(self, query: str, vector_results: Dict[str, Any], graph_results: Dict[str, Any]) -> str:
        """Generate career transition response."""
        response_parts = []
        
        # Add career transitions - handle both dict and list formats
        career_transitions = graph_results.get('career_transitions')
        if career_transitions:
            if isinstance(career_transitions, dict):
                if career_transitions.get('paths', 0) > 0:
                    transitions = career_transitions
                    response_parts.append(f"I found {transitions['paths']} potential career transition paths:")
                    
                    if transitions.get('transitions'):
                        for transition in transitions['transitions'][:3]:
                            target_role = transition.get('target_role', 'Unknown')
                            overlap = transition.get('overlap_percentage', 0)
                            difficulty = transition.get('difficulty', 'Unknown')
                            time_estimate = transition.get('estimated_time', 'Unknown')
                            
                            response_parts.append(f"\n🎯 {target_role}:")
                            response_parts.append(f"   • Match: {overlap}% of required skills")
                            response_parts.append(f"   • Difficulty: {difficulty}")
                            response_parts.append(f"   • Timeline: {time_estimate}")
                            
                            if transition.get('missing_skills'):
                                missing = ', '.join(transition['missing_skills'][:3])
                                response_parts.append(f"   • Key skills to learn: {missing}")
            elif isinstance(career_transitions, list):
                response_parts.append(f"I found {len(career_transitions)} potential career transition paths:")
                
                for transition in career_transitions[:3]:
                    if isinstance(transition, dict):
                        target_role = transition.get('target_role', 'Unknown')
                        overlap = transition.get('overlap_percentage', 0)
                        difficulty = transition.get('difficulty', 'Unknown')
                        time_estimate = transition.get('estimated_time', 'Unknown')
                        
                        response_parts.append(f"\n🎯 {target_role}:")
                        response_parts.append(f"   • Match: {overlap}% of required skills")
                        response_parts.append(f"   • Difficulty: {difficulty}")
                        response_parts.append(f"   • Timeline: {time_estimate}")
                        
                        if transition.get('missing_skills'):
                            missing = ', '.join(transition['missing_skills'][:3])
                            response_parts.append(f"   • Key skills to learn: {missing}")
        
        # Add skill gaps - handle both dict and list formats
        skill_gaps = graph_results.get('skill_gaps')
        if skill_gaps:
            if isinstance(skill_gaps, dict):
                if skill_gaps.get('gaps', 0) > 0:
                    gaps = skill_gaps
                    response_parts.append(f"\n📚 Skill gaps identified: {gaps['gaps']} areas for improvement")
                    
                    if gaps.get('missing_skills'):
                        for skill in gaps['missing_skills'][:3]:
                            if isinstance(skill, dict):
                                importance = skill.get('importance', 'Medium')
                                learning_time = skill.get('learning_time', 'Unknown')
                                response_parts.append(f"• {skill.get('skill', 'Unknown')} ({importance} priority) - {learning_time}")
            elif isinstance(skill_gaps, list):
                response_parts.append(f"\n📚 Skill gaps identified: {len(skill_gaps)} areas for improvement")
                
                for skill in skill_gaps[:3]:
                    if isinstance(skill, dict):
                        importance = skill.get('importance', 'Medium')
                        learning_time = skill.get('learning_time', 'Unknown')
                        response_parts.append(f"• {skill.get('skill', 'Unknown')} ({importance} priority) - {learning_time}")
        
        if not response_parts:
            response_parts.append("I can help you plan your career transition! Please share more details about your current skills and target role.")
        
        return "\n".join(response_parts)
    
    def _generate_skill_learning_response(self, query: str, vector_results: Dict[str, Any], graph_results: Dict[str, Any]) -> str:
        """Generate skill learning response."""
        response_parts = []
        
        # Add skill network insights
        skill_network = graph_results.get('skill_network')
        if skill_network:
            if isinstance(skill_network, dict):
                if skill_network.get('connections', 0) > 0:
                    network = skill_network
                    response_parts.append(f"Based on the skill network analysis, I found {network['connections']} skill connections.")
                    
                    if network.get('central_skills'):
                        central = ', '.join(network['central_skills'])
                        response_parts.append(f"Central skills in your domain: {central}")
            elif isinstance(skill_network, list):
                response_parts.append(f"Based on the skill network analysis, I found {len(skill_network)} skill connections.")
        
        # Add co-occurring skills
        co_occurring_skills = graph_results.get('co_occurring_skills')
        if co_occurring_skills:
            response_parts.append(f"\n📈 Skills that frequently work together:")
            
            if isinstance(co_occurring_skills, list):
                for skill_data in co_occurring_skills[:3]:
                    if isinstance(skill_data, dict):
                        skill_name = skill_data.get('skill', 'Unknown')
                        co_skills = skill_data.get('co_occurring_skills', [])
                        if co_skills:
                            related = ', '.join([s.get('skill', '') for s in co_skills[:3]])
                            response_parts.append(f"• {skill_name} → {related}")
        
        # Add learning paths
        learning_paths = graph_results.get('learning_paths')
        if learning_paths:
            if isinstance(learning_paths, dict):
                if learning_paths.get('paths', 0) > 0:
                    paths = learning_paths
                    response_parts.append(f"\n🎓 Learning path recommendations: {paths['paths']} structured paths available")
                    
                    if paths.get('recommendations'):
                        for rec in paths['recommendations'][:3]:
                            if isinstance(rec, dict):
                                skill = rec.get('skill', 'Unknown')
                                learning_path = ', '.join(rec.get('learning_path', [])[:3])
                                difficulty = rec.get('difficulty', 'Unknown')
                                response_parts.append(f"• {skill} ({difficulty}): {learning_path}")
            elif isinstance(learning_paths, list):
                response_parts.append(f"\n🎓 Learning path recommendations: {len(learning_paths)} structured paths available")
                
                for rec in learning_paths[:3]:
                    if isinstance(rec, dict):
                        skill = rec.get('skill', 'Unknown')
                        learning_path = ', '.join(rec.get('learning_path', [])[:3])
                        difficulty = rec.get('difficulty', 'Unknown')
                        response_parts.append(f"• {skill} ({difficulty}): {learning_path}")
        
        if not response_parts:
            response_parts.append("I can help you identify the most valuable skills to learn! Please specify your target role or current skill level.")
        
        return "\n".join(response_parts)
    
    def _generate_learning_path_response(self, query: str, vector_results: Dict[str, Any], graph_results: Dict[str, Any]) -> str:
        """Generate learning path response."""
        response_parts = []
        
        # Add prerequisite skills
        if graph_results.get('prerequisite_skills', {}).get('prerequisites', 0) > 0:
            prereqs = graph_results['prerequisite_skills']
            response_parts.append(f"📚 Prerequisite analysis: {prereqs['prerequisites']} skill requirements identified")
            
            if prereqs.get('requirements'):
                for req in prereqs['requirements'][:3]:
                    skill = req.get('skill', 'Unknown')
                    prereq_list = ', '.join(req.get('prerequisites', [])[:3])
                    difficulty = req.get('difficulty', 'Unknown')
                    response_parts.append(f"• {skill} ({difficulty}): Requires {prereq_list}")
        
        # Add learning sequence
        if graph_results.get('learning_sequence', {}).get('sequences', 0) > 0:
            sequences = graph_results['learning_sequence']
            response_parts.append(f"\n🔄 Optimal learning sequences: {sequences['sequences']} structured paths")
            
            if sequences.get('learning_paths'):
                for path in sequences['learning_paths'][:2]:
                    target_role = path.get('target_role', 'Unknown')
                    total_duration = path.get('total_duration', 'Unknown')
                    response_parts.append(f"\n🎯 {target_role} Path ({total_duration}):")
                    
                    if path.get('sequence'):
                        for step in path['sequence'][:5]:
                            skill = step.get('skill', 'Unknown')
                            duration = step.get('duration', 'Unknown')
                            order = step.get('order', 0)
                            response_parts.append(f"   {order}. {skill} ({duration})")
        
        # Add project recommendations
        if graph_results.get('project_recommendations', {}).get('projects', 0) > 0:
            projects = graph_results['project_recommendations']
            response_parts.append(f"\n💻 Project recommendations: {projects['projects']} hands-on projects")
            
            if projects.get('recommendations'):
                for proj in projects['recommendations'][:3]:
                    skill = proj.get('skill', 'Unknown')
                    project_list = ', '.join(proj.get('projects', [])[:2])
                    response_parts.append(f"• {skill}: {project_list}")
        
        if not response_parts:
            response_parts.append("I can help you create a personalized learning path! Please specify your target skill or role.")
        
        return "\n".join(response_parts)
    
    def _generate_market_response(self, query: str, vector_results: Dict[str, Any], graph_results: Dict[str, Any]) -> str:
        """Generate market analysis response."""
        response_parts = []
        
        # Add market demand
        if graph_results.get('market_demand', {}).get('demand', 0) > 0:
            demand = graph_results['market_demand']
            response_parts.append(f"📊 Market demand analysis: {demand['demand']} skills analyzed")
            
            if demand.get('market_data'):
                for skill_data in demand['market_data'][:3]:
                    skill = skill_data.get('skill', 'Unknown')
                    demand_level = skill_data.get('demand_level', 'Unknown')
                    salary_range = skill_data.get('salary_range', 'Unknown')
                    growth_rate = skill_data.get('growth_rate', 'Unknown')
                    response_parts.append(f"• {skill}: {demand_level} demand, {salary_range}, {growth_rate} growth")
        
        # Add salary trends
        if graph_results.get('salary_trends', {}).get('trends', 0) > 0:
            trends = graph_results['salary_trends']
            response_parts.append(f"\n💰 Salary trends: {trends['trends']} skills with trend data")
            
            if trends.get('salary_data'):
                for trend in trends['salary_data'][:3]:
                    skill = trend.get('skill', 'Unknown')
                    avg_salary = trend.get('average_salary', 'Unknown')
                    trend_direction = trend.get('trend', 'Unknown')
                    experience = trend.get('experience_level', 'Unknown')
                    response_parts.append(f"• {skill}: {avg_salary} average, {trend_direction} trend, {experience} level")
        
        # Add job opportunities
        if graph_results.get('job_opportunities', {}).get('opportunities', 0) > 0:
            jobs = graph_results['job_opportunities']
            response_parts.append(f"\n💼 Job opportunities: {jobs['opportunities']} career paths identified")
            
            if jobs.get('jobs'):
                for job in jobs['jobs'][:3]:
                    skill = job.get('skill', 'Unknown')
                    job_titles = ', '.join(job.get('job_titles', [])[:2])
                    salary_range = job.get('salary_range', 'Unknown')
                    response_parts.append(f"• {skill}: {job_titles} ({salary_range})")
        
        if not response_parts:
            response_parts.append("I can provide market insights! Please specify which skills or roles you'd like to analyze.")
        
        return "\n".join(response_parts)
    
    def _generate_project_response(self, query: str, vector_results: Dict[str, Any], graph_results: Dict[str, Any]) -> str:
        """Generate project ideas response."""
        response_parts = []
        
        # Add project suggestions
        if graph_results.get('project_suggestions', {}).get('suggestions', 0) > 0:
            suggestions = graph_results['project_suggestions']
            response_parts.append(f"💡 Project ideas: {suggestions['suggestions']} project suggestions")
            
            if suggestions.get('projects'):
                for proj in suggestions['projects'][:3]:
                    skill = proj.get('skill', 'Unknown')
                    ideas = ', '.join(proj.get('project_ideas', [])[:2])
                    complexity = proj.get('complexity', 'Unknown')
                    timeline = proj.get('timeline', 'Unknown')
                    response_parts.append(f"• {skill} ({complexity}): {ideas} - {timeline}")
        
        # Add technology stack
        if graph_results.get('technology_stack', {}).get('stacks', 0) > 0:
            stacks = graph_results['technology_stack']
            response_parts.append(f"\n🛠️ Technology stacks: {stacks['stacks']} recommended stacks")
            
            if stacks.get('technologies'):
                for tech in stacks['technologies'][:3]:
                    skill = tech.get('skill', 'Unknown')
                    tech_stack = ', '.join(tech.get('tech_stack', [])[:3])
                    category = tech.get('category', 'Unknown')
                    response_parts.append(f"• {skill} ({category}): {tech_stack}")
        
        # Add implementation steps
        if graph_results.get('implementation_steps', {}).get('steps', 0) > 0:
            steps = graph_results['implementation_steps']
            response_parts.append(f"\n📋 Implementation guidance: {steps['steps']} step-by-step guides")
            
            if steps.get('implementation'):
                for impl in steps['implementation'][:2]:
                    skill = impl.get('skill', 'Unknown')
                    step_list = ', '.join(impl.get('steps', [])[:3])
                    timeline = impl.get('timeline', 'Unknown')
                    response_parts.append(f"• {skill}: {step_list} - {timeline}")
        
        if not response_parts:
            response_parts.append("I can suggest project ideas! Please specify your interests or target technologies.")
        
        return "\n".join(response_parts)
    
    def _generate_general_response(self, query: str, vector_results: Dict[str, Any], graph_results: Dict[str, Any]) -> str:
        """Generate general response when query type is unclear."""
        response_parts = []
        
        # Add any available insights
        if graph_results.get('skill_network', {}).get('connections', 0) > 0:
            network = graph_results['skill_network']
            response_parts.append(f"I found {network['connections']} skill connections in the knowledge graph.")
        
        if graph_results.get('developer_network', {}).get('connections', 0) > 0:
            network = graph_results['developer_network']
            response_parts.append(f"There are {network['connections']} developer connections available.")
        
        if vector_results:
            total_results = sum(len(results) if isinstance(results, list) else 0 for results in vector_results.values())
            response_parts.append(f"Vector search found {total_results} relevant entities.")
        
        if not response_parts:
            response_parts.append("I can help you with career guidance, skill analysis, networking, learning paths, market trends, or project ideas. Please ask a specific question!")
        
        return "\n".join(response_parts)
    
    def _prepare_context(self, vector_results: Dict[str, Any], graph_results: Dict[str, Any], 
                        path_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for LLM response generation."""
        return {
            'vector_search_results': {
                'skills_found': len(vector_results.get('skills', [])),
                'developers_found': len(vector_results.get('developers', [])),
                'repositories_found': len(vector_results.get('repositories', [])),
                'jobs_found': len(vector_results.get('jobs', []))
            },
            'graph_insights': {
                'skill_network': graph_results.get('skill_network', []),
                'career_transitions': graph_results.get('career_transitions', []),
                'learning_paths': graph_results.get('learning_paths', []),
                'developer_network': graph_results.get('developer_network', []),
                'similar_developers': graph_results.get('similar_developers', []),
                'co_occurring_skills': graph_results.get('co_occurring_skills', []),
                'skill_gaps': graph_results.get('skill_gaps', []),
                'prerequisite_skills': graph_results.get('prerequisite_skills', []),
                'learning_sequence': graph_results.get('learning_sequence', []),
                'project_recommendations': graph_results.get('project_recommendations', []),
                'market_demand': graph_results.get('market_demand', []),
                'salary_trends': graph_results.get('salary_trends', []),
                'job_opportunities': graph_results.get('job_opportunities', []),
                'project_suggestions': graph_results.get('project_suggestions', []),
                'technology_stack': graph_results.get('technology_stack', []),
                'implementation_steps': graph_results.get('implementation_steps', [])
            },
            'career_analysis': {
                'skill_based_paths': path_insights.get('skill_based_paths', []),
                'skill_gaps': path_insights.get('skill_gaps', []),
                'recommended_transitions': path_insights.get('recommended_transitions', []),
                'transition_roadmap': path_insights.get('transition_roadmap', [])
            }
        }
    
    def _calculate_confidence(self, vector_results: Dict[str, Any], graph_results: Dict[str, Any]) -> float:
        """Calculate confidence score for the response."""
        try:
            confidence = 0.0
            
            # Base confidence from vector search results
            total_entities = sum(len(entities) if isinstance(entities, list) else 0 for entities in vector_results.values())
            if total_entities > 0:
                confidence += min(total_entities / 15.0, 0.4)  # Max 0.4 from vector results
            
            # Additional confidence from graph insights
            if graph_results:
                graph_confidence = 0.0
                
                # Skill network confidence
                if graph_results.get('skill_network', {}).get('connections', 0) > 0:
                    graph_confidence += 0.15
                
                # Developer network confidence
                if graph_results.get('developer_network', {}).get('connections', 0) > 0:
                    graph_confidence += 0.15
                
                # Career transitions confidence
                if graph_results.get('career_transitions', {}).get('paths', 0) > 0:
                    graph_confidence += 0.15
                
                # Learning paths confidence
                if graph_results.get('learning_paths', {}).get('paths', 0) > 0:
                    graph_confidence += 0.15
                
                # Market demand confidence
                if graph_results.get('market_demand', {}).get('demand', 0) > 0:
                    graph_confidence += 0.15
                
                # Similar developers confidence
                if graph_results.get('similar_developers', {}).get('developers', 0) > 0:
                    graph_confidence += 0.1
                
                # Co-occurring skills confidence
                if graph_results.get('co_occurring_skills'):
                    graph_confidence += 0.1
                
                confidence += min(graph_confidence, 0.6)  # Max 0.6 from graph results
            
            # Ensure confidence is between 0.1 and 0.9
            return min(max(confidence, 0.1), 0.9)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.3
    
    def _calculate_transition_difficulty(self, overlap_percentage: float) -> str:
        """Calculate difficulty of career transition."""
        if overlap_percentage >= 0.7:
            return "Easy"
        elif overlap_percentage >= 0.4:
            return "Moderate"
        else:
            return "Challenging"
    
    def _estimate_transition_time(self, missing_skills_count: int) -> str:
        """Estimate time needed for career transition."""
        if missing_skills_count <= 2:
            return "3-6 months"
        elif missing_skills_count <= 5:
            return "6-12 months"
        else:
            return "12-18 months"
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        try:
            if not self.graph:
                return {"error": "Graph not initialized"}
            
            node_types = Counter()
            edge_types = Counter()
            
            # Count node types
            for node, attrs in self.graph.nodes(data=True):
                node_type = attrs.get('type', 'unknown')
                node_types[node_type] += 1
            
            # Count edge types
            for edge in self.graph.edges(data=True):
                edge_type = edge[2].get('type', 'unknown')
                edge_types[edge_type] += 1
            
            return {
                'nodes': self.graph.number_of_nodes(),
                'edges': self.graph.number_of_edges(),
                'density': round(nx.density(self.graph), 3),
                'connected_components': nx.number_connected_components(self.graph.to_undirected()) if self.graph.number_of_nodes() > 1 else 1,
                'average_degree': round(sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(), 2) if self.graph.number_of_nodes() > 0 else 0,
                'node_types': dict(node_types),
                'edge_types': dict(edge_types),
                'is_connected': nx.is_connected(self.graph.to_undirected()) if self.graph.number_of_nodes() > 1 else True
            }
            
        except Exception as e:
            logger.error(f"Error getting graph statistics: {e}")
            return {"error": str(e)}

    def _find_similar_developers(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find developers with similar skills."""
        try:
            developer_nodes = [node for node in relevant_nodes if node.startswith('developer_')]
            if not developer_nodes:
                return {"developers": 0, "similarities": []}
            
            similarities = []
            
            for dev_node in developer_nodes:
                if dev_node in self.graph:
                    dev_data = self.graph.nodes[dev_node]
                    dev_skills = self._get_developer_skills(dev_node)
                    
                    if dev_skills:
                        similarities.append({
                            'developer': dev_data.get('username', 'Unknown'),
                            'name': dev_data.get('name', 'Unknown'),
                            'skills': dev_skills,
                            'similarity_score': 0.85,
                            'location': dev_data.get('location', 'Unknown')
                        })
            
            return {
                "developers": len(similarities),
                "similarities": similarities[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding similar developers: {e}")
            return {"developers": 0, "similarities": []}
    
    def _find_collaboration_opportunities(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find collaboration opportunities."""
        try:
            developer_nodes = [node for node in relevant_nodes if node.startswith('developer_')]
            if not developer_nodes:
                return {"opportunities": 0, "collaborations": []}
            
            collaborations = []
            
            for dev_node in developer_nodes:
                if dev_node in self.graph:
                    dev_data = self.graph.nodes[dev_node]
                    dev_skills = self._get_developer_skills(dev_node)
                    
                    if dev_skills:
                        collaborations.append({
                            'developer': dev_data.get('username', 'Unknown'),
                            'name': dev_data.get('name', 'Unknown'),
                            'expertise': dev_skills[:3],  # Top 3 skills
                            'collaboration_type': 'Skill Sharing',
                            'project_suggestions': ['Open Source Contribution', 'Hackathon Team', 'Study Group']
                        })
            
            return {
                "opportunities": len(collaborations),
                "collaborations": collaborations[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding collaboration opportunities: {e}")
            return {"opportunities": 0, "collaborations": []}
    
    def _find_skill_relationships(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find relationships between skills."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"relationships": 0, "connections": []}
            
            connections = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_data = self.graph.nodes[skill_node]
                    neighbors = list(self.graph.neighbors(skill_node))
                    
                    related_skills = []
                    for neighbor in neighbors:
                        if neighbor.startswith('skill_') and neighbor in self.graph.nodes:
                            neighbor_data = self.graph.nodes[neighbor]
                            related_skills.append({
                                'skill': neighbor_data.get('name', 'Unknown'),
                                'relationship_type': 'complementary',
                                'strength': 0.8
                            })
                    
                    if related_skills:
                        connections.append({
                            'skill': skill_data.get('name', 'Unknown'),
                            'related_skills': related_skills[:3],  # Top 3
                            'total_connections': len(related_skills)
                        })
            
            return {
                "relationships": len(connections),
                "connections": connections[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding skill relationships: {e}")
            return {"relationships": 0, "connections": []}
    
    def _find_skill_evolution(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find skill evolution patterns."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"patterns": 0, "evolution": []}
            
            evolution = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_data = self.graph.nodes[skill_node]
                    skill_name = skill_data.get('name', 'Unknown')
                    
                    # Define evolution paths for common skills
                    evolution_paths = {
                        'Python': ['Python Basics', 'Data Analysis', 'Machine Learning', 'AI/ML'],
                        'JavaScript': ['JavaScript Basics', 'Frontend Development', 'Full-Stack', 'Advanced JS'],
                        'Machine Learning': ['ML Basics', 'Deep Learning', 'AI Engineering', 'MLOps'],
                        'React': ['React Basics', 'Advanced React', 'Full-Stack', 'React Native'],
                        'Docker': ['Docker Basics', 'Container Orchestration', 'DevOps', 'Cloud Native']
                    }
                    
                    if skill_name in evolution_paths:
                        evolution.append({
                            'skill': skill_name,
                            'evolution_path': evolution_paths[skill_name],
                            'current_stage': 'Intermediate',
                            'next_stage': evolution_paths[skill_name][2] if len(evolution_paths[skill_name]) > 2 else 'Advanced'
                        })
            
            return {
                "patterns": len(evolution),
                "evolution": evolution[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding skill evolution: {e}")
            return {"patterns": 0, "evolution": []}
    
    def _find_prerequisite_skills(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find prerequisite skills for learning paths."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"prerequisites": 0, "requirements": []}
            
            requirements = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_data = self.graph.nodes[skill_node]
                    skill_name = skill_data.get('name', 'Unknown')
                    
                    # Define prerequisites for common skills
                    prerequisites = {
                        'Machine Learning': ['Python', 'Statistics', 'Linear Algebra'],
                        'Deep Learning': ['Machine Learning', 'Python', 'Calculus'],
                        'React': ['JavaScript', 'HTML', 'CSS'],
                        'Docker': ['Linux', 'Command Line', 'Networking'],
                        'AWS': ['Linux', 'Networking', 'Security'],
                        'RAG': ['Python', 'Machine Learning', 'Vector Databases'],
                        'LLMs': ['Python', 'Machine Learning', 'NLP'],
                        'MCP': ['Python', 'API Development', 'Protocol Design']
                    }
                    
                    if skill_name in prerequisites:
                        requirements.append({
                            'skill': skill_name,
                            'prerequisites': prerequisites[skill_name],
                            'difficulty': 'Advanced',
                            'estimated_time': '3-6 months'
                        })
            
            return {
                "prerequisites": len(requirements),
                "requirements": requirements[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding prerequisite skills: {e}")
            return {"prerequisites": 0, "requirements": []}
    
    def _find_learning_sequence(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find optimal learning sequence."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"sequences": 0, "learning_paths": []}
            
            learning_paths = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_data = self.graph.nodes[skill_node]
                    skill_name = skill_data.get('name', 'Unknown')
                    
                    # Define learning sequences
                    sequences = {
                        'AI Engineer': [
                            {'skill': 'Python', 'duration': '2 months', 'order': 1},
                            {'skill': 'Machine Learning', 'duration': '3 months', 'order': 2},
                            {'skill': 'Deep Learning', 'duration': '4 months', 'order': 3},
                            {'skill': 'RAG', 'duration': '2 months', 'order': 4},
                            {'skill': 'LLMs', 'duration': '3 months', 'order': 5}
                        ],
                        'Full-Stack Developer': [
                            {'skill': 'HTML/CSS', 'duration': '1 month', 'order': 1},
                            {'skill': 'JavaScript', 'duration': '2 months', 'order': 2},
                            {'skill': 'React', 'duration': '2 months', 'order': 3},
                            {'skill': 'Node.js', 'duration': '2 months', 'order': 4},
                            {'skill': 'Database Design', 'duration': '1 month', 'order': 5}
                        ]
                    }
                    
                    if skill_name in ['Python', 'Machine Learning', 'React', 'JavaScript']:
                        learning_paths.append({
                            'target_role': 'AI Engineer' if skill_name in ['Python', 'Machine Learning'] else 'Full-Stack Developer',
                            'sequence': sequences['AI Engineer'] if skill_name in ['Python', 'Machine Learning'] else sequences['Full-Stack Developer'],
                            'total_duration': '12-14 months',
                            'current_skill': skill_name
                        })
            
            return {
                "sequences": len(learning_paths),
                "learning_paths": learning_paths[:3]  # Top 3
            }
            
        except Exception as e:
            logger.error(f"Error finding learning sequence: {e}")
            return {"sequences": 0, "learning_paths": []}
    
    def _find_project_recommendations(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find project recommendations based on skills."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"projects": 0, "recommendations": []}
            
            recommendations = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_data = self.graph.nodes[skill_node]
                    skill_name = skill_data.get('name', 'Unknown')
                    
                    # Define project recommendations
                    projects = {
                        'Python': ['Web Application', 'Data Analysis Tool', 'Automation Script'],
                        'Machine Learning': ['Sentiment Analysis', 'Image Classification', 'Recommendation System'],
                        'React': ['Todo App', 'E-commerce Site', 'Social Media App'],
                        'RAG': ['Document Assistant', 'Knowledge Base', 'Research Tool'],
                        'LLMs': ['AI Chatbot', 'Text Generator', 'Code Assistant'],
                        'Docker': ['Containerized Web App', 'Microservices Demo', 'DevOps Pipeline']
                    }
                    
                    if skill_name in projects:
                        recommendations.append({
                            'skill': skill_name,
                            'projects': projects[skill_name],
                            'difficulty': 'Intermediate',
                            'estimated_time': '2-4 weeks per project',
                            'technologies': [skill_name, 'Git', 'Cloud Platform']
                        })
            
            return {
                "projects": len(recommendations),
                "recommendations": recommendations[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding project recommendations: {e}")
            return {"projects": 0, "recommendations": []}
    
    def _find_market_demand(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find market demand for skills."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"demand": 0, "market_data": []}
            
            market_data = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_data = self.graph.nodes[skill_node]
                    skill_name = skill_data.get('name', 'Unknown')
                    
                    # Define market demand data
                    demand_data = {
                        'Python': {'demand': 'Very High', 'salary_range': '$80k-$150k', 'growth': '25%'},
                        'Machine Learning': {'demand': 'Very High', 'salary_range': '$100k-$200k', 'growth': '30%'},
                        'React': {'demand': 'High', 'salary_range': '$70k-$130k', 'growth': '20%'},
                        'RAG': {'demand': 'Very High', 'salary_range': '$120k-$200k', 'growth': '40%'},
                        'LLMs': {'demand': 'Very High', 'salary_range': '$130k-$220k', 'growth': '50%'},
                        'Docker': {'demand': 'High', 'salary_range': '$80k-$140k', 'growth': '15%'},
                        'AWS': {'demand': 'High', 'salary_range': '$90k-$160k', 'growth': '18%'}
                    }
                    
                    if skill_name in demand_data:
                        market_data.append({
                            'skill': skill_name,
                            'demand_level': demand_data[skill_name]['demand'],
                            'salary_range': demand_data[skill_name]['salary_range'],
                            'growth_rate': demand_data[skill_name]['growth'],
                            'job_count': '10,000+'
                        })
            
            return {
                "demand": len(market_data),
                "market_data": market_data[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding market demand: {e}")
            return {"demand": 0, "market_data": []}
    
    def _find_salary_trends(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find salary trends for skills."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"trends": 0, "salary_data": []}
            
            salary_data = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_data = self.graph.nodes[skill_node]
                    skill_name = skill_data.get('name', 'Unknown')
                    
                    # Define salary trends
                    trends = {
                        'Python': {'current': '$95k', 'trend': '+15%', 'experience': '3-5 years'},
                        'Machine Learning': {'current': '$130k', 'trend': '+25%', 'experience': '3-5 years'},
                        'React': {'current': '$100k', 'trend': '+12%', 'experience': '2-4 years'},
                        'RAG': {'current': '$150k', 'trend': '+35%', 'experience': '2-3 years'},
                        'LLMs': {'current': '$160k', 'trend': '+40%', 'experience': '2-3 years'}
                    }
                    
                    if skill_name in trends:
                        salary_data.append({
                            'skill': skill_name,
                            'average_salary': trends[skill_name]['current'],
                            'trend': trends[skill_name]['trend'],
                            'experience_level': trends[skill_name]['experience'],
                            'market_position': 'High Demand'
                        })
            
            return {
                "trends": len(salary_data),
                "salary_data": salary_data[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding salary trends: {e}")
            return {"trends": 0, "salary_data": []}
    
    def _find_job_opportunities(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find job opportunities."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"opportunities": 0, "jobs": []}
            
            jobs = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_data = self.graph.nodes[skill_node]
                    skill_name = skill_data.get('name', 'Unknown')
                    
                    # Define job opportunities
                    opportunities = {
                        'Python': ['Software Engineer', 'Data Scientist', 'Backend Developer'],
                        'Machine Learning': ['ML Engineer', 'Data Scientist', 'AI Engineer'],
                        'React': ['Frontend Developer', 'Full-Stack Developer', 'UI/UX Developer'],
                        'RAG': ['AI Engineer', 'ML Engineer', 'Research Scientist'],
                        'LLMs': ['AI Engineer', 'ML Engineer', 'NLP Engineer']
                    }
                    
                    if skill_name in opportunities:
                        jobs.append({
                            'skill': skill_name,
                            'job_titles': opportunities[skill_name],
                            'companies': ['Tech Giants', 'Startups', 'Consulting Firms'],
                            'remote_available': True,
                            'salary_range': '$80k-$200k'
                        })
            
            return {
                "opportunities": len(jobs),
                "jobs": jobs[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding job opportunities: {e}")
            return {"opportunities": 0, "jobs": []}
    
    def _find_project_suggestions(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find project suggestions."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"suggestions": 0, "projects": []}
            
            projects = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_data = self.graph.nodes[skill_node]
                    skill_name = skill_data.get('name', 'Unknown')
                    
                    # Define project suggestions
                    suggestions = {
                        'Python': ['Web Application', 'Data Analysis Tool', 'Automation Script'],
                        'Machine Learning': ['Predictive Model', 'Classification System', 'Recommendation Engine'],
                        'React': ['Interactive Dashboard', 'E-commerce Platform', 'Social Media App'],
                        'RAG': ['Document Assistant', 'Knowledge Base', 'Research Tool'],
                        'LLMs': ['AI Chatbot', 'Text Generator', 'Code Assistant']
                    }
                    
                    if skill_name in suggestions:
                        projects.append({
                            'skill': skill_name,
                            'project_ideas': suggestions[skill_name],
                            'complexity': 'Intermediate',
                            'timeline': '4-8 weeks',
                            'technologies': [skill_name, 'Git', 'Cloud Platform']
                        })
            
            return {
                "suggestions": len(projects),
                "projects": projects[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding project suggestions: {e}")
            return {"suggestions": 0, "projects": []}
    
    def _find_technology_stack(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find technology stack recommendations."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"stacks": 0, "technologies": []}
            
            technologies = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_data = self.graph.nodes[skill_node]
                    skill_name = skill_data.get('name', 'Unknown')
                    
                    # Define technology stacks
                    stacks = {
                        'Python': ['Flask/Django', 'Pandas', 'NumPy', 'PostgreSQL'],
                        'Machine Learning': ['Scikit-learn', 'TensorFlow', 'PyTorch', 'Jupyter'],
                        'React': ['Node.js', 'Express', 'MongoDB', 'Redux'],
                        'RAG': ['LangChain', 'Qdrant', 'OpenAI', 'FastAPI'],
                        'LLMs': ['Hugging Face', 'OpenAI API', 'Anthropic', 'Vector DB']
                    }
                    
                    if skill_name in stacks:
                        technologies.append({
                            'skill': skill_name,
                            'tech_stack': stacks[skill_name],
                            'category': 'Full-Stack' if skill_name in ['Python', 'React'] else 'AI/ML',
                            'deployment': 'Cloud (AWS/GCP/Azure)',
                            'monitoring': 'Logging & Analytics'
                        })
            
            return {
                "stacks": len(technologies),
                "technologies": technologies[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding technology stack: {e}")
            return {"stacks": 0, "technologies": []}
    
    def _find_implementation_steps(self, relevant_nodes: List[str]) -> Dict[str, Any]:
        """Find implementation steps for projects."""
        try:
            skill_nodes = [node for node in relevant_nodes if node.startswith('skill_')]
            if not skill_nodes:
                return {"steps": 0, "implementation": []}
            
            implementation = []
            
            for skill_node in skill_nodes:
                if skill_node in self.graph:
                    skill_data = self.graph.nodes[skill_node]
                    skill_name = skill_data.get('name', 'Unknown')
                    
                    # Define implementation steps
                    steps = {
                        'Python': ['Setup Environment', 'Design Architecture', 'Implement Core Logic', 'Add Tests', 'Deploy'],
                        'Machine Learning': ['Data Collection', 'Data Preprocessing', 'Model Training', 'Evaluation', 'Deployment'],
                        'React': ['Setup Project', 'Design Components', 'Implement Features', 'Add Styling', 'Deploy'],
                        'RAG': ['Setup Vector DB', 'Implement Embeddings', 'Create Retrieval', 'Build Interface', 'Deploy'],
                        'LLMs': ['Choose Model', 'Setup API', 'Implement Prompting', 'Add Context', 'Deploy']
                    }
                    
                    if skill_name in steps:
                        implementation.append({
                            'skill': skill_name,
                            'steps': steps[skill_name],
                            'timeline': '6-8 weeks',
                            'difficulty': 'Intermediate',
                            'resources': ['Documentation', 'Tutorials', 'Community Support']
                        })
            
            return {
                "steps": len(implementation),
                "implementation": implementation[:5]  # Top 5
            }
            
        except Exception as e:
            logger.error(f"Error finding implementation steps: {e}")
            return {"steps": 0, "implementation": []}


# Global Graph RAG service instance
graph_rag_service = GraphRAGService() 