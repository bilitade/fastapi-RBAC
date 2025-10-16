
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException, status
import hashlib

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    return _create_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), token_type="access")


def create_refresh_token(data: dict):
    return _create_token(data, timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES), token_type="refresh")


def _create_token(data: dict, expires_delta: timedelta, token_type: str = "access"):
    to_encode = data.copy()
    # Ensure 'sub' is string per JWT claim expectations
    sub = to_encode.get("sub")
    if sub is not None and not isinstance(sub, str):
        to_encode["sub"] = str(sub)

    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    from jose import JWTError, jwt
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # ensure token type is access
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def verify_refresh_token(token: str):
    from jose import JWTError, jwt
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """Return a SHA256 hex digest for the token string for DB storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
