from datetime import datetime
import mimetypes
import os
import shutil
import sys
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
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


def get_audio_duration(file_path: str) -> float:
    """
    Reads the exact duration in seconds from the local audio file.
    Tries Python's native wave module first, then falls back to ffprobe.
    """
    # 1. Native wave module for .wav files
    try:
        import wave
        with wave.open(file_path, "rb") as w:
            frames = w.getnframes()
            rate = w.getframerate()
            if rate > 0:
                return round(frames / float(rate), 2)
    except Exception:
        pass

    # 2. FFprobe inspection for all supported audio formats (.mp3, .m4a, .wav)
    try:
        from app.transcription import configure_ffmpeg
        ffmpeg_exe = configure_ffmpeg()
        ffprobe_exe = os.path.join(os.path.dirname(ffmpeg_exe), "ffprobe.exe" if os.name == "nt" else "ffprobe")
        if os.path.exists(ffprobe_exe):
            import subprocess
            cmd = [
                ffprobe_exe, "-v", "error", "-show_entries",
                "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                return round(float(res.stdout.strip()), 2)
    except Exception:
        pass

    return 0.0


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Complete audio pipeline associated with the authenticated user:
    1. Saves uploaded audio file locally.
    2. Computes the real audio duration from the file.
    3. Transcribes audio to text using Whisper.
    4. Analyzes transcript with Gemini to extract summary, key points, decisions, and action items.
    5. Persists meeting record and all structured items to Neon PostgreSQL linked to current_user.id.
    6. Returns full transcript, Gemini analysis, saved database meeting object, and audio stream URL.
    """
    safe_filename = os.path.basename(file.filename)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uploads_dir = os.path.join(base_dir, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    # Save uploaded audio
    file_path = os.path.join(uploads_dir, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Compute real audio duration from uploaded file
    audio_duration = get_audio_duration(file_path)

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
    raw_name = os.path.splitext(safe_filename)[0].replace("-", " ").replace("_", " ").strip().title()
    meeting_title = f"Audio: {raw_name}" if raw_name else "Audio Meeting Recording"

    # 4. Persist to Neon PostgreSQL with current user's ownership
    new_meeting = Meeting(
        user_id=current_user.id,
        title=meeting_title,
        meeting_date=datetime.utcnow(),
        transcript=transcript,
        summary=analysis.get("summary", "").strip(),
        audio_filename=safe_filename,
        audio_duration=audio_duration
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
        "filename": safe_filename,
        "message": "Audio uploaded, transcribed with Whisper, analyzed by Gemini, and saved to Neon PostgreSQL successfully!",
        "transcript": transcript,
        "analysis": analysis,
        "meeting": formatted_meeting,
        "audio_url": f"/api/v1/audio/{new_meeting.id}",
        "duration": audio_duration
    }


@router.get("/{meeting_id}")
async def get_audio_stream(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Streams the uploaded audio recording for a specific meeting.
    Requires standard authentication via Authorization: Bearer header (no tokens in URLs).
    Enforces user ownership check.
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to view this audio recording"
        )

    # Strictly verify that an audio file is associated with this meeting (no guessing fallbacks)
    if not meeting.audio_filename:
        raise HTTPException(status_code=404, detail="No audio file associated with this meeting")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "uploads", meeting.audio_filename)
    if not os.path.exists(file_path):
        file_path = os.path.join("uploads", meeting.audio_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found on server")

    media_type, _ = mimetypes.guess_type(file_path)
    if not media_type:
        media_type = "audio/wav"

    return FileResponse(
        file_path,
        media_type=media_type,
        filename=meeting.audio_filename,
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600"
        }
    )