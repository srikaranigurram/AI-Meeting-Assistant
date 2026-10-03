from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os

# SQLite database connection (configurable via environment variable)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

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