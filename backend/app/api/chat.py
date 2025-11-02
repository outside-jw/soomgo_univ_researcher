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

        # Check turn limit BEFORE incrementing
        current_turns, max_turns, limit_reached = crud.check_turn_limit(db, session_id, current_stage or "도전_이해")

        # Force stage transition if turn limit reached
        forced_transition = False
        forced_transition_message = None
        if limit_reached:
            # Determine next stage based on current stage
            stage_progression = {
                "도전_이해": "아이디어_생성",
                "아이디어_생성": "실행_준비",
                "실행_준비": "실행_준비"  # Stay at final stage
            }
            next_stage = stage_progression.get(current_stage, "아이디어_생성")

            # Only force transition if not at final stage
            if current_stage != "실행_준비":
                forced_transition = True
                current_stage = next_stage
                forced_transition_message = f"{current_stage} 단계의 최대 대화 턴 수({max_turns}턴)에 도달했습니다. 이제 {next_stage} 단계로 진행합니다."
                logger.info(f"Forced stage transition for session {session_id}: {current_stage} -> {next_stage}")

        # Generate scaffolding using Gemini
        scaffolding_data = gemini_service.generate_scaffolding(
            user_message=request.message,
            conversation_history=history,
            current_stage=current_stage
        )

        # Update turn count for current stage
        new_turns, max_turns, _ = crud.update_turn_count(db, session_id, scaffolding_data["current_stage"])

        # Check if stage transition occurred (natural or forced)
        new_stage = scaffolding_data["current_stage"]
        if new_stage != current_stage or forced_transition:
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

        # Get turn counts for all stages
        turn_counts = crud.get_turn_counts(db, session_id)

        # Create response
        response = ChatResponse(
            session_id=session_id,
            agent_message=scaffolding_data["scaffolding_question"],
            scaffolding_data=ScaffoldingResponse(**scaffolding_data),
            turn_counts=turn_counts,
            forced_transition=forced_transition,
            forced_transition_message=forced_transition_message,
            timestamp=datetime.now()
        )

        logger.info(f"Generated response for session {session_id}, stage: {scaffolding_data['current_stage']}, turns: {new_turns}/{max_turns}")
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
