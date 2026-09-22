from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.activity import log_activity
from app.database import get_db

router = APIRouter(prefix="/api/archive", tags=["archive"])


@router.get("", response_model=list[schemas.ArchiveRecordOut])
def list_archive_records(
    project_id: Optional[int] = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.ArchiveRecord)
    if project_id:
        query = query.filter(models.ArchiveRecord.project_id == project_id)
    return query.all()


@router.post("", response_model=schemas.ArchiveRecordOut, status_code=201)
def create_archive_record(
    payload: schemas.ArchiveRecordCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    episode = db.get(models.Episode, payload.episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    auth.ensure_project_access(db, current_user, payload.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear registros de archivo")
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
def update_archive_record(
    record_id: int,
    payload: schemas.ArchiveRecordUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    record = db.get(models.ArchiveRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro de archivo no encontrado")
    auth.ensure_project_access(db, current_user, record.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este registro de archivo")

    updates = payload.model_dump(exclude_unset=True)
    # A human must explicitly confirm archive_verified; it is never inferred automatically.
    if updates.get("archive_verified"):
        if current_user.role not in (auth.MANAGEMENT_ROLES | {"ARCHIVE"}):
            raise HTTPException(status_code=403, detail="Solo archivo/coordinación puede verificar el archivo")
        if not updates.get("verified_by") and not record.verified_by:
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
