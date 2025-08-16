"""
Knowledge Graph Builder for DevCareerCompass Phase 2.
Creates and manages graph relationships between developers, skills, and repositories.
"""

import networkx as nx
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import numpy as np

from src.database.models import Developer, Repository, Skill, Commit, DeveloperSkill
from src.embeddings.embedding_generator import embedding_generator
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class KnowledgeGraphBuilder:
    """Builds and manages the knowledge graph for career insights."""
    
    def __init__(self):
        """Initialize the knowledge graph builder."""
        self.graph = nx.MultiDiGraph()
        self._node_mapping = {}  # Maps database IDs to graph node IDs
        self._edge_weights = {}
    
    async def build_graph_from_database(self, session) -> nx.MultiDiGraph:
        """
        Build the knowledge graph from database data.
        
        Args:
            session: Database session
            
        Returns:
            NetworkX graph representing the knowledge graph
        """
        try:
            logger.info("Building knowledge graph from database...")
            
            # Clear existing graph
            self.graph.clear()
            self._node_mapping.clear()
            self._edge_weights.clear()
            
            # Add nodes for all entities
            await self._add_developer_nodes(session)
            await self._add_skill_nodes(session)
            await self._add_repository_nodes(session)
            
            # Add edges for relationships
            self._add_developer_skill_edges(session)
            self._add_developer_repository_edges(session)
            self._add_skill_repository_edges(session)
            self._add_skill_similarity_edges()
            
            logger.info(f"Knowledge graph built successfully. Nodes: {self.graph.number_of_nodes()}, Edges: {self.graph.number_of_edges()}")
            return self.graph
            
        except Exception as e:
            logger.error(f"Error building knowledge graph: {e}")
            return nx.MultiDiGraph()
    
    async def _add_developer_nodes(self, session):
        """Add developer nodes to the graph."""
        try:
            developers = session.query(Developer).all()
            
            for developer in developers:
                node_id = f"developer_{developer.id}"
                self._node_mapping[f"developer_{developer.id}"] = node_id
                
                # Get developer's repositories and skills
                repositories = session.query(Repository).filter(Repository.developer_id == developer.id).all()
                skills = session.query(Skill).join(DeveloperSkill).filter(DeveloperSkill.developer_id == developer.id).all()
                
                # Generate embedding
                embedding = await embedding_generator.generate_developer_embedding(developer, repositories, skills)
                
                # Add node with attributes
                self.graph.add_node(node_id, 
                    type="developer",
                    id=developer.id,
                    username=developer.username,
                    name=developer.name,
                    bio=developer.bio,
                    location=developer.location,
                    company=developer.company,
                    followers=developer.followers,
                    public_repos=developer.public_repos,
                    embedding=embedding.tolist(),
                    created_at=developer.created_at.isoformat() if developer.created_at else None
                )
            
            logger.debug(f"Added {len(developers)} developer nodes")
            
        except Exception as e:
            logger.error(f"Error adding developer nodes: {e}")
    
    async def _add_skill_nodes(self, session):
        """Add skill nodes to the graph."""
        try:
            skills = session.query(Skill).all()
            
            for skill in skills:
                node_id = f"skill_{skill.id}"
                self._node_mapping[f"skill_{skill.id}"] = node_id
                
                # Generate embedding
                embedding = await embedding_generator.generate_skill_embedding(skill)
                
                # Add node with attributes
                self.graph.add_node(node_id,
                    type="skill",
                    id=skill.id,
                    name=skill.name,
                    category=skill.category,
                    description=skill.description,
                    popularity_score=skill.popularity_score,
                    market_demand_score=skill.market_demand_score,
                    embedding=embedding.tolist(),
                    created_at=skill.created_at.isoformat() if skill.created_at else None
                )
            
            logger.debug(f"Added {len(skills)} skill nodes")
            
        except Exception as e:
            logger.error(f"Error adding skill nodes: {e}")
    
    async def _add_repository_nodes(self, session):
        """Add repository nodes to the graph."""
        try:
            repositories = session.query(Repository).all()
            
            for repository in repositories:
                node_id = f"repository_{repository.id}"
                self._node_mapping[f"repository_{repository.id}"] = node_id
                
                # Get repository commits
                commits = session.query(Commit).filter(Commit.repository_id == repository.id).all()
                
                # Generate embedding
                embedding = await embedding_generator.generate_repository_embedding(repository, commits)
                
                # Add node with attributes
                self.graph.add_node(node_id,
                    type="repository",
                    id=repository.id,
                    name=repository.name,
                    full_name=repository.full_name,
                    description=repository.description,
                    language=repository.language,
                    languages=repository.languages,
                    topics=repository.topics,
                    stargazers_count=repository.stargazers_count,
                    forks_count=repository.forks_count,
                    embedding=embedding.tolist(),
                    created_at=repository.created_at.isoformat() if repository.created_at else None
                )
            
            logger.debug(f"Added {len(repositories)} repository nodes")
            
        except Exception as e:
            logger.error(f"Error adding repository nodes: {e}")
    
    def _add_developer_skill_edges(self, session):
        """Add edges between developers and skills."""
        try:
            developer_skills = session.query(DeveloperSkill).all()
            
            for dev_skill in developer_skills:
                developer_node = self._node_mapping.get(f"developer_{dev_skill.developer_id}")
                skill_node = self._node_mapping.get(f"skill_{dev_skill.skill_id}")
                
                if developer_node and skill_node:
                    # Calculate edge weight based on proficiency and usage frequency
                    weight = self._calculate_skill_weight(dev_skill)
                    
                    self.graph.add_edge(developer_node, skill_node,
                        type="has_skill",
                        proficiency_level=dev_skill.proficiency_level,
                        usage_frequency=dev_skill.usage_frequency,
                        weight=weight,
                        first_used_at=dev_skill.first_used_at.isoformat() if dev_skill.first_used_at else None,
                        last_used_at=dev_skill.last_used_at.isoformat() if dev_skill.last_used_at else None
                    )
            
            logger.debug(f"Added {len(developer_skills)} developer-skill edges")
            
        except Exception as e:
            logger.error(f"Error adding developer-skill edges: {e}")
    
    def _add_developer_repository_edges(self, session):
        """Add edges between developers and repositories."""
        try:
            repositories = session.query(Repository).all()
            
            for repository in repositories:
                developer_node = self._node_mapping.get(f"developer_{repository.developer_id}")
                repository_node = self._node_mapping.get(f"repository_{repository.id}")
                
                if developer_node and repository_node:
                    # Calculate edge weight based on repository metrics
                    weight = self._calculate_repository_weight(repository)
                    
                    self.graph.add_edge(developer_node, repository_node,
                        type="owns_repository",
                        weight=weight,
                        is_fork=repository.is_fork,
                        is_private=repository.is_private,
                        created_at=repository.created_at.isoformat() if repository.created_at else None
                    )
            
            logger.debug(f"Added {len(repositories)} developer-repository edges")
            
        except Exception as e:
            logger.error(f"Error adding developer-repository edges: {e}")
    
    def _add_skill_repository_edges(self, session):
        """Add edges between skills and repositories based on languages and topics."""
        try:
            repositories = session.query(Repository).all()
            
            for repository in repositories:
                repository_node = self._node_mapping.get(f"repository_{repository.id}")
                
                if not repository_node:
                    continue
                
                # Add edges for primary language
                if repository.language:
                    skills = session.query(Skill).filter(Skill.name == repository.language).all()
                    for skill in skills:
                        skill_node = self._node_mapping.get(f"skill_{skill.id}")
                        if skill_node:
                            self.graph.add_edge(repository_node, skill_node,
                                type="uses_language",
                                weight=1.0,
                                language_type="primary"
                            )
                
                # Add edges for additional languages
                if repository.languages:
                    try:
                        # Handle both string and dict formats
                        languages_dict = None
                        if isinstance(repository.languages, dict):
                            languages_dict = repository.languages
                        elif isinstance(repository.languages, str):
                            # Try to parse as JSON
                            import json
                            try:
                                languages_dict = json.loads(repository.languages)
                            except:
                                pass
                        
                        if languages_dict and isinstance(languages_dict, dict):
                            for language in languages_dict.keys():
                                skills = session.query(Skill).filter(Skill.name == language).all()
                                for skill in skills:
                                    skill_node = self._node_mapping.get(f"skill_{skill.id}")
                                    if skill_node:
                                        self.graph.add_edge(repository_node, skill_node,
                                            type="uses_language",
                                            weight=0.5,
                                            language_type="secondary"
                                        )
                    except Exception as e:
                        logger.warning(f"Error processing repository languages for edges: {e}")
                
                # Add edges for topics
                if repository.topics:
                    try:
                        # Handle both list and string formats
                        topics_list = None
                        if isinstance(repository.topics, list):
                            topics_list = repository.topics
                        elif isinstance(repository.topics, str):
                            # Try to parse as JSON
                            import json
                            try:
                                topics_list = json.loads(repository.topics)
                            except:
                                pass
                        
                        if topics_list and isinstance(topics_list, list):
                            for topic in topics_list:
                                skills = session.query(Skill).filter(Skill.name == topic).all()
                                for skill in skills:
                                    skill_node = self._node_mapping.get(f"skill_{skill.id}")
                                    if skill_node:
                                        self.graph.add_edge(repository_node, skill_node,
                                            type="uses_topic",
                                            weight=0.3,
                                            topic=topic
                                        )
                    except Exception as e:
                        logger.warning(f"Error processing repository topics for edges: {e}")
            
            logger.debug("Added skill-repository edges")
            
        except Exception as e:
            logger.error(f"Error adding skill-repository edges: {e}")
    
    def _add_skill_similarity_edges(self):
        """Add edges between similar skills based on embeddings."""
        try:
            skill_nodes = [node for node, attrs in self.graph.nodes(data=True) if attrs.get('type') == 'skill']
            
            for i, skill1 in enumerate(skill_nodes):
                for skill2 in skill_nodes[i+1:]:
                    # Calculate similarity between skill embeddings
                    embedding1 = np.array(self.graph.nodes[skill1]['embedding'])
                    embedding2 = np.array(self.graph.nodes[skill2]['embedding'])
                    
                    similarity = np.dot(embedding1, embedding2)
                    
                    # Add edge if similarity is above threshold
                    if similarity > 0.7:  # Threshold for similarity
                        self.graph.add_edge(skill1, skill2,
                            type="similar_to",
                            weight=similarity,
                            similarity_score=float(similarity)
                        )
            
            logger.debug("Added skill similarity edges")
            
        except Exception as e:
            logger.error(f"Error adding skill similarity edges: {e}")
    
    def _calculate_skill_weight(self, dev_skill: DeveloperSkill) -> float:
        """Calculate edge weight for developer-skill relationship."""
        # Base weight from proficiency level
        proficiency_weights = {
            'beginner': 0.3,
            'intermediate': 0.6,
            'advanced': 0.8,
            'expert': 1.0
        }
        
        base_weight = proficiency_weights.get(dev_skill.proficiency_level, 0.5)
        
        # Adjust based on usage frequency (normalize to 0-1)
        usage_factor = min(dev_skill.usage_frequency / 100.0, 1.0) if dev_skill.usage_frequency else 0.5
        
        return base_weight * usage_factor
    
    def _calculate_repository_weight(self, repository: Repository) -> float:
        """Calculate edge weight for developer-repository relationship."""
        # Base weight
        weight = 1.0
        
        # Adjust based on repository metrics
        if repository.stargazers_count:
            weight += min(repository.stargazers_count / 1000.0, 1.0)
        
        if repository.forks_count:
            weight += min(repository.forks_count / 100.0, 0.5)
        
        return min(weight, 2.0)  # Cap at 2.0
    
    def get_developer_skills(self, developer_id: int) -> List[Dict[str, Any]]:
        """Get skills for a specific developer."""
        try:
            developer_node = self._node_mapping.get(f"developer_{developer_id}")
            if not developer_node:
                return []
            
            skills = []
            for neighbor in self.graph.neighbors(developer_node):
                if self.graph.nodes[neighbor]['type'] == 'skill':
                    edge_data = self.graph.get_edge_data(developer_node, neighbor)
                    for edge_key, edge_attrs in edge_data.items():
                        if edge_attrs['type'] == 'has_skill':
                            skills.append({
                                'skill_id': self.graph.nodes[neighbor]['id'],
                                'skill_name': self.graph.nodes[neighbor]['name'],
                                'category': self.graph.nodes[neighbor]['category'],
                                'proficiency_level': edge_attrs['proficiency_level'],
                                'usage_frequency': edge_attrs['usage_frequency'],
                                'weight': edge_attrs['weight']
                            })
                            break
            
            return skills
            
        except Exception as e:
            logger.error(f"Error getting developer skills: {e}")
            return []
    
    def get_skill_developers(self, skill_id: int) -> List[Dict[str, Any]]:
        """Get developers who have a specific skill."""
        try:
            skill_node = self._node_mapping.get(f"skill_{skill_id}")
            if not skill_node:
                return []
            
            developers = []
            for neighbor in self.graph.predecessors(skill_node):
                if self.graph.nodes[neighbor]['type'] == 'developer':
                    edge_data = self.graph.get_edge_data(neighbor, skill_node)
                    for edge_key, edge_attrs in edge_data.items():
                        if edge_attrs['type'] == 'has_skill':
                            developers.append({
                                'developer_id': self.graph.nodes[neighbor]['id'],
                                'username': self.graph.nodes[neighbor]['username'],
                                'name': self.graph.nodes[neighbor]['name'],
                                'proficiency_level': edge_attrs['proficiency_level'],
                                'usage_frequency': edge_attrs['usage_frequency'],
                                'weight': edge_attrs['weight']
                            })
                            break
            
            return developers
            
        except Exception as e:
            logger.error(f"Error getting skill developers: {e}")
            return []
    
    def get_similar_skills(self, skill_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get skills similar to a given skill."""
        try:
            skill_node = self._node_mapping.get(f"skill_{skill_id}")
            if not skill_node:
                return []
            
            similar_skills = []
            for neighbor in self.graph.neighbors(skill_node):
                if self.graph.nodes[neighbor]['type'] == 'skill':
                    edge_data = self.graph.get_edge_data(skill_node, neighbor)
                    for edge_key, edge_attrs in edge_data.items():
                        if edge_attrs['type'] == 'similar_to':
                            similar_skills.append({
                                'skill_id': self.graph.nodes[neighbor]['id'],
                                'skill_name': self.graph.nodes[neighbor]['name'],
                                'category': self.graph.nodes[neighbor]['category'],
                                'similarity_score': edge_attrs['similarity_score']
                            })
                            break
            
            # Sort by similarity score and limit results
            similar_skills.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_skills[:limit]
            
        except Exception as e:
            logger.error(f"Error getting similar skills: {e}")
            return []
    
    def save_graph(self, filepath: str):
        """Save the graph to a file."""
        try:
            # Convert numpy arrays to lists for JSON serialization
            graph_data = nx.node_link_data(self.graph)
            
            with open(filepath, 'w') as f:
                json.dump(graph_data, f, indent=2)
            
            logger.info(f"Knowledge graph saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving knowledge graph: {e}")
    
    def load_graph(self, filepath: str):
        """Load the graph from a file."""
        try:
            with open(filepath, 'r') as f:
                graph_data = json.load(f)
            
            self.graph = nx.node_link_graph(graph_data, directed=True, multigraph=True)
            
            # Rebuild node mapping
            self._node_mapping.clear()
            for node, attrs in self.graph.nodes(data=True):
                entity_type = attrs.get('type')
                entity_id = attrs.get('id')
                if entity_type and entity_id:
                    self._node_mapping[f"{entity_type}_{entity_id}"] = node
            
            logger.info(f"Knowledge graph loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading knowledge graph: {e}")


# Global knowledge graph builder instance
knowledge_graph_builder = KnowledgeGraphBuilder() 