"""sync product catalog columns and indexes

Revision ID: g7b8c9d01234
Revises: f6a789012345
Create Date: 2026-08-07 21:42:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "g7b8c9d01234"
down_revision: Union[str, None] = "f6a789012345"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Safely add missing columns to products table
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS rating FLOAT DEFAULT 4.5;")
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0;")
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS popularity_score FLOAT DEFAULT 0.0;")
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS search_keywords TEXT;")
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS stock_status VARCHAR(50) DEFAULT 'in_stock';")
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS discount_percentage FLOAT DEFAULT 0.0;")
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS base_price NUMERIC(12, 2);")
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS category VARCHAR(255);")
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS brand VARCHAR(255);")
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS ean VARCHAR(50);")

    # 2. Safely create indexes for query performance
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_category_brand ON products (category, brand);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_base_price ON products (base_price);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_popularity ON products (popularity_score);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_rating ON products (rating);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_category ON products (category);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_brand ON products (brand);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_ean ON products (ean);")


def downgrade() -> None:
    # Safe no-op on downgrade to prevent data loss
    pass
