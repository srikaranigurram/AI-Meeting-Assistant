def test_root_endpoint(client):
    """Test root endpoint returns 200 and running status message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "running" in data["message"].lower()


def test_health_check_endpoint(client):
    """Test /health endpoint returns healthy status for Docker and monitoring."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "running" in data["message"].lower()


def test_register_validation_missing_password(client):
    """Test validation failure when required password field is missing."""
    response = client.post("/auth/register", json={"username": "missing_pass_user"})
    assert response.status_code == 422


def test_register_validation_missing_username(client):
    """Test validation failure when required username field is missing."""
    response = client.post("/auth/register", json={"password": "missing_user_pass"})
    assert response.status_code == 422


def test_create_meeting_validation_missing_title(client, auth_headers):
    """Test validation failure when title is missing in meeting creation."""
    response = client.post("/meetings/", json={"transcript": "Some text without title"}, headers=auth_headers)
    assert response.status_code == 422
