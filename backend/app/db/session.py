"""
COMPAREX Backend – Database Session Factory

Provides async SQLAlchemy engine and session factory.
Use get_db() as a FastAPI dependency to inject DB sessions into endpoints.
"""

import os
import sys
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Async engine with connection pooling
engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
}

is_test_env = "pytest" in sys.modules or bool(os.environ.get("PYTEST_CURRENT_TEST"))

if "sqlite" in settings.ASYNC_DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
elif is_test_env:
    # Use NullPool during testing to prevent asyncpg connections from being held
    # across different event loops in pytest-asyncio runs.
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_recycle"] = 300
    engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    **engine_kwargs,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency — yields a database session and ensures cleanup.

    Usage:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
