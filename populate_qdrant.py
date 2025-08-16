#!/usr/bin/env python3
"""
Script to populate Qdrant collections with sample data for RAG functionality
"""

import os
import sys
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.vector_store.qdrant_client import QdrantVectorClient
from src.embeddings.embedding_generator import embedding_generator
from src.database.connection import db_manager
from src.database.models import Developer, Repository, Skill, JobPosting
from src.utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

def populate_qdrant_collections():
    """Populate Qdrant collections with sample data"""
    
    print("🔧 Populating Qdrant collections...")
    
    # Initialize Qdrant client
    qdrant_client = QdrantVectorClient()
    
    # Initialize embedding generator
    embedding_gen = embedding_generator
    
    try:
        # Create collections if they don't exist
        print("📦 Creating collections...")
        qdrant_client.create_skills_collection()
        qdrant_client.create_developers_collection()
        qdrant_client.create_repositories_collection()
        qdrant_client.create_job_postings_collection()
        
        # Get data from database
        with db_manager.get_session() as session:
            print("📊 Loading data from database...")
            
            # Get skills
            skills = session.query(Skill).limit(50).all()
            print(f"Found {len(skills)} skills")
            
            # Get developers
            developers = session.query(Developer).limit(20).all()
            print(f"Found {len(developers)} developers")
            
            # Get repositories
            repositories = session.query(Repository).limit(30).all()
            print(f"Found {len(repositories)} repositories")
            
            # Get job postings
            job_postings = session.query(JobPosting).limit(25).all()
            print(f"Found {len(job_postings)} job postings")
            
            # Convert to dictionaries to avoid session issues
            skills_data = []
            for skill in skills:
                skills_data.append({
                    'id': skill.id,
                    'name': skill.name,
                    'category': skill.category or 'general',
                    'description': skill.description or ''
                })
            
            developers_data = []
            for dev in developers:
                developers_data.append({
                    'id': dev.id,
                    'github_id': dev.github_id or '',
                    'username': dev.username,
                    'name': dev.name or '',
                    'email': dev.email or '',
                    'bio': dev.bio or '',
                    'location': dev.location or '',
                    'company': dev.company or '',
                    'public_repos': dev.public_repos or 0,
                    'followers': dev.followers or 0,
                    'following': dev.following or 0,
                    'created_at': dev.created_at.isoformat() if dev.created_at else datetime.now().isoformat()
                })
            
            repositories_data = []
            for repo in repositories:
                repositories_data.append({
                    'id': repo.id,
                    'github_id': repo.github_id or '',
                    'name': repo.name,
                    'full_name': repo.full_name or '',
                    'description': repo.description or '',
                    'language': repo.language or '',
                    'languages': repo.languages or {},
                    'topics': repo.topics or [],
                    'stargazers_count': repo.stargazers_count or 0,
                    'forks_count': repo.forks_count or 0,
                    'created_at': repo.created_at.isoformat() if repo.created_at else datetime.now().isoformat()
                })
            
            job_postings_data = []
            for job in job_postings:
                job_postings_data.append({
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'description': job.description or '',
                    'requirements': job.requirements or '',
                    'salary_min': job.salary_min or 0,
                    'salary_max': job.salary_max or 0,
                    'job_type': job.job_type or '',
                    'experience_level': job.experience_level or '',
                    'remote_option': job.remote_option or False,
                    'data_source': job.data_source or 'indeed',
                    'posted_date': job.posted_date.isoformat() if job.posted_date else datetime.now().isoformat()
                })
        
        # Prepare skills data
        if skills_data:
            print("🔧 Preparing skills data...")
            qdrant_skills_data = []
            for skill in skills_data:
                try:
                    # Generate embedding
                    embedding = embedding_gen._hash_based_embedding(skill['name'], 384)
                    qdrant_skills_data.append({
                        'id': skill['id'],
                        'vector': embedding.tolist(),
                        'name': skill['name'],
                        'category': skill['category'],
                        'description': skill['description'],
                        'popularity_score': np.random.uniform(0.1, 1.0),
                        'market_demand_score': np.random.uniform(0.1, 1.0),
                        'created_at': datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error processing skill {skill['name']}: {e}")
            
            if qdrant_skills_data:
                qdrant_client.insert_skills(qdrant_skills_data)
                print(f"✅ Inserted {len(qdrant_skills_data)} skills")
        
        # Prepare developers data
        if developers_data:
            print("👥 Preparing developers data...")
            qdrant_developers_data = []
            for dev in developers_data:
                try:
                    # Create text representation
                    dev_text = f"{dev['username']} {dev['name']} {dev['bio']} {dev['location']} {dev['company']}"
                    embedding = embedding_gen._hash_based_embedding(dev_text, 384)
                    qdrant_developers_data.append({
                        'id': dev['id'],
                        'vector': embedding.tolist(),
                        'github_id': dev['github_id'],
                        'username': dev['username'],
                        'name': dev['name'],
                        'email': dev['email'],
                        'bio': dev['bio'],
                        'location': dev['location'],
                        'company': dev['company'],
                        'public_repos': dev['public_repos'],
                        'followers': dev['followers'],
                        'following': dev['following'],
                        'created_at': dev['created_at']
                    })
                except Exception as e:
                    logger.error(f"Error processing developer {dev['username']}: {e}")
            
            if qdrant_developers_data:
                qdrant_client.insert_developers(qdrant_developers_data)
                print(f"✅ Inserted {len(qdrant_developers_data)} developers")
        
        # Prepare repositories data
        if repositories_data:
            print("📁 Preparing repositories data...")
            qdrant_repos_data = []
            for repo in repositories_data:
                try:
                    # Create text representation
                    repo_text = f"{repo['name']} {repo['description']} {repo['language']} {' '.join(repo['topics'])}"
                    embedding = embedding_gen._hash_based_embedding(repo_text, 384)
                    qdrant_repos_data.append({
                        'id': repo['id'],
                        'vector': embedding.tolist(),
                        'github_id': repo['github_id'],
                        'name': repo['name'],
                        'full_name': repo['full_name'],
                        'description': repo['description'],
                        'language': repo['language'],
                        'languages': repo['languages'],
                        'topics': repo['topics'],
                        'stargazers_count': repo['stargazers_count'],
                        'forks_count': repo['forks_count'],
                        'created_at': repo['created_at']
                    })
                except Exception as e:
                    logger.error(f"Error processing repository {repo['name']}: {e}")
            
            if qdrant_repos_data:
                qdrant_client.insert_repositories(qdrant_repos_data)
                print(f"✅ Inserted {len(qdrant_repos_data)} repositories")
        
        # Prepare job postings data
        if job_postings_data:
            print("💼 Preparing job postings data...")
            qdrant_jobs_data = []
            for job in job_postings_data:
                try:
                    # Create text representation
                    job_text = f"{job['title']} {job['company']} {job['location']} {job['description']}"
                    embedding = embedding_gen._hash_based_embedding(job_text, 384)
                    qdrant_jobs_data.append({
                        'id': job['id'],
                        'vector': embedding.tolist(),
                        'job_id': job['id'],
                        'title': job['title'],
                        'company': job['company'],
                        'location': job['location'],
                        'description': job['description'],
                        'requirements': job['requirements'],
                        'salary_min': job['salary_min'],
                        'salary_max': job['salary_max'],
                        'job_type': job['job_type'],
                        'experience_level': job['experience_level'],
                        'remote_option': job['remote_option'],
                        'data_source': job['data_source'],
                        'posted_date': job['posted_date']
                    })
                except Exception as e:
                    logger.error(f"Error processing job {job['title']}: {e}")
            
            if qdrant_jobs_data:
                qdrant_client.insert_job_postings(qdrant_jobs_data)
                print(f"✅ Inserted {len(qdrant_jobs_data)} job postings")
        
        print("🎉 Qdrant collections populated successfully!")
        print("\n📊 Summary:")
        print(f"   • Skills: {len(qdrant_skills_data) if 'qdrant_skills_data' in locals() else 0}")
        print(f"   • Developers: {len(qdrant_developers_data) if 'qdrant_developers_data' in locals() else 0}")
        print(f"   • Repositories: {len(qdrant_repos_data) if 'qdrant_repos_data' in locals() else 0}")
        print(f"   • Job Postings: {len(qdrant_jobs_data) if 'qdrant_jobs_data' in locals() else 0}")
        
    except Exception as e:
        logger.error(f"Error populating Qdrant collections: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    populate_qdrant_collections() 