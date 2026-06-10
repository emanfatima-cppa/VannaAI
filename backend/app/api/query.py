"""app/api/query.py"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.core.permissions import check_instance_access
from app.models.query import QueryRequest, QueryResponse, FeedbackRequest
from app.services import vanna_service, context_service, feedback_service
from app.db.connection_manager import get_all_instances, INSTANCE_META

router = APIRouter(prefix="/api/query", tags=["query"])

# Maximum number of sample values to include in a column's summary.
_MAX_SAMPLE_VALUES = 3


def _build_answer_summary(result: dict) -> str:
    """
    Produce a meaningful, LLM-readable summary of the query result so the
    context service can later resolve follow-up references like
    'those customers', 'the top result', or 'the same period'.

    Rules:
      - Error   → plain error message.
      - 0 rows  → "No rows returned."
      - 1 row   → inline key=value pairs for every column.
      - 2+ rows → row count + per-column value samples drawn from the first
                  _MAX_SAMPLE_VALUES rows, so the LLM knows what entities
                  were returned without seeing the full resultset.
    """
    if result.get("error"):
        return f"Error: {result['error']}"

    rows: list[dict] = result.get("results") or []

    if not rows:
        return "No rows returned."

    if len(rows) == 1:
        # Single row: emit all column values verbatim
        pairs = ", ".join(f"{k}={v}" for k, v in rows[0].items())
        return f"1 row: {pairs}"

    # Multiple rows: emit row count + sampled values per column
    row_count = len(rows)
    sample_rows = rows[:_MAX_SAMPLE_VALUES]
    columns = list(rows[0].keys())

    col_summaries = []
    for col in columns:
        samples = [str(r[col]) for r in sample_rows if r.get(col) is not None]
        if samples:
            col_summaries.append(f"{col}: [{', '.join(samples)}{'…' if row_count > _MAX_SAMPLE_VALUES else ''}]")

    cols_str = "; ".join(col_summaries) if col_summaries else "no columns"
    return f"{row_count} rows — {cols_str}"


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
    enriched_question = (
        f"{context_block}\n\nCurrent question: {req.question}".strip()
        if context_block
        else req.question
    )

    result = vanna_service.run_query(req.instance_key, enriched_question)

    context_service.add_turn(
        current_user["username"],
        req.instance_key,
        req.session_id,
        req.question,
        result.get("sql"),
        _build_answer_summary(result),
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