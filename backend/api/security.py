"""Password hashing and short-lived bearer token helpers."""

import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()
JWT_SECRET = os.getenv("JWT_SECRET", "development-only-change-this-secret-before-deploying")
if os.getenv("APP_ENV", "development").lower() == "production" and "JWT_SECRET" not in os.environ:
    raise RuntimeError("JWT_SECRET must be configured when APP_ENV=production.")
JWT_ALGORITHM = "HS256"
TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "60"))


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expires}, JWT_SECRET, algorithm=JWT_ALGORITHM)
