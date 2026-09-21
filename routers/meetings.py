from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.meeting import Meeting
from models.user import User
from services.auth_service import get_current_user

router = APIRouter(prefix="/meetings", tags=["Meetings"])


class MeetingCreate(BaseModel):
    title: str
    transcript: str = ""
    summary: str = ""
    action_items: str = ""


@router.post("/")
async def create_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_meeting = Meeting(
        title=meeting_data.title,
        transcript=meeting_data.transcript,
        summary=meeting_data.summary,
        action_items=meeting_data.action_items,
        user_id=current_user.id
    )

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return {
        "message": "Meeting created successfully!",
        "meeting_id": new_meeting.id,
        "title": new_meeting.title
    }


@router.get("/")
async def get_meetings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meetings = db.query(Meeting).filter(
        Meeting.user_id == current_user.id
    ).all()

    return meetings


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    return meeting


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    db.delete(meeting)
    db.commit()

    return {
        "message": "Meeting deleted successfully!"
    }