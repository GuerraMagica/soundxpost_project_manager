import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { projectsApi, tasksApi } from "../api/endpoints";
import { EmptyState, ErrorState, Spinner } from "../components/Common";
import { PriorityDot, StatusBadge } from "../components/Badges";
import type { Task } from "../types";

const TASK_STATUSES = ["PENDIENTE", "EN PROGRESO", "BLOQUEADO", "EN REVISIÓN", "FINALIZADO", "CANCELADO"];
type ViewMode = "LISTA" | "BOARD" | "CALENDARIO";

export function TasksPage() {
  const [view, setView] = useState<ViewMode>("LISTA");
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: () => projectsApi.list() });
  const [projectFilter, setProjectFilter] = useState<number | "">("");

  const { data: tasks, isLoading, isError } = useQuery({
    queryKey: ["tasks", "all", projectFilter],
    queryFn: () => tasksApi.list(projectFilter === "" ? {} : { project_id: projectFilter }),
  });
  const queryClient = useQueryClient();
  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => tasksApi.update(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasks", "all"] }),
  });

  const projectName = (id: number) => projects?.find((p) => p.id === id)?.name ?? `#${id}`;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <select value={projectFilter} onChange={(e) => setProjectFilter(e.target.value ? Number(e.target.value) : "")} className="rounded-md border border-slate-300 px-2 py-1.5 text-sm">
          <option value="">Todos los proyectos</option>
          {projects?.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <div className="flex gap-1 rounded-md border border-slate-200 bg-white p-1">
          {(["LISTA", "BOARD", "CALENDARIO"] as ViewMode[]).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`rounded px-3 py-1 text-xs font-medium ${view === v ? "bg-brand-600 text-white" : "text-slate-500 hover:bg-slate-100"}`}
            >
              {v}
            </button>
          ))}
        </div>
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorState message="No se han podido cargar las tareas." />}
      {tasks && tasks.length === 0 && <EmptyState message="No hay tareas registradas." />}

      {tasks && tasks.length > 0 && view === "LISTA" && (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
              <th className="py-2">Título</th><th>Proyecto</th><th>Prioridad</th><th>Fecha límite</th><th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.id} className="border-b border-slate-100">
                <td className="py-2">{task.title}</td>
                <td className="text-slate-500">{projectName(task.project_id)}</td>
                <td><PriorityDot priority={task.priority} /></td>
                <td className="text-slate-500">{task.due_date ?? "—"}</td>
                <td>
                  <select value={task.status} onChange={(e) => updateStatus.mutate({ id: task.id, status: e.target.value })} className="rounded-md border border-slate-300 px-2 py-1 text-xs">
                    {TASK_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {tasks && tasks.length > 0 && view === "BOARD" && (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
          {TASK_STATUSES.map((status) => (
            <div key={status} className="rounded-lg bg-slate-100 p-2">
              <div className="mb-2 text-xs font-semibold text-slate-500">{status} ({tasks.filter((t) => t.status === status).length})</div>
              <div className="space-y-2">
                {tasks.filter((t) => t.status === status).map((task) => (
                  <div key={task.id} className="rounded-md border border-slate-200 bg-white p-2 shadow-sm">
                    <div className="text-xs font-medium text-slate-800">{task.title}</div>
                    <div className="mt-1 text-[11px] text-slate-400">{projectName(task.project_id)}</div>
                    <select
                      value={task.status}
                      onChange={(e) => updateStatus.mutate({ id: task.id, status: e.target.value })}
                      className="mt-1 w-full rounded border border-slate-200 text-[11px]"
                    >
                      {TASK_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {tasks && tasks.length > 0 && view === "CALENDARIO" && <TaskCalendar tasks={tasks} projectName={projectName} />}
    </div>
  );
}

function TaskCalendar({ tasks, projectName }: { tasks: Task[]; projectName: (id: number) => string }) {
  const withDates = tasks.filter((t) => t.due_date).sort((a, b) => (a.due_date! < b.due_date! ? -1 : 1));
  const byDate = new Map<string, Task[]>();
  for (const t of withDates) {
    const list = byDate.get(t.due_date!) ?? [];
    list.push(t);
    byDate.set(t.due_date!, list);
  }
  if (byDate.size === 0) return <EmptyState message="Ninguna tarea tiene fecha límite asignada." />;
  return (
    <div className="space-y-3">
      {[...byDate.entries()].map(([date, dayTasks]) => (
        <div key={date} className="rounded-lg border border-slate-200 bg-white p-3">
          <div className="text-xs font-semibold text-slate-500">{date}</div>
          <ul className="mt-1 space-y-1 text-sm">
            {dayTasks.map((t) => (
              <li key={t.id} className="flex items-center justify-between">
                <span>{t.title} <span className="text-xs text-slate-400">({projectName(t.project_id)})</span></span>
                <StatusBadge status={t.status} />
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
