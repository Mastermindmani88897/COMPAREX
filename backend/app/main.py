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
        import os
        from alembic import command
        from alembic.config import Config
        from sqlalchemy import inspect, text
        from app.db.base import Base
        from app.db.session import engine
        import app.models  # noqa: F401
        from app.models.product import Product

        # 1. Programmatically run Alembic upgrade head
        def run_alembic(sync_conn):
            try:
                main_dir = os.path.dirname(os.path.abspath(__file__))
                base_dir = os.path.dirname(os.path.dirname(main_dir))
                ini_path = os.path.join(base_dir, "alembic.ini")
                if os.path.exists(ini_path):
                    cfg = Config(ini_path)
                    if settings.DATABASE_URL:
                        raw_url = settings.DATABASE_URL
                        db_url = raw_url.replace("postgresql+asyncpg://", "postgresql://")
                        cfg.set_main_option("sqlalchemy.url", db_url)
                    command.upgrade(cfg, "head")
                    logger.info("Alembic programmatic migration upgrade to head succeeded.")
            except Exception as a_exc:
                logger.warning("Alembic programmatic migration notice: %s", a_exc)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(run_alembic)

        # 2. Inspect products table columns dynamically and self-heal
        async with engine.begin() as conn:
            def get_cols(sync_conn):
                inspector = inspect(sync_conn)
                if inspector.has_table("products"):
                    return [c["name"] for c in inspector.get_columns("products")]
                return []

            existing_cols = await conn.run_sync(get_cols)
            logger.info("Products table columns in DB: %s", existing_cols)

            expected_cols = [c.name for c in Product.__table__.columns]
            missing_cols = [c for c in expected_cols if c not in existing_cols]

            column_ddls = {
                "normalized_name": (
                    "ALTER TABLE products ADD COLUMN IF NOT EXISTS normalized_name VARCHAR(500);"
                ),
                "model_name": (
                    "ALTER TABLE products ADD COLUMN IF NOT EXISTS model_name VARCHAR(255);"
                ),
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
                    "CREATE INDEX IF NOT EXISTS ix_products_normalized_name ON products"
                    " (normalized_name);"
                ),
                "CREATE INDEX IF NOT EXISTS ix_products_model_name ON products (model_name);",
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
                (
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_user_product_wishlist ON wishlist_items"
                    " (user_id, product_id);"
                ),
            ]

            other_ddls = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(50);",
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username);",
                (
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username_lower ON users"
                    " (LOWER(username));"
                ),
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
                    "CREATE TABLE IF NOT EXISTS product_views ("
                    " id UUID PRIMARY KEY DEFAULT gen_random_uuid(),"
                    " user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,"
                    " product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,"
                    " viewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),"
                    " price_at_view NUMERIC(12, 2),"
                    " CONSTRAINT uq_user_product_view UNIQUE (user_id, product_id)"
                    ");"
                ),
                "CREATE INDEX IF NOT EXISTS ix_product_views_user_id ON product_views (user_id);",
                (
                    "CREATE INDEX IF NOT EXISTS ix_product_views_product_id ON product_views "
                    "(product_id);"
                ),
                (
                    "CREATE INDEX IF NOT EXISTS ix_product_views_viewed_at ON product_views "
                    "(viewed_at DESC);"
                ),
            ]

            for col in missing_cols:
                if col in column_ddls:
                    await conn.execute(text(column_ddls[col]))

            for idx_stmt in index_ddls + other_ddls:
                await conn.execute(text(idx_stmt))

            # Data repair: map orphaned price_history rows to existing product listings
            repair_stmt = (
                "UPDATE price_history SET listing_id = ("
                "  SELECT id FROM product_listings "
                "  WHERE product_listings.product_id = price_history.product_id "
                "  LIMIT 1"
                ") WHERE listing_id IS NULL AND product_id IS NOT NULL;"
            )
            await conn.execute(text(repair_stmt))

            # Clean any unmappable orphaned price_history records
            clean_orphaned = "DELETE FROM price_history WHERE listing_id IS NULL;"
            await conn.execute(text(clean_orphaned))

            # Final validation check
            final_existing_cols = await conn.run_sync(get_cols)
            still_missing = [c for c in expected_cols if c not in final_existing_cols]

            if still_missing:
                err_msg = f"DATABASE SCHEMA FAILURE: Missing Product columns: {still_missing}"
                logger.error(err_msg)
                raise RuntimeError(err_msg)

            logger.info("Products table schema verification SUCCESS: All columns present.")

        logger.info("Schema validation completed successfully.")
    except Exception as exc:
        logger.error("Startup database schema verification failure: %s", exc, exc_info=True)
        raise exc


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
