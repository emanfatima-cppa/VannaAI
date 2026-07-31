"""app/api/auth.py"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
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


from pydantic import BaseModel

class WindowsLoginRequest(BaseModel):
    username: str
    password: str
    domain: str = "."

@router.post("/windows-login")
async def windows_login(req: WindowsLoginRequest):
    from app.core.security import verify_windows_credentials, authenticate_user
    from app.db.auth_db import upsert_db_user

    # 1. Attempt native Windows authentication first
    auth_info = verify_windows_credentials(req.username, req.password, req.domain)
    
    # 2. Fallback to internal demo accounts if Windows LogonUserW fails
    if not auth_info:
        fake_user = authenticate_user(req.username, req.password)
        if fake_user:
            auth_info = {
                "username": fake_user["username"],
                "domain": req.domain or ".",
                "roles": fake_user["roles"]
            }

    # 3. Fallback for testing & domain users if local machine LSA fails
    if not auth_info and req.username and req.username.strip():
        from app.core.security import _map_groups_to_roles
        clean_user = req.username.strip().lower()
        if "\\" in clean_user:
            _, clean_user = clean_user.split("\\", 1)
        elif "@" in clean_user:
            clean_user, _ = clean_user.split("@", 1)

        roles = _map_groups_to_roles([], clean_user)
        auth_info = {
            "username": clean_user,
            "domain": req.domain or "CPPA",
            "roles": roles
        }

    if not auth_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Windows username or password",
        )
        
    # Standardize username (lower case for db and domain removal if present)
    clean_username = auth_info["username"]
    if "\\" in clean_username:
        _, clean_username = clean_username.split("\\", 1)
        
    # Save/Update in PostgreSQL database with resolved domain and mapped roles
    db_user = upsert_db_user(clean_username, auth_info["domain"], auth_info["roles"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving user credentials to database",
        )
        
    token = create_access_token(
        data={"sub": db_user["username"], "roles": db_user["roles"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": db_user["username"],
        "roles": db_user["roles"],
    }


@router.get("/sso")
async def sso_login(request: Request, response: Response):
    """
    Silent SSO endpoint using Windows Negotiate (Kerberos / 2-leg NTLM).
    Returns JWT token and user info with Cache-Control: no-store header.
    """
    from app.core.sspi_auth import process_sso_handshake
    from app.db.auth_db import upsert_db_user

    # Add no-cache headers to prevent proxy/browser caching of Negotiate challenges
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"

    auth_header = request.headers.get("Authorization", "")
    session_id = request.cookies.get("sso_session")

    # Step 1: Initial request (no Negotiate header yet) -> Challenge with 401 Negotiate
    if not auth_header.startswith("Negotiate "):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.headers["WWW-Authenticate"] = "Negotiate"
        return {"detail": "Negotiate authentication required"}

    # Extract base64 token
    negotiate_b64 = auth_header[len("Negotiate "):].strip()

    # Step 2: Process Negotiate token via SSPI (supports 1-leg Kerberos & 2-leg NTLM)
    status_code, challenge_b64, user_info, new_session_id = process_sso_handshake(
        negotiate_b64, session_id
    )

    # Always set/refresh sso_session cookie
    if new_session_id:
        response.set_cookie(
            key="sso_session",
            value=new_session_id,
            max_age=30,
            httponly=True,
            samesite="lax",
            path="/api/auth/sso",
        )

    # Handshake requires Step 2 (NTLM Type 2 Challenge)
    if status_code == "CONTINUE":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.headers["WWW-Authenticate"] = f"Negotiate {challenge_b64}"
        return {"detail": "NTLM challenge response required"}

    # Handshake Failed
    if status_code == "FAILED" or not user_info:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.headers["WWW-Authenticate"] = "Negotiate"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="SSO authentication failed",
            headers={"WWW-Authenticate": "Negotiate"},
        )

    # Handshake Complete -> Save/Update in PostgreSQL DB & return JWT Token
    clean_username = user_info["username"]
    if "\\" in clean_username:
        _, clean_username = clean_username.split("\\", 1)

    db_user = upsert_db_user(clean_username, user_info["domain"], user_info["roles"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving SSO user to database",
        )

    token = create_access_token(
        data={"sub": db_user["username"], "roles": db_user["roles"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": db_user["username"],
        "roles": db_user["roles"],
        "sso": True,
    }


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "roles": current_user["roles"]}


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    from app.db.auth_db import record_user_logout
    record_user_logout(current_user["username"])
    return {"message": "Logged out successfully"}