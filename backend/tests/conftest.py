"""
COMPAREX Backend – Pytest Fixtures & Configuration

Provides an in-memory SQLite database session override for isolated,
ultra-fast unit and integration testing without requiring external Postgres.

When running against a real PostgreSQL CI database (GitHub Actions), the
seed_test_products fixture also inserts minimal deterministic test records
via AsyncSessionLocal so that services that bypass the get_db() dependency
override (e.g., ai_shopping_service DB fallback) still return results.
"""

import os
import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.deps import get_db
from app.db.base import Base
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Detect whether we are running against a real PostgreSQL database (e.g. CI)
_DB_URL = os.environ.get("DATABASE_URL", "")
_IS_POSTGRES_CI = _DB_URL.startswith("postgresql")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Configure in-memory SQLite engine and override get_db dependency."""
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

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
    await test_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def seed_test_products():
    """
    Insert minimal deterministic test products into the real PostgreSQL
    CI database so that services using AsyncSessionLocal directly
    (e.g. ai_shopping_service DB fallback) can return results.

    This fixture is a no-op when running against the in-memory SQLite
    override (i.e. local dev without DATABASE_URL pointing to Postgres).
    It NEVER touches the production Neon/Render database.
    """
    if not _IS_POSTGRES_CI:
        yield
        return

    # Import here to avoid circular imports during collection
    from app.db.session import AsyncSessionLocal
    from app.models.product import Product

    # Minimal deterministic CI-only test products
    _CI_TEST_PRODUCTS = [
        {
            "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
            "name": "[CI-TEST] Apple iPhone 15 128GB",
            "brand": "Apple",
            "category": "electronics",
            "base_price": Decimal("69999"),
            "rating": 4.7,
            "is_verified": True,
            "is_quarantined": False,
        },
        {
            "id": uuid.UUID("00000000-0000-0000-0000-000000000002"),
            "name": "[CI-TEST] Apple MacBook Air M4 13-inch",
            "brand": "Apple",
            "category": "Laptops",
            "base_price": Decimal("114900"),
            "rating": 4.8,
            "is_verified": True,
            "is_quarantined": False,
        },
        {
            "id": uuid.UUID("00000000-0000-0000-0000-000000000003"),
            "name": "[CI-TEST] ASUS ROG Strix G16 Gaming Laptop",
            "brand": "ASUS",
            "category": "Gaming Laptops",
            "base_price": Decimal("79999"),
            "rating": 4.5,
            "is_verified": True,
            "is_quarantined": False,
        },
    ]

    try:
        async with AsyncSessionLocal() as session:
            for prod_data in _CI_TEST_PRODUCTS:
                prod = await session.get(Product, prod_data["id"])
                if prod is None:
                    prod = Product(**prod_data)
                    session.add(prod)
            await session.commit()
    except Exception as exc:
        print(f"seed_test_products setup warning: {exc}")

    yield


@pytest.fixture
async def async_client():
    """Httpx AsyncClient fixture for testing endpoints."""
    from httpx import ASGITransport, AsyncClient
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def db_session():
    """Yield an async database session bound to the test SQLite in-memory engine."""
    from app.api.deps import get_db
    override = app.dependency_overrides.get(get_db)
    if override:
        async for session in override():
            yield session
    else:
        test_engine = create_async_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        async_session = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
