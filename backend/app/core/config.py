"""
COMPAREX Backend – Core Configuration Module

Loads all settings from environment variables using Pydantic BaseSettings.
All configuration is centralized here — no magic strings elsewhere.
"""

import re
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
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
    ENVIRONMENT: str = Field(
        default="development",
        pattern="^(development|staging|production)$",
    )
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
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/comparex"
    DATABASE_ECHO: bool = False

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Ensure database URL uses postgresql+asyncpg protocol and asyncpg SSL parameters."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)

        url = url.replace("sslmode=require", "ssl=require").replace("sslmode=prefer", "ssl=prefer")
        if "channel_binding=" in url:
            url = re.sub(r"&?channel_binding=[^&]+", "", url)
        return url

    # ── Auth (JWT) ────────────────────────────────────────────────
    SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_SECRET: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @property
    def EFFECTIVE_JWT_SECRET(self) -> str:
        """Use JWT_SECRET if defined, otherwise fallback to SECRET_KEY."""
        return self.JWT_SECRET or self.SECRET_KEY

    # ── Upstash Redis ─────────────────────────────────────────────
    REDIS_URL: Optional[str] = None
    UPSTASH_REDIS_REST_URL: Optional[str] = None
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = None

    # ── Email ──────────────────────────────────────────────────────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # ── Logging ───────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # "json" | "text"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance (singleton pattern)."""
    return Settings()


settings = get_settings()
