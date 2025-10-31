"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Message(BaseModel):
    """Single message in conversation"""
    role: str = Field(..., description="Role: 'user' or 'agent'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default=None, description="Message timestamp")


class ChatRequest(BaseModel):
    """Request for chat endpoint"""
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    message: str = Field(..., description="User message")
    conversation_history: List[Message] = Field(default=[], description="Previous conversation history")
    current_stage: Optional[str] = Field(None, description="Current CPS stage if known")


class ScaffoldingResponse(BaseModel):
    """Scaffolding response from Gemini"""
    current_stage: str = Field(..., description="Inferred CPS stage")
    detected_metacog_needs: List[str] = Field(..., description="Metacognitive elements to address")
    response_depth: str = Field(..., description="Assessment: shallow|medium|deep")
    scaffolding_question: str = Field(..., description="Question to promote thinking")
    should_transition: bool = Field(..., description="Whether to move to next stage")
    reasoning: str = Field(..., description="Explanation of decision")


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    session_id: str = Field(..., description="Session ID")
    agent_message: str = Field(..., description="Agent's scaffolding question")
    scaffolding_data: ScaffoldingResponse = Field(..., description="Detailed scaffolding analysis")
    timestamp: datetime = Field(..., description="Response timestamp")


class SessionCreate(BaseModel):
    """Request to create new session"""
    user_id: Optional[str] = Field(None, description="User identifier")
    assignment_text: str = Field(..., description="Assignment/problem text")


class SessionResponse(BaseModel):
    """Response with session info"""
    session_id: str = Field(..., description="Session ID")
    created_at: datetime = Field(..., description="Creation timestamp")
