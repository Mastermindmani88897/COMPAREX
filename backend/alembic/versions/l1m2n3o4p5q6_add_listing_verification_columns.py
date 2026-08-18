"""add_listing_verification_columns

Revision ID: l1m2n3o4p5q6
Revises: k1l2m3n4o5p6
Create Date: 2026-08-09 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'l1m2n3o4p5q6'
down_revision: Union[str, None] = 'k1l2m3n4o5p6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE product_listings "
        "ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50) NOT NULL DEFAULT 'verified';"
    )
    op.execute(
        "ALTER TABLE product_listings "
        "ADD COLUMN IF NOT EXISTS match_score NUMERIC(5, 4) NOT NULL DEFAULT 1.0000;"
    )
    op.execute(
        "ALTER TABLE product_listings "
        "ADD COLUMN IF NOT EXISTS is_exact_url BOOLEAN NOT NULL DEFAULT TRUE;"
    )
    op.execute(
        "ALTER TABLE product_listings "
        "ADD COLUMN IF NOT EXISTS retrieved_at TIMESTAMPTZ;"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_product_listings_verification_status "
        "ON product_listings (verification_status);"
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_product_listings_verification_status'), table_name='product_listings')
    op.drop_column('product_listings', 'retrieved_at')
    op.drop_column('product_listings', 'is_exact_url')
    op.drop_column('product_listings', 'match_score')
    op.drop_column('product_listings', 'verification_status')
