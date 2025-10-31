"""
Database models for CPS scaffolding research system
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Session(Base):
    """User session for problem-solving task"""
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(255), nullable=True, index=True)
    assignment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    conversations = relationship("Conversation", back_populates="session", cascade="all, delete-orphan")
    stage_transitions = relationship("StageTransition", back_populates="session", cascade="all, delete-orphan")
    metrics = relationship("SessionMetric", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"


class Conversation(Base):
    """Individual conversation messages with CPS annotations"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(10), nullable=False)  # 'user' or 'agent'
    message = Column(Text, nullable=False)
    cps_stage = Column(String(50), nullable=True)  # Current CPS stage
    metacog_elements = Column(JSON, nullable=True)  # List of metacognitive elements
    response_depth = Column(String(20), nullable=True)  # 'shallow', 'medium', 'deep'
    should_transition = Column(Boolean, nullable=True)  # Whether agent suggested transition
    reasoning = Column(Text, nullable=True)  # Agent's reasoning for scaffolding decision
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    session = relationship("Session", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id={self.session_id}, role={self.role})>"


class StageTransition(Base):
    """CPS stage transitions for analysis"""
    __tablename__ = "stage_transitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    from_stage = Column(String(50), nullable=True)  # Previous stage (null for first stage)
    to_stage = Column(String(50), nullable=False)  # New stage
    transition_reason = Column(Text, nullable=True)  # Why transition occurred
    message_count = Column(Integer, nullable=False, default=0)  # Number of messages in previous stage
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    session = relationship("Session", back_populates="stage_transitions")

    def __repr__(self):
        return f"<StageTransition(id={self.id}, from={self.from_stage}, to={self.to_stage})>"


class SessionMetric(Base):
    """Aggregated metrics per session for research analysis"""
    __tablename__ = "session_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)

    # Message counts
    total_messages = Column(Integer, default=0, nullable=False)
    user_messages = Column(Integer, default=0, nullable=False)
    agent_messages = Column(Integer, default=0, nullable=False)

    # Response depth distribution
    shallow_responses = Column(Integer, default=0, nullable=False)
    medium_responses = Column(Integer, default=0, nullable=False)
    deep_responses = Column(Integer, default=0, nullable=False)

    # Stage progression
    stages_completed = Column(JSON, nullable=True)  # List of completed stages
    total_stage_transitions = Column(Integer, default=0, nullable=False)

    # Metacognitive element usage
    monitoring_count = Column(Integer, default=0, nullable=False)  # 점검
    control_count = Column(Integer, default=0, nullable=False)  # 조절
    knowledge_count = Column(Integer, default=0, nullable=False)  # 지식

    # Time metrics
    session_duration_seconds = Column(Integer, nullable=True)
    avg_response_time_seconds = Column(Integer, nullable=True)

    # Completion status
    completed = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="metrics")

    def __repr__(self):
        return f"<SessionMetric(session_id={self.session_id}, total_messages={self.total_messages})>"
