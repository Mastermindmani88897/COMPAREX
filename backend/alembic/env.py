"""
COMPAREX Backend – Alembic Environment

This file configures Alembic's env.py to use our SQLAlchemy models
and read the database URL from our settings module.
"""

import asyncio
import re
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import settings and Base (must be importable from this directory)
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.base import Base

# Import all models so Alembic can see them
from app.models import user, product, marketplace, category  # noqa: F401

config = context.config


def _make_sync_url(url: str) -> str:
    """
    Convert an async database URL to a synchronous psycopg2 URL for
    Alembic CLI migrations.  The asyncpg driver cannot be used in
    Alembic's synchronous migration context.

    Examples:
        postgresql+asyncpg://... → postgresql+psycopg2://...
        postgres://...           → postgresql+psycopg2://...
    """
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    url = url.replace("postgres://", "postgresql+psycopg2://")
    # Strip asyncpg-only SSL params that psycopg2 does not understand
    url = re.sub(r"\?ssl=require$", "?sslmode=require", url)
    url = re.sub(r"\?ssl=prefer$", "?sslmode=prefer", url)
    url = re.sub(r"&?channel_binding=[^&]+", "", url)
    return url


# Override alembic.ini sqlalchemy.url with our settings
# Use the sync (psycopg2) URL for Alembic CLI; async engines are used only
# inside the running FastAPI application, not during migrations.
sync_db_url = _make_sync_url(settings.ASYNC_DATABASE_URL)
config.set_main_option("sqlalchemy.url", sync_db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using async engine."""
    # Restore the asyncpg URL for the async engine (overrides sync_db_url
    # that was set for the Alembic config main option above)
    async_section = dict(config.get_section(config.config_ini_section, {}))
    async_section["sqlalchemy.url"] = settings.ASYNC_DATABASE_URL
    connectable = async_engine_from_config(
        async_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
