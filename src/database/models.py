"""
Database models for DevCareerCompass
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Developer(Base):
    """Developer profile information"""
    __tablename__ = "developers"
    
    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True, nullable=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    blog = Column(String(500), nullable=True)
    twitter_username = Column(String(255), nullable=True)
    public_repos = Column(Integer, default=0, nullable=True)
    public_gists = Column(Integer, default=0, nullable=True)
    followers = Column(Integer, default=0, nullable=True)
    following = Column(Integer, default=0, nullable=True)
    # New field to track data source
    data_source = Column(String(50), default='github', index=True)  # 'github', 'stackoverflow', 'reddit'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    
    # Relationships
    repositories = relationship("Repository", back_populates="developer")
    skills = relationship("DeveloperSkill", back_populates="developer")
    
    def __repr__(self):
        return f"<Developer(username='{self.username}', source='{self.data_source}')>"


class Repository(Base):
    """Repository information"""
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True, nullable=True, index=True)
    developer_id = Column(Integer, ForeignKey("developers.id"), nullable=False)
    name = Column(String(255), nullable=False)
    full_name = Column(String(500), nullable=False)
    description = Column(Text)
    language = Column(String(100))
    languages = Column(JSON)  # Store language statistics as JSON
    topics = Column(JSON)  # Store repository topics as JSON
    is_fork = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    stargazers_count = Column(Integer, default=0)
    watchers_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    open_issues_count = Column(Integer, default=0)
    size = Column(Integer, default=0)
    default_branch = Column(String(100), default="main")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    pushed_at = Column(DateTime)
    homepage = Column(String(500))
    license_name = Column(String(255))
    has_wiki = Column(Boolean, default=False)
    has_pages = Column(Boolean, default=False)
    has_downloads = Column(Boolean, default=False)
    has_issues = Column(Boolean, default=True)
    has_projects = Column(Boolean, default=False)
    has_discussions = Column(Boolean, default=False)
    archived_at = Column(DateTime)
    disabled = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    allow_forking = Column(Boolean, default=True)
    is_template = Column(Boolean, default=False)
    web_commit_signoff_required = Column(Boolean, default=False)
    visibility = Column(String(50))
    network_count = Column(Integer, default=0)
    subscribers_count = Column(Integer, default=0)
    
    # Relationships
    developer = relationship("Developer", back_populates="repositories")
    commits = relationship("Commit", back_populates="repository")
    
    def __repr__(self):
        return f"<Repository(full_name='{self.full_name}')>"


class Commit(Base):
    """Commit information"""
    __tablename__ = "commits"
    
    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    sha = Column(String(40), nullable=False, index=True)
    author_name = Column(String(255))
    author_email = Column(String(255))
    committer_name = Column(String(255))
    committer_email = Column(String(255))
    message = Column(Text, nullable=False)
    commit_date = Column(DateTime, nullable=False)
    author_date = Column(DateTime)
    url = Column(String(500))
    html_url = Column(String(500))
    comment_count = Column(Integer, default=0)
    verification_verified = Column(Boolean, default=False)
    verification_reason = Column(String(255))
    verification_signature = Column(String(255))
    verification_payload = Column(String(255))
    
    # Relationships
    repository = relationship("Repository", back_populates="commits")
    
    def __repr__(self):
        return f"<Commit(sha='{self.sha[:8]}', message='{self.message[:50]}...')>"


class Skill(Base):
    """Skill/topic information"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(100))  # e.g., "programming_language", "framework", "tool"
    description = Column(Text)
    popularity_score = Column(Float, default=0.0)
    market_demand_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    developer_skills = relationship("DeveloperSkill", back_populates="skill")
    
    def __repr__(self):
        return f"<Skill(name='{self.name}', category='{self.category}')>"


class DeveloperSkill(Base):
    """Many-to-many relationship between developers and skills"""
    __tablename__ = "developer_skills"
    
    id = Column(Integer, primary_key=True)
    developer_id = Column(Integer, ForeignKey("developers.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    proficiency_level = Column(Float, default=0.0)  # 0.0 to 1.0
    usage_frequency = Column(Integer, default=0)  # Number of repositories using this skill
    first_used_at = Column(DateTime)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    developer = relationship("Developer", back_populates="skills")
    skill = relationship("Skill", back_populates="developer_skills")
    
    def __repr__(self):
        return f"<DeveloperSkill(developer_id={self.developer_id}, skill_id={self.skill_id})>"


class JobPosting(Base):
    """Job posting information from various sources"""
    __tablename__ = "job_postings"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default='USD')
    job_type = Column(String(50), nullable=True)  # 'full-time', 'part-time', 'contract', 'internship'
    experience_level = Column(String(50), nullable=True)  # 'entry', 'mid', 'senior', 'lead'
    remote_option = Column(Boolean, default=False)
    posted_date = Column(DateTime, nullable=True)
    application_url = Column(String(500), nullable=True)
    # Data source tracking
    data_source = Column(String(50), nullable=False, index=True)  # 'indeed'
    source_id = Column(String(255), nullable=True)  # Original ID from source
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<JobPosting(title='{self.title}', company='{self.company}', source='{self.data_source}')>"


class JobSkill(Base):
    """Skills required for job postings"""
    __tablename__ = "job_skills"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    is_required = Column(Boolean, default=True)
    importance_score = Column(Float, default=1.0)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("JobPosting")
    skill = relationship("Skill")
    
    def __repr__(self):
        return f"<JobSkill(job_id={self.job_id}, skill_id={self.skill_id})>"


class CareerPath(Base):
    """Career path and role information"""
    __tablename__ = "career_paths"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(100))  # e.g., "frontend", "backend", "fullstack", "devops"
    description = Column(Text)
    required_skills = Column(JSON)  # List of skill IDs
    recommended_skills = Column(JSON)  # List of skill IDs
    salary_range_min = Column(Integer)
    salary_range_max = Column(Integer)
    market_demand_score = Column(Float, default=0.0)
    growth_potential_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CareerPath(name='{self.name}', category='{self.category}')>"


# Create indexes for better query performance
Index("idx_developer_github_id", Developer.github_id)
Index("idx_developer_data_source", Developer.data_source)
Index("idx_repository_github_id", Repository.github_id)
Index("idx_commit_sha", Commit.sha)
Index("idx_skill_name", Skill.name)
Index("idx_developer_skill_proficiency", DeveloperSkill.proficiency_level)
Index("idx_job_posting_title", JobPosting.title)
Index("idx_job_posting_company", JobPosting.company)
Index("idx_job_posting_data_source", JobPosting.data_source)
Index("idx_career_path_category", CareerPath.category) 