import { api, qs } from "./client";
import type {
  ADREntry,
  ActivityEntry,
  ArchiveRecord,
  DashboardSummary,
  DeliveryPackage,
  Episode,
  Output,
  Project,
  Risk,
  Task,
  User,
} from "../types";

export const projectsApi = {
  list: (status?: string) => api.get<Project[]>(`/api/projects${qs({ status_filter: status })}`),
  get: (id: number) => api.get<Project>(`/api/projects/${id}`),
  create: (payload: Partial<Project>) => api.post<Project>("/api/projects", payload),
  update: (id: number, payload: Partial<Project>) => api.patch<Project>(`/api/projects/${id}`, payload),
  episodes: (id: number) => api.get<Episode[]>(`/api/projects/${id}/episodes`),
};

export const episodesApi = {
  create: (payload: Partial<Episode> & { project_id: number; code: string }) =>
    api.post<Episode>("/api/episodes", payload),
  update: (id: number, payload: Partial<Episode>) => api.patch<Episode>(`/api/episodes/${id}`, payload),
};

export const tasksApi = {
  list: (filters: { project_id?: number; episode_id?: number; status_filter?: string } = {}) =>
    api.get<Task[]>(`/api/tasks${qs(filters)}`),
  create: (payload: Partial<Task> & { title: string; project_id: number }) =>
    api.post<Task>("/api/tasks", payload),
  update: (id: number, payload: Partial<Task>) => api.patch<Task>(`/api/tasks/${id}`, payload),
  remove: (id: number) => api.del<void>(`/api/tasks/${id}`),
};

export const adrApi = {
  list: (filters: { project_id?: number; episode_id?: number } = {}) =>
    api.get<ADREntry[]>(`/api/adr${qs(filters)}`),
  create: (payload: Partial<ADREntry> & { project_id: number; episode_id: number; character_name: string }) =>
    api.post<ADREntry>("/api/adr", payload),
  update: (id: number, payload: Partial<ADREntry>) => api.patch<ADREntry>(`/api/adr/${id}`, payload),
};

export const deliveryApi = {
  listOutputs: (filters: { project_id?: number; episode_id?: number } = {}) =>
    api.get<Output[]>(`/api/delivery/outputs${qs(filters)}`),
  createOutput: (payload: Partial<Output> & { project_id: number; episode_id: number; material_type: string }) =>
    api.post<Output>("/api/delivery/outputs", payload),
  updateOutput: (id: number, payload: Partial<Output>) => api.patch<Output>(`/api/delivery/outputs/${id}`, payload),
  listPackages: (filters: { project_id?: number; episode_id?: number } = {}) =>
    api.get<DeliveryPackage[]>(`/api/delivery/packages${qs(filters)}`),
  createPackage: (
    payload: Partial<DeliveryPackage> & { project_id: number; episode_id: number; material_type: string },
  ) => api.post<DeliveryPackage>("/api/delivery/packages", payload),
  updatePackage: (id: number, payload: Partial<DeliveryPackage>) =>
    api.patch<DeliveryPackage>(`/api/delivery/packages/${id}`, payload),
};

export const archiveApi = {
  list: (projectId?: number) => api.get<ArchiveRecord[]>(`/api/archive${qs({ project_id: projectId })}`),
  create: (payload: Partial<ArchiveRecord> & { project_id: number; episode_id: number }) =>
    api.post<ArchiveRecord>("/api/archive", payload),
  update: (id: number, payload: Partial<ArchiveRecord>) => api.patch<ArchiveRecord>(`/api/archive/${id}`, payload),
};

export const risksApi = {
  list: (filters: { project_id?: number; status_filter?: string; severity?: string } = {}) =>
    api.get<Risk[]>(`/api/risks${qs(filters)}`),
  run: () => api.post<{ created: number; updated: number; closed: number; evaluated: number }>("/api/risks/run"),
  updateStatus: (id: number, status: string) => api.patch<Risk>(`/api/risks/${id}`, { status }),
};

export const activityApi = {
  list: (projectId?: number, limit = 50) =>
    api.get<ActivityEntry[]>(`/api/activity${qs({ project_id: projectId, limit })}`),
};

export const usersApi = {
  list: () => api.get<User[]>("/api/users"),
};

export const dashboardApi = {
  summary: () => api.get<DashboardSummary>("/api/dashboard/summary"),
};
