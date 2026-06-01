"""app/services/feedback_service.py
Stores thumbs-up / thumbs-down feedback.
On thumbs-UP: automatically re-trains Vanna with the Q→SQL pair.
On thumbs-DOWN: logs it for review; does NOT pollute the model.
"""
import uuid
from datetime import datetime
from tinydb import TinyDB, Query
from app.services import vanna_service

_db = TinyDB("./feedback_store.json")
_feedback_table = _db.table("feedback")


def submit_feedback(
    instance_key: str,
    question: str,
    sql: str,
    thumbs_up: bool,
    user: str,
    comment: str = "",
) -> dict:
    record = {
        "id": str(uuid.uuid4()),
        "instance_key": instance_key,
        "question": question,
        "sql": sql,
        "thumbs_up": thumbs_up,
        "user": user,
        "comment": comment,
        "timestamp": datetime.utcnow().isoformat(),
        "trained": False,
    }

    _feedback_table.insert(record)

    # Auto-train on positive feedback
    if thumbs_up and sql:
        try:
            vanna_service.train_qa(instance_key, question, sql)
            # Mark as trained
            Q = Query()
            _feedback_table.update({"trained": True}, Q.id == record["id"])
            record["trained"] = True
        except Exception as e:
            record["train_error"] = str(e)

    return record


def get_feedback(instance_key: str = None) -> list[dict]:
    if instance_key:
        Q = Query()
        return _feedback_table.search(Q.instance_key == instance_key)
    return _feedback_table.all()


def get_feedback_stats(instance_key: str) -> dict:
    Q = Query()
    all_fb = _feedback_table.search(Q.instance_key == instance_key)
    total = len(all_fb)
    positive = sum(1 for f in all_fb if f["thumbs_up"])
    negative = total - positive
    return {
        "total": total,
        "positive": positive,
        "negative": negative,
        "trained_from_feedback": sum(1 for f in all_fb if f.get("trained")),
    }