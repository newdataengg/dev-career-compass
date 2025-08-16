#!/usr/bin/env python3
"""
🚀 DevCareerCompass Real Data Collector
Collects real developer data from multiple platforms:
- GitHub (developers, repositories, commits)
- Stack Overflow (users, questions, answers)
- Reddit (programming communities)
- Indeed (job listings, skills)
- Indeed (job listings, skills)
"""

import sys
import os
import asyncio
import logging
import time
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_pipeline.data_collector import DataCollector
from src.database.connection import init_database, db_manager
from src.database.models import Developer, Repository, Skill, Commit, DeveloperSkill, JobPosting
from src.config.settings import settings
from src.utils.logger import setup_logging, get_application_logger

logger = get_application_logger(__name__)


class RealDataCollector:
    """Comprehensive real data collector from multiple platforms"""
    
    def __init__(self):
        self.github_collector = DataCollector()
        self.session = requests.Session()
        self.loaded_count = 0
        self.start_time = None
        
        # Initialize job market aggregator
        from src.data_pipeline.job_market_clients import JobMarketDataAggregator
        self.job_market_aggregator = JobMarketDataAggregator()
        
        # API Keys and endpoints
        self.stack_overflow_key = os.getenv('STACK_OVERFLOW_KEY')
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')


        
    def start_timer(self):
        """Start the loading timer"""
        self.start_time = datetime.now()
        print(f"⏱️  Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def end_timer(self):
        """End the loading timer and show duration"""
        if self.start_time:
            end_time = datetime.now()
            duration = end_time - self.start_time
            print(f"⏱️  Completed in: {duration}")
            print(f"📊 Average: {self.loaded_count / max(duration.total_seconds(), 1):.2f} items/second")
    
    def show_current_stats(self):
        """Show current database statistics from all data sources"""
        print("\n📊 Current Database Statistics:")
        with db_manager.get_session() as session:
            # Developer statistics by source
            github_devs = session.query(Developer).filter(Developer.data_source == 'github').count()
            stackoverflow_devs = session.query(Developer).filter(Developer.data_source == 'stackoverflow').count()
            reddit_devs = session.query(Developer).filter(Developer.data_source == 'reddit').count()
            total_devs = session.query(Developer).count()
            
            # Repository and commit statistics (GitHub only)
            repo_count = session.query(Repository).count()
            commit_count = session.query(Commit).count()
            
            # Skill statistics
            skill_count = session.query(Skill).count()
            
            # Job posting statistics by source

            indeed_jobs = session.query(JobPosting).filter(JobPosting.data_source == 'indeed').count()
            total_jobs = session.query(JobPosting).count()
            
            print(f"   👥 Developers:")
            print(f"      • GitHub: {github_devs:,}")
            print(f"      • Stack Overflow: {stackoverflow_devs:,}")
            print(f"      • Reddit: {reddit_devs:,}")
            print(f"      • Total: {total_devs:,}")
            
            print(f"   📚 Repositories: {repo_count:,} (GitHub)")
            print(f"   🔄 Commits: {commit_count:,} (GitHub)")
            print(f"   🎯 Skills: {skill_count:,}")
            
            print(f"   💼 Job Postings:")

            print(f"      • Indeed: {indeed_jobs:,}")
            print(f"      • Total: {total_jobs:,}")
            
            # Show percentages
            if total_devs > 0:
                print(f"\n   📈 Data Distribution:")
                print(f"      • GitHub: {(github_devs/total_devs*100):.1f}%")
                print(f"      • Stack Overflow: {(stackoverflow_devs/total_devs*100):.1f}%")
                print(f"      • Reddit: {(reddit_devs/total_devs*100):.1f}%")
            
            if total_jobs > 0:
    
                print(f"      • Indeed Jobs: {(indeed_jobs/total_jobs*100):.1f}%")
    
    # ==================== GITHUB DATA COLLECTION ====================
    
    def collect_github_massive(self, target_count: int = 1000):
        """Collect massive amounts of GitHub data"""
        print(f"\n🐙 GitHub Massive Data Collection")
        print(f"   Target: {target_count} developers")
        
        self.start_timer()
        
        # Multiple collection strategies
        strategies = [
            self._github_trending_languages,
            self._github_popular_users,
            self._github_company_developers,
            self._github_location_based,
            self._github_repository_owners
        ]
        
        total_loaded = 0
        
        for strategy in strategies:
            if total_loaded >= target_count:
                break
            
            remaining = target_count - total_loaded
            loaded = strategy(remaining)
            total_loaded += loaded
            
            print(f"   ✅ Strategy completed: {loaded} developers loaded")
            print(f"   📊 Total so far: {total_loaded}/{target_count}")
        
        self.end_timer()
        return total_loaded
    
    def _github_trending_languages(self, target_count: int):
        """Collect from trending repositories in multiple languages"""
        languages = [
            'python', 'javascript', 'java', 'go', 'rust', 'typescript', 
            'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin', 'scala',
            'dart', 'elixir', 'clojure', 'haskell', 'ocaml', 'f#',
            'r', 'matlab', 'julia', 'perl', 'lua', 'groovy'
        ]
        
        loaded = 0
        for language in languages:
            if loaded >= target_count:
                break
            
            print(f"      🔍 Collecting {language} trending repos...")
            trending_repos = self.github_collector.github_client.get_trending_repositories(language)
            
            for repo in trending_repos:
                if loaded >= target_count:
                    break
                
                owner_login = repo['owner']['login']
                if self._save_github_developer(owner_login):
                    loaded += 1
                    self.loaded_count += 1
                
                time.sleep(settings.rate_limit_delay)
        
        return loaded
    
    def _github_popular_users(self, target_count: int):
        """Collect popular users by various criteria"""
        queries = [
            "followers:>1000", "followers:>5000", "followers:>10000",
            "repos:>50", "repos:>100", "repos:>200",
            "type:user language:python", "type:user language:javascript",
            "type:user language:java", "type:user language:go"
        ]
        
        loaded = 0
        for query in queries:
            if loaded >= target_count:
                break
            
            print(f"      🔍 Searching: {query}")
            users = self.github_collector.github_client.search_users(query, max_results=50)
            
            for user in users:
                if loaded >= target_count:
                    break
                
                if self._save_github_developer(user.login):
                    loaded += 1
                    self.loaded_count += 1
                
                time.sleep(settings.rate_limit_delay)
        
        return loaded
    
    def _github_company_developers(self, target_count: int):
        """Collect developers from major tech companies"""
        companies = [
            'google', 'microsoft', 'apple', 'meta', 'amazon', 'netflix',
            'uber', 'airbnb', 'stripe', 'shopify', 'github', 'gitlab',
            'docker', 'hashicorp', 'databricks', 'snowflake', 'palantir'
        ]
        
        loaded = 0
        for company in companies:
            if loaded >= target_count:
                break
            
            print(f"      🏢 Collecting {company} developers...")
            users = self.github_collector.github_client.search_users(f"company:{company}", max_results=30)
            
            for user in users:
                if loaded >= target_count:
                    break
                
                if self._save_github_developer(user.login):
                    loaded += 1
                    self.loaded_count += 1
                
                time.sleep(settings.rate_limit_delay)
        
        return loaded
    
    def _github_location_based(self, target_count: int):
        """Collect developers by location"""
        locations = [
            'San Francisco', 'New York', 'London', 'Berlin', 'Tokyo',
            'Toronto', 'Sydney', 'Amsterdam', 'Paris', 'Singapore'
        ]
        
        loaded = 0
        for location in locations:
            if loaded >= target_count:
                break
            
            print(f"      🌍 Collecting {location} developers...")
            users = self.github_collector.github_client.search_users(f"location:{location}", max_results=30)
            
            for user in users:
                if loaded >= target_count:
                    break
                
                if self._save_github_developer(user.login):
                    loaded += 1
                    self.loaded_count += 1
                
                time.sleep(settings.rate_limit_delay)
        
        return loaded
    
    def _github_repository_owners(self, target_count: int):
        """Collect owners of popular repositories"""
        repo_queries = [
            "stars:>1000", "stars:>5000", "stars:>10000",
            "forks:>500", "forks:>1000", "forks:>5000"
        ]
        
        loaded = 0
        for query in repo_queries:
            if loaded >= target_count:
                break
            
            print(f"      📚 Searching repos: {query}")
            repos = self.github_collector.github_client.github.search_repositories(
                query=query, sort="stars", order="desc"
            )
            
            for repo in repos[:50]:
                if loaded >= target_count:
                    break
                
                if self._save_github_developer(repo.owner.login):
                    loaded += 1
                    self.loaded_count += 1
                
                time.sleep(settings.rate_limit_delay)
        
        return loaded
    
    def _save_github_developer(self, username: str) -> bool:
        """Save a GitHub developer to database"""
        try:
            # Check if already exists
            with db_manager.get_session() as session:
                existing_dev = session.query(Developer).filter(Developer.username == username).first()
                if existing_dev:
                    return False
            
            # Get developer data
            developer = self.github_collector.github_client.get_user(username)
            if not developer:
                return False
            
            # Save to database
            with db_manager.get_session() as session:
                db_developer = Developer(
                    github_id=developer.id,
                    username=developer.login,
                    name=developer.name,
                    email=developer.email,
                    bio=developer.bio,
                    location=developer.location,
                    company=developer.company,
                    blog=developer.blog,
                    twitter_username=developer.twitter_username,
                    public_repos=developer.public_repos or 0,
                    public_gists=developer.public_gists or 0,
                    followers=developer.followers or 0,
                    following=developer.following or 0,
                    created_at=developer.created_at,
                    updated_at=developer.updated_at,
                    data_source='github'
                )
                
                session.add(db_developer)
                session.commit()
                
                # Collect repositories
                self._collect_developer_repositories(session, db_developer, username)
                
                return True
                
        except Exception as e:
            logger.error(f"Error saving GitHub developer {username}: {e}")
            return False
    
    def _collect_developer_repositories(self, session, db_developer, username):
        """Collect repositories for a developer"""
        try:
            repos = self.github_collector.github_client.get_user_repositories(username, max_repos=20)
            
            for repo in repos:
                # Check if repository already exists
                existing_repo = session.query(Repository).filter(Repository.github_id == repo.id).first()
                if existing_repo:
                    continue
                
                # Get languages and topics
                languages = self.github_collector.github_client.get_repository_languages(repo)
                topics = self.github_collector.github_client.get_repository_topics(repo)
                
                # Save repository
                db_repo = Repository(
                    github_id=repo.id,
                    developer_id=db_developer.id,
                    name=repo.name,
                    full_name=repo.full_name,
                    description=repo.description,
                    language=repo.language,
                    languages=str(languages) if languages else None,
                    topics=str(topics) if topics else None,
                    stargazers_count=repo.stargazers_count,
                    watchers_count=repo.watchers_count,
                    forks_count=repo.forks_count,
                    open_issues_count=repo.open_issues_count,
                    size=repo.size,
                    default_branch=repo.default_branch,
                    created_at=repo.created_at,
                    updated_at=repo.updated_at,
                    pushed_at=repo.pushed_at,
                    homepage=repo.homepage,
                    license_name=repo.license.name if repo.license else None,
                    has_wiki=getattr(repo, 'has_wiki', False),
                    has_pages=getattr(repo, 'has_pages', False),
                    has_downloads=getattr(repo, 'has_downloads', False),
                    has_issues=getattr(repo, 'has_issues', True),
                    has_projects=getattr(repo, 'has_projects', False),
                    has_discussions=getattr(repo, 'has_discussions', False),
                    archived_at=getattr(repo, 'archived_at', None),
                    disabled=getattr(repo, 'disabled', False),
                    archived=getattr(repo, 'archived', False),
                    allow_forking=getattr(repo, 'allow_forking', True),
                    is_template=getattr(repo, 'is_template', False),
                    web_commit_signoff_required=getattr(repo, 'web_commit_signoff_required', False),
                    visibility=getattr(repo, 'visibility', 'public'),
                    network_count=getattr(repo, 'network_count', 0),
                    subscribers_count=getattr(repo, 'subscribers_count', 0)
                )
                
                session.add(db_repo)
                session.commit()
                
        except Exception as e:
            logger.error(f"Error collecting repositories for {username}: {e}")
    
    # ==================== STACK OVERFLOW DATA COLLECTION ====================
    
    def collect_stack_overflow_data(self, target_count: int = 500):
        """Collect Stack Overflow data"""
        print(f"\n💬 Stack Overflow Data Collection")
        print(f"   Target: {target_count} users")
        
        if not self.stack_overflow_key:
            print("   ⚠️  Stack Overflow API key not found. Skipping...")
            return 0
        
        self.start_timer()
        
        # Stack Overflow API endpoints
        base_url = "https://api.stackexchange.com/2.3"
        
        # Collect top users by reputation
        loaded = 0
        
        # Different user categories
        user_types = ['reputation', 'creation', 'name']
        
        for user_type in user_types:
            if loaded >= target_count:
                break
            
            print(f"      🔍 Collecting {user_type} users...")
            
            url = f"{base_url}/users"
            params = {
                'order': 'desc',
                'sort': user_type,
                'site': 'stackoverflow',
                'pagesize': 100,
                'key': self.stack_overflow_key
            }
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for user in data.get('items', []):
                    if loaded >= target_count:
                        break
                    
                    if self._save_stack_overflow_user(user):
                        loaded += 1
                        self.loaded_count += 1
                    
                    time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error collecting Stack Overflow {user_type} users: {e}")
                continue
        
        self.end_timer()
        return loaded
    
    def _save_stack_overflow_user(self, user_data: Dict) -> bool:
        """Save Stack Overflow user to database"""
        try:
            username = user_data.get('display_name', '')
            
            # Check if already exists
            with db_manager.get_session() as session:
                existing_dev = session.query(Developer).filter(Developer.username == username).first()
                if existing_dev:
                    return False
            
            # Save to database
            with db_manager.get_session() as session:
                db_developer = Developer(
                    github_id=None,  # Stack Overflow user
                    username=username,
                    name=user_data.get('display_name'),
                    email=None,  # Not available from Stack Overflow
                    bio=user_data.get('about_me', ''),
                    location=user_data.get('location'),
                    company=None,  # Not available from Stack Overflow
                    blog=user_data.get('website_url'),
                    twitter_username=None,
                    public_repos=0,  # Not applicable
                    public_gists=0,
                    followers=user_data.get('reputation', 0),
                    following=0,
                    created_at=datetime.fromtimestamp(user_data.get('creation_date', 0)),
                    updated_at=datetime.fromtimestamp(user_data.get('last_modified_date', 0)),
                    data_source='stackoverflow'
                )
                
                session.add(db_developer)
                session.commit()
                
                return True
                
        except Exception as e:
            logger.error(f"Error saving Stack Overflow user: {e}")
            return False
    
    # ==================== REDDIT DATA COLLECTION ====================
    
    def collect_reddit_data(self, target_count: int = 300):
        """Collect Reddit data from programming communities"""
        print(f"\n🤖 Reddit Data Collection")
        print(f"   Target: {target_count} users")
        
        if not self.reddit_client_id or not self.reddit_client_secret:
            print("   ⚠️  Reddit API credentials not found. Skipping...")
            return 0
        
        self.start_timer()
        
        # Programming subreddits
        subreddits = [
            'programming', 'python', 'javascript', 'java', 'webdev',
            'reactjs', 'node', 'golang', 'rust', 'cpp', 'csharp',
            'datascience', 'machinelearning', 'devops', 'aws', 'docker'
        ]
        
        loaded = 0
        
        for subreddit in subreddits:
            if loaded >= target_count:
                break
            
            print(f"      🔍 Collecting from r/{subreddit}...")
            
            # Get top posts and their authors
            url = f"https://www.reddit.com/r/{subreddit}/top.json"
            headers = {
                'User-Agent': 'DevCareerCompass/1.0'
            }
            
            try:
                response = self.session.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                for post in data.get('data', {}).get('children', []):
                    if loaded >= target_count:
                        break
                    
                    author = post['data'].get('author')
                    if author and author != '[deleted]':
                        if self._save_reddit_user(author, subreddit):
                            loaded += 1
                            self.loaded_count += 1
                    
                    time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error collecting from r/{subreddit}: {e}")
                continue
        
        self.end_timer()
        return loaded
    
    def _save_reddit_user(self, username: str, subreddit: str) -> bool:
        """Save Reddit user to database"""
        try:
            # Check if already exists
            with db_manager.get_session() as session:
                existing_dev = session.query(Developer).filter(Developer.username == username).first()
                if existing_dev:
                    return False
            
            # Get user info
            url = f"https://www.reddit.com/user/{username}/about.json"
            headers = {
                'User-Agent': 'DevCareerCompass/1.0'
            }
            
            try:
                response = self.session.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                user_data = data.get('data', {})
                
            except:
                # If we can't get user data, create basic entry
                user_data = {}
            
            # Save to database
            with db_manager.get_session() as session:
                db_developer = Developer(
                    github_id=None,  # Reddit user
                    username=username,
                    name=user_data.get('display_name', username),
                    email=None,
                    bio=user_data.get('public_description', f'Reddit user from r/{subreddit}'),
                    location=None,
                    company=None,
                    blog=None,
                    twitter_username=None,
                    public_repos=0,
                    public_gists=0,
                    followers=user_data.get('total_karma', 0),
                    following=0,
                    created_at=datetime.fromtimestamp(user_data.get('created_utc', 0)) if user_data.get('created_utc') else datetime.now(),
                    updated_at=datetime.now(),
                    data_source='reddit'
                )
                
                session.add(db_developer)
                session.commit()
                
                return True
                
        except Exception as e:
            logger.error(f"Error saving Reddit user {username}: {e}")
            return False
    

    
    # ==================== INDEED DATA COLLECTION ====================
    
    def collect_indeed_data(self, target_count: int = 300):
        """Collect Indeed job data using X-Rapid API"""
        print(f"\n🔍 Indeed Data Collection")
        print(f"   Target: {target_count} job listings")
        
        self.start_timer()
        
        # Job search queries
        job_queries = [
            'software engineer', 'data scientist', 'frontend developer',
            'backend developer', 'devops engineer', 'machine learning engineer',
            'python developer', 'javascript developer', 'java developer',
            'react developer', 'node.js developer', 'aws engineer'
        ]
        
        loaded = 0
        
        for query in job_queries:
            if loaded >= target_count:
                break
            
            print(f"      🔍 Searching Indeed jobs: {query}")
            
            try:
                # Use the job market aggregator to get Indeed jobs
                indeed_jobs = self.job_market_aggregator.indeed_jobs.search_jobs(query, limit=20)
                
                for job in indeed_jobs:
                    if loaded >= target_count:
                        break
                    
                    job_data = {
                        'title': job.get('title', query),
                        'company': job.get('company', 'Tech Company'),
                        'location': job.get('location', 'Remote'),
                        'description': job.get('description', f'Job posting for {query}'),
                        'requirements': job.get('requirements', ''),
                        'salary_min': job.get('salary_min'),
                        'salary_max': job.get('salary_max'),
                        'job_type': job.get('job_type', 'full-time'),
                        'experience_level': job.get('experience_level'),
                        'remote_option': job.get('remote_option', False),
                        'posted_date': job.get('posted_date'),
                        'application_url': job.get('url', ''),
                        'skills': [query.split()[0], 'programming', 'development']
                    }
                    
                    if self._save_indeed_job(job_data):
                        loaded += 1
                        self.loaded_count += 1
                
                time.sleep(1.0)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error collecting Indeed jobs for {query}: {e}")
                continue
        
        self.end_timer()
        print(f"   ✅ Indeed collection completed: {loaded} job listings")
        return loaded
    
    def _save_indeed_job(self, job_data: Dict) -> bool:
        """Save Indeed job data to database"""
        try:
            with db_manager.get_session() as session:
                # Save job posting
                db_job = JobPosting(
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    description=job_data['description'],
                    requirements=job_data.get('requirements', ''),
                    salary_min=job_data.get('salary_min'),
                    salary_max=job_data.get('salary_max'),
                    job_type=job_data.get('job_type', 'full-time'),
                    experience_level=job_data.get('experience_level'),
                    remote_option=job_data.get('remote_option', False),
                    posted_date=job_data.get('posted_date'),
                    application_url=job_data.get('application_url'),
                    data_source='indeed',
                    source_id=job_data.get('id')
                )
                
                session.add(db_job)
                session.commit()
                
                # Extract and save skills from job description
                skills = job_data.get('skills', [])
                for skill_name in skills:
                    # Find or create skill
                    skill = session.query(Skill).filter(Skill.name == skill_name).first()
                    if not skill:
                        skill = Skill(
                            name=skill_name,
                            category='job_requirement',
                            description=f'Skill required for {job_data["title"]} positions'
                        )
                        session.add(skill)
                        session.commit()
                    
                    # Link skill to job
                    from src.database.models import JobSkill
                    job_skill = JobSkill(
                        job_id=db_job.id,
                        skill_id=skill.id,
                        is_required=True,
                        importance_score=1.0
                    )
                    session.add(job_skill)
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving Indeed job: {e}")
            return False
    
    # ==================== MAIN COLLECTION METHODS ====================
    
    def collect_all_platforms(self, target_total: int = 2000):
        """Collect data from all platforms"""
        print(f"🚀 DevCareerCompass Real Data Collection")
        print(f"=" * 60)
        print(f"🎯 Target: {target_total} total items")
        
        # Initialize database
        init_database()
        print("   ✅ Database initialized")
        
        # Show initial stats
        self.show_current_stats()
        
        # Calculate targets for each platform
        platform_targets = {
            'github': min(800, target_total // 3),
            'stack_overflow': min(500, target_total // 4),
            'reddit': min(300, target_total // 6),
    
            'indeed': min(300, target_total // 6)
        }
        
        total_loaded = 0
        
        # GitHub Collection
        print(f"\n🐙 Starting GitHub collection...")
        github_loaded = self.collect_github_massive(platform_targets['github'])
        total_loaded += github_loaded
        
        # Stack Overflow Collection
        print(f"\n💬 Starting Stack Overflow collection...")
        so_loaded = self.collect_stack_overflow_data(platform_targets['stack_overflow'])
        total_loaded += so_loaded
        
        # Reddit Collection
        print(f"\n🤖 Starting Reddit collection...")
        reddit_loaded = self.collect_reddit_data(platform_targets['reddit'])
        total_loaded += reddit_loaded
        

        
        # Indeed Collection
        print(f"\n🔍 Starting Indeed collection...")
        indeed_loaded = self.collect_indeed_data(platform_targets['indeed'])
        total_loaded += indeed_loaded
        
        # Show final stats
        print(f"\n🎉 Real Data Collection Completed!")
        print(f"   📊 Summary:")
        print(f"      • GitHub: {github_loaded} developers")
        print(f"      • Stack Overflow: {so_loaded} users")
        print(f"      • Reddit: {reddit_loaded} users")

        print(f"      • Indeed: {indeed_loaded} job listings")
        print(f"      • Total: {total_loaded} items")
        
        self.show_current_stats()
        
        return total_loaded


def main():
    """Main function for real data collection"""
    print("🚀 DevCareerCompass Real Data Collector")
    print("=" * 60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup logging
    setup_logging()
    logger.info("Starting real data collection")
    
    try:
        # Initialize collector
        collector = RealDataCollector()
        
        # Show options
        print(f"\n🎯 Data Collection Options:")
        print(f"   1. GitHub (100 developers)")
        print(f"   2. Stack Overflow (100 users)")
        print(f"   3. Reddit (100 users)")

        print(f"   5. Indeed (50 job listings)")
        print(f"   6. Show Current Statistics Only")
        
        choice = input(f"\n📝 Enter your choice (1-6): ").strip()
        
        if choice == "1":
            print("🐙 Starting GitHub collection (100 developers)...")
            total_loaded = collector.collect_github_massive(20)
        elif choice == "2":
            print("💬 Starting Stack Overflow collection (100 users)...")
            total_loaded = collector.collect_stack_overflow_data(20)
        elif choice == "3":
            print("🤖 Starting Reddit collection (100 users)...")
            total_loaded = collector.collect_reddit_data(20)

        elif choice == "5":
            print("💼 Starting Indeed collection (50 job listings)...")
            total_loaded = collector.collect_indeed_data(50)
        elif choice == "6":
            collector.show_current_stats()
            return 0
        else:
            print("❌ Invalid choice. Using GitHub collection (100 developers)...")
            total_loaded = collector.collect_github_massive(100)
        
        print(f"\n🎉 Data collection completed!")
        print(f"   📅 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📊 Total items loaded: {total_loaded}")
        
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        print(f"\n❌ Data collection failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 