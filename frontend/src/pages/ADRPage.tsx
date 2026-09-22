import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { adrApi, projectsApi } from "../api/endpoints";
import { EmptyState, ErrorState, Spinner } from "../components/Common";

const ADR_STATUSES = [
  "PENDIENTE", "CONVOCADO", "GRABADO", "NO RECIBIDO", "RECIBIDO", "PENDIENTE EDICIÓN",
  "EDITANDO", "EDITADO", "AÑADIDO EN SESIÓN", "EN MEZCLA", "FINALIZADO", "CANCELADO", "N/A",
];

export function ADRPage() {
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: () => projectsApi.list() });
  const [projectFilter, setProjectFilter] = useState<number | "">("");
  const { data: entries, isLoading, isError } = useQuery({
    queryKey: ["adr", "all", projectFilter],
    queryFn: () => adrApi.list(projectFilter === "" ? {} : { project_id: projectFilter }),
  });
  const queryClient = useQueryClient();
  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => adrApi.update(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["adr", "all"] }),
  });

  const projectName = (id: number) => projects?.find((p) => p.id === id)?.name ?? `#${id}`;

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-500">
        Unidad de seguimiento: proyecto + episodio + personaje + convocatoria. No se hace seguimiento cue por cue.
      </p>
      <select value={projectFilter} onChange={(e) => setProjectFilter(e.target.value ? Number(e.target.value) : "")} className="rounded-md border border-slate-300 px-2 py-1.5 text-sm">
        <option value="">Todos los proyectos</option>
        {projects?.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
      </select>

      {isLoading && <Spinner />}
      {isError && <ErrorState message="No se ha podido cargar el ADR Tracker." />}
      {entries && entries.length === 0 && <EmptyState message="No hay convocatorias ADR registradas." />}

      {entries && entries.length > 0 && (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
              <th className="py-2">Proyecto</th><th>Character Name</th><th>Actor Name</th><th>Convocatoria</th>
              <th>Total Cues</th><th>ADD</th><th>TBW</th><th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e) => (
              <tr key={e.id} className="border-b border-slate-100">
                <td className="py-2 text-slate-500">{projectName(e.project_id)}</td>
                <td>{e.character_name}</td>
                <td className="text-slate-500">{e.actor_name ?? "—"}</td>
                <td>{e.convocatoria}</td>
                <td>{e.total_cues ?? "—"}</td>
                <td>{e.add_flag ? "Y" : ""}</td>
                <td>{e.tbw_flag ? "Y" : ""}</td>
                <td>
                  <select value={e.status} onChange={(ev) => updateStatus.mutate({ id: e.id, status: ev.target.value })} className="rounded-md border border-slate-300 px-2 py-1 text-xs">
                    {ADR_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
