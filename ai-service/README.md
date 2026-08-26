# AI Service (Module 3: AI + Database)

This directory contains the **AI + Database** module for the **AI Meeting Assistant** project.

## Module Scope & Responsibilities
1. **Speech-to-Text**: Running Whisper locally for offline transcription of meeting audio. *(Implemented in Step 2)*
2. **AI Processing**: Parsing, structuring, and analyzing meeting transcripts using Google Gemini API. *(Implemented in Step 3)*
3. **Summarization**: Generating concise and informative meeting summaries. *(Implemented in Step 3)*
4. **Action-Item Extraction**: Extracting key tasks, assignees, deadlines, and action items. *(Implemented in Step 3)*
5. **Database Integration**: Storing meeting records, summaries, and action items using Cloud PostgreSQL (Neon). *(Implemented in Step 4)*
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
GEMINI_MODEL=gemini-3.6-flash
GEMINI_FALLBACK_MODEL=gemini-3.5-flash-lite

# Database Configuration (Neon Cloud PostgreSQL)
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
```

> **SECURITY WARNING**: The real `.env` file is git-ignored. `DATABASE_URL` contains sensitive passwords and MUST NEVER be committed to Git or pushed to public repositories.

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
   GEMINI_MODEL=gemini-3.6-flash
   GEMINI_FALLBACK_MODEL=gemini-3.5-flash-lite
   ```

### 2. Resilience, Retry, and Fallback Architecture
- **Primary Model**: `gemini-3.6-flash`
- **Fallback Model**: `gemini-3.5-flash-lite`

### 3. Running AI Processing CLI
Test transcript analysis using the standalone CLI helper:

```powershell
# Run with default sample transcript
python -m app.cli_ai

# Run with custom transcript argument
python -m app.cli_ai "Today we discussed the AI Meeting Assistant. Sree will finish the UI on Friday."
```

---

## Step 4: Cloud PostgreSQL Database Integration & Meeting History (Neon)

Step 4 connects the AI service to **Neon Cloud PostgreSQL** to store meeting history and structured analysis.

### 1. Neon Cloud PostgreSQL Requirements & Credentials
1. Sign up / log into [Neon Console](https://console.neon.tech/).
2. Create a PostgreSQL service.
3. Retrieve the Service URI connection string (e.g. `postgresql://user:password@host:port/defaultdb?sslmode=require`).
4. Set `DATABASE_URL` in your local `.env` file:
   ```env
   DATABASE_URL=postgresql://user:password@host:port/defaultdb?sslmode=require
   ```

### 2. Database Schema (`database/schema.sql`)
The canonical schema is stored in `database/schema.sql`. It defines 4 relational tables:
- **`MEETINGS`**: `id` (PK), `title`, `meeting_date`, `transcript`, `summary`, `created_at`, `updated_at`
- **`KEY_POINTS`**: `id` (PK), `meeting_id` (FK -> MEETINGS ON DELETE CASCADE), `point`
- **`DECISIONS`**: `id` (PK), `meeting_id` (FK -> MEETINGS ON DELETE CASCADE), `decision`
- **`ACTION_ITEMS`**: `id` (PK), `meeting_id` (FK -> MEETINGS ON DELETE CASCADE), `task`, `assigned_to` (NULL allowed), `deadline` (NULL allowed), `status` (default 'pending')

### 3. End-to-End Pipeline & Database Integration Test (`e2e_database_test`)
To test the complete workflow (`sample.wav` → Whisper → Gemini API → Neon PostgreSQL → Retrieve Meeting):

```powershell
python -m app.e2e_database_test
```

> **Note**: `app.e2e_database_test` requires a valid `DATABASE_URL` set in `.env` pointing to an accessible Neon Cloud PostgreSQL instance.

---

## Running Automated Unit Tests

Run all offline unit tests (Speech-to-Text + Gemini AI Processor + Database Module with mocked DB connections). This command does NOT make network calls or require a live database:

```powershell
python -m unittest discover -s tests
```
