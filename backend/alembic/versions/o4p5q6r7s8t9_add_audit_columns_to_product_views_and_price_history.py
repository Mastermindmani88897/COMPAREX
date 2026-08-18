"""add audit columns to product_views and price_history

Revision ID: o4p5q6r7s8t9
Revises: n3o4p5q6r7s8
Create Date: 2026-08-18 08:30:00.000000

Root Cause Fix:
    The SQLAlchemy Base class (app/db/base.py) defines created_at and updated_at
    as shared audit columns on ALL models. However the original migrations for
    product_views and price_history were created before this Base audit pattern
    was established, so those tables are missing the columns in the live database.

    This causes:
        asyncpg.exceptions.UndefinedColumnError:
        column product_views.created_at does not exist

    Fix:
        ADD COLUMN IF NOT EXISTS for both tables — safe for production.
        Backfill existing rows with NOW() so NOT NULL constraint is satisfied.
        Does NOT delete or alter any existing rows.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'o4p5q6r7s8t9'
down_revision: Union[str, None] = 'n3o4p5q6r7s8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── product_views: add missing audit columns ─────────────────────────────
    # Step 1: add as nullable first so existing rows don't violate NOT NULL
    op.execute(
        "ALTER TABLE product_views "
        "ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ;"
    )
    op.execute(
        "ALTER TABLE product_views "
        "ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;"
    )
    # Step 2: backfill existing rows
    op.execute(
        "UPDATE product_views SET created_at = NOW() WHERE created_at IS NULL;"
    )
    op.execute(
        "UPDATE product_views SET updated_at = NOW() WHERE updated_at IS NULL;"
    )
    # Step 3: set NOT NULL constraint and default
    op.execute(
        "ALTER TABLE product_views "
        "ALTER COLUMN created_at SET NOT NULL, "
        "ALTER COLUMN created_at SET DEFAULT NOW();"
    )
    op.execute(
        "ALTER TABLE product_views "
        "ALTER COLUMN updated_at SET NOT NULL, "
        "ALTER COLUMN updated_at SET DEFAULT NOW();"
    )

    # ── price_history: add missing audit columns ──────────────────────────────
    op.execute(
        "ALTER TABLE price_history "
        "ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ;"
    )
    op.execute(
        "ALTER TABLE price_history "
        "ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;"
    )
    op.execute(
        "UPDATE price_history SET created_at = NOW() WHERE created_at IS NULL;"
    )
    op.execute(
        "UPDATE price_history SET updated_at = NOW() WHERE updated_at IS NULL;"
    )
    op.execute(
        "ALTER TABLE price_history "
        "ALTER COLUMN created_at SET NOT NULL, "
        "ALTER COLUMN created_at SET DEFAULT NOW();"
    )
    op.execute(
        "ALTER TABLE price_history "
        "ALTER COLUMN updated_at SET NOT NULL, "
        "ALTER COLUMN updated_at SET DEFAULT NOW();"
    )


def downgrade() -> None:
    # Remove the audit columns we added (safe — no data loss to other columns)
    op.execute(
        "ALTER TABLE product_views "
        "DROP COLUMN IF EXISTS created_at, "
        "DROP COLUMN IF EXISTS updated_at;"
    )
    op.execute(
        "ALTER TABLE price_history "
        "DROP COLUMN IF EXISTS created_at, "
        "DROP COLUMN IF EXISTS updated_at;"
    )
