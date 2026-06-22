"""app/services/intent_normalizer.py
Normalizes user questions before retrieval.

Standalone queries are passed through unchanged — they already carry full
context, so rewriting them adds latency/cost without improving recall.

Follow-up queries (questions that depend on a prior turn, e.g. "what about
its members?" or "show the same for last week") are rewritten via a single
LLM call into a clear, context-independent question phrased with the
domain's canonical terminology, using the recent conversation history to
resolve references.
"""

from typing import Optional


# ─── LLM-based intent rewrite (follow-up questions only) ────────────────────

_REWRITE_SYSTEM_PROMPT = """\
You are a query normalizer for a Meeting Management System (MeetingSphere).

The system has these main entities:
- Committees (groups that hold meetings)
- Meetings (individual sessions held by a committee)
- Members / Users (people assigned to committees)
- Agendas (topics for a meeting)
- Minutes of Meeting (MOM) – notes recorded after a meeting
- Shared Documents – files shared with committees or meetings
- Attachments – files attached to agenda items or minutes
- Meeting Profiles – configuration templates for committees

You will be given the recent conversation history and a follow-up question
from the user. Rewrite the follow-up question into a single, standalone
question, following these rules strictly:

  1. ONLY resolve something if the follow-up question itself contains an
     actual unresolved reference — a pronoun ("it", "its", "they"), a
     demonstrative ("that meeting", "this one"), or an implicit reference
     ("the same one", "him/her"). Replace that specific reference with the
     concrete entity it points to, using the conversation history.
     Example: "what about its members?" -> "What are the members of the
     Finance Committee?" (the history showed "its" = Finance Committee)

  2. If the follow-up question already fully specifies what it's asking
     about — by name, by an explicit ordinal/relative description ("the
     second last meeting", "last week's meetings"), or any other
     self-contained phrasing — do NOT add any extra detail, filter,
     qualifier, or entity name that is not already in the question, even if
     that detail is sitting in the conversation history.
     Example: "show me the attachments of second last meeting" -> "What are
     the attachments of the second last meeting?" (do NOT append a
     committee name — "second last meeting" already fully specifies which
     meeting is meant, with no pronoun to resolve)

  3. Canonical terminology substitution (e.g. "attendees" -> "Members",
     "sessions" -> "Meetings") is allowed and encouraged, but only as a
     vocabulary swap — never as a reason to introduce new specifics.

  4. If nothing in the question needs resolving, return it unchanged
     (only with canonical terminology applied per rule 3).

When in doubt, prefer changing less. Respond with ONLY the rewritten
question — no explanation, no quotes.
"""


def _format_history(conversation_history: list[str]) -> str:
    return "\n".join(f"- {turn}" for turn in conversation_history)


def llm_rewrite_question(
    question: str,
    api_key: str,
    conversation_history: Optional[list[str]] = None,
    model: str = "gpt-4.1-mini",
) -> str:
    """
    Use an LLM to rewrite a follow-up question into a standalone,
    domain-canonical question. Falls back to the original question on
    any error.

    `conversation_history` should contain the recent prior turns (most
    recent last) so the model can resolve references like "it" or "the
    same one".
    """
    import openai

    user_content = question
    if conversation_history:
        user_content = (
            f"Conversation history:\n{_format_history(conversation_history)}\n\n"
            f"Follow-up question: {question}"
        )

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _REWRITE_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0,
            max_tokens=200,
        )
        rewritten = response.choices[0].message.content.strip()
        return rewritten if rewritten else question
    except Exception:
        return question  # graceful fallback — never break the pipeline


def normalize_question(
    question: str,
    api_key: str,
    is_followup: bool = False,
    conversation_history: Optional[list[str]] = None,
    model: str = "gpt-4.1-mini",
) -> tuple[str, str]:
    """
    Full normalization pipeline.

      - Standalone queries: returned as-is, no API call.
      - Follow-up queries: rewritten via LLM into a standalone,
        domain-canonical question.

    `is_followup` should be set by the caller (e.g. based on whether this
    turn references prior conversation, or via a lightweight classifier
    upstream).

    Returns (normalized_question, method_used) where method_used is
    'llm' or 'passthrough'.
    """
    if not is_followup:
        return question, "passthrough"

    rewritten = llm_rewrite_question(
        question,
        api_key=api_key,
        conversation_history=conversation_history,
        model=model,
    )
    method = "llm" if rewritten.lower() != question.lower() else "passthrough"
    return rewritten, method