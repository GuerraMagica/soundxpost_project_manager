"""SQLAlchemy ORM models for SOUND X-POST.

All status/severity fields are stored as plain strings (not native SQL enums)
so that the value sets documented in the product spec can evolve without a
schema migration. Validation of allowed values happens in the Pydantic
schemas / API layer.
"""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Many-to-many: additional collaborators on a task, distinct from the single
# principal `assignee_id` on Task.
task_collaborators = Table(
    "task_collaborators",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)

# Many-to-many: participants confirmed on a manually-created calendar event.
event_participants = Table(
    "event_participants",
    Base.metadata,
    Column("event_id", ForeignKey("calendar_events.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    role: Mapped[str] = mapped_column(String(40))  # ADMIN, SUPERVISOR, COORDINATOR, EDITOR, MIXER, QC, ARCHIVE, VIEWER
    department: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    memberships: Mapped[list["ProjectMembership"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class ProjectMembership(Base):
    """A user's participation in a project — distinct from a single task assignment.

    A user can belong to several projects at once (e.g. a supervisor across
    shows, an editor across two episodes of the same project).
    """

    __tablename__ = "project_memberships"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role_in_project: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(back_populates="memberships")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    code: Mapped[str] = mapped_column(String(40), unique=True)
    project_type: Mapped[str] = mapped_column(String(40))  # SERIES, FEATURE_FILM, DOCUMENTARY, COMMERCIAL, PROMOTIONAL, REGIONAL_VERSION, TECHNICAL_ADAPTATION
    client_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    delivery_platform: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="ACTIVE")  # ACTIVE, ARCHIVED, ON_HOLD
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    authorized_paths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    episodes: Mapped[list["Episode"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    memberships: Mapped[list["ProjectMembership"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    code: Mapped[str] = mapped_column(String(40))  # e.g. S01E01, E101, FILM
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    mix_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="IN_PROGRESS")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)

    project: Mapped["Project"] = relationship(back_populates="episodes")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    episode_id: Mapped[Optional[int]] = mapped_column(ForeignKey("episodes.id"), nullable=True)
    discipline: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="PENDIENTE")
    priority: Mapped[str] = mapped_column(String(20), default="NORMAL")  # LOW, NORMAL, HIGH, URGENT
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    depends_on_task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    evidence_ref: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    origin_risk_id: Mapped[Optional[int]] = mapped_column(ForeignKey("risks.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)

    project: Mapped["Project"] = relationship(back_populates="tasks")
    episode: Mapped[Optional["Episode"]] = relationship()
    assignee: Mapped[Optional["User"]] = relationship(foreign_keys=[assignee_id])
    collaborators: Mapped[list["User"]] = relationship(secondary=task_collaborators)

    @property
    def collaborator_ids(self) -> list[int]:
        return [u.id for u in self.collaborators]


class CalendarEvent(Base):
    """A manually-created production event (ADR session, QC date, reconform, etc.).

    Scheduling milestones that already live on other entities (mix date on
    Episode, delivery date on Episode, due date on Task) are NOT duplicated
    here — the calendar API merges those directly from their source of
    truth so there is never a second, possibly stale, date for the same
    fact. This table only stores events that have no other home.
    """

    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    episode_id: Mapped[Optional[int]] = mapped_column(ForeignKey("episodes.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    event_type: Mapped[str] = mapped_column(String(40))  # ADR_SESSION, QC, RECONFORM, CUSTOM
    start: Mapped[datetime] = mapped_column(DateTime)
    end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    timezone: Mapped[str] = mapped_column(String(60), default="Europe/Madrid")
    responsible_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    related_task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    related_output_id: Mapped[Optional[int]] = mapped_column(ForeignKey("outputs.id"), nullable=True)
    created_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)

    project: Mapped["Project"] = relationship()
    episode: Mapped[Optional["Episode"]] = relationship()
    responsible_user: Mapped[Optional["User"]] = relationship(foreign_keys=[responsible_user_id])
    participants: Mapped[list["User"]] = relationship(secondary=event_participants)

    @property
    def participant_ids(self) -> list[int]:
        return [u.id for u in self.participants]


class ADREntry(Base):
    """Tracking unit: PROJECT + EPISODE + CHARACTER + CONVOCATORIA (not per-cue)."""

    __tablename__ = "adr_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    episode_id: Mapped[int] = mapped_column(ForeignKey("episodes.id"))
    character_name: Mapped[str] = mapped_column(String(150))
    actor_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    convocatoria: Mapped[int] = mapped_column(Integer, default=1)
    total_cues: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    add_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    tbw_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(40), default="PENDIENTE")
    source: Mapped[str] = mapped_column(String(40), default="MANUAL")  # MANUAL, PGPTSESSION_IMPORT
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project: Mapped["Project"] = relationship()
    episode: Mapped["Episode"] = relationship()


class Output(Base):
    """A deliverable master/stem and its QC lifecycle (PM_VO 5.1, MNE, stems, etc.)."""

    __tablename__ = "outputs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    episode_id: Mapped[int] = mapped_column(ForeignKey("episodes.id"))
    material_type: Mapped[str] = mapped_column(String(80))  # PM_VO_5_1, MNE_2_0, DX_STEM, ...
    version: Mapped[str] = mapped_column(String(20), default="V01")
    status: Mapped[str] = mapped_column(
        String(20), default="NOT_STARTED"
    )  # NOT_STARTED, WIP, OUTPUT_READY, IN_QC, QC_FAIL, PASSED, N_A
    qc_round: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project: Mapped["Project"] = relationship()
    episode: Mapped["Episode"] = relationship()


class DeliveryPackage(Base):
    __tablename__ = "delivery_packages"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    episode_id: Mapped[int] = mapped_column(ForeignKey("episodes.id"))
    material_type: Mapped[str] = mapped_column(String(80))
    version: Mapped[str] = mapped_column(String(20), default="V01")
    status: Mapped[str] = mapped_column(
        String(20), default="PENDING"
    )  # PENDING, BUILDING, READY, FINAL, DELIVERED, N_A
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project: Mapped["Project"] = relationship()
    episode: Mapped["Episode"] = relationship()


class ArchiveRecord(Base):
    __tablename__ = "archive_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    episode_id: Mapped[int] = mapped_column(ForeignKey("episodes.id"))
    pt_session: Mapped[str] = mapped_column(String(20), default="PENDIENTE")
    pm: Mapped[str] = mapped_column(String(20), default="PENDIENTE")
    mne: Mapped[str] = mapped_column(String(20), default="PENDIENTE")
    stems: Mapped[str] = mapped_column(String(20), default="PENDIENTE")
    cuesheet: Mapped[str] = mapped_column(String(20), default="PENDIENTE")
    qc_docs: Mapped[str] = mapped_column(String(20), default="PENDIENTE")
    dubbing_ad: Mapped[str] = mapped_column(String(20), default="N_A")
    archive_path: Mapped[Optional[str]] = mapped_column(String(400), nullable=True)
    lto_id: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    verified_by: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    verified_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    archive_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project: Mapped["Project"] = relationship()
    episode: Mapped["Episode"] = relationship()


class Risk(Base):
    __tablename__ = "risks"

    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[str] = mapped_column(String(80))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    episode_id: Mapped[Optional[int]] = mapped_column(ForeignKey("episodes.id"), nullable=True)
    severity: Mapped[str] = mapped_column(String(20))  # INFO, WARNING, HIGH, CRITICAL
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str] = mapped_column(Text)
    suggested_action: Mapped[str] = mapped_column(Text)
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), default="DETECTED"
    )  # DETECTED, ACKNOWLEDGED, IN_PROGRESS, RESOLVED_PENDING_VERIFICATION, CLOSED
    dedupe_key: Mapped[str] = mapped_column(String(300), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project: Mapped["Project"] = relationship()
    episode: Mapped[Optional["Episode"]] = relationship()
    owner: Mapped[Optional["User"]] = relationship()


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    episode_id: Mapped[Optional[int]] = mapped_column(ForeignKey("episodes.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str] = mapped_column(String(40))
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(40), default="APP")  # APP, RISK_ENGINE, DEMO_SEED
    actor: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    old_state: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    new_state: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    evidence_ref: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship()
    episode: Mapped[Optional["Episode"]] = relationship()
