from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.activity import log_activity
from app.database import get_db

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(
    status_filter: Optional[str] = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Project)
    if status_filter:
        query = query.filter(models.Project.status == status_filter)
    return query.order_by(models.Project.created_at.desc()).all()


@router.post("", response_model=schemas.ProjectOut, status_code=201)
def create_project(
    payload: schemas.ProjectCreate,
    current_user: models.User = Depends(auth.require_roles(*auth.MANAGEMENT_ROLES)),
    db: Session = Depends(get_db),
):
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
def get_project(
    project_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@router.patch("/{project_id}", response_model=schemas.ProjectOut)
def update_project(
    project_id: int,
    payload: schemas.ProjectUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    auth.ensure_project_access(db, current_user, project_id)
    if current_user.role not in auth.MANAGEMENT_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este proyecto")
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
def list_project_episodes(
    project_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Episode)
        .filter(models.Episode.project_id == project_id)
        .order_by(models.Episode.order_index)
        .all()
    )


@router.get("/{project_id}/members", response_model=list[schemas.ProjectMembershipOut])
def list_project_members(
    project_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    auth.ensure_project_access(db, current_user, project_id)
    return db.query(models.ProjectMembership).filter(models.ProjectMembership.project_id == project_id).all()


@router.post("/{project_id}/members", response_model=schemas.ProjectMembershipOut, status_code=201)
def add_project_member(
    project_id: int,
    payload: schemas.ProjectMembershipCreate,
    current_user: models.User = Depends(auth.require_roles(*auth.MANAGEMENT_ROLES)),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if not db.get(models.User, payload.user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    existing = (
        db.query(models.ProjectMembership)
        .filter(models.ProjectMembership.project_id == project_id, models.ProjectMembership.user_id == payload.user_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="El usuario ya pertenece a este proyecto")
    membership = models.ProjectMembership(project_id=project_id, user_id=payload.user_id, role_in_project=payload.role_in_project)
    db.add(membership)
    db.flush()
    log_activity(
        db,
        project_id=project_id,
        event_type="MEMBER_ADDED",
        entity_type="PROJECT_MEMBERSHIP",
        entity_id=membership.id,
        new_state=payload.role_in_project,
    )
    db.commit()
    db.refresh(membership)
    return membership


@router.delete("/{project_id}/members/{user_id}", status_code=204)
def remove_project_member(
    project_id: int,
    user_id: int,
    current_user: models.User = Depends(auth.require_roles(*auth.MANAGEMENT_ROLES)),
    db: Session = Depends(get_db),
):
    membership = (
        db.query(models.ProjectMembership)
        .filter(models.ProjectMembership.project_id == project_id, models.ProjectMembership.user_id == user_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="El usuario no pertenece a este proyecto")
    db.delete(membership)
    db.commit()
    return None
