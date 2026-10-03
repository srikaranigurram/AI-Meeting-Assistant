import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure test environment variables are set before importing application modules
os.environ.setdefault("JWT_SECRET_KEY", "test-devops-jwt-secret-key-12345")
os.environ.setdefault("GEMINI_API_KEY", "test-devops-gemini-api-key-67890")

from database import Base, get_db
from main import app
from models.user import User
from models.meeting import Meeting

# Isolated test SQLite database
TEST_DB_FILE = "test_meeting_devops.db"
TEST_DATABASE_URL = f"sqlite:///./{TEST_DB_FILE}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test tables before tests run, and clean up afterwards."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass


@pytest.fixture
def db_session():
    """Provide a clean database session for tests, clearing tables after each test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up records after each test to ensure test isolation
        with test_engine.connect() as conn:
            conn.execute(Meeting.__table__.delete())
            conn.execute(User.__table__.delete())
            conn.commit()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Registers a default test user and returns credentials."""
    user_data = {
        "username": "testuser_devops",
        "password": "SecurePassword123!"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    return user_data


@pytest.fixture
def auth_headers(client, registered_user):
    """Logs in the default test user and returns Bearer token authorization headers."""
    login_response = client.post("/auth/login", json=registered_user)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
