# AI Service (Module 3: AI + Database)

This directory contains the **AI + Database** module for the **AI Meeting Assistant** project.

## Module Scope & Responsibilities
1. **Speech-to-Text**: Running Whisper locally for offline transcription of meeting audio. *(Implemented in Step 2)*
2. **AI Processing**: Parsing, structuring, and analyzing meeting transcripts using Google Gemini API. *(Implemented in Step 3)*
3. **Summarization**: Generating concise and informative meeting summaries. *(Implemented in Step 3)*
4. **Action-Item Extraction**: Extracting key tasks, assignees, deadlines, and action items. *(Implemented in Step 3)*
5. **Database Integration**: Storing meeting records, summaries, and action items using PostgreSQL. *(Upcoming Step 4)*
6. **Backend Integration**: Connecting with the central team backend to expose service endpoints.
7. **Containerization & Testing**: Dockerizing the service and implementing automated test suites for continuous integration.

---

## Environment Setup & Prerequisites

### 1. Virtual Environment Setup
Open PowerShell inside the `ai-service/` directory:

```powershell
# Navigate to the ai-service folder
cd ai-service

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment on Windows PowerShell
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration (`.env`)
Copy `.env.example` to `.env` to configure local environment variables:

```powershell
Copy-Item .env.example .env
```

Ensure `.env` contains:
```env
# FFmpeg Configuration for AI Service
FFMPEG_PATH=C:\path\to\ffmpeg\bin\ffmpeg.exe

# Google Gemini API Configuration for AI Service
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-flash-latest
GEMINI_FALLBACK_MODEL=gemini-3.5-flash
```

> **IMPORTANT**: The real `.env` file is git-ignored to ensure API keys and personal paths are never committed.

---

## Step 2: Speech-to-Text (OpenAI Whisper)

Whisper relies on **FFmpeg** for decoding audio formats (`.mp3`, `.wav`, etc.). Set `FFMPEG_PATH` in `.env` to your local FFmpeg binary path.

Run transcription on a sample audio file:
```powershell
python -m app.main sample.wav
```

---

## Step 3: AI Processing (Google Gemini API with Retries & Fallback)

Step 3 processes meeting transcripts into structured JSON analysis containing a summary, key discussion points, decisions, and action items.

### 1. Obtaining a Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Create a free API key.
3. Set your API key in your local `.env` file:
   ```env
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   GEMINI_MODEL=gemini-flash-latest
   GEMINI_FALLBACK_MODEL=gemini-3.5-flash
   ```

### 2. Resilience, Retry, and Fallback Architecture
- **Primary Model**: `gemini-flash-latest` (Automatically points to the current active stable Gemini Flash model on Google AI Studio).
- **Fallback Model**: `gemini-3.5-flash`

### 3. Running AI Processing CLI
Test transcript analysis using the standalone CLI helper:

```powershell
# Run with default sample transcript
python -m app.cli_ai

# Run with custom transcript argument
python -m app.cli_ai "Today we discussed the AI Meeting Assistant. Sree will finish the UI on Friday."
```

#### Example Input Transcript
```text
"Today we discussed the AI Meeting Assistant project.
Sree will complete the frontend by Friday.
Ravi will configure the database on Saturday.
The team decided to test the application on Monday."
```

#### Example Expected Output (Structured JSON)
```json
{
  "summary": "The team discussed the AI Meeting Assistant project, frontend development, database configuration, and testing.",
  "key_points": [
    "Frontend development",
    "Database configuration",
    "Application testing"
  ],
  "decisions": [
    "The application will be tested on Monday."
  ],
  "action_items": [
    {
      "task": "Complete the frontend",
      "assigned_to": "Sree",
      "deadline": "Friday",
      "status": "pending"
    },
    {
      "task": "Configure the database",
      "assigned_to": "Ravi",
      "deadline": "Saturday",
      "status": "pending"
    }
  ]
}
```

---

## End-to-End Pipeline Verification

To test the complete audio-to-structured-analysis pipeline (`sample.wav` → Whisper → Gemini API → JSON):

```powershell
python -m app.e2e_test
```

---

## Running Automated Unit Tests

Run all unit tests (Speech-to-Text + Gemini AI Processor) with mocked API responses (does NOT make network calls or require an API key):

```powershell
python -m unittest discover -s tests
```
