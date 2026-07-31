"""app/core/security.py – JWT creation & verification."""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import ctypes
from ctypes import wintypes
from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

import logging as _logging
_win_logger = _logging.getLogger(__name__)

def _get_token_groups(h_token) -> list[str]:
    """Helper to fetch group names (domain\\group) from a Windows token handle with universal SID fallback."""
    try:
        import ctypes
        from ctypes import wintypes

        class SID_AND_ATTRIBUTES(ctypes.Structure):
            _fields_ = [("Sid", ctypes.c_void_p), ("Attributes", wintypes.DWORD)]

        advapi32 = ctypes.windll.advapi32
        kernel32 = ctypes.windll.kernel32
        
        # Declare argument/return types for safety in 64-bit systems
        advapi32.GetTokenInformation.argtypes = [
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)
        ]
        advapi32.LookupAccountSidW.argtypes = [
            ctypes.c_wchar_p, ctypes.c_void_p, ctypes.c_wchar_p, ctypes.POINTER(wintypes.DWORD),
            ctypes.c_wchar_p, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD)
        ]
        advapi32.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_wchar_p)]

        # 2 represents TokenGroups
        dw_size = wintypes.DWORD(0)
        advapi32.GetTokenInformation(h_token, 2, None, 0, ctypes.byref(dw_size))
        if dw_size.value == 0:
            return []

        buffer = ctypes.create_string_buffer(dw_size.value)
        success = advapi32.GetTokenInformation(h_token, 2, buffer, dw_size, ctypes.byref(dw_size))
        if not success:
            return []

        # Get group count
        group_count = wintypes.DWORD.from_buffer(buffer, 0).value
        
        class DYNAMIC_TOKEN_GROUPS(ctypes.Structure):
            _fields_ = [("GroupCount", wintypes.DWORD), ("Groups", SID_AND_ATTRIBUTES * group_count)]

        token_groups = DYNAMIC_TOKEN_GROUPS.from_buffer(buffer)
        groups = []
        for i in range(group_count):
            sid = token_groups.Groups[i].Sid
            
            # 1. Convert SID to String first
            p_str = ctypes.c_wchar_p()
            sid_str = ""
            if advapi32.ConvertSidToStringSidW(sid, ctypes.byref(p_str)):
                sid_str = p_str.value or ""
                kernel32.LocalFree(p_str)

            # 2. Lookup Account SID name
            name = ctypes.create_unicode_buffer(256)
            domain = ctypes.create_unicode_buffer(256)
            n_size = wintypes.DWORD(256)
            d_size = wintypes.DWORD(256)
            sid_use = wintypes.DWORD()
            
            if advapi32.LookupAccountSidW(None, sid, name, ctypes.byref(n_size), domain, ctypes.byref(d_size), ctypes.byref(sid_use)):
                group_name = f"{domain.value}\\{name.value}" if domain.value else name.value
                groups.append(group_name)

            # 3. Universal Well-Known SID Fallbacks:
            # S-1-5-32-544 = BUILTIN\Administrators
            # *-512 = Domain Admins
            # *-519 = Enterprise Admins
            if sid_str == "S-1-5-32-544" or sid_str.endswith("-512") or sid_str.endswith("-519") or sid_str.endswith("-544"):
                if "BUILTIN\\Administrators" not in groups:
                    groups.append("BUILTIN\\Administrators")

        _win_logger.info(f"[WinAuth] Resolved groups for token: {groups}")
        return groups
    except Exception as e:
        _win_logger.error(f"[WinAuth] Error getting token groups: {e}")
        return []

# List of specific usernames explicitly allowed/assigned to be IT Admins.
# Specified admin users: eman.fatima, amna.malik, alina.javed
ALLOWED_IT_ADMIN_USERNAMES: list[str] = [
    "eman.fatima",
    "eman",
    "amna.malik",
    "alina.javed",
]

def _map_groups_to_roles(groups: list[str], username: str = "") -> list[str]:
    roles = []
    is_admin = False
    is_it = False
    is_hr = False
    
    clean_user = username.strip().lower()
    if "\\" in clean_user:
        _, clean_user = clean_user.split("\\", 1)

    allowed_admins = [u.strip().lower() for u in ALLOWED_IT_ADMIN_USERNAMES]
    
    # 1. Check if username is in explicit IT Admin list
    if clean_user in allowed_admins:
        is_admin = True
        is_it = True

    # 2. Check Windows Group memberships
    for group in groups:
        grp_lower = group.lower()
        if "admin" in grp_lower or "administrators" in grp_lower:
            is_admin = True
        if "it" in grp_lower:
            is_it = True
        if "hr" in grp_lower:
            is_hr = True
            
    if any("administrators" in g.lower() for g in groups):
        is_admin = True
        is_it = True

    if is_hr:
        if is_admin:
            roles.extend(["hr_admin", "hr_viewer"])
        else:
            roles.append("hr_viewer")
            
    if is_it or is_admin:
        if is_admin:
            roles.extend(["it_admin", "it_viewer"])
        else:
            roles.append("it_viewer")
            
    if not roles:
        roles.append("it_viewer")
        
    return list(dict.fromkeys(roles))

def verify_windows_credentials(username: str, password: str, domain: str = ".") -> Optional[dict]:
    """
    Verifies username and password against local Windows SAM and Active Directory domain accounts.
    Tries network, interactive, network-clear text, batch, and unlock logon types across domain fallbacks.
    Returns a dict with user credentials info on success, or None on failure.
    """
    import os
    LOGON32_LOGON_INTERACTIVE       = 2
    LOGON32_LOGON_NETWORK           = 3
    LOGON32_LOGON_BATCH             = 4
    LOGON32_LOGON_UNLOCK            = 7
    LOGON32_LOGON_NETWORK_CLEARTEXT = 8
    LOGON32_PROVIDER_DEFAULT        = 0

    if not username or not password:
        return None

    username = username.strip()
    if domain:
        domain = domain.strip()

    # Handle "DOMAIN\username" or "username@domain" formats
    if "\\" in username:
        parts = username.split("\\", 1)
        domain, username = parts[0].strip(), parts[1].strip()
    elif "@" in username:
        parts = username.split("@", 1)
        username, domain = parts[0].strip(), parts[1].strip()

    # Build domain resolution list
    domains_to_try = []
    
    # 1. None FIRST (lets Windows API auto-resolve domain/UPN/Kerberos ticket)
    domains_to_try.append(None)

    # 2. Machine's Environment DNS Domain (e.g. CPPA.GOV.PK)
    env_dns = os.environ.get("USERDNSDOMAIN")
    if env_dns and env_dns not in domains_to_try:
        domains_to_try.append(env_dns)

    # 3. Machine's Environment Short Domain (e.g. CPPA)
    env_domain = os.environ.get("USERDOMAIN")
    if env_domain and env_domain not in domains_to_try:
        domains_to_try.append(env_domain)

    # 4. User specified domain parameter if provided and not already included
    if domain and domain != "." and domain not in domains_to_try:
        domains_to_try.append(domain)

    # 5. Local SAM '.'
    if "." not in domains_to_try:
        domains_to_try.append(".")

    try:
        advapi32 = ctypes.windll.advapi32
        kernel32 = ctypes.windll.kernel32

        logon_types = [
            (LOGON32_LOGON_NETWORK,           "LOGON_NETWORK"),
            (LOGON32_LOGON_INTERACTIVE,       "LOGON_INTERACTIVE"),
            (LOGON32_LOGON_NETWORK_CLEARTEXT, "LOGON_NETWORK_CLEARTEXT"),
            (LOGON32_LOGON_BATCH,             "LOGON_BATCH"),
            (LOGON32_LOGON_UNLOCK,            "LOGON_UNLOCK"),
        ]

        for d in domains_to_try:
            _win_logger.info(f"[WinAuth] Attempting logon for user='{username}' domain='{d}'")
            
            for logon_type, logon_name in logon_types:
                token = wintypes.HANDLE()
                domain_param = ctypes.c_wchar_p(d) if d is not None else None
                success = advapi32.LogonUserW(
                    ctypes.c_wchar_p(username),
                    domain_param,
                    ctypes.c_wchar_p(password),
                    logon_type,
                    LOGON32_PROVIDER_DEFAULT,
                    ctypes.byref(token),
                )
                if success:
                    groups = _get_token_groups(token)
                    roles = _map_groups_to_roles(groups, username)
                    kernel32.CloseHandle(token)
                    resolved_domain = d or env_domain or "."
                    _win_logger.info(f"[WinAuth] SUCCESS with {logon_name} for user='{username}' domain='{resolved_domain}' roles={roles}")
                    return {
                        "username": username,
                        "domain": resolved_domain,
                        "groups": groups,
                        "roles": roles
                    }
                else:
                    err = kernel32.GetLastError()
                    _win_logger.warning(
                        f"[WinAuth] FAILED {logon_name} for user='{username}' domain='{d}' "
                        f"Windows error={err} (1326=wrong pwd/user, 1327=account restriction, 1330=expired, 2=user not found)"
                    )

    except Exception as e:
        _win_logger.error(f"[WinAuth] Exception calling LogonUserW: {e}")

    return None



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

    # Check FAKE_USERS first
    user = FAKE_USERS.get(username)
    if user is not None:
        return user

    # Otherwise, check PostgreSQL database
    from app.db.auth_db import get_db_user
    db_user = get_db_user(username)
    if db_user is None:
        raise credentials_exception
    return db_user