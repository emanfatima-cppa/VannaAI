"""app/api/query.py"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.core.permissions import check_instance_access
from app.models.query import QueryRequest, QueryResponse, FeedbackRequest
from app.services import vanna_service, context_service, feedback_service
from app.db.connection_manager import get_all_instances, INSTANCE_META

router = APIRouter(prefix="/api/query", tags=["query"])


@router.get("/instances")
async def list_instances(current_user: dict = Depends(get_current_user)):
    """Return only the instances the current user can access."""
    all_instances = get_all_instances()
    accessible = []
    for inst in all_instances:
        try:
            check_instance_access(inst["key"], current_user)
            accessible.append(inst)
        except HTTPException:
            pass
    return accessible


@router.post("/ask", response_model=QueryResponse)
async def ask(req: QueryRequest, current_user: dict = Depends(get_current_user)):
    check_instance_access(req.instance_key, current_user)

    context_block = context_service.get_context_prompt(
        current_user["username"], req.instance_key, req.session_id
    )
    enriched_question = (
        f"{context_block}\n\nCurrent question: {req.question}".strip()
        if context_block else req.question
    )

    result = vanna_service.run_query(
        req.instance_key,
        enriched_question,          # for SQL generation (needs context)
        summary_question=req.question,  # clean question for NL summary
    )

    # Summarise for context memory.
    # IMPORTANT: this needs enough concrete detail (actual identifiers/titles
    # from the rows) for a later follow-up like "and its agenda?" to resolve
    # against specific entities — a bare row count gives the rewriter
    # nothing to anchor "it"/"its" to, and it'll fall back to whatever is
    # semantically nearest in training data instead of the right meeting.
    if result["results"]:
        preview_rows = result["results"][:5]
        row_previews = [
            ", ".join(f"{k}={v}" for k, v in row.items())
            for row in preview_rows
        ]
        preview_text = "; ".join(row_previews)
        if len(preview_text) > 800:
            preview_text = preview_text[:800] + "..."
        remaining = len(result["results"]) - len(preview_rows)
        if remaining > 0:
            preview_text += f"; ... ({remaining} more row(s))"
        summary = f"{len(result['results'])} row(s) returned: {preview_text}"
    elif result["error"]:
        summary = f"Error: {result['error']}"
    else:
        summary = "No results"

    context_service.add_turn(
        current_user["username"], req.instance_key, req.session_id,
        req.question, result.get("sql"), summary
    )

    return QueryResponse(
        instance_key=req.instance_key,
        question=req.question,
        sql=result.get("sql"),
        results=result.get("results"),
        error=result.get("error"),
        session_id=req.session_id,
        nl_summary=result.get("nl_summary"),   # ← new
    )


@router.get("/history")
async def session_history(
    instance_key: str,
    session_id: str = "default",
    current_user: dict = Depends(get_current_user),
):
    check_instance_access(instance_key, current_user)
    return context_service.get_session_history(
        current_user["username"], instance_key, session_id
    )


@router.delete("/history")
async def clear_history(
    instance_key: str,
    session_id: str = "default",
    current_user: dict = Depends(get_current_user),
):
    check_instance_access(instance_key, current_user)
    context_service.clear_context(current_user["username"], instance_key, session_id)
    return {"cleared": True}


@router.post("/feedback")
async def feedback(req: FeedbackRequest, current_user: dict = Depends(get_current_user)):
    check_instance_access(req.instance_key, current_user)
    record = feedback_service.submit_feedback(
        instance_key=req.instance_key,
        question=req.question,
        sql=req.sql,
        thumbs_up=req.thumbs_up,
        user=current_user["username"],
        comment=req.comment,
    )
    return {
        "saved": True,
        "trained": record.get("trained", False),
        "message": "Added to training data ✓" if record.get("trained") else "Feedback recorded",
    }