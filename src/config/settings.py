"""
Application settings and configuration management
"""
import os
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # GitHub API Configuration
    github_token: Optional[str] = Field(None, env="GITHUB_TOKEN")
    github_api_base_url: str = Field("https://api.github.com", env="GITHUB_API_BASE_URL")
    
    # Database Configuration
    database_url: str = Field("sqlite:///./devcareer_compass.db", env="DATABASE_URL")
    
    # Qdrant Cloud Vector Database Configuration
    qdrant_cloud_url: Optional[str] = Field(None, env="QDRANT_CLOUD_URL")
    qdrant_api_key: Optional[str] = Field(None, env="QDRANT_API_KEY")
    
    # Application Configuration
    app_env: str = Field("development", env="APP_ENV")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    debug: bool = Field(True, env="DEBUG")
    
    # Data Collection Configuration
    max_repositories_per_user: int = Field(100, env="MAX_REPOSITORIES_PER_USER")
    max_commits_per_repository: int = Field(1000, env="MAX_COMMITS_PER_REPOSITORY")
    rate_limit_delay: float = Field(1.0, env="RATE_LIMIT_DELAY")
    max_developers_to_collect: int = Field(100, env="MAX_DEVELOPERS_TO_COLLECT")
    
    # Stack Overflow API Configuration
    stack_overflow_api_key: Optional[str] = Field(None, env="STACK_OVERFLOW_KEY")
    stack_overflow_api_base_url: str = Field("https://api.stackexchange.com/2.3", env="STACK_OVERFLOW_API_BASE_URL")
    
    # Reddit API Configuration
    reddit_client_id: Optional[str] = Field(None, env="REDDIT_CLIENT_ID")
    reddit_client_secret: Optional[str] = Field(None, env="REDDIT_CLIENT_SECRET")
    reddit_user_agent: Optional[str] = Field(None, env="REDDIT_USER_AGENT")
    reddit_username: Optional[str] = Field(None, env="REDDIT_USERNAME")
    reddit_password: Optional[str] = Field(None, env="REDDIT_PASSWORD")
    

    
    # Indeed API Configuration (X-Rapid)
    xrapid_api_key: Optional[str] = Field(None, env="XRAPID_API_KEY")
    
    # Adjuna API Configuration
    adjuna_app_id: Optional[str] = Field(None, env="ADZUNA_APP_ID")
    adjuna_app_key: Optional[str] = Field(None, env="ADZUNA_APP_KEY")
    adjuna_api_base_url: str = Field("https://api.adzuna.com/v1", env="ADJUNA_API_BASE_URL")
    
    # OpenAI API Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings 