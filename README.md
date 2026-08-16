# AI-Meeting-Assistant
AI-powered meeting assistant that converts meeting audio into transcripts, summaries, and actionable tasks.

## 📌 About the Project

AI-Meeting-Assistant is an AI-powered web application designed to simplify meeting management.

The application allows users to upload or record meeting audio. The system converts the audio into text, generates an AI-powered summary, identifies important discussion points, and extracts actionable tasks from the meeting.

All processed meetings are stored securely so users can access their previous meetings, transcripts, summaries, and action items whenever needed.

The project also demonstrates modern DevOps practices including Git/GitHub, Docker, Jenkins, automated testing, and CI/CD.

## ✨ Features

- 🎙️ Record meeting audio
- 📁 Upload recorded meeting audio
- 📝 Automatic speech-to-text transcription
- 🤖 AI-generated meeting summaries
- ✅ Automatic action-item extraction
- 👤 Identify assigned tasks
- 📅 Track deadlines
- 📚 Store meeting history
- 🔍 Search previous meetings
- 🔐 User authentication
- 🐳 Docker containerization
- 🔄 Jenkins CI/CD pipeline

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
       │  AI Processing  │       │   PostgreSQL    │
       │ Whisper + LLM   │       │    Database     │
       └────────┬────────┘       └─────────────────┘
                │
                ▼
       ┌─────────────────┐
       │   Transcript    │
       │    Summary      │
       │  Action Items   │
       └─────────────────┘
