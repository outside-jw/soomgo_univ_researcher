"""
Chat API endpoints for CPS scaffolding
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session as SQLAlchemySession
from typing import List
import uuid
from datetime import datetime
import logging

from ..models.schemas import (
    ChatRequest,
    ChatResponse,
    ScaffoldingResponse,
    SessionCreate,
    SessionResponse,
    Message
)
from ..services.gemini_service import gemini_service
from ..db import get_db
from .. import crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: SQLAlchemySession = Depends(get_db)):
    """
    Send a message and receive scaffolding question

    The agent analyzes the user's message and conversation history,
    then generates an appropriate scaffolding question to promote
    creative metacognition.
    """
    try:
        # Validate session exists if session_id provided
        session_id = request.session_id
        if session_id:
            db_session = crud.get_session(db, session_id)
            if not db_session:
                raise HTTPException(
                    status_code=404,
                    detail=f"Session {session_id} not found. Please create a session first."
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="session_id is required. Please create a session first using /api/chat/session endpoint."
            )

        # Save user message to database
        crud.create_conversation(
            db=db,
            session_id=session_id,
            role="user",
            message=request.message
        )

        # Convert conversation history to dict format
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        # Get current stage from database if not provided
        current_stage = request.current_stage
        if not current_stage:
            current_stage = crud.get_latest_stage(db, session_id)

        # Generate scaffolding using Gemini
        scaffolding_data = gemini_service.generate_scaffolding(
            user_message=request.message,
            conversation_history=history,
            current_stage=current_stage
        )

        # Check if stage transition occurred
        new_stage = scaffolding_data["current_stage"]
        if new_stage != current_stage:
            # Record stage transition
            crud.create_stage_transition(
                db=db,
                session_id=session_id,
                from_stage=current_stage,
                to_stage=new_stage,
                transition_reason=scaffolding_data.get("reasoning"),
                message_count=len(history) + 1
            )

        # Save agent message to database
        crud.create_conversation(
            db=db,
            session_id=session_id,
            role="agent",
            message=scaffolding_data["scaffolding_question"],
            cps_stage=scaffolding_data["current_stage"],
            metacog_elements=scaffolding_data.get("detected_metacog_needs", []),
            response_depth=scaffolding_data.get("response_depth"),
            should_transition=scaffolding_data.get("should_transition"),
            reasoning=scaffolding_data.get("reasoning")
        )

        # Create response
        response = ChatResponse(
            session_id=session_id,
            agent_message=scaffolding_data["scaffolding_question"],
            scaffolding_data=ScaffoldingResponse(**scaffolding_data),
            timestamp=datetime.now()
        )

        logger.info(f"Generated response for session {session_id}, stage: {scaffolding_data['current_stage']}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process message. Please try again."
        )


@router.post("/session", response_model=SessionResponse)
async def create_session(request: SessionCreate, db: SQLAlchemySession = Depends(get_db)):
    """
    Create a new conversation session

    Initializes a new session for a learner to work through
    a specific problem/assignment.
    """
    try:
        # Create session in database
        db_session = crud.create_session(db, request)

        response = SessionResponse(
            session_id=db_session.id,
            created_at=db_session.created_at
        )

        logger.info(f"Created new session: {db_session.id} for user: {request.user_id}")
        return response

    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create session. Please try again."
        )


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint

    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "CPS Scaffolding Agent",
        "timestamp": datetime.now().isoformat()
    }
