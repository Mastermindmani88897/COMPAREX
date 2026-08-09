"""
COMPAREX Backend – Product ORM Model
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.brand import Brand
    from app.models.category import Category
    from app.models.product_image import ProductImage
    from app.models.product_listing import ProductListing
    from app.models.product_specification import ProductSpecification


class Product(Base):
    """Product model — represents a canonical product in our index."""

    __tablename__ = "products"

    __table_args__ = (
        Index("ix_products_category_brand", "category", "brand"),
        Index("ix_products_base_price", "base_price"),
        Index("ix_products_popularity", "popularity_score"),
        Index("ix_products_rating", "rating"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("brands.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ean: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True, index=True)
    base_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    rating: Mapped[float | None] = mapped_column(Float, nullable=True, default=4.5)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    popularity_score: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    normalized_name: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    model_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    search_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    stock_status: Mapped[str | None] = mapped_column(String(50), nullable=True, default="in_stock")
    discount_percentage: Mapped[float | None] = mapped_column(Float, nullable=True, default=0.0)
    is_quarantined: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    category_rel: Mapped["Category | None"] = relationship("Category", backref="products")
    brand_rel: Mapped["Brand | None"] = relationship("Brand", back_populates="products")
    listings: Mapped[list["ProductListing"]] = relationship(
        "ProductListing",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    specifications: Mapped[list["ProductSpecification"]] = relationship(
        "ProductSpecification",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r}>"
