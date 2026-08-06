"""
COMPAREX Backend - Wishlist Model

Tracks user favorite/wishlist products with target price monitoring,
preferred marketplace, and notes.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class Wishlist(Base):
    """User wishlist / favorites model."""

    __tablename__ = "wishlist_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    preferred_marketplace: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, default="Amazon"
    )

    target_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", backref="wishlist_items_list")
    product: Mapped["Product"] = relationship("Product", backref="in_wishlists")

    def __repr__(self) -> str:
        return f"<Wishlist id={self.id} user={self.user_id} product={self.product_id}>"
