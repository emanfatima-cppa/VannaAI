"""app/core/sspi_auth.py
Windows SSPI-based Negotiate/Kerberos/NTLM authentication helper.
Supports both single-leg (Kerberos) and 2-leg (NTLM) Negotiate handshakes.
Uses native Windows secur32.dll via ctypes (zero external Python package dependencies).
Unifies group & role resolution via QuerySecurityContextToken + _get_token_groups.
"""

import base64
import ctypes
from ctypes import wintypes
import logging
import os
import time
import uuid
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Win32 & SSPI Constants & Structures
secur32 = ctypes.windll.secur32
kernel32 = ctypes.windll.kernel32


class SecHandle(ctypes.Structure):
    _fields_ = [("dwLower", ctypes.c_size_t), ("dwUpper", ctypes.c_size_t)]


class SecBuffer(ctypes.Structure):
    _fields_ = [
        ("cbBuffer", wintypes.ULONG),
        ("BufferType", wintypes.ULONG),
        ("pvBuffer", ctypes.c_void_p),
    ]


class SecBufferDesc(ctypes.Structure):
    _fields_ = [
        ("ulVersion", wintypes.ULONG),
        ("cBuffers", wintypes.ULONG),
        ("pBuffers", ctypes.POINTER(SecBuffer)),
    ]


class SecPkgContext_NamesW(ctypes.Structure):
    _fields_ = [("sUserName", ctypes.c_wchar_p)]


SECBUFFER_TOKEN = 2
SECBUFFER_VERSION = 0
SEC_E_OK = 0
SEC_I_CONTINUE_NEEDED = 0x00090112
SECPKG_CRED_INBOUND = 1
SECPKG_ATTR_NAMES = 1

# Prototypes for secur32
secur32.AcquireCredentialsHandleW.argtypes = [
    ctypes.c_wchar_p,
    ctypes.c_wchar_p,
    wintypes.ULONG,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.POINTER(SecHandle),
    ctypes.POINTER(ctypes.c_longlong),
]
secur32.AcquireCredentialsHandleW.restype = wintypes.LONG

secur32.AcceptSecurityContext.argtypes = [
    ctypes.POINTER(SecHandle),
    ctypes.POINTER(SecHandle),
    ctypes.POINTER(SecBufferDesc),
    wintypes.ULONG,
    wintypes.ULONG,
    ctypes.POINTER(SecHandle),
    ctypes.POINTER(SecBufferDesc),
    ctypes.POINTER(wintypes.ULONG),
    ctypes.POINTER(ctypes.c_longlong),
]
secur32.AcceptSecurityContext.restype = wintypes.LONG

secur32.QuerySecurityContextToken.argtypes = [
    ctypes.POINTER(SecHandle),
    ctypes.POINTER(wintypes.HANDLE),
]
secur32.QuerySecurityContextToken.restype = wintypes.LONG

secur32.QueryContextAttributesW.argtypes = [
    ctypes.POINTER(SecHandle),
    wintypes.ULONG,
    ctypes.c_void_p,
]
secur32.QueryContextAttributesW.restype = wintypes.LONG

secur32.DeleteSecurityContext.argtypes = [ctypes.POINTER(SecHandle)]
secur32.DeleteSecurityContext.restype = wintypes.LONG

secur32.FreeCredentialsHandle.argtypes = [ctypes.POINTER(SecHandle)]
secur32.FreeCredentialsHandle.restype = wintypes.LONG


# In-memory session store for multi-leg NTLM handshakes
# Format: { session_id: { "cred": SecHandle, "ctx": SecHandle, "created_at": float } }
SSO_SESSIONS: dict[str, dict] = {}
SESSION_TTL_SECONDS = 30  # Max seconds allowed to complete 2-leg NTLM handshake


def _cleanup_expired_sso_sessions():
    """Remove expired NTLM handshake sessions to avoid handle memory leaks."""
    now = time.time()
    expired_ids = []
    for sid, sess in list(SSO_SESSIONS.items()):
        if now - sess["created_at"] > SESSION_TTL_SECONDS:
            expired_ids.append(sid)
            try:
                if sess.get("ctx"):
                    secur32.DeleteSecurityContext(ctypes.byref(sess["ctx"]))
                if sess.get("cred"):
                    secur32.FreeCredentialsHandle(ctypes.byref(sess["cred"]))
            except Exception as e:
                logger.warning(f"[SSO] Cleanup error for session {sid}: {e}")
    for sid in expired_ids:
        SSO_SESSIONS.pop(sid, None)


def process_sso_handshake(
    negotiate_b64: str, session_id: Optional[str] = None
) -> Tuple[str, Optional[str], Optional[dict], str]:
    """
    Processes a Negotiate (Kerberos / NTLM) token step using native Windows SSPI.

    Returns a tuple:
        (status, challenge_b64, user_info, new_session_id)

    Possible status values:
        - "COMPLETE": Handshake succeeded. user_info contains username, domain, groups, roles.
        - "CONTINUE": Handshake requires step 2 (NTLM). challenge_b64 contains Type 2 NTLM challenge.
        - "FAILED": Handshake failed.
    """
    _cleanup_expired_sso_sessions()

    if not session_id or session_id not in SSO_SESSIONS:
        session_id = str(uuid.uuid4())
        sess_data = None
    else:
        sess_data = SSO_SESSIONS.get(session_id)

    try:
        in_bytes = base64.b64decode(negotiate_b64)
    except Exception as e:
        logger.error(f"[SSO] Invalid base64 Negotiate token: {e}")
        return "FAILED", None, None, session_id

    # Create input buffer
    in_buf = SecBuffer(
        cbBuffer=len(in_bytes),
        BufferType=SECBUFFER_TOKEN,
        pvBuffer=ctypes.cast(in_bytes, ctypes.c_void_p),
    )
    in_desc = SecBufferDesc(
        ulVersion=SECBUFFER_VERSION, cBuffers=1, pBuffers=ctypes.pointer(in_buf)
    )

    # Output buffer setup (12KB for max Kerberos/NTLM ticket payload)
    out_max = 12288
    out_raw = (ctypes.c_ubyte * out_max)()
    out_buf = SecBuffer(
        cbBuffer=out_max,
        BufferType=SECBUFFER_TOKEN,
        pvBuffer=ctypes.cast(out_raw, ctypes.c_void_p),
    )
    out_desc = SecBufferDesc(
        ulVersion=SECBUFFER_VERSION, cBuffers=1, pBuffers=ctypes.pointer(out_buf)
    )

    # Initialize SSPI credentials handle if starting new session
    if not sess_data:
        cred = SecHandle()
        pts = ctypes.c_longlong()
        st = secur32.AcquireCredentialsHandleW(
            None,
            "Negotiate",
            SECPKG_CRED_INBOUND,
            None,
            None,
            None,
            None,
            ctypes.byref(cred),
            ctypes.byref(pts),
        )
        if st != 0:
            logger.error(
                f"[SSO] AcquireCredentialsHandleW failed with status {hex(st & 0xFFFFFFFF)}"
            )
            return "FAILED", None, None, session_id
        ctx = None
    else:
        cred = sess_data["cred"]
        ctx = sess_data["ctx"]

    # Call AcceptSecurityContext
    new_ctx = SecHandle()
    ctx_ptr = ctypes.byref(ctx) if ctx else None
    out_context_attr = wintypes.ULONG()
    pts_out = ctypes.c_longlong()

    ret = secur32.AcceptSecurityContext(
        ctypes.byref(cred),
        ctx_ptr,
        ctypes.byref(in_desc),
        0,  # Context attributes
        0,  # Target Data Rep (SECURITY_NATIVE_DREP)
        ctypes.byref(new_ctx),
        ctypes.byref(out_desc),
        ctypes.byref(out_context_attr),
        ctypes.byref(pts_out),
    )

    unsigned_ret = ret & 0xFFFFFFFF

    # Case 1: More tokens needed (NTLM Type 2 Challenge ready for step 2)
    if unsigned_ret == SEC_I_CONTINUE_NEEDED:
        out_bytes = bytes(out_raw[: out_buf.cbBuffer]) if out_buf.cbBuffer > 0 else b""
        challenge_b64 = base64.b64encode(out_bytes).decode("ascii") if out_bytes else ""

        # Store session context for Step 2
        SSO_SESSIONS[session_id] = {
            "cred": cred,
            "ctx": new_ctx,
            "created_at": time.time(),
        }
        logger.info(
            f"[SSO] NTLM 2-leg handshake step 1 complete. Session '{session_id}' waiting for Type 3 response."
        )
        return "CONTINUE", challenge_b64, None, session_id

    # Case 2: Success / Complete (Kerberos 1-step or NTLM 2-step complete)
    elif unsigned_ret == SEC_E_OK:
        username = None
        # Extract authenticated username
        names = SecPkgContext_NamesW()
        if (
            secur32.QueryContextAttributesW(
                ctypes.byref(new_ctx), SECPKG_ATTR_NAMES, ctypes.byref(names)
            )
            == 0
        ):
            if names.sUserName:
                username = names.sUserName
                # Free memory allocated by QueryContextAttributesW
                kernel32.LocalFree(ctypes.c_void_p.from_buffer(names).value)

        # Extract Windows user impersonation token handle (h_token)
        h_token = wintypes.HANDLE()
        has_token = (
            secur32.QuerySecurityContextToken(
                ctypes.byref(new_ctx), ctypes.byref(h_token)
            )
            == 0
            and h_token.value
        )

        # Clean up SSPI context & credentials
        secur32.DeleteSecurityContext(ctypes.byref(new_ctx))
        secur32.FreeCredentialsHandle(ctypes.byref(cred))
        SSO_SESSIONS.pop(session_id, None)

        if not username:
            logger.error("[SSO] SSPI completed but username could not be queried.")
            if has_token and h_token.value:
                kernel32.CloseHandle(h_token)
            return "FAILED", None, None, session_id

        # Standardize domain & clean username
        clean_username = username
        resolved_domain = os.environ.get("USERDOMAIN", ".")
        if "\\" in username:
            parts = username.split("\\", 1)
            resolved_domain, clean_username = parts[0], parts[1]
        elif "@" in username:
            parts = username.split("@", 1)
            clean_username = parts[0]
            resolved_domain = parts[1].split(".")[0].upper()

        # Unify Role & Group Resolution!
        # Use exact same _get_token_groups(h_token) and _map_groups_to_roles(groups, username) as /windows-login
        from app.core.security import _get_token_groups, _map_groups_to_roles

        groups = []
        if has_token and h_token.value:
            groups = _get_token_groups(h_token)
            kernel32.CloseHandle(h_token)

        roles = _map_groups_to_roles(groups, clean_username)

        logger.info(
            f"[SSO] SUCCESS: User='{clean_username}' domain='{resolved_domain}' groups={groups} roles={roles}"
        )

        user_info = {
            "username": clean_username,
            "domain": resolved_domain,
            "groups": groups,
            "roles": roles,
        }
        return "COMPLETE", None, user_info, session_id

    # Case 3: Failed
    else:
        logger.error(
            f"[SSO] SSPI AcceptSecurityContext failed with status {hex(unsigned_ret)}"
        )
        # Clean up handles
        if ctx:
            secur32.DeleteSecurityContext(ctypes.byref(ctx))
        secur32.FreeCredentialsHandle(ctypes.byref(cred))
        SSO_SESSIONS.pop(session_id, None)
        return "FAILED", None, None, session_id
