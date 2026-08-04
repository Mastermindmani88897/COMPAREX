"""
COMPAREX Backend – AIConversation Model

Stores multi-turn conversational AI interaction messages and session context.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AIConversation(Base):
    """Conversational AI chat turn message history model."""

    __tablename__ = "ai_conversations"

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

    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    sender: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", backref="ai_conversations")

    def __repr__(self) -> str:
        return f"<AIConversation session={self.session_id} sender={self.sender}>"
