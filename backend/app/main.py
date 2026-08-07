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


async def verify_and_migrate_db_schema():
    """Verify ORM model columns exist in database and apply auto-migrations on startup."""
    try:
        from sqlalchemy import text
        from app.db.session import engine
        from app.db.base import Base
        import app.models  # noqa: F401

        # 1. Create all missing ORM tables safely
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 2. Check & alter table columns if missing
        async with engine.begin() as conn:
            statements = [
                (
                    "google_id",
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255);",
                ),
                (
                    "google_id_idx",
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_id ON users (google_id);",
                ),
                (
                    "login_provider",
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS login_provider VARCHAR(50) "
                    "DEFAULT 'email' NOT NULL;",
                ),
                ("avatar_url", "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;"),
                (
                    "hashed_password",
                    "ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;",
                ),
                (
                    "price_alerts_mp",
                    "ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS marketplace "
                    "VARCHAR(100) DEFAULT 'All Marketplaces' NOT NULL;",
                ),
                (
                    "price_alerts_method",
                    "ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS notification_method "
                    "VARCHAR(50) DEFAULT 'both' NOT NULL;",
                ),
                (
                    "price_history_pid",
                    "ALTER TABLE price_history ADD COLUMN IF NOT EXISTS product_id "
                    "UUID REFERENCES products(id) ON DELETE CASCADE;",
                ),
                (
                    "price_history_slug",
                    "ALTER TABLE price_history ADD COLUMN IF NOT EXISTS marketplace_slug "
                    "VARCHAR(100);",
                ),
                (
                    "idx_ph_pid",
                    "CREATE INDEX IF NOT EXISTS ix_price_history_product_id "
                    "ON price_history (product_id);",
                ),
                (
                    "idx_ph_slug",
                    "CREATE INDEX IF NOT EXISTS ix_price_history_marketplace_slug "
                    "ON price_history (marketplace_slug);",
                ),
                (
                    "idx_notif_user",
                    "CREATE INDEX IF NOT EXISTS ix_notifications_user_id "
                    "ON notifications (user_id);",
                ),
                (
                    "idx_notif_read",
                    "CREATE INDEX IF NOT EXISTS ix_notifications_is_read "
                    "ON notifications (is_read);",
                ),
            ]

            for key, stmt in statements:
                await conn.execute(text(stmt))

        logger.info(
            "Database schema validation completed cleanly. All ORM tables verified."
        )
    except Exception as exc:
        logger.warning("Startup database schema verification warning: %s", exc)


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
    await verify_and_migrate_db_schema()

    # Start background price monitor service
    import asyncio
    from app.services.price_monitor_service import start_periodic_price_monitor

    monitor_task = asyncio.create_task(start_periodic_price_monitor(interval_seconds=1800))

    yield

    # ── Shutdown ──────────────────────────────────────────────────
    logger.info("Shutting down %s", settings.APP_NAME)
    monitor_task.cancel()
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
