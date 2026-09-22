import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { projectsApi } from "../api/endpoints";
import { Card, EmptyState, ErrorState, Spinner } from "../components/Common";
import { StatusBadge } from "../components/Badges";
import type { Project, ProjectType } from "../types";

const PROJECT_TYPES: ProjectType[] = [
  "SERIES",
  "FEATURE_FILM",
  "DOCUMENTARY",
  "COMMERCIAL",
  "PROMOTIONAL",
  "REGIONAL_VERSION",
  "TECHNICAL_ADAPTATION",
];

function NewProjectForm({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [projectType, setProjectType] = useState<ProjectType>("SERIES");
  const [clientName, setClientName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const create = useMutation({
    mutationFn: () =>
      projectsApi.create({ name, code, project_type: projectType, client_name: clientName || null }),
    onSuccess: () => {
      setOpen(false);
      setName("");
      setCode("");
      setClientName("");
      setError(null);
      onCreated();
    },
    onError: (e: Error) => setError(e.message),
  });

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700"
      >
        + Nuevo proyecto
      </button>
    );
  }

  return (
    <form
      className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm space-y-3"
      onSubmit={(e) => {
        e.preventDefault();
        create.mutate();
      }}
    >
      {error && <div className="rounded-md bg-red-50 p-2 text-xs text-red-700">{error}</div>}
      <div className="grid grid-cols-2 gap-3">
        <label className="text-xs font-medium text-slate-600">
          Nombre
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
          />
        </label>
        <label className="text-xs font-medium text-slate-600">
          Código interno
          <input
            required
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
          />
        </label>
        <label className="text-xs font-medium text-slate-600">
          Tipo
          <select
            value={projectType}
            onChange={(e) => setProjectType(e.target.value as ProjectType)}
            className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
          >
            {PROJECT_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs font-medium text-slate-600">
          Cliente / productora
          <input
            value={clientName}
            onChange={(e) => setClientName(e.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
          />
        </label>
      </div>
      <div className="flex justify-end gap-2">
        <button type="button" onClick={() => setOpen(false)} className="rounded-md px-3 py-1.5 text-sm text-slate-600">
          Cancelar
        </button>
        <button
          type="submit"
          disabled={create.isPending}
          className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          Crear proyecto
        </button>
      </div>
    </form>
  );
}

export function ProjectsList() {
  const [searchParams] = useSearchParams();
  const statusFilter = searchParams.get("status") ?? undefined;
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["projects", statusFilter],
    queryFn: () => projectsApi.list(statusFilter),
  });

  const refresh = () => queryClient.invalidateQueries({ queryKey: ["projects"] });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          {statusFilter ? `Filtrando por estado: ${statusFilter}` : "Todos los proyectos"}
        </p>
        <NewProjectForm onCreated={refresh} />
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorState message="No se han podido cargar los proyectos." />}
      {data && data.length === 0 && <EmptyState message="No hay proyectos que coincidan con este filtro." />}

      {data && data.length > 0 && (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
          {data.map((project: Project) => (
            <Link key={project.id} to={`/proyectos/${project.id}`}>
              <Card>
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-xs text-slate-400">{project.code}</div>
                    <div className="font-semibold text-slate-900">{project.name}</div>
                  </div>
                  <StatusBadge status={project.status} />
                </div>
                <div className="mt-2 text-xs text-slate-500">{project.project_type}</div>
                {project.client_name && <div className="text-xs text-slate-500">{project.client_name}</div>}
                {project.is_demo && (
                  <div className="mt-2 inline-block rounded bg-amber-50 px-1.5 py-0.5 text-[10px] font-semibold text-amber-700">
                    DEMO
                  </div>
                )}
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
