from __future__ import annotations

from sqlalchemy import Column, Integer, String, UniqueConstraint

from app.db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)


