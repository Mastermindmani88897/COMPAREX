"""add quarantine columns and search indexes to products

Revision ID: k1l2m3n4o5p6
Revises: j0e1f2g34567
Create Date: 2026-08-09 11:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'k1l2m3n4o5p6'
down_revision: Union[str, None] = 'j0e1f2g34567'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS is_quarantined BOOLEAN NOT NULL DEFAULT FALSE;")
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT TRUE;")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_is_quarantined ON products (is_quarantined);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_is_verified ON products (is_verified);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_search_active ON products (is_quarantined, category, brand);")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_products_search_active;")
    op.execute("DROP INDEX IF EXISTS ix_products_is_verified;")
    op.execute("DROP INDEX IF EXISTS ix_products_is_quarantined;")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS is_verified;")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS is_quarantined;")
