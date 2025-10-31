"""
CRUD operations for Session model
"""
from sqlalchemy.orm import Session as SQLAlchemySession
from typing import List, Optional
from datetime import datetime
import uuid

from ..models.database import Session, Conversation, StageTransition, SessionMetric
from ..models.schemas import SessionCreate


def create_session(db: SQLAlchemySession, session_data: SessionCreate) -> Session:
    """
    Create a new session

    Args:
        db: Database session
        session_data: Session creation data

    Returns:
        Created Session object
    """
    session_id = str(uuid.uuid4())

    db_session = Session(
        id=session_id,
        user_id=session_data.user_id,
        assignment_text=session_data.assignment_text,
        is_active=True
    )

    db.add(db_session)

    # Initialize metrics for this session
    metrics = SessionMetric(session_id=session_id)
    db.add(metrics)

    db.commit()
    db.refresh(db_session)

    return db_session


def get_session(db: SQLAlchemySession, session_id: str) -> Optional[Session]:
    """
    Get session by ID

    Args:
        db: Database session
        session_id: Session ID

    Returns:
        Session object or None if not found
    """
    return db.query(Session).filter(Session.id == session_id).first()


def get_user_sessions(
    db: SQLAlchemySession,
    user_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[Session]:
    """
    Get all sessions for a user

    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Session objects
    """
    return (
        db.query(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_session(
    db: SQLAlchemySession,
    session_id: str,
    is_active: Optional[bool] = None,
    completed_at: Optional[datetime] = None
) -> Optional[Session]:
    """
    Update session status

    Args:
        db: Database session
        session_id: Session ID
        is_active: Whether session is active
        completed_at: Completion timestamp

    Returns:
        Updated Session object or None if not found
    """
    db_session = get_session(db, session_id)
    if not db_session:
        return None

    if is_active is not None:
        db_session.is_active = is_active
        # Auto-set completed_at when session becomes inactive
        if is_active is False and db_session.completed_at is None:
            db_session.completed_at = datetime.utcnow()

    if completed_at is not None:
        db_session.completed_at = completed_at

    db_session.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_session)

    return db_session


def delete_session(db: SQLAlchemySession, session_id: str) -> bool:
    """
    Delete session and all related data

    Args:
        db: Database session
        session_id: Session ID

    Returns:
        True if deleted, False if not found
    """
    db_session = get_session(db, session_id)
    if not db_session:
        return False

    db.delete(db_session)
    db.commit()

    return True
