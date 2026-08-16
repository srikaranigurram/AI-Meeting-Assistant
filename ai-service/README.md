# AI Service (Module 3: AI + Database)

This directory contains the **AI + Database** module for the **AI Meeting Assistant** project.

## Module Scope & Future Responsibilities
1. **Speech-to-Text**: Running Whisper locally for offline transcription of meeting audio. *(Implemented in Step 2)*
2. **AI Processing**: Parsing, structuring, and analyzing meeting transcripts.
3. **Summarization**: Generating concise and informative meeting summaries.
4. **Action-Item Extraction**: Extracting key tasks, assignees, and action items from transcripts.
5. **Database Integration**: Storing meeting records, summaries, and action items using PostgreSQL.
6. **Backend Integration**: Connecting with the central team backend to expose service endpoints.
7. **Containerization & Testing**: Dockerizing the service and implementing automated test suites for continuous integration.

---

## Step 2: Speech-to-Text (OpenAI Whisper)

### 1. Prerequisites & Virtual Environment Setup
Open PowerShell inside the `ai-service/` directory:

```powershell
# Navigate to the ai-service folder
cd ai-service

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment on Windows PowerShell
.\venv\Scripts\Activate.ps1
```

### 2. FFmpeg Configuration (Windows / Project-Level)

OpenAI Whisper relies on **FFmpeg** for decoding audio formats (`.mp3`, `.m4a`, `.wav`, etc.). To ensure Whisper can locate FFmpeg without modifying global system environment variables:

#### Option A: Using `.env` File (Recommended)
Copy `.env.example` to `.env` and set `FFMPEG_PATH` to your local `ffmpeg.exe` path or `bin` directory:

```powershell
Copy-Item .env.example .env
```

Edit `.env` to set your local FFmpeg path:
```env
FFMPEG_PATH=C:\Users\<YourUsername>\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe
```

#### Option B: Using PowerShell Session Variable
Alternatively, set `FFMPEG_PATH` in your current PowerShell session:

```powershell
$env:FFMPEG_PATH="C:\Users\<YourUsername>\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
```

### 3. Install Dependencies
Install dependencies in your active virtual environment:

```powershell
pip install -r requirements.txt
```

---

## Testing Speech-to-Text Transcription

### Option A: Testing with Your Own Sample Audio File
1. Place a sample audio file (e.g., `.wav` or `.mp3`) inside an `audio/` folder inside `ai-service/`:
   ```powershell
   mkdir -p audio
   # Copy your sample file to: audio/sample.wav
   ```
2. Run the main module passing the path to your audio file:
   ```powershell
   python -m app.main audio/sample.wav
   ```

**Expected Output:**
```text
==========================================
  AI Meeting Assistant - Module 3 (AI)   
==========================================

Target audio file provided: audio/sample.wav
Loading local Whisper model ('base')...
Transcribing audio file: 'audio/sample.wav'...

--- Transcription Output ---
Today we discussed the project deadline and assigned tasks to the team.
----------------------------
```

### Option B: Running Unit Tests
Run the unit test suite to verify missing file handling, FFmpeg configuration validation, and module components:
```powershell
python -m unittest discover -s tests
```
