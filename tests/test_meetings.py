def test_create_meeting_success(client, auth_headers):
    """Test authenticated user can create a meeting."""
    payload = {
        "title": "Architecture Review",
        "transcript": "Reviewed microservices and Docker containers.",
        "summary": "Agreed to use Docker Compose for container orchestration.",
        "action_items": "Person 4 to finalize docker-compose.yml"
    }
    response = client.post("/meetings/", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Meeting created successfully!"
    assert data["title"] == "Architecture Review"
    assert "meeting_id" in data


def test_create_meeting_unauthorized(client):
    """Test unauthenticated request cannot create a meeting."""
    payload = {"title": "Unauthorized Meeting"}
    response = client.post("/meetings/", json=payload)
    assert response.status_code in [401, 403]


def test_get_meetings_list(client, auth_headers):
    """Test fetching all meetings belonging to the authenticated user."""
    client.post("/meetings/", json={"title": "Meeting 1"}, headers=auth_headers)
    client.post("/meetings/", json={"title": "Meeting 2"}, headers=auth_headers)

    response = client.get("/meetings/", headers=auth_headers)
    assert response.status_code == 200
    meetings = response.json()
    assert len(meetings) == 2
    titles = [m["title"] for m in meetings]
    assert "Meeting 1" in titles
    assert "Meeting 2" in titles


def test_user_meeting_isolation(client, auth_headers):
    """Test user cannot see another user's meetings."""
    # User 1 creates a meeting
    client.post("/meetings/", json={"title": "User1 Private Meeting"}, headers=auth_headers)

    # Register and login User 2
    client.post("/auth/register", json={"username": "user2", "password": "User2Pass!"})
    login_res = client.post("/auth/login", json={"username": "user2", "password": "User2Pass!"})
    user2_token = login_res.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 2 list should be empty
    response = client.get("/meetings/", headers=user2_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_single_meeting_success(client, auth_headers):
    """Test fetching a specific meeting by ID."""
    create_res = client.post("/meetings/", json={"title": "Single Meeting"}, headers=auth_headers)
    meeting_id = create_res.json()["meeting_id"]

    response = client.get(f"/meetings/{meeting_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == meeting_id
    assert data["title"] == "Single Meeting"


def test_get_single_meeting_not_found(client, auth_headers):
    """Test 404 when meeting ID does not exist."""
    response = client.get("/meetings/99999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Meeting not found"


def test_delete_meeting_success(client, auth_headers):
    """Test deleting an existing meeting."""
    create_res = client.post("/meetings/", json={"title": "To Delete"}, headers=auth_headers)
    meeting_id = create_res.json()["meeting_id"]

    delete_res = client.delete(f"/meetings/{meeting_id}", headers=auth_headers)
    assert delete_res.status_code == 200
    assert delete_res.json()["message"] == "Meeting deleted successfully!"

    # Verify meeting is gone
    get_res = client.get(f"/meetings/{meeting_id}", headers=auth_headers)
    assert get_res.status_code == 404


def test_delete_meeting_not_found(client, auth_headers):
    """Test deleting non-existent meeting returns 404."""
    response = client.delete("/meetings/99999", headers=auth_headers)
    assert response.status_code == 404
