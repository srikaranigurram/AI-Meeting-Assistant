import os
import unittest
from unittest.mock import patch, MagicMock

from app.ai_processor import process_transcript


class TestAIProcessorGemini(unittest.TestCase):

    def test_empty_transcript_raises_value_error(self):
        """Verify that empty or whitespace-only transcript raises ValueError."""
        for invalid_input in ["", "   ", None]:
            with self.subTest(transcript=invalid_input):
                with self.assertRaises(ValueError) as ctx:
                    process_transcript(invalid_input)
                self.assertEqual(str(ctx.exception), "Transcript cannot be empty.")

    @patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=True)
    def test_missing_api_key_raises_runtime_error(self):
        """Verify that missing GEMINI_API_KEY environment variable raises RuntimeError."""
        with self.assertRaises(RuntimeError) as ctx:
            process_transcript("Valid transcript text.")
        self.assertIn("GEMINI_API_KEY environment variable is missing", str(ctx.exception))

    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_test_key_123"}, clear=True)
    @patch("google.genai.Client")
    def test_valid_gemini_response_parsing(self, mock_client_cls):
        """Verify that valid Gemini JSON response is parsed into expected Python dictionary structure."""
        mock_response = MagicMock()
        mock_response.text = """{
            "summary": "The team discussed project progress and assigned upcoming tasks.",
            "key_points": ["Frontend progress", "Database configuration"],
            "decisions": ["Test application on Monday"],
            "action_items": [
                {
                    "task": "Complete frontend",
                    "assigned_to": "Sree",
                    "deadline": "Friday",
                    "status": "pending"
                }
            ]
        }"""
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        sample_transcript = "Sree will complete frontend by Friday."
        result = process_transcript(sample_transcript)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["summary"], "The team discussed project progress and assigned upcoming tasks.")
        self.assertEqual(len(result["key_points"]), 2)
        self.assertEqual(len(result["decisions"]), 1)
        self.assertEqual(len(result["action_items"]), 1)
        self.assertEqual(result["action_items"][0]["task"], "Complete frontend")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_test_key_123"}, clear=True)
    @patch("time.sleep", return_value=None)
    @patch("google.genai.Client")
    def test_retry_on_503_transient_error_success(self, mock_client_cls, mock_sleep):
        """Verify that a 503 transient error retries with backoff and succeeds on subsequent attempt."""
        mock_success_response = MagicMock()
        mock_success_response.text = """{
            "summary": "Summary after retry",
            "key_points": [],
            "decisions": [],
            "action_items": []
        }"""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = [
            Exception("503 UNAVAILABLE: High demand"),
            mock_success_response
        ]
        mock_client_cls.return_value = mock_client

        result = process_transcript("Meeting transcript text.")
        self.assertEqual(result["summary"], "Summary after retry")
        self.assertEqual(mock_client.models.generate_content.call_count, 2)
        mock_sleep.assert_called_with(2)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_test_key_123", "GEMINI_FALLBACK_MODEL": "gemini-1.5-flash"}, clear=True)
    @patch("time.sleep", return_value=None)
    @patch("google.genai.Client")
    def test_fallback_model_success_when_primary_exhausted(self, mock_client_cls, mock_sleep):
        """Verify that when primary model fails all retries with 503, fallback model is tried and succeeds."""
        mock_fallback_response = MagicMock()
        mock_fallback_response.text = """{
            "summary": "Summary from fallback model",
            "key_points": [],
            "decisions": [],
            "action_items": []
        }"""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = [
            Exception("503 UNAVAILABLE"),  # Attempt 1 primary
            Exception("503 UNAVAILABLE"),  # Attempt 2 primary
            Exception("503 UNAVAILABLE"),  # Attempt 3 primary
            mock_fallback_response         # Attempt 1 fallback
        ]
        mock_client_cls.return_value = mock_client

        result = process_transcript("Meeting transcript text.")
        self.assertEqual(result["summary"], "Summary from fallback model")
        self.assertEqual(mock_client.models.generate_content.call_count, 4)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_test_key_123", "GEMINI_FALLBACK_MODEL": "gemini-1.5-flash"}, clear=True)
    @patch("time.sleep", return_value=None)
    @patch("google.genai.Client")
    def test_failure_when_all_retries_and_fallback_exhausted(self, mock_client_cls, mock_sleep):
        """Verify that when both primary and fallback models fail with 503, RuntimeError is raised."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("503 UNAVAILABLE: High demand")
        mock_client_cls.return_value = mock_client

        with self.assertRaises(RuntimeError) as ctx:
            process_transcript("Meeting transcript text.")
        self.assertIn("Gemini service unavailable on primary", str(ctx.exception))

    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_test_key_123"}, clear=True)
    @patch("google.genai.Client")
    def test_invalid_json_response_handling(self, mock_client_cls):
        """Verify that malformed or non-JSON Gemini response raises ValueError."""
        mock_response = MagicMock()
        mock_response.text = "This is raw non-JSON text output."
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        with self.assertRaises(ValueError) as ctx:
            process_transcript("Sample meeting transcript text.")
        self.assertEqual(str(ctx.exception), "AI model returned invalid JSON.")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_test_key_123"}, clear=True)
    @patch("google.genai.Client")
    def test_missing_required_fields_handling(self, mock_client_cls):
        """Verify that JSON response missing top-level required fields raises ValueError."""
        mock_response = MagicMock()
        mock_response.text = """{
            "summary": "Summary text",
            "key_points": ["Point 1"]
        }"""
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        with self.assertRaises(ValueError) as ctx:
            process_transcript("Sample meeting transcript text.")
        self.assertEqual(str(ctx.exception), "AI model returned invalid JSON.")


if __name__ == "__main__":
    unittest.main()
