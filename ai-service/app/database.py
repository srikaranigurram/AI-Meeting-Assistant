import os
import re
from datetime import datetime, timezone
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row


def sanitize_db_url(db_url: str) -> str:
    """
    Sanitizes a database connection URL by masking password/credentials for safe logging.
    Example: postgresql://user:secret@host:5432/db -> postgresql://user:***@host:5432/db
    """
    if not db_url:
        return "[EMPTY]"
    return re.sub(r"(://[^:]+:)[^@]+@", r"\1***@", db_url)


def get_db_url() -> str:
    """
    Reads and validates DATABASE_URL from environment variables.

    Raises:
        RuntimeError: If DATABASE_URL is missing or empty.
    """
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url or not db_url.strip():
        raise RuntimeError(
            "DATABASE_URL environment variable is missing. "
            "Please set a valid PostgreSQL DATABASE_URL in your .env file or environment."
        )
    return db_url.strip()


def get_db_connection():
    """
    Creates and returns a new connection to PostgreSQL database.

    Raises:
        RuntimeError: If DATABASE_URL is missing or connection fails.
    """
    db_url = get_db_url()
    try:
        conn = psycopg.connect(db_url, row_factory=dict_row)
        return conn
    except Exception as e:
        safe_url = sanitize_db_url(db_url)
        err_msg = str(e)
        # Redact raw URL or password if present in raw error string
        if db_url in err_msg:
            err_msg = err_msg.replace(db_url, safe_url)
        err_msg = re.sub(r"(://[^:]+:)[^@]+@", r"\1***@", err_msg)
        raise RuntimeError(f"Database connection failed ({safe_url}): {err_msg}") from None


def init_db(schema_path: str = None):
    """
    Executes schema SQL file to initialize database tables in PostgreSQL.
    """
    if schema_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_schema = os.path.abspath(os.path.join(base_dir, "..", "..", "database", "schema.sql"))
        service_schema = os.path.abspath(os.path.join(base_dir, "..", "database", "schema.sql"))
        if os.path.exists(root_schema):
            schema_path = root_schema
        elif os.path.exists(service_schema):
            schema_path = service_schema
        else:
            schema_path = root_schema

    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at: '{os.path.abspath(schema_path)}'")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()


def save_meeting(title: str, meeting_date, transcript: str, analysis: dict) -> int:
    """
    Saves meeting metadata, transcript, and AI analysis (summary, key_points, decisions, action_items)
    into PostgreSQL inside an atomic transaction block.

    Args:
        title (str): Meeting title.
        meeting_date (datetime or str or None): Date of meeting.
        transcript (str): Full meeting transcript.
        analysis (dict): Structured AI analysis containing summary, key_points, decisions, action_items.

    Returns:
        int: Created meeting ID.

    Raises:
        ValueError: If required fields are missing or invalid.
        RuntimeError: If database operation fails.
    """
    if not title or not str(title).strip():
        raise ValueError("Meeting title cannot be empty.")
    if not transcript or not str(transcript).strip():
        raise ValueError("Meeting transcript cannot be empty.")
    if not isinstance(analysis, dict):
        raise ValueError("Analysis must be a dictionary.")

    summary = analysis.get("summary")
    if not summary or not str(summary).strip():
        raise ValueError("Analysis summary cannot be empty.")

    key_points = analysis.get("key_points", [])
    if not isinstance(key_points, list):
        raise ValueError("Analysis key_points must be a list.")

    decisions = analysis.get("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("Analysis decisions must be a list.")

    action_items = analysis.get("action_items", [])
    if not isinstance(action_items, list):
        raise ValueError("Analysis action_items must be a list.")

    # Format meeting_date
    if meeting_date is None:
        m_date = datetime.now(timezone.utc)
    elif isinstance(meeting_date, datetime):
        m_date = meeting_date
    elif isinstance(meeting_date, str):
        try:
            m_date = datetime.fromisoformat(meeting_date)
        except ValueError:
            m_date = datetime.now(timezone.utc)
    else:
        m_date = datetime.now(timezone.utc)

    conn = get_db_connection()
    try:
        with conn.transaction():
            with conn.cursor() as cur:
                # 1. Insert into MEETINGS
                cur.execute(
                    """
                    INSERT INTO MEETINGS (title, meeting_date, transcript, summary, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id;
                    """,
                    (title.strip(), m_date, transcript.strip(), summary.strip())
                )
                meeting_id = cur.fetchone()["id"]

                # 2. Insert into KEY_POINTS
                for point in key_points:
                    if point and str(point).strip():
                        cur.execute(
                            "INSERT INTO KEY_POINTS (meeting_id, point) VALUES (%s, %s);",
                            (meeting_id, str(point).strip())
                        )

                # 3. Insert into DECISIONS
                for decision in decisions:
                    if decision and str(decision).strip():
                        cur.execute(
                            "INSERT INTO DECISIONS (meeting_id, decision) VALUES (%s, %s);",
                            (meeting_id, str(decision).strip())
                        )

                # 4. Insert into ACTION_ITEMS
                for item in action_items:
                    if isinstance(item, dict) and item.get("task"):
                        task = str(item["task"]).strip()
                        assigned_to = item.get("assigned_to")
                        if assigned_to is not None:
                            assigned_to = str(assigned_to).strip()
                            if not assigned_to:
                                assigned_to = None

                        deadline = item.get("deadline")
                        if deadline is not None:
                            deadline = str(deadline).strip()
                            if not deadline:
                                deadline = None

                        status = str(item.get("status", "pending")).strip() or "pending"

                        cur.execute(
                            """
                            INSERT INTO ACTION_ITEMS (meeting_id, task, assigned_to, deadline, status)
                            VALUES (%s, %s, %s, %s, %s);
                            """,
                            (meeting_id, task, assigned_to, deadline, status)
                        )

        return meeting_id
    except Exception as e:
        conn.rollback()
        err_str = str(e)
        raise RuntimeError(f"Failed to save meeting: {err_str}") from e
    finally:
        conn.close()


def get_meeting(meeting_id: int) -> dict:
    """
    Retrieves a complete meeting record including transcript, summary, key points,
    decisions, and action items by meeting_id.

    Args:
        meeting_id (int): Meeting primary key.

    Returns:
        dict or None: Formatted meeting dictionary or None if not found.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Fetch meeting
            cur.execute(
                """
                SELECT id, title, meeting_date, transcript, summary, created_at, updated_at
                FROM MEETINGS
                WHERE id = %s;
                """,
                (meeting_id,)
            )
            meeting = cur.fetchone()
            if not meeting:
                return None

            # 2. Fetch key points
            cur.execute(
                "SELECT id, point FROM KEY_POINTS WHERE meeting_id = %s ORDER BY id ASC;",
                (meeting_id,)
            )
            key_points_rows = cur.fetchall()
            key_points = [row["point"] for row in key_points_rows]

            # 3. Fetch decisions
            cur.execute(
                "SELECT id, decision FROM DECISIONS WHERE meeting_id = %s ORDER BY id ASC;",
                (meeting_id,)
            )
            decisions_rows = cur.fetchall()
            decisions = [row["decision"] for row in decisions_rows]

            # 4. Fetch action items
            cur.execute(
                """
                SELECT id, task, assigned_to, deadline, status
                FROM ACTION_ITEMS
                WHERE meeting_id = %s
                ORDER BY id ASC;
                """,
                (meeting_id,)
            )
            action_items_rows = cur.fetchall()
            action_items = [
                {
                    "id": row["id"],
                    "task": row["task"],
                    "assigned_to": row["assigned_to"],
                    "deadline": row["deadline"],
                    "status": row["status"]
                }
                for row in action_items_rows
            ]

            return {
                "id": meeting["id"],
                "title": meeting["title"],
                "meeting_date": meeting["meeting_date"].isoformat() if hasattr(meeting["meeting_date"], "isoformat") else str(meeting["meeting_date"]),
                "transcript": meeting["transcript"],
                "summary": meeting["summary"],
                "created_at": meeting["created_at"].isoformat() if hasattr(meeting["created_at"], "isoformat") else str(meeting["created_at"]),
                "updated_at": meeting["updated_at"].isoformat() if hasattr(meeting["updated_at"], "isoformat") else str(meeting["updated_at"]),
                "key_points": key_points,
                "decisions": decisions,
                "action_items": action_items
            }
    finally:
        conn.close()


def get_meeting_history() -> list:
    """
    Retrieves a list of all stored meetings with complete metadata and child records,
    ordered by created_at DESC.

    Returns:
        list[dict]: List of meeting dictionaries.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM MEETINGS ORDER BY created_at DESC;")
            rows = cur.fetchall()
            meeting_ids = [row["id"] for row in rows]
    finally:
        conn.close()

    history = []
    for m_id in meeting_ids:
        m = get_meeting(m_id)
        if m:
            history.append(m)
    return history
