"""
COMPAREX Backend – AIFeedback Model

Stores user helpful/not helpful rating feedback on AI recommendations.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AIFeedback(Base):
    """User rating feedback model for AI recommendation accuracy tuning."""

    __tablename__ = "ai_feedbacks"

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

    recommendation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    is_helpful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", backref="ai_feedbacks")

    def __repr__(self) -> str:
        return f"<AIFeedback user={self.user_id} helpful={self.is_helpful}>"
