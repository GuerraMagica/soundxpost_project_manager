from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.activity import log_activity
from app.database import get_db

router = APIRouter(prefix="/api/adr", tags=["adr"])


@router.get("", response_model=list[schemas.ADREntryOut])
def list_adr_entries(
    project_id: Optional[int] = None,
    episode_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.ADREntry)
    if project_id:
        query = query.filter(models.ADREntry.project_id == project_id)
    if episode_id:
        query = query.filter(models.ADREntry.episode_id == episode_id)
    return query.order_by(models.ADREntry.character_name, models.ADREntry.convocatoria).all()


@router.post("", response_model=schemas.ADREntryOut, status_code=201)
def create_adr_entry(payload: schemas.ADREntryCreate, db: Session = Depends(get_db)):
    episode = db.get(models.Episode, payload.episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    entry = models.ADREntry(**payload.model_dump())
    db.add(entry)
    db.flush()
    log_activity(
        db,
        project_id=entry.project_id,
        episode_id=entry.episode_id,
        event_type="ADR_ENTRY_CREATED",
        entity_type="ADR_ENTRY",
        entity_id=entry.id,
        new_state=entry.status,
    )
    db.commit()
    db.refresh(entry)
    return entry


@router.patch("/{entry_id}", response_model=schemas.ADREntryOut)
def update_adr_entry(entry_id: int, payload: schemas.ADREntryUpdate, db: Session = Depends(get_db)):
    entry = db.get(models.ADREntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Convocatoria ADR no encontrada")
    old_status = entry.status
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.flush()
    if payload.status and payload.status != old_status:
        log_activity(
            db,
            project_id=entry.project_id,
            episode_id=entry.episode_id,
            event_type="ADR_STATUS_CHANGED",
            entity_type="ADR_ENTRY",
            entity_id=entry.id,
            old_state=old_status,
            new_state=entry.status,
        )
    db.commit()
    db.refresh(entry)
    return entry
