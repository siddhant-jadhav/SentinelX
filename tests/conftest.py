"""
SentinelX — Pytest Configuration
"""
import os
import sys
import pytest

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override environment for testing
os.environ["DATABASE_URL"] = "sqlite:///./test_sentinelx.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-ci"
os.environ["OTX_API_KEY"] = ""


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initialize a fresh test database for the session."""
    from backend.database import init_db, engine
    from backend.models import Base

    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    db_path = "test_sentinelx.db"
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def db_session():
    """Provide a transactional database session for a test."""
    from backend.database import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def api_client():
    """Provide a FastAPI test client."""
    from fastapi.testclient import TestClient
    from backend.main import app

    with TestClient(app) as client:
        yield client
