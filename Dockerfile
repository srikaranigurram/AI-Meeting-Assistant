```dockerfile
# Dockerfile for AI Meeting Assistant Backend

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies for audio processing and health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application files
COPY database.py main.py ./
COPY models/ ./models/
COPY routers/ ./routers/
COPY services/ ./services/

# Create persistent-data directories and a non-root application user
RUN useradd --create-home --shell /usr/sbin/nologin appuser && \
    mkdir -p /app/uploads && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Container health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
