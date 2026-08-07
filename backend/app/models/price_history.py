"""
COMPAREX Backend – PriceHistory ORM Model

Tracks historical price changes for a specific product listing or marketplace over time.
Enables price trend analysis, price drops detection, multi-store history graphs, and charts.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.product_listing import ProductListing


class PriceHistory(Base):
    """Historical price record for a product listing or marketplace."""

    __tablename__ = "price_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product_listings.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    marketplace_slug: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)

    listing: Mapped[Optional["ProductListing"]] = relationship(
        "ProductListing", back_populates="price_history"
    )

    product: Mapped[Optional["Product"]] = relationship("Product", backref="price_histories")

    def __repr__(self) -> str:
        return (
            f"<PriceHistory product={self.product_id} "
            f"store={self.marketplace_slug} price={self.price}>"
        )
