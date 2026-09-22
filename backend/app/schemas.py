"""Pydantic schemas (API request/response contracts)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------- Users ----
class UserOut(ORMModel):
    id: int
    name: str
    email: str
    role: str
    department: Optional[str] = None
    is_active: bool
    is_demo: bool


class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    department: Optional[str] = None
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProjectMembershipBase(BaseModel):
    user_id: int
    role_in_project: Optional[str] = None


class ProjectMembershipCreate(ProjectMembershipBase):
    pass


class ProjectMembershipOut(ProjectMembershipBase):
    id: int
    project_id: int
    created_at: datetime
    user: UserOut

    model_config = ConfigDict(from_attributes=True)



# ------------------------------------------------------------- Projects ----
class ProjectBase(BaseModel):
    name: str
    code: str
    project_type: str
    client_name: Optional[str] = None
    delivery_platform: Optional[str] = None
    status: str = "ACTIVE"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    authorized_paths: Optional[str] = None
    notes: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client_name: Optional[str] = None
    delivery_platform: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    authorized_paths: Optional[str] = None
    notes: Optional[str] = None


class ProjectOut(ProjectBase):
    id: int
    is_demo: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------- Episodes ----
class EpisodeBase(BaseModel):
    code: str
    title: Optional[str] = None
    order_index: int = 0
    mix_date: Optional[date] = None
    delivery_date: Optional[date] = None
    status: str = "IN_PROGRESS"


class EpisodeCreate(EpisodeBase):
    project_id: int


class EpisodeUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = None
    order_index: Optional[int] = None
    mix_date: Optional[date] = None
    delivery_date: Optional[date] = None
    status: Optional[str] = None


class EpisodeOut(EpisodeBase):
    id: int
    project_id: int
    is_demo: bool

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------- Tasks ----
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: int
    episode_id: Optional[int] = None
    discipline: Optional[str] = None
    assignee_id: Optional[int] = None
    status: str = "PENDIENTE"
    priority: str = "NORMAL"
    due_date: Optional[date] = None
    depends_on_task_id: Optional[int] = None
    evidence_ref: Optional[str] = None


class TaskCreate(TaskBase):
    collaborator_ids: list[int] = []


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    episode_id: Optional[int] = None
    discipline: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    depends_on_task_id: Optional[int] = None
    evidence_ref: Optional[str] = None
    collaborator_ids: Optional[list[int]] = None


class TaskOut(TaskBase):
    id: int
    origin_risk_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    collaborator_ids: list[int] = []

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------- ADR entries ----
class ADREntryBase(BaseModel):
    project_id: int
    episode_id: int
    character_name: str
    actor_name: Optional[str] = None
    convocatoria: int = 1
    total_cues: Optional[int] = None
    add_flag: bool = False
    tbw_flag: bool = False
    status: str = "PENDIENTE"


class ADREntryCreate(ADREntryBase):
    pass


class ADREntryUpdate(BaseModel):
    actor_name: Optional[str] = None
    total_cues: Optional[int] = None
    add_flag: Optional[bool] = None
    tbw_flag: Optional[bool] = None
    status: Optional[str] = None


class ADREntryOut(ADREntryBase):
    id: int
    source: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------- Output ----
class OutputBase(BaseModel):
    project_id: int
    episode_id: int
    material_type: str
    version: str = "V01"
    status: str = "NOT_STARTED"
    qc_round: int = 0
    notes: Optional[str] = None


class OutputCreate(OutputBase):
    pass


class OutputUpdate(BaseModel):
    version: Optional[str] = None
    status: Optional[str] = None
    qc_round: Optional[int] = None
    notes: Optional[str] = None


class OutputOut(OutputBase):
    id: int
    approved_at: Optional[datetime] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------- Delivery package ----
class DeliveryPackageBase(BaseModel):
    project_id: int
    episode_id: int
    material_type: str
    version: str = "V01"
    status: str = "PENDING"
    notes: Optional[str] = None


class DeliveryPackageCreate(DeliveryPackageBase):
    pass


class DeliveryPackageUpdate(BaseModel):
    version: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class DeliveryPackageOut(DeliveryPackageBase):
    id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------- Archive record ----
class ArchiveRecordBase(BaseModel):
    project_id: int
    episode_id: int
    pt_session: str = "PENDIENTE"
    pm: str = "PENDIENTE"
    mne: str = "PENDIENTE"
    stems: str = "PENDIENTE"
    cuesheet: str = "PENDIENTE"
    qc_docs: str = "PENDIENTE"
    dubbing_ad: str = "N_A"
    archive_path: Optional[str] = None
    lto_id: Optional[str] = None
    notes: Optional[str] = None


class ArchiveRecordCreate(ArchiveRecordBase):
    pass


class ArchiveRecordUpdate(BaseModel):
    pt_session: Optional[str] = None
    pm: Optional[str] = None
    mne: Optional[str] = None
    stems: Optional[str] = None
    cuesheet: Optional[str] = None
    qc_docs: Optional[str] = None
    dubbing_ad: Optional[str] = None
    archive_path: Optional[str] = None
    lto_id: Optional[str] = None
    verified_by: Optional[str] = None
    verified_date: Optional[date] = None
    archive_verified: Optional[bool] = None
    notes: Optional[str] = None


class ArchiveRecordOut(ArchiveRecordBase):
    id: int
    verified_by: Optional[str] = None
    verified_date: Optional[date] = None
    archive_verified: bool
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------- Risks ----
class RiskOut(ORMModel):
    id: int
    rule_id: str
    project_id: int
    episode_id: Optional[int] = None
    severity: str
    title: str
    description: str
    evidence: str
    suggested_action: str
    owner_id: Optional[int] = None
    due_date: Optional[date] = None
    status: str
    created_at: datetime
    updated_at: datetime


class RiskStatusUpdate(BaseModel):
    status: str


# ------------------------------------------------------------- Activity ----
class ActivityLogOut(ORMModel):
    id: int
    project_id: int
    episode_id: Optional[int] = None
    event_type: str
    entity_type: str
    entity_id: Optional[int] = None
    source: str
    actor: Optional[str] = None
    old_state: Optional[str] = None
    new_state: Optional[str] = None
    evidence_ref: Optional[str] = None
    created_at: datetime


# --------------------------------------------------------------- Calendar ----
class CalendarEventBase(BaseModel):
    project_id: int
    episode_id: Optional[int] = None
    title: str
    event_type: str = "CUSTOM"  # ADR_SESSION, QC, RECONFORM, CUSTOM
    start: datetime
    end: Optional[datetime] = None
    all_day: bool = False
    timezone: str = "Europe/Madrid"
    responsible_user_id: Optional[int] = None
    description: Optional[str] = None
    related_task_id: Optional[int] = None
    related_output_id: Optional[int] = None


class CalendarEventCreate(CalendarEventBase):
    participant_ids: list[int] = []


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    event_type: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    all_day: Optional[bool] = None
    responsible_user_id: Optional[int] = None
    description: Optional[str] = None
    participant_ids: Optional[list[int]] = None


class CalendarEventOut(CalendarEventBase):
    id: int
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    participant_ids: list[int] = []

    model_config = ConfigDict(from_attributes=True)


class CalendarFeedItem(BaseModel):
    """A unified, read-model item merging real CalendarEvents with milestones
    that live on other entities (episode mix/delivery dates, task due dates).
    `source` + `source_id` tell the frontend which API to call to move/edit it.
    """

    id: str
    source: str  # CALENDAR_EVENT, EPISODE_MIX, EPISODE_DELIVERY, TASK
    source_id: int
    project_id: int
    episode_id: Optional[int] = None
    title: str
    event_type: str
    start: datetime
    end: Optional[datetime] = None
    all_day: bool = False
    responsible_user_id: Optional[int] = None
    status: Optional[str] = None
    editable: bool = True
