from __future__ import annotations

import os
from passlib.context import CryptContext


_crypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(plain_password: str) -> str:
    return _crypt_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return _crypt_context.verify(plain_password, password_hash)


