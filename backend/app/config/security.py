from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException
from jose import JWTError, jwt

from app.config.settings import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _require_jwt_secret() -> str:
    secret = settings.JWT_SECRET.strip()
    if not secret:
        raise HTTPException(
            status_code=503,
            detail="Server misconfigured: JWT_SECRET is missing. Add it in Vercel Environment Variables.",
        )
    return secret


def create_access_token(subject: str) -> str:
    secret = _require_jwt_secret()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": int(expire.timestamp())}
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    secret = settings.JWT_SECRET.strip()
    if not secret:
        return None
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
        subject = payload.get("sub")
        return subject if isinstance(subject, str) else None
    except JWTError:
        return None
