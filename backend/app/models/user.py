"""app/models/user.py – Pydantic schemas for users and roles."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ── Role definitions ──────────────────────────────────────────────────────────

VALID_ROLES = [
    "hr_admin",
    "hr_viewer",
    "it_admin",
    "it_viewer",
]

ROLE_DESCRIPTIONS = {
    "hr_admin":  "Full access to all HR instances (policies + salaries)",
    "hr_viewer": "Read-only access to HR policies instance",
    "it_admin":  "Full access to all IT instances (MeetingSphere + CDXP)",
    "it_viewer": "Read-only access to IT instances",
}


# ── Request schemas ───────────────────────────────────────────────────────────

class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)
    roles: list[str] = Field(default=[], description=f"Subset of: {VALID_ROLES}")
    full_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "securepassword123",
                "roles": ["hr_viewer"],
                "full_name": "John Doe",
                "email": "john@example.com",
            }
        }


class UserUpdateRequest(BaseModel):
    """Partial update – all fields optional."""
    password: Optional[str] = Field(None, min_length=8)
    roles: Optional[list[str]] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class UserLoginRequest(BaseModel):
    username: str
    password: str


# ── Response schemas ──────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    """Safe user representation – never includes hashed_password."""
    username: str
    roles: list[str]
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    users: list[UserResponse]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    roles: list[str]
    expires_in_minutes: int


# ── Role schemas ──────────────────────────────────────────────────────────────

class RoleInfo(BaseModel):
    role: str
    description: str
    accessible_instances: list[str]


class RoleListResponse(BaseModel):
    roles: list[RoleInfo]


# ── Utility validators ────────────────────────────────────────────────────────

def validate_roles(roles: list[str]) -> list[str]:
    """Raise ValueError if any role is not in VALID_ROLES."""
    invalid = [r for r in roles if r not in VALID_ROLES]
    if invalid:
        raise ValueError(f"Invalid role(s): {invalid}. Must be one of: {VALID_ROLES}")
    return roles