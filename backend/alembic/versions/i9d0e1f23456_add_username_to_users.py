"""add username to users

Revision ID: i9d0e1f23456
Revises: h8c9d0e12345
Create Date: 2026-08-08 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'i9d0e1f23456'
down_revision: Union[str, None] = 'h8c9d0e12345'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Safely add username column to users table if it does not exist
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(50);")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username);")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username_lower ON users (LOWER(username));")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_users_username_lower;")
    op.execute("DROP INDEX IF EXISTS ix_users_username;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS username;")
