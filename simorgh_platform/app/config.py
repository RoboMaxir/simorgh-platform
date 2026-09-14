"""
SIMORGH Platform API - Configuration Management
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "SIMORGH Platform API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/simorgh_platform"

    # Security
    secret_key: str = "change-this-secret-key-in-production-min-32-chars"
    access_token_expire_minutes: int = 30
    api_key_prefix: str = "sph_"

    # AI Providers
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    qwen_api_key: Optional[str] = None
    local_llm_endpoint: Optional[str] = None

    # Rate Limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_ai_requests_per_hour: int = 100

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
