"""
SIMORGH Platform API - Configuration Management
"""
from functools import lru_cache
from typing import Optional, List

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
    jwt_secret_key: str = "change-this-secret-key-in-production-min-32-chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    argon2_memory_cost: int = 65536
    argon2_time_cost: int = 3
    argon2_parallelism: int = 1

    # AI Providers - OpenAI Compatible
    default_openai_compatible_base_url: Optional[str] = None
    default_openai_compatible_api_key: Optional[str] = None
    
    # Logical Model Configuration (YAML/JSON string or env var)
    # Format: {"reasoning": [{"provider": "openai-compatible", "model": "qwen-72b"}], ...}
    logical_models_config: Optional[str] = None

    # Rate Limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_day: int = 10000

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
