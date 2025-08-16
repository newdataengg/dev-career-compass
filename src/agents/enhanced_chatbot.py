#!/usr/bin/env python3
"""
Enhanced AI Chatbot for DevCareerCompass
Uses vector search, career analysis, and real data for intelligent responses
"""

import asyncio
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.vector_store.qdrant_client import QdrantVectorClient
from src.embeddings.embedding_generator import embedding_generator
from src.database.connection import db_manager
from src.database.models import Developer, Skill, Repository, JobPosting, JobSkill
from src.llm.llm_client import llm_client
from src.knowledge_graph.graph_rag_service import graph_rag_service
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class EnhancedAIChatbot:
    """Enhanced AI chatbot with vector search and career analysis capabilities."""
    
    def __init__(self):
        self.conversation_history = {}
        self.qdrant_client = None
        self.embedding_generator = None
        self.graph_rag_service = None
        self._initialized = False
        
        # Career paths with detailed information
        self.career_paths = {
            'full stack developer': {
                'description': 'Develops both frontend and backend applications',
                'required_skills': ['JavaScript', 'Python', 'React', 'Node.js', 'SQL', 'Git'],
                'salary_range': '$70,000 - $150,000',
                'growth_potential': 'High',
                'category': 'Web Development',
                'learning_path': [
                    'Learn HTML, CSS, and JavaScript fundamentals',
                    'Master a frontend framework (React, Vue, or Angular)',
                    'Learn backend development with Node.js or Python',
                    'Understand databases and SQL',
                    'Learn version control with Git',
                    'Practice building full-stack projects'
                ]
            },
            'data scientist': {
                'description': 'Analyzes data and builds machine learning models',
                'required_skills': ['Python', 'R', 'SQL', 'Machine Learning', 'Statistics', 'Pandas'],
                'salary_range': '$80,000 - $160,000',
                'growth_potential': 'Very High',
                'category': 'Data Science',
                'learning_path': [
                    'Learn Python programming fundamentals',
                    'Master data manipulation with Pandas and NumPy',
                    'Study statistics and probability',
                    'Learn machine learning algorithms',
                    'Practice with real datasets',
                    'Learn data visualization tools'
                ]
            },
            'devops engineer': {
                'description': 'Manages infrastructure and deployment pipelines',
                'required_skills': ['Linux', 'Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Python'],
                'salary_range': '$75,000 - $140,000',
                'growth_potential': 'High',
                'category': 'Infrastructure',
                'learning_path': [
                    'Learn Linux system administration',
                    'Master containerization with Docker',
                    'Learn cloud platforms (AWS, Azure, GCP)',
                    'Understand CI/CD pipelines',
                    'Learn infrastructure as code',
                    'Practice with real deployment scenarios'
                ]
            },
            'frontend developer': {
                'description': 'Builds user interfaces and client-side applications',
                'required_skills': ['HTML', 'CSS', 'JavaScript', 'React', 'TypeScript', 'Webpack'],
                'salary_range': '$60,000 - $130,000',
                'growth_potential': 'High',
                'category': 'Web Development',
                'learning_path': [
                    'Master HTML and CSS fundamentals',
                    'Learn JavaScript ES6+ features',
                    'Study a frontend framework (React, Vue, Angular)',
                    'Learn TypeScript for type safety',
                    'Understand build tools and bundlers',
                    'Practice responsive design and accessibility'
                ]
            },
            'backend developer': {
                'description': 'Develops server-side applications and APIs',
                'required_skills': ['Python', 'Java', 'Node.js', 'SQL', 'REST APIs', 'Microservices'],
                'salary_range': '$70,000 - $140,000',
                'growth_potential': 'High',
                'category': 'Web Development',
                'learning_path': [
                    'Learn a backend language (Python, Java, or Node.js)',
                    'Master database design and SQL',
                    'Learn REST API development',
                    'Understand authentication and security',
                    'Study microservices architecture',
                    'Practice building scalable applications'
                ]
            }
        }
    
    async def initialize_chatbot(self):
        """Initialize the enhanced chatbot."""
        logger.info("Initializing Enhanced AI Chatbot...")
        
        try:
            # Initialize Qdrant client
            self.qdrant_client = QdrantVectorClient()
            self.embedding_generator = embedding_generator
            
            # Initialize LLM client
            try:
                self.llm_client = llm_client
                logger.info("✅ LLM client initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ LLM client initialization failed: {e}")
                self.llm_client = None
            
            # Initialize Graph RAG service
            self.graph_rag_service = graph_rag_service
            await self.graph_rag_service.initialize()
            
            # Test vector search connection
            health = self.qdrant_client.health_check()
            logger.info(f"Qdrant status: {health['status']}, Collections: {len(health.get('collections', []))}")
            
            # Test Graph RAG service
            graph_stats = self.graph_rag_service.get_graph_statistics()
            logger.info(f"Graph RAG initialized: {graph_stats.get('total_nodes', 0)} nodes, {graph_stats.get('total_edges', 0)} edges")
            
            # Test database connection
            with db_manager.get_session() as session:
                # Developer statistics by source
                github_devs = session.query(Developer).filter(Developer.data_source == 'github').count()
                stackoverflow_devs = session.query(Developer).filter(Developer.data_source == 'stackoverflow').count()
                reddit_devs = session.query(Developer).filter(Developer.data_source == 'reddit').count()
                total_devs = session.query(Developer).count()
                
                # Skill statistics
                skill_count = session.query(Skill).count()
                
                # Job posting statistics
    
                indeed_jobs = session.query(JobPosting).filter(JobPosting.data_source == 'indeed').count()
                total_jobs = session.query(JobPosting).count()
                
                logger.info(f"Database connected: {total_devs} developers ({github_devs} GitHub, {stackoverflow_devs} Stack Overflow, {reddit_devs} Reddit), {skill_count} skills, {total_jobs} job postings ({indeed_jobs} Indeed)")
            
            self._initialized = True
            logger.info("✅ Enhanced AI Chatbot initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced AI Chatbot: {e}")
            self._initialized = False
            return False
    
    async def chat(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process a chat message and return a response."""
        try:
            # Initialize conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Add user message to history
            self.conversation_history[user_id].append({
                'role': 'user',
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Generate response
            response = await self._generate_intelligent_response(user_id, message)
            
            # Add assistant response to history
            self.conversation_history[user_id].append({
                'role': 'assistant',
                'message': response['message'],
                'timestamp': datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return {
                'message': "I'm experiencing technical difficulties. Please try again in a moment.",
                'type': 'error',
                'confidence': 0.3
            }
    
    async def _generate_intelligent_response(self, user_id: str, message: str) -> Dict[str, Any]:
        """Generate intelligent response using vector search and career analysis."""
        message_lower = message.lower()
        
        # Handle general skill questions FIRST (before greetings to avoid conflicts)
        skill_keywords = ['skill', 'technology', 'learn', 'programming', 'language', 'skills do i need', 'what skills', 'which skills', 'skills are', 'skills in', 'high demand', 'demand']
        if any(keyword in message_lower for keyword in skill_keywords):
            return await self._handle_skill_question(message)
        
        # Handle greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            logger.info("Message matched greeting keywords")
            return await self._handle_greeting()
        
        # Check for repository queries FIRST
        repository_keywords = ['repository', 'repo', 'github', 'gitlab', 'bitbucket', 'project', 'codebase']
        if any(keyword in message_lower for keyword in repository_keywords):
            return await self._handle_repository_question(message)
        
        # Check for specific skill queries
        specific_skills = ['python', 'javascript', 'java', 'react', 'node.js', 'sql', 'docker', 'kubernetes', 'aws', 'git', 'html', 'css', 'typescript', 'vue', 'angular', 'mongodb', 'postgresql', 'redis', 'nginx', 'linux', 'bash', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'jupyter']
        
        # Check if the query is asking about a specific skill
        if any(skill in message_lower for skill in specific_skills):
            # Look for skill-specific query patterns
            skill_query_patterns = [
                'tell me about', 'what is', 'explain', 'details on', 'more details on',
                'how to use', 'learn', 'information about', 'guide to'
            ]
            
            if any(pattern in message_lower for pattern in skill_query_patterns):
                return await self._handle_specific_skill_question(message)
        
        # Handle developer queries FIRST (before career queries to avoid conflicts)
        developer_keywords = ['developer', 'programmer', 'coder', 'who is', 'find developers', 'popular developer', 'most popular', 'developers working on', 'developers who', 'find developers', 'working on']
        if any(keyword in message_lower for keyword in developer_keywords):
            return await self._handle_developer_question(message)
        
        # Handle salary questions FIRST (before career queries to avoid conflicts)
        salary_keywords = ['salary', 'pay', 'money', 'earn', 'income', 'compensation', 'wage']
        salary_indicators = ['what\'s the salary', 'how much', 'salary for', 'pay for', 'earn as']
        
        if any(word in message_lower for word in salary_keywords) or any(indicator in message_lower for indicator in salary_indicators):
            return await self._handle_salary_question(message)
        
        # Handle career path questions (excluding developer, salary, and skill queries)
        career_keywords = ['career', 'role', 'path', 'data science', 'data scientist']
        
        if any(word in message_lower for word in career_keywords):
            return await self._handle_career_question(message)
        

        
        # Handle job posting questions (before career queries)
        job_keywords = ['job posting', 'job listing', 'job opening', 'hiring', 'recruitment', 'job market', 'employment', 'jobs in', 'positions in', 'job opportunities']
        if any(keyword in message_lower for keyword in job_keywords):
            return await self._handle_job_question(message)
        
        # Handle learning path questions
        if any(word in message_lower for word in ['learn', 'study', 'course', 'tutorial', 'roadmap']):
            return await self._handle_learning_question(message)
        
        # Handle AI-specific questions (before general career queries)
        ai_keywords = ['ai engineer', 'artificial intelligence', 'machine learning engineer', 'ml engineer', 'ai developer', 'ai engineering', 'ai trends', 'ai trend', 'latest ai', 'ai technology', 'ai developments', 'ai news', 'ai updates']
        if any(keyword in message_lower for keyword in ai_keywords):
            return await self._handle_ai_question(message)
        
        # Handle specific technology questions
        if any(word in message_lower for word in ['python', 'javascript', 'react', 'node', 'sql', 'docker']):
            return await self._handle_technology_question(message)
        
        # Try Graph RAG for complex queries
        if self.graph_rag_service and self.graph_rag_service._initialized:
            try:
                # Determine query type based on content
                query_type = self._determine_query_type(message)
                graph_rag_response = await self.graph_rag_service.graph_rag_query(message, query_type)
                
                if graph_rag_response and 'response' in graph_rag_response and not graph_rag_response.get('error'):
                    return {
                        'message': graph_rag_response['response'],
                        'type': 'graph_rag_response',
                        'confidence': graph_rag_response.get('confidence', 0.8),
                        'graph_insights': graph_rag_response.get('graph_insights', {}),
                        'career_paths': graph_rag_response.get('career_paths', {})
                    }
            except Exception as e:
                logger.error(f"Graph RAG query failed: {e}")
        
        # Default response with suggestions
        return await self._handle_general_question(message)
    
    async def _handle_greeting(self) -> Dict[str, Any]:
        """Handle greeting messages."""
        greeting = (
            "Hello! I'm your AI career assistant powered by DevCareerCompass. "
            "I can help you with:\n\n"
            "🎯 **Career Guidance**: Explore different developer roles and paths\n"
            "💡 **Skill Analysis**: Get personalized skill recommendations\n"
            "💰 **Salary Insights**: Understand market compensation\n"
            "📚 **Learning Paths**: Get step-by-step learning roadmaps\n"
            "🔍 **Technology Trends**: Stay updated with industry insights\n\n"
            "What would you like to know about your developer career?"
        )
        
        return {
            'message': greeting,
            'type': 'greeting',
            'confidence': 0.95
        }
    
    async def _handle_career_question(self, message: str) -> Dict[str, Any]:
        """Handle career-related questions using vector search."""
        try:
            message_lower = message.lower()
            
            # Check for specific career path queries
            career_keywords = {
                'full stack': 'Full Stack Developer',
                'fullstack': 'Full Stack Developer',
                'frontend': 'Frontend Developer',
                'front end': 'Frontend Developer',
                'backend': 'Backend Developer',
                'back end': 'Backend Developer',
                'data scientist': 'Data Scientist',
                'data science': 'Data Scientist',
                'machine learning': 'Data Scientist',
                'ml': 'Data Scientist',
                'ai': 'Data Scientist',
                'devops': 'DevOps Engineer',
                'dev ops': 'DevOps Engineer'
            }
            
            # Check for career path keywords
            for keyword, career_path in career_keywords.items():
                if keyword in message_lower:
                    if career_path.lower() in self.career_paths:
                        return await self._provide_career_details(career_path, self.career_paths[career_path.lower()])
            
            # Special handling for data science skill queries
            if any(term in message_lower for term in ['data science', 'data scientist', 'machine learning', 'ml', 'ai']):
                if 'skill' in message_lower or 'need' in message_lower:
                    return await self._handle_data_science_skills()
            
            # Check for specific career paths
            for career_path, details in self.career_paths.items():
                if career_path.lower() in message_lower:
                    return await self._provide_career_details(career_path.title(), details)
            
            # Use vector search if available
            if self._initialized and self.qdrant_client:
                try:
                    # Generate embedding for the query using hash-based method
                    query_embedding = self.embedding_generator._hash_based_embedding(message, 384).tolist()
                    similar_careers = self.qdrant_client.search_similar_career_paths(query_embedding, top_k=3)
                    
                    if similar_careers:
                        career_list = "\n".join([f"• **{career['path_name']}**" for career in similar_careers])
                        response = (
                            f"Based on your query, here are some relevant career paths:\n\n{career_list}\n\n"
                            "Would you like me to provide detailed information about any specific role? "
                            "Just ask about the career path you're interested in!"
                        )
                    else:
                        response = (
                            "I can help you explore various developer career paths! Here are some popular options:\n\n"
                            "• **Full Stack Developer** - Build complete web applications\n"
                            "• **Data Scientist** - Analyze data and build ML models\n"
                            "• **DevOps Engineer** - Manage infrastructure and deployment\n"
                            "• **Frontend Developer** - Create user interfaces\n"
                            "• **Backend Developer** - Build server-side applications\n\n"
                            "Which career path interests you most?"
                        )
                except Exception as e:
                    logger.error(f"Vector search error: {e}")
                    response = (
                        "I can help you explore various developer career paths! Here are some popular options:\n\n"
                        "• **Full Stack Developer** - Build complete web applications\n"
                        "• **Data Scientist** - Analyze data and build ML models\n"
                        "• **DevOps Engineer** - Manage infrastructure and deployment\n"
                        "• **Frontend Developer** - Create user interfaces\n"
                        "• **Backend Developer** - Build server-side applications\n\n"
                        "Which career path interests you most?"
                    )
            else:
                response = (
                    "I can help you explore various developer career paths! Here are some popular options:\n\n"
                    "• **Full Stack Developer** - Build complete web applications\n"
                    "• **Data Scientist** - Analyze data and build ML models\n"
                    "• **DevOps Engineer** - Manage infrastructure and deployment\n"
                    "• **Frontend Developer** - Create user interfaces\n"
                    "• **Backend Developer** - Build server-side applications\n\n"
                    "Which career path interests you most?"
                )
            
            return {
                'message': response,
                'type': 'career_exploration',
                'confidence': 0.9
            }
            
        except Exception as e:
            logger.error(f"Error in career question handling: {e}")
            return {
                'message': "I can help you explore different developer career paths. Popular options include Full Stack Developer, Data Scientist, DevOps Engineer, Frontend Developer, and Backend Developer. Which one interests you?",
                'type': 'career_exploration',
                'confidence': 0.8
            }
    
    async def _provide_career_details(self, career_path: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Provide detailed information about a specific career path."""
        response = (
            f"## {career_path.title()} Career Path\n\n"
            f"**Description**: {details['description']}\n\n"
            f"**Key Skills**: {', '.join(details['required_skills'])}\n\n"
            f"**Salary Range**: {details['salary_range']}\n\n"
            f"**Growth Potential**: {details['growth_potential']}\n\n"
            f"**Category**: {details['category']}\n\n"
            f"**Learning Path**:\n"
            f"1. Master the core skills: {', '.join(details['required_skills'][:3])}\n"
            f"2. Build projects to demonstrate your expertise\n"
            f"3. Contribute to open source projects\n"
            f"4. Network with professionals in the field\n"
            f"5. Stay updated with industry trends\n\n"
            f"Would you like me to provide more specific information about any of these skills or help you create a personalized learning plan?"
        )
        
        return {
            'message': response,
            'type': 'career_details',
            'confidence': 0.95,
            'career_path': career_path
        }
    
    async def _handle_data_science_skills(self) -> Dict[str, Any]:
        """Provide specific information about data science skills."""
        response = (
            "## Data Science Skills You Need\n\n"
            "**Core Programming Skills**:\n"
            "• **Python** - Primary language for data science\n"
            "• **R** - Statistical computing and graphics\n"
            "• **SQL** - Database querying and data manipulation\n\n"
            "**Data Manipulation & Analysis**:\n"
            "• **Pandas** - Data manipulation and analysis\n"
            "• **NumPy** - Numerical computing\n"
            "• **Matplotlib/Seaborn** - Data visualization\n\n"
            "**Machine Learning**:\n"
            "• **Scikit-learn** - Traditional ML algorithms\n"
            "• **TensorFlow/PyTorch** - Deep learning frameworks\n"
            "• **Jupyter Notebooks** - Interactive development\n\n"
            "**Statistics & Mathematics**:\n"
            "• **Statistical Analysis** - Hypothesis testing, regression\n"
            "• **Probability** - Understanding uncertainty\n"
            "• **Linear Algebra** - Matrix operations for ML\n\n"
            "**Tools & Platforms**:\n"
            "• **Git** - Version control\n"
            "• **Docker** - Containerization\n"
            "• **Cloud Platforms** - AWS, Google Cloud, Azure\n\n"
            "Would you like me to provide a learning roadmap for any of these skills?"
        )
        
        return {
            'message': response,
            'type': 'skill_recommendation',
            'confidence': 0.95
        }
    
    async def _handle_specific_skill_question(self, message: str) -> Dict[str, Any]:
        """Handle queries about specific skills/technologies."""
        message_lower = message.lower()
        
        # Skill information database
        skill_info = {
            'python': {
                'name': 'Python',
                'category': 'Programming Language',
                'description': 'A high-level, interpreted programming language known for its simplicity and readability.',
                'use_cases': ['Web Development', 'Data Science', 'Machine Learning', 'Automation', 'Scientific Computing'],
                'difficulty': 'Beginner-friendly',
                'learning_time': '2-6 months for basics',
                'resources': ['Python.org official tutorial', 'Codecademy Python course', 'Real Python tutorials'],
                'career_applications': ['Software Developer', 'Data Scientist', 'DevOps Engineer', 'Web Developer'],
                'market_demand': 'Very High',
                'salary_impact': '+15-25%'
            },
            'javascript': {
                'name': 'JavaScript',
                'category': 'Programming Language',
                'description': 'A versatile programming language primarily used for web development, both frontend and backend.',
                'use_cases': ['Web Development', 'Mobile Apps', 'Server-side Development', 'Game Development'],
                'difficulty': 'Moderate',
                'learning_time': '3-8 months for proficiency',
                'resources': ['MDN Web Docs', 'Eloquent JavaScript', 'JavaScript.info'],
                'career_applications': ['Frontend Developer', 'Full Stack Developer', 'Web Developer', 'Mobile Developer'],
                'market_demand': 'Very High',
                'salary_impact': '+20-30%'
            },
            'react': {
                'name': 'React',
                'category': 'Frontend Framework',
                'description': 'A JavaScript library for building user interfaces, particularly single-page applications.',
                'use_cases': ['Web Applications', 'Mobile Apps (React Native)', 'Progressive Web Apps'],
                'difficulty': 'Moderate',
                'learning_time': '2-4 months',
                'resources': ['React official docs', 'React Tutorial', 'Create React App'],
                'career_applications': ['Frontend Developer', 'React Developer', 'Full Stack Developer'],
                'market_demand': 'Very High',
                'salary_impact': '+25-35%'
            },
            'sql': {
                'name': 'SQL',
                'category': 'Database Language',
                'description': 'Structured Query Language for managing and manipulating relational databases.',
                'use_cases': ['Database Management', 'Data Analysis', 'Business Intelligence', 'Backend Development'],
                'difficulty': 'Beginner-friendly',
                'learning_time': '1-3 months',
                'resources': ['SQL Tutorial', 'W3Schools SQL', 'Mode Analytics SQL Tutorial'],
                'career_applications': ['Data Analyst', 'Database Administrator', 'Backend Developer', 'Data Scientist'],
                'market_demand': 'High',
                'salary_impact': '+10-20%'
            },
            'docker': {
                'name': 'Docker',
                'category': 'Containerization',
                'description': 'A platform for developing, shipping, and running applications in containers.',
                'use_cases': ['Application Deployment', 'Microservices', 'DevOps', 'Development Environment'],
                'difficulty': 'Moderate',
                'learning_time': '2-4 months',
                'resources': ['Docker official docs', 'Docker Tutorial', 'Docker Hub'],
                'career_applications': ['DevOps Engineer', 'Site Reliability Engineer', 'Backend Developer'],
                'market_demand': 'Very High',
                'salary_impact': '+20-30%'
            }
        }
        
        # Find the skill being asked about
        for skill_key, skill_data in skill_info.items():
            if skill_key in message_lower:
                response = (
                    f"## {skill_data['name']} - {skill_data['category']}\n\n"
                    f"**Description**: {skill_data['description']}\n\n"
                    f"**Primary Use Cases**:\n"
                    f"• {', '.join(skill_data['use_cases'])}\n\n"
                    f"**Learning Difficulty**: {skill_data['difficulty']}\n"
                    f"**Time to Learn**: {skill_data['learning_time']}\n\n"
                    f"**Career Applications**:\n"
                    f"• {', '.join(skill_data['career_applications'])}\n\n"
                    f"**Market Demand**: {skill_data['market_demand']}\n"
                    f"**Salary Impact**: {skill_data['salary_impact']}\n\n"
                    f"**Recommended Learning Resources**:\n"
                    f"• {', '.join(skill_data['resources'])}\n\n"
                    f"Would you like me to provide a learning roadmap for {skill_data['name']} or explain how it fits into specific career paths?"
                )
                
                return {
                    'message': response,
                    'type': 'skill_details',
                    'confidence': 0.95,
                    'skill': skill_data['name']
                }
        
        # Fallback for skills not in our database
        return await self._handle_skill_question(message)
    
    async def _handle_general_repository_info(self) -> Dict[str, Any]:
        """Handle general repository information queries."""
        response = (
            "## Repository Information\n\n"
            "**What is a Repository?**\n"
            "A repository (or 'repo') is a storage location for software projects, typically containing:\n"
            "• Source code files\n"
            "• Documentation\n"
            "• Configuration files\n"
            "• README files\n"
            "• License information\n\n"
            "**Popular Repository Platforms**:\n"
            "• **GitHub** - Most popular, great for open source\n"
            "• **GitLab** - Comprehensive DevOps platform\n"
            "• **Bitbucket** - Good for team collaboration\n"
            "• **Azure DevOps** - Microsoft's solution\n\n"
            "**Repository Types**:\n"
            "• **Public** - Open to everyone\n"
            "• **Private** - Restricted access\n"
            "• **Fork** - Copy of another repository\n"
            "• **Template** - Reusable project structure\n\n"
            "Would you like me to:\n"
            "• Explain how to create a repository?\n"
            "• Show you how to contribute to open source?\n"
            "• Help you understand repository structure?\n"
            "• Find specific repositories for learning?"
        )
        
        return {
            'message': response,
            'type': 'repository_info',
            'confidence': 0.9
        }
    
    async def _handle_repository_question(self, message: str) -> Dict[str, Any]:
        """Handle queries about repositories and codebases."""
        message_lower = message.lower()
        
        try:
            # Check if it's asking about a specific repository
            if any(word in message_lower for word in ['mojombo']):
                return await self._handle_specific_repository_query(message)
            
            # Check for general repository questions
            if any(word in message_lower for word in ['what is', 'explain', 'tell me about']):
                return await self._handle_general_repository_info()
            
            # Default to repository search
            return await self._handle_specific_repository_query(message)
            
        except Exception as e:
            logger.error(f"Error in repository question handling: {e}")
            return await self._handle_general_question(message)
    
    async def _handle_specific_repository_query(self, message: str) -> Dict[str, Any]:
        """Handle queries about specific repositories like 'mojombo'."""
        message_lower = message.lower()
        
        # Check for specific repository names
        if 'mojombo' in message_lower:
            response = (
                "## Repository: mojombo\n\n"
                "**About mojombo**:\n"
                "This appears to be a reference to Tom Preston-Werner (GitHub username: mojombo), "
                "one of GitHub's co-founders and creators of Jekyll.\n\n"
                "**Notable Contributions**:\n"
                "• **Jekyll** - Static site generator\n"
                "• **GitHub** - Co-founder and former CEO\n"
                "• **Gravatar** - Global avatar service\n"
                "• **Semantic Versioning** - Version numbering system\n\n"
                "**Learning Opportunities**:\n"
                "• Study Jekyll for static site generation\n"
                "• Learn about semantic versioning (semver)\n"
                "• Explore GitHub's open source projects\n"
                "• Understand modern web development practices\n\n"
                "**Related Skills**:\n"
                "• Ruby (Jekyll is built with Ruby)\n"
                "• Static site generation\n"
                "• Open source contribution\n"
                "• Web development\n\n"
                "Would you like me to provide more details about any of these topics or help you find similar repositories to learn from?"
            )
            
            return {
                'message': response,
                'type': 'repository_details',
                'confidence': 0.95,
                'repository': 'mojombo'
            }
        
        # Generic repository search response
        response = (
            "## Repository Search\n\n"
            "I can help you find and understand repositories! Here are some ways to explore:\n\n"
            "**Popular Repository Categories**:\n"
            "• **Learning Projects** - Tutorials and examples\n"
            "• **Open Source Libraries** - Reusable code\n"
            "• **Full-Stack Applications** - Complete projects\n"
            "• **API Examples** - Backend implementations\n"
            "• **Frontend Frameworks** - UI/UX projects\n\n"
            "**How to Find Good Repositories**:\n"
            "1. **GitHub Trending** - See what's popular\n"
            "2. **GitHub Topics** - Browse by technology\n"
            "3. **Awesome Lists** - Curated collections\n"
            "4. **GitHub Stars** - Highly-rated projects\n\n"
            "**Repository Analysis**:\n"
            "• Check README files for documentation\n"
            "• Look at commit history for activity\n"
            "• Review issues and pull requests\n"
            "• Examine the tech stack used\n\n"
            "What type of repository are you looking for? I can help you find relevant examples!"
        )
        
        return {
            'message': response,
            'type': 'repository_search',
            'confidence': 0.9
        }
    
    async def _handle_developer_question(self, message: str) -> Dict[str, Any]:
        """Handle queries about developers and programmers."""
        message_lower = message.lower()
        
        try:
            # Check for specific developer queries
            if any(word in message_lower for word in ['who is', 'find developers', 'popular developer']):
                return await self._handle_developer_search(message)
            
            # General developer information
            response = (
                "## Developer Information\n\n"
                "**What is a Developer?**\n"
                "A developer (or programmer) is someone who writes code to create software applications, websites, and systems.\n\n"
                "**Types of Developers**:\n"
                "• **Frontend Developer** - Builds user interfaces\n"
                "• **Backend Developer** - Creates server-side logic\n"
                "• **Full Stack Developer** - Works on both frontend and backend\n"
                "• **Mobile Developer** - Creates mobile applications\n"
                "• **DevOps Engineer** - Manages infrastructure and deployment\n"
                "• **Data Scientist** - Analyzes data and builds ML models\n\n"
                "**Essential Skills**:\n"
                "• Programming languages (Python, JavaScript, Java, etc.)\n"
                "• Version control (Git)\n"
                "• Problem-solving abilities\n"
                "• Collaboration and communication\n"
                "• Continuous learning mindset\n\n"
                "**Career Path**:\n"
                "1. **Junior Developer** - Entry level, learning and growing\n"
                "2. **Mid-level Developer** - More responsibility, mentoring others\n"
                "3. **Senior Developer** - Technical leadership, architecture decisions\n"
                "4. **Lead Developer** - Team management, project planning\n"
                "5. **Technical Architect** - System design, technology strategy\n\n"
                "Would you like me to:\n"
                "• Show you how to become a developer?\n"
                "• Find specific developers in our database?\n"
                "• Explain different developer roles?\n"
                "• Help you choose a development path?"
            )
            
            return {
                'message': response,
                'type': 'developer_info',
                'confidence': 0.9
            }
            
        except Exception as e:
            logger.error(f"Error in developer question handling: {e}")
            return await self._handle_general_question(message)
    
    async def _handle_developer_search(self, message: str) -> Dict[str, Any]:
        """Handle specific developer search queries using RAG system."""
        message_lower = message.lower()
        
        try:
            # Use vector search if available
            if self._initialized and self.qdrant_client:
                # Generate embedding for the query
                query_embedding = self.embedding_generator._hash_based_embedding(message, 384).tolist()
                similar_developers = self.qdrant_client.search_similar_developers(query_embedding, top_k=5)
                
                if similar_developers:
                    response = "## Developers Found\n\n"
                    response += f"Based on your query, here are relevant developers:\n\n"
                    
                    for i, dev in enumerate(similar_developers, 1):
                        response += (
                            f"**{i}. {dev.get('name', dev.get('username', 'Unknown'))}**\n"
                            f"• Username: @{dev.get('username', 'N/A')}\n"
                            f"• Location: {dev.get('location', 'Not specified')}\n"
                            f"• Company: {dev.get('company', 'Not specified')}\n"
                            f"• Public Repos: {dev.get('public_repos', 0)}\n"
                            f"• Followers: {dev.get('followers', 0):,}\n"
                            f"• Match Score: {dev.get('score', 0):.2f}\n\n"
                        )
                    
                    response += "Would you like me to provide more details about any of these developers or help you find developers with specific skills?"
                    
                    return {
                        'message': response,
                        'type': 'developer_search',
                        'confidence': 0.95,
                        'developers_found': len(similar_developers)
                    }
            
            # Fallback to database search
            with db_manager.get_session() as session:
                total_developers = session.query(Developer).count()
                top_developers_query = session.query(Developer).order_by(Developer.followers.desc()).limit(5).all()
                
                # Convert to dictionaries within session context to avoid session binding issues
                top_developers = []
                for dev in top_developers_query:
                    top_developers.append({
                        'name': dev.name,
                        'username': dev.username,
                        'followers': dev.followers,
                        'public_repos': dev.public_repos,
                        'location': dev.location,
                        'company': dev.company
                    })
            
            if 'popular' in message_lower or 'most popular' in message_lower:
                response = (
                    "## Most Popular Developers\n\n"
                    f"Based on our database of {total_developers} developers:\n\n"
                )
                
                for i, dev in enumerate(top_developers, 1):
                    response += (
                        f"**{i}. {dev['name'] or dev['username']}**\n"
                        f"• Username: @{dev['username']}\n"
                        f"• Followers: {dev['followers']:,}\n"
                        f"• Public Repos: {dev['public_repos']}\n"
                        f"• Location: {dev['location'] or 'Not specified'}\n"
                        f"• Company: {dev['company'] or 'Not specified'}\n\n"
                    )
                
                response += "Would you like me to provide more details about any of these developers or help you find developers with specific skills?"
                
                return {
                    'message': response,
                    'type': 'developer_search',
                    'confidence': 0.95
                }
            
            # Generic developer search response
            response = (
                "## Developer Search\n\n"
                f"Our database contains information about {total_developers} developers.\n\n"
                "**Search Options**:\n"
                "• **By Skills** - Find developers who know specific technologies\n"
                "• **By Location** - Find developers in specific regions\n"
                "• **By Company** - Find developers working at specific companies\n"
                "• **By Popularity** - Find the most followed developers\n"
                "• **By Activity** - Find developers with many repositories\n\n"
                "**Popular Search Examples**:\n"
                "• 'Find developers who know Python'\n"
                "• 'Show me developers in San Francisco'\n"
                "• 'Who are the top developers at Google?'\n"
                "• 'Find React developers'\n\n"
                "What type of developer are you looking for?"
            )
            
            return {
                'message': response,
                'type': 'developer_search',
                'confidence': 0.9
            }
            
        except Exception as e:
            logger.error(f"Error in developer search: {e}")
            return await self._handle_general_question(message)
    
    async def _handle_skill_question(self, message: str) -> Dict[str, Any]:
        """Handle skill-related questions using RAG with vector search and LLM."""
        try:
            # Use RAG system with vector search and LLM
            if self._initialized and self.qdrant_client and self.llm_client:
                try:
                    # Generate embedding for the query
                    query_embedding = self.embedding_generator._hash_based_embedding(message, 384).tolist()
                    
                    # Search for similar skills, jobs, and career paths
                    similar_skills = self.qdrant_client.search_similar_skills(query_embedding, top_k=8)
                    similar_jobs = self.qdrant_client.search_similar_job_postings(query_embedding, top_k=5)
                    similar_careers = self.qdrant_client.search_similar_career_paths(query_embedding, top_k=3)
                    
                    # Build context from retrieved data
                    context_parts = []
                    
                    if similar_skills:
                        skill_info = []
                        for skill in similar_skills:
                            skill_info.append(f"• {skill['skill_name']} (Market Demand: {skill.get('market_demand_score', 'N/A')}, Popularity: {skill.get('popularity_score', 'N/A')})")
                        context_parts.append(f"**High-Demand Skills:**\n" + "\n".join(skill_info))
                    
                    if similar_jobs:
                        job_info = []
                        for job in similar_jobs:
                            salary_info = ""
                            if job.get('salary_min') and job.get('salary_max'):
                                salary_info = f" (Salary: ${job['salary_min']:,}-${job['salary_max']:,})"
                            job_info.append(f"• {job['title']} at {job['company']}{salary_info}")
                        context_parts.append(f"**Related Job Postings:**\n" + "\n".join(job_info))
                    
                    if similar_careers:
                        career_info = []
                        for career in similar_careers:
                            career_info.append(f"• {career['path_name']} - {career.get('description', 'Career path')}")
                        context_parts.append(f"**Career Paths:**\n" + "\n".join(career_info))
                    
                    # Create comprehensive context
                    context = "\n\n".join(context_parts)
                    
                    # Generate LLM response with context
                    prompt = f"""
You are an expert career advisor specializing in technology skills and career development. 
Based on the following real data from job market, skills database, and career paths, provide a comprehensive and natural answer to the user's question.

User Question: {message}

Context Data:
{context}

Please provide a detailed, conversational response that includes:
1. A clear analysis of high-demand skills based on the data
2. Market insights about these skills and why they're valuable
3. Career opportunities and typical salary ranges
4. Specific learning recommendations and resources
5. Future trends and how to stay competitive

Write in a natural, conversational tone as if you're speaking directly to the user. Use markdown formatting for better readability. Make sure your response is at least 200 words and provides actionable insights.
"""
                    
                    # Generate response using LLM
                    llm_response = await self.llm_client.generate_text(prompt)
                    
                    if llm_response and len(llm_response.strip()) > 100 and not llm_response.strip().startswith('{'):
                        response = llm_response
                        confidence = 0.9
                    else:
                        # Fallback to structured response
                        response = self._generate_structured_skill_response(similar_skills, similar_jobs, similar_careers)
                        confidence = 0.85
                        
                except Exception as e:
                    logger.error(f"RAG system error: {e}")
                    # Fallback to database search
                    response = await self._fallback_skill_response()
                    confidence = 0.7
            else:
                # Fallback to database search
                response = await self._fallback_skill_response()
                confidence = 0.7
            
            return {
                'message': response,
                'type': 'skill_recommendation',
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error in skill question handling: {e}")
            return {
                'message': "I can help you understand different programming skills and technologies. Popular skills include Python, JavaScript, React, Node.js, SQL, and Docker. Which skill would you like to learn more about?",
                'type': 'skill_general',
                'confidence': 0.7
            }
    
    def _generate_structured_skill_response(self, similar_skills, similar_jobs, similar_careers):
        """Generate a structured response when LLM is not available."""
        response_parts = []
        
        if similar_skills:
            skill_list = "\n".join([
                f"• **{skill['skill_name']}** (Market Demand: {skill.get('market_demand_score', 'N/A')})"
                for skill in similar_skills[:5]
            ])
            response_parts.append(f"## 🎯 High-Demand Skills\n\n{skill_list}")
        
        if similar_jobs:
            job_list = "\n".join([
                f"• **{job['title']}** at {job['company']}"
                for job in similar_jobs[:3]
            ])
            response_parts.append(f"## 💼 Related Job Opportunities\n\n{job_list}")
        
        if similar_careers:
            career_list = "\n".join([
                f"• **{career['path_name']}** - {career.get('description', 'Career path')}"
                for career in similar_careers[:3]
            ])
            response_parts.append(f"## 🚀 Career Paths\n\n{career_list}")
        
        response_parts.append("\n## 📚 Learning Recommendations\n\nBased on current market trends, I recommend focusing on skills that combine technical expertise with practical applications. Consider building projects that showcase these skills and stay updated with industry developments.")
        
        return "\n\n".join(response_parts)
    
    async def _fallback_skill_response(self):
        """Fallback response when RAG system is not available."""
        try:
            with db_manager.get_session() as session:
                # Get top skills by market demand
                skills_query = session.query(Skill).order_by(Skill.market_demand_score.desc()).limit(8).all()
                skill_names = [skill.name for skill in skills_query]
            
            if skill_names:
                skill_list = "\n".join([f"• **{skill}**" for skill in skill_names])
                return f"""## 🎯 High-Demand Skills in 2024

Based on our database analysis, here are the most in-demand skills:

{skill_list}

## 💡 Recommendations

1. **Focus on Fundamentals**: Master core programming concepts
2. **Build Projects**: Create portfolio-worthy applications
3. **Stay Updated**: Follow industry trends and new technologies
4. **Network**: Connect with professionals in your target field

Would you like detailed information about any specific skill or career path?"""
            else:
                return "I can help you understand different programming skills and technologies. Popular skills include Python, JavaScript, React, Node.js, SQL, and Docker. Which skill would you like to learn more about?"
        except Exception as e:
            logger.error(f"Error in fallback skill response: {e}")
            return "I can help you understand different programming skills and technologies. Popular skills include Python, JavaScript, React, Node.js, SQL, and Docker. Which skill would you like to learn more about?"
    
    async def _handle_salary_question(self, message: str) -> Dict[str, Any]:
        """Handle salary-related questions using RAG system."""
        try:
            # Use vector search to find relevant job postings with salary data
            if self._initialized and self.qdrant_client:
                # Generate embedding for the query
                query_embedding = self.embedding_generator._hash_based_embedding(message, 384).tolist()
                similar_jobs = self.qdrant_client.search_similar_job_postings(query_embedding, top_k=5)
                
                if similar_jobs:
                    # Extract salary information from job postings
                    salary_data = []
                    for job in similar_jobs:
                        if job.get('salary_min') and job.get('salary_max'):
                            salary_range = f"${job['salary_min']:,} - ${job['salary_max']:,}"
                            salary_data.append({
                                'title': job['title'],
                                'company': job['company'],
                                'location': job['location'],
                                'salary_range': salary_range,
                                'experience_level': job.get('experience_level', 'Not specified')
                            })
                    
                    if salary_data:
                        # Group by experience level
                        junior_salaries = [job for job in salary_data if 'junior' in job['experience_level'].lower() or 'entry' in job['experience_level'].lower()]
                        senior_salaries = [job for job in salary_data if 'senior' in job['experience_level'].lower() or 'lead' in job['experience_level'].lower()]
                        mid_salaries = [job for job in salary_data if job not in junior_salaries and job not in senior_salaries]
                        
                        response = "## AI Engineer Salary Insights\n\n"
                        response += "Based on real job postings from our database:\n\n"
                        
                        if senior_salaries:
                            response += "**Senior AI Engineers**:\n"
                            for job in senior_salaries[:3]:
                                response += f"• {job['title']} at {job['company']} ({job['location']}): {job['salary_range']}\n"
                            response += "\n"
                        
                        if mid_salaries:
                            response += "**Mid-level AI Engineers**:\n"
                            for job in mid_salaries[:3]:
                                response += f"• {job['title']} at {job['company']} ({job['location']}): {job['salary_range']}\n"
                            response += "\n"
                        
                        if junior_salaries:
                            response += "**Junior AI Engineers**:\n"
                            for job in junior_salaries[:3]:
                                response += f"• {job['title']} at {job['company']} ({job['location']}): {job['salary_range']}\n"
                            response += "\n"
                        
                        response += "**Key Factors Affecting AI Engineer Salaries**:\n"
                        response += "• **Experience Level**: Senior roles typically pay 30-50% more than junior positions\n"
                        response += "• **Location**: Tech hubs like San Francisco, NYC, and Seattle offer higher salaries\n"
                        response += "• **Company Size**: Large tech companies often pay premium salaries\n"
                        response += "• **Skills**: Specialized AI skills (RAG, MCP, LLMs) command higher compensation\n"
                        response += "• **Remote Work**: Many companies offer competitive salaries for remote positions\n\n"
                        
                        response += f"**Data Source**: Based on {len(similar_jobs)} recent job postings from Indeed and other sources.\n\n"
                        response += "Would you like me to provide more specific salary information for a particular location or skill set?"
                        
                        return {
                            'message': response,
                            'type': 'salary_info',
                            'confidence': 0.95,
                            'jobs_analyzed': len(similar_jobs)
                        }
            
            # Fallback to database search if vector search fails
            try:
                with db_manager.get_session() as session:
                    # Search for AI-related job postings with salary data
                    ai_jobs = session.query(JobPosting).filter(
                        (JobPosting.title.contains('AI') | 
                         JobPosting.title.contains('Machine Learning') |
                         JobPosting.title.contains('Data Scientist') |
                         JobPosting.description.contains('AI')) &
                        (JobPosting.salary_min.isnot(None) | JobPosting.salary_max.isnot(None))
                    ).limit(5).all()
                    
                    if ai_jobs:
                        response = "## AI Engineer Salary Insights\n\n"
                        response += "Based on real job postings from our database:\n\n"
                        
                        for job in ai_jobs:
                            if job.salary_min and job.salary_max:
                                salary_range = f"${job.salary_min:,} - ${job.salary_max:,}"
                                response += f"• **{job.title}** at {job.company} ({job.location}): {salary_range}\n"
                        
                        response += "\n**Salary Trends**:\n"
                        response += "• **Entry Level**: $70,000 - $100,000\n"
                        response += "• **Mid Level**: $100,000 - $150,000\n"
                        response += "• **Senior Level**: $150,000 - $250,000+\n\n"
                        response += "Would you like more specific information about AI engineering salaries?"
                        
                        return {
                            'message': response,
                            'type': 'salary_info',
                            'confidence': 0.9,
                            'jobs_analyzed': len(ai_jobs)
                        }
            except Exception as db_error:
                logger.error(f"Database salary search error: {db_error}")
            
            # Final fallback response
            response = (
                "## AI Engineer Salary Insights\n\n"
                "Based on market data, typical salary ranges for AI Engineers:\n\n"
                "• **Junior AI Engineer**: $70,000 - $100,000\n"
                "• **Mid-level AI Engineer**: $100,000 - $150,000\n"
                "• **Senior AI Engineer**: $150,000 - $250,000+\n"
                "• **AI Engineering Lead**: $200,000 - $300,000+\n\n"
                "**High-Demand AI Skills** (command premium salaries):\n"
                "• RAG (Retrieval-Augmented Generation) Systems\n"
                "• Large Language Models (LLMs)\n"
                "• MCP (Model Context Protocol)\n"
                "• Vector Databases and Embeddings\n"
                "• Prompt Engineering\n\n"
                "**Location Impact**:\n"
                "• San Francisco/NYC: +30-50% higher salaries\n"
                "• Remote positions: Often competitive with local rates\n\n"
                "Would you like me to search for specific salary data from recent job postings?"
            )
            
            return {
                'message': response,
                'type': 'salary_info',
                'confidence': 0.8
            }
            
        except Exception as e:
            logger.error(f"Error in salary question handler: {e}")
            return {
                'message': "I'm having trouble accessing salary data right now. Please try again later.",
                'type': 'error',
                'confidence': 0.3
            }
    
    async def _handle_job_question(self, message: str) -> Dict[str, Any]:
        """Handle job posting-related questions."""
        try:
            # Use vector search if available
            if self._initialized and self.qdrant_client:
                # Generate embedding for the query
                query_embedding = self.embedding_generator._hash_based_embedding(message, 384).tolist()
                similar_jobs = self.qdrant_client.search_similar_job_postings(query_embedding, top_k=3)
                
                if similar_jobs:
                    job_list = "\n".join([
                        f"• **{job['title']}** at {job['company']} ({job['location']}) - {job['data_source'].title()}"
                        for job in similar_jobs
                    ])
                    
                    response = (
                        f"## Job Posting Insights\n\n"
                        f"Based on your query, here are some relevant job postings:\n\n{job_list}\n\n"
                        f"**Job Market Trends**:\n"
                        f"• **Remote Work**: Many companies offer remote or hybrid options\n"
                        f"• **Salary Ranges**: Vary by location, experience, and company size\n"
                        f"• **Required Skills**: Focus on practical experience and modern technologies\n\n"
                        f"**Popular Job Platforms**:\n"
                        
                        f"• **Indeed** - Wide variety of job types and locations\n"
                        f"• **Glassdoor** - Company reviews and salary information\n"
                        f"• **Stack Overflow Jobs** - Developer-specific opportunities\n\n"
                        f"Would you like me to provide more specific information about any of these roles?"
                    )
                    
                    return {
                        'message': response,
                        'type': 'job_search_results',
                        'confidence': 0.9,
                        'jobs_found': len(similar_jobs)
                    }
            
            # Fallback response if no vector search or no results
            response = (
                "## Job Posting Insights\n\n"
                "Here are some key aspects of job postings:\n\n"
                "• **Job Titles** - Common roles include 'Software Engineer', 'Data Scientist', 'Full Stack Developer', etc.\n"
                "• **Required Skills** - Companies often list specific technologies and programming languages.\n"
                "• **Salary** - Job postings typically include a salary range.\n"
                "• **Location** - Many postings specify remote or on-site work.\n"
                "• **Company** - Information about the company, its size, industry, and reputation.\n\n"
                "**How to Find Job Postings**:\n"
                
                "2. **Indeed** - Wide variety of job types\n"
                "3. **Glassdoor** - Reviews, salaries, and company information\n"
                "4. **Stack Overflow Jobs** - Developer-specific jobs\n"
                "5. **RemoteOK** - For remote-friendly positions\n\n"
                "**Tips for Applying**:\n"
                "• Read the job description carefully\n"
                "• Tailor your resume and cover letter\n"
                "• Prepare for technical interviews\n"
                "• Network with professionals in your field\n\n"
                "Would you like me to provide more specific information about job posting trends or help you find a job?"
            )
            
            return {
                'message': response,
                'type': 'job_info',
                'confidence': 0.9
            }
            
        except Exception as e:
            logger.error(f"Error in job question handler: {e}")
            return {
                'message': "I'm having trouble accessing job posting data right now. Please try again later.",
                'type': 'error',
                'confidence': 0.3
            }
    
    async def _handle_ai_question(self, message: str) -> Dict[str, Any]:
        """Handle AI-specific questions using RAG system."""
        try:
            message_lower = message.lower()
            
            # Check if it's a salary question about AI
            if any(word in message_lower for word in ['salary', 'pay', 'money', 'earn', 'income']):
                return await self._handle_salary_question(message)
            
            # Check if it's asking about AI trends
            if any(word in message_lower for word in ['trend', 'trends', 'latest', 'new', 'emerging', 'recent', 'current']):
                return await self._handle_ai_trends_question(message)
            
            # Use RAG with LLM for AI questions
            if self._initialized and self.qdrant_client:
                # Retrieve relevant context
                context = await self._retrieve_ai_trends_context(message)
                
                # Generate LLM response with context
                response = await self._generate_llm_response_with_context(
                    message=message,
                    context=context,
                    response_type="ai_career"
                )
                
                return {
                    'message': response,
                    'type': 'ai_career_info',
                    'confidence': 0.95,
                    'context_used': len(context) if context else 0
                }
            
            # Fallback response
            response = (
                "## AI Engineering Career Path\n\n"
                "**What is AI Engineering?**\n"
                "AI Engineers build and deploy artificial intelligence systems, including machine learning models, neural networks, and intelligent applications.\n\n"
                "**Key Skills**:\n"
                "• **Programming**: Python, R, Julia\n"
                "• **Mathematics**: Linear Algebra, Calculus, Statistics\n"
                "• **Machine Learning**: Scikit-learn, TensorFlow, PyTorch\n"
                "• **Deep Learning**: Neural Networks, CNNs, RNNs\n"
                "• **AI Tools**: RAG Systems, LLMs, Vector Databases\n\n"
                "**Career Progression**:\n"
                "• **Junior AI Engineer**: Focus on model implementation\n"
                "• **Senior AI Engineer**: Lead AI projects and teams\n"
                "• **AI Research Engineer**: Develop new AI algorithms\n"
                "• **AI Engineering Lead**: Strategic AI initiatives\n\n"
                "Would you like specific information about AI engineering salaries, required skills, or job opportunities?"
            )
            
            return {
                'message': response,
                'type': 'ai_career_info',
                'confidence': 0.9
            }
            
        except Exception as e:
            logger.error(f"Error in AI question handler: {e}")
            return {
                'message': "I'm having trouble accessing AI career information right now. Please try again later.",
                'type': 'error',
                'confidence': 0.3
            }

    async def _handle_ai_trends_question(self, message: str) -> Dict[str, Any]:
        """Handle AI trends and latest developments questions using RAG with LLM."""
        try:
            # Step 1: Retrieve relevant context from vector database
            context = await self._retrieve_ai_trends_context(message)
            
            # Step 2: Generate LLM response using retrieved context
            response = await self._generate_llm_response_with_context(
                message=message,
                context=context,
                response_type="ai_trends"
            )
            
            return {
                'message': response,
                'type': 'ai_trends',
                'confidence': 0.95,
                'context_used': len(context) if context else 0
            }
            
        except Exception as e:
            logger.error(f"Error in AI trends handler: {e}")
            return {
                'message': "I'm having trouble accessing AI trends information right now. Please try again later.",
                'type': 'error',
                'confidence': 0.3
            }

    async def _handle_learning_question(self, message: str) -> Dict[str, Any]:
        """Handle learning path questions."""
        response = (
            "## Learning Path Recommendations\n\n"
            "I can help you create personalized learning paths! Here are some popular options:\n\n"
            "🎯 **Web Development Path**:\n"
            "1. HTML, CSS, JavaScript fundamentals\n"
            "2. React or Vue.js frontend framework\n"
            "3. Node.js backend development\n"
            "4. Database design and SQL\n"
            "5. Deployment and DevOps basics\n\n"
            "🤖 **Data Science Path**:\n"
            "1. Python programming\n"
            "2. Data analysis with Pandas\n"
            "3. Statistics and probability\n"
            "4. Machine learning algorithms\n"
            "5. Data visualization\n\n"
            "☁️ **DevOps Path**:\n"
            "1. Linux system administration\n"
            "2. Docker containerization\n"
            "3. Cloud platforms (AWS/Azure)\n"
            "4. CI/CD pipelines\n"
            "5. Infrastructure as code\n\n"
            "Which learning path interests you? I can provide a detailed step-by-step roadmap!"
        )
        
        return {
            'message': response,
            'type': 'learning_path',
            'confidence': 0.9
        }
    
    async def _handle_technology_question(self, message: str) -> Dict[str, Any]:
        """Handle specific technology questions."""
        tech_info = {
            'python': {
                'description': 'Versatile programming language for web development, data science, and automation',
                'use_cases': 'Web development, data analysis, machine learning, automation',
                'learning_time': '3-6 months for basics',
                'resources': 'Python.org, Real Python, Codecademy'
            },
            'javascript': {
                'description': 'Essential language for web development and building interactive applications',
                'use_cases': 'Frontend development, backend (Node.js), mobile apps',
                'learning_time': '2-4 months for basics',
                'resources': 'MDN Web Docs, JavaScript.info, freeCodeCamp'
            },
            'react': {
                'description': 'Popular JavaScript library for building user interfaces',
                'use_cases': 'Single-page applications, mobile apps, interactive UIs',
                'learning_time': '2-3 months after JavaScript',
                'resources': 'React docs, Create React App, React Tutorial'
            },
            'node': {
                'description': 'JavaScript runtime for building server-side applications',
                'use_cases': 'Backend APIs, real-time applications, microservices',
                'learning_time': '1-2 months after JavaScript',
                'resources': 'Node.js docs, Express.js, Node.js Tutorial'
            },
            'sql': {
                'description': 'Standard language for managing and querying databases',
                'use_cases': 'Data storage, analysis, reporting, business intelligence',
                'learning_time': '1-2 months',
                'resources': 'SQL Tutorial, W3Schools, LeetCode SQL'
            },
            'docker': {
                'description': 'Platform for developing, shipping, and running applications in containers',
                'use_cases': 'Application deployment, development environments, microservices',
                'learning_time': '1-2 months',
                'resources': 'Docker docs, Docker Tutorial, Docker Hub'
            }
        }
        
        for tech, info in tech_info.items():
            if tech in message_lower:
                response = (
                    f"## {tech.title()} Technology Overview\n\n"
                    f"**Description**: {info['description']}\n\n"
                    f"**Use Cases**: {info['use_cases']}\n\n"
                    f"**Learning Time**: {info['learning_time']}\n\n"
                    f"**Learning Resources**: {info['resources']}\n\n"
                    f"Would you like me to provide a detailed learning path for {tech.title()}?"
                )
                return {
                    'message': response,
                    'type': 'technology_info',
                    'confidence': 0.95,
                    'technology': tech
                }
        
        return {
            'message': "I can provide detailed information about various technologies like Python, JavaScript, React, Node.js, SQL, and Docker. Which technology would you like to learn more about?",
            'type': 'technology_general',
            'confidence': 0.8
        }
    
    def _determine_query_type(self, message: str) -> str:
        """Determine the type of query for Graph RAG processing."""
        message_lower = message.lower()
        
        # Career guidance queries
        if any(word in message_lower for word in ['career', 'path', 'transition', 'advancement', 'growth', 'development']):
            return 'career_guidance'
        
        # Skill analysis queries
        if any(word in message_lower for word in ['skill', 'technology', 'learn', 'master', 'improve', 'gap']):
            return 'skill_analysis'
        
        # Networking queries
        if any(word in message_lower for word in ['network', 'connect', 'collaborate', 'mentor', 'community']):
            return 'networking'
        
        # Learning path queries
        if any(word in message_lower for word in ['learn', 'study', 'course', 'roadmap', 'curriculum']):
            return 'learning_path'
        
        # Job market queries
        if any(word in message_lower for word in ['job', 'market', 'opportunity', 'position', 'role']):
            return 'job_market'
        
        # Project ideas queries
        if any(word in message_lower for word in ['project', 'build', 'create', 'develop', 'portfolio']):
            return 'project_ideas'
        
        # Default to career guidance
        return 'career_guidance'
    
    async def _handle_general_question(self, message: str) -> Dict[str, Any]:
        """Handle general questions with helpful suggestions."""
        response = (
            "I'm here to help with your developer career! Here are some things I can assist you with:\n\n"
            "🎯 **Career Guidance**: Ask about different developer roles and career paths\n"
            "💡 **Skill Recommendations**: Get personalized skill suggestions based on your goals\n"
            "💰 **Salary Information**: Learn about compensation for different roles\n"
            "📚 **Learning Paths**: Get step-by-step learning roadmaps\n"
            "🔍 **Technology Insights**: Learn about specific technologies and their applications\n\n"
            "Try asking me questions like:\n"
            "• \"What skills do I need for a full stack developer role?\"\n"
            "• \"How much do data scientists earn?\"\n"
            "• \"What's the learning path for Python?\"\n"
            "• \"Tell me about React development\"\n\n"
            "What would you like to know?"
        )
        
        return {
            'message': response,
            'type': 'general_help',
            'confidence': 0.8
        }
    
    def get_conversation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a user."""
        return self.conversation_history.get(user_id, [])
    
    async def _retrieve_ai_trends_context(self, message: str) -> List[Dict[str, Any]]:
        """Retrieve relevant context for AI trends questions from vector database."""
        try:
            if not self._initialized or not self.qdrant_client:
                return []
            
            # Generate embedding for the query
            query_embedding = self.embedding_generator._hash_based_embedding(message, 384).tolist()
            
            # Search for relevant skills, jobs, and career paths
            similar_skills = self.qdrant_client.search_similar_skills(query_embedding, top_k=5)
            similar_jobs = self.qdrant_client.search_similar_job_postings(query_embedding, top_k=3)
            similar_careers = self.qdrant_client.search_similar_career_paths(query_embedding, top_k=3)
            
    
            logger.info(f"Retrieved {len(similar_skills)} skills, {len(similar_jobs)} jobs, {len(similar_careers)} careers for query: {message[:50]}...")
            
            context = []
            
            # Add AI-related skills
            if similar_skills:
                for skill in similar_skills:
                    skill_name = skill.get('skill_name', 'Unknown Skill')
                    if any(ai_term in skill_name.lower() for ai_term in ['ai', 'machine learning', 'deep learning', 'neural', 'tensorflow', 'pytorch', 'scikit', 'rag', 'llm', 'vector']):
                        context.append({
                            'type': 'skill',
                            'content': f"AI Skill: {skill_name} - {skill.get('category', 'AI/ML')}",
                            'relevance': skill.get('score', 0)
                        })
            
            # Add AI-related job postings
            if similar_jobs:
                for job in similar_jobs:
                    job_title = job.get('title', 'Unknown Job')
                    if any(ai_term in job_title.lower() for ai_term in ['ai', 'machine learning', 'data scientist', 'ml engineer', 'ai engineer']):
                        context.append({
                            'type': 'job',
                            'content': f"AI Job: {job_title} at {job.get('company', 'Unknown Company')} - {job.get('description', '')[:200]}...",
                            'relevance': job.get('score', 0)
                        })
            
            # Add career path information
            if similar_careers:
                for career in similar_careers:
                    path_name = career.get('path_name', 'Unknown Career Path')
                    if any(ai_term in path_name.lower() for ai_term in ['ai', 'data scientist', 'machine learning']):
                        context.append({
                            'type': 'career',
                            'content': f"AI Career: {path_name} - {career.get('description', '')[:200]}...",
                            'relevance': career.get('score', 0)
                        })
            
            # Sort by relevance
            context.sort(key=lambda x: x['relevance'], reverse=True)
            
            final_context = context[:10]  # Return top 10 most relevant items
            logger.info(f"Final context for AI trends query: {len(final_context)} items")
            
            return final_context
            
        except Exception as e:
            logger.error(f"Error retrieving AI trends context: {e}")
            return []
    
    async def _generate_llm_response_with_context(self, message: str, context: List[Dict[str, Any]], response_type: str) -> str:
        """Generate LLM response using retrieved context (RAG pattern)."""
        try:
            if not context:
                # Fallback to general AI trends knowledge if no context found
                return await self._generate_fallback_ai_trends_response(message)
            
            # Prepare context for LLM
            context_text = "\n\n".join([
                f"{item['type'].title()}: {item['content']}"
                for item in context
            ])
            
            # Create RAG prompt
            prompt = f"""
You are an AI career assistant with expertise in AI trends and developments. Use the following context to answer the user's question about AI trends.

User Question: {message}

Relevant Context:
{context_text}

Instructions:
1. Use the provided context to give accurate, up-to-date information about AI trends
2. Focus on practical applications and career implications
3. If the context doesn't fully answer the question, supplement with your knowledge of current AI trends
4. Structure your response with clear headings and bullet points
5. Include specific examples and career opportunities where relevant

Please provide a comprehensive, well-structured response about AI trends based on the context and your knowledge.
"""
            
            # Generate response using LLM
            if hasattr(self, 'llm_client') and self.llm_client:
                response = await self.llm_client.generate_text(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=1500
                )
            else:
                # Fallback if LLM client not available
                response = await self._generate_fallback_ai_trends_response(message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return await self._generate_fallback_ai_trends_response(message)
    
    async def _generate_fallback_ai_trends_response(self, message: str) -> str:
        """Generate fallback response when LLM is not available."""
        return (
            "## Latest AI Trends and Developments (2024-2025)\n\n"
            "**🔥 Current AI Trends**:\n\n"
            "**1. RAG (Retrieval-Augmented Generation)**\n"
            "• **What it is**: Combines large language models with external knowledge bases\n"
            "• **Why it's trending**: Solves hallucination issues and provides accurate, up-to-date information\n"
            "• **Applications**: AI assistants, knowledge management, research tools\n\n"
            
            "**2. MCP (Model Context Protocol)**\n"
            "• **What it is**: Standardized protocol for AI tool integration\n"
            "• **Why it's trending**: Enables AI models to use external tools and APIs seamlessly\n"
            "• **Applications**: AI agents, automation, workflow integration\n\n"
            
            "**3. Vector Databases & Embeddings**\n"
            "• **What it is**: Specialized databases for similarity search and semantic understanding\n"
            "• **Why it's trending**: Essential for RAG systems and semantic search\n"
            "• **Applications**: Recommendation systems, search engines, content discovery\n\n"
            
            "**4. Prompt Engineering & Optimization**\n"
            "• **What it is**: Techniques for optimizing AI model interactions\n"
            "• **Why it's trending**: Critical for getting the best results from LLMs\n"
            "• **Applications**: AI product development, content generation, automation\n\n"
            
            "**5. AI Safety & Guardrails**\n"
            "• **What it is**: Methods to ensure AI systems behave safely and ethically\n"
            "• **Why it's trending**: Essential as AI becomes more powerful and widespread\n"
            "• **Applications**: Content filtering, bias detection, safety protocols\n\n"
            
            "**6. Multimodal AI**\n"
            "• **What it is**: AI that can process text, images, audio, and video\n"
            "• **Why it's trending**: More natural and comprehensive AI interactions\n"
            "• **Applications**: Content creation, analysis, accessibility tools\n\n"
            
            "**🚀 Emerging Technologies**:\n"
            "• **Agentic AI**: Autonomous AI agents that can complete complex tasks\n"
            "• **Synchronous/Asynchronous AI**: Real-time and batch AI processing\n"
            "• **Graph RAG**: Combining knowledge graphs with RAG for enhanced reasoning\n"
            "• **AI Evaluation Methods**: Systematic ways to measure AI performance\n\n"
            
            "**💼 Career Impact**:\n"
            "These trends are creating new job opportunities in:\n"
            "• **AI Engineering**: Building and deploying AI systems\n"
            "• **Prompt Engineering**: Optimizing AI interactions\n"
            "• **AI Safety**: Ensuring responsible AI development\n"
            "• **Vector Database Engineering**: Specialized data infrastructure\n\n"
            
            "Would you like me to provide more details about any specific AI trend or how to get started in AI engineering?"
        )

    def clear_conversation_history(self, user_id: str):
        """Clear conversation history for a user."""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]


# Global instance
enhanced_chatbot = EnhancedAIChatbot() 