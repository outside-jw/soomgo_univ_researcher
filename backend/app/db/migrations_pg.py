"""
PostgreSQL-compatible database migrations
Adds turn tracking columns to session_metrics table for CPS stage management
"""
import logging
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from typing import Set

logger = logging.getLogger(__name__)


def get_existing_columns(session: Session, table_name: str) -> Set[str]:
    """
    Get set of existing column names for a table using PostgreSQL-compatible method

    Args:
        session: SQLAlchemy session
        table_name: Name of the table to inspect

    Returns:
        Set of column names that exist in the table
    """
    try:
        inspector = inspect(session.bind)
        columns = inspector.get_columns(table_name)
        return {col['name'] for col in columns}
    except Exception as e:
        logger.warning(f"Could not inspect table {table_name}: {e}")
        return set()


def migrate_add_turn_tracking_columns_pg(session: Session):
    """
    Add turn tracking columns to session_metrics table (PostgreSQL version)

    Adds the following columns if they don't exist:
    - challenge_understanding_turns (도전_이해 max: 6)
    - idea_generation_turns (아이디어_생성 max: 8)
    - action_preparation_turns (실행_준비 max: 6)
    - current_stage (current CPS stage)
    - last_updated (timestamp of last update)

    Uses SQLAlchemy inspector for PostgreSQL compatibility
    """
    try:
        # Get existing columns
        existing_columns = get_existing_columns(session, 'session_metrics')

        if not existing_columns:
            logger.info("session_metrics table does not exist yet, will be created by init_db()")
            return

        logger.info(f"Found existing columns in session_metrics: {existing_columns}")

        # Define columns to add
        columns_to_add = {
            'challenge_understanding_turns': 'INTEGER DEFAULT 0 NOT NULL',
            'idea_generation_turns': 'INTEGER DEFAULT 0 NOT NULL',
            'action_preparation_turns': 'INTEGER DEFAULT 0 NOT NULL',
            'current_stage': 'VARCHAR(50)',
            'last_updated': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL'
        }

        # Add missing columns
        columns_added = []
        for column_name, column_def in columns_to_add.items():
            if column_name not in existing_columns:
                try:
                    logger.info(f"Adding column: {column_name}")
                    sql = text(f"""
                        ALTER TABLE session_metrics
                        ADD COLUMN {column_name} {column_def}
                    """)
                    session.execute(sql)
                    session.commit()
                    columns_added.append(column_name)
                    logger.info(f"✓ Added column: {column_name}")
                except Exception as e:
                    session.rollback()
                    logger.error(f"Failed to add column {column_name}: {e}")
                    raise
            else:
                logger.info(f"Column {column_name} already exists, skipping")

        if columns_added:
            logger.info(f"Migration completed successfully. Added {len(columns_added)} columns: {columns_added}")
        else:
            logger.info("Migration completed. All columns already exist.")

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        raise


def run_migrations_pg(session: Session):
    """
    Run all PostgreSQL migrations

    Args:
        session: SQLAlchemy session
    """
    logger.info("Starting PostgreSQL database migrations...")

    try:
        migrate_add_turn_tracking_columns_pg(session)
        logger.info("All migrations completed successfully")
    except Exception as e:
        logger.error(f"Migration suite failed: {e}", exc_info=True)
        raise
