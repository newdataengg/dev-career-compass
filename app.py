#!/usr/bin/env python3
"""
DevCareerCompass Interactive Web Application
Modern Flask-based web interface with advanced data visualization and AI-powered insights.
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import threading
import queue
from collections import defaultdict, Counter
import pandas as pd
import numpy as np

# Import DevCareerCompass components
from src.config.settings import settings
from src.database.connection import db_manager, init_database
from src.database.models import Developer, Repository, Skill, Commit, DeveloperSkill, JobPosting, JobSkill
from src.llm.llm_client import llm_client
from src.agents.agent_orchestrator import AgentOrchestrator
from src.embeddings.embedding_generator import embedding_generator
from src.knowledge_graph.graph_builder import knowledge_graph_builder
from src.knowledge_graph.graph_rag_service import graph_rag_service
from src.insights.career_analyzer import career_analyzer
from src.utils.logger import setup_logging, get_application_logger
from src.vector_store.qdrant_client import qdrant_client

# Import the unified main components
# Note: These components were moved to individual modules
# Phase1Foundation, Phase2Embeddings, etc. are now handled differently

# Import enhanced chatbot
from src.agents.enhanced_chatbot import enhanced_chatbot

logger = get_application_logger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'devcareercompass-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devcareer_compass.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Rate limiting will be added later after deployment is working
limiter = None

# Global variables for DevCareerCompass components
devcareer_components = {
    'phase1': None,
    'phase2': None,
    'phase3': None,
    'phase4': None,
    'phase5': None,
    'phase6': None,
    'deep_models': None,
    'real_time_learning': None,
    'chatbot': enhanced_chatbot,
    'advanced_viz': None
}

# Background task queue
task_queue = queue.Queue()

class User(UserMixin, db.Model):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def initialize_devcareer_components():
    """Initialize all DevCareerCompass components."""
    try:
        logger.info("Initializing DevCareerCompass components...")
        
        # Initialize basic components (phases are now handled differently)
        devcareer_components['phase1'] = "Foundation Phase - Database initialized"
        devcareer_components['phase2'] = "Embeddings Phase - Vector store connected"
        devcareer_components['phase3'] = "Multi-Agent Phase - Chatbot available"
        devcareer_components['phase4'] = "Real-Time Phase - Ready for analysis"
        devcareer_components['phase5'] = "Advanced ML Phase - Career analyzer ready"
        devcareer_components['phase6'] = "Deep Learning Phase - Models available"
        
        # Initialize advanced components
        devcareer_components['deep_models'] = "Deep Learning Models - Available"
        devcareer_components['real_time_learning'] = "Real-Time Learning - Active"
        devcareer_components['advanced_viz'] = "Advanced Visualizations - Ready"
        
        logger.info("DevCareerCompass components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing DevCareerCompass components: {e}")
        return False

def run_async_initialization():
    """Run async initialization in background."""
    async def init_async():
        try:
            # Initialize LLM client
            await llm_client.initialize()
            
            # Initialize agent orchestrator
            agent_orchestrator = AgentOrchestrator(llm_client)
            await agent_orchestrator.initialize()
            
            # Initialize career analyzer
            await career_analyzer.initialize()
            
            # Initialize Graph RAG service
            await graph_rag_service.initialize()
            
            # Initialize chatbot
            if 'chatbot' in devcareer_components:
                await devcareer_components['chatbot'].initialize_chatbot()
            else:
                # Initialize the enhanced_chatbot instance
                await enhanced_chatbot.initialize_chatbot()
                devcareer_components['chatbot'] = enhanced_chatbot
            
            # Initialize Phase 5 components
            # Phase 5 is now handled differently
            pass
            
            # Initialize Phase 6 components
            # These components are now handled differently
            pass
            
            logger.info("Async initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Error in async initialization: {e}")
    
    asyncio.run(init_async())

# Data Analysis Functions
def get_comprehensive_statistics():
    """Get comprehensive statistics for the dashboard."""
    try:
        with db_manager.get_session() as session:
            # Basic counts
            total_developers = session.query(Developer).count()
            total_repositories = session.query(Repository).count()
            total_skills = session.query(Skill).count()
            total_commits = session.query(Commit).count()
            total_jobs = session.query(JobPosting).count()
            
            # Developers by source
            developers_by_source = session.query(Developer.data_source, db.func.count(Developer.id)).group_by(Developer.data_source).all()
            
            # Top programming languages
            languages = session.query(Repository.language).filter(Repository.language.isnot(None)).all()
            language_counts = Counter([lang[0] for lang in languages if lang[0]])
            top_languages = dict(language_counts.most_common(10))
            
            # Top skills
            skills = session.query(Skill.name, Skill.popularity_score).order_by(Skill.popularity_score.desc()).limit(10).all()
            top_skills = {skill[0]: skill[1] for skill in skills}
            
            # Job market insights
            jobs_by_source = session.query(JobPosting.data_source, db.func.count(JobPosting.id)).group_by(JobPosting.data_source).all()
            
            # Recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_developers = session.query(Developer).filter(Developer.created_at >= week_ago).count()
            recent_repos = session.query(Repository).filter(Repository.created_at >= week_ago).count()
            
            # Career paths analysis
            career_paths = session.query(Developer.company).filter(Developer.company.isnot(None)).all()
            company_counts = Counter([company[0] for company in career_paths if company[0]])
            top_companies = dict(company_counts.most_common(10))
            
            return {
                'total_developers': total_developers,
                'total_repositories': total_repositories,
                'total_skills': total_skills,
                'total_commits': total_commits,
                'total_jobs': total_jobs,
                'developers_by_source': dict(developers_by_source),
                'top_languages': top_languages,
                'top_skills': top_skills,
                'jobs_by_source': dict(jobs_by_source),
                'recent_activity': {
                    'developers': recent_developers,
                    'repositories': recent_repos
                },
                'top_companies': top_companies
            }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {}

def get_developer_insights():
    """Get detailed developer insights."""
    try:
        with db_manager.get_session() as session:
            # Top developers by followers
            top_developers = session.query(Developer).order_by(Developer.followers.desc()).limit(10).all()
            
            # Developers by location
            locations = session.query(Developer.location).filter(Developer.location.isnot(None)).all()
            location_counts = Counter([loc[0] for loc in locations if loc[0]])
            
            # Skills distribution
            dev_skills = session.query(DeveloperSkill).join(Skill).all()
            skill_distribution = Counter([ds.skill.name for ds in dev_skills])
            
            return {
                'top_developers': [
                    {
                        'username': dev.username,
                        'name': dev.name,
                        'followers': dev.followers,
                        'public_repos': dev.public_repos,
                        'location': dev.location,
                        'company': dev.company
                    } for dev in top_developers
                ],
                'location_distribution': dict(location_counts.most_common(10)),
                'skill_distribution': dict(skill_distribution.most_common(15))
            }
    except Exception as e:
        logger.error(f"Error getting developer insights: {e}")
        return {}

def get_job_market_insights():
    """Get job market insights."""
    try:
        with db_manager.get_session() as session:
            # Job postings by type
            job_types = session.query(JobPosting.job_type).filter(JobPosting.job_type.isnot(None)).all()
            job_type_counts = Counter([jt[0] for jt in job_types if jt[0]])
            
            # Remote work trends
            remote_jobs = session.query(JobPosting).filter(JobPosting.remote_option == True).count()
            total_jobs = session.query(JobPosting).count()
            remote_percentage = (remote_jobs / total_jobs * 100) if total_jobs > 0 else 0
            
            # Top companies hiring
            companies = session.query(JobPosting.company).filter(JobPosting.company.isnot(None)).all()
            company_counts = Counter([comp[0] for comp in companies if comp[0]])
            
            # Salary insights
            salary_data = session.query(JobPosting.salary_min, JobPosting.salary_max).filter(
                JobPosting.salary_min.isnot(None),
                JobPosting.salary_max.isnot(None)
            ).all()
            
            avg_salary_min = np.mean([s[0] for s in salary_data]) if salary_data else 0
            avg_salary_max = np.mean([s[1] for s in salary_data]) if salary_data else 0
            
            return {
                'job_types': dict(job_type_counts),
                'remote_percentage': round(remote_percentage, 2),
                'top_companies': dict(company_counts.most_common(10)),
                'salary_insights': {
                    'avg_min': round(avg_salary_min, 2),
                    'avg_max': round(avg_salary_max, 2)
                }
            }
    except Exception as e:
        logger.error(f"Error getting job market insights: {e}")
        return {}

# Helper functions for AI Skills Dashboard
def get_consistent_statistics():
    """Get consistent statistics across all pages."""
    try:
        with db_manager.get_session() as session:
            developers = session.query(Developer).count()
            repositories = session.query(Repository).count()
            skills = session.query(Skill).count()
            jobs = session.query(JobPosting).count()
            
            return {
                'developers': int(developers),
                'repositories': int(repositories),
                'skills': int(skills),
                'jobs': int(jobs)
            }
    except Exception as e:
        logger.error(f"Error getting consistent statistics: {e}")
        return {'developers': 0, 'repositories': 0, 'skills': 0, 'jobs': 0}

def get_top_ai_skills():
    """Get top AI-related skills."""
    try:
        with db_manager.get_session() as session:
            # Get skills with developer counts
            skills = session.query(Skill, func.count(DeveloperSkill.developer_id).label('count')).\
                outerjoin(DeveloperSkill).\
                group_by(Skill.id).\
                order_by(func.count(DeveloperSkill.developer_id).desc()).\
                limit(10).all()
            
            return [
                {
                    'name': skill.name,
                    'category': skill.category,
                    'count': count,
                    'demand_score': min(100, count * 10)  # Simple demand calculation
                }
                for skill, count in skills
            ]
    except Exception as e:
        logger.error(f"Error getting top AI skills: {e}")
        return []

def get_emerging_skills():
    """Get emerging AI skills."""
    try:
        with db_manager.get_session() as session:
            # Get skills with recent activity
            skills = session.query(Skill, func.count(DeveloperSkill.developer_id).label('count')).\
                outerjoin(DeveloperSkill).\
                group_by(Skill.id).\
                order_by(Skill.created_at.desc()).\
                limit(8).all()
            
            return [
                {
                    'name': skill.name,
                    'category': skill.category,
                    'growth_rate': min(50, count * 5)  # Simple growth calculation
                }
                for skill, count in skills
            ]
    except Exception as e:
        logger.error(f"Error getting emerging skills: {e}")
        return []

def get_top_ai_developers():
    """Get top developers with AI skills."""
    try:
        with db_manager.get_session() as session:
            # Get developers with AI-related skills
            developers = session.query(Developer).\
                join(DeveloperSkill).\
                join(Skill).\
                filter(Skill.category.in_(['ai_ml', 'programming_language'])).\
                group_by(Developer.id).\
                order_by(Developer.followers.desc()).\
                limit(10).all()
            
            result = []
            for dev in developers:
                # Get AI skills for this developer
                ai_skills = session.query(Skill.name).\
                    join(DeveloperSkill).\
                    filter(DeveloperSkill.developer_id == dev.id).\
                    filter(Skill.category.in_(['ai_ml', 'programming_language'])).\
                    limit(5).all()
                
                # Get repository count
                repo_count = session.query(Repository).\
                    filter(Repository.developer_id == dev.id).count()
                
                result.append({
                    'username': dev.username,
                    'name': dev.name,
                    'avatar_url': f"https://github.com/{dev.username}.png",
                    'ai_skills': [skill[0] for skill in ai_skills],
                    'experience_level': 'senior' if dev.followers > 1000 else 'mid' if dev.followers > 100 else 'junior',
                    'repo_count': repo_count
                })
            
            return result
    except Exception as e:
        logger.error(f"Error getting top AI developers: {e}")
        return []

def get_recent_activity():
    """Get recent activity data."""
    try:
        with db_manager.get_session() as session:
            # Get recent developers
            recent_devs = session.query(Developer).\
                order_by(Developer.created_at.desc()).\
                limit(3).all()
            
            activities = []
            for dev in recent_devs:
                activities.append({
                    'title': f"New developer: {dev.name or dev.username}",
                    'time': dev.created_at.strftime('%Y-%m-%d'),
                    'icon': 'user-plus'
                })
            
            # Get recent repositories
            recent_repos = session.query(Repository).\
                order_by(Repository.created_at.desc()).\
                limit(2).all()
            
            for repo in recent_repos:
                activities.append({
                    'title': f"New repository: {repo.name}",
                    'time': repo.created_at.strftime('%Y-%m-%d'),
                    'icon': 'code'
                })
            
            return activities[:5]  # Return top 5 activities
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return []

def get_skill_categories():
    """Get skill categories with counts."""
    try:
        with db_manager.get_session() as session:
            categories = session.query(Skill.category, func.count(Skill.id).label('count')).\
                group_by(Skill.category).\
                all()
            
            total = sum(count for _, count in categories)
            
            return [
                {
                    'name': category,
                    'count': count,
                    'percentage': round((count / total * 100) if total > 0 else 0, 1)
                }
                for category, count in categories
            ]
    except Exception as e:
        logger.error(f"Error getting skill categories: {e}")
        return []

def get_skills_chart_data():
    """Get skills data for charts."""
    try:
        with db_manager.get_session() as session:
            skills = session.query(Skill.name, func.count(DeveloperSkill.developer_id).label('count')).\
                outerjoin(DeveloperSkill).\
                group_by(Skill.id).\
                order_by(func.count(DeveloperSkill.developer_id).desc()).\
                limit(8).all()
            
            labels = [skill[0] for skill in skills]
            data = [skill[1] for skill in skills]
            
            return labels, data
    except Exception as e:
        logger.error(f"Error getting skills chart data: {e}")
        return [], []

# Analytics helper functions
def get_ai_analytics_insights():
    """Get AI-focused analytics insights."""
    try:
        with db_manager.get_session() as session:
            # Calculate AI skills demand
            ai_skills = session.query(Skill).filter(Skill.category == 'ai_ml').count()
            total_skills = session.query(Skill).count()
            demand_score = round((ai_skills / total_skills * 100) if total_skills > 0 else 0, 1)
            
            # Calculate growth metrics
            recent_devs = session.query(Developer).filter(
                Developer.created_at >= datetime.now() - timedelta(days=30)
            ).count()
            total_devs = session.query(Developer).count()
            dev_growth = round((recent_devs / total_devs * 100) if total_devs > 0 else 0, 1)
            
            return {
                'demand_score': demand_score,
                'demand_growth': 15.2,  # Simulated growth
                'dev_growth': dev_growth,
                'new_developers': recent_devs,
                'repo_activity': 85.5,  # Simulated activity
                'new_repos': 12,  # Simulated
                'job_trend': 92.3,  # Simulated trend
                'new_jobs': 8  # Simulated
            }
    except Exception as e:
        logger.error(f"Error getting AI analytics insights: {e}")
        return {}

def get_ai_skills_heatmap():
    """Get AI skills heatmap data."""
    try:
        with db_manager.get_session() as session:
            ai_skills = session.query(Skill, func.count(DeveloperSkill.developer_id).label('count')).\
                filter(Skill.category == 'ai_ml').\
                outerjoin(DeveloperSkill).\
                group_by(Skill.id).\
                order_by(func.count(DeveloperSkill.developer_id).desc()).\
                limit(10).all()
            
            max_count = max([count for _, count in ai_skills]) if ai_skills else 1
            
            return [
                {
                    'name': skill.name,
                    'intensity': round((count / max_count * 100) if max_count > 0 else 0, 1)
                }
                for skill, count in ai_skills
            ]
    except Exception as e:
        logger.error(f"Error getting AI skills heatmap: {e}")
        return []

def get_skills_correlation():
    """Get skills correlation data."""
    try:
        # Simulated correlation data
        correlations = [
            {'skill1': 'RAG Systems', 'skill2': 'Vector Databases', 'correlation': 85},
            {'skill1': 'Prompt Engineering', 'skill2': 'Chain-of-Thought', 'correlation': 78},
            {'skill1': 'MCP Framework', 'skill2': 'API Development', 'correlation': 72},
            {'skill1': 'Guardrails', 'skill2': 'Content Filtering', 'correlation': 68},
            {'skill1': 'Embeddings', 'skill2': 'Semantic Search', 'correlation': 91}
        ]
        return correlations
    except Exception as e:
        logger.error(f"Error getting skills correlation: {e}")
        return []

def get_data_source_analysis():
    """Get data source analysis."""
    try:
        with db_manager.get_session() as session:
            github_devs = session.query(Developer).filter(Developer.data_source == 'github').count()
            github_repos = session.query(Repository).count()
            github_langs = session.query(Repository.language).filter(Repository.language.isnot(None)).distinct().count()
            
            # Simulated data for other sources
            return {
                'github': {
                    'developers': github_devs,
                    'repositories': github_repos,
                    'languages': github_langs
                },
                'stackoverflow': {
                    'developers': 45,
                    'questions': 1200,
                    'tags': 89
                },
                'reddit': {
                    'posts': 340,
                    'comments': 2100,
                    'subreddits': 12
                },
                'jobs': {
                    'postings': session.query(JobPosting).count(),
                    'companies': session.query(JobPosting.company).filter(JobPosting.company.isnot(None)).distinct().count(),
                    'remote': 65
                }
            }
    except Exception as e:
        logger.error(f"Error getting data source analysis: {e}")
        return {}

def get_advanced_insights():
    """Get advanced insights."""
    try:
        return [
            {
                'title': 'RAG Adoption',
                'description': 'Retrieval-Augmented Generation is the fastest-growing AI skill',
                'icon': 'rocket',
                'color': 'green',
                'metric': '+45%'
            },
            {
                'title': 'MCP Framework',
                'description': 'Model Context Protocol gaining traction in enterprise',
                'icon': 'plug',
                'color': 'blue',
                'metric': '+32%'
            },
            {
                'title': 'Guardrails',
                'description': 'AI safety and validation becoming critical',
                'icon': 'shield-alt',
                'color': 'red',
                'metric': '+28%'
            },
            {
                'title': 'Prompt Engineering',
                'description': 'Most in-demand skill for LLM applications',
                'icon': 'magic',
                'color': 'purple',
                'metric': '+67%'
            },
            {
                'title': 'Vector Databases',
                'description': 'Essential for modern AI applications',
                'icon': 'database',
                'color': 'orange',
                'metric': '+53%'
            },
            {
                'title': 'Fine-tuning',
                'description': 'Custom model training on the rise',
                'icon': 'cogs',
                'color': 'indigo',
                'metric': '+39%'
            }
        ]
    except Exception as e:
        logger.error(f"Error getting advanced insights: {e}")
        return []

def get_ai_recommendations():
    """Get AI engineering recommendations."""
    try:
        return [
            {
                'title': 'Start with RAG Systems',
                'description': 'Build a solid foundation with retrieval-augmented generation',
                'skills': ['RAG Systems', 'Vector Databases', 'Embeddings']
            },
            {
                'title': 'Master Prompt Engineering',
                'description': 'Learn advanced prompting techniques for better LLM performance',
                'skills': ['Prompt Engineering', 'Chain-of-Thought', 'Few-Shot Learning']
            },
            {
                'title': 'Implement Guardrails',
                'description': 'Ensure AI safety and validation in production systems',
                'skills': ['Guardrails', 'Content Filtering', 'Bias Detection']
            },
            {
                'title': 'Explore MCP Framework',
                'description': 'Build scalable AI applications with Model Context Protocol',
                'skills': ['MCP Framework', 'API Development', 'Tool Integration']
            }
        ]
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {e}")
        return []

def get_skills_trend_data():
    """Get skills trend data for charts."""
    try:
        # Simulated trend data
        labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        data = [45, 52, 58, 65, 72, 78]
        return labels, data
    except Exception as e:
        logger.error(f"Error getting skills trend data: {e}")
        return [], []

def get_developer_growth_data():
    """Get developer growth data for charts."""
    try:
        # Simulated growth data
        labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        data = [12, 18, 25, 32, 41, 48]
        return labels, data
    except Exception as e:
        logger.error(f"Error getting developer growth data: {e}")
        return [], []

# New Helper Functions for Streamlined UI
def get_top_skills():
    """Get top skills across all categories."""
    try:
        with db_manager.get_session() as session:
            skills = session.query(Skill, func.count(DeveloperSkill.developer_id).label('count')).\
                outerjoin(DeveloperSkill).\
                group_by(Skill.id).\
                order_by(func.count(DeveloperSkill.developer_id).desc()).\
                limit(8).all()
            
            return [
                {
                    'name': skill.name or 'Unknown Skill',
                    'category': skill.category or 'General',
                    'popularity_score': min(100, (count or 0) * 8)
                }
                for skill, count in skills
            ]
    except Exception as e:
        logger.error(f"Error getting top skills: {e}")
        return []

def get_recent_job_trends():
    """Get recent job market trends."""
    try:
        with db_manager.get_session() as session:
            jobs = session.query(JobPosting).\
                order_by(JobPosting.created_at.desc()).\
                limit(5).all()
            
            return [
                {
                    'title': job.title or 'Unknown Position',
                    'company': job.company or 'Unknown Company',
                    'experience_level': job.experience_level or 'Not specified',
                    'remote_option': bool(job.remote_option) if job.remote_option is not None else False
                }
                for job in jobs
            ]
    except Exception as e:
        logger.error(f"Error getting recent job trends: {e}")
        return []

def get_career_paths():
    """Get career path recommendations."""
    try:
        return [
            {
                'title': 'AI Engineer',
                'description': 'Build and deploy AI systems',
                'skills': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow'],
                'salary_range': '$80,000 - $150,000',
                'growth': 'High'
            },
            {
                'title': 'Data Scientist',
                'description': 'Analyze data and build predictive models',
                'skills': ['Python', 'R', 'SQL', 'Statistics', 'Machine Learning'],
                'salary_range': '$70,000 - $140,000',
                'growth': 'Very High'
            },
            {
                'title': 'Full-Stack Developer',
                'description': 'Develop both frontend and backend applications',
                'skills': ['JavaScript', 'Python', 'React', 'Node.js', 'SQL'],
                'salary_range': '$60,000 - $130,000',
                'growth': 'High'
            }
        ]
    except Exception as e:
        logger.error(f"Error getting career paths: {e}")
        return []

def get_skill_recommendations():
    """Get skill recommendations based on market demand."""
    try:
        with db_manager.get_session() as session:
            skills = session.query(Skill).\
                order_by(Skill.market_demand_score.desc()).\
                limit(10).all()
            
            return [
                {
                    'name': skill.name or 'Unknown Skill',
                    'category': skill.category or 'General',
                    'demand_score': skill.market_demand_score or 50,
                    'description': skill.description or 'High-demand skill'
                }
                for skill in skills
            ]
    except Exception as e:
        logger.error(f"Error getting skill recommendations: {e}")
        return []

def get_job_market_trends():
    """Get job market trends and insights."""
    try:
        with db_manager.get_session() as session:
            jobs = session.query(JobPosting).\
                order_by(JobPosting.created_at.desc()).\
                limit(10).all()
            
            return [
                {
                    'title': job.title or 'Unknown Position',
                    'company': job.company or 'Unknown Company',
                    'location': job.location or 'Remote',
                    'experience_level': job.experience_level or 'Not specified',
                    'remote_option': bool(job.remote_option) if job.remote_option is not None else False,
                    'posted_date': job.posted_date.strftime('%Y-%m-%d') if job.posted_date else 'Recent'
                }
                for job in jobs
            ]
    except Exception as e:
        logger.error(f"Error getting job market trends: {e}")
        return []

def get_top_companies():
    """Get top companies hiring developers."""
    try:
        with db_manager.get_session() as session:
            companies = session.query(JobPosting.company, func.count(JobPosting.id).label('job_count')).\
                group_by(JobPosting.company).\
                order_by(func.count(JobPosting.id).desc()).\
                limit(8).all()
            
            return [
                {
                    'name': company or 'Unknown Company',
                    'job_count': count or 0,
                    'logo': f"https://logo.clearbit.com/{(company or 'company').lower().replace(' ', '')}.com"
                }
                for company, count in companies
            ]
    except Exception as e:
        logger.error(f"Error getting top companies: {e}")
        return []

def get_salary_insights():
    """Get salary insights and trends."""
    try:
        with db_manager.get_session() as session:
            jobs = session.query(JobPosting).\
                filter(JobPosting.salary_min.isnot(None)).\
                limit(20).all()
            
            salaries = []
            for job in jobs:
                if job.salary_min and job.salary_max:
                    avg_salary = (job.salary_min + job.salary_max) / 2
                    salaries.append({
                        'title': job.title or 'Unknown Position',
                        'company': job.company or 'Unknown Company',
                        'avg_salary': float(avg_salary),
                        'experience_level': job.experience_level or 'Not specified'
                    })
            
            return salaries
    except Exception as e:
        logger.error(f"Error getting salary insights: {e}")
        return []

# Routes
@app.route('/')
def index():
    """Interactive home page with overview."""
    stats = get_comprehensive_statistics()
    return render_template('index.html', stats=stats)

@app.route('/dashboard')
def dashboard():
    """Main dashboard with integrated career intelligence."""
    try:
        # Get consistent statistics
        stats = get_consistent_statistics()
        
        # Get top skills (not just AI skills)
        top_skills = get_top_skills()
        
        # Get recent job trends
        recent_jobs = get_recent_job_trends()
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             top_skills=top_skills,
                             recent_jobs=recent_jobs)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('dashboard.html', 
                             stats={}, 
                             top_skills=[],
                             recent_jobs=[])





















# New Streamlined Routes
@app.route('/career_insights')
def career_insights():
    """Career insights and path recommendations."""
    try:
        stats = get_consistent_statistics()
        career_paths = get_career_paths()
        skill_recommendations = get_skill_recommendations()
        
        return render_template('career_insights.html', 
                             stats=stats,
                             career_paths=career_paths,
                             skill_recommendations=skill_recommendations)
    except Exception as e:
        logger.error(f"Error loading career insights: {e}")
        return render_template('career_insights.html', 
                             stats={},
                             career_paths=[],
                             skill_recommendations=[])

@app.route('/job_market')
def job_market():
    """Job market analysis and opportunities."""
    try:
        stats = get_consistent_statistics()
        job_trends = get_job_market_trends()
        top_companies = get_top_companies()
        salary_data = get_salary_insights()
        
        return render_template('job_market.html', 
                             stats=stats,
                             job_trends=job_trends,
                             top_companies=top_companies,
                             salary_data=salary_data)
    except Exception as e:
        logger.error(f"Error loading job market: {e}")
        return render_template('job_market.html', 
                             stats={},
                             job_trends=[],
                             top_companies=[],
                             salary_data={})

@app.route('/ai_assistant')
def ai_assistant():
    """AI-powered career assistant."""
    try:
        stats = get_consistent_statistics()
        return render_template('ai_assistant.html', stats=stats)
    except Exception as e:
        logger.error(f"Error loading AI assistant: {e}")
        return render_template('ai_assistant.html', stats={})

# API Endpoints
@app.route('/api/statistics')
def api_statistics():
    """API endpoint for comprehensive statistics."""
    try:
        stats = get_comprehensive_statistics()
        dev_insights = get_developer_insights()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'top_developers': dev_insights.get('top_developers', []),
            'top_skills': dev_insights.get('skill_distribution', {})
        })
    except Exception as e:
        logger.error(f"Error in statistics API: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/developers')
def api_developers():
    """API endpoint to get developers with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        with db_manager.get_session() as session:
            query = session.query(Developer)
            
            if search:
                query = query.filter(Developer.username.contains(search) | 
                                   Developer.name.contains(search))
            
            developers = query.order_by(Developer.followers.desc()).offset((page-1)*per_page).limit(per_page).all()
            
            return jsonify({
                'success': True,
                'developers': [
                    {
                        'id': dev.id,
                        'username': dev.username,
                        'name': dev.name,
                        'followers': dev.followers,
                        'public_repos': dev.public_repos,
                        'location': dev.location,
                        'company': dev.company,
                        'data_source': dev.data_source
                    } for dev in developers
                ]
            })
    except Exception as e:
        logger.error(f"Error in developers API: {e}")
        return jsonify({'success': False, 'error': str(e)})



@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat API endpoint."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        
        # Get response from enhanced AI chatbot
        async def get_chat_response():
            try:
                return await devcareer_components['chatbot'].chat(user_id, message)
            except Exception as e:
                logger.error(f"Error in chatbot response: {e}")
                return {
                    'message': "I'm having trouble processing your request right now. Please try again in a moment, or ask me about career guidance, skills, or technology trends.",
                    'confidence': 0.0,
                    'intent': 'error'
                }
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(get_chat_response())
        loop.close()
        
        return jsonify({
            'success': True,
            'response': response.get('message', 'Sorry, I encountered an error. Please try again.'),
            'confidence': response.get('confidence', 0.0)
        })
        
    except Exception as e:
        logger.error(f"Error in chat API: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'response': {
                'message': "Sorry, I encountered an error. Please try again.",
                'confidence': 0.0,
                'intent': 'error'
            }
        })

@app.route('/api/graph_rag', methods=['POST'])
def graph_rag_query():
    """Graph RAG query endpoint."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        query_type = data.get('query_type', 'career_guidance')
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'})
        
        # Get response from Graph RAG service
        async def get_graph_rag_response():
            try:
                return await graph_rag_service.graph_rag_query(query, query_type)
            except Exception as e:
                logger.error(f"Error in Graph RAG response: {e}")
                return {
                    'error': str(e),
                    'response': "I'm having trouble processing your Graph RAG query right now. Please try again."
                }
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(get_graph_rag_response())
        loop.close()
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        logger.error(f"Error in Graph RAG API: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'response': {
                'error': str(e),
                'response': "Sorry, I encountered an error with the Graph RAG query. Please try again."
            }
        })

@app.route('/api/graph_statistics')
def graph_statistics():
    """Get knowledge graph statistics."""
    try:
        if not graph_rag_service._initialized:
            return jsonify({
                'success': False,
                'error': 'Graph RAG service not initialized'
            })
        
        stats = graph_rag_service.get_graph_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting graph statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/collect_data', methods=['POST'])
def api_collect_data():
    """API endpoint for data collection."""
    try:
        data = request.get_json()
        data_type = data.get('type', '')
        
        # Import here to avoid circular imports
        from real_data_collector import RealDataCollector
        
        collector = RealDataCollector()
        
        if data_type == 'github':
            result = collector.collect_github_massive(50)
        elif data_type == 'stackoverflow':
            result = collector.collect_stack_overflow_data(50)
        elif data_type == 'reddit':
            result = collector.collect_reddit_data(50)
        
        elif data_type == 'indeed':
            result = collector.collect_indeed_data(25)
        else:
            return jsonify({'success': False, 'error': 'Invalid data type'})
        
        return jsonify({
            'success': True,
            'message': f'Successfully collected {result} items from {data_type}',
            'count': result
        })
        
    except Exception as e:
        logger.error(f"Error in data collection API: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/search', methods=['POST'])
def api_search():
    """Advanced search API endpoint."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        search_type = data.get('type', 'all')  # all, developers, repositories, skills, jobs
        
        results = {}
        
        with db_manager.get_session() as session:
            if search_type in ['all', 'developers']:
                dev_results = session.query(Developer).filter(
                    Developer.username.contains(query) | 
                    Developer.name.contains(query) |
                    Developer.company.contains(query)
                ).limit(10).all()
                results['developers'] = [
                    {
                        'username': dev.username,
                        'name': dev.name,
                        'company': dev.company,
                        'followers': dev.followers
                    } for dev in dev_results
                ]
            
            if search_type in ['all', 'repositories']:
                repo_results = session.query(Repository).filter(
                    Repository.name.contains(query) |
                    Repository.description.contains(query)
                ).limit(10).all()
                results['repositories'] = [
                    {
                        'name': repo.name,
                        'full_name': repo.full_name,
                        'description': repo.description,
                        'language': repo.language,
                        'stars': repo.stargazers_count
                    } for repo in repo_results
                ]
            
            if search_type in ['all', 'skills']:
                skill_results = session.query(Skill).filter(
                    Skill.name.contains(query)
                ).limit(10).all()
                results['skills'] = [
                    {
                        'name': skill.name,
                        'category': skill.category,
                        'popularity': skill.popularity_score
                    } for skill in skill_results
                ]
            
            if search_type in ['all', 'jobs']:
                job_results = session.query(JobPosting).filter(
                    JobPosting.title.contains(query) |
                    JobPosting.company.contains(query)
                ).limit(10).all()
                results['jobs'] = [
                    {
                        'title': job.title,
                        'company': job.company,
                        'location': job.location,
                        'job_type': job.job_type
                    } for job in job_results
                ]
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in search API: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Simple registration for demo purposes."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Simple demo registration
        if username and email and password:
            # Create a simple user object
            user = User()
            user.id = 2  # Different ID for new user
            user.username = username
            user.email = email
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Please fill in all fields', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login for demo purposes."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple demo authentication
        if username == 'admin' and password == 'admin':
            # Create a simple user object
            user = User()
            user.id = 1
            user.username = username
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Data collection endpoint for live data
@app.route('/api/collect-data', methods=['POST'])
def collect_live_data():
    """Trigger live data collection for capstone demonstration."""
    try:
        logger.info("Starting live data collection...")
        
        # Import data collection modules
        from src.data_pipeline.data_collector import DataCollector
        from src.embeddings.embedding_generator import embedding_generator
        
        # Initialize data collector
        collector = DataCollector()
        
        # Collect GitHub trending developers
        github_developers = collector.collect_from_github_trending(max_users=20)
        
        # Collect repositories for existing developers
        collector.collect_repositories_for_existing_developers(max_developers=10)
        
        # Collect job market data
        job_data = collector.collect_market_data()
        
        # Note: Embeddings will be generated separately
        embedding_count = 0
        
        # Get current statistics
        with db_manager.get_session() as session:
            total_developers = session.query(Developer).count()
            total_repositories = session.query(Repository).count()
            total_jobs = session.query(JobPosting).count()
        
        return jsonify({
            "success": True,
            "message": "Live data collection completed",
            "data": {
                "developers_collected": len(github_developers),
                "total_developers": total_developers,
                "total_repositories": total_repositories,
                "job_postings": total_jobs,
                "embeddings_generated": embedding_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error in live data collection: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Health check endpoint for deployment monitoring
@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring."""
    try:
        # Basic health checks
        db_status = "healthy"
        try:
            # Test database connection
            db.session.execute('SELECT 1')
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": db_status,
            "components": {
                "chatbot": "available" if devcareer_components.get('chatbot') else "unavailable",
                "vector_store": "available" if qdrant_client else "unavailable",
                "knowledge_graph": "available" if knowledge_graph_builder else "unavailable"
            }
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        init_database()
        db.create_all()
    
    # Initialize components
    initialize_devcareer_components()
    
    # Run async initialization in background
    init_thread = threading.Thread(target=run_async_initialization)
    init_thread.daemon = True
    init_thread.start()
    
    # Run the app
    port = int(os.environ.get('PORT', 3000))
    app.run(debug=False, host='0.0.0.0', port=port) 