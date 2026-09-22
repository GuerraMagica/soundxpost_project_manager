"""Small helper to append entries to the activity/event log."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app import models


def log_activity(
    db: Session,
    *,
    project_id: int,
    event_type: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    episode_id: Optional[int] = None,
    source: str = "APP",
    actor: Optional[str] = None,
    old_state: Optional[str] = None,
    new_state: Optional[str] = None,
    evidence_ref: Optional[str] = None,
) -> models.ActivityLog:
    entry = models.ActivityLog(
        project_id=project_id,
        episode_id=episode_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        source=source,
        actor=actor,
        old_state=old_state,
        new_state=new_state,
        evidence_ref=evidence_ref,
    )
    db.add(entry)
    db.flush()
    return entry
