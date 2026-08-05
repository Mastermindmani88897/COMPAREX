"""
COMPAREX Backend – Core Configuration Module

Loads all settings from environment variables using Pydantic BaseSettings.
All configuration is centralized here — no magic strings elsewhere.
"""

import json
import re
from functools import lru_cache
from typing import Any, List, Optional, Union

from pydantic import field_validator
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
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def parse_environment(cls, v: Any) -> str:
        if isinstance(v, str):
            v_clean = v.strip().lower()
            if v_clean in ("prod", "production"):
                return "production"
            if v_clean in ("stage", "staging"):
                return "staging"
            if v_clean in ("dev", "development"):
                return "development"
            return v_clean
        return "development"

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
        "https://comparex-eight.vercel.app",
        "https://comparex-backend-33jp.onrender.com",
    ]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: List[str] = ["*"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

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
        elif url.startswith("sqlite://") and not url.startswith("sqlite+aiosqlite://"):
            url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)

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

    # ── Official Marketplace & Third-Party APIs ─────────────────
    AMAZON_PAAPI_KEY: Optional[str] = None
    AMAZON_PAAPI_SECRET: Optional[str] = None
    FLIPKART_AFFILIATE_ID: Optional[str] = None
    FLIPKART_AFFILIATE_TOKEN: Optional[str] = None
    THIRD_PARTY_SHOPPING_API_KEY: Optional[str] = None
    THIRD_PARTY_SHOPPING_PROVIDER: Optional[str] = "shopping_api"

    # ── Google OAuth & Gemini AI ──────────────────────────────────
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "gemini"

    # ── Logging ───────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # "json" | "text"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance (singleton pattern)."""
    return Settings()


settings = get_settings()
