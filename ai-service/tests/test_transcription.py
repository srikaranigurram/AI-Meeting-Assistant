import os
import tempfile
import unittest
import wave
import struct
from unittest.mock import patch

from app.transcription import transcribe_audio, configure_ffmpeg


class TestTranscription(unittest.TestCase):

    def test_missing_audio_file_raises_error(self):
        """Verify that passing a non-existent audio file path raises FileNotFoundError."""
        invalid_path = "non_existent_audio_file.wav"
        with self.assertRaises(FileNotFoundError):
            transcribe_audio(invalid_path)

    @patch("app.transcription.load_dotenv")
    @patch("shutil.which", return_value=None)
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_ffmpeg_configuration_raises_error(self, mock_which, mock_load_dotenv):
        """Verify that missing FFMPEG_PATH and missing system ffmpeg raises RuntimeError independently of local environment."""
        with self.assertRaises(RuntimeError) as ctx:
            configure_ffmpeg()
        self.assertIn("FFmpeg configuration missing", str(ctx.exception))

    @patch("app.transcription.load_dotenv")
    @patch.dict(os.environ, {"FFMPEG_PATH": "C:\\invalid\\non_existent_ffmpeg_path\\ffmpeg.exe"}, clear=True)
    def test_invalid_ffmpeg_path_raises_error(self, mock_load_dotenv):
        """Verify that setting FFMPEG_PATH to a non-existent path raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError) as ctx:
            configure_ffmpeg()
        self.assertIn("Configured FFMPEG_PATH does not exist", str(ctx.exception))

    @patch("app.transcription.load_dotenv")
    def test_valid_ffmpeg_configuration_file(self, mock_load_dotenv):
        """Verify that a valid FFMPEG_PATH pointing to a file updates process PATH."""
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp_exe:
            fake_ffmpeg_path = tmp_exe.name

        try:
            with patch.dict(os.environ, {"FFMPEG_PATH": fake_ffmpeg_path}, clear=True):
                resolved_exe = configure_ffmpeg()
                self.assertEqual(resolved_exe, os.path.abspath(fake_ffmpeg_path))

                bin_dir = os.path.dirname(os.path.abspath(fake_ffmpeg_path))
                path_dirs = os.environ.get("PATH", "").split(os.pathsep)
                self.assertIn(bin_dir, path_dirs)
        finally:
            if os.path.exists(fake_ffmpeg_path):
                os.remove(fake_ffmpeg_path)

    def test_sample_wav_file_structure(self):
        """Verify standard library WAV file generation for sample audio testing."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            sample_wav_path = tmp_file.name

        try:
            # Generate a 1-second silent mono WAV file (16kHz, 16-bit PCM)
            sample_rate = 16000
            duration = 1.0
            num_samples = int(sample_rate * duration)

            with wave.open(sample_wav_path, "w") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                for _ in range(num_samples):
                    wav_file.writeframes(struct.pack("<h", 0))

            self.assertTrue(os.path.exists(sample_wav_path))
        finally:
            if os.path.exists(sample_wav_path):
                os.remove(sample_wav_path)


if __name__ == "__main__":
    unittest.main()
