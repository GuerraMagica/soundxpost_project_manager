from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.activity import log_activity
from app.database import get_db

router = APIRouter(prefix="/api/delivery", tags=["delivery"])


@router.get("/outputs", response_model=list[schemas.OutputOut])
def list_outputs(
    project_id: Optional[int] = None,
    episode_id: Optional[int] = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Output)
    if project_id:
        query = query.filter(models.Output.project_id == project_id)
    if episode_id:
        query = query.filter(models.Output.episode_id == episode_id)
    return query.order_by(models.Output.material_type).all()


@router.post("/outputs", response_model=schemas.OutputOut, status_code=201)
def create_output(
    payload: schemas.OutputCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    episode = db.get(models.Episode, payload.episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    auth.ensure_project_access(db, current_user, payload.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para registrar outputs")
    output = models.Output(**payload.model_dump())
    db.add(output)
    db.flush()
    log_activity(
        db,
        project_id=output.project_id,
        episode_id=output.episode_id,
        event_type="OUTPUT_REGISTERED",
        entity_type="OUTPUT",
        entity_id=output.id,
        new_state=output.status,
    )
    db.commit()
    db.refresh(output)
    return output


@router.patch("/outputs/{output_id}", response_model=schemas.OutputOut)
def update_output(
    output_id: int,
    payload: schemas.OutputUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import datetime

    output = db.get(models.Output, output_id)
    if not output:
        raise HTTPException(status_code=404, detail="Output no encontrado")
    auth.ensure_project_access(db, current_user, output.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este output")
    old_status = output.status
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(output, field, value)
    if payload.status == "PASSED" and old_status != "PASSED":
        output.approved_at = datetime.utcnow()
    db.flush()
    if payload.status and payload.status != old_status:
        log_activity(
            db,
            project_id=output.project_id,
            episode_id=output.episode_id,
            event_type="OUTPUT_STATUS_CHANGED",
            entity_type="OUTPUT",
            entity_id=output.id,
            old_state=old_status,
            new_state=output.status,
        )
        if output.status == "PASSED":
            log_activity(
                db,
                project_id=output.project_id,
                episode_id=output.episode_id,
                event_type="QC_CLOSED_PASSED",
                entity_type="OUTPUT",
                entity_id=output.id,
                new_state="PASSED",
            )
    db.commit()
    db.refresh(output)
    return output


@router.get("/packages", response_model=list[schemas.DeliveryPackageOut])
def list_delivery_packages(
    project_id: Optional[int] = None,
    episode_id: Optional[int] = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.DeliveryPackage)
    if project_id:
        query = query.filter(models.DeliveryPackage.project_id == project_id)
    if episode_id:
        query = query.filter(models.DeliveryPackage.episode_id == episode_id)
    return query.order_by(models.DeliveryPackage.material_type).all()


@router.post("/packages", response_model=schemas.DeliveryPackageOut, status_code=201)
def create_delivery_package(
    payload: schemas.DeliveryPackageCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    episode = db.get(models.Episode, payload.episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")
    auth.ensure_project_access(db, current_user, payload.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para registrar delivery packages")
    package = models.DeliveryPackage(**payload.model_dump())
    db.add(package)
    db.flush()
    log_activity(
        db,
        project_id=package.project_id,
        episode_id=package.episode_id,
        event_type="DELIVERY_PACKAGE_CREATED",
        entity_type="DELIVERY_PACKAGE",
        entity_id=package.id,
        new_state=package.status,
    )
    db.commit()
    db.refresh(package)
    return package


@router.patch("/packages/{package_id}", response_model=schemas.DeliveryPackageOut)
def update_delivery_package(
    package_id: int,
    payload: schemas.DeliveryPackageUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    package = db.get(models.DeliveryPackage, package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Delivery Package no encontrado")
    auth.ensure_project_access(db, current_user, package.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este delivery package")
    old_status = package.status
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(package, field, value)
    db.flush()
    if payload.status and payload.status != old_status:
        log_activity(
            db,
            project_id=package.project_id,
            episode_id=package.episode_id,
            event_type="DELIVERY_STATUS_CHANGED",
            entity_type="DELIVERY_PACKAGE",
            entity_id=package.id,
            old_state=old_status,
            new_state=package.status,
        )
    db.commit()
    db.refresh(package)
    return package
