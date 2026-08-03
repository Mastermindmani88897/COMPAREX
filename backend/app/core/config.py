"""
COMPAREX Backend – Core Configuration Module

Loads all settings from environment variables using Pydantic BaseSettings.
All configuration is centralized here — no magic strings elsewhere.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────
    APP_NAME: str = "COMPAREX"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI Shopping Intelligence Platform API"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True

    # ── Server ────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── API ───────────────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"

    # ── CORS ──────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: List[str] = ["*"]

    # ── Database ──────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/comparex"
    DATABASE_ECHO: bool = False

    # ── Auth (JWT) ────────────────────────────────────────────────
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Redis (Phase 2) ───────────────────────────────────────────
    REDIS_URL: Optional[str] = None

    # ── Email (Phase 2) ───────────────────────────────────────────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # ── Logging ───────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" | "text"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance (singleton pattern)."""
    return Settings()


settings = get_settings()
