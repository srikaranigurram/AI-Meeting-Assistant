import os
import shutil
from dotenv import load_dotenv


def configure_ffmpeg() -> str:
    """
    Locates and validates the FFmpeg executable from FFMPEG_PATH or system PATH,
    and ensures its directory is added to process PATH for Whisper.

    Returns:
        str: Absolute path to the resolved FFmpeg executable.

    Raises:
        RuntimeError: If FFMPEG_PATH is missing and ffmpeg is not on system PATH.
        FileNotFoundError: If the configured FFMPEG_PATH does not exist.
    """
    load_dotenv()

    ffmpeg_path = os.environ.get("FFMPEG_PATH")

    if not ffmpeg_path:
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            return system_ffmpeg
        raise RuntimeError(
            "FFmpeg configuration missing: 'FFMPEG_PATH' environment variable is not set "
            "and 'ffmpeg' was not found in system PATH. "
            "Please configure FFMPEG_PATH in your .env file or environment."
        )

    ffmpeg_path = os.path.abspath(ffmpeg_path)

    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(
            f"Configured FFMPEG_PATH does not exist: '{ffmpeg_path}'"
        )

    if os.path.isfile(ffmpeg_path):
        ffmpeg_bin_dir = os.path.dirname(ffmpeg_path)
        resolved_exe = ffmpeg_path
    elif os.path.isdir(ffmpeg_path):
        ffmpeg_bin_dir = ffmpeg_path
        exe_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        resolved_exe = os.path.join(ffmpeg_path, exe_name)
        if not os.path.exists(resolved_exe):
            raise FileNotFoundError(
                f"FFmpeg executable '{exe_name}' not found in directory: '{ffmpeg_path}'"
            )
    else:
        raise FileNotFoundError(
            f"Invalid FFMPEG_PATH target: '{ffmpeg_path}'"
        )

    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    if ffmpeg_bin_dir not in path_dirs:
        os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ.get("PATH", "")

    return resolved_exe


def transcribe_audio(audio_path: str, model_name: str = "base") -> str:
    """
    Transcribe a local audio file using OpenAI Whisper running locally.

    Args:
        audio_path (str): Path to the local audio file (.wav, .mp3, .m4a, etc.).
        model_name (str): Whisper model size to load ('tiny', 'base', 'small', etc.).
                          Defaults to 'base' for fast execution on standard laptops.

    Returns:
        str: Transcribed text from the audio file.

    Raises:
        FileNotFoundError: If the specified audio file path does not exist.
        RuntimeError: If an error occurs during model loading or transcription.
    """
    # 1. Verify that the audio file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at path: '{audio_path}'")

    # 2. Configure FFmpeg path before loading Whisper
    configure_ffmpeg()

    try:
        import whisper
    except ImportError as e:
        raise RuntimeError(
            "The 'openai-whisper' package is not installed. "
            "Please run: pip install -r requirements.txt"
        ) from e

    try:
        # 3. Load the Whisper model locally
        # Whisper automatically downloads the model weights on the first run and caches them locally.
        print(f"Loading local Whisper model ('{model_name}')...")
        model = whisper.load_model(model_name)

        # 4. Perform transcription
        # Whisper handles audio loading, resampling, and speech recognition internally.
        print(f"Transcribing audio file: '{audio_path}'...")
        result = model.transcribe(audio_path)

        # 5. Extract and clean the transcript text
        transcript_text = result.get("text", "").strip()
        return transcript_text

    except Exception as e:
        # 6. Handle unexpected errors cleanly
        raise RuntimeError(f"Error during audio transcription: {str(e)}") from e

