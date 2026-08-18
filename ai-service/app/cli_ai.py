import json
import sys
from app.ai_processor import process_transcript

DEFAULT_SAMPLE_TRANSCRIPT = (
    "Today we discussed the AI Meeting Assistant project. "
    "Sree will complete the frontend by Friday. "
    "Ravi will configure the database on Saturday. "
    "The team decided to test the application on Monday."
)


def main():
    print("==========================================")
    print("  AI Meeting Assistant - Step 3 (Gemini)  ")
    print("==========================================")

    if len(sys.argv) > 1:
        transcript = " ".join(sys.argv[1:])
        print("\nProvided Transcript:")
        print(f'"{transcript}"')
    else:
        transcript = DEFAULT_SAMPLE_TRANSCRIPT
        print("\nNo transcript argument provided. Using sample transcript:")
        print(f'"{transcript}"')

    print("\nSending transcript to Google Gemini API for structured analysis...")

    try:
        result = process_transcript(transcript)
        print("\n--- AI Analysis Output (JSON) ---")
        print(json.dumps(result, indent=2))
        print("---------------------------------")
    except Exception as err:
        print(f"\n[ERROR] {err}")


if __name__ == "__main__":
    main()
