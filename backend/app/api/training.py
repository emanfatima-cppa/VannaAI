"""app/api/training.py – admin-only training endpoints."""
from fastapi import APIRouter, Depends, BackgroundTasks
from app.core.security import get_current_user
from app.core.permissions import require_admin, check_instance_access
from app.models.query import TrainRequest
from app.training.trainer import train_instance, train_all_instances
from app.services.vanna_service import get_training_data, remove_training_data
from app.services.feedback_service import get_feedback, get_feedback_stats

router = APIRouter(prefix="/api/training", tags=["training"])


@router.post("/run")
async def run_training(
    req: TrainRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    require_admin(current_user)
    check_instance_access(req.instance_key, current_user)
    background_tasks.add_task(train_instance, req.instance_key, req.skip_schema)
    return {"status": "Training started in background", "instance": req.instance_key}


@router.post("/run-all")
async def run_all_training(
    background_tasks: BackgroundTasks,
    skip_schema: bool = False,
    current_user: dict = Depends(get_current_user),
):
    require_admin(current_user)
    background_tasks.add_task(train_all_instances, skip_schema)
    return {"status": "Training all instances started in background"}


@router.get("/data/{instance_key}")
async def list_training_data(
    instance_key: str,
    current_user: dict = Depends(get_current_user),
):
    require_admin(current_user)
    check_instance_access(instance_key, current_user)
    return get_training_data(instance_key)


@router.delete("/data/{instance_key}/{training_id}")
async def delete_training_record(
    instance_key: str,
    training_id: str,
    current_user: dict = Depends(get_current_user),
):
    require_admin(current_user)
    check_instance_access(instance_key, current_user)
    removed = remove_training_data(instance_key, training_id)
    return {"removed": removed}


@router.get("/feedback")
async def list_feedback(
    instance_key: str = None,
    current_user: dict = Depends(get_current_user),
):
    require_admin(current_user)
    return get_feedback(instance_key)


@router.get("/feedback/stats/{instance_key}")
async def feedback_stats(
    instance_key: str,
    current_user: dict = Depends(get_current_user),
):
    require_admin(current_user)
    return get_feedback_stats(instance_key)