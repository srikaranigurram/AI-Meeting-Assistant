import logging
from fastapi import FastAPI

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ai_meeting_assistant")

from database import engine, Base
from models.user import User
from models.meeting import Meeting

from routers.audio import router as audio_router
from routers.summary import router as summary_router
from routers.action_items import router as action_items_router
from routers.auth import router as auth_router
from routers.meetings import router as meetings_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Meeting Assistant API")
logger.info("AI Meeting Assistant API initialized")

# Include all routers
app.include_router(audio_router)
app.include_router(summary_router)
app.include_router(action_items_router)
app.include_router(auth_router)
app.include_router(meetings_router)


@app.get("/")
def root():
    return {
        "message": "AI Meeting Assistant API is running!"
    }


@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed - status: healthy")
    return {
        "status": "healthy",
        "message": "AI Meeting Assistant backend is running"
    }