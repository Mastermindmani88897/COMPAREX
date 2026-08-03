"""
COMPAREX Backend – ProductSpecification ORM Model

Key-value attributes for product specifications (e.g., RAM: 16GB, Storage: 512GB SSD).
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product


class ProductSpecification(Base):
    """Specification key-value attribute linked to a Product."""

    __tablename__ = "product_specifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    group: Mapped[str | None] = mapped_column(String(100), nullable=True, default="General")
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="specifications")

    def __repr__(self) -> str:
        return f"<ProductSpecification product={self.product_id} {self.key}={self.value}>"
