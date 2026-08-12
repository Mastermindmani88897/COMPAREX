"""add_product_id_and_marketplace_slug_to_price_history

Adds product_id and marketplace_slug columns to price_history table,
which are present in the PriceHistory SQLAlchemy model (via ORM) but were
missing from the database schema since the original migration only included
listing_id, price, currency, created_at, updated_at.

Also makes listing_id nullable to support direct product-level observations
that are not tied to a specific ProductListing record.

Revision ID: n3o4p5q6r7s8
Revises: m2n3o4p5q6r7
Create Date: 2026-08-12 04:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "n3o4p5q6r7s8"
down_revision: Union[str, None] = "m2n3o4p5q6r7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add product_id column (nullable FK to products)
    op.add_column(
        "price_history",
        sa.Column("product_id", sa.UUID(), nullable=True),
    )
    op.create_index(
        "ix_price_history_product_id",
        "price_history",
        ["product_id"],
        unique=False,
    )
    # FK is deferred to avoid issues with existing rows
    op.create_foreign_key(
        "fk_price_history_product_id",
        "price_history",
        "products",
        ["product_id"],
        ["id"],
        ondelete="CASCADE",
        deferrable=True,
        initially="DEFERRED",
    )

    # 2. Add marketplace_slug column (nullable, indexed for analytics)
    op.add_column(
        "price_history",
        sa.Column("marketplace_slug", sa.String(length=100), nullable=True),
    )
    op.create_index(
        "ix_price_history_marketplace_slug",
        "price_history",
        ["marketplace_slug"],
        unique=False,
    )

    # 3. Make listing_id nullable so price history can exist without a
    #    specific ProductListing record (e.g. product-level observations)
    op.alter_column(
        "price_history",
        "listing_id",
        existing_type=sa.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "price_history",
        "listing_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
    op.drop_index("ix_price_history_marketplace_slug", table_name="price_history")
    op.drop_column("price_history", "marketplace_slug")

    op.drop_constraint(
        "fk_price_history_product_id", "price_history", type_="foreignkey"
    )
    op.drop_index("ix_price_history_product_id", table_name="price_history")
    op.drop_column("price_history", "product_id")
