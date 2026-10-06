import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai

load_dotenv()

router = APIRouter(
    prefix="/action-items",
    tags=["Action Items"]
)


class TranscriptRequest(BaseModel):
    transcript: str


@router.post("/")
async def extract_action_items(data: TranscriptRequest):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is missing."
        )

    if not data.transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty."
        )

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are an AI Meeting Assistant.

Analyze the following meeting transcript and extract all action items.

For each action item, include:
1. Person responsible
2. Task to complete
3. Deadline, if mentioned

If any information is not mentioned, write "Not mentioned".

Present the result in a clear and organized format.

Meeting Transcript:
{data.transcript}
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
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