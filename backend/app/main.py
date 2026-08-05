"""
COMPAREX Backend – FastAPI Application Entry Point

This module creates and configures the FastAPI application instance.
All startup/shutdown logic, middleware, routers, and exception handlers
are wired here using the application factory pattern.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import v1_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.middleware.cors import setup_cors
from app.middleware.error_handler import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.middleware.observability import ObservabilityMiddleware
from app.middleware.security import EnterpriseSecurityMiddleware

# Initialize logging first
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan — runs startup logic before yield
    and shutdown logic after yield.
    """
    # ── Startup ───────────────────────────────────────────────────
    logger.info(
        "Starting %s v%s in %s environment",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.ENVIRONMENT,
    )
    # Phase 2: DB connection warm-up, Redis connection, scheduler start
    yield

    # ── Shutdown ──────────────────────────────────────────────────
    logger.info("Shutting down %s", settings.APP_NAME)
    # Phase 2: Close DB pool, Redis, background tasks


def create_application() -> FastAPI:
    """Application factory — creates and configures the FastAPI instance."""

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
        contact={
            "name": "COMPAREX Support",
            "email": "support@comparex.io",
            "url": "https://comparex.io",
        },
        license_info={
            "name": "MIT",
        },
    )

    # ── Enterprise & CORS Middleware ──────────────────────────────
    # Note: In Starlette/FastAPI, middleware registered last runs first.
    # CORSMiddleware must be registered last to intercept OPTIONS preflight requests.
    app.add_middleware(EnterpriseSecurityMiddleware)
    app.add_middleware(ObservabilityMiddleware)
    setup_cors(app)

    # ── Exception Handlers ────────────────────────────────────────
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ── Root & Utility Endpoints ─────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root():
        return JSONResponse(
            {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "description": settings.APP_DESCRIPTION,
                "status": "online",
                "docs": settings.DOCS_URL,
                "health": "/health",
                "api_v1": settings.API_V1_PREFIX,
            }
        )

    @app.get("/health", include_in_schema=False)
    async def health_root():
        return JSONResponse(
            {
                "status": "ok",
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
            }
        )

    @app.get("/openapi.json", include_in_schema=False)
    async def openapi_root():
        return JSONResponse(app.openapi())

    # ── Routers ───────────────────────────────────────────────────
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)

    return app


# Application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
