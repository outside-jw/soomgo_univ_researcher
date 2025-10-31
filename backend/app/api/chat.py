"""
Chat API endpoints for CPS scaffolding
"""
from fastapi import APIRouter, HTTPException
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message and receive scaffolding question

    The agent analyzes the user's message and conversation history,
    then generates an appropriate scaffolding question to promote
    creative metacognition.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Convert conversation history to dict format
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        # Generate scaffolding using Gemini
        scaffolding_data = gemini_service.generate_scaffolding(
            user_message=request.message,
            conversation_history=history,
            current_stage=request.current_stage
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

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session", response_model=SessionResponse)
async def create_session(request: SessionCreate):
    """
    Create a new conversation session

    Initializes a new session for a learner to work through
    a specific problem/assignment.
    """
    try:
        session_id = str(uuid.uuid4())

        # TODO: Store session in database
        # For now, just return the session info

        response = SessionResponse(
            session_id=session_id,
            created_at=datetime.now()
        )

        logger.info(f"Created new session: {session_id}")
        return response

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CPS Scaffolding Agent",
        "timestamp": datetime.now().isoformat()
    }
