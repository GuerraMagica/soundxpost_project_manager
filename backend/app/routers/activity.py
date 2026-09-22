from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("", response_model=list[schemas.ActivityLogOut])
def list_activity(
    project_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(models.ActivityLog)
    if project_id:
        query = query.filter(models.ActivityLog.project_id == project_id)
    return query.order_by(models.ActivityLog.created_at.desc()).limit(limit).all()
