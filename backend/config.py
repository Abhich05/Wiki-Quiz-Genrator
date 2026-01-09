"""
Configuration management with environment variables and validation
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # API Configuration
    app_name: str = "Wiki Quiz Generator"
    app_version: str = "2.0.0"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # AI Configuration
    google_api_key: str
    ai_model: str = "gemini-2.0-flash-exp"
    ai_temperature: float = 0.7
    ai_max_tokens: int = 2048
    ai_timeout: int = 30
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour in seconds
    
    # Caching
    redis_enabled: bool = False
    redis_url: Optional[str] = None
    cache_ttl: int = 3600  # 1 hour
    
    # Database
    database_url: Optional[str] = None
    db_pool_size: int = 5
    db_max_overflow: int = 10
    
    # Security
    cors_origins: list[str] = ["*"]
    allowed_hosts: list[str] = ["*"]
    secret_key: str = "change-this-in-production-super-secret-key-123"
    
    # Monitoring & Logging
    log_level: str = "INFO"
    sentry_dsn: Optional[str] = None
    enable_metrics: bool = True
    
    # Wikipedia Scraping
    wikipedia_timeout: int = 10
    wikipedia_retries: int = 3
    wikipedia_user_agent: str = "WikiQuizBot/2.0 (Educational Purpose)"
    
    # Quiz Configuration
    max_questions_per_quiz: int = 20
    min_questions_per_quiz: int = 3
    default_questions: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
