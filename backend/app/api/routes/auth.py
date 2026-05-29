"""
FusionGuardNet – Auth Router
POST /api/v1/auth/register  – create account, returns JWT
POST /api/v1/auth/login     – authenticate, returns JWT
GET  /api/v1/auth/me        – current user (Bearer token)
"""

import re
import logging
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator
from typing import Optional

from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, decode_access_token,
)
from app.core.config import settings
from app.database.sqlite_db import (
    create_user, get_user_by_username, get_user_by_email, user_exists,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/token", auto_error=False)

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username:  str
    email:     str
    password:  str
    full_name: Optional[str] = ""

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 30:
            raise ValueError("Username must be at most 30 characters")
        if not re.match(r"^[a-zA-Z0-9_\-]+$", v):
            raise ValueError("Username may only contain letters, numbers, _ and -")
        return v.lower()

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_RE.match(v):
            raise ValueError("Invalid email address")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         dict


class UserResponse(BaseModel):
    id:        int
    username:  str
    email:     str
    full_name: str
    role:      str


# ── Dependency ────────────────────────────────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication required")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token invalid or expired")
    user = get_user_by_username(payload.get("sub", ""))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")
    return user


def _user_dict(user: dict) -> dict:
    return {
        "id":        user["id"],
        "username":  user["username"],
        "email":     user["email"],
        "full_name": user.get("full_name", ""),
        "role":      user.get("role", "analyst"),
    }


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest):
    exists = user_exists(req.username, req.email)
    if exists["username_taken"]:
        raise HTTPException(status_code=400, detail="Username already taken")
    if exists["email_taken"]:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(
        username=req.username,
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name or req.username,
    )
    if not user:
        raise HTTPException(status_code=400, detail="Could not create account – please try again")

    token = create_access_token(
        {"sub": user["username"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info("New user registered: %s", user["username"])
    return {"access_token": token, "token_type": "bearer", "user": _user_dict(user)}


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    user = get_user_by_username(req.username.strip().lower())
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")
    token = create_access_token(
        {"sub": user["username"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info("User logged in: %s", user["username"])
    return {"access_token": token, "token_type": "bearer", "user": _user_dict(user)}


# OAuth2 form-based endpoint (used by Swagger UI "Authorize" button)
@router.post("/login/token", include_in_schema=False)
async def login_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": create_access_token({"sub": user["username"]}), "token_type": "bearer"}


# ── Me ────────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return _user_dict(current_user)
