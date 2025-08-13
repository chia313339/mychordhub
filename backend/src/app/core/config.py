"""
Application configuration management using Pydantic Settings.
"""
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Server Settings
    SERVER_NAME: str = "MyChordHub API"
    SERVER_HOST: AnyHttpUrl = "https://localhost"  # type: ignore
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "mychordhub"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "mychordhub"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        # Build PostgreSQL URL manually
        values = info.data if hasattr(info, 'data') else {}
        return (
            f"postgresql://{values.get('POSTGRES_USER', 'mychordhub')}:"
            f"{values.get('POSTGRES_PASSWORD', 'password')}@"
            f"{values.get('POSTGRES_SERVER', 'localhost')}:"
            f"{values.get('POSTGRES_PORT', 5432)}/"
            f"{values.get('POSTGRES_DB', 'mychordhub')}"
        )

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379/0"

    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Application Settings
    PROJECT_NAME: str = "MyChordHub"
    DESCRIPTION: str = "Guitar Tab Editing Platform API"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif"]
    
    # Music Settings
    DEFAULT_BPM: int = 120
    MAX_CHORD_POSITIONS: int = 24  # Maximum fret position
    CHORD_CACHE_TTL: int = 3600  # 1 hour in seconds
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()