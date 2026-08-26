# AI-Meeting-Assistant
AI-powered meeting assistant that converts meeting audio into transcripts, summaries, and actionable tasks.

## 📌 About the Project

AI-Meeting-Assistant is an AI-powered web application designed to simplify meeting management.

The application allows users to upload or record meeting audio. The system converts the audio into text, generates an AI-powered summary, identifies important discussion points, and extracts actionable tasks from the meeting.

All processed meetings are stored securely in cloud PostgreSQL so users can access their previous meetings, transcripts, summaries, and action items whenever needed.

The project also demonstrates modern DevOps practices including Git/GitHub, Docker, Jenkins, automated testing, and CI/CD.

---

## ✅ Completed Checkpoints

- **STEP 1: Project Setup** ✅
- **STEP 2: Speech-to-Text (Whisper)** ✅
- **STEP 3: AI Processing (Google Gemini API with retries & fallback)** ✅
- **STEP 4: Cloud PostgreSQL Database + Meeting History (Aiven PostgreSQL)** ✅

---

## ✨ Features

- 🎙️ Record meeting audio
- 📁 Upload recorded meeting audio
- 📝 Automatic speech-to-text transcription (Whisper)
- 🤖 AI-generated meeting summaries (Google Gemini API)
- ✅ Automatic action-item extraction with assigned tasks and deadlines
- ☁️ Cloud database storage using Aiven PostgreSQL
- 📚 Store meeting history, decisions, key discussion points
- 🔒 Secure environment variable configuration (`DATABASE_URL`, `GEMINI_API_KEY`)
- 🧪 Comprehensive offline unit testing & integration test suite

---

## 🗄️ Database Architecture & Schema (Step 4)

Meeting data and AI analysis are stored in **Aiven Cloud PostgreSQL** using a normalized relational schema (`database/schema.sql`):

- `MEETINGS`: Stores meeting metadata, transcript, and concise summary (`id`, `title`, `meeting_date`, `transcript`, `summary`, `created_at`, `updated_at`).
- `KEY_POINTS`: Key discussion topics linked to a meeting (`id`, `meeting_id` FK -> MEETINGS ON DELETE CASCADE, `point`).
- `DECISIONS`: Decisions made during the meeting (`id`, `meeting_id` FK -> MEETINGS ON DELETE CASCADE, `decision`).
- `ACTION_ITEMS`: Actionable tasks (`id`, `meeting_id` FK -> MEETINGS ON DELETE CASCADE, `task`, `assigned_to` [NULL allowed], `deadline` [NULL allowed], `status`).

### Database Setup & Connection
Connect to Aiven PostgreSQL via the environment variable `DATABASE_URL`:
```env
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
```

> **SECURITY WARNING**: `DATABASE_URL` contains database connection credentials and must NEVER be committed to Git.

---

## 🧪 Testing

### Running Unit Tests (Offline)
Runs unit tests for Speech-to-Text, Gemini AI processor, and Database CRUD functions (with mocked connections):
```powershell
cd ai-service
.\venv\Scripts\python.exe -m unittest discover -s tests
```

### Running Real Cloud Database Integration Test
Runs the end-to-end pipeline (`sample.wav` → Whisper → Gemini API → Aiven PostgreSQL → Retrieve Meeting):
```powershell
cd ai-service
.\venv\Scripts\python.exe -m app.e2e_database_test
```

---

## 🏗️ System Architecture


                    ┌─────────────────┐
                    │      User       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Frontend     │
                    │     React       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Backend     │
                    │     FastAPI     │
                    └──────┬───┬──────┘
                           │   │
                ┌──────────┘   └──────────┐
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │  AI Processing  │       │Aiven PostgreSQL │
       │ Whisper + LLM   │       │    Database     │
       └────────┬────────┘       └─────────────────┘
                │
                ▼
       ┌─────────────────┐
       │   Transcript    │
       │    Summary      │
       │  Action Items   │
       └─────────────────┘
