"""add_product_id_and_marketplace_slug_to_price_history

Adds product_id and marketplace_slug columns to price_history table,
which are present in the PriceHistory SQLAlchemy model (via ORM) but were
missing from the database schema since the original migration only included
listing_id, price, currency, created_at, updated_at.

Also makes listing_id nullable to support direct product-level observations
that are not tied to a specific ProductListing record.

Root cause fix (DuplicateColumnError):
    Migration f6a789012345 already added product_id and marketplace_slug via
    raw SQL with ADD COLUMN IF NOT EXISTS. This migration originally used
    op.add_column() (no idempotency guard), causing DuplicateColumnError on
    a fresh CI database when both migrations run in sequence.
    Fix: use raw SQL with ADD COLUMN IF NOT EXISTS / CREATE INDEX IF NOT EXISTS
    throughout so this migration is idempotent regardless of prior state.

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
    # 1. Add product_id column (nullable FK to products) — idempotent
    op.execute(
        "ALTER TABLE price_history "
        "ADD COLUMN IF NOT EXISTS product_id UUID "
        "REFERENCES products(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_price_history_product_id "
        "ON price_history (product_id);"
    )

    # 2. Add marketplace_slug column — idempotent
    op.execute(
        "ALTER TABLE price_history "
        "ADD COLUMN IF NOT EXISTS marketplace_slug VARCHAR(100);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_price_history_marketplace_slug "
        "ON price_history (marketplace_slug);"
    )

    # 3. Make listing_id nullable so price history can exist without a
    #    specific ProductListing record (e.g. product-level observations).
    #    Uses ALTER COLUMN … DROP NOT NULL — idempotent in PostgreSQL.
    op.execute(
        "ALTER TABLE price_history ALTER COLUMN listing_id DROP NOT NULL;"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE price_history ALTER COLUMN listing_id SET NOT NULL;"
    )
    op.execute(
        "DROP INDEX IF EXISTS ix_price_history_marketplace_slug;"
    )
    op.execute(
        "ALTER TABLE price_history DROP COLUMN IF EXISTS marketplace_slug;"
    )
    op.execute(
        "DROP INDEX IF EXISTS ix_price_history_product_id;"
    )
    op.execute(
        "ALTER TABLE price_history DROP COLUMN IF EXISTS product_id;"
    )
