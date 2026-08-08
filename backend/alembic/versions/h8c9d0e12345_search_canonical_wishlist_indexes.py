"""search canonical wishlist indexes

Revision ID: h8c9d0e12345
Revises: g7b8c9d01234
Create Date: 2026-08-08 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h8c9d0e12345'
down_revision: Union[str, None] = 'g7b8c9d01234'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add search & canonical fields to products
    op.add_column('products', sa.Column('normalized_name', sa.String(length=500), nullable=True))
    op.add_column('products', sa.Column('model_name', sa.String(length=255), nullable=True))
    
    op.create_index(op.f('ix_products_normalized_name'), 'products', ['normalized_name'], unique=False)
    op.create_index(op.f('ix_products_model_name'), 'products', ['model_name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_products_model_name'), table_name='products')
    op.drop_index(op.f('ix_products_normalized_name'), table_name='products')
    op.drop_column('products', 'model_name')
    op.drop_column('products', 'normalized_name')
