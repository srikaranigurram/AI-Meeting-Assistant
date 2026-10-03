# DevOps, Testing, Deployment & Monitoring Guide
**Project:** AI-Meeting-Assistant  
**Role:** Person 4 — DevOps + Testing + Deployment + Monitoring + Documentation  
**Engineer:** Vishal (GitHub: `vishaljatoth10`, Email: `vishaljatoth10@gmail.com`)  

---

## 📑 Table of Contents
1. [DevOps Architecture](#-devops-architecture)
2. [Git Workflow & Branching Strategy](#-git-workflow--branching-strategy)
3. [Environment Variables & Security](#-environment-variables--security)
4. [Docker & Containerization](#-docker--containerization)
5. [Docker Compose Architecture](#-docker-compose-architecture)
6. [Automated Testing Suite (pytest)](#-automated-testing-suite-pytest)
7. [Jenkins CI/CD Pipeline](#-jenkins-cicd-pipeline)
8. [Monitoring, Health Checks & Logging](#-monitoring-health-checks--logging)
9. [Deployment Guide](#-deployment-guide)

---

## 🏗️ DevOps Architecture

```
                                 [ Developer / Git ]
                                         │
                                         ▼
                            [ GitHub Repository ]
                      (main, develop, feature/* branches)
                                         │
                                         ▼ Webhook / Poll
                            [ Jenkins CI/CD Pipeline ]
       ┌─────────────────────────────────┼─────────────────────────────────┐
       ▼                                 ▼                                 ▼
1. Checkout & Deps              2. Run Pytest Suite               3. Docker Build
   (python3 venv)                  (32 Tests Pass)                   (python:3.11-slim)
                                         │
                                         ▼
                            4. Container Deployment
                                         │
                                         ▼
                        ┌─────────────────────────────────┐
                        │         Docker Compose          │
                        │                                 │
                        │   ┌─────────────────────────┐   │
                        │   │  FastAPI Backend (:8000)│   │
                        │   │  - Health Check /health │   │
                        │   │  - Auth & Meeting APIs  │   │
                        │   │  - Python Logging       │   │
                        │   └───────────┬─────────────┘   │
                        │               │                 │
                        │               ▼                 │
                        │   ┌─────────────────────────┐   │
                        │   │ SQLite (Default) /      │   │
                        │   │ PostgreSQL (Profile)    │   │
                        │   └─────────────────────────┘   │
                        └────────────────┼────────────────┘
                                         │
                                         ▼
                               [ External AI Services ]
                                 - Google Gemini API
                                 - Faster-Whisper
```

---

## 🌿 Git Workflow & Branching Strategy

The repository follows a GitFlow-inspired branching strategy to support multi-person team development without collisions:

| Branch Name | Purpose | Assigned Responsibility |
|:---|:---|:---|
| `main` | Production-ready stable release code | All Team |
| `develop` | Integration branch for ongoing development | All Team |
| `feature/devops` | DevOps configuration, tests, Docker, Jenkins, monitoring | **Person 4 (Vishal)** |
| `feature/backend` | Backend APIs, models, routing | Person 2 |
| `feature/frontend` | Web interface / React frontend | Person 1 |
| `feature/AI` | Whisper transcription and Gemini LLM prompts | Person 3 |
| `backend-devops` | Historical Person 2 backend branch *(preserved)* | Person 2 |

### Git Identity for Person 4
All Person 4 commits are authored with:
```bash
git config --local user.name "vishaljatoth10"
git config --local user.email "vishaljatoth10@gmail.com"
```

---

## 🔒 Environment Variables & Security

Sensitive credentials must **never** be checked into version control.

### Protected Secrets Policy
The repository `.gitignore` strictly protects:
- `.env` (environment variables and secret keys)
- `.venv/` (Python virtual environments)
- `database.db` and `test*.db` (SQLite databases)
- `uploads/` (Audio files)
- `__pycache__/` and `*.pyc` (Python bytecode)
- `.pytest_cache/`, `.coverage`, `htmlcov/` (Testing artifacts)

### Configuration Template (`.env.example`)
To configure a local environment, copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

| Variable | Description | Example / Default |
|:---|:---|:---|
| `JWT_SECRET_KEY` | Secret key used to sign and verify JWT authentication tokens | `your_secure_random_key` |
| `GEMINI_API_KEY` | Google Gemini API key for meeting summaries and action items | `AIzaSy...` |
| `DATABASE_URL` | SQLAlchemy database connection string | `sqlite:///./database.db` |
| `PORT` | FastAPI server listening port | `8000` |

---

## 🐳 Docker & Containerization

The backend application is configured for containerization using `python:3.11-slim`, which provides a suitable runtime for `faster-whisper` and `ctranslate2` while keeping the image footprint minimal.

### Dockerfile Highlights
- **Base Image:** `python:3.11-slim`
- **System Dependencies:** `ffmpeg` (audio decoding) and `curl` (container health checks)
- **Security:** Secrets and local virtual environments are excluded via `.dockerignore`
- **Healthcheck:** Evaluates `GET /health` every 30 seconds
- **Port:** Exposes port `8000`
- **Server:** Runs FastAPI using `uvicorn main:app --host 0.0.0.0 --port 8000`

### Building the Docker Image
```bash
# Build from project root
docker build -t ai-meeting-assistant-backend:latest .

# Alternatively, using backend/Dockerfile:
docker build -f backend/Dockerfile -t ai-meeting-assistant-backend:latest .
```

### Running the Docker Container Standalone
```bash
docker run -d \
  --name ai_meeting_backend \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/uploads:/app/uploads" \
  -v "$(pwd)/database.db:/app/database.db" \
  ai-meeting-assistant-backend:latest
```

---

## 🐙 Docker Compose Architecture

The `docker-compose.yml` file coordinates services according to the project architecture:

### 1. Default Mode (SQLite)
Preserves Person 2's SQLite configuration with persistent file volume mounts:
```bash
docker compose up -d --build
```

### 2. PostgreSQL Mode (Optional Profile)
To run the backend with an enterprise PostgreSQL container:
```bash
docker compose --profile postgres up -d --build
```

### 3. Frontend Container Integration (Future Ready)
When the frontend team delivers React/Vite source code in `./frontend`, simply uncomment the `frontend` service definition in `docker-compose.yml`.

---

## 🧪 Automated Testing Suite (pytest)

Automated testing is implemented using `pytest` and `fastapi.testclient.TestClient`. Tests run in complete isolation:
- They **do not** call the external Google Gemini API (mocked via fixtures).
- They **do not** require audio model downloads (mocked via fixtures).
- They **do not** modify `database.db` (isolated temporary SQLite database used).
- They **do not** leak or require real secrets.

### Test Categories & Coverage

| Test File | Category | Test Cases Covered |
|:---|:---|:---|
| `tests/test_unit.py` | Unit Tests | Bcrypt password hashing & verification, JWT encoding/decoding, ORM model instantiation |
| `tests/test_api_and_health.py` | API & Health Tests | Root endpoint `GET /`, Health check `GET /health`, Request validation (missing payload fields) |
| `tests/test_auth.py` | Authentication Tests | User registration, duplicate registration conflict (400), valid login, invalid credentials (401), `/auth/me` with valid JWT, expired JWT rejection, unauthorized requests |
| `tests/test_meetings.py` | CRUD & API Tests | Meeting creation, meeting listing, user meeting isolation, fetch meeting by ID, 404 for missing meetings, meeting deletion |
| `tests/test_integration.py` | Integration Tests | Mocked AI summary generation (`/summary/`), mocked action item extraction (`/action-items/`), audio file upload workflow (`/audio/upload`), end-to-end full meeting lifecycle |

### Running the Tests Locally
```bash
# Activate virtual environment
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux/macOS

# Run all tests with verbose output
pytest -v

# Run with coverage report
pytest -v --cov=. --cov-report=term-missing
```

### Verification Result
```
32 tests passed (100% success rate)
- Unit Tests: 4 Passed
- API & Health Tests: 5 Passed
- Authentication Tests: 9 Passed
- Meeting CRUD Tests: 8 Passed
- Integration & AI Tests: 6 Passed
Total: 32 Passed (100% Success Rate)
```

---

## 🔄 Jenkins CI/CD Pipeline

The `Jenkinsfile` defines a Declarative Pipeline that automates the integration and deployment workflow across 6 distinct stages:

```
GitHub Repository
       ↓
Jenkins Trigger
       ↓
[Stage 1: Checkout] ──────────► Pull latest code from Git
       ↓
[Stage 2: Install Deps] ──────► Create .ci_venv, install requirements-dev.txt
       ↓
[Stage 3: Run Tests] ─────────► pytest with JUnit XML report generation
       ↓
[Stage 4: Build] ─────────────► Python syntax & module compilation checks
       ↓
[Stage 5: Docker Build] ──────► Build tagged Docker image (${IMAGE_NAME}:${BUILD_NUMBER})
       ↓
[Stage 6: Deploy] ────────────► Deploy container locally/staging and verify /health
```

### Secret Management in Jenkins
Secrets are injected securely at runtime via the Jenkins Credential Store:
```groovy
environment {
    JWT_SECRET_KEY = credentials('JWT_SECRET_KEY')
    GEMINI_API_KEY = credentials('GEMINI_API_KEY')
}
```
**No passwords, API keys, or tokens are hardcoded in the pipeline.**

---

## 📊 Monitoring, Health Checks & Logging

### 1. Health Check Endpoint
- **URL:** `GET /health`
- **Response Format:**
```json
{
  "status": "healthy",
  "message": "AI Meeting Assistant backend is running"
}
```
- **CLI Check:**
```bash
curl -f http://localhost:8000/health
```

### 2. Application Logging
The application uses Python's standard `logging` library configured with structured timestamps and log levels in `main.py`:
```
2026-09-30 20:48:39,525 [INFO] ai_meeting_assistant: AI Meeting Assistant API initialized
2026-09-30 20:48:39,543 [INFO] ai_meeting_assistant: Health check endpoint accessed - status: healthy
```

### 3. Docker Container Status
Check running containers and health status:
```bash
# Check status and healthcheck condition
docker ps --filter "name=ai_meeting"

# Check Docker Compose status
docker compose ps

# Follow application logs in real-time
docker logs -f ai_meeting_backend
```

### 4. Jenkins Build Status
- Build results, execution timelines, and stage transitions are available in the Jenkins Web UI under the project dashboard.
- Test trends and passed/failed counts are tracked via the JUnit test report archive (`test-reports/junit.xml`).

---

## 🚀 Deployment Guide

### Quick Start (Local Production Simulation)
1. **Clone the repository:**
   ```bash
   git clone -b feature/devops https://github.com/srikaranigurram/AI-Meeting-Assistant.git
   cd AI-Meeting-Assistant
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Add your JWT_SECRET_KEY and GEMINI_API_KEY to .env
   ```

3. **Start containers with Docker Compose:**
   ```bash
   docker compose up -d --build
   ```

4. **Verify container health:**
   ```bash
   curl http://localhost:8000/health
   ```

5. **Stop containers:**
   ```bash
   docker compose down
   ```
