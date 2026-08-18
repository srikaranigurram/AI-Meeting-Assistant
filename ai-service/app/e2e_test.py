import json
import os
import sys
from app.transcription import transcribe_audio
from app.ai_processor import process_transcript

DEFAULT_AUDIO_PATH = "sample.wav"


def main():
    print("==================================================")
    print("  AI Meeting Assistant - End-to-End Pipeline Test ")
    print("==================================================")

    audio_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_AUDIO_PATH

    if not os.path.exists(audio_path):
        print(f"\n[ERROR] Audio file not found at: '{os.path.abspath(audio_path)}'")
        sys.exit(1)

    print(f"\n[Step 1/2] Transcribing audio file: '{audio_path}' with Whisper...")
    try:
        transcript = transcribe_audio(audio_path)
        print("\n--- Whisper Transcription Output ---")
        print(transcript)
        print("------------------------------------")
    except Exception as err:
        print(f"\n[ERROR] Transcription failed: {err}")
        sys.exit(1)

    print("\n[Step 2/2] Analyzing transcript with Google Gemini API...")
    try:
        analysis = process_transcript(transcript)
        print("\n--- Final Structured AI Analysis (JSON) ---")
        print(json.dumps(analysis, indent=2))
        print("--------------------------------------------")
        print("\n[SUCCESS] End-to-end pipeline completed successfully!")
    except Exception as err:
        print(f"\n[ERROR] AI processing failed: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
