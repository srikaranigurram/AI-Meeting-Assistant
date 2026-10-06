from datetime import datetime
import os
import shutil
import sys
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.meeting import Meeting, KeyPoint, Decision, ActionItem
from models.user import User
from routers.meetings import format_meeting_response
from services.auth_service import get_current_user
from services.transcription import transcribe_audio

# Ensure ai-service root is in sys.path for AI processor at runtime
ai_service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai-service"))
if ai_service_dir not in sys.path:
    sys.path.insert(0, ai_service_dir)

from app.ai_processor import process_transcript

router = APIRouter(
    prefix="/audio",
    tags=["Audio"]
)


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Complete audio pipeline associated with the authenticated user:
    1. Saves uploaded audio file locally.
    2. Transcribes audio to text using Whisper.
    3. Analyzes transcript with Gemini to extract summary, key points, decisions, and action items.
    4. Persists meeting record and all structured items to Neon PostgreSQL linked to current_user.id.
    5. Returns full transcript, Gemini analysis, and saved database meeting object.
    """
    # Create uploads folder if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Save uploaded audio
    file_path = os.path.join("uploads", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Convert audio to text using Whisper
    try:
        transcript = transcribe_audio(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Whisper transcription failed: {str(e)}"
        )

    if not transcript or not transcript.strip():
        transcript = "[No speech detected in audio file]"

    # 2. Analyze transcript with Gemini
    analysis = {
        "summary": "Audio recording transcribed without AI analysis.",
        "key_points": [],
        "decisions": [],
        "action_items": []
    }
    if transcript != "[No speech detected in audio file]":
        try:
            analysis = process_transcript(transcript)
        except Exception as e:
            # Fallback if Gemini transient error occurs
            analysis["summary"] = f"Transcript generated. AI analysis notice: {str(e)[:120]}"

    # 3. Create friendly meeting title from filename
    raw_name = os.path.splitext(file.filename)[0].replace("-", " ").replace("_", " ").strip().title()
    meeting_title = f"Audio: {raw_name}" if raw_name else "Audio Meeting Recording"

    # 4. Persist to Neon PostgreSQL with current user's ownership
    new_meeting = Meeting(
        user_id=current_user.id,
        title=meeting_title,
        meeting_date=datetime.utcnow(),
        transcript=transcript,
        summary=analysis.get("summary", "").strip()
    )
    db.add(new_meeting)
    db.flush()

    # Add Key Points
    for pt in analysis.get("key_points", []):
        if pt and str(pt).strip():
            db.add(KeyPoint(meeting_id=new_meeting.id, point=str(pt).strip()))

    # Add Decisions
    for dec in analysis.get("decisions", []):
        if dec and str(dec).strip():
            db.add(Decision(meeting_id=new_meeting.id, decision=str(dec).strip()))

    # Add Action Items
    for item in analysis.get("action_items", []):
        if isinstance(item, dict) and item.get("task"):
            db.add(ActionItem(
                meeting_id=new_meeting.id,
                task=str(item["task"]).strip(),
                assigned_to=item.get("assigned_to"),
                deadline=item.get("deadline"),
                status=item.get("status", "pending")
            ))
        elif isinstance(item, str) and item.strip():
            db.add(ActionItem(
                meeting_id=new_meeting.id,
                task=item.strip(),
                assigned_to=None,
                deadline=None,
                status="pending"
            ))

    db.commit()
    db.refresh(new_meeting)

    formatted_meeting = format_meeting_response(new_meeting)

    return {
        "filename": file.filename,
        "message": "Audio uploaded, transcribed with Whisper, analyzed by Gemini, and saved to Neon PostgreSQL successfully!",
        "transcript": transcript,
        "analysis": analysis,
        "meeting": formatted_meeting
    }