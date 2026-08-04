"""
COMPAREX Backend – KnowledgeGraph Model

Stores graph relationship edges between products, brands, categories, accessories, and bundles.
"""

import uuid

from sqlalchemy import Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KnowledgeGraph(Base):
    """Shopping Knowledge Graph relationship edge model."""

    __tablename__ = "knowledge_graph_edges"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    def __repr__(self) -> str:
        return f"<KnowledgeGraph {self.source_id} -[{self.relation_type}]-> {self.target_id}>"
