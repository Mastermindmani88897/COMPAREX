"""
COMPAREX Backend – Database Base & Models Registry

Defines the SQLAlchemy declarative base that all models inherit from.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    # Shared audit columns — every table gets these
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict:
        """Serialize model to a plain dict (utility method)."""
        return {
            col.name: getattr(self, col.name)
            for col in self.__table__.columns
        }


# Import all models here so Alembic can discover them for migrations
# (import order matters — referenced tables must be imported before dependents)
