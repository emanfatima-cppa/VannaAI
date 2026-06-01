"""app/api/admin.py
Super-admin routes for:
  - User management  (list / create / update / delete)
  - Instance health checks
  - Dynamic instance registration / deregistration
  - System-wide feedback aggregation
  - Audit log (in-memory for now)

All endpoints require a role ending in '_admin'.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user, pwd_context, FAKE_USERS
from app.core.permissions import require_admin, INSTANCE_ROLES
from app.models.user import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse,
    RoleInfo,
    RoleListResponse,
    VALID_ROLES,
    ROLE_DESCRIPTIONS,
    validate_roles,
)
from app.models.feedback import (
    FeedbackStatsResponse,
    FeedbackAllStatsResponse,
)
from app.db.instances import (
    get_all_instance_details,
    get_instance_detail,
    check_health,
    check_all_health,
    register_instance,
    deregister_instance,
    build_mssql_conn_string,
    build_azure_sql_conn_string,
    InstanceAlreadyExistsError,
    InstanceNotFoundError,
)
from app.services.feedback_service import get_feedback_stats
from app.db.connection_manager import INSTANCE_META

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])

# ── Simple in-memory audit log ────────────────────────────────────────────────
_audit_log: list[dict] = []


def _audit(action: str, actor: str, detail: str = ""):
    entry = {"ts": datetime.utcnow().isoformat(), "action": action, "actor": actor, "detail": detail}
    _audit_log.append(entry)
    logger.info(f"AUDIT | {actor} | {action} | {detail}")


# ═══════════════════════════════════════════════════════════════════════════════
# USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/users", response_model=UserListResponse)
async def list_users(current_user: dict = Depends(get_current_user)):
    """List all users (without passwords)."""
    require_admin(current_user)
    users = [
        UserResponse(username=u["username"], roles=u["roles"])
        for u in FAKE_USERS.values()
    ]
    return UserListResponse(total=len(users), users=users)


@router.get("/users/{username}", response_model=UserResponse)
async def get_user(username: str, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    user = FAKE_USERS.get(username)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    return UserResponse(username=user["username"], roles=user["roles"])


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(req: UserCreateRequest, current_user: dict = Depends(get_current_user)):
    """
    Create a new user.
    NOTE: FAKE_USERS is an in-memory dict. In production, persist to a real DB.
    """
    require_admin(current_user)

    if req.username in FAKE_USERS:
        raise HTTPException(status_code=409, detail=f"Username '{req.username}' already exists")

    try:
        validate_roles(req.roles)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    FAKE_USERS[req.username] = {
        "username": req.username,
        "hashed_password": pwd_context.hash(req.password),
        "roles": req.roles,
        "full_name": req.full_name,
        "email": req.email,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
    }
    _audit("CREATE_USER", current_user["username"], f"created user '{req.username}' with roles {req.roles}")
    return UserResponse(
        username=req.username,
        roles=req.roles,
        full_name=req.full_name,
        email=req.email,
    )


@router.patch("/users/{username}", response_model=UserResponse)
async def update_user(
    username: str,
    req: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Partial update: password, roles, full_name, email, is_active."""
    require_admin(current_user)

    user = FAKE_USERS.get(username)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    if req.password is not None:
        user["hashed_password"] = pwd_context.hash(req.password)

    if req.roles is not None:
        try:
            validate_roles(req.roles)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        user["roles"] = req.roles

    if req.full_name is not None:
        user["full_name"] = req.full_name
    if req.email is not None:
        user["email"] = req.email
    if req.is_active is not None:
        user["is_active"] = req.is_active

    _audit("UPDATE_USER", current_user["username"], f"updated '{username}'")
    return UserResponse(
        username=user["username"],
        roles=user["roles"],
        full_name=user.get("full_name"),
        email=user.get("email"),
        is_active=user.get("is_active", True),
    )


@router.delete("/users/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(username: str, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)

    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    if username not in FAKE_USERS:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    del FAKE_USERS[username]
    _audit("DELETE_USER", current_user["username"], f"deleted '{username}'")


# ═══════════════════════════════════════════════════════════════════════════════
# ROLES
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/roles", response_model=RoleListResponse)
async def list_roles(current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    roles = []
    for role in VALID_ROLES:
        accessible = [k for k, allowed in INSTANCE_ROLES.items() if role in allowed]
        roles.append(RoleInfo(
            role=role,
            description=ROLE_DESCRIPTIONS.get(role, ""),
            accessible_instances=accessible,
        ))
    return RoleListResponse(roles=roles)


# ═══════════════════════════════════════════════════════════════════════════════
# INSTANCE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/instances")
async def list_instances(current_user: dict = Depends(get_current_user)):
    """All instances with enriched metadata (db_type_label, is_runtime, etc.)."""
    require_admin(current_user)
    return get_all_instance_details()


@router.get("/instances/{instance_key}")
async def get_instance(instance_key: str, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    detail = get_instance_detail(instance_key)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Instance '{instance_key}' not found")
    return detail


@router.get("/instances/{instance_key}/health")
async def instance_health(instance_key: str, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    return check_health(instance_key)


@router.get("/health")
async def all_health(current_user: dict = Depends(get_current_user)):
    """Health check every registered instance."""
    require_admin(current_user)
    return check_all_health()


# ── Dynamic instance registration ─────────────────────────────────────────────

class RegisterInstanceBody:
    """Inline model to avoid circular import with models/."""
    pass


from pydantic import BaseModel as _BM
from typing import Literal as _Lit, Optional as _Opt


class RegisterInstanceRequest(_BM):
    key: str
    label: str
    group: str
    db_type: _Lit["sqlserver", "azure_sql", "oracle", "postgres", "mysql"]
    description: str = ""
    # Provide either a raw conn_string OR individual fields
    conn_string: _Opt[str] = None
    # MSSQL / Azure fields (used if conn_string is None)
    server: _Opt[str] = None
    database: _Opt[str] = None
    uid: _Opt[str] = None
    pwd: _Opt[str] = None
    trust_cert: bool = True
    timeout: int = 30


@router.post("/instances", status_code=status.HTTP_201_CREATED)
async def register_new_instance(
    req: RegisterInstanceRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Dynamically register a new DB instance without restarting the server.
    The instance will be available immediately but is not persisted across restarts.
    Add it to connection_manager.py for permanence.
    """
    require_admin(current_user)

    # Build conn string if not provided directly
    conn_string = req.conn_string
    if not conn_string:
        if not all([req.server, req.database, req.uid, req.pwd]):
            raise HTTPException(
                status_code=422,
                detail="Provide either conn_string or (server, database, uid, pwd)",
            )
        if req.db_type == "azure_sql":
            conn_string = build_azure_sql_conn_string(
                req.server, req.database, req.uid, req.pwd, timeout=req.timeout
            )
        else:
            conn_string = build_mssql_conn_string(
                req.server, req.database, req.uid, req.pwd, trust_cert=req.trust_cert
            )

    try:
        detail = register_instance(
            key=req.key,
            label=req.label,
            group=req.group,
            db_type=req.db_type,
            description=req.description,
            conn_string=conn_string,
        )
    except InstanceAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))

    _audit("REGISTER_INSTANCE", current_user["username"], f"registered '{req.key}' ({req.label})")
    return detail


@router.delete("/instances/{instance_key}", status_code=status.HTTP_204_NO_CONTENT)
async def deregister_instance_endpoint(
    instance_key: str,
    current_user: dict = Depends(get_current_user),
):
    """Remove a runtime-registered instance (static instances cannot be removed)."""
    require_admin(current_user)
    try:
        deregister_instance(instance_key)
    except InstanceAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InstanceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    _audit("DEREGISTER_INSTANCE", current_user["username"], f"removed '{instance_key}'")


# ═══════════════════════════════════════════════════════════════════════════════
# FEEDBACK AGGREGATION (cross-instance dashboard)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/feedback/all", response_model=FeedbackAllStatsResponse)
async def all_feedback_stats(current_user: dict = Depends(get_current_user)):
    """Aggregate feedback stats across every instance – for the admin dashboard."""
    require_admin(current_user)

    instance_keys = list(INSTANCE_META.keys())
    per_instance = []
    for key in instance_keys:
        raw = get_feedback_stats(key)
        per_instance.append(FeedbackStatsResponse.from_raw(key, raw))

    grand_total    = sum(s.total for s in per_instance)
    grand_positive = sum(s.positive for s in per_instance)
    grand_negative = sum(s.negative for s in per_instance)
    grand_trained  = sum(s.trained_from_feedback for s in per_instance)

    return FeedbackAllStatsResponse(
        instances=per_instance,
        grand_total=grand_total,
        grand_positive=grand_positive,
        grand_negative=grand_negative,
        grand_trained=grand_trained,
        overall_positive_rate=round(grand_positive / grand_total, 4) if grand_total > 0 else 0.0,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT LOG
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/audit-log")
async def get_audit_log(
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
):
    require_admin(current_user)
    return {"total": len(_audit_log), "entries": _audit_log[-limit:]}