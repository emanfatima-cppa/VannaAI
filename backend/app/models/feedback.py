"""app/models/feedback.py – Pydantic schemas for the feedback & training loop."""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# ── Request schemas ───────────────────────────────────────────────────────────

class FeedbackSubmitRequest(BaseModel):
    """
    Submitted by the frontend when the user clicks 👍 or 👎.
    thumbs_up=True  → auto-trains Vanna with this Q→SQL pair.
    thumbs_up=False → logs for admin review only.
    """
    instance_key: str
    question: str = Field(..., min_length=1)
    sql: str = Field(..., min_length=1)
    thumbs_up: bool
    comment: str = Field(default="", max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "instance_key": "it_meetingsphere",
                "question": "How many meetings are this month?",
                "sql": "SELECT COUNT(*) FROM Meetings WHERE MONTH(ScheduledAt) = MONTH(GETDATE())",
                "thumbs_up": True,
                "comment": "Perfect result",
            }
        }


class FeedbackFilterRequest(BaseModel):
    """Query parameters for filtering feedback records."""
    instance_key: Optional[str] = None
    thumbs_up: Optional[bool] = None          # None = all, True = positive only, False = negative only
    trained: Optional[bool] = None            # None = all, True = already used for training
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


# ── Response schemas ──────────────────────────────────────────────────────────

class FeedbackRecord(BaseModel):
    """A single stored feedback entry."""
    id: str
    instance_key: str
    question: str
    sql: str
    thumbs_up: bool
    user: str
    comment: str
    timestamp: str                            # ISO-8601 string from tinydb
    trained: bool = False
    train_error: Optional[str] = None


class FeedbackSubmitResponse(BaseModel):
    saved: bool
    trained: bool
    message: str
    record_id: Optional[str] = None


class FeedbackListResponse(BaseModel):
    total: int
    records: list[FeedbackRecord]


class FeedbackStatsResponse(BaseModel):
    instance_key: str
    total: int
    positive: int
    negative: int
    trained_from_feedback: int
    positive_rate: float = 0.0               # 0.0–1.0

    @classmethod
    def from_raw(cls, instance_key: str, raw: dict) -> "FeedbackStatsResponse":
        total = raw.get("total", 0)
        positive = raw.get("positive", 0)
        return cls(
            instance_key=instance_key,
            total=total,
            positive=positive,
            negative=raw.get("negative", 0),
            trained_from_feedback=raw.get("trained_from_feedback", 0),
            positive_rate=round(positive / total, 4) if total > 0 else 0.0,
        )


class FeedbackAllStatsResponse(BaseModel):
    """Aggregated stats across all instances – used by the admin dashboard."""
    instances: list[FeedbackStatsResponse]
    grand_total: int
    grand_positive: int
    grand_negative: int
    grand_trained: int
    overall_positive_rate: float


# ── Training data schemas (reused by admin panel) ─────────────────────────────

class TrainingRecord(BaseModel):
    """
    Mirrors the rows Vanna returns from get_training_data().
    training_data_type is one of: 'sql', 'ddl', 'documentation'
    """
    id: str
    training_data_type: Literal["sql", "ddl", "documentation"]
    question: Optional[str] = None           # present when type == 'sql'
    content: Optional[str] = None            # present when type == 'documentation'
    ddl: Optional[str] = None                # present when type == 'ddl'


class TrainingDataResponse(BaseModel):
    instance_key: str
    total: int
    records: list[TrainingRecord]


class TrainJobResponse(BaseModel):
    status: str
    instance: Optional[str] = None
    message: str = ""