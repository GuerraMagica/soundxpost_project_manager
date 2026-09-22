from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.activity import log_activity
from app.database import get_db

router = APIRouter(prefix="/api/episodes", tags=["episodes"])


@router.post("", response_model=schemas.EpisodeOut, status_code=201)
def create_episode(
    payload: schemas.EpisodeCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    auth.ensure_project_access(db, current_user, payload.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear episodios")
    episode = models.Episode(**payload.model_dump())
    db.add(episode)
    db.flush()
    log_activity(
        db,
        project_id=project.id,
        episode_id=episode.id,
        event_type="EPISODE_CREATED",
        entity_type="EPISODE",
        entity_id=episode.id,
    )
    db.commit()
    db.refresh(episode)
    return episode


@router.get("/{episode_id}", response_model=schemas.EpisodeOut)
def get_episode(
    episode_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    episode = db.get(models.Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    return episode


@router.patch("/{episode_id}", response_model=schemas.EpisodeOut)
def update_episode(
    episode_id: int,
    payload: schemas.EpisodeUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    episode = db.get(models.Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    auth.ensure_project_access(db, current_user, episode.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este episodio")
    old_status = episode.status
    old_mix_date = episode.mix_date
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(episode, field, value)
    db.flush()
    if payload.status and payload.status != old_status:
        log_activity(
            db,
            project_id=episode.project_id,
            episode_id=episode.id,
            event_type="EPISODE_STATUS_CHANGED",
            entity_type="EPISODE",
            entity_id=episode.id,
            old_state=old_status,
            new_state=episode.status,
        )
    if payload.mix_date and payload.mix_date != old_mix_date:
        log_activity(
            db,
            project_id=episode.project_id,
            episode_id=episode.id,
            event_type="MIX_DATE_CHANGED",
            entity_type="EPISODE",
            entity_id=episode.id,
            old_state=str(old_mix_date) if old_mix_date else None,
            new_state=str(episode.mix_date),
        )
    db.commit()
    db.refresh(episode)
    return episode
