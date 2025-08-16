"""
Qdrant Cloud Vector Database Client for DevCareerCompass
High-performance vector search and storage for career insights
"""

import os
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

from src.utils.logger import get_logger
from src.embeddings.embedding_generator import embedding_generator

# Load environment variables from .env file
load_dotenv()

logger = get_logger(__name__)


class QdrantVectorClient:
    """
    Qdrant Cloud Vector Database Client
    
    Features:
    - Cloud-based vector storage with high availability
    - Real-time similarity search
    - Automatic scaling and optimization
    - Advanced filtering and metadata search
    """
    
    def __init__(self, cloud_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize Qdrant Cloud client
        
        Args:
            cloud_url: Qdrant Cloud URL (optional, uses env var)
            api_key: Qdrant Cloud API key (optional, uses env var)
        """
        self.cloud_url = cloud_url or os.getenv('QDRANT_CLOUD_URL')
        self.api_key = api_key or os.getenv('QDRANT_API_KEY')
        
        # Clean URL if it has trailing characters
        if self.cloud_url:
            self.cloud_url = self.cloud_url.rstrip('%').rstrip()
        
        if not self.cloud_url or not self.api_key:
            logger.warning("Qdrant Cloud credentials not found. Using local fallback.")
            self.client = QdrantClient(":memory:")
            self._is_cloud = False
        else:
            self.client = QdrantClient(
                url=self.cloud_url,
                api_key=self.api_key
            )
            self._is_cloud = True
            logger.info("✅ Connected to Qdrant Cloud")
    
    def _get_collection_name(self, collection_type: str) -> str:
        """Get standardized collection name"""
        return f"devcareer_{collection_type}"
    
    def create_skills_collection(self, dimension: int = 384) -> bool:
        """Create collection for skill vectors"""
        collection_name = self._get_collection_name("skills")
        
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            if any(col.name == collection_name for col in collections.collections):
                logger.info(f"Collection {collection_name} already exists")
                return True
            
            # Create collection with optimized settings
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE,
                    on_disk=True  # Store vectors on disk for large datasets
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    memmap_threshold=20000,
                    indexing_threshold=20000
                )
            )
            
            logger.info(f"✅ Created skills collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create skills collection: {e}")
            return False
    
    def create_developers_collection(self, dimension: int = 384) -> bool:
        """Create collection for developer vectors"""
        collection_name = self._get_collection_name("developers")
        
        try:
            collections = self.client.get_collections()
            if any(col.name == collection_name for col in collections.collections):
                logger.info(f"Collection {collection_name} already exists")
                return True
            
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE,
                    on_disk=True
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    memmap_threshold=20000,
                    indexing_threshold=20000
                )
            )
            
            logger.info(f"✅ Created developers collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create developers collection: {e}")
            return False
    
    def create_repositories_collection(self, dimension: int = 384) -> bool:
        """Create collection for repository vectors"""
        collection_name = self._get_collection_name("repositories")
        
        try:
            collections = self.client.get_collections()
            if any(col.name == collection_name for col in collections.collections):
                logger.info(f"Collection {collection_name} already exists")
                return True
            
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE,
                    on_disk=True
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    memmap_threshold=20000,
                    indexing_threshold=20000
                )
            )
            
            logger.info(f"✅ Created repositories collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create repositories collection: {e}")
            return False
    
    def create_career_paths_collection(self, dimension: int = 384) -> bool:
        """Create collection for career path vectors"""
        collection_name = self._get_collection_name("career_paths")
        
        try:
            collections = self.client.get_collections()
            if any(col.name == collection_name for col in collections.collections):
                logger.info(f"Collection {collection_name} already exists")
                return True
            
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE,
                    on_disk=True
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    memmap_threshold=20000,
                    indexing_threshold=20000
                )
            )
            
            logger.info(f"✅ Created career paths collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create career paths collection: {e}")
            return False
    
    def create_job_postings_collection(self, dimension: int = 384) -> bool:
        """Create collection for job posting vectors"""
        collection_name = self._get_collection_name("job_postings")
        
        try:
            collections = self.client.get_collections()
            if any(col.name == collection_name for col in collections.collections):
                logger.info(f"Collection {collection_name} already exists")
                return True
            
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE,
                    on_disk=True
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    memmap_threshold=20000,
                    indexing_threshold=20000
                )
            )
            
            logger.info(f"✅ Created job postings collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create job postings collection: {e}")
            return False
    
    def insert_skills(self, skills_data: List[Dict[str, Any]]) -> bool:
        """Insert skill vectors into collection"""
        collection_name = self._get_collection_name("skills")
        
        try:
            points = []
            for skill in skills_data:
                point = PointStruct(
                    id=skill['id'],
                    vector=skill['vector'],
                    payload={
                        'skill_id': skill['id'],
                        'skill_name': skill['name'],
                        'category': skill.get('category', ''),
                        'description': skill.get('description', ''),
                        'popularity_score': skill.get('popularity_score', 0.0),
                        'market_demand_score': skill.get('market_demand_score', 0.0),
                        'created_at': skill.get('created_at', datetime.now().isoformat())
                    }
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"✅ Inserted {len(skills_data)} skills into {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert skills: {e}")
            return False
    
    def insert_developers(self, developers_data: List[Dict[str, Any]]) -> bool:
        """Insert developer vectors into collection"""
        collection_name = self._get_collection_name("developers")
        
        try:
            points = []
            for dev in developers_data:
                point = PointStruct(
                    id=dev['id'],
                    vector=dev['vector'],
                    payload={
                        'developer_id': dev['id'],
                        'github_id': dev.get('github_id', ''),
                        'username': dev.get('username', ''),
                        'name': dev.get('name', ''),
                        'email': dev.get('email', ''),
                        'bio': dev.get('bio', ''),
                        'location': dev.get('location', ''),
                        'company': dev.get('company', ''),
                        'public_repos': dev.get('public_repos', 0),
                        'followers': dev.get('followers', 0),
                        'following': dev.get('following', 0),
                        'created_at': dev.get('created_at', datetime.now().isoformat())
                    }
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"✅ Inserted {len(developers_data)} developers into {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert developers: {e}")
            return False
    
    def insert_repositories(self, repos_data: List[Dict[str, Any]]) -> bool:
        """Insert repository vectors into collection"""
        collection_name = self._get_collection_name("repositories")
        
        try:
            points = []
            for repo in repos_data:
                point = PointStruct(
                    id=repo['id'],
                    vector=repo['vector'],
                    payload={
                        'repository_id': repo['id'],
                        'github_id': repo.get('github_id', ''),
                        'developer_id': repo.get('developer_id', ''),
                        'name': repo.get('name', ''),
                        'full_name': repo.get('full_name', ''),
                        'description': repo.get('description', ''),
                        'language': repo.get('language', ''),
                        'languages': repo.get('languages', ''),
                        'topics': repo.get('topics', ''),
                        'stargazers_count': repo.get('stargazers_count', 0),
                        'forks_count': repo.get('forks_count', 0),
                        'is_fork': repo.get('is_fork', False),
                        'is_private': repo.get('is_private', False),
                        'created_at': repo.get('created_at', datetime.now().isoformat())
                    }
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"✅ Inserted {len(repos_data)} repositories into {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert repositories: {e}")
            return False
    
    def insert_career_paths(self, career_paths_data: List[Dict[str, Any]]) -> bool:
        """Insert career path vectors into collection"""
        collection_name = self._get_collection_name("career_paths")
        
        try:
            points = []
            for path in career_paths_data:
                point = PointStruct(
                    id=path['id'],
                    vector=path['vector'],
                    payload={
                        'path_id': path['id'],
                        'path_name': path['name'],
                        'category': path.get('category', ''),
                        'description': path.get('description', ''),
                        'required_skills': path.get('required_skills', []),
                        'salary_range': path.get('salary_range', ''),
                        'growth_potential': path.get('growth_potential', ''),
                        'created_at': path.get('created_at', datetime.now().isoformat())
                    }
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"✅ Inserted {len(career_paths_data)} career paths into {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert career paths: {e}")
            return False
    
    def insert_job_postings(self, job_postings_data: List[Dict[str, Any]]) -> bool:
        """Insert job posting vectors into collection"""
        collection_name = self._get_collection_name("job_postings")
        
        try:
            points = []
            for job in job_postings_data:
                point = PointStruct(
                    id=job['id'],
                    vector=job['vector'],
                    payload={
                        'job_id': job['id'],
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('location', ''),
                        'description': job.get('description', ''),
                        'requirements': job.get('requirements', ''),
                        'salary_min': job.get('salary_min'),
                        'salary_max': job.get('salary_max'),
                        'job_type': job.get('job_type', ''),
                        'experience_level': job.get('experience_level', ''),
                        'remote_option': job.get('remote_option', False),
                        'data_source': job.get('data_source', ''),  # indeed
                        'source_id': job.get('source_id', ''),
                        'posted_date': job.get('posted_date', datetime.now().isoformat()),
                        'created_at': job.get('created_at', datetime.now().isoformat())
                    }
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"✅ Inserted {len(job_postings_data)} job postings into {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert job postings: {e}")
            return False
    
    def search_similar_skills(self, query_vector: List[float], top_k: int = 5, 
                            filter_conditions: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar skills"""
        collection_name = self._get_collection_name("skills")
        
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=self._build_filter(filter_conditions),
                with_payload=True,
                with_vectors=False
            )
            
            similar_skills = []
            for hit in search_result:
                similar_skills.append({
                    'skill_id': hit.payload.get('skill_id'),
                    'skill_name': hit.payload.get('skill_name'),
                    'category': hit.payload.get('category'),
                    'description': hit.payload.get('description'),
                    'popularity_score': hit.payload.get('popularity_score'),
                    'market_demand_score': hit.payload.get('market_demand_score'),
                    'score': hit.score
                })
            
            return similar_skills
            
        except Exception as e:
            logger.error(f"Failed to search similar skills: {e}")
            return []
    
    def search_similar_developers(self, query_vector: List[float], top_k: int = 5,
                                filter_conditions: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar developers"""
        collection_name = self._get_collection_name("developers")
        
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=self._build_filter(filter_conditions),
                with_payload=True,
                with_vectors=False
            )
            
            similar_developers = []
            for hit in search_result:
                similar_developers.append({
                    'developer_id': hit.payload.get('developer_id'),
                    'username': hit.payload.get('username'),
                    'name': hit.payload.get('name'),
                    'location': hit.payload.get('location'),
                    'company': hit.payload.get('company'),
                    'public_repos': hit.payload.get('public_repos'),
                    'followers': hit.payload.get('followers'),
                    'score': hit.score
                })
            
            return similar_developers
            
        except Exception as e:
            logger.error(f"Failed to search similar developers: {e}")
            return []
    
    def search_similar_repositories(self, query_vector: List[float], top_k: int = 5,
                                  filter_conditions: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar repositories"""
        collection_name = self._get_collection_name("repositories")
        
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=self._build_filter(filter_conditions),
                with_payload=True,
                with_vectors=False
            )
            
            similar_repos = []
            for hit in search_result:
                similar_repos.append({
                    'repository_id': hit.payload.get('repository_id'),
                    'name': hit.payload.get('name'),
                    'full_name': hit.payload.get('full_name'),
                    'description': hit.payload.get('description'),
                    'language': hit.payload.get('language'),
                    'stargazers_count': hit.payload.get('stargazers_count'),
                    'forks_count': hit.payload.get('forks_count'),
                    'score': hit.score
                })
            
            return similar_repos
            
        except Exception as e:
            logger.error(f"Failed to search similar repositories: {e}")
            return []
    
    def search_similar_career_paths(self, query_vector: List[float], top_k: int = 5,
                                  filter_conditions: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar career paths"""
        collection_name = self._get_collection_name("career_paths")
        
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=self._build_filter(filter_conditions),
                with_payload=True,
                with_vectors=False
            )
            
            similar_paths = []
            for hit in search_result:
                similar_paths.append({
                    'path_id': hit.payload.get('path_id'),
                    'path_name': hit.payload.get('path_name'),
                    'category': hit.payload.get('category'),
                    'description': hit.payload.get('description'),
                    'required_skills': hit.payload.get('required_skills', []),
                    'salary_range': hit.payload.get('salary_range'),
                    'growth_potential': hit.payload.get('growth_potential'),
                    'score': hit.score
                })
            
            return similar_paths
            
        except Exception as e:
            logger.error(f"Failed to search similar career paths: {e}")
            return []
    
    def search_similar_job_postings(self, query_vector: List[float], top_k: int = 5,
                                  filter_conditions: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar job postings"""
        collection_name = self._get_collection_name("job_postings")
        
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=self._build_filter(filter_conditions),
                with_payload=True,
                with_vectors=False
            )
            
            similar_jobs = []
            for hit in search_result:
                similar_jobs.append({
                    'job_id': hit.payload.get('job_id'),
                    'title': hit.payload.get('title'),
                    'company': hit.payload.get('company'),
                    'location': hit.payload.get('location'),
                    'description': hit.payload.get('description'),
                    'requirements': hit.payload.get('requirements'),
                    'salary_min': hit.payload.get('salary_min'),
                    'salary_max': hit.payload.get('salary_max'),
                    'job_type': hit.payload.get('job_type'),
                    'experience_level': hit.payload.get('experience_level'),
                    'remote_option': hit.payload.get('remote_option', False),
                    'data_source': hit.payload.get('data_source'),  # indeed
                    'posted_date': hit.payload.get('posted_date'),
                    'score': hit.score
                })
            
            return similar_jobs
            
        except Exception as e:
            logger.error(f"Failed to search similar job postings: {e}")
            return []
    
    def _build_filter(self, filter_conditions: Optional[Dict]) -> Optional[models.Filter]:
        """Build Qdrant filter from conditions"""
        if not filter_conditions:
            return None
        
        must_conditions = []
        
        for field, value in filter_conditions.items():
            if isinstance(value, str):
                must_conditions.append(
                    models.FieldCondition(
                        key=field,
                        match=models.MatchValue(value=value)
                    )
                )
            elif isinstance(value, list):
                must_conditions.append(
                    models.FieldCondition(
                        key=field,
                        match=models.MatchAny(any=value)
                    )
                )
            elif isinstance(value, dict):
                if 'min' in value and 'max' in value:
                    must_conditions.append(
                        models.FieldCondition(
                            key=field,
                            range=models.DatetimeRange(
                                gte=value['min'],
                                lte=value['max']
                            )
                        )
                    )
        
        return models.Filter(must=must_conditions) if must_conditions else None
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            collection_info = self.client.get_collection(collection_name)
            # Use points_count as vectors_count since vectors_count can be None
            vectors_count = collection_info.vectors_count if collection_info.vectors_count is not None else collection_info.points_count
            return {
                "name": collection_name,
                "vectors_count": vectors_count,
                "points_count": collection_info.points_count,
                "segments_count": collection_info.segments_count,
                "config": collection_info.config.dict()
            }
        except Exception as e:
            logger.error(f"Error getting collection stats for {collection_name}: {e}")
            return {}
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"✅ Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check Qdrant service health"""
        try:
            collections = self.list_collections()
            return {
                "status": "healthy",
                "is_cloud": self._is_cloud,
                "collections_count": len(collections),
                "collections": collections
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "is_cloud": self._is_cloud
            }


# Create a global instance of QdrantVectorClient
qdrant_client = QdrantVectorClient() 