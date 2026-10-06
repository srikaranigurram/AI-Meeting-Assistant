from typing import List, Optional, Union
from datetime import datetime
import os
import sys
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.meeting import Meeting, KeyPoint, Decision, ActionItem
from models.user import User
from services.auth_service import get_current_user

router = APIRouter(prefix="/meetings", tags=["Meetings"])


class ActionItemIn(BaseModel):
    task: str
    assigned_to: Optional[str] = None
    deadline: Optional[str] = None
    status: Optional[str] = "pending"


class MeetingCreate(BaseModel):
    title: str
    meeting_date: Optional[str] = None
    transcript: str = ""
    summary: str = ""
    key_points: Optional[List[str]] = []
    decisions: Optional[List[str]] = []
    action_items: Optional[List[Union[ActionItemIn, dict, str]]] = []


def format_meeting_response(meeting: Meeting) -> dict:
    return {
        "id": meeting.id,
        "user_id": meeting.user_id,
        "title": meeting.title,
        "meeting_date": meeting.meeting_date.isoformat() if meeting.meeting_date else None,
        "transcript": meeting.transcript,
        "summary": meeting.summary,
        "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
        "updated_at": meeting.updated_at.isoformat() if meeting.updated_at else None,
        "key_points": [kp.point for kp in meeting.key_points],
        "decisions": [d.decision for d in meeting.decisions],
        "action_items": [
            {
                "id": ai.id,
                "task": ai.task,
                "assigned_to": ai.assigned_to,
                "deadline": ai.deadline,
                "status": ai.status
            }
            for ai in meeting.action_items
        ]
    }


@router.post("/")
async def create_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    m_date = datetime.utcnow()
    if meeting_data.meeting_date:
        try:
            m_date = datetime.fromisoformat(meeting_data.meeting_date)
        except ValueError:
            m_date = datetime.utcnow()

    new_meeting = Meeting(
        user_id=current_user.id,
        title=meeting_data.title.strip(),
        meeting_date=m_date,
        transcript=meeting_data.transcript.strip(),
        summary=meeting_data.summary.strip()
    )

    db.add(new_meeting)
    db.flush()  # Populates new_meeting.id

    # Insert Key Points
    for pt in (meeting_data.key_points or []):
        if pt and str(pt).strip():
            db.add(KeyPoint(meeting_id=new_meeting.id, point=str(pt).strip()))

    # Insert Decisions
    for dec in (meeting_data.decisions or []):
        if dec and str(dec).strip():
            db.add(Decision(meeting_id=new_meeting.id, decision=str(dec).strip()))

    # Insert Action Items
    for item in (meeting_data.action_items or []):
        if isinstance(item, ActionItemIn):
            db.add(ActionItem(
                meeting_id=new_meeting.id,
                task=item.task,
                assigned_to=item.assigned_to,
                deadline=item.deadline,
                status=item.status or "pending"
            ))
        elif isinstance(item, dict):
            task = item.get("task", "")
            if task:
                db.add(ActionItem(
                    meeting_id=new_meeting.id,
                    task=str(task).strip(),
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

    return {
        "message": "Meeting created successfully!",
        "meeting": format_meeting_response(new_meeting)
    }


@router.get("/")
async def get_meetings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns only meetings belonging to the currently authenticated user.
    """
    meetings = (
        db.query(Meeting)
        .filter(Meeting.user_id == current_user.id)
        .order_by(Meeting.created_at.desc())
        .all()
    )
    return [format_meeting_response(m) for m in meetings]


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns a meeting by ID, enforcing that the current user owns it.
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    if meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to view this meeting"
        )

    return format_meeting_response(meeting)


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a meeting by ID, enforcing that the current user owns it.
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    if meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to delete this meeting"
        )

    db.delete(meeting)
    db.commit()

    return {
        "message": "Meeting deleted successfully!"
    }


class MeetingAnalyzeRequest(BaseModel):
    title: str
    transcript: str


@router.post("/analyze")
async def analyze_and_create_meeting(
    payload: MeetingAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyzes transcript with Gemini and saves the meeting under the authenticated user.
    """
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="Meeting title is required")
    if not payload.transcript.strip():
        raise HTTPException(status_code=400, detail="Meeting transcript cannot be empty")

    # Ensure ai-service root is in sys.path for AI processor
    ai_service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai-service"))
    if ai_service_dir not in sys.path:
        sys.path.insert(0, ai_service_dir)

    from app.ai_processor import process_transcript
    analysis = process_transcript(payload.transcript)

    new_meeting = Meeting(
        user_id=current_user.id,
        title=payload.title.strip(),
        meeting_date=datetime.utcnow(),
        transcript=payload.transcript.strip(),
        summary=analysis.get("summary", "").strip()
    )
    db.add(new_meeting)
    db.flush()

    for pt in analysis.get("key_points", []):
        if pt and str(pt).strip():
            db.add(KeyPoint(meeting_id=new_meeting.id, point=str(pt).strip()))

    for dec in analysis.get("decisions", []):
        if dec and str(dec).strip():
            db.add(Decision(meeting_id=new_meeting.id, decision=str(dec).strip()))

    for item in analysis.get("action_items", []):
        if isinstance(item, dict) and item.get("task"):
            db.add(ActionItem(
                meeting_id=new_meeting.id,
                task=str(item["task"]).strip(),
                assigned_to=item.get("assigned_to"),
                deadline=item.get("deadline"),
                status=item.get("status", "pending")
            ))

    db.commit()
    db.refresh(new_meeting)

    return {
        "message": "Meeting analyzed and saved successfully!",
        "meeting": format_meeting_response(new_meeting)
    }


class ActionItemUpdate(BaseModel):
    status: str


@router.patch("/action-items/{item_id}")
async def update_action_item_status(
    item_id: int,
    data: ActionItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates action item status, verifying that the current user owns the associated meeting.
    """
    item = db.query(ActionItem).filter(ActionItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")

    meeting = db.query(Meeting).filter(Meeting.id == item.meeting_id).first()
    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You do not have permission to update this action item"
        )

    item.status = data.status
    db.commit()
    db.refresh(item)

    return {
        "message": "Action item status updated successfully",
        "id": item.id,
        "status": item.status
    }