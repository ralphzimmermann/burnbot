from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.auth import User
from app.models.favorites import Favorite


class FavoriteEvent(BaseModel):
    id: str
    title: str = ""
    type: str = ""
    camp: str = ""
    campurl: str | None = None
    location: str = ""
    latitude: float | None = None
    longitude: float | None = None
    description: str = ""
    times: list[dict] = []


router = APIRouter(prefix="/favorites", tags=["favorites"])  # mounted at /favorites


def require_user(request: Request, db: Session) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.get("", response_model=List[FavoriteEvent])
def list_favorites(request: Request, db: Session = Depends(get_db)) -> List[FavoriteEvent]:
    user = require_user(request, db)
    favs = db.query(Favorite).filter(Favorite.user_id == user.id).order_by(Favorite.id.asc()).all()
    return [FavoriteEvent.model_validate_json(f.event_json) for f in favs]


@router.post("", response_model=FavoriteEvent)
def add_favorite(event: FavoriteEvent, request: Request, db: Session = Depends(get_db)) -> FavoriteEvent:
    user = require_user(request, db)
    existing = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.event_id == event.id).first()
    if existing:
        return event
    fav = Favorite(user_id=int(user.id), event_id=event.id, event_json=event.model_dump_json())
    db.add(fav)
    db.commit()
    return event


@router.delete("/{event_id}")
def remove_favorite(event_id: str, request: Request, db: Session = Depends(get_db)) -> dict:
    user = require_user(request, db)
    deleted = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.event_id == event_id).delete()
    db.commit()
    return {"deleted": deleted > 0}


