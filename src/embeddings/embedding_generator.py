"""
Embedding generator for DevCareerCompass Phase 3.
Creates vector embeddings for skills, developers, and repositories using LLM.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json

from src.database.models import Developer, Repository, Skill, Commit
from src.llm.llm_client import llm_client
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for various entities in the system."""
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize the embedding generator.
        
        Args:
            embedding_dim: Dimension of the embeddings (default: 384 for sentence-transformers)
        """
        self.embedding_dim = embedding_dim
        self._skill_embeddings_cache = {}
        self._developer_embeddings_cache = {}
        self._repository_embeddings_cache = {}
    
    async def generate_skill_embedding(self, skill: Skill) -> np.ndarray:
        """
        Generate embedding for a skill.
        
        Args:
            skill: Skill object to embed
            
        Returns:
            numpy array representing the skill embedding
        """
        try:
            # Create a text representation of the skill
            skill_text = f"{skill.name} {skill.category or ''} {skill.description or ''}"
            
            # Generate LLM-based embedding
            embedding = await self._generate_llm_embedding(skill_text, self.embedding_dim)
            
            # Cache the embedding
            self._skill_embeddings_cache[skill.id] = embedding
            
            logger.debug(f"Generated embedding for skill: {skill.name}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding for skill {skill.name}: {e}")
            return np.zeros(self.embedding_dim)
    
    async def generate_developer_embedding(self, developer: Developer, repositories: List[Repository], skills: List[Skill]) -> np.ndarray:
        """
        Generate embedding for a developer based on their profile, repositories, and skills.
        
        Args:
            developer: Developer object to embed
            repositories: List of developer's repositories
            skills: List of developer's skills
            
        Returns:
            numpy array representing the developer embedding
        """
        try:
            # Create a comprehensive text representation
            developer_text = f"{developer.username} {developer.name or ''} {developer.bio or ''} {developer.location or ''} {developer.company or ''}"
            
            # Add repository information
            repo_languages = []
            repo_topics = []
            for repo in repositories:
                if repo.language:
                    repo_languages.append(repo.language)
                if repo.topics:
                    repo_topics.extend(repo.topics)
            
            # Add skills information
            skill_names = [skill.name for skill in skills]
            
            # Combine all information
            full_text = f"{developer_text} {' '.join(repo_languages)} {' '.join(repo_topics)} {' '.join(skill_names)}"
            
            # Generate LLM-based embedding
            embedding = await self._generate_llm_embedding(full_text, self.embedding_dim)
            
            # Cache the embedding
            self._developer_embeddings_cache[developer.id] = embedding
            
            logger.debug(f"Generated embedding for developer: {developer.username}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding for developer {developer.username}: {e}")
            return np.zeros(self.embedding_dim)
    
    async def generate_repository_embedding(self, repository: Repository, commits: List[Commit]) -> np.ndarray:
        """
        Generate embedding for a repository based on its metadata and commit history.
        
        Args:
            repository: Repository object to embed
            commits: List of repository commits
            
        Returns:
            numpy array representing the repository embedding
        """
        try:
            # Create text representation
            repo_text = f"{repository.name} {repository.description or ''} {repository.language or ''}"
            
            # Add languages and topics
            if repository.languages:
                try:
                    # Handle both string and dict formats
                    if isinstance(repository.languages, dict):
                        repo_text += f" {' '.join(repository.languages.keys())}"
                    elif isinstance(repository.languages, str):
                        # Try to parse as JSON
                        import json
                        try:
                            languages_dict = json.loads(repository.languages)
                            if isinstance(languages_dict, dict):
                                repo_text += f" {' '.join(languages_dict.keys())}"
                        except:
                            repo_text += f" {repository.languages}"
                except Exception as e:
                    logger.warning(f"Error processing repository languages: {e}")
            
            if repository.topics:
                try:
                    # Handle both list and string formats
                    if isinstance(repository.topics, list):
                        repo_text += f" {' '.join(repository.topics)}"
                    elif isinstance(repository.topics, str):
                        # Try to parse as JSON
                        import json
                        try:
                            topics_list = json.loads(repository.topics)
                            if isinstance(topics_list, list):
                                repo_text += f" {' '.join(topics_list)}"
                        except:
                            repo_text += f" {repository.topics}"
                except Exception as e:
                    logger.warning(f"Error processing repository topics: {e}")
            
            # Add commit information (limited to recent commits)
            recent_commits = commits[:10]  # Limit to 10 most recent commits
            commit_messages = [commit.message for commit in recent_commits]
            repo_text += f" {' '.join(commit_messages)}"
            
            # Generate LLM-based embedding
            embedding = await self._generate_llm_embedding(repo_text, self.embedding_dim)
            
            # Cache the embedding
            self._repository_embeddings_cache[repository.id] = embedding
            
            logger.debug(f"Generated embedding for repository: {repository.full_name}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding for repository {repository.full_name}: {e}")
            return np.zeros(self.embedding_dim)
    
    async def _generate_llm_embedding(self, text: str, dimension: int) -> np.ndarray:
        """
        Generate embedding using LLM client.
        
        Args:
            text: Text to embed
            dimension: Dimension of the embedding
            
        Returns:
            numpy array representing the embedding
        """
        try:
            # Use LLM client to generate embeddings
            embeddings = await llm_client.generate_embeddings([text])
            
            if embeddings and len(embeddings) > 0:
                embedding = np.array(embeddings[0])
                
                # Ensure correct dimension
                if len(embedding) != dimension:
                    # Pad or truncate to match required dimension
                    if len(embedding) > dimension:
                        embedding = embedding[:dimension]
                    else:
                        padding = np.zeros(dimension - len(embedding))
                        embedding = np.concatenate([embedding, padding])
                
                # Normalize the embedding
                embedding = embedding / np.linalg.norm(embedding)
                
                return embedding
            else:
                # Fallback to hash-based embedding
                return self._hash_based_embedding(text, dimension)
                
        except Exception as e:
            logger.warning(f"LLM embedding failed, using hash-based fallback: {e}")
            return self._hash_based_embedding(text, dimension)
    
    def _hash_based_embedding(self, text: str, dimension: int) -> np.ndarray:
        """
        Generate a hash-based embedding for text (fallback method).
        
        Args:
            text: Text to embed
            dimension: Dimension of the embedding
            
        Returns:
            numpy array representing the embedding
        """
        # Create a hash of the text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Use the hash to seed a random number generator (ensure it's within valid range)
        seed = int(text_hash, 16) % (2**32 - 1)  # Ensure seed is within valid range
        np.random.seed(seed)
        
        # Generate a random embedding
        embedding = np.random.normal(0, 1, dimension)
        
        # Normalize the embedding
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def get_cached_embedding(self, entity_type: str, entity_id: int) -> Optional[np.ndarray]:
        """
        Get a cached embedding for an entity.
        
        Args:
            entity_type: Type of entity ('skill', 'developer', 'repository')
            entity_id: ID of the entity
            
        Returns:
            Cached embedding or None if not found
        """
        cache_map = {
            'skill': self._skill_embeddings_cache,
            'developer': self._developer_embeddings_cache,
            'repository': self._repository_embeddings_cache
        }
        
        return cache_map.get(entity_type, {}).get(entity_id)
    
    def clear_cache(self, entity_type: Optional[str] = None):
        """
        Clear the embedding cache.
        
        Args:
            entity_type: Type of entity to clear cache for, or None to clear all
        """
        if entity_type is None:
            self._skill_embeddings_cache.clear()
            self._developer_embeddings_cache.clear()
            self._repository_embeddings_cache.clear()
        else:
            cache_map = {
                'skill': self._skill_embeddings_cache,
                'developer': self._developer_embeddings_cache,
                'repository': self._repository_embeddings_cache
            }
            cache_map.get(entity_type, {}).clear()
        
        logger.debug(f"Cleared embedding cache for {entity_type or 'all entities'}")


# Global embedding generator instance
embedding_generator = EmbeddingGenerator() 