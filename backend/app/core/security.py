"""app/core/security.py – JWT creation & verification."""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── Fake user store (replace with a real DB table) ───────────────────────────
FAKE_USERS = {
    "hr_admin": {
        "username": "hr_admin",
        "hashed_password": pwd_context.hash("hr_admin123"),
        "roles": ["hr_admin", "hr_viewer"],
    },
    "hr_viewer": {
        "username": "hr_viewer",
        "hashed_password": pwd_context.hash("hr_viewer123"),
        "roles": ["hr_viewer"],
    },
    "it_admin": {
        "username": "it_admin",
        "hashed_password": pwd_context.hash("it_admin123"),
        "roles": ["it_admin", "it_viewer"],
    },
    "it_viewer": {
        "username": "it_viewer",
        "hashed_password": pwd_context.hash("it_viewer123"),
        "roles": ["it_viewer"],
    },
}


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = FAKE_USERS.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = FAKE_USERS.get(username)
    if user is None:
        raise credentials_exception
    return user