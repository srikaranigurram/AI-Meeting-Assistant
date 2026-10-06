import os
import sys
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

load_dotenv()

# Ensure ai-service root is in sys.path
ai_service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai-service"))
if ai_service_dir not in sys.path:
    sys.path.insert(0, ai_service_dir)

try:
    from app.ai_processor import process_transcript
except ImportError:
    process_transcript = None

router = APIRouter(
    prefix="/action-items",
    tags=["Action Items"]
)


class TranscriptRequest(BaseModel):
    transcript: str


@router.post("/")
async def extract_action_items(data: TranscriptRequest):
    if not data.transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty."
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is missing. Please configure GEMINI_API_KEY."
        )

    try:
        if process_transcript is not None:
            analysis = process_transcript(data.transcript)
            action_items = analysis.get("action_items", [])
            return {
                "action_items": action_items,
                "message": "Action items extracted successfully!"
            }
        else:
            from google import genai
            client = genai.Client(api_key=api_key)
            model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
            response = client.models.generate_content(
                model=model_name,
                contents=f"Extract action items from the following meeting transcript:\n\n{data.transcript}"
            )
            return {
                "action_items": response.text,
                "message": "Action items extracted successfully!"
            }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini API error: {str(error)}"
        )