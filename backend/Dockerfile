# ==============================================================================
# Dockerfile for AI-Meeting-Assistant Backend
# Base image: Python 3.11-slim
# Build context: repository root (.)
# Command: docker build -f backend/Dockerfile -t ai-meeting-assistant-backend .
# ==============================================================================

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies (ffmpeg for audio transcription, curl for container healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY database.py main.py ./
COPY models/ ./models/
COPY routers/ ./routers/
COPY services/ ./services/

# Ensure uploads directory exists
RUN mkdir -p uploads

# Expose FastAPI application port
EXPOSE 8000

# Container healthcheck using existing /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
