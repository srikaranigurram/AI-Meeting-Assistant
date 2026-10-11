import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import jwt

# Load environment configuration safely
load_dotenv()
fallback_env = os.path.join(os.path.dirname(__file__), "..", "ai-service", ".env")
if os.path.exists(fallback_env):
    load_dotenv(fallback_env)

BASE_URL = os.getenv("TEST_API_URL", "http://localhost:8000/api/v1")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ai_meeting_assistant_jwt_secret_dev_key_2026_super_secure")


def test_audio_playback_pipeline():
    token_user1 = jwt.encode(
        {'sub': '1', 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
        SECRET_KEY,
        algorithm='HS256'
    )
    token_user4 = jwt.encode(
        {'sub': '4', 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
        SECRET_KEY,
        algorithm='HS256'
    )

    sample2_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'uploads', 'sample2.wav')
    )
    assert os.path.exists(sample2_path), f"Sample audio file not found: {sample2_path}"
    expected_file_size = os.path.getsize(sample2_path)
    print(f"sample2.wav file size: {expected_file_size} bytes")

    meeting_id = None
    try:
        # 1. Upload sample2.wav as User 1
        with open(sample2_path, 'rb') as f:
            files = {'file': ('sample2.wav', f, 'audio/wav')}
            headers = {'Authorization': f'Bearer {token_user1}'}
            resp = requests.post(f'{BASE_URL}/audio/upload', files=files, headers=headers, timeout=60)

        assert resp.status_code == 200, f"Upload failed: {resp.text}"
        data = resp.json()
        meeting = data.get('meeting', {})
        meeting_id = meeting.get('id')
        duration = meeting.get('audio_duration')
        audio_url = meeting.get('audio_url')
        audio_filename = meeting.get('audio_filename')

        print(f"Created Meeting ID: {meeting_id}, Title: {meeting.get('title')}")
        print(f"Extracted Duration: {duration}s, audio_filename: {audio_filename}, audio_url: {audio_url}")

        # Check that duration reflects actual ~9.8s
        assert duration is not None, "Duration must not be None"
        assert abs(duration - 9.83) < 0.2, f"Expected ~9.8s, got {duration}s"

        # 2. Test Stream via standard Authorization Header
        stream_resp = requests.get(
            f'{BASE_URL}/audio/{meeting_id}',
            headers={'Authorization': f'Bearer {token_user1}'},
            timeout=15
        )
        assert stream_resp.status_code == 200, f"Streaming failed: {stream_resp.status_code}"
        assert len(stream_resp.content) == expected_file_size, "Stream content length does not match uploaded file"
        assert "audio/" in stream_resp.headers.get("content-type", ""), "Content-Type must be audio"
        print(f"Stream via Authorization Header: 200 OK, Received {len(stream_resp.content)} bytes")

        # 3. Verify that URL query token is NOT accepted (JWT in URL avoided)
        query_token_resp = requests.get(f'{BASE_URL}/audio/{meeting_id}?token={token_user1}', timeout=15)
        assert query_token_resp.status_code == 401, f"Expected 401 for token in URL, got {query_token_resp.status_code}"
        print("Query parameter token correctly rejected (tokens avoided in URLs)")

        # 4. Test Unauthenticated Request -> must be 401
        unauth_resp = requests.get(f'{BASE_URL}/audio/{meeting_id}', timeout=15)
        assert unauth_resp.status_code == 401, f"Expected 401, got {unauth_resp.status_code}"
        print("Unauthenticated access correctly rejected with 401")

        # 5. Test Unauthorized User (User 4 trying to access User 1 meeting) -> must be 403
        forbid_resp = requests.get(
            f'{BASE_URL}/audio/{meeting_id}',
            headers={'Authorization': f'Bearer {token_user4}'},
            timeout=15
        )
        assert forbid_resp.status_code == 403, f"Expected 403, got {forbid_resp.status_code}"
        print("Cross-user access correctly rejected with 403")

        # 6. Verify Meeting listing returns audio_filename and duration
        meetings_resp = requests.get(
            f'{BASE_URL}/meetings/{meeting_id}',
            headers={'Authorization': f'Bearer {token_user1}'},
            timeout=15
        )
        assert meetings_resp.status_code == 200
        m_data = meetings_resp.json()
        assert m_data.get('audio_filename') == 'sample2.wav'
        assert abs(m_data.get('audio_duration') - 9.83) < 0.2
        assert m_data.get('audio_url') == f"/api/v1/audio/{meeting_id}"
        print("Meeting details in database correctly verified")

        print("\nALL AUDIO PLAYBACK VERIFICATION CHECKS PASSED SUCCESSFULLY!")

    finally:
        # Clean up test meeting to leave database in clean state
        if meeting_id:
            try:
                requests.delete(
                    f'{BASE_URL}/meetings/{meeting_id}',
                    headers={'Authorization': f'Bearer {token_user1}'},
                    timeout=15
                )
                print(f"Cleaned up test meeting {meeting_id}")
            except Exception as e:
                print(f"Cleanup note: {e}")


if __name__ == '__main__':
    test_audio_playback_pipeline()
