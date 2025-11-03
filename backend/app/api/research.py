"""
Research data export API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session as SQLAlchemySession
from typing import List, Optional
import csv
import io
from fastapi.responses import StreamingResponse
import logging

from ..db import get_db
from .. import crud
from ..models.database import Session, Conversation, StageTransition, SessionMetric

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])


@router.get("/sessions")
async def get_all_sessions(
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Get all sessions for research analysis

    Args:
        user_id: Optional filter by user ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of sessions with metadata
    """
    try:
        if user_id:
            sessions = crud.get_user_sessions(db, user_id, skip, limit)
        else:
            # Order by created_at descending (newest first)
            sessions = db.query(Session).order_by(Session.created_at.desc()).offset(skip).limit(limit).all()

        return {
            "total": len(sessions),
            "sessions": [
                {
                    "session_id": s.id,
                    "user_id": s.user_id,
                    "assignment_text": s.assignment_text,
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                    "is_active": s.is_active
                }
                for s in sessions
            ]
        }

    except Exception as e:
        logger.error(f"Error fetching sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch sessions")


@router.get("/sessions/{session_id}/conversations")
async def get_session_conversations_api(
    session_id: str,
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Get all conversations for a session

    Args:
        session_id: Session ID
        db: Database session

    Returns:
        List of conversations with CPS annotations
    """
    try:
        # Verify session exists
        session = crud.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        conversations = crud.get_session_conversations(db, session_id, limit=1000)

        return {
            "session_id": session_id,
            "total": len(conversations),
            "conversations": [
                {
                    "id": c.id,
                    "role": c.role,
                    "message": c.message,
                    "cps_stage": c.cps_stage,
                    "metacog_elements": c.metacog_elements,
                    "response_depth": c.response_depth,
                    "should_transition": c.should_transition,
                    "reasoning": c.reasoning,
                    "created_at": c.created_at.isoformat()
                }
                for c in conversations
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")


@router.get("/sessions/{session_id}/transitions")
async def get_session_transitions_api(
    session_id: str,
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Get all stage transitions for a session

    Args:
        session_id: Session ID
        db: Database session

    Returns:
        List of stage transitions
    """
    try:
        # Verify session exists
        session = crud.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        transitions = crud.get_session_transitions(db, session_id)

        return {
            "session_id": session_id,
            "total": len(transitions),
            "transitions": [
                {
                    "id": t.id,
                    "from_stage": t.from_stage,
                    "to_stage": t.to_stage,
                    "transition_reason": t.transition_reason,
                    "message_count": t.message_count,
                    "created_at": t.created_at.isoformat()
                }
                for t in transitions
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transitions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch transitions")


@router.get("/sessions/{session_id}/metrics")
async def get_session_metrics_api(
    session_id: str,
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Get aggregated metrics for a session

    Args:
        session_id: Session ID
        db: Database session

    Returns:
        Session metrics for research analysis
    """
    try:
        # Verify session exists
        session = crud.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        metrics = db.query(SessionMetric).filter(
            SessionMetric.session_id == session_id
        ).first()

        if not metrics:
            raise HTTPException(status_code=404, detail=f"Metrics not found for session {session_id}")

        return {
            "session_id": session_id,
            "total_messages": metrics.total_messages,
            "user_messages": metrics.user_messages,
            "agent_messages": metrics.agent_messages,
            "shallow_responses": metrics.shallow_responses,
            "medium_responses": metrics.medium_responses,
            "deep_responses": metrics.deep_responses,
            "stages_completed": metrics.stages_completed,
            "total_stage_transitions": metrics.total_stage_transitions,
            "monitoring_count": metrics.monitoring_count,
            "control_count": metrics.control_count,
            "knowledge_count": metrics.knowledge_count,
            "session_duration_seconds": metrics.session_duration_seconds,
            "avg_response_time_seconds": metrics.avg_response_time_seconds,
            "completed": metrics.completed
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")


@router.get("/export/conversations/csv")
async def export_conversations_csv(
    user_id: Optional[str] = None,
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Export all conversations to CSV for research analysis

    Args:
        user_id: Optional filter by user ID
        db: Database session

    Returns:
        CSV file with all conversation data
    """
    try:
        # Query conversations
        query = db.query(Conversation).join(Session)

        if user_id:
            query = query.filter(Session.user_id == user_id)

        conversations = query.order_by(Conversation.created_at).all()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "conversation_id",
            "session_id",
            "user_id",
            "role",
            "message",
            "cps_stage",
            "metacog_elements",
            "response_depth",
            "should_transition",
            "reasoning",
            "created_at"
        ])

        # Write data
        for c in conversations:
            writer.writerow([
                c.id,
                c.session_id,
                c.session.user_id,
                c.role,
                c.message,
                c.cps_stage,
                ",".join(c.metacog_elements) if c.metacog_elements else "",
                c.response_depth,
                c.should_transition,
                c.reasoning,
                c.created_at.isoformat()
            ])

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=conversations.csv"}
        )

    except Exception as e:
        logger.error(f"Error exporting conversations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to export conversations")


@router.get("/export/metrics/csv")
async def export_metrics_csv(
    user_id: Optional[str] = None,
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Export session metrics to CSV for research analysis

    Args:
        user_id: Optional filter by user ID
        db: Database session

    Returns:
        CSV file with session metrics
    """
    try:
        # Query metrics
        query = db.query(SessionMetric).join(Session)

        if user_id:
            query = query.filter(Session.user_id == user_id)

        metrics = query.all()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "session_id",
            "user_id",
            "total_messages",
            "user_messages",
            "agent_messages",
            "shallow_responses",
            "medium_responses",
            "deep_responses",
            "stages_completed",
            "total_stage_transitions",
            "monitoring_count",
            "control_count",
            "knowledge_count",
            "session_duration_seconds",
            "avg_response_time_seconds",
            "completed",
            "created_at"
        ])

        # Write data
        for m in metrics:
            writer.writerow([
                m.session_id,
                m.session.user_id,
                m.total_messages,
                m.user_messages,
                m.agent_messages,
                m.shallow_responses,
                m.medium_responses,
                m.deep_responses,
                ",".join(m.stages_completed) if m.stages_completed else "",
                m.total_stage_transitions,
                m.monitoring_count,
                m.control_count,
                m.knowledge_count,
                m.session_duration_seconds,
                m.avg_response_time_seconds,
                m.completed,
                m.created_at.isoformat()
            ])

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=session_metrics.csv"}
        )

    except Exception as e:
        logger.error(f"Error exporting metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to export metrics")
