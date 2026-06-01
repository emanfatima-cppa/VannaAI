"""app/api/auth.py"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.core.security import authenticate_user, create_access_token, get_current_user
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(
        data={"sub": user["username"], "roles": user["roles"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user["username"],
        "roles": user["roles"],
    }


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "roles": current_user["roles"]}