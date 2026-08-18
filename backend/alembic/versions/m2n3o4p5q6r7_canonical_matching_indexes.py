"""canonical_matching_indexes

Revision ID: m2n3o4p5q6r7
Revises: l1m2n3o4p5q6
Create Date: 2026-08-11 10:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'm2n3o4p5q6r7'
down_revision: Union[str, None] = 'l1m2n3o4p5q6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure indexes for canonical product search and matching fields
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_products_normalized_name "
        "ON products (normalized_name);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_products_model_name "
        "ON products (model_name);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_price_history_listing_id "
        "ON price_history (listing_id);"
    )


def downgrade() -> None:
    op.drop_index('ix_price_history_listing_id', table_name='price_history', if_exists=True)
    op.drop_index('ix_products_model_name', table_name='products', if_exists=True)
    op.drop_index('ix_products_normalized_name', table_name='products', if_exists=True)
