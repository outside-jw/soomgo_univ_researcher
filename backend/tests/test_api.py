"""
Tests for API endpoints
"""
import pytest
from unittest.mock import patch, MagicMock
import json

from app import crud
from app.models.schemas import SessionCreate


class TestChatAPI:
    """Test chat API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/chat/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "CPS Scaffolding Agent"

    def test_create_session(self, client, sample_session_data):
        """Test session creation endpoint"""
        response = client.post("/api/chat/session", json=sample_session_data)
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "created_at" in data

    @patch('app.services.gemini_service.gemini_service.generate_scaffolding')
    def test_send_message_success(self, mock_gemini, client, db_session, sample_session_data):
        """Test sending a message successfully"""
        # Create session first
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)

        # Mock Gemini response
        mock_gemini.return_value = {
            "current_stage": "도전_이해_자료탐색",
            "detected_metacog_needs": ["점검", "조절"],
            "response_depth": "medium",
            "scaffolding_question": "학생들이 수업에 집중하지 못하는 구체적인 상황은 무엇인가요?",
            "should_transition": False,
            "reasoning": "학습자의 응답이 중간 깊이, 더 구체적인 탐색 필요"
        }

        # Send message
        request_data = {
            "session_id": db_session_obj.id,
            "message": "학생들이 수업에 집중을 잘 안 해요",
            "conversation_history": [],
            "current_stage": "도전_이해_자료탐색"
        }
        response = client.post("/api/chat/message", json=request_data)
        assert response.status_code == 200
        data = response.json()

        assert data["session_id"] == db_session_obj.id
        assert "agent_message" in data
        assert "scaffolding_data" in data
        assert data["scaffolding_data"]["current_stage"] == "도전_이해_자료탐색"

    def test_send_message_no_session(self, client):
        """Test sending a message without session_id"""
        request_data = {
            "message": "test message",
            "conversation_history": []
        }
        response = client.post("/api/chat/message", json=request_data)
        assert response.status_code == 400
        assert "session_id is required" in response.json()["detail"]

    def test_send_message_invalid_session(self, client):
        """Test sending a message with invalid session_id"""
        request_data = {
            "session_id": "invalid-session-id",
            "message": "test message",
            "conversation_history": []
        }
        response = client.post("/api/chat/message", json=request_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch('app.services.gemini_service.gemini_service.generate_scaffolding')
    def test_stage_transition_recorded(self, mock_gemini, client, db_session, sample_session_data):
        """Test that stage transitions are recorded"""
        # Create session
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)

        # Mock Gemini response with stage transition
        mock_gemini.return_value = {
            "current_stage": "도전_이해_문제구조화",
            "detected_metacog_needs": ["조절"],
            "response_depth": "deep",
            "scaffolding_question": "이제 문제를 어떻게 정의하시겠습니까?",
            "should_transition": True,
            "reasoning": "충분한 자료 탐색 완료"
        }

        # Send message
        request_data = {
            "session_id": db_session_obj.id,
            "message": "학생들이 수업 내용이 어렵다고 느끼고, 참여 동기가 부족합니다",
            "conversation_history": [],
            "current_stage": "도전_이해_자료탐색"
        }
        response = client.post("/api/chat/message", json=request_data)
        assert response.status_code == 200

        # Verify transition was recorded
        transitions = crud.get_session_transitions(db_session, db_session_obj.id)
        assert len(transitions) == 1
        assert transitions[0].from_stage == "도전_이해_자료탐색"
        assert transitions[0].to_stage == "도전_이해_문제구조화"


class TestResearchAPI:
    """Test research API endpoints"""

    def test_get_all_sessions(self, client, db_session, sample_session_data):
        """Test retrieving all sessions"""
        # Create sessions
        session_data = SessionCreate(**sample_session_data)
        crud.create_session(db_session, session_data)
        crud.create_session(db_session, session_data)

        # Get all sessions
        response = client.get("/api/research/sessions")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["sessions"]) == 2

    def test_get_sessions_by_user(self, client, db_session, sample_session_data):
        """Test retrieving sessions filtered by user_id"""
        # Create sessions for different users
        session_data1 = SessionCreate(**sample_session_data)
        crud.create_session(db_session, session_data1)

        session_data2 = SessionCreate(user_id="another_user", assignment_text="Different task")
        crud.create_session(db_session, session_data2)

        # Get sessions for specific user
        response = client.get(f"/api/research/sessions?user_id={sample_session_data['user_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["sessions"][0]["user_id"] == sample_session_data["user_id"]

    def test_get_session_conversations(self, client, db_session, sample_session_data, sample_conversation_data):
        """Test retrieving conversations for a session"""
        # Create session and conversations
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)
        crud.create_conversation(db_session, session_id=db_session_obj.id, **sample_conversation_data)
        crud.create_conversation(db_session, session_id=db_session_obj.id, **sample_conversation_data)

        # Get conversations
        response = client.get(f"/api/research/sessions/{db_session_obj.id}/conversations")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == db_session_obj.id
        assert data["total"] == 2
        assert len(data["conversations"]) == 2

    def test_get_session_conversations_not_found(self, client):
        """Test retrieving conversations for non-existent session"""
        response = client.get("/api/research/sessions/invalid-id/conversations")
        assert response.status_code == 404

    def test_get_session_transitions(self, client, db_session, sample_session_data, sample_stage_transition_data):
        """Test retrieving transitions for a session"""
        # Create session and transitions
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)
        crud.create_stage_transition(db_session, session_id=db_session_obj.id, **sample_stage_transition_data)

        # Get transitions
        response = client.get(f"/api/research/sessions/{db_session_obj.id}/transitions")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == db_session_obj.id
        assert data["total"] == 1
        assert len(data["transitions"]) == 1

    def test_get_session_metrics(self, client, db_session, sample_session_data, sample_conversation_data):
        """Test retrieving metrics for a session"""
        # Create session and conversations
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)
        crud.create_conversation(db_session, session_id=db_session_obj.id, **sample_conversation_data)

        # Get metrics
        response = client.get(f"/api/research/sessions/{db_session_obj.id}/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == db_session_obj.id
        assert data["total_messages"] == 1
        assert data["user_messages"] == 1
        assert data["medium_responses"] == 1

    def test_export_conversations_csv(self, client, db_session, sample_session_data, sample_conversation_data):
        """Test exporting conversations to CSV"""
        # Create session and conversations
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)
        crud.create_conversation(db_session, session_id=db_session_obj.id, **sample_conversation_data)

        # Export CSV
        response = client.get("/api/research/export/conversations/csv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]

        # Verify CSV content
        csv_content = response.text
        assert "conversation_id" in csv_content
        assert "session_id" in csv_content
        assert sample_conversation_data["message"] in csv_content

    def test_export_metrics_csv(self, client, db_session, sample_session_data, sample_conversation_data):
        """Test exporting metrics to CSV"""
        # Create session and conversations
        session_data = SessionCreate(**sample_session_data)
        db_session_obj = crud.create_session(db_session, session_data)
        crud.create_conversation(db_session, session_id=db_session_obj.id, **sample_conversation_data)

        # Export CSV
        response = client.get("/api/research/export/metrics/csv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]

        # Verify CSV content
        csv_content = response.text
        assert "session_id" in csv_content
        assert "total_messages" in csv_content
        assert db_session_obj.id in csv_content

    def test_export_conversations_csv_with_user_filter(self, client, db_session, sample_session_data, sample_conversation_data):
        """Test exporting conversations filtered by user_id"""
        # Create sessions for different users
        session_data1 = SessionCreate(**sample_session_data)
        db_session1 = crud.create_session(db_session, session_data1)
        crud.create_conversation(db_session, session_id=db_session1.id, **sample_conversation_data)

        session_data2 = SessionCreate(user_id="another_user", assignment_text="Different task")
        db_session2 = crud.create_session(db_session, session_data2)
        crud.create_conversation(db_session, session_id=db_session2.id, **sample_conversation_data)

        # Export CSV for specific user
        response = client.get(f"/api/research/export/conversations/csv?user_id={sample_session_data['user_id']}")
        assert response.status_code == 200

        # Verify only user1's data is in CSV
        csv_content = response.text
        assert db_session1.id in csv_content
        assert db_session2.id not in csv_content
