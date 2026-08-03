"""
COMPAREX Backend – ProductListing ORM Model

Represents a product's price entry on a specific marketplace.
One product can have multiple listings (one per marketplace).
This is the core data model for the price comparison engine.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.marketplace import Marketplace
    from app.models.price_history import PriceHistory
    from app.models.product import Product


class ProductListing(Base):
    """
    A product listing on a specific marketplace.

    Tracks the current price, URL, availability, and seller info
    for a given Product on a given Marketplace.
    """

    __tablename__ = "product_listings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign keys
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    marketplace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("marketplaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Price data
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    original_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)

    # Listing metadata
    listing_url: Mapped[str] = mapped_column(Text, nullable=False)
    seller_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_prime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 1), nullable=True)
    review_count: Mapped[int | None] = mapped_column(nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="listings")
    marketplace: Mapped["Marketplace"] = relationship("Marketplace", back_populates="listings")
    price_history: Mapped[list["PriceHistory"]] = relationship(
        "PriceHistory",
        back_populates="listing",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ProductListing product={self.product_id} "
            f"marketplace={self.marketplace_id} price={self.price}>"
        )
