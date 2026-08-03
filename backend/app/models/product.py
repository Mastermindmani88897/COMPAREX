"""
COMPAREX Backend – Product ORM Model
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text
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
