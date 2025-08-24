"""
GitHub API client for data collection
"""
import time
import logging
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
from github import Github, GithubException
from github.Repository import Repository as GithubRepository
from github.Commit import Commit as GithubCommit
from github.NamedUser import NamedUser as GithubUser

from src.config.settings import settings

logger = logging.getLogger(__name__)


class GitHubClient:
    """GitHub API client with rate limiting and error handling"""
    
    def __init__(self):
        if settings.github_token:
            self.github = Github(settings.github_token)
        else:
            self.github = None
            logger.warning("GitHub token not provided. GitHub API features will be disabled.")
        self.rate_limit_delay = settings.rate_limit_delay
        self._last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        self._last_request_time = time.time()
    
    def get_user(self, username: str) -> Optional[GithubUser]:
        """Get GitHub user information"""
        if not self.github:
            logger.warning("GitHub API not available. Token not provided.")
            return None
        try:
            self._rate_limit()
            user = self.github.get_user(username)
            logger.info(f"Retrieved user: {username}")
            return user
        except GithubException as e:
            logger.error(f"Error retrieving user {username}: {e}")
            return None
    
    def get_user_repositories(self, username: str, max_repos: int = None) -> List[GithubRepository]:
        """Get repositories for a user"""
        try:
            self._rate_limit()
            user = self.get_user(username)
            if not user:
                return []
            
            max_repos = max_repos or settings.max_repositories_per_user
            repos = list(user.get_repos()[:max_repos])
            logger.info(f"Retrieved {len(repos)} repositories for user: {username}")
            return repos
        except GithubException as e:
            logger.error(f"Error retrieving repositories for {username}: {e}")
            return []
    
    def get_repository_commits(self, repo: GithubRepository, max_commits: int = None) -> List[GithubCommit]:
        """Get commits for a repository"""
        try:
            self._rate_limit()
            max_commits = max_commits or settings.max_commits_per_repository
            commits = list(repo.get_commits()[:max_commits])
            logger.info(f"Retrieved {len(commits)} commits for repository: {repo.full_name}")
            return commits
        except GithubException as e:
            logger.error(f"Error retrieving commits for {repo.full_name}: {e}")
            return []
    
    def get_repository_languages(self, repo: GithubRepository) -> Dict[str, int]:
        """Get language statistics for a repository"""
        try:
            self._rate_limit()
            languages = repo.get_languages()
            logger.debug(f"Retrieved languages for {repo.full_name}: {languages}")
            return languages
        except GithubException as e:
            logger.error(f"Error retrieving languages for {repo.full_name}: {e}")
            return {}
    
    def get_repository_topics(self, repo: GithubRepository) -> List[str]:
        """Get topics for a repository"""
        try:
            self._rate_limit()
            topics = repo.get_topics()
            logger.debug(f"Retrieved topics for {repo.full_name}: {topics}")
            return topics
        except GithubException as e:
            logger.error(f"Error retrieving topics for {repo.full_name}: {e}")
            return []
    
    def search_users(self, query: str, max_results: int = 10) -> List[GithubUser]:
        """Search for GitHub users"""
        if not self.github:
            logger.warning("GitHub API not available. Token not provided.")
            return []
        try:
            self._rate_limit()
            users = self.github.search_users(query=query)
            results = list(users[:max_results])
            logger.info(f"Found {len(results)} users for query: {query}")
            return results
        except GithubException as e:
            logger.error(f"Error searching users with query '{query}': {e}")
            return []
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        try:
            rate_limit = self.github.get_rate_limit()
            return {
                "core": {
                    "limit": rate_limit.core.limit,
                    "remaining": rate_limit.core.remaining,
                    "reset": datetime.fromtimestamp(rate_limit.core.reset.timestamp())
                },
                "search": {
                    "limit": rate_limit.search.limit,
                    "remaining": rate_limit.search.remaining,
                    "reset": datetime.fromtimestamp(rate_limit.search.reset.timestamp())
                }
            }
        except GithubException as e:
            logger.error(f"Error getting rate limit status: {e}")
            return {}
    
    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited"""
        status = self.get_rate_limit_status()
        core_remaining = status.get("core", {}).get("remaining", 0)
        return core_remaining <= 0
    
    def wait_for_rate_limit_reset(self):
        """Wait until rate limit resets"""
        status = self.get_rate_limit_status()
        core_reset = status.get("core", {}).get("reset")
        if core_reset:
            wait_time = (core_reset - datetime.now()).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limited. Waiting {wait_time:.0f} seconds for reset...")
                time.sleep(wait_time + 1)  # Add 1 second buffer
    
    def get_trending_repositories(self, language: str = None, time_range: str = 'daily') -> List[Dict[str, Any]]:
        """Get trending repositories using GitHub Search API"""
        try:
            self._rate_limit()
            
            # Use GitHub Search API to find popular repositories
            # by searching for repositories with high star counts in the specified language
            query = f"language:{language}" if language else "stars:>100"
            
            # Convert time_range to proper date format
            if time_range == 'daily':
                # Search for repositories created in the last 7 days
                from datetime import datetime, timedelta
                week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                query += f" created:>={week_ago}"
            elif time_range == 'weekly':
                # Search for repositories created in the last 30 days
                from datetime import datetime, timedelta
                month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                query += f" created:>={month_ago}"
            elif time_range == 'monthly':
                # Search for repositories created in the last 90 days
                from datetime import datetime, timedelta
                three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
                query += f" created:>={three_months_ago}"
            
            repos = self.github.search_repositories(
                query=query,
                sort="stars",
                order="desc"
            )
            
            trending_repos = []
            for repo in repos[:20]:  # Get top 20 trending repos
                trending_repos.append({
                    'id': repo.id,
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'owner': {
                        'login': repo.owner.login,
                        'id': repo.owner.id,
                        'type': repo.owner.type
                    },
                    'created_at': repo.created_at.isoformat() if repo.created_at else None,
                    'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                    'html_url': repo.html_url,
                    'clone_url': repo.clone_url
                })
            
            logger.info(f"Retrieved {len(trending_repos)} trending repositories for language: {language}")
            return trending_repos
            
        except GithubException as e:
            logger.error(f"Error retrieving trending repositories for language {language}: {e}")
            return [] 