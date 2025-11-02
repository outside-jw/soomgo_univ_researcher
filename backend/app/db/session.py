"""
Database session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

# Create database engine with optimized connection pooling
# Determine connect_args based on database type
connect_args = {}
if settings.DATABASE_URL.startswith("postgresql"):
    # PostgreSQL-specific connection arguments
    connect_args = {
        "connect_timeout": 10,  # Connection timeout in seconds
    }

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,  # Base connection pool size (suitable for 30 users)
    max_overflow=10,  # Additional connections when pool is full
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=settings.DEBUG,  # Log SQL statements in debug mode
    connect_args=connect_args
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[SQLAlchemySession, None, None]:
    """
    Dependency for FastAPI endpoints to get database session

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session
            pass

    Yields:
        SQLAlchemy Session instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[SQLAlchemySession, None, None]:
    """
    Context manager for database session

    Usage:
        with get_db_context() as db:
            # Use db session
            pass

    Yields:
        SQLAlchemy Session instance
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database tables and run migrations

    This should be called during application startup to create all tables
    and apply any necessary schema migrations
    """
    from ..models.database import Base
    from .migrations_pg import run_migrations_pg

    try:
        # Create all tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Run PostgreSQL migrations to add any missing columns
        logger.info("Running PostgreSQL migrations...")
        db = SessionLocal()
        try:
            run_migrations_pg(db)
            logger.info("Migrations completed successfully")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise
