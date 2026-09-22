from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.activity import log_activity
from app.database import get_db

router = APIRouter(prefix="/api/archive", tags=["archive"])


@router.get("", response_model=list[schemas.ArchiveRecordOut])
def list_archive_records(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.ArchiveRecord)
    if project_id:
        query = query.filter(models.ArchiveRecord.project_id == project_id)
    return query.all()


@router.post("", response_model=schemas.ArchiveRecordOut, status_code=201)
def create_archive_record(payload: schemas.ArchiveRecordCreate, db: Session = Depends(get_db)):
    episode = db.get(models.Episode, payload.episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    record = models.ArchiveRecord(**payload.model_dump())
    db.add(record)
    db.flush()
    log_activity(
        db,
        project_id=record.project_id,
        episode_id=record.episode_id,
        event_type="ARCHIVE_RECORD_CREATED",
        entity_type="ARCHIVE_RECORD",
        entity_id=record.id,
    )
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{record_id}", response_model=schemas.ArchiveRecordOut)
def update_archive_record(record_id: int, payload: schemas.ArchiveRecordUpdate, db: Session = Depends(get_db)):
    record = db.get(models.ArchiveRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro de archivo no encontrado")

    updates = payload.model_dump(exclude_unset=True)
    # A human must explicitly confirm archive_verified; it is never inferred automatically.
    if updates.get("archive_verified") and not updates.get("verified_by") and not record.verified_by:
        raise HTTPException(
            status_code=400,
            detail="Se requiere 'verified_by' para marcar el archivo como verificado",
        )
    for field, value in updates.items():
        setattr(record, field, value)
    db.flush()
    if updates.get("archive_verified"):
        log_activity(
            db,
            project_id=record.project_id,
            episode_id=record.episode_id,
            event_type="ARCHIVE_VERIFIED",
            entity_type="ARCHIVE_RECORD",
            entity_id=record.id,
            new_state="VERIFIED",
            actor=record.verified_by,
        )
    db.commit()
    db.refresh(record)
    return record
