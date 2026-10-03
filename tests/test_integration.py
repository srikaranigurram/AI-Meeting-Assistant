import io
from unittest.mock import MagicMock
import pytest


class MockGeminiResponse:
    def __init__(self, text: str):
        self.text = text


class MockGeminiModels:
    def __init__(self, response_text: str):
        self.response_text = response_text

    def generate_content(self, model: str, contents: str):
        return MockGeminiResponse(self.response_text)


class MockGeminiClient:
    def __init__(self, api_key: str = None, response_text: str = "Mocked AI output"):
        self.models = MockGeminiModels(response_text)


def test_summary_success(client, monkeypatch):
    """Test /summary/ endpoint with mocked Gemini API."""
    expected_summary = "1. Main Points: DevOps and Testing. 2. Decisions: Use Pytest and Docker."
    monkeypatch.setattr(
        "routers.summary.genai.Client",
        lambda api_key: MockGeminiClient(api_key, expected_summary)
    )

    payload = {"transcript": "We discussed deploying the backend using Docker and Jenkins CI/CD."}
    response = client.post("/summary/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == expected_summary
    assert data["message"] == "AI meeting summary generated successfully!"


def test_summary_empty_transcript(client):
    """Test /summary/ returns 400 when transcript is empty string."""
    response = client.post("/summary/", json={"transcript": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "Transcript cannot be empty."


def test_action_items_success(client, monkeypatch):
    """Test /action-items/ endpoint with mocked Gemini API."""
    expected_actions = "- Vishal: Create Dockerfile and Jenkinsfile by Friday."
    monkeypatch.setattr(
        "routers.action_items.genai.Client",
        lambda api_key: MockGeminiClient(api_key, expected_actions)
    )

    payload = {"transcript": "Vishal will handle DevOps, testing, and Docker setup."}
    response = client.post("/action-items/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["action_items"] == expected_actions
    assert data["message"] == "Action items extracted successfully!"


def test_action_items_empty_transcript(client):
    """Test /action-items/ returns 400 when transcript is empty."""
    response = client.post("/action-items/", json={"transcript": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "Transcript cannot be empty."


def test_audio_upload_with_mocked_transcription(client, monkeypatch, tmp_path):
    """Test audio upload endpoint with mocked Whisper transcription service."""
    mock_transcript = "Welcome to the DevOps and testing sync meeting."
    monkeypatch.setattr("routers.audio.transcribe_audio", lambda path: mock_transcript)

    # Simulated audio file
    fake_audio = io.BytesIO(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00")
    files = {"file": ("test_audio.wav", fake_audio, "audio/wav")}

    response = client.post("/audio/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_audio.wav"
    assert data["transcript"] == mock_transcript
    assert "successfully" in data["message"].lower()


def test_end_to_end_meeting_workflow(client, monkeypatch):
    """Integration test: Register -> Login -> Summary -> Action Items -> Create Meeting -> Verify -> Delete."""
    # 1. Register User
    reg_res = client.post("/auth/register", json={
        "username": "workflow_user",
        "password": "WorkflowPassword123!"
    })
    assert reg_res.status_code == 200

    # 2. Login User
    login_res = client.post("/auth/login", json={
        "username": "workflow_user",
        "password": "WorkflowPassword123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Generate Summary (Mocked Gemini)
    mock_summary = "Sprint planning completed with action items assigned."
    monkeypatch.setattr(
        "routers.summary.genai.Client",
        lambda api_key: MockGeminiClient(api_key, mock_summary)
    )
    summary_res = client.post("/summary/", json={"transcript": "Team discussed the project scope."})
    assert summary_res.status_code == 200
    summary_text = summary_res.json()["summary"]

    # 4. Extract Action Items (Mocked Gemini)
    mock_actions = "1. Setup Jenkins. 2. Implement automated tests."
    monkeypatch.setattr(
        "routers.action_items.genai.Client",
        lambda api_key: MockGeminiClient(api_key, mock_actions)
    )
    actions_res = client.post("/action-items/", json={"transcript": "Team discussed the project scope."})
    assert actions_res.status_code == 200
    actions_text = actions_res.json()["action_items"]

    # 5. Create Meeting with results
    meeting_payload = {
        "title": "Comprehensive Workflow Meeting",
        "transcript": "Team discussed the project scope.",
        "summary": summary_text,
        "action_items": actions_text
    }
    create_res = client.post("/meetings/", json=meeting_payload, headers=headers)
    assert create_res.status_code == 200
    meeting_id = create_res.json()["meeting_id"]

    # 6. Retrieve and verify meeting
    get_res = client.get(f"/meetings/{meeting_id}", headers=headers)
    assert get_res.status_code == 200
    meeting = get_res.json()
    assert meeting["title"] == "Comprehensive Workflow Meeting"
    assert meeting["summary"] == mock_summary
    assert meeting["action_items"] == mock_actions

    # 7. Delete meeting
    delete_res = client.delete(f"/meetings/{meeting_id}", headers=headers)
    assert delete_res.status_code == 200

    # 8. Confirm deletion
    confirm_res = client.get(f"/meetings/{meeting_id}", headers=headers)
    assert confirm_res.status_code == 404
