"""create product_views table

Revision ID: j0e1f2g34567
Revises: i9d0e1f23456
Create Date: 2026-08-08 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'j0e1f2g34567'
down_revision: Union[str, None] = 'i9d0e1f23456'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS product_views (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            viewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            price_at_view NUMERIC(12, 2),
            CONSTRAINT uq_user_product_view UNIQUE (user_id, product_id)
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_views_user_id ON product_views (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_views_product_id ON product_views (product_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_views_viewed_at ON product_views (viewed_at DESC);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS product_views CASCADE;")
