"""
Stack Overflow API client for collecting developer data
"""
import logging
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.config.settings import settings

logger = logging.getLogger(__name__)


class StackOverflowClient:
    """Client for interacting with Stack Overflow API"""
    
    def __init__(self):
        self.api_key = settings.stack_overflow_api_key
        self.base_url = settings.stack_overflow_api_base_url
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile from Stack Overflow"""
        try:
            url = f"{self.base_url}/users/{user_id}"
            params = {
                'site': 'stackoverflow',
                'key': self.api_key if self.api_key else None
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if 'items' in data and data['items']:
                return data['items'][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Stack Overflow user {user_id}: {e}")
            return None
    
    def search_users(self, query: str = "python", page: int = 1, page_size: int = 30) -> List[Dict[str, Any]]:
        """Search for users on Stack Overflow"""
        try:
            url = f"{self.base_url}/users"
            params = {
                'site': 'stackoverflow',
                'inname': query,
                'page': page,
                'pagesize': page_size,
                'order': 'desc',
                'sort': 'reputation',
                'key': self.api_key if self.api_key else None
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except Exception as e:
            logger.error(f"Error searching Stack Overflow users: {e}")
            return []
    
    def get_user_answers(self, user_id: int, page: int = 1, page_size: int = 30) -> List[Dict[str, Any]]:
        """Get user's answers from Stack Overflow"""
        try:
            url = f"{self.base_url}/users/{user_id}/answers"
            params = {
                'site': 'stackoverflow',
                'page': page,
                'pagesize': page_size,
                'order': 'desc',
                'sort': 'activity',
                'key': self.api_key if self.api_key else None
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except Exception as e:
            logger.error(f"Error fetching Stack Overflow answers for user {user_id}: {e}")
            return []
    
    def get_user_questions(self, user_id: int, page: int = 1, page_size: int = 30) -> List[Dict[str, Any]]:
        """Get user's questions from Stack Overflow"""
        try:
            url = f"{self.base_url}/users/{user_id}/questions"
            params = {
                'site': 'stackoverflow',
                'page': page,
                'pagesize': page_size,
                'order': 'desc',
                'sort': 'activity',
                'key': self.api_key if self.api_key else None
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except Exception as e:
            logger.error(f"Error fetching Stack Overflow questions for user {user_id}: {e}")
            return []
    
    def get_user_tags(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's top tags from Stack Overflow"""
        try:
            url = f"{self.base_url}/users/{user_id}/top-tags"
            params = {
                'site': 'stackoverflow',
                'key': self.api_key if self.api_key else None
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except Exception as e:
            logger.error(f"Error fetching Stack Overflow tags for user {user_id}: {e}")
            return []
    
    def get_top_users_by_tag(self, tag: str, page: int = 1, page_size: int = 30) -> List[Dict[str, Any]]:
        """Get top users for a specific tag"""
        try:
            url = f"{self.base_url}/users"
            params = {
                'site': 'stackoverflow',
                'page': page,
                'pagesize': page_size,
                'order': 'desc',
                'sort': 'reputation',
                'key': self.api_key if self.api_key else None
            }
            
            # Add tag filter if provided
            if tag:
                params['inname'] = tag
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except Exception as e:
            logger.error(f"Error fetching top users for tag {tag}: {e}")
            return []
    
    def get_popular_tags(self) -> List[Dict[str, Any]]:
        """Get popular tags on Stack Overflow"""
        try:
            url = f"{self.base_url}/tags"
            params = {
                'site': 'stackoverflow',
                'order': 'desc',
                'sort': 'popular',
                'pagesize': 100,
                'key': self.api_key if self.api_key else None
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except Exception as e:
            logger.error(f"Error fetching popular tags: {e}")
            return []
    
    def rate_limit_delay(self):
        """Respect rate limits"""
        time.sleep(settings.rate_limit_delay) 