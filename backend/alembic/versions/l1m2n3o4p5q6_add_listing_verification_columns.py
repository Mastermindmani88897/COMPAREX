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
    op.add_column(
        'product_listings',
        sa.Column('verification_status', sa.String(length=50), nullable=False, server_default='verified')
    )
    op.add_column(
        'product_listings',
        sa.Column('match_score', sa.Numeric(precision=5, scale=4), nullable=False, server_default='1.0000')
    )
    op.add_column(
        'product_listings',
        sa.Column('is_exact_url', sa.Boolean(), nullable=False, server_default='true')
    )
    op.add_column(
        'product_listings',
        sa.Column('retrieved_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index(
        op.f('ix_product_listings_verification_status'),
        'product_listings',
        ['verification_status'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_product_listings_verification_status'), table_name='product_listings')
    op.drop_column('product_listings', 'retrieved_at')
    op.drop_column('product_listings', 'is_exact_url')
    op.drop_column('product_listings', 'match_score')
    op.drop_column('product_listings', 'verification_status')
