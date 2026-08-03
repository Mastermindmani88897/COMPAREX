"""
COMPAREX Backend – Marketplace ORM Model
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product_listing import ProductListing


class Marketplace(Base):
    """Marketplace model — represents a supported shopping marketplace."""

    __tablename__ = "marketplaces"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    country_code: Mapped[str] = mapped_column(String(10), default="IN", nullable=False)

    listings: Mapped[list["ProductListing"]] = relationship(
        "ProductListing",
        back_populates="marketplace",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Marketplace id={self.id} name={self.name!r}>"
