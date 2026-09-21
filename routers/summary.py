import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai

load_dotenv()

router = APIRouter(prefix="/summary", tags=["Summary"])


class TranscriptRequest(BaseModel):
    transcript: str


@router.post("/")
async def generate_summary(data: TranscriptRequest):
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

Analyze the following meeting transcript and provide a clear,
well-organized meeting summary.

Include:
1. Main Discussion Points
2. Important Decisions
3. Action Items
4. Deadlines, if mentioned

If any information is not available, write "Not mentioned".

Keep the response concise and easy to understand.

Meeting Transcript:
{data.transcript}
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        return {
            "summary": response.text,
            "message": "AI meeting summary generated successfully!"
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini API error: {str(error)}"
        )