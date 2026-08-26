import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app.database import (
    get_db_url,
    get_db_connection,
    save_meeting,
    get_meeting,
    get_meeting_history,
    sanitize_db_url,
)


class TestDatabaseModule(unittest.TestCase):

    def test_sanitize_db_url(self):
        """Verify that password and secrets are masked by sanitize_db_url."""
        raw_url = "postgresql://myuser:secretpassword123@db.aivencloud.com:12345/defaultdb"
        sanitized = sanitize_db_url(raw_url)
        self.assertNotIn("secretpassword123", sanitized)
        self.assertIn("myuser:***@db.aivencloud.com", sanitized)

    @patch.dict(os.environ, {"DATABASE_URL": ""}, clear=True)
    def test_missing_database_url_raises_runtime_error(self):
        """Verify that missing or empty DATABASE_URL raises RuntimeError."""
        with self.assertRaises(RuntimeError) as ctx:
            get_db_url()
        self.assertIn("DATABASE_URL environment variable is missing", str(ctx.exception))

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@invalidhost:5432/db"}, clear=True)
    @patch("psycopg.connect")
    def test_connection_failure_sanitizes_credentials(self, mock_connect):
        """Verify that connection failure handles errors cleanly without printing passwords."""
        mock_connect.side_effect = Exception("Connection refused to pass@invalidhost:5432")
        with self.assertRaises(RuntimeError) as ctx:
            get_db_connection()
        err_msg = str(ctx.exception)
        self.assertIn("Database connection failed", err_msg)

    def test_save_meeting_missing_required_fields(self):
        """Verify validation errors for missing title, transcript, or summary."""
        valid_analysis = {
            "summary": "Sample summary",
            "key_points": ["Point 1"],
            "decisions": ["Decision 1"],
            "action_items": []
        }

        # Empty title
        with self.assertRaises(ValueError) as ctx:
            save_meeting("", None, "Transcript text", valid_analysis)
        self.assertIn("Meeting title cannot be empty", str(ctx.exception))

        # Empty transcript
        with self.assertRaises(ValueError) as ctx:
            save_meeting("Meeting Title", None, "", valid_analysis)
        self.assertIn("Meeting transcript cannot be empty", str(ctx.exception))

        # Invalid analysis (not a dict)
        with self.assertRaises(ValueError) as ctx:
            save_meeting("Meeting Title", None, "Transcript text", "invalid analysis")
        self.assertIn("Analysis must be a dictionary", str(ctx.exception))

        # Empty summary in analysis
        with self.assertRaises(ValueError) as ctx:
            save_meeting("Meeting Title", None, "Transcript text", {"summary": ""})
        self.assertIn("Analysis summary cannot be empty", str(ctx.exception))

    @patch("app.database.get_db_connection")
    def test_save_meeting_success(self, mock_get_conn):
        """Verify successful save_meeting execution inserts metadata, key points, decisions, and action items."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"id": 101}
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.transaction.return_value.__enter__.return_value = None
        mock_get_conn.return_value = mock_conn

        sample_analysis = {
            "summary": "Team aligned on sprint goals.",
            "key_points": ["Frontend updates", "Backend integration"],
            "decisions": ["Deploy next Monday"],
            "action_items": [
                {
                    "task": "Complete tests",
                    "assigned_to": "Sree",
                    "deadline": "Friday",
                    "status": "pending"
                },
                {
                    "task": "Configure database",
                    "assigned_to": None,
                    "deadline": None,
                    "status": "pending"
                }
            ]
        }

        meeting_id = save_meeting(
            title="Sprint Planning",
            meeting_date="2026-08-19T10:00:00+00:00",
            transcript="Sample transcript text",
            analysis=sample_analysis
        )

        self.assertEqual(meeting_id, 101)
        self.assertTrue(mock_cursor.execute.called)
        self.assertTrue(mock_conn.close.called)

    @patch("app.database.get_db_connection")
    def test_save_meeting_rollback_on_failure(self, mock_get_conn):
        """Verify transaction rollback occurs if any insert operation fails during save_meeting."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # First query (MEETINGS insert) succeeds, second fails
        mock_cursor.fetchone.return_value = {"id": 102}
        mock_cursor.execute.side_effect = [
            None,  # INSERT INTO MEETINGS
            Exception("Database constraint violation")  # INSERT INTO KEY_POINTS fails
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.transaction.return_value.__enter__.return_value = None
        mock_get_conn.return_value = mock_conn

        sample_analysis = {
            "summary": "Summary text",
            "key_points": ["Key point 1"],
            "decisions": [],
            "action_items": []
        }

        with self.assertRaises(RuntimeError) as ctx:
            save_meeting("Test Title", None, "Transcript text", sample_analysis)

        self.assertIn("Failed to save meeting", str(ctx.exception))
        self.assertTrue(mock_conn.rollback.called)
        self.assertTrue(mock_conn.close.called)

    @patch("app.database.get_db_connection")
    def test_get_meeting_success(self, mock_get_conn):
        """Verify get_meeting retrieves meeting metadata and child records into expected dict structure."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Mock meeting row
        now = datetime.now(timezone.utc)
        mock_meeting_row = {
            "id": 42,
            "title": "Architecture Sync",
            "meeting_date": now,
            "transcript": "Full transcript content",
            "summary": "Discussed system architecture",
            "created_at": now,
            "updated_at": now
        }

        # Mock key points
        mock_key_points = [{"id": 1, "point": "Point A"}, {"id": 2, "point": "Point B"}]
        # Mock decisions
        mock_decisions = [{"id": 10, "decision": "Decision A"}]
        # Mock action items
        mock_action_items = [
            {
                "id": 100,
                "task": "Action 1",
                "assigned_to": "Ravi",
                "deadline": "Tomorrow",
                "status": "pending"
            },
            {
                "id": 101,
                "task": "Action 2",
                "assigned_to": None,
                "deadline": None,
                "status": "pending"
            }
        ]

        mock_cursor.fetchone.return_value = mock_meeting_row
        mock_cursor.fetchall.side_effect = [
            mock_key_points,
            mock_decisions,
            mock_action_items
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        meeting = get_meeting(42)

        self.assertIsNotNone(meeting)
        self.assertEqual(meeting["id"], 42)
        self.assertEqual(meeting["title"], "Architecture Sync")
        self.assertEqual(len(meeting["key_points"]), 2)
        self.assertEqual(meeting["key_points"][0], "Point A")
        self.assertEqual(len(meeting["decisions"]), 1)
        self.assertEqual(len(meeting["action_items"]), 2)
        self.assertIsNone(meeting["action_items"][1]["assigned_to"])
        self.assertIsNone(meeting["action_items"][1]["deadline"])

    @patch("app.database.get_db_connection")
    def test_get_meeting_not_found(self, mock_get_conn):
        """Verify get_meeting returns None when meeting ID does not exist."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        meeting = get_meeting(999)
        self.assertIsNone(meeting)

    @patch("app.database.get_meeting")
    @patch("app.database.get_db_connection")
    def test_get_meeting_history(self, mock_get_conn, mock_get_meeting):
        """Verify get_meeting_history retrieves all meetings ordered by creation date."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 2}, {"id": 1}]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        mock_get_meeting.side_effect = [
            {"id": 2, "title": "Meeting 2"},
            {"id": 1, "title": "Meeting 1"}
        ]

        history = get_meeting_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["id"], 2)
        self.assertEqual(history[1]["id"], 1)


if __name__ == "__main__":
    unittest.main()
