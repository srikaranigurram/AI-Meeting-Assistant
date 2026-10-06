import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables (checks root .env, then falls back to ai-service/.env)
load_dotenv()
if not os.getenv("DATABASE_URL"):
    fallback_env = os.path.join(os.path.dirname(__file__), "ai-service", ".env")
    if os.path.exists(fallback_env):
        load_dotenv(fallback_env)

raw_db_url = os.getenv("DATABASE_URL")

def build_engine(db_url: str):
    """
    Constructs a resilient SQLAlchemy engine supporting Neon Cloud PostgreSQL
    and graceful fallback to SQLite for local development.
    """
    if not db_url or not db_url.strip():
        # Fallback to local SQLite if no DATABASE_URL is configured
        sqlite_url = "sqlite:///./database.db"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})

    url = db_url.strip()

    # Standardize postgres:// to postgresql://
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    # Resolve PostgreSQL dialect based on available drivers
    if url.startswith("postgresql://"):
        try:
            import psycopg
            engine_url = "postgresql+psycopg://" + url[len("postgresql://"):]
        except ImportError:
            engine_url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    else:
        engine_url = url

    if "sqlite" in engine_url:
        return create_engine(engine_url, connect_args={"check_same_thread": False})
    else:
        return create_engine(engine_url, pool_pre_ping=True)

engine = build_engine(raw_db_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()