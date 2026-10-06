import os
import sys

# Ensure ai-service root is in sys.path so its app package is importable
ai_service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai-service"))
if ai_service_dir not in sys.path:
    sys.path.insert(0, ai_service_dir)

try:
    from app.transcription import transcribe_audio as _transcribe_audio
except ImportError:
    # Fallback to local whisper if imported in alternate structure
    _transcribe_audio = None


def transcribe_audio(file_path: str, model_name: str = "base") -> str:
    """
    Transcribes audio using the centralized AI service Whisper pipeline.
    """
    if _transcribe_audio is not None:
        return _transcribe_audio(file_path, model_name=model_name)

    # Fallback if app.transcription couldn't be loaded directly
    import whisper
    model = whisper.load_model(model_name)
    result = model.transcribe(file_path)
    return result.get("text", "").strip()