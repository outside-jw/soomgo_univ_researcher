"""
CRUD operations for Conversation model
"""
from sqlalchemy.orm import Session as SQLAlchemySession
from typing import List, Optional
from datetime import datetime

from ..models.database import Conversation, SessionMetric


def create_conversation(
    db: SQLAlchemySession,
    session_id: str,
    role: str,
    message: str,
    cps_stage: Optional[str] = None,
    metacog_elements: Optional[List[str]] = None,
    response_depth: Optional[str] = None,
    should_transition: Optional[bool] = None,
    reasoning: Optional[str] = None
) -> Conversation:
    """
    Create a new conversation message

    Args:
        db: Database session
        session_id: Session ID
        role: 'user' or 'agent'
        message: Message content
        cps_stage: Current CPS stage
        metacog_elements: List of metacognitive elements
        response_depth: 'shallow', 'medium', or 'deep'
        should_transition: Whether agent suggested transition
        reasoning: Agent's reasoning

    Returns:
        Created Conversation object
    """
    conversation = Conversation(
        session_id=session_id,
        role=role,
        message=message,
        cps_stage=cps_stage,
        metacog_elements=metacog_elements,
        response_depth=response_depth,
        should_transition=should_transition,
        reasoning=reasoning
    )

    db.add(conversation)

    # Update session metrics
    _update_metrics_for_conversation(
        db,
        session_id,
        role,
        metacog_elements,
        response_depth
    )

    db.commit()
    db.refresh(conversation)

    return conversation


def get_conversation(db: SQLAlchemySession, conversation_id: int) -> Optional[Conversation]:
    """Get conversation by ID"""
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_session_conversations(
    db: SQLAlchemySession,
    session_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[Conversation]:
    """
    Get all conversations for a session

    Args:
        db: Database session
        session_id: Session ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Conversation objects ordered by creation time
    """
    return (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_latest_conversations(
    db: SQLAlchemySession,
    session_id: str,
    limit: int = 5
) -> List[Conversation]:
    """
    Get the latest N conversations for a session

    Args:
        db: Database session
        session_id: Session ID
        limit: Number of recent conversations to return

    Returns:
        List of recent Conversation objects
    """
    return (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
        .all()
    )


def _update_metrics_for_conversation(
    db: SQLAlchemySession,
    session_id: str,
    role: str,
    metacog_elements: Optional[List[str]],
    response_depth: Optional[str]
):
    """
    Update session metrics when a conversation is created

    Args:
        db: Database session
        session_id: Session ID
        role: 'user' or 'agent'
        metacog_elements: List of metacognitive elements
        response_depth: Response depth assessment
    """
    metrics = db.query(SessionMetric).filter(
        SessionMetric.session_id == session_id
    ).first()

    if not metrics:
        # Create metrics if doesn't exist
        metrics = SessionMetric(session_id=session_id)
        db.add(metrics)

    # Update message counts
    metrics.total_messages += 1
    if role == "user":
        metrics.user_messages += 1
    elif role == "agent":
        metrics.agent_messages += 1

    # Update metacognitive element counts
    if metacog_elements:
        for element in metacog_elements:
            if element == "점검" or element == "monitoring":
                metrics.monitoring_count += 1
            elif element == "조절" or element == "control":
                metrics.control_count += 1
            elif element == "지식" or element == "knowledge":
                metrics.knowledge_count += 1

    # Update response depth counts
    if response_depth:
        if response_depth == "shallow":
            metrics.shallow_responses += 1
        elif response_depth == "medium":
            metrics.medium_responses += 1
        elif response_depth == "deep":
            metrics.deep_responses += 1

    metrics.updated_at = datetime.utcnow()
