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
    # ── Verify Environment Variables ─────────────────────────────────────
    env_keys = {
        "DATABASE_URL": bool(settings.DATABASE_URL),
        "JWT_SECRET": bool(settings.EFFECTIVE_JWT_SECRET),
        "GOOGLE_CLIENT_ID": bool(settings.GOOGLE_CLIENT_ID),
        "GOOGLE_CLIENT_SECRET": bool(settings.GOOGLE_CLIENT_SECRET),
        "GEMINI_API_KEY": bool(settings.GEMINI_API_KEY),
        "RAINFOREST_API_KEY": bool(settings.RAINFOREST_API_KEY),
        "BRIGHTDATA_API_KEY": bool(settings.BRIGHTDATA_API_KEY),
        "SERPAPI_API_KEY": bool(settings.SERPAPI_API_KEY),
        "ZENROWS_API_KEY": bool(settings.ZENROWS_API_KEY),
    }
    missing_envs = [k for k, v in env_keys.items() if not v]
    if missing_envs:
        logger.warning("Production Environment Variables Missing: %s", missing_envs)
    else:
        logger.info("Environment Variables Verified: All 9 required keys present.")

    try:
        from sqlalchemy import inspect, text
        from app.db.base import Base
        from app.db.session import engine
        import app.models  # noqa: F401
        from app.models.product import Product

        # 1. Create all missing ORM tables safely
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 2. Inspect products table columns dynamically
        async with engine.begin() as conn:
            def get_cols(sync_conn):
                inspector = inspect(sync_conn)
                if inspector.has_table("products"):
                    return [c["name"] for c in inspector.get_columns("products")]
                return []

            existing_cols = await conn.run_sync(get_cols)
            logger.info("Products table columns: %s", existing_cols)

            expected_cols = [c.name for c in Product.__table__.columns]
            missing_cols = [c for c in expected_cols if c not in existing_cols]
            logger.info("Missing columns: %s", missing_cols)

            # Column DDL Mappings for Products table
            column_ddls = {
                "rating": "ALTER TABLE products ADD COLUMN IF NOT EXISTS rating FLOAT DEFAULT 4.5;",
                "review_count": (
                    "ALTER TABLE products ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0;"
                ),
                "popularity_score": (
                    "ALTER TABLE products ADD COLUMN IF NOT EXISTS popularity_score FLOAT DEFAULT"
                    " 0.0;"
                ),
                "search_keywords": (
                    "ALTER TABLE products ADD COLUMN IF NOT EXISTS search_keywords TEXT;"
                ),
                "stock_status": (
                    "ALTER TABLE products ADD COLUMN IF NOT EXISTS stock_status VARCHAR(50)"
                    " DEFAULT 'in_stock';"
                ),
                "discount_percentage": (
                    "ALTER TABLE products ADD COLUMN IF NOT EXISTS discount_percentage FLOAT"
                    " DEFAULT 0.0;"
                ),
                "base_price": (
                    "ALTER TABLE products ADD COLUMN IF NOT EXISTS base_price NUMERIC(12, 2);"
                ),
                "category": (
                    "ALTER TABLE products ADD COLUMN IF NOT EXISTS category VARCHAR(255);"
                ),
                "brand": "ALTER TABLE products ADD COLUMN IF NOT EXISTS brand VARCHAR(255);",
                "ean": "ALTER TABLE products ADD COLUMN IF NOT EXISTS ean VARCHAR(50);",
            }

            index_ddls = [
                (
                    "CREATE INDEX IF NOT EXISTS ix_products_category_brand ON products (category,"
                    " brand);"
                ),
                (
                    "CREATE INDEX IF NOT EXISTS ix_products_base_price ON products (base_price);"
                ),
                (
                    "CREATE INDEX IF NOT EXISTS ix_products_popularity ON products"
                    " (popularity_score);"
                ),
                "CREATE INDEX IF NOT EXISTS ix_products_rating ON products (rating);",
                "CREATE INDEX IF NOT EXISTS ix_products_category ON products (category);",
                "CREATE INDEX IF NOT EXISTS ix_products_brand ON products (brand);",
                "CREATE INDEX IF NOT EXISTS ix_products_ean ON products (ean);",
            ]

            # Additional System Table Alterations
            other_ddls = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255);",
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_id ON users (google_id);",
                (
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS login_provider VARCHAR(50)"
                    " DEFAULT 'email' NOT NULL;"
                ),
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;",
                "ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;",
                (
                    "ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS marketplace VARCHAR(100)"
                    " DEFAULT 'All Marketplaces' NOT NULL;"
                ),
                (
                    "ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS notification_method"
                    " VARCHAR(50) DEFAULT 'both' NOT NULL;"
                ),
                (
                    "ALTER TABLE price_history ADD COLUMN IF NOT EXISTS product_id UUID REFERENCES"
                    " products(id) ON DELETE CASCADE;"
                ),
                (
                    "ALTER TABLE price_history ADD COLUMN IF NOT EXISTS marketplace_slug"
                    " VARCHAR(100);"
                ),
                (
                    "CREATE INDEX IF NOT EXISTS ix_price_history_product_id ON price_history"
                    " (product_id);"
                ),
                (
                    "CREATE INDEX IF NOT EXISTS ix_price_history_marketplace_slug ON price_history"
                    " (marketplace_slug);"
                ),
                (
                    "CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications"
                    " (user_id);"
                ),
                (
                    "CREATE INDEX IF NOT EXISTS ix_notifications_is_read ON notifications"
                    " (is_read);"
                ),
            ]

            executed_any = False
            for col in missing_cols:
                if col in column_ddls:
                    await conn.execute(text(column_ddls[col]))
                    executed_any = True

            for idx_stmt in index_ddls + other_ddls:
                await conn.execute(text(idx_stmt))

            if executed_any:
                logger.info(
                    "Migration executed: Added missing columns (%s) to products table.",
                    missing_cols,
                )
            else:
                logger.info("Migration executed: Schema up to date, all Product columns present.")

        logger.info("Schema validation completed.")
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
