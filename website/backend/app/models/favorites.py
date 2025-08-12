from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint, Index

from app.db import Base


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_favorites_user_event"),
        Index("ix_favorites_user_id", "user_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(String(64), nullable=False)
    event_json = Column(Text, nullable=False)


