"""
CRUD operations for session metrics including turn counting
"""
from sqlalchemy.orm import Session
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging

from ..models.database import SessionMetric

logger = logging.getLogger(__name__)

# Turn limits per CPS stage (from customer requirements)
TURN_LIMITS = {
    "도전_이해": 6,
    "아이디어_생성": 8,
    "실행_준비": 6,
}


def get_or_create_session_metric(db: Session, session_id: str) -> SessionMetric:
    """
    Get existing session metric or create new one

    Args:
        db: Database session
        session_id: Session ID

    Returns:
        SessionMetric object
    """
    metric = db.query(SessionMetric).filter(SessionMetric.session_id == session_id).first()

    if not metric:
        metric = SessionMetric(session_id=session_id)
        db.add(metric)
        db.commit()
        db.refresh(metric)
        logger.info(f"Created new session metric for session {session_id}")

    return metric


def update_turn_count(
    db: Session,
    session_id: str,
    cps_stage: str
) -> Tuple[int, int, bool]:
    """
    Increment turn count for the given CPS stage

    Args:
        db: Database session
        session_id: Session ID
        cps_stage: Current CPS stage (도전_이해, 아이디어_생성, 실행_준비)

    Returns:
        Tuple of (current_turns, max_turns, limit_reached)
    """
    metric = get_or_create_session_metric(db, session_id)

    # Map stage to column name
    stage_column_map = {
        "도전_이해": "challenge_understanding_turns",
        "아이디어_생성": "idea_generation_turns",
        "실행_준비": "action_preparation_turns",
    }

    column_name = stage_column_map.get(cps_stage)

    if not column_name:
        logger.warning(f"Unknown CPS stage: {cps_stage}, not counting turns")
        return 0, 0, False

    # Increment turn count
    current_value = getattr(metric, column_name)
    new_value = current_value + 1
    setattr(metric, column_name, new_value)

    # Update current stage and timestamp
    metric.current_stage = cps_stage
    metric.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(metric)

    # Check if limit reached
    max_turns = TURN_LIMITS.get(cps_stage, 999)
    limit_reached = new_value >= max_turns

    logger.info(
        f"Session {session_id}, Stage {cps_stage}: Turn {new_value}/{max_turns}, "
        f"Limit reached: {limit_reached}"
    )

    return new_value, max_turns, limit_reached


def get_turn_counts(db: Session, session_id: str) -> Dict[str, Dict[str, int]]:
    """
    Get all turn counts for a session

    Args:
        db: Database session
        session_id: Session ID

    Returns:
        Dictionary with turn counts per stage:
        {
            "도전_이해": {"current": 3, "max": 6},
            "아이디어_생성": {"current": 0, "max": 8},
            "실행_준비": {"current": 0, "max": 6}
        }
    """
    metric = get_or_create_session_metric(db, session_id)

    return {
        "도전_이해": {
            "current": metric.challenge_understanding_turns,
            "max": TURN_LIMITS["도전_이해"]
        },
        "아이디어_생성": {
            "current": metric.idea_generation_turns,
            "max": TURN_LIMITS["아이디어_생성"]
        },
        "실행_준비": {
            "current": metric.action_preparation_turns,
            "max": TURN_LIMITS["실행_준비"]
        }
    }


def reset_stage_turns(db: Session, session_id: str, cps_stage: str) -> None:
    """
    Reset turn count for a specific stage (useful for stage transitions)

    Args:
        db: Database session
        session_id: Session ID
        cps_stage: CPS stage to reset
    """
    metric = get_or_create_session_metric(db, session_id)

    stage_column_map = {
        "도전_이해": "challenge_understanding_turns",
        "아이디어_생성": "idea_generation_turns",
        "실행_준비": "action_preparation_turns",
    }

    column_name = stage_column_map.get(cps_stage)

    if column_name:
        setattr(metric, column_name, 0)
        metric.last_updated = datetime.utcnow()
        db.commit()
        logger.info(f"Reset turn count for session {session_id}, stage {cps_stage}")


def check_turn_limit(db: Session, session_id: str, cps_stage: str) -> Tuple[int, int, bool]:
    """
    Check current turn count without incrementing

    Args:
        db: Database session
        session_id: Session ID
        cps_stage: Current CPS stage

    Returns:
        Tuple of (current_turns, max_turns, limit_reached)
    """
    metric = get_or_create_session_metric(db, session_id)

    stage_column_map = {
        "도전_이해": "challenge_understanding_turns",
        "아이디어_생성": "idea_generation_turns",
        "실행_준비": "action_preparation_turns",
    }

    column_name = stage_column_map.get(cps_stage)

    if not column_name:
        return 0, 0, False

    current_turns = getattr(metric, column_name)
    max_turns = TURN_LIMITS.get(cps_stage, 999)
    limit_reached = current_turns >= max_turns

    return current_turns, max_turns, limit_reached
