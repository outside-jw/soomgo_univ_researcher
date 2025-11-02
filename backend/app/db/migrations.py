"""
Database migration utilities
Simple migration system for adding turn tracking columns
"""
import sqlite3
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def get_db_path() -> Path:
    """Get the database path"""
    backend_dir = Path(__file__).parent.parent.parent
    return backend_dir / "univ_consult.db"


def column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns


def migrate_add_turn_tracking_columns(db_path: Optional[Path] = None):
    """
    Add turn tracking columns to session_metrics table

    Adds:
    - challenge_understanding_turns (도전_이해 max: 6)
    - idea_generation_turns (아이디어_생성 max: 8)
    - action_preparation_turns (실행_준비 max: 6)
    - current_stage
    - last_updated
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        logger.warning(f"Database not found at {db_path}, will be created on first run")
        return

    logger.info(f"Running migration on {db_path}")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check and add challenge_understanding_turns
        if not column_exists(cursor, 'session_metrics', 'challenge_understanding_turns'):
            logger.info("Adding column: challenge_understanding_turns")
            cursor.execute("""
                ALTER TABLE session_metrics
                ADD COLUMN challenge_understanding_turns INTEGER DEFAULT 0 NOT NULL
            """)

        # Check and add idea_generation_turns
        if not column_exists(cursor, 'session_metrics', 'idea_generation_turns'):
            logger.info("Adding column: idea_generation_turns")
            cursor.execute("""
                ALTER TABLE session_metrics
                ADD COLUMN idea_generation_turns INTEGER DEFAULT 0 NOT NULL
            """)

        # Check and add action_preparation_turns
        if not column_exists(cursor, 'session_metrics', 'action_preparation_turns'):
            logger.info("Adding column: action_preparation_turns")
            cursor.execute("""
                ALTER TABLE session_metrics
                ADD COLUMN action_preparation_turns INTEGER DEFAULT 0 NOT NULL
            """)

        # Check and add current_stage
        if not column_exists(cursor, 'session_metrics', 'current_stage'):
            logger.info("Adding column: current_stage")
            cursor.execute("""
                ALTER TABLE session_metrics
                ADD COLUMN current_stage VARCHAR(50)
            """)

        # Check and add last_updated
        if not column_exists(cursor, 'session_metrics', 'last_updated'):
            logger.info("Adding column: last_updated")
            # SQLite doesn't support CURRENT_TIMESTAMP in ALTER TABLE, so we use a default value
            from datetime import datetime
            default_time = datetime.utcnow().isoformat()
            cursor.execute(f"""
                ALTER TABLE session_metrics
                ADD COLUMN last_updated DATETIME DEFAULT '{default_time}' NOT NULL
            """)

        conn.commit()
        logger.info("Migration completed successfully")

    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}", exc_info=True)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Run migration when executed directly
    logging.basicConfig(level=logging.INFO)
    migrate_add_turn_tracking_columns()
    print("✅ Migration completed")
