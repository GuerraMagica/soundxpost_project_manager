from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.activity import log_activity
from app.database import get_db

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Project)
    if status_filter:
        query = query.filter(models.Project.status == status_filter)
    return query.order_by(models.Project.created_at.desc()).all()


@router.post("", response_model=schemas.ProjectOut, status_code=201)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    if db.query(models.Project).filter(models.Project.code == payload.code).first():
        raise HTTPException(status_code=409, detail="Ya existe un proyecto con ese código")
    project = models.Project(**payload.model_dump())
    db.add(project)
    db.flush()
    log_activity(
        db,
        project_id=project.id,
        event_type="PROJECT_CREATED",
        entity_type="PROJECT",
        entity_id=project.id,
        new_state=project.status,
    )
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@router.patch("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, payload: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    old_status = project.status
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.flush()
    if payload.status and payload.status != old_status:
        log_activity(
            db,
            project_id=project.id,
            event_type="PROJECT_STATUS_CHANGED",
            entity_type="PROJECT",
            entity_id=project.id,
            old_state=old_status,
            new_state=project.status,
        )
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}/episodes", response_model=list[schemas.EpisodeOut])
def list_project_episodes(project_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Episode)
        .filter(models.Episode.project_id == project_id)
        .order_by(models.Episode.order_index)
        .all()
    )
