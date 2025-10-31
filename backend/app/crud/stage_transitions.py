"""
CRUD operations for StageTransition model
"""
from sqlalchemy.orm import Session as SQLAlchemySession
from typing import List, Optional

from ..models.database import StageTransition, SessionMetric


def create_stage_transition(
    db: SQLAlchemySession,
    session_id: str,
    from_stage: Optional[str],
    to_stage: str,
    transition_reason: Optional[str] = None,
    message_count: int = 0
) -> StageTransition:
    """
    Create a new stage transition record

    Args:
        db: Database session
        session_id: Session ID
        from_stage: Previous CPS stage (None for first stage)
        to_stage: New CPS stage
        transition_reason: Reason for transition
        message_count: Number of messages in previous stage

    Returns:
        Created StageTransition object
    """
    transition = StageTransition(
        session_id=session_id,
        from_stage=from_stage,
        to_stage=to_stage,
        transition_reason=transition_reason,
        message_count=message_count
    )

    db.add(transition)

    # Update session metrics
    _update_metrics_for_transition(db, session_id, to_stage)

    db.commit()
    db.refresh(transition)

    return transition


def get_session_transitions(
    db: SQLAlchemySession,
    session_id: str
) -> List[StageTransition]:
    """
    Get all stage transitions for a session

    Args:
        db: Database session
        session_id: Session ID

    Returns:
        List of StageTransition objects ordered by creation time
    """
    return (
        db.query(StageTransition)
        .filter(StageTransition.session_id == session_id)
        .order_by(StageTransition.created_at.asc())
        .all()
    )


def get_latest_stage(db: SQLAlchemySession, session_id: str) -> str:
    """
    Get the latest CPS stage for a session

    Args:
        db: Database session
        session_id: Session ID

    Returns:
        Latest CPS stage name or default stage if no transitions
    """
    transition = (
        db.query(StageTransition)
        .filter(StageTransition.session_id == session_id)
        .order_by(StageTransition.created_at.desc())
        .first()
    )

    return transition.to_stage if transition else "도전_이해_기회구성"


def _update_metrics_for_transition(
    db: SQLAlchemySession,
    session_id: str,
    new_stage: str
):
    """
    Update session metrics when a stage transition occurs

    Args:
        db: Database session
        session_id: Session ID
        new_stage: New CPS stage
    """
    metrics = db.query(SessionMetric).filter(
        SessionMetric.session_id == session_id
    ).first()

    if not metrics:
        metrics = SessionMetric(session_id=session_id)
        db.add(metrics)

    # Update stages completed
    if metrics.stages_completed is None:
        metrics.stages_completed = []

    if new_stage not in metrics.stages_completed:
        metrics.stages_completed = metrics.stages_completed + [new_stage]

    # Increment transition count
    metrics.total_stage_transitions += 1
