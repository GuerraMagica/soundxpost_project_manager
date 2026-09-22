"""Unified calendar API: merges real CalendarEvent rows with milestones that
live on other entities (Episode.mix_date, Episode.delivery_date, Task.due_date)
so there is never two conflicting dates for the same fact. Moving a mix/
delivery/task item via drag-and-drop calls the existing episodes/tasks
endpoints — this router only owns standalone events (ADR sessions, QC dates,
reconforms, custom production events).
"""
from __future__ import annotations

from datetime import datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.activity import log_activity
from app.database import get_db

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


def _as_datetime(d) -> datetime:
    return datetime.combine(d, time.min)


@router.get("/events", response_model=list[schemas.CalendarFeedItem])
def list_calendar_events(
    project_id: Optional[int] = None,
    project_ids: Optional[str] = None,  # comma-separated
    user_id: Optional[int] = None,
    event_type: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    project_id_list: list[int] = []
    if project_ids:
        project_id_list = [int(x) for x in project_ids.split(",") if x.strip()]
    elif project_id:
        project_id_list = [project_id]

    feed: list[schemas.CalendarFeedItem] = []

    # --- Mezclas y entregas: fuente de verdad = Episode ---------------------
    ep_query = db.query(models.Episode)
    if project_id_list:
        ep_query = ep_query.filter(models.Episode.project_id.in_(project_id_list))
    episodes = ep_query.all()

    for ep in episodes:
        if ep.mix_date and (not event_type or event_type == "MIX"):
            item_start = _as_datetime(ep.mix_date)
            if (not start or item_start >= start) and (not end or item_start <= end):
                feed.append(
                    schemas.CalendarFeedItem(
                        id=f"episode_mix:{ep.id}",
                        source="EPISODE_MIX",
                        source_id=ep.id,
                        project_id=ep.project_id,
                        episode_id=ep.id,
                        title=f"Mezcla — {ep.code}",
                        event_type="MIX",
                        start=item_start,
                        all_day=True,
                        status=ep.status,
                    )
                )
        if ep.delivery_date and (not event_type or event_type == "DELIVERY"):
            item_start = _as_datetime(ep.delivery_date)
            if (not start or item_start >= start) and (not end or item_start <= end):
                feed.append(
                    schemas.CalendarFeedItem(
                        id=f"episode_delivery:{ep.id}",
                        source="EPISODE_DELIVERY",
                        source_id=ep.id,
                        project_id=ep.project_id,
                        episode_id=ep.id,
                        title=f"Entrega — {ep.code}",
                        event_type="DELIVERY",
                        start=item_start,
                        all_day=True,
                        status=ep.status,
                    )
                )

    # --- Tareas con fecha límite ---------------------------------------------
    if not event_type or event_type == "TASK":
        task_query = db.query(models.Task).filter(models.Task.due_date.isnot(None))
        if project_id_list:
            task_query = task_query.filter(models.Task.project_id.in_(project_id_list))
        if user_id:
            task_query = task_query.filter(models.Task.assignee_id == user_id)
        for task in task_query.all():
            item_start = _as_datetime(task.due_date)
            if (not start or item_start >= start) and (not end or item_start <= end):
                feed.append(
                    schemas.CalendarFeedItem(
                        id=f"task:{task.id}",
                        source="TASK",
                        source_id=task.id,
                        project_id=task.project_id,
                        episode_id=task.episode_id,
                        title=task.title,
                        event_type="TASK",
                        start=item_start,
                        all_day=True,
                        responsible_user_id=task.assignee_id,
                        status=task.status,
                    )
                )

    # --- Eventos manuales (ADR_SESSION, QC, RECONFORM, CUSTOM) --------------
    ce_query = db.query(models.CalendarEvent)
    if project_id_list:
        ce_query = ce_query.filter(models.CalendarEvent.project_id.in_(project_id_list))
    if event_type:
        ce_query = ce_query.filter(models.CalendarEvent.event_type == event_type)
    if user_id:
        ce_query = ce_query.filter(models.CalendarEvent.responsible_user_id == user_id)
    if start:
        ce_query = ce_query.filter(models.CalendarEvent.start >= start)
    if end:
        ce_query = ce_query.filter(models.CalendarEvent.start <= end)
    for ev in ce_query.all():
        feed.append(
            schemas.CalendarFeedItem(
                id=f"calendar_event:{ev.id}",
                source="CALENDAR_EVENT",
                source_id=ev.id,
                project_id=ev.project_id,
                episode_id=ev.episode_id,
                title=ev.title,
                event_type=ev.event_type,
                start=ev.start,
                end=ev.end,
                all_day=ev.all_day,
                responsible_user_id=ev.responsible_user_id,
            )
        )

    return feed


@router.post("/events", response_model=schemas.CalendarEventOut, status_code=201)
def create_calendar_event(
    payload: schemas.CalendarEventCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    auth.ensure_project_access(db, current_user, payload.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear eventos")

    data = payload.model_dump()
    participant_ids = data.pop("participant_ids", [])
    event = models.CalendarEvent(**data, created_by_id=current_user.id, updated_by_id=current_user.id)
    if participant_ids:
        event.participants = db.query(models.User).filter(models.User.id.in_(participant_ids)).all()
    db.add(event)
    db.flush()
    log_activity(
        db,
        project_id=event.project_id,
        episode_id=event.episode_id,
        event_type="CALENDAR_EVENT_CREATED",
        entity_type="CALENDAR_EVENT",
        entity_id=event.id,
        actor=current_user.name,
        new_state=event.event_type,
    )
    db.commit()
    db.refresh(event)
    return event


@router.patch("/events/{event_id}", response_model=schemas.CalendarEventOut)
def update_calendar_event(
    event_id: int,
    payload: schemas.CalendarEventUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    event = db.get(models.CalendarEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    auth.ensure_project_access(db, current_user, event.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este evento")

    old_start = event.start
    updates = payload.model_dump(exclude_unset=True)
    participant_ids = updates.pop("participant_ids", None)
    for field, value in updates.items():
        setattr(event, field, value)
    if participant_ids is not None:
        event.participants = db.query(models.User).filter(models.User.id.in_(participant_ids)).all()
    event.updated_by_id = current_user.id
    db.flush()
    if payload.start and payload.start != old_start:
        log_activity(
            db,
            project_id=event.project_id,
            episode_id=event.episode_id,
            event_type="CALENDAR_EVENT_MOVED",
            entity_type="CALENDAR_EVENT",
            entity_id=event.id,
            actor=current_user.name,
            old_state=old_start.isoformat(),
            new_state=event.start.isoformat(),
        )
    db.commit()
    db.refresh(event)
    return event


@router.delete("/events/{event_id}", status_code=204)
def delete_calendar_event(
    event_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    event = db.get(models.CalendarEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    auth.ensure_project_access(db, current_user, event.project_id)
    if current_user.role not in auth.OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este evento")
    db.delete(event)
    db.commit()
    return None
