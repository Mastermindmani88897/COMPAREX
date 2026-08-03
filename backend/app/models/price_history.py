"""
COMPAREX Backend – PriceHistory ORM Model

Tracks historical price changes for a specific product listing over time.
Enables price trend analysis, price drops detection, and charts.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product_listing import ProductListing


class PriceHistory(Base):
    """Historical price record for a product listing on a marketplace."""

    __tablename__ = "price_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product_listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)

    listing: Mapped["ProductListing"] = relationship(
        "ProductListing", back_populates="price_history"
    )

    def __repr__(self) -> str:
        return f"<PriceHistory listing={self.listing_id} price={self.price}>"
