from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.activity import log_activity
from app.database import get_db
from app.risk_engine.rules import run_risk_engine

router = APIRouter(prefix="/api/risks", tags=["risks"])


@router.get("", response_model=list[schemas.RiskOut])
def list_risks(
    project_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Risk)
    if project_id:
        query = query.filter(models.Risk.project_id == project_id)
    if status_filter:
        query = query.filter(models.Risk.status == status_filter)
    else:
        query = query.filter(models.Risk.status != "CLOSED")
    if severity:
        query = query.filter(models.Risk.severity == severity)
    severity_order = {"CRITICAL": 0, "HIGH": 1, "WARNING": 2, "INFO": 3}
    risks = query.all()
    risks.sort(key=lambda r: severity_order.get(r.severity, 9))
    return risks


@router.post("/run", status_code=200)
def trigger_risk_engine(db: Session = Depends(get_db)):
    """Manually re-evaluate all risk rules (idempotent)."""
    return run_risk_engine(db)


@router.patch("/{risk_id}", response_model=schemas.RiskOut)
def update_risk_status(risk_id: int, payload: schemas.RiskStatusUpdate, db: Session = Depends(get_db)):
    risk = db.get(models.Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Riesgo no encontrado")
    old_status = risk.status
    risk.status = payload.status
    db.flush()
    log_activity(
        db,
        project_id=risk.project_id,
        episode_id=risk.episode_id,
        event_type="RISK_STATUS_CHANGED",
        entity_type="RISK",
        entity_id=risk.id,
        old_state=old_status,
        new_state=risk.status,
    )
    db.commit()
    db.refresh(risk)
    return risk
