from datetime import datetime, timedelta
from jose import jwt
import os


def test_register_user_success(client):
    """Test successful user registration."""
    response = client.post("/auth/register", json={
        "username": "alice",
        "password": "Password123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered successfully!"
    assert data["username"] == "alice"
    assert "user_id" in data


def test_register_user_duplicate_username(client, registered_user):
    """Test duplicate registration returns 400."""
    response = client.post("/auth/register", json=registered_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_login_user_success(client, registered_user):
    """Test login with valid credentials returns JWT token."""
    response = client.post("/auth/login", json=registered_user)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["message"] == "Login successful!"


def test_login_user_invalid_username(client):
    """Test login with non-existent username returns 401."""
    response = client.post("/auth/login", json={
        "username": "non_existent_user",
        "password": "SomePassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_user_invalid_password(client, registered_user):
    """Test login with incorrect password returns 401."""
    response = client.post("/auth/login", json={
        "username": registered_user["username"],
        "password": "WrongPassword!"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_get_current_user_profile_success(client, auth_headers, registered_user):
    """Test /auth/me returns current user details when authorized."""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == registered_user["username"]
    assert data["message"] == "JWT authentication successful!"


def test_get_current_user_profile_unauthorized(client):
    """Test /auth/me returns 401 or 403 when Authorization header is missing."""
    response = client.get("/auth/me")
    assert response.status_code in [401, 403]


def test_get_current_user_profile_invalid_token(client):
    """Test /auth/me returns 401 when given an invalid token."""
    headers = {"Authorization": "Bearer invalid.token.string"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401
    assert "detail" in response.json()


def test_get_current_user_profile_expired_token(client):
    """Test /auth/me returns 401 when JWT token is expired."""
    secret_key = os.getenv("JWT_SECRET_KEY", "test-devops-jwt-secret-key-12345")
    expired_payload = {
        "sub": "1",
        "username": "testuser",
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    expired_token = jwt.encode(expired_payload, secret_key, algorithm="HS256")
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401
