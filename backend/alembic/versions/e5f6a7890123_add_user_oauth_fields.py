"""Add User OAuth Fields (google_id, login_provider, avatar_url, nullable hashed_password)

Revision ID: e5f6a7890123
Revises: d4e5f6a78901
Create Date: 2026-08-05 14:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7890123'
down_revision: Union[str, None] = 'd4e5f6a78901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add google_id column and unique index
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255);")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_id ON users (google_id);")

    # 2. Add login_provider column with default 'email'
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS login_provider VARCHAR(50) DEFAULT 'email' NOT NULL;")

    # 3. Add avatar_url column
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;")

    # 4. Make hashed_password nullable for OAuth users
    op.execute("ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_users_google_id;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS google_id;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS login_provider;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS avatar_url;")
    op.execute("ALTER TABLE users ALTER COLUMN hashed_password SET NOT NULL;")
