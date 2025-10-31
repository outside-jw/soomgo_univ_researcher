"""
Tests for CRUD operations
"""
import pytest
from datetime import datetime
import uuid

from app import crud
from app.models.schemas import SessionCreate
from app.models.database import Session, Conversation, StageTransition, SessionMetric


class TestSessionCRUD:
    """Test session CRUD operations"""

    def test_create_session(self, db_session, sample_session_data):
        """Test creating a new session"""
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)

        assert db_session_obj.id is not None
        assert db_session_obj.user_id == sample_session_data["user_id"]
        assert db_session_obj.assignment_text == sample_session_data["assignment_text"]
        assert db_session_obj.is_active is True
        assert db_session_obj.created_at is not None

        # Verify metrics were created
        metrics = db_session.query(SessionMetric).filter(
            SessionMetric.session_id == db_session_obj.id
        ).first()
        assert metrics is not None
        assert metrics.total_messages == 0

    def test_get_session(self, db_session, sample_session_data):
        """Test retrieving a session"""
        # Create session
        session_data = SessionCreate(**sample_session_data)
        created_session = crud.create_session(db_session, session_data)

        # Retrieve session
        retrieved_session = crud.get_session(db_session, created_session.id)
        assert retrieved_session is not None
        assert retrieved_session.id == created_session.id
        assert retrieved_session.user_id == created_session.user_id

    def test_get_nonexistent_session(self, db_session):
        """Test retrieving a non-existent session"""
        fake_id = str(uuid.uuid4())
        session = crud.get_session(db_session, fake_id)
        assert session is None

    def test_get_user_sessions(self, db_session, sample_session_data):
        """Test retrieving all sessions for a user"""
        # Create multiple sessions for the same user
        session_data = SessionCreate(**sample_session_data)
        crud.create_session(db_session, session_data)
        crud.create_session(db_session, session_data)

        # Retrieve sessions
        user_sessions = crud.get_user_sessions(db_session, sample_session_data["user_id"])
        assert len(user_sessions) == 2
        assert all(s.user_id == sample_session_data["user_id"] for s in user_sessions)

    def test_update_session(self, db_session, sample_session_data):
        """Test updating a session"""
        # Create session
        session_data = SessionCreate(**sample_session_data)
        created_session = crud.create_session(db_session, session_data)

        # Update session
        updated_session = crud.update_session(
            db_session,
            created_session.id,
            is_active=False
        )
        assert updated_session.is_active is False
        assert updated_session.completed_at is not None

    def test_delete_session(self, db_session, sample_session_data):
        """Test deleting a session"""
        # Create session
        session_data = SessionCreate(**sample_session_data)
        created_session = crud.create_session(db_session, session_data)

        # Delete session
        result = crud.delete_session(db_session, created_session.id)
        assert result is True

        # Verify deletion
        deleted_session = crud.get_session(db_session, created_session.id)
        assert deleted_session is None


class TestConversationCRUD:
    """Test conversation CRUD operations"""

    def test_create_conversation(self, db_session, sample_session_data, sample_conversation_data):
        """Test creating a conversation"""
        # Create session first
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)

        # Create conversation
        conversation = crud.create_conversation(
            db_session,
            session_id=db_session_obj.id,
            **sample_conversation_data
        )

        assert conversation.id is not None
        assert conversation.session_id == db_session_obj.id
        assert conversation.role == sample_conversation_data["role"]
        assert conversation.message == sample_conversation_data["message"]
        assert conversation.cps_stage == sample_conversation_data["cps_stage"]
        assert conversation.metacog_elements == sample_conversation_data["metacog_elements"]
        assert conversation.response_depth == sample_conversation_data["response_depth"]

        # Verify metrics were updated
        metrics = db_session.query(SessionMetric).filter(
            SessionMetric.session_id == db_session_obj.id
        ).first()
        assert metrics.total_messages == 1
        assert metrics.user_messages == 1
        assert metrics.medium_responses == 1
        assert metrics.monitoring_count == 1
        assert metrics.control_count == 1

    def test_get_conversation(self, db_session, sample_session_data, sample_conversation_data):
        """Test retrieving a conversation"""
        # Create session and conversation
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)
        created_conv = crud.create_conversation(
            db_session,
            session_id=db_session_obj.id,
            **sample_conversation_data
        )

        # Retrieve conversation
        retrieved_conv = crud.get_conversation(db_session, created_conv.id)
        assert retrieved_conv is not None
        assert retrieved_conv.id == created_conv.id

    def test_get_session_conversations(self, db_session, sample_session_data, sample_conversation_data):
        """Test retrieving all conversations for a session"""
        # Create session
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)

        # Create multiple conversations
        crud.create_conversation(db_session, session_id=db_session_obj.id, **sample_conversation_data)
        crud.create_conversation(db_session, session_id=db_session_obj.id, **sample_conversation_data)

        # Retrieve conversations
        conversations = crud.get_session_conversations(db_session, db_session_obj.id)
        assert len(conversations) == 2
        assert all(c.session_id == db_session_obj.id for c in conversations)

    def test_get_latest_conversations(self, db_session, sample_session_data, sample_conversation_data):
        """Test retrieving latest conversations with limit"""
        # Create session
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)

        # Create multiple conversations
        for _ in range(5):
            crud.create_conversation(db_session, session_id=db_session_obj.id, **sample_conversation_data)

        # Retrieve latest 3 conversations
        conversations = crud.get_latest_conversations(db_session, db_session_obj.id, limit=3)
        assert len(conversations) == 3


class TestStageTransitionCRUD:
    """Test stage transition CRUD operations"""

    def test_create_stage_transition(self, db_session, sample_session_data, sample_stage_transition_data):
        """Test creating a stage transition"""
        # Create session
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)

        # Create stage transition
        transition = crud.create_stage_transition(
            db_session,
            session_id=db_session_obj.id,
            **sample_stage_transition_data
        )

        assert transition.id is not None
        assert transition.session_id == db_session_obj.id
        assert transition.from_stage == sample_stage_transition_data["from_stage"]
        assert transition.to_stage == sample_stage_transition_data["to_stage"]
        assert transition.transition_reason == sample_stage_transition_data["transition_reason"]
        assert transition.message_count == sample_stage_transition_data["message_count"]

        # Verify metrics were updated
        metrics = db_session.query(SessionMetric).filter(
            SessionMetric.session_id == db_session_obj.id
        ).first()
        assert metrics.total_stage_transitions == 1

    def test_get_session_transitions(self, db_session, sample_session_data, sample_stage_transition_data):
        """Test retrieving all transitions for a session"""
        # Create session
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)

        # Create multiple transitions
        crud.create_stage_transition(db_session, session_id=db_session_obj.id, **sample_stage_transition_data)
        crud.create_stage_transition(db_session, session_id=db_session_obj.id, **sample_stage_transition_data)

        # Retrieve transitions
        transitions = crud.get_session_transitions(db_session, db_session_obj.id)
        assert len(transitions) == 2
        assert all(t.session_id == db_session_obj.id for t in transitions)

    def test_get_latest_stage(self, db_session, sample_session_data, sample_stage_transition_data):
        """Test retrieving the latest CPS stage"""
        # Create session
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)

        # Create stage transition
        crud.create_stage_transition(db_session, session_id=db_session_obj.id, **sample_stage_transition_data)

        # Get latest stage
        latest_stage = crud.get_latest_stage(db_session, db_session_obj.id)
        assert latest_stage == sample_stage_transition_data["to_stage"]

    def test_get_latest_stage_no_transitions(self, db_session, sample_session_data):
        """Test retrieving latest stage when no transitions exist"""
        # Create session
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)

        # Get latest stage (should return default)
        latest_stage = crud.get_latest_stage(db_session, db_session_obj.id)
        assert latest_stage == "도전_이해_기회구성"


class TestCascadeDelete:
    """Test cascade delete behavior"""

    def test_delete_session_cascades(self, db_session, sample_session_data, sample_conversation_data, sample_stage_transition_data):
        """Test that deleting a session cascades to related records"""
        # Create session
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)

        # Create related records
        crud.create_conversation(db_session, session_id=db_session_obj.id, **sample_conversation_data)
        crud.create_stage_transition(db_session, session_id=db_session_obj.id, **sample_stage_transition_data)

        # Verify records exist
        conversations = crud.get_session_conversations(db_session, db_session_obj.id)
        transitions = crud.get_session_transitions(db_session, db_session_obj.id)
        metrics = db_session.query(SessionMetric).filter(
            SessionMetric.session_id == db_session_obj.id
        ).first()

        assert len(conversations) > 0
        assert len(transitions) > 0
        assert metrics is not None

        # Delete session
        crud.delete_session(db_session, db_session_obj.id)

        # Verify cascade delete
        conversations = crud.get_session_conversations(db_session, db_session_obj.id)
        transitions = crud.get_session_transitions(db_session, db_session_obj.id)
        metrics = db_session.query(SessionMetric).filter(
            SessionMetric.session_id == db_session_obj.id
        ).first()

        assert len(conversations) == 0
        assert len(transitions) == 0
        assert metrics is None
