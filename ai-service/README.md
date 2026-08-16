# AI Service (Module 3: AI + Database)

This directory contains the **AI + Database** module for the **AI Meeting Assistant** project.

## Module Scope & Future Responsibilities
1. **Speech-to-Text**: Running Whisper locally for offline transcription of meeting audio.
2. **AI Processing**: Parsing, structuring, and analyzing meeting transcripts.
3. **Summarization**: Generating concise and informative meeting summaries.
4. **Action-Item Extraction**: Extracting key tasks, assignees, and action items from transcripts.
5. **Database Integration**: Storing meeting records, summaries, and action items using PostgreSQL.
6. **Backend Integration**: Connecting with the central team backend to expose service endpoints.
7. **Containerization & Testing**: Dockerizing the service and implementing automated test suites for continuous integration.

## Getting Started

### 1. Create and Activate Virtual Environment
```bash
# Navigate to the ai-service folder
cd ai-service

# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate on Windows (Command Prompt)
.\venv\Scripts\activate.bat

# Activate on Linux/macOS
source venv/bin/activate
```

### 2. Verify Execution
```bash
python -m app.main
```
