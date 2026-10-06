import os
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# Load environment configuration
load_dotenv()
if not os.getenv("DATABASE_URL"):
    fallback_env = os.path.join(os.path.dirname(__file__), "ai-service", ".env")
    if os.path.exists(fallback_env):
        load_dotenv(fallback_env)

from database import engine, Base
from models.user import User
from models.meeting import Meeting, KeyPoint, Decision, ActionItem

from routers.audio import router as audio_router
from routers.summary import router as summary_router
from routers.action_items import router as action_items_router
from routers.auth import router as auth_router
from routers.meetings import router as meetings_router

# Create database tables in Neon PostgreSQL / SQLite
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[WARNING] Database initialization note: {e}")

app = FastAPI(
    title="AI Meeting Assistant API",
    description="Backend API powering transcription, AI processing, and meeting intelligence",
    version="1.0.0"
)

# Configure CORS to allow React frontend (default port 5173 and common dev ports)
cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
)
allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 Router prefix group to match frontend VITE_API_URL expectations
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(audio_router)
api_v1_router.include_router(summary_router)
api_v1_router.include_router(action_items_router)
api_v1_router.include_router(meetings_router)

@api_v1_router.get("/health")
def api_v1_health():
    return {
        "status": "healthy",
        "api_version": "v1",
        "message": "AI Meeting Assistant backend is running"
    }

# Mount both /api/v1 and root prefixes for complete client compatibility
app.include_router(api_v1_router)

app.include_router(auth_router)
app.include_router(audio_router)
app.include_router(summary_router)
app.include_router(action_items_router)
app.include_router(meetings_router)


@app.get("/")
def root():
    return {
        "message": "AI Meeting Assistant API is running!",
        "docs_url": "/docs",
        "api_v1_prefix": "/api/v1"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "AI Meeting Assistant backend is running"
    }