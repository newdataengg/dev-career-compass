"""
Enhanced data collector for gathering and storing multi-platform developer data
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import time

from src.data_pipeline.github_client import GitHubClient
from src.data_pipeline.stack_overflow_client import StackOverflowClient
from src.data_pipeline.job_market_clients import JobMarketDataAggregator
from src.database.models import Developer, Repository, Skill, Commit, DeveloperSkill
from src.database.connection import db_manager
from src.config.settings import settings
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class DataCollector:
    """Enhanced data collector for multiple platforms"""
    
    def __init__(self):
        self.github_client = GitHubClient()
        self.stack_overflow_client = StackOverflowClient()
        self.job_market_aggregator = JobMarketDataAggregator()
        
        logger.info("Enhanced DataCollector initialized with multiple sources")
    
    def collect_from_github_trending(self, max_users: int = 50) -> List[Developer]:
        """Collect developer data from GitHub trending repositories"""
        logger.info(f"Collecting {max_users} developers from GitHub trending")
        
        developers = []
        try:
            # Get trending repositories for popular languages
            languages = ['python', 'javascript', 'java', 'go', 'rust', 'typescript']
            
            for language in languages:
                if len(developers) >= max_users:
                    break
                
                trending_repos = self.github_client.get_trending_repositories(language)
                
                for repo in trending_repos[:max_users // len(languages)]:
                    if len(developers) >= max_users:
                        break
                    
                    owner_login = repo['owner']['login']
                    
                    # Check if developer already exists
                    with db_manager.get_session() as session:
                        existing_dev = session.query(Developer).filter(Developer.username == owner_login).first()
                        if existing_dev:
                            continue
                    
                    # Collect developer data
                    try:
                        developer = self.github_client.get_user(owner_login)
                        if developer:
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
                                    updated_at=developer.updated_at
                                )
                                
                                session.add(db_developer)
                                session.commit()
                                
                                # Collect repositories for this developer
                                self._collect_developer_repositories(session, db_developer, owner_login)
                                
                                developers.append(db_developer)
                                logger.info(f"Collected developer: {developer.get('login')}")
                    
                    except Exception as e:
                        logger.error(f"Error collecting developer {owner_login}: {e}")
                        continue
                    
                    # Rate limiting
                    time.sleep(settings.rate_limit_delay)
        
        except Exception as e:
            logger.error(f"Error in GitHub trending collection: {e}")
        
        logger.info(f"Successfully collected {len(developers)} developers from GitHub trending")
        return developers
    
    def _collect_developer_repositories(self, session: Session, developer: Developer, username: str):
        """Collect repositories for a developer"""
        try:
            logger.info(f"Collecting repositories for developer: {username}")
            
            # Get repositories from GitHub
            github_repos = self.github_client.get_user_repositories(username, max_repos=10)
            
            for github_repo in github_repos:
                try:
                    # Check if repository already exists
                    existing_repo = session.query(Repository).filter(
                        Repository.github_id == github_repo.id
                    ).first()
                    
                    if existing_repo:
                        continue
                    
                    # Create repository record
                    repo = Repository(
                        github_id=github_repo.id,
                        developer_id=developer.id,
                        name=github_repo.name,
                        full_name=github_repo.full_name,
                        description=github_repo.description,
                        language=github_repo.language,
                        languages=github_repo.get_languages() if hasattr(github_repo, 'get_languages') else {},
                        topics=github_repo.get_topics() if hasattr(github_repo, 'get_topics') else [],
                        is_fork=github_repo.fork,
                        is_private=github_repo.private,
                        is_archived=github_repo.archived,
                        stargazers_count=github_repo.stargazers_count,
                        watchers_count=github_repo.watchers_count,
                        forks_count=github_repo.forks_count,
                        open_issues_count=github_repo.open_issues_count,
                        size=github_repo.size,
                        default_branch=github_repo.default_branch,
                        created_at=github_repo.created_at,
                        updated_at=github_repo.updated_at,
                        pushed_at=github_repo.pushed_at,
                        homepage=github_repo.homepage,
                        license_name=github_repo.license.name if github_repo.license else None,
                        has_wiki=github_repo.has_wiki,
                        has_pages=github_repo.has_pages,
                        has_downloads=github_repo.has_downloads,
                        has_issues=github_repo.has_issues,
                        has_projects=github_repo.has_projects,
                        has_discussions=getattr(github_repo, 'has_discussions', False),
                        archived_at=getattr(github_repo, 'archived_at', None),
                        disabled=getattr(github_repo, 'disabled', False),
                        archived=getattr(github_repo, 'archived', False),
                        allow_forking=getattr(github_repo, 'allow_forking', True),
                        is_template=getattr(github_repo, 'is_template', False),
                        web_commit_signoff_required=getattr(github_repo, 'web_commit_signoff_required', False),
                        visibility=getattr(github_repo, 'visibility', 'public'),
                        network_count=getattr(github_repo, 'network_count', 0),
                        subscribers_count=getattr(github_repo, 'subscribers_count', 0)
                    )
                    
                    session.add(repo)
                    session.commit()
                    
                    logger.info(f"Collected repository: {github_repo.full_name}")
                    
                    # Extract skills from repository languages and topics
                    self._extract_repository_skills(session, developer, repo)
                    
                except Exception as e:
                    logger.error(f"Error collecting repository {github_repo.full_name}: {e}")
                    continue
                
                # Rate limiting for repository collection
                time.sleep(settings.rate_limit_delay)
            
            logger.info(f"Collected {len(github_repos)} repositories for {username}")
            
        except Exception as e:
            logger.error(f"Error collecting repositories for {username}: {e}")
    
    def _extract_repository_skills(self, session: Session, developer: Developer, repository: Repository):
        """Extract skills from repository languages and topics"""
        try:
            # Extract skills from languages
            if repository.languages:
                for language, bytes_count in repository.languages.items():
                    if language:
                        self._add_skill_to_developer(session, developer, language.lower(), bytes_count)
            
            # Extract skills from topics
            if repository.topics:
                for topic in repository.topics:
                    if topic:
                        self._add_skill_to_developer(session, developer, topic.lower(), 1)
            
            # Extract skills from primary language
            if repository.language:
                self._add_skill_to_developer(session, developer, repository.language.lower(), 1000)
                
        except Exception as e:
            logger.error(f"Error extracting skills from repository {repository.full_name}: {e}")
    
    def collect_from_stack_overflow(self, max_users: int = 50) -> List[Developer]:
        """Collect developer data from Stack Overflow"""
        logger.info(f"Collecting {max_users} developers from Stack Overflow")
        
        developers = []
        try:
            # Get popular tags and find top users
            popular_tags = ['python', 'javascript', 'java', 'c#', 'php', 'html', 'css', 'sql']
            
            for tag in popular_tags:
                if len(developers) >= max_users:
                    break
                
                users = self.stack_overflow_client.get_top_users_by_tag(tag, page_size=max_users // len(popular_tags))
                
                for user_data in users:
                    if len(developers) >= max_users:
                        break
                    
                    try:
                        developer = self._process_stack_overflow_user(user_data)
                        if developer:
                            developers.append(developer)
                            logger.info(f"Collected Stack Overflow developer: {developer.username}")
                    except Exception as e:
                        logger.error(f"Error processing Stack Overflow user: {e}")
                        continue
                    
                    # Rate limiting
                    time.sleep(settings.rate_limit_delay)
        
        except Exception as e:
            logger.error(f"Error in Stack Overflow collection: {e}")
        
        logger.info(f"Successfully collected {len(developers)} developers from Stack Overflow")
        return developers
    
    def collect_market_data(self) -> Dict[str, Any]:
        """Collect comprehensive job market data from multiple sources and store in database"""
        logger.info("Collecting comprehensive job market data...")
        
        try:
            # Get market data for popular technologies
            technologies = ['python', 'javascript', 'java', 'react', 'node.js', 'aws']
            
            market_data = {
                'technologies': {},
                'overall_trends': {},
                'collection_time': datetime.now().isoformat(),
                'sources': ['github_jobs', 'stack_overflow_jobs', 'indeed_jobs'],
                'jobs_stored': 0
            }
            
            # Get trends for each technology
            technology_trends = self.job_market_aggregator.get_technology_trends(technologies)
            market_data['technologies'] = technology_trends
            
            # Get comprehensive data for Python (as primary example)
            python_market_data = self.job_market_aggregator.get_comprehensive_market_data('python')
            market_data['python_detailed'] = python_market_data
            
            # Store job postings in database
            jobs_stored = self._store_job_postings_in_database(python_market_data)
            market_data['jobs_stored'] = jobs_stored
            
            # Overall market insights
            market_data['overall_trends'] = {
                'total_jobs_analyzed': sum(trend['total_jobs'] for trend in technology_trends.values()),
                'most_demanded_tech': max(technology_trends.items(), key=lambda x: x[1]['total_jobs'])[0] if technology_trends else 'python',
                'average_salary_range': '60k-120k',
                'remote_work_prevalence': 'High',
                'top_locations': ['San Francisco', 'New York', 'London', 'Remote', 'Seattle']
            }
            
            logger.info(f"Successfully collected comprehensive market data and stored {jobs_stored} jobs")
            return market_data
            
        except Exception as e:
            logger.error(f"Error collecting market data: {e}")
            return {
                'error': str(e),
                'collection_time': datetime.now().isoformat(),
                'jobs_stored': 0
            }
    
    def bulk_collect_developers(self, max_developers: int = 100) -> List[Developer]:
        """Bulk collect developers from all sources"""
        logger.info(f"Starting bulk collection of {max_developers} developers")
        
        all_developers = []
        
        try:
            # Collect from GitHub trending (60% of total)
            github_count = int(max_developers * 0.6)
            github_developers = self.collect_from_github_trending(github_count)
            all_developers.extend(github_developers)
            
            # Collect from Stack Overflow (40% of total)
            remaining = max_developers - len(all_developers)
            if remaining > 0:
                so_developers = self.collect_from_stack_overflow(remaining)
                all_developers.extend(so_developers)
            
            logger.info(f"Bulk collection completed. Total developers: {len(all_developers)}")
            
        except Exception as e:
            logger.error(f"Error in bulk collection: {e}")
        
        return all_developers
    
    def collect_repositories_for_existing_developers(self, max_developers: int = 20):
        """Collect repositories for existing developers who don't have repositories"""
        logger.info(f"Collecting repositories for {max_developers} existing developers")
        
        try:
            with db_manager.get_session() as session:
                # Get developers who have GitHub IDs but no repositories
                developers_without_repos = session.query(Developer).filter(
                    Developer.github_id.isnot(None)
                ).outerjoin(Repository).filter(
                    Repository.id.is_(None)
                ).limit(max_developers).all()
                
                logger.info(f"Found {len(developers_without_repos)} developers without repositories")
                
                for developer in developers_without_repos:
                    try:
                        if developer.username and not developer.username.startswith('so_'):
                            self._collect_developer_repositories(session, developer, developer.username)
                            logger.info(f"Collected repositories for: {developer.username}")
                        
                        # Rate limiting
                        time.sleep(settings.rate_limit_delay)
                        
                    except Exception as e:
                        logger.error(f"Error collecting repositories for {developer.username}: {e}")
                        continue
                
                logger.info(f"Repository collection completed for {len(developers_without_repos)} developers")
                
        except Exception as e:
            logger.error(f"Error in repository collection: {e}")
    
    def _store_job_postings_in_database(self, market_data: Dict[str, Any]) -> int:
        """Store job postings from market data in the database"""
        jobs_stored = 0
        
        try:
            with db_manager.get_session() as session:
                # Extract jobs from aggregated trends
                jobs = market_data.get('aggregated_trends', [])
                
                for job_data in jobs:
                    try:
                        # Check if job already exists
                        existing_job = session.query(JobPosting).filter(
                            JobPosting.source_id == job_data.get('id'),
                            JobPosting.data_source == 'market_aggregator'
                        ).first()
                        
                        if existing_job:
                            continue
                        
                        # Create new job posting
                        job_posting = JobPosting(
                            title=job_data.get('title', ''),
                            company=job_data.get('company', ''),
                            location=job_data.get('location', ''),
                            description=job_data.get('description', ''),
                            salary_min=job_data.get('salary_min'),
                            salary_max=job_data.get('salary_max'),
                            salary_currency='USD',
                            job_type=job_data.get('type', 'full-time'),
                            experience_level=self._determine_experience_level(job_data.get('title', '')),
                            remote_option='remote' in job_data.get('location', '').lower(),
                            posted_date=datetime.fromisoformat(job_data.get('created_at', datetime.now().isoformat())),
                            application_url=job_data.get('url', ''),
                            data_source='market_aggregator',
                            source_id=job_data.get('id', '')
                        )
                        
                        session.add(job_posting)
                        jobs_stored += 1
                        
                    except Exception as e:
                        logger.error(f"Error storing job posting: {e}")
                        continue
                
                session.commit()
                logger.info(f"Stored {jobs_stored} new job postings in database")
                
        except Exception as e:
            logger.error(f"Error in job posting storage: {e}")
        
        return jobs_stored
    
    def _determine_experience_level(self, title: str) -> str:
        """Determine experience level from job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['senior', 'lead', 'principal', 'staff']):
            return 'senior'
        elif any(word in title_lower for word in ['junior', 'entry', 'associate']):
            return 'entry'
        else:
            return 'mid'
    
    def collect_commits_for_repositories(self, max_repositories: int = 50):
        """Collect commits for repositories that don't have commits"""
        logger.info(f"Collecting commits for {max_repositories} repositories")
        
        try:
            with db_manager.get_session() as session:
                # Get repositories without commits
                repositories_without_commits = session.query(Repository).outerjoin(Commit).filter(
                    Commit.id.is_(None)
                ).limit(max_repositories).all()
                
                logger.info(f"Found {len(repositories_without_commits)} repositories without commits")
                
                for repository in repositories_without_commits:
                    try:
                        # Get GitHub repository object
                        github_repo = self.github_client.github.get_repo(repository.full_name)
                        
                        # Get commits
                        commits = self.github_client.get_repository_commits(github_repo, max_commits=20)
                        
                        for github_commit in commits:
                            try:
                                # Check if commit already exists
                                existing_commit = session.query(Commit).filter(
                                    Commit.sha == github_commit.sha
                                ).first()
                                
                                if existing_commit:
                                    continue
                                
                                # Create commit record
                                commit = Commit(
                                    repository_id=repository.id,
                                    sha=github_commit.sha,
                                    author_name=github_commit.author.name if github_commit.author else None,
                                    author_email=github_commit.author.email if github_commit.author else None,
                                    committer_name=github_commit.committer.name if github_commit.committer else None,
                                    committer_email=github_commit.committer.email if github_commit.committer else None,
                                    message=github_commit.commit.message,
                                    commit_date=github_commit.commit.author.date,
                                    author_date=github_commit.commit.author.date,
                                    url=github_commit.url,
                                    html_url=github_commit.html_url,
                                    comment_count=getattr(github_commit.commit, 'comment_count', 0),
                                    verification_verified=getattr(github_commit.commit, 'verification', None) and getattr(github_commit.commit.verification, 'verified', False),
                                    verification_reason=getattr(github_commit.commit, 'verification', None) and getattr(github_commit.commit.verification, 'reason', None),
                                    verification_signature=getattr(github_commit.commit, 'verification', None) and getattr(github_commit.commit.verification, 'signature', None),
                                    verification_payload=getattr(github_commit.commit, 'verification', None) and getattr(github_commit.commit.verification, 'payload', None)
                                )
                                
                                session.add(commit)
                                
                            except Exception as e:
                                logger.error(f"Error processing commit {github_commit.sha}: {e}")
                                continue
                        
                        session.commit()
                        logger.info(f"Collected {len(commits)} commits for repository: {repository.full_name}")
                        
                        # Rate limiting
                        time.sleep(settings.rate_limit_delay)
                        
                    except Exception as e:
                        logger.error(f"Error collecting commits for {repository.full_name}: {e}")
                        continue
                
                logger.info(f"Commit collection completed for {len(repositories_without_commits)} repositories")
                
        except Exception as e:
            logger.error(f"Error in commit collection: {e}")
    
    def _process_stack_overflow_user(self, user_data: Dict[str, Any]) -> Optional[Developer]:
        """Process Stack Overflow user data and create/update developer record"""
        try:
            username = f"so_{user_data.get('user_id', 'unknown')}"
            
            # Check if developer already exists
            with db_manager.get_session() as session:
                existing_dev = session.query(Developer).filter(Developer.username == username).first()
                if existing_dev:
                    return existing_dev
                
                # Convert Unix timestamps to datetime objects
                created_at = None
                updated_at = None
                
                if user_data.get('creation_date'):
                    try:
                        created_at = datetime.fromtimestamp(user_data['creation_date'])
                    except (ValueError, TypeError):
                        created_at = datetime.now()
                
                if user_data.get('last_access_date'):
                    try:
                        updated_at = datetime.fromtimestamp(user_data['last_access_date'])
                    except (ValueError, TypeError):
                        updated_at = datetime.now()
                
                # Create new developer record
                developer = Developer(
                    github_id=None,  # Stack Overflow users don't have GitHub IDs
                    username=username,
                    name=user_data.get('display_name', ''),
                    email=None,
                    bio=user_data.get('about_me', ''),
                    location=user_data.get('location', ''),
                    company=None,
                    blog=user_data.get('website_url', ''),
                    twitter_username=None,
                    public_repos=0,
                    public_gists=0,
                    followers=user_data.get('reputation', 0),  # Use reputation as followers
                    following=0,
                    created_at=created_at,
                    updated_at=updated_at
                )
                
                session.add(developer)
                session.commit()
                
                # Extract skills from user's tags
                if 'tags' in user_data:
                    for tag_data in user_data['tags']:
                        tag_name = tag_data.get('tag_name', '').lower()
                        if tag_name:
                            self._add_skill_to_developer(session, developer, tag_name, tag_data.get('answer_count', 1))
                
                return developer
                
        except Exception as e:
            logger.error(f"Error processing Stack Overflow user: {e}")
            return None
    
    def _add_skill_to_developer(self, session: Session, developer: Developer, skill_name: str, usage_count: int = 1):
        """Add or update a skill for a developer"""
        try:
            # Find or create skill
            skill = session.query(Skill).filter(Skill.name == skill_name).first()
            if not skill:
                skill = Skill(
                    name=skill_name,
                    category=self._categorize_skill(skill_name),
                    description=f"Skill: {skill_name}"
                )
                session.add(skill)
                session.commit()
                
            # Check if developer already has this skill
            existing_skill = session.query(DeveloperSkill).filter(
                DeveloperSkill.developer_id == developer.id,
                DeveloperSkill.skill_id == skill.id
            ).first()
            
            if not existing_skill:
                # Calculate proficiency level based on usage count (0.0 to 1.0)
                proficiency_level = min(1.0, usage_count / 1000.0)  # Normalize to 0-1 range
                
                # Add skill to developer
                developer_skill = DeveloperSkill(
                    developer_id=developer.id,
                    skill_id=skill.id,
                    proficiency_level=proficiency_level,
                    usage_frequency=usage_count
                )
                session.add(developer_skill)
                session.commit()
                
        except Exception as e:
            logger.error(f"Error adding skill {skill_name} to developer: {e}")
    
    def _categorize_skill(self, skill_name: str) -> str:
        """Categorize a skill based on its name"""
        skill_lower = skill_name.lower()
        
        if skill_lower in ['python', 'javascript', 'java', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin']:
            return 'programming_language'
        elif skill_lower in ['react', 'vue', 'angular', 'jquery', 'bootstrap', 'css', 'html']:
            return 'frontend'
        elif skill_lower in ['node.js', 'express', 'django', 'flask', 'spring', 'laravel']:
            return 'backend'
        elif skill_lower in ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins']:
            return 'devops'
        elif skill_lower in ['mysql', 'postgresql', 'mongodb', 'redis', 'sql']:
            return 'database'
        elif skill_lower in ['git', 'github', 'gitlab', 'bitbucket']:
            return 'version_control'
        else:
            return 'other' 