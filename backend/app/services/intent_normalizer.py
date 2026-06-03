"""app/services/intent_normalizer.py
Normalizes user questions by expanding synonyms and mapping domain vocabulary
to the terms used in training data and documentation.

Two complementary strategies:
  1. Keyword substitution  – fast, deterministic, zero-cost
  2. LLM intent rewrite   – handles complex/ambiguous phrasings (optional, one API call)
"""

import re
from typing import Optional


# ─── Domain synonym map ───────────────────────────────────────────────────────
# Keys   = canonical term used in training data / docs
# Values = list of user synonyms that should map to the canonical term
#
# Add new synonyms here as you discover them from real user queries.

SYNONYM_MAP: dict[str, list[str]] = {

    # ── People / membership ───────────────────────────────────────────────────
    "members": [
        "participants", "attendees", "people", "persons", "individuals",
        "users", "invitees", "delegates", "representatives", "contributors",
        "staff", "employees", "team", "team members",

        # Added
        "associates", "colleagues", "memberships", "stakeholders",
        "registrants", "guests", "volunteers", "occupants",
        "affiliates", "constituents",
    ],

    # ── Meetings ──────────────────────────────────────────────────────────────
    "meeting": [
        "session", "event", "conference", "call", "assembly", "gathering",
        "huddle", "sync", "standup", "stand-up", "roundtable", "seminar",
        "webinar", "workshop",

        # Added
        "discussion", "consultation", "briefing", "forum", "summit",
        "convention", "town hall", "check-in", "review", "strategy session",
    ],

    "meetings": [
        "sessions", "events", "conferences", "calls", "assemblies",
        "gatherings", "huddles", "syncs", "standups", "seminars",
        "webinars", "workshops",

        # Added
        "discussions", "consultations", "briefings", "forums", "summits",
        "conventions", "town halls", "check-ins", "reviews",
        "strategy sessions",
    ],

    # ── Committees ────────────────────────────────────────────────────────────
    "committee": [
        "board", "panel", "group", "team", "council", "task force",
        "working group", "sub-committee", "subcommittee", "department",

        # Added
        "commission", "bureau", "unit", "division", "cell",
        "advisory board", "steering committee", "governing body",
        "crew", "collective",
    ],

    "committees": [
        "boards", "panels", "groups", "teams", "councils", "task forces",
        "working groups", "sub-committees", "subcommittees", "departments",

        # Added
        "commissions", "bureaus", "units", "divisions", "cells",
        "advisory boards", "steering committees", "governing bodies",
        "crews", "collectives",
    ],

    # ── Agendas ───────────────────────────────────────────────────────────────
    "agendas": [
        "agenda items", "topics", "discussion points", "items",
        "talking points", "points", "action items",

        # Added
        "subjects", "matters", "issues", "bullet points", "plans",
        "schedules", "itineraries", "objectives", "discussion topics",
        "focus areas",
    ],

    "agenda": [
        "agenda item", "topic", "discussion point", "item",
        "talking point", "point",

        # Added
        "subject", "matter", "issue", "bullet point", "plan",
        "schedule", "itinerary", "objective", "discussion topic",
        "focus area",
    ],

    # ── Minutes of Meeting ────────────────────────────────────────────────────
    "minutes": [
        "mom", "minutes of meeting", "meeting notes", "notes",
        "meeting records", "records", "proceedings", "summary",
        "meeting summary",

        # Added
        "transcript", "log", "documentation", "report", "recap",
        "brief", "memorandum", "digest", "chronicle", "account",
    ],

    # ── Documents / attachments ───────────────────────────────────────────────
    "shared documents": [
        "files", "shared files", "documents", "docs", "attachments",
        "resources", "materials", "references",

        # Added
        "artifacts", "records", "papers", "worksheets", "spreadsheets",
        "presentations", "reports", "manuals", "handouts", "content",
    ],

    "attachment": [
        "file", "document", "doc", "upload", "annexed file",
        "annexed document", "appended file",

        # Added
        "enclosure", "supplement", "appendix", "insert", "annex",
        "addendum", "supporting file", "supporting document",
        "linked file", "enclosed file",
    ],

    "attachments": [
        "files", "documents", "docs", "uploads", "annexed files",
        "appended files",

        # Added
        "enclosures", "supplements", "appendices", "inserts", "annexes",
        "addenda", "supporting files", "supporting documents",
        "linked files", "enclosed files",
    ],

    # ── Temporal / ordering ───────────────────────────────────────────────────
    "upcoming": [
        "future", "next", "scheduled", "planned", "incoming",
        "forthcoming", "coming",

        # Added
        "anticipated", "expected", "pending", "approaching", "on the horizon",
        "prospective", "queued", "arranged", "booked", "slated",
    ],

    "recent": [
        "latest", "last", "newest", "most recent", "previous",
        "just held", "past",

        # Added
        "current", "fresh", "new", "recently completed", "just concluded",
        "latest available", "updated", "near-term past",
        "recently conducted", "newly added",
    ],

    # ── Counts / aggregations ─────────────────────────────────────────────────
    "how many": [
        "count of", "number of", "total number of", "total count of",
        "quantity of", "# of",

        # Added
        "how much", "amount of", "aggregate of", "sum of",
        "overall count of", "tally of", "volume of",
        "frequency of", "enumeration of", "headcount of",
    ],

    "list": [
        "show", "display", "give me", "fetch", "get", "find",
        "retrieve", "what are", "tell me", "can you show", "can you list",

        # Added
        "enumerate", "present", "provide", "output", "return",
        "reveal", "lookup", "view", "bring up", "supply",
    ],
}

# Pre-build a flat lookup: synonym (lower) → canonical term
_FLAT_MAP: dict[str, str] = {}
for canonical, synonyms in SYNONYM_MAP.items():
    for syn in synonyms:
        _FLAT_MAP[syn.lower()] = canonical


def normalize_question(question: str) -> str:
    """
    Apply synonym substitution to the question.

    Strategy: match multi-word synonyms before single-word ones to avoid
    partial replacements (e.g. "team members" → "members" before "team" alone).
    Already-canonical terms are left untouched.

    Returns the normalized question string.
    """
    normalized = question

    # Sort synonyms longest-first so multi-word phrases are replaced first
    sorted_synonyms = sorted(_FLAT_MAP.keys(), key=len, reverse=True)

    for syn in sorted_synonyms:
        canonical = _FLAT_MAP[syn]
        # Word-boundary aware, case-insensitive replacement
        pattern = r'(?<!\w)' + re.escape(syn) + r'(?!\w)'
        normalized = re.sub(pattern, canonical, normalized, flags=re.IGNORECASE)

    return normalized


# ─── Optional: LLM-based intent rewrite ──────────────────────────────────────

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

Your job: rewrite the user's question so it clearly uses the above terminology,
without changing the intent. Keep the rewrite short and natural.
Respond with ONLY the rewritten question — no explanation, no quotes.
"""


def llm_rewrite_question(question: str, api_key: str, model: str = "gpt-4.1-mini") -> str:
    """
    Use an LLM to rewrite ambiguous questions into domain-canonical phrasing.
    Falls back to the original question on any error.

    This is optional and only recommended for questions that the synonym map
    doesn't handle well (detected by checking whether normalize_question changed
    anything meaningful).
    """
    import openai

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _REWRITE_SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0,
            max_tokens=200,
        )
        rewritten = response.choices[0].message.content.strip()
        return rewritten if rewritten else question
    except Exception:
        return question  # graceful fallback — never break the pipeline


def normalize_with_llm_fallback(
    question: str,
    api_key: str,
    model: str = "gpt-4.1-mini",
    always_rewrite: bool = False,
) -> tuple[str, str]:
    """
    Full normalization pipeline:
      1. Apply fast keyword substitution
      2. Optionally pass through LLM rewriter

    Returns (normalized_question, method_used) where method_used is
    'keyword', 'llm', or 'passthrough'.
    """
    after_keyword = normalize_question(question)

    # If keyword substitution already changed something, it's likely enough
    if not always_rewrite and after_keyword.lower() != question.lower():
        return after_keyword, "keyword"

    # For unchanged questions (no synonym hit), try LLM rewrite
    after_llm = llm_rewrite_question(after_keyword, api_key=api_key, model=model)
    method = "llm" if after_llm.lower() != after_keyword.lower() else "passthrough"
    return after_llm, method