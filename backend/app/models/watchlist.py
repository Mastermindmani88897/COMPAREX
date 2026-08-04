"""
COMPAREX Backend – Watchlist Model

Tracks user bookmarked products for price monitoring and quick access.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class Watchlist(Base):
    """User bookmarked/saved products model."""

    __tablename__ = "watchlists"

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

    user: Mapped["User"] = relationship("User", backref="watchlist_items")
    product: Mapped["Product"] = relationship("Product", backref="in_watchlists")

    def __repr__(self) -> str:
        return f"<Watchlist user={self.user_id} product={self.product_id}>"
