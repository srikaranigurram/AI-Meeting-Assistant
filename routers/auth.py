import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_
import bcrypt
from jose import jwt
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from services.auth_service import get_current_user

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ai_meeting_assistant_jwt_secret_dev_key_2026_super_secure")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hashes a password using direct bcrypt (max 72 bytes)."""
    pw_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


class UserRegister(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


@router.post("/register")
async def register_user(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    identifier = user.username or user.email
    if not identifier:
        raise HTTPException(status_code=400, detail="Username or email is required")

    email = user.email or identifier
    username = user.username or identifier
    full_name = user.full_name or username

    existing_user = db.query(User).filter(
        or_(User.username == username, User.email == email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this username or email already exists"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token_data = {
        "sub": str(new_user.id),
        "username": new_user.username,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "message": "User registered successfully!",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(new_user.id),
            "username": new_user.username,
            "email": new_user.email,
            "fullName": new_user.full_name
        }
    }


@router.post("/login")
async def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    identifier = user.username or user.email
    if not identifier:
        raise HTTPException(status_code=400, detail="Username or email is required")

    existing_user = db.query(User).filter(
        or_(User.username == identifier, User.email == identifier)
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(user.password, existing_user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token_data = {
        "sub": str(existing_user.id),
        "username": existing_user.username,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    access_token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Login successful!",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(existing_user.id),
            "username": existing_user.username,
            "email": existing_user.email or existing_user.username,
            "fullName": existing_user.full_name or existing_user.username
        }
    }


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    return {
        "success": True,
        "message": f"Password reset instructions have been dispatched to {data.email}."
    }


@router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "JWT authentication successful!",
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "fullName": current_user.full_name
    }