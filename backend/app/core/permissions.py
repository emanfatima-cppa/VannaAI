"""app/core/permissions.py – maps DB instances to allowed roles."""
from fastapi import HTTPException, status

# ── Instance → role whitelist ─────────────────────────────────────────────────
INSTANCE_ROLES: dict[str, list[str]] = {
    "hr_policies":       ["hr_admin", "hr_viewer"],
    "hr_salaries":       ["hr_admin"],
    "it_meetingsphere":  ["it_admin", "it_viewer"],
    "it_cdxp":            ["it_admin", "it_viewer"],
}


def check_instance_access(instance_key: str, user: dict) -> None:
    """Raise 403 if the user has no role that grants access to the instance."""
    allowed = INSTANCE_ROLES.get(instance_key)
    if allowed is None:
        raise HTTPException(status_code=404, detail=f"Unknown instance: {instance_key}")

    user_roles: list[str] = user.get("roles", [])
    if not any(r in allowed for r in user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role(s) {user_roles} not permitted on instance '{instance_key}'",
        )


def require_admin(user: dict) -> None:
    """Only hr_admin or it_admin may trigger training."""
    if not any(r.endswith("_admin") for r in user.get("roles", [])):
        raise HTTPException(status_code=403, detail="Admin role required")