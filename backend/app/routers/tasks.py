from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.activity import log_activity
from app.database import get_db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[schemas.TaskOut])
def list_tasks(
    project_id: Optional[int] = None,
    episode_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Task)
    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    if episode_id:
        query = query.filter(models.Task.episode_id == episode_id)
    if status_filter:
        query = query.filter(models.Task.status == status_filter)
    return query.order_by(models.Task.created_at.desc()).all()


@router.post("", response_model=schemas.TaskOut, status_code=201)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    project = db.get(models.Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    task = models.Task(**payload.model_dump())
    db.add(task)
    db.flush()
    log_activity(
        db,
        project_id=task.project_id,
        episode_id=task.episode_id,
        event_type="TASK_CREATED",
        entity_type="TASK",
        entity_id=task.id,
        new_state=task.status,
    )
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    old_status = task.status
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    if payload.status and payload.status in ("FINALIZADO", "CANCELADO") and old_status not in (
        "FINALIZADO",
        "CANCELADO",
    ):
        from datetime import datetime

        task.resolved_at = datetime.utcnow()
    db.flush()
    if payload.status and payload.status != old_status:
        log_activity(
            db,
            project_id=task.project_id,
            episode_id=task.episode_id,
            event_type="TASK_STATUS_CHANGED",
            entity_type="TASK",
            entity_id=task.id,
            old_state=old_status,
            new_state=task.status,
        )
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    db.delete(task)
    db.commit()
    return None
