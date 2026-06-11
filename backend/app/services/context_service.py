"""app/services/context_service.py
Maintains per-session conversation context so follow-up questions
can reference previous queries and results.
"""
from collections import deque
from typing import Optional
import threading

MAX_CONTEXT_TURNS = 10  # keep last N Q&A pairs per session

_sessions: dict[str, deque] = {}
_lock = threading.Lock()


def _session_key(user: str, instance_key: str, session_id: str) -> str:
    return f"{user}::{instance_key}::{session_id}"


def add_turn(user: str, instance_key: str, session_id: str, question: str, sql: Optional[str], answer_summary: str) -> None:
    key = _session_key(user, instance_key, session_id)
    with _lock:
        if key not in _sessions:
            _sessions[key] = deque(maxlen=MAX_CONTEXT_TURNS)
        _sessions[key].append({
            "question": question,
            "sql": sql,
            "answer_summary": answer_summary,
        })


def get_context_prompt(user: str, instance_key: str, session_id: str) -> str:
    """
    Build a natural-language context block to prepend to the next question,
    so Vanna's LLM call can reference prior turns.
    """
    key = _session_key(user, instance_key, session_id)
    with _lock:
        history = list(_sessions.get(key, []))

    if not history:
        return ""

    lines = ["Previous questions in this session:"]
    for i, turn in enumerate(history, 1):
        lines.append(f"  {i}. Q: {turn['question']}")
        if turn["sql"]:
            lines.append(f"     SQL: {turn['sql']}")
        lines.append(f"     Result summary: {turn['answer_summary']}")
    return "\n".join(lines)


def clear_context(user: str, instance_key: str, session_id: str) -> None:
    key = _session_key(user, instance_key, session_id)
    with _lock:
        _sessions.pop(key, None)


def get_session_history(user: str, instance_key: str, session_id: str) -> list[dict]:
    key = _session_key(user, instance_key, session_id)
    with _lock:
        return list(_sessions.get(key, []))