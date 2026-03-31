"""
Configuration management using Pydantic Settings
Loads from environment variables and .env file
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5678"]

    # Claude AI
    ANTHROPIC_API_KEY: str = Field(..., env="ANTHROPIC_API_KEY")
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    CLAUDE_MAX_TOKENS: int = 4096

    # Database
    DATABASE_URL: str = "sqlite:///./data/search_score_send.db"
    DATABASE_ENCRYPTION_KEY: str = Field(..., env="DATABASE_ENCRYPTION_KEY")

    # n8n
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook"
    N8N_API_URL: str = "http://localhost:5678/api/v1"
    N8N_API_KEY: str = Field(default="", env="N8N_API_KEY")

    # HITL
    HITL_APPROVAL_TIMEOUT_MINUTES: int = 60
    HITL_FINAL_APPROVAL_TIMEOUT_HOURS: int = 24
    DEFAULT_REVIEWER_EMAIL: str = Field(..., env="DEFAULT_REVIEWER_EMAIL")

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = Field(..., env="SMTP_USER")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    SMTP_FROM: str = "noreply@search-score-send.com"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # GDPR
    DATA_RETENTION_DAYS: int = 180
    ANONYMIZATION_ENABLED: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/api.log"

    # Search Platform APIs
    LINKEDIN_API_KEY: str = Field(default="", env="LINKEDIN_API_KEY")
    GITHUB_API_KEY: str = Field(default="", env="GITHUB_API_KEY")
    STACKOVERFLOW_API_KEY: str = Field(default="", env="STACKOVERFLOW_API_KEY")

    # Feature Flags
    ENABLE_HITL: bool = True
    ENABLE_SSE_PROGRESS: bool = True
    ENABLE_AUDIT_LOGGING: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure log directory exists
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

# Ensure data directory exists
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
