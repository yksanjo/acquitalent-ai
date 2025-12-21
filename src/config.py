"""Configuration management for AcquiTalent AI"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    anthropic_api_key: str
    openai_api_key: Optional[str] = None
    apify_api_token: Optional[str] = None
    listen_notes_api_key: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    eventbrite_token: Optional[str] = None
    instantly_api_key: Optional[str] = None
    instantly_workspace_id: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./acquitalent.db"
    
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    frontend_url: str = "http://localhost:3000"
    
    # Signal Fusion Settings
    min_openness_score: int = 70
    max_candidates_per_day: int = 100  # LinkedIn rate limit safety
    
    # Outreach Settings
    target_open_rate: float = 0.20
    target_reply_rate: float = 0.05
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

