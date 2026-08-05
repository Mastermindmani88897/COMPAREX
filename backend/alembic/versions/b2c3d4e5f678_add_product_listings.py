"""Add product_listings table

Revision ID: b2c3d4e5f678
Revises: 1abbce3398dc
Create Date: 2026-08-03 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f678'
down_revision: Union[str, None] = '1abbce3398dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'product_listings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('marketplace_id', sa.UUID(), nullable=False),
        sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('original_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('listing_url', sa.Text(), nullable=False),
        sa.Column('seller_name', sa.String(length=255), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_prime', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('rating', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['marketplace_id'], ['marketplaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_product_listings_id'), 'product_listings', ['id'], unique=False)
    op.create_index(op.f('ix_product_listings_product_id'), 'product_listings', ['product_id'], unique=False)
    op.create_index(op.f('ix_product_listings_marketplace_id'), 'product_listings', ['marketplace_id'], unique=False)
    # Unique constraint: one listing per product+marketplace combination
    op.create_index(
        'uq_product_marketplace_listing',
        'product_listings',
        ['product_id', 'marketplace_id'],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('uq_product_marketplace_listing', table_name='product_listings')
    op.drop_index(op.f('ix_product_listings_marketplace_id'), table_name='product_listings')
    op.drop_index(op.f('ix_product_listings_product_id'), table_name='product_listings')
    op.drop_index(op.f('ix_product_listings_id'), table_name='product_listings')
    op.drop_table('product_listings')
