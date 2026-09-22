"""Aggregated data for the 'Centro Operativo' dashboard."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    today = date.today()
    horizon = today + timedelta(days=7)

    open_risks = (
        db.query(models.Risk)
        .filter(models.Risk.status.notin_(["CLOSED"]))
        .order_by(models.Risk.severity)
        .all()
    )
    severity_order = {"CRITICAL": 0, "HIGH": 1, "WARNING": 2, "INFO": 3}
    open_risks.sort(key=lambda r: severity_order.get(r.severity, 9))

    upcoming_mixes = (
        db.query(models.Episode)
        .filter(models.Episode.mix_date.isnot(None))
        .filter(models.Episode.mix_date >= today)
        .filter(models.Episode.mix_date <= horizon)
        .order_by(models.Episode.mix_date)
        .all()
    )
    upcoming_deliveries = (
        db.query(models.Episode)
        .filter(models.Episode.delivery_date.isnot(None))
        .filter(models.Episode.delivery_date >= today)
        .filter(models.Episode.delivery_date <= horizon)
        .order_by(models.Episode.delivery_date)
        .all()
    )
    pending_tasks = (
        db.query(models.Task)
        .filter(models.Task.status.notin_(["FINALIZADO", "CANCELADO"]))
        .order_by(models.Task.due_date)
        .limit(20)
        .all()
    )
    recent_qc = (
        db.query(models.Output)
        .filter(models.Output.status.in_(["IN_QC", "QC_FAIL", "PASSED"]))
        .order_by(models.Output.updated_at.desc())
        .limit(10)
        .all()
    )
    pending_adr = (
        db.query(models.ADREntry)
        .filter(models.ADREntry.status.notin_(["FINALIZADO", "CANCELADO", "N/A"]))
        .order_by(models.ADREntry.updated_at.desc())
        .limit(10)
        .all()
    )
    recent_activity = db.query(models.ActivityLog).order_by(models.ActivityLog.created_at.desc()).limit(15).all()
    active_projects = db.query(models.Project).filter(models.Project.status == "ACTIVE").all()

    return {
        "risks": [schemas.RiskOut.model_validate(r) for r in open_risks],
        "upcoming_mixes": [schemas.EpisodeOut.model_validate(e) for e in upcoming_mixes],
        "upcoming_deliveries": [schemas.EpisodeOut.model_validate(e) for e in upcoming_deliveries],
        "pending_tasks": [schemas.TaskOut.model_validate(t) for t in pending_tasks],
        "recent_qc": [schemas.OutputOut.model_validate(o) for o in recent_qc],
        "pending_adr": [schemas.ADREntryOut.model_validate(a) for a in pending_adr],
        "recent_activity": [schemas.ActivityLogOut.model_validate(a) for a in recent_activity],
        "active_projects": [schemas.ProjectOut.model_validate(p) for p in active_projects],
    }
