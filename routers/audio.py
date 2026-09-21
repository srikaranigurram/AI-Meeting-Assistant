from fastapi import APIRouter, UploadFile, File
import os
import shutil

from services.transcription import transcribe_audio

router = APIRouter(
    prefix="/audio",
    tags=["Audio"]
)


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):

    # Create uploads folder if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Save uploaded audio
    file_path = os.path.join("uploads", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert audio to text
    transcript = transcribe_audio(file_path)

    return {
        "filename": file.filename,
        "message": "Audio uploaded and transcribed successfully!",
        "transcript": transcript
    }