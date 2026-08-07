"""
COMPAREX Backend – CORS Configuration

Configures Cross-Origin Resource Sharing for the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    """Attach CORS middleware to the FastAPI application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_origin_regex=(
            r"https://.*\.vercel\.app|https://.*\.onrender\.com|"
            r"http://localhost:\d+|http://127\.0\.0\.1:\d+"
        ),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
