"""
Integration tests for full conversation flow
"""
import pytest
from unittest.mock import patch, MagicMock

from app import crud
from app.models.schemas import SessionCreate


class TestFullConversationFlow:
    """Test complete conversation flow from start to finish"""

    @patch('app.services.gemini_service.gemini_service.generate_scaffolding')
    def test_complete_cps_journey(self, mock_gemini, client, db_session, sample_session_data):
        """Test a complete CPS problem-solving journey"""

        # Stage 1: Create session
        response = client.post("/api/chat/session", json=sample_session_data)
        assert response.status_code == 200
        session_id = response.json()["session_id"]

        # Stage 2: 도전 이해 - 기회 구성
        mock_gemini.return_value = {
            "current_stage": "도전_이해_기회구성",
            "detected_metacog_needs": ["지식"],
            "response_depth": "medium",
            "scaffolding_question": "과거에 비슷한 문제를 해결한 경험이 있나요?",
            "should_transition": False,
            "reasoning": "기회 구성 단계에서 사전 경험 활성화 필요"
        }

        message1 = {
            "session_id": session_id,
            "message": "학생들의 수업 참여도를 높이고 싶습니다",
            "conversation_history": [],
            "current_stage": "도전_이해_기회구성"
        }
        response = client.post("/api/chat/message", json=message1)
        assert response.status_code == 200
        assert response.json()["scaffolding_data"]["current_stage"] == "도전_이해_기회구성"

        # Stage 3: 도전 이해 - 자료 탐색
        mock_gemini.return_value = {
            "current_stage": "도전_이해_자료탐색",
            "detected_metacog_needs": ["점검", "조절"],
            "response_depth": "deep",
            "scaffolding_question": "학생들이 집중하지 못하는 구체적인 원인을 몇 가지 더 찾아볼 수 있나요?",
            "should_transition": True,
            "reasoning": "충분한 경험 활성화, 자료 탐색 단계로 전환"
        }

        message2 = {
            "session_id": session_id,
            "message": "네, 작년에도 비슷한 문제가 있었어요",
            "conversation_history": [
                {"role": "user", "content": message1["message"]},
                {"role": "agent", "content": "과거에 비슷한 문제를 해결한 경험이 있나요?"}
            ],
            "current_stage": "도전_이해_기회구성"
        }
        response = client.post("/api/chat/message", json=message2)
        assert response.status_code == 200
        assert response.json()["scaffolding_data"]["current_stage"] == "도전_이해_자료탐색"

        # Verify stage transition was recorded
        transitions = crud.get_session_transitions(db_session, session_id)
        assert len(transitions) == 1
        assert transitions[0].from_stage == "도전_이해_기회구성"
        assert transitions[0].to_stage == "도전_이해_자료탐색"

        # Stage 4: Continue with data exploration
        mock_gemini.return_value = {
            "current_stage": "도전_이해_자료탐색",
            "detected_metacog_needs": ["조절"],
            "response_depth": "deep",
            "scaffolding_question": "이 중에서 가장 먼저 해결해야 할 원인은 무엇이라고 생각하나요?",
            "should_transition": False,
            "reasoning": "충분한 원인 파악, 우선순위 결정 유도"
        }

        message3 = {
            "session_id": session_id,
            "message": "수업 내용이 어렵고, 수업 방식이 일방적이며, 학생들의 관심사와 무관한 내용이 많습니다",
            "conversation_history": [
                {"role": "user", "content": message1["message"]},
                {"role": "agent", "content": "과거에 비슷한 문제를 해결한 경험이 있나요?"},
                {"role": "user", "content": message2["message"]},
                {"role": "agent", "content": "학생들이 집중하지 못하는 구체적인 원인을 몇 가지 더 찾아볼 수 있나요?"}
            ],
            "current_stage": "도전_이해_자료탐색"
        }
        response = client.post("/api/chat/message", json=message3)
        assert response.status_code == 200

        # Stage 5: Transition to problem formulation
        mock_gemini.return_value = {
            "current_stage": "도전_이해_문제구조화",
            "detected_metacog_needs": ["조절"],
            "response_depth": "medium",
            "scaffolding_question": "이 문제를 '어떻게 하면...?' 형식의 질문으로 다시 표현해볼 수 있나요?",
            "should_transition": True,
            "reasoning": "우선순위 결정 완료, 문제 구조화 단계로 전환"
        }

        message4 = {
            "session_id": session_id,
            "message": "수업 내용의 난이도 조절이 가장 중요할 것 같아요",
            "conversation_history": [
                {"role": "user", "content": message1["message"]},
                {"role": "agent", "content": "과거에 비슷한 문제를 해결한 경험이 있나요?"},
                {"role": "user", "content": message2["message"]},
                {"role": "agent", "content": "학생들이 집중하지 못하는 구체적인 원인을 몇 가지 더 찾아볼 수 있나요?"},
                {"role": "user", "content": message3["message"]},
                {"role": "agent", "content": "이 중에서 가장 먼저 해결해야 할 원인은 무엇이라고 생각하나요?"}
            ],
            "current_stage": "도전_이해_자료탐색"
        }
        response = client.post("/api/chat/message", json=message4)
        assert response.status_code == 200
        assert response.json()["scaffolding_data"]["current_stage"] == "도전_이해_문제구조화"

        # Verify all conversations were saved
        conversations = crud.get_session_conversations(db_session, session_id)
        assert len(conversations) == 8  # 4 user + 4 agent messages

        # Verify metrics were updated
        response = client.get(f"/api/research/sessions/{session_id}/metrics")
        assert response.status_code == 200
        metrics = response.json()
        assert metrics["total_messages"] == 8
        assert metrics["user_messages"] == 4
        assert metrics["agent_messages"] == 4
        assert metrics["total_stage_transitions"] == 2
        assert metrics["deep_responses"] >= 2

        # Verify we can export the data
        response = client.get("/api/research/export/conversations/csv")
        assert response.status_code == 200
        csv_content = response.text
        assert session_id in csv_content
        assert "학생들의 수업 참여도" in csv_content


class TestMetricsCalculation:
    """Test automatic metrics calculation"""

    @patch('app.services.gemini_service.gemini_service.generate_scaffolding')
    def test_metrics_update_on_conversation(self, mock_gemini, client, db_session, sample_session_data):
        """Test that metrics are automatically updated when conversations are added"""

        # Create session
        response = client.post("/api/chat/session", json=sample_session_data)
        session_id = response.json()["session_id"]

        # Initial metrics should be zero
        response = client.get(f"/api/research/sessions/{session_id}/metrics")
        initial_metrics = response.json()
        assert initial_metrics["total_messages"] == 0
        assert initial_metrics["user_messages"] == 0
        assert initial_metrics["monitoring_count"] == 0

        # Send message with monitoring metacog element
        mock_gemini.return_value = {
            "current_stage": "도전_이해_기회구성",
            "detected_metacog_needs": ["점검"],
            "response_depth": "deep",
            "scaffolding_question": "이 과제는 어느 정도 어렵다고 생각하나요?",
            "should_transition": False,
            "reasoning": "점검 메타인지 촉진"
        }

        message = {
            "session_id": session_id,
            "message": "학생 참여도를 높이는 방법을 찾고 싶습니다",
            "conversation_history": [],
            "current_stage": "도전_이해_기회구성"
        }
        client.post("/api/chat/message", json=message)

        # Verify metrics were updated
        response = client.get(f"/api/research/sessions/{session_id}/metrics")
        updated_metrics = response.json()
        assert updated_metrics["total_messages"] == 2  # user + agent
        assert updated_metrics["user_messages"] == 1
        assert updated_metrics["agent_messages"] == 1
        assert updated_metrics["deep_responses"] == 1
        assert updated_metrics["monitoring_count"] == 1


class TestErrorHandling:
    """Test error handling in integration scenarios"""

    def test_message_without_session(self, client):
        """Test sending message without creating session first"""
        message = {
            "message": "test message",
            "conversation_history": []
        }
        response = client.post("/api/chat/message", json=message)
        assert response.status_code == 400

    def test_invalid_session_id(self, client):
        """Test using invalid session_id"""
        message = {
            "session_id": "nonexistent-session",
            "message": "test message",
            "conversation_history": []
        }
        response = client.post("/api/chat/message", json=message)
        assert response.status_code == 404

    @patch('app.services.gemini_service.gemini_service.generate_scaffolding')
    def test_gemini_service_failure(self, mock_gemini, client, db_session, sample_session_data):
        """Test handling of Gemini service failure"""
        # Create session
        response = client.post("/api/chat/session", json=sample_session_data)
        session_id = response.json()["session_id"]

        # Mock Gemini failure
        mock_gemini.side_effect = Exception("Gemini API error")

        message = {
            "session_id": session_id,
            "message": "test message",
            "conversation_history": [],
            "current_stage": "도전_이해_기회구성"
        }
        response = client.post("/api/chat/message", json=message)
        assert response.status_code == 500


class TestDataExport:
    """Test data export functionality"""

    @patch('app.services.gemini_service.gemini_service.generate_scaffolding')
    def test_csv_export_completeness(self, mock_gemini, client, db_session, sample_session_data):
        """Test that CSV export contains all required data"""
        # Create session and conversations
        response = client.post("/api/chat/session", json=sample_session_data)
        session_id = response.json()["session_id"]

        mock_gemini.return_value = {
            "current_stage": "도전_이해_기회구성",
            "detected_metacog_needs": ["점검", "조절"],
            "response_depth": "deep",
            "scaffolding_question": "테스트 질문",
            "should_transition": False,
            "reasoning": "테스트"
        }

        # Send multiple messages
        for i in range(3):
            message = {
                "session_id": session_id,
                "message": f"테스트 메시지 {i}",
                "conversation_history": [],
                "current_stage": "도전_이해_기회구성"
            }
            client.post("/api/chat/message", json=message)

        # Export conversations CSV
        response = client.get("/api/research/export/conversations/csv")
        assert response.status_code == 200
        csv_content = response.text

        # Verify CSV headers
        assert "conversation_id" in csv_content
        assert "session_id" in csv_content
        assert "role" in csv_content
        assert "message" in csv_content
        assert "cps_stage" in csv_content
        assert "metacog_elements" in csv_content
        assert "response_depth" in csv_content

        # Verify data rows
        lines = csv_content.strip().split('\n')
        assert len(lines) >= 7  # header + 6 messages (3 user + 3 agent)

        # Export metrics CSV
        response = client.get("/api/research/export/metrics/csv")
        assert response.status_code == 200
        csv_content = response.text

        # Verify metrics headers
        assert "session_id" in csv_content
        assert "total_messages" in csv_content
        assert "monitoring_count" in csv_content
        assert "control_count" in csv_content
