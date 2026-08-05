"""
COMPAREX Database Migration Script

Applies OAuth column migrations safely to the PostgreSQL database (Neon / Render).
- Adds google_id column & unique index
- Adds login_provider column (default 'email')
- Adds avatar_url column
- Makes hashed_password nullable
"""

import sys
import os
from sqlalchemy import create_engine, text

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def migrate_users_table():
    """Migrate PostgreSQL users table using psycopg2 engine to include Google OAuth columns."""
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    logger.info("Connecting to PostgreSQL database for migration...")
    engine = create_engine(db_url, echo=False)

    sql_statements = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255);",
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_id ON users (google_id);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS login_provider VARCHAR(50) DEFAULT 'email' NOT NULL;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;",
        "ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;",
    ]

    with engine.begin() as conn:
        for stmt in sql_statements:
            logger.info("Executing: %s", stmt)
            conn.execute(text(stmt))

    engine.dispose()
    logger.info("Database migration completed successfully! All User OAuth columns are present.")


if __name__ == "__main__":
    migrate_users_table()
