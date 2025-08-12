from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.auth import User
from app.security import hash_password, verify_password


class AuthPayload(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str


router = APIRouter(prefix="", tags=["auth"])  # mount at /auth/* via include_router


@router.post("/auth/register", response_model=UserResponse, status_code=201)
def register(payload: AuthPayload, request: Request, db: Session = Depends(get_db)) -> UserResponse:
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = int(user.id)
    return UserResponse(id=int(user.id), username=user.username)


@router.post("/auth/login", response_model=UserResponse)
def login(payload: AuthPayload, request: Request, db: Session = Depends(get_db)) -> UserResponse:
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    request.session["user_id"] = int(user.id)
    return UserResponse(id=int(user.id), username=user.username)


@router.post("/auth/logout")
def logout(request: Request) -> dict:
    # Clear any session keys safely
    for key in list(request.session.keys()):
        request.session.pop(key, None)
    # Explicitly reset session data
    request.session.clear()
    return {"ok": True}


@router.get("/auth/me", response_model=UserResponse)
def me(request: Request, db: Session = Depends(get_db)) -> UserResponse:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return UserResponse(id=int(user.id), username=user.username)


