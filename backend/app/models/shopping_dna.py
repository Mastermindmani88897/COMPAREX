"""
COMPAREX Backend – ShoppingDNA Model

Stores user Shopping Persona traits (e.g. Budget Shopper, Tech Enthusiast, Deal Hunter).
"""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class ShoppingDNA(Base):
    """User Shopping DNA persona and behavioral traits model."""

    __tablename__ = "shopping_dnas"

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
        unique=True,
        index=True,
    )

    persona_name: Mapped[str] = mapped_column(String(50), default="Mixed Shopper")
    traits: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String).with_variant(JSON, "sqlite"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", backref="shopping_dna")

    def __repr__(self) -> str:
        return f"<ShoppingDNA user={self.user_id} persona={self.persona_name}>"
