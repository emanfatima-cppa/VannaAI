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

    # Build context-enriched question
    context_block = context_service.get_context_prompt(
        current_user["username"], req.instance_key, req.session_id
    )
    enriched_question = f"{context_block}\n\nCurrent question: {req.question}".strip() if context_block else req.question

    result = vanna_service.run_query(req.instance_key, enriched_question)

    # Summarise answer for context (row count or first value)
    if result["results"]:
        summary = f"{len(result['results'])} row(s) returned"
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