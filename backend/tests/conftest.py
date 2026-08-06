"""
COMPAREX Backend – Pytest Fixtures & Configuration

Provides in-memory SQLite database session override for isolated,
ultra-fast unit and integration testing without requiring external Postgres.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.deps import get_db
from app.db.base import Base
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Configure in-memory SQLite engine and override get_db dependency."""
    # settings.ENVIRONMENT must match the pattern (development|staging|production)
    # so we leave it as-is during testing; only override get_db dependency.

    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def _override_get_db():
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client():
    """Httpx AsyncClient fixture for testing endpoints."""
    from httpx import ASGITransport, AsyncClient
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
