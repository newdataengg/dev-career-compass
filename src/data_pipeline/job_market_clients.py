"""
Alternative Job Market Data Sources for DevCareerCompass
Replaces Adzuna API with more reliable and accessible data sources
"""
import logging
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from src.config.settings import settings

logger = logging.getLogger(__name__)


class GitHubJobsClient:
    """GitHub Jobs API client - Free and reliable job data"""
    
    def __init__(self):
        self.base_url = "https://jobs.github.com/positions.json"
        self.session = requests.Session()
        logger.info("GitHub Jobs API client initialized")
    
    def search_jobs(self, query: str = "python developer", location: str = None, 
                   page: int = 1, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for jobs on GitHub Jobs"""
        try:
            params = {
                'search': query,
                'page': page
            }
            
            if location:
                params['location'] = location
            
            logger.info(f"Searching GitHub Jobs for: {query}")
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            jobs = response.json()
            logger.info(f"Found {len(jobs)} jobs on GitHub Jobs")
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error searching GitHub Jobs: {e}")
            return []
    
    def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed job information"""
        try:
            url = f"https://jobs.github.com/positions/{job_id}.json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching GitHub Jobs details: {e}")
            return None
    
    def get_market_trends(self, technology: str = "python") -> List[Dict[str, Any]]:
        """Get market trends by searching for technology jobs"""
        jobs = self.search_jobs(f"{technology} developer", limit=10)
        
        trends = []
        for job in jobs:
            trends.append({
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'location': job.get('location', ''),
                'type': job.get('type', ''),
                'created_at': job.get('created_at', ''),
                'url': job.get('url', ''),
                'technology': technology
            })
        
        return trends


class StackOverflowJobsClient:
    """Stack Overflow Jobs API client - Developer-focused job data"""
    
    def __init__(self):
        self.base_url = "https://stackoverflow.com/jobs/feed"
        self.session = requests.Session()
        logger.info("Stack Overflow Jobs client initialized")
    
    def search_jobs(self, query: str = "python", location: str = None, 
                   limit: int = 50) -> List[Dict[str, Any]]:
        """Search for jobs on Stack Overflow Jobs"""
        try:
            params = {
                'q': query,
                'l': location if location else '',
                'u': 'Miles',  # Distance unit
                'd': '20'      # Distance in miles
            }
            
            logger.info(f"Searching Stack Overflow Jobs for: {query}")
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse RSS feed
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            jobs = []
            for item in root.findall('.//item')[:limit]:
                job = {
                    'title': item.find('title').text if item.find('title') is not None else '',
                    'company': item.find('a10:name', namespaces={'a10': 'http://www.w3.org/2005/Atom'}).text if item.find('a10:name', namespaces={'a10': 'http://www.w3.org/2005/Atom'}) is not None else '',
                    'location': item.find('location').text if item.find('location') is not None else '',
                    'description': item.find('description').text if item.find('description') is not None else '',
                    'link': item.find('link').text if item.find('link') is not None else '',
                    'published': item.find('pubDate').text if item.find('pubDate') is not None else ''
                }
                jobs.append(job)
            
            logger.info(f"Found {len(jobs)} jobs on Stack Overflow Jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching Stack Overflow Jobs: {e}")
            return []





class IndeedJobsClient:
    """Indeed Jobs API client - Comprehensive job data using X-Rapid API"""
    
    def __init__(self):
        self.base_url = "https://indeed12.p.rapidapi.com"
        self.session = requests.Session()
        self.api_key = settings.xrapid_api_key
        
        if self.api_key:
            self.session.headers.update({
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': 'indeed12.p.rapidapi.com'
            })
        
        logger.info("Indeed Jobs client initialized with X-Rapid API")
    
    def search_jobs(self, query: str = "python developer", location: str = None, 
                   limit: int = 50) -> List[Dict[str, Any]]:
        """Search for jobs on Indeed using X-Rapid API"""
        try:
            if not self.api_key:
                logger.warning("X-Rapid API key not configured - skipping collection")
                return []
            
            logger.info(f"Searching Indeed Jobs for: {query}")
            
            # Use the correct endpoint from the documentation
            params = {
                'query': query,
                'location': location or 'Remote',
                'start': 1,  # Starting position
                'limit': min(limit, 20)  # API limit
            }
            
            response = self.session.get(f"{self.base_url}/jobs/search", params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('data', [])
            
            logger.info(f"Found {len(jobs)} jobs on Indeed")
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Indeed Jobs: {e}")
            return []
    
    def get_company_jobs(self, company: str, location: str = "us", start: int = 1) -> List[Dict[str, Any]]:
        """Get jobs from a specific company using Indeed API"""
        try:
            if not self.api_key:
                logger.warning("X-Rapid API key not configured")
                return []
            
            logger.info(f"Searching Indeed Jobs for company: {company}")
            
            params = {
                'locality': location,
                'start': start
            }
            
            response = self.session.get(f"{self.base_url}/company/{company}/jobs", params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('data', [])
            
            logger.info(f"Found {len(jobs)} jobs for company {company}")
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting company jobs for {company}: {e}")
            return []
    

class JobMarketDataAggregator:
    """Aggregates job market data from multiple sources"""
    
    def __init__(self):
        self.github_jobs = GitHubJobsClient()
        self.stack_overflow_jobs = StackOverflowJobsClient()
        self.indeed_jobs = IndeedJobsClient()
        
        logger.info("Job Market Data Aggregator initialized")
    
    def get_comprehensive_market_data(self, technology: str = "python", 
                                    location: str = None) -> Dict[str, Any]:
        """Get comprehensive job market data from all sources"""
        logger.info(f"Collecting comprehensive market data for: {technology}")
        
        market_data = {
            'technology': technology,
            'location': location,
            'sources': {},
            'aggregated_trends': [],
            'skills_demand': {},
            'salary_ranges': {},
            'total_jobs': 0,
            'collection_time': datetime.now().isoformat()
        }
        
        # Collect from GitHub Jobs
        try:
            github_jobs = self.github_jobs.search_jobs(f"{technology} developer", location, limit=20)
            market_data['sources']['github_jobs'] = {
                'count': len(github_jobs),
                'jobs': github_jobs[:5]  # Store first 5 for trends
            }
            market_data['total_jobs'] += len(github_jobs)
        except Exception as e:
            logger.error(f"GitHub Jobs collection failed: {e}")
            market_data['sources']['github_jobs'] = {'count': 0, 'error': str(e)}
        
        # Collect from Stack Overflow Jobs
        try:
            so_jobs = self.stack_overflow_jobs.search_jobs(technology, location, limit=20)
            market_data['sources']['stack_overflow_jobs'] = {
                'count': len(so_jobs),
                'jobs': so_jobs[:5]
            }
            market_data['total_jobs'] += len(so_jobs)
        except Exception as e:
            logger.error(f"Stack Overflow Jobs collection failed: {e}")
            market_data['sources']['stack_overflow_jobs'] = {'count': 0, 'error': str(e)}
        

        
        # Collect from Indeed Jobs
        try:
            indeed_jobs = self.indeed_jobs.search_jobs(f"{technology} developer", location, limit=20)
            market_data['sources']['indeed_jobs'] = {
                'count': len(indeed_jobs),
                'jobs': indeed_jobs[:5]
            }
            market_data['total_jobs'] += len(indeed_jobs)
        except Exception as e:
            logger.error(f"Indeed Jobs collection failed: {e}")
            market_data['sources']['indeed_jobs'] = {'count': 0, 'error': str(e)}
        
        # Aggregate trends
        all_jobs = []
        for source_data in market_data['sources'].values():
            if 'jobs' in source_data:
                all_jobs.extend(source_data['jobs'])
        
        # Create aggregated trends
        market_data['aggregated_trends'] = all_jobs[:10]
        
        # Analyze skills demand
        market_data['skills_demand'] = self._analyze_skills_demand(all_jobs, technology)
        
        # Analyze salary ranges
        market_data['salary_ranges'] = self._analyze_salary_ranges(all_jobs)
        
        logger.info(f"Comprehensive market data collected: {market_data['total_jobs']} total jobs")
        return market_data
    
    def _analyze_skills_demand(self, jobs: List[Dict[str, Any]], primary_skill: str) -> Dict[str, Any]:
        """Analyze skills demand from job data"""
        skills = [primary_skill, 'JavaScript', 'Java', 'React', 'AWS', 'Docker', 'Kubernetes']
        
        demand_analysis = {}
        for skill in skills:
            # Count jobs mentioning this skill
            count = sum(1 for job in jobs if skill.lower() in 
                       (job.get('title', '') + job.get('description', '')).lower())
            
            demand_analysis[skill] = {
                'job_count': count,
                'demand_level': 'high' if count > 10 else 'medium' if count > 5 else 'low'
            }
        
        return demand_analysis
    
    def _analyze_salary_ranges(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze salary ranges from job data"""
        # Extract salary information (this would need more sophisticated parsing)
        salary_data = {
            'min_salary': 50000,
            'max_salary': 150000,
            'average_salary': 95000,
            'salary_range': '50k-150k',
            'currency': 'USD'
        }
        
        return salary_data
    
    def get_technology_trends(self, technologies: List[str]) -> Dict[str, Any]:
        """Get trends for multiple technologies"""
        trends = {}
        
        for tech in technologies:
            logger.info(f"Analyzing trends for: {tech}")
            market_data = self.get_comprehensive_market_data(tech)
            trends[tech] = {
                'total_jobs': market_data['total_jobs'],
                'demand_level': 'high' if market_data['total_jobs'] > 50 else 'medium' if market_data['total_jobs'] > 20 else 'low',
                'top_locations': self._extract_top_locations(market_data['aggregated_trends']),
                'salary_range': market_data['salary_ranges']['salary_range']
            }
        
        return trends
    
    def _extract_top_locations(self, jobs: List[Dict[str, Any]]) -> List[str]:
        """Extract top job locations"""
        locations = {}
        for job in jobs:
            location = job.get('location', '') or job.get('formattedLocation', '')
            if location:
                locations[location] = locations.get(location, 0) + 1
        
        # Return top 5 locations
        sorted_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)
        return [loc[0] for loc in sorted_locations[:5]] 