import json
import os
import sys
from app.transcription import transcribe_audio
from app.ai_processor import process_transcript
from app.database import get_db_url, init_db, save_meeting, get_meeting, sanitize_db_url

DEFAULT_AUDIO_PATH = "sample.wav"


def main():
    print("==================================================================")
    print("  AI Meeting Assistant - End-to-End Pipeline & Database Test     ")
    print("==================================================================")

    # 0. Check Database Connection String presence
    try:
        raw_db_url = get_db_url()
        safe_url = sanitize_db_url(raw_db_url)
        print(f"\n[Database] Connecting to PostgreSQL at: {safe_url}")
    except RuntimeError as err:
        print(f"\n[ERROR] Database Configuration Error: {err}")
        print("Please configure a valid DATABASE_URL in your local .env file.")
        sys.exit(1)

    audio_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AUDIO_PATH

    if not os.path.exists(audio_path):
        print(f"\n[ERROR] Audio file not found at: '{os.path.abspath(audio_path)}'")
        sys.exit(1)

    # Step 1: Transcribe Audio
    print(f"\n[Step 1/5] Transcribing audio file: '{audio_path}' with Whisper...")
    try:
        transcript = transcribe_audio(audio_path)
        print("\n--- Whisper Transcription Output ---")
        print(transcript)
        print("------------------------------------")
    except Exception as err:
        print(f"\n[ERROR] Transcription failed: {err}")
        sys.exit(1)

    # Step 2: AI Processing
    print("\n[Step 2/5] Analyzing transcript with Google Gemini API...")
    try:
        analysis = process_transcript(transcript)
        print("\n--- Structured AI Analysis Output (JSON) ---")
        print(json.dumps(analysis, indent=2))
        print("--------------------------------------------")
    except Exception as err:
        print(f"\n[ERROR] AI processing failed: {err}")
        sys.exit(1)

    # Step 3: Initialize DB Schema (Ensuring tables exist)
    print("\n[Step 3/5] Verifying/Initializing database schema in Aiven PostgreSQL...")
    try:
        init_db()
        print("[Database] Schema verified successfully.")
    except Exception as err:
        print(f"\n[ERROR] Database schema initialization failed: {err}")
        sys.exit(1)

    # Step 4: Save Meeting to Database
    meeting_title = f"Meeting Analysis - {os.path.basename(audio_path)}"
    print(f"\n[Step 4/5] Saving meeting '{meeting_title}' into PostgreSQL...")
    try:
        meeting_id = save_meeting(
            title=meeting_title,
            meeting_date=None,
            transcript=transcript,
            analysis=analysis
        )
        print(f"[Database] Meeting saved successfully with ID: {meeting_id}")
    except Exception as err:
        print(f"\n[ERROR] Failed to save meeting to database: {err}")
        sys.exit(1)

    # Step 5: Retrieve Saved Meeting
    print(f"\n[Step 5/5] Retrieving saved meeting ID #{meeting_id} from PostgreSQL...")
    try:
        stored_meeting = get_meeting(meeting_id)
        if not stored_meeting:
            print(f"[ERROR] Could not find stored meeting ID #{meeting_id} in database!")
            sys.exit(1)

        print("\n--- Stored Meeting History Record ---")
        print(f"ID           : {stored_meeting['id']}")
        print(f"Title        : {stored_meeting['title']}")
        print(f"Created At   : {stored_meeting['created_at']}")
        print(f"Summary      : {stored_meeting['summary']}")
        print(f"Key Points   : {len(stored_meeting['key_points'])} items")
        print(f"Decisions    : {len(stored_meeting['decisions'])} items")
        print(f"Action Items : {len(stored_meeting['action_items'])} items")
        print("-------------------------------------")
        print("\n[SUCCESS] End-to-End Pipeline & Cloud PostgreSQL integration completed successfully!")
    except Exception as err:
        print(f"\n[ERROR] Failed to retrieve meeting from database: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
