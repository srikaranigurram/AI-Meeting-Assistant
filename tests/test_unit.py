from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from models.user import User
from models.meeting import Meeting
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
TEST_SECRET = "test-devops-jwt-secret-key-12345"
ALGORITHM = "HS256"


def test_password_hashing():
    """Unit test: Password hashing generates valid bcrypt hash."""
    plain_password = "SecretPassword!2026"
    hashed = pwd_context.hash(plain_password)
    assert hashed != plain_password
    assert pwd_context.verify(plain_password, hashed) is True
    assert pwd_context.verify("WrongPassword", hashed) is False


def test_jwt_token_generation_and_decoding():
    """Unit test: JWT creation, claims verification, and decoding."""
    payload = {
        "sub": "42",
        "username": "vishal_devops",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, TEST_SECRET, algorithm=ALGORITHM)
    assert isinstance(token, str)

    decoded = jwt.decode(token, TEST_SECRET, algorithms=[ALGORITHM])
    assert decoded["sub"] == "42"
    assert decoded["username"] == "vishal_devops"


def test_user_model_instantiation():
    """Unit test: User ORM model initializes properly."""
    user = User(username="test_devops_user", password="hashed_password_sample")
    assert user.username == "test_devops_user"
    assert user.password == "hashed_password_sample"


def test_meeting_model_instantiation():
    """Unit test: Meeting ORM model initializes with expected attributes."""
    meeting = Meeting(
        title="Sprint Planning",
        transcript="Discussing DevOps pipeline and Docker setup.",
        summary="Sprint planning meeting concluded with DevOps tasks.",
        action_items="Vishal to setup Jenkins and Docker.",
        user_id=1
    )
    assert meeting.title == "Sprint Planning"
    assert meeting.user_id == 1
    assert "DevOps" in meeting.transcript
    assert "Jenkins" in meeting.action_items
