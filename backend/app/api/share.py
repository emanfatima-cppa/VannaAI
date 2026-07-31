"""app/api/share.py"""
import uuid
import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_user
from app.db.auth_db import create_shared_session, get_shared_session
from app.services import context_service

router = APIRouter(prefix="/api/share", tags=["share"])


class ShareCreateRequest(BaseModel):
    instance_key: str
    messages: list
    title: Optional[str] = None


class ForkShareRequest(BaseModel):
    share_id: str


@router.post("/create")
async def create_share_link(
    req: ShareCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a frozen, shareable snapshot of a chat conversation."""
    if not req.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot share an empty conversation"
        )

    # Generate title from first question if not provided
    title = req.title
    if not title:
        first_q = None
        for m in req.messages:
            if isinstance(m, dict) and m.get("question"):
                first_q = m.get("question")
                break
        title = first_q[:60] if first_q else "Shared Chat"

    share_id = f"sh_{uuid.uuid4().hex[:10]}"
    messages_json = json.dumps(req.messages)

    success = create_shared_session(
        share_id=share_id,
        owner_username=current_user["username"],
        instance_key=req.instance_key,
        title=title,
        messages_json=messages_json,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save shared chat session"
        )

    return {
        "share_id": share_id,
        "title": title,
        "instance_key": req.instance_key,
        "owner_username": current_user["username"],
    }


@router.get("/{share_id}")
async def get_shared_chat(share_id: str):
    """Get public/authenticated shared chat snapshot by share_id."""
    data = get_shared_session(share_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared chat link not found or expired"
        )

    try:
        data["messages"] = json.loads(data["messages_json"])
    except Exception:
        data["messages"] = []

    data.pop("messages_json", None)
    return data


@router.post("/fork")
async def fork_shared_chat(
    req: ForkShareRequest,
    current_user: dict = Depends(get_current_user),
):
    """Fork a shared chat into a new active session for the recipient."""
    data = get_shared_session(req.share_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared chat link not found"
        )

    new_session_id = f"fork_{uuid.uuid4().hex[:8]}"
    try:
        messages = json.loads(data["messages_json"])
        for msg in messages:
            if isinstance(msg, dict):
                q = msg.get("question")
                sql = msg.get("sql")
                summary = msg.get("nl_summary") or msg.get("error") or "Shared turn"
                if q:
                    context_service.add_turn(
                        user=current_user["username"],
                        instance_key=data["instance_key"],
                        session_id=new_session_id,
                        question=q,
                        sql=sql,
                        answer_summary=summary,
                    )
    except Exception:
        pass

    return {
        "new_session_id": new_session_id,
        "instance_key": data["instance_key"],
        "messages": json.loads(data["messages_json"]) if data.get("messages_json") else [],
    }
