"""app/services/context_service.py
Maintains per-session conversation context so follow-up questions
can reference previous queries and results.
"""
from collections import deque
from typing import Optional
import threading
import re

MAX_CONTEXT_TURNS = 5        # last 5 turns is enough signal without noise
_SQL_SNIPPET_LENGTH = 120    # chars — enough to convey table/column intent

_sessions: dict[str, deque] = {}
_lock = threading.Lock()


def _session_key(user: str, instance_key: str, session_id: str) -> str:
    return f"{user}::{instance_key}::{session_id}"


def _compress_sql(sql: Optional[str]) -> Optional[str]:
    """
    Reduce SQL to its most meaningful skeleton so the LLM understands
    *what was queried* without being distracted by the full syntax.

    Strategy:
      1. Collapse all whitespace to single spaces.
      2. Strip inline comments.
      3. If still longer than _SQL_SNIPPET_LENGTH, keep the SELECT list and
         FROM clause, then append '…' — callers already store the full SQL
         for the feedback/history endpoints.
    """
    if not sql:
        return None

    # Collapse whitespace & strip SQL line comments
    compressed = re.sub(r"--[^\n]*", "", sql)
    compressed = re.sub(r"\s+", " ", compressed).strip()

    if len(compressed) <= _SQL_SNIPPET_LENGTH:
        return compressed

    # Try to extract just "SELECT … FROM <table>" as a meaningful anchor
    match = re.match(
        r"(SELECT\s+.+?\s+FROM\s+[\w\".]+)",
        compressed,
        re.IGNORECASE | re.DOTALL,
    )
    if match:
        snippet = match.group(1)
        # Still trim if the SELECT list itself is huge (e.g. SELECT *)
        if len(snippet) > _SQL_SNIPPET_LENGTH:
            snippet = snippet[:_SQL_SNIPPET_LENGTH]
        return snippet + "…"

    return compressed[:_SQL_SNIPPET_LENGTH] + "…"


def add_turn(
    user: str,
    instance_key: str,
    session_id: str,
    question: str,
    sql: Optional[str],
    answer_summary: str,
) -> None:
    key = _session_key(user, instance_key, session_id)
    with _lock:
        if key not in _sessions:
            _sessions[key] = deque(maxlen=MAX_CONTEXT_TURNS)
        _sessions[key].append({
            "question": question,
            "sql": sql,                          # full SQL preserved for history/feedback
            "sql_snippet": _compress_sql(sql),   # compact form used in prompts only
            "answer_summary": answer_summary,
        })


def get_context_prompt(user: str, instance_key: str, session_id: str) -> str:
    """
    Build a tightly-scoped context block to prepend to the next LLM call.

    Format keeps the most recent turns last (most relevant for follow-ups)
    and uses a compact structure that's easy for an LLM to parse:

        [Session context – 3 prior turns]
        Turn 1 | Q: … | SQL: … | Result: …
        Turn 2 | Q: … | SQL: … | Result: …
        ...
        Use this context to resolve references like 'those results', 'the same filter', etc.
    """
    key = _session_key(user, instance_key, session_id)
    with _lock:
        history = list(_sessions.get(key, []))

    if not history:
        return ""

    n = len(history)
    lines = [f"[Session context – {n} prior turn{'s' if n != 1 else ''}]"]

    for i, turn in enumerate(history, 1):
        parts = [f"Turn {i}", f"Q: {turn['question']}"]
        if turn["sql_snippet"]:
            parts.append(f"SQL: {turn['sql_snippet']}")
        parts.append(f"Result: {turn['answer_summary']}")
        lines.append(" | ".join(parts))

    lines.append(
        "Use this context to resolve references like 'those results', "
        "'the same filter', 'compare with previous', etc."
    )
    return "\n".join(lines)


def clear_context(user: str, instance_key: str, session_id: str) -> None:
    key = _session_key(user, instance_key, session_id)
    with _lock:
        _sessions.pop(key, None)


def get_session_history(user: str, instance_key: str, session_id: str) -> list[dict]:
    """Returns full history (including untruncated SQL) for the history endpoint."""
    key = _session_key(user, instance_key, session_id)
    with _lock:
        # Expose the stored dict but omit the internal sql_snippet key
        return [
            {k: v for k, v in turn.items() if k != "sql_snippet"}
            for turn in _sessions.get(key, [])
        ]