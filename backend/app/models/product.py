"""
COMPAREX Backend – Product ORM Model (Placeholder for Phase 2)
"""

import uuid
from decimal import Decimal

from sqlalchemy import Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    """Product model — represents a product in our index."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ean: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r}>"
