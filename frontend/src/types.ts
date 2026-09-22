export type ProjectType =
  | "SERIES"
  | "FEATURE_FILM"
  | "DOCUMENTARY"
  | "COMMERCIAL"
  | "PROMOTIONAL"
  | "REGIONAL_VERSION"
  | "TECHNICAL_ADAPTATION";

export interface Project {
  id: number;
  name: string;
  code: string;
  project_type: ProjectType;
  client_name: string | null;
  delivery_platform: string | null;
  status: string;
  start_date: string | null;
  end_date: string | null;
  authorized_paths: string | null;
  notes: string | null;
  is_demo: boolean;
  created_at: string;
}

export interface Episode {
  id: number;
  project_id: number;
  code: string;
  title: string | null;
  order_index: number;
  mix_date: string | null;
  delivery_date: string | null;
  status: string;
  is_demo: boolean;
}

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  department: string | null;
  is_active: boolean;
  is_demo: boolean;
}

export interface ProjectMembership {
  id: number;
  project_id: number;
  user_id: number;
  role_in_project: string | null;
  created_at: string;
  user: User;
}

export interface Task {
  id: number;
  title: string;
  description: string | null;
  project_id: number;
  episode_id: number | null;
  discipline: string | null;
  assignee_id: number | null;
  status: string;
  priority: string;
  due_date: string | null;
  depends_on_task_id: number | null;
  evidence_ref: string | null;
  origin_risk_id: number | null;
  created_at: string;
  resolved_at: string | null;
  collaborator_ids: number[];
}

export interface ADREntry {
  id: number;
  project_id: number;
  episode_id: number;
  character_name: string;
  actor_name: string | null;
  convocatoria: number;
  total_cues: number | null;
  add_flag: boolean;
  tbw_flag: boolean;
  status: string;
  source: string;
  updated_at: string;
}

export interface Output {
  id: number;
  project_id: number;
  episode_id: number;
  material_type: string;
  version: string;
  status: string;
  qc_round: number;
  notes: string | null;
  approved_at: string | null;
  updated_at: string;
}

export interface DeliveryPackage {
  id: number;
  project_id: number;
  episode_id: number;
  material_type: string;
  version: string;
  status: string;
  notes: string | null;
  updated_at: string;
}

export interface ArchiveRecord {
  id: number;
  project_id: number;
  episode_id: number;
  pt_session: string;
  pm: string;
  mne: string;
  stems: string;
  cuesheet: string;
  qc_docs: string;
  dubbing_ad: string;
  archive_path: string | null;
  lto_id: string | null;
  verified_by: string | null;
  verified_date: string | null;
  archive_verified: boolean;
  notes: string | null;
  updated_at: string;
}

export interface Risk {
  id: number;
  rule_id: string;
  project_id: number;
  episode_id: number | null;
  severity: "INFO" | "WARNING" | "HIGH" | "CRITICAL";
  title: string;
  description: string;
  evidence: string;
  suggested_action: string;
  owner_id: number | null;
  due_date: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ActivityEntry {
  id: number;
  project_id: number;
  episode_id: number | null;
  event_type: string;
  entity_type: string;
  entity_id: number | null;
  source: string;
  actor: string | null;
  old_state: string | null;
  new_state: string | null;
  evidence_ref: string | null;
  created_at: string;
}

export interface DashboardSummary {
  risks: Risk[];
  upcoming_mixes: Episode[];
  upcoming_deliveries: Episode[];
  pending_tasks: Task[];
  recent_qc: Output[];
  pending_adr: ADREntry[];
  recent_activity: ActivityEntry[];
  active_projects: Project[];
}

export type CalendarSource = "CALENDAR_EVENT" | "EPISODE_MIX" | "EPISODE_DELIVERY" | "TASK";

export interface CalendarFeedItem {
  id: string;
  source: CalendarSource;
  source_id: number;
  project_id: number;
  episode_id: number | null;
  title: string;
  event_type: string;
  start: string;
  end: string | null;
  all_day: boolean;
  responsible_user_id: number | null;
  status: string | null;
  editable: boolean;
}

export interface CalendarEventPayload {
  project_id: number;
  episode_id?: number | null;
  title: string;
  event_type: string;
  start: string;
  end?: string | null;
  all_day?: boolean;
  responsible_user_id?: number | null;
  description?: string | null;
  participant_ids?: number[];
}
