"""Application configuration."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://buyer@localhost:5432/data_analytics"
    )
    direct_database_url: Optional[str] = os.getenv("DIRECT_DATABASE_URL")
    
    # API
    api_title: str = "Analytics Dashboard API"
    api_version: str = "v1"
    api_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Cache
    cache_ttl: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()

