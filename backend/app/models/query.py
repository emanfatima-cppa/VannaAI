"""app/models/query.py"""
from pydantic import BaseModel
from typing import Optional, Any


class QueryRequest(BaseModel):
    instance_key: str
    question: str
    session_id: str = "default"


class QueryResponse(BaseModel):
    instance_key: str
    question: str
    sql: Optional[str]
    results: Optional[list[dict[str, Any]]]
    error: Optional[str]
    session_id: str
    nl_summary: Optional[str] = None


class FeedbackRequest(BaseModel):
    instance_key: str
    question: str
    sql: str
    thumbs_up: bool
    comment: str = ""


class TrainRequest(BaseModel):
    instance_key: str
    skip_schema: bool = False