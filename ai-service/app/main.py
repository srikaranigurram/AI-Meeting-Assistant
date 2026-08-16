import sys
from app.transcription import transcribe_audio


def main():
    print("==========================================")
    print("  AI Meeting Assistant - Module 3 (AI)   ")
    print("==========================================")

    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        print(f"\nTarget audio file provided: {audio_file}")
        try:
            transcript = transcribe_audio(audio_file)
            print("\n--- Transcription Output ---")
            print(transcript)
            print("----------------------------")
        except Exception as err:
            print(f"\n[ERROR] {err}")
    else:
        print("\nUsage:")
        print("  python -m app.main <path_to_audio_file>")
        print("\nExample:")
        print("  python -m app.main audio/sample.wav\n")


if __name__ == "__main__":
    main()
