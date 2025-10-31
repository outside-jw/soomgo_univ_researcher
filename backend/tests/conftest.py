"""
Pytest configuration and fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession
from fastapi.testclient import TestClient
import uuid

from app.models.database import Base
from app.main import app
from app.db import get_db


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session, db_engine):
    """Create a test client with database override"""
    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from app.api import chat, research

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Override lifespan to prevent DB initialization conflicts
    @asynccontextmanager
    async def test_lifespan(app_instance):
        # Skip DB initialization in tests
        yield

    # Recreate app with test lifespan
    test_app = FastAPI(
        title="CPS Scaffolding Agent - Test",
        version="1.0.0-test",
        lifespan=test_lifespan
    )

    # Include routers
    test_app.include_router(chat.router)
    test_app.include_router(research.router)

    # Override database dependency
    test_app.dependency_overrides[get_db] = override_get_db

    # Create test client
    client = TestClient(test_app)

    yield client

    # Cleanup
    test_app.dependency_overrides.clear()


@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        "user_id": "test_user_001",
        "assignment_text": "학교에서 학생들의 수업 참여도를 높이는 방법을 고민하고 있습니다."
    }


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing"""
    return {
        "role": "user",
        "message": "학생들이 수업에 집중하지 못하는 이유가 무엇일까요?",
        "cps_stage": "도전_이해_자료탐색",
        "metacog_elements": ["점검", "조절"],
        "response_depth": "medium",
        "should_transition": False,
        "reasoning": "학습자가 문제 원인 탐색 시작"
    }


@pytest.fixture
def sample_stage_transition_data():
    """Sample stage transition data for testing"""
    return {
        "from_stage": "도전_이해_자료탐색",
        "to_stage": "도전_이해_문제구조화",
        "transition_reason": "충분한 자료 탐색 완료, 문제 구조화 단계로 전환",
        "message_count": 5
    }
