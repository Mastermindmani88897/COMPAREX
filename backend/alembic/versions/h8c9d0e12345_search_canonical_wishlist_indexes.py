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
    # Safely add missing columns to products table if they do not exist
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS normalized_name VARCHAR(500);")
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS model_name VARCHAR(255);")

    # Safely create indexes if they do not exist
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_normalized_name ON products (normalized_name);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_model_name ON products (model_name);")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_user_product_wishlist ON wishlist_items (user_id, product_id);")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_products_model_name;")
    op.execute("DROP INDEX IF EXISTS ix_products_normalized_name;")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS model_name;")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS normalized_name;")
