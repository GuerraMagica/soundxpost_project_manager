from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.activity import log_activity
from app.database import get_db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[schemas.TaskOut])
def list_tasks(
    project_id: Optional[int] = None,
    episode_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    current_user: models.User = Depends(auth.get_current_user),
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
def create_task(
    payload: schemas.TaskCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    auth.ensure_project_access(db, current_user, payload.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear tareas")
    data = payload.model_dump()
    collaborator_ids = data.pop("collaborator_ids", [])
    task = models.Task(**data)
    if collaborator_ids:
        task.collaborators = db.query(models.User).filter(models.User.id.in_(collaborator_ids)).all()
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
def update_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    auth.ensure_project_access(db, current_user, task.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta tarea")
    old_status = task.status
    updates = payload.model_dump(exclude_unset=True)
    collaborator_ids = updates.pop("collaborator_ids", None)
    for field, value in updates.items():
        setattr(task, field, value)
    if collaborator_ids is not None:
        task.collaborators = db.query(models.User).filter(models.User.id.in_(collaborator_ids)).all()
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
def delete_task(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    auth.ensure_project_access(db, current_user, task.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta tarea")
    db.delete(task)
    db.commit()
    return None
