import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { archiveApi, projectsApi } from "../api/endpoints";
import { EmptyState, ErrorState, Spinner } from "../components/Common";

const ARCHIVE_COMPONENT_STATUSES = ["PENDIENTE", "LISTO", "N/A", "BLOQUEADO"];
const FIELDS = ["pt_session", "pm", "mne", "stems", "cuesheet", "qc_docs"] as const;

export function ArchivePage() {
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: () => projectsApi.list() });
  const [projectFilter, setProjectFilter] = useState<number | "">("");
  const { data: records, isLoading, isError } = useQuery({
    queryKey: ["archive", "all", projectFilter],
    queryFn: () => archiveApi.list(projectFilter === "" ? undefined : projectFilter),
  });
  const queryClient = useQueryClient();
  const update = useMutation({
    mutationFn: ({ id, field, value }: { id: number; field: string; value: string }) => archiveApi.update(id, { [field]: value }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["archive", "all"] }),
  });
  const verify = useMutation({
    mutationFn: ({ id, verifiedBy }: { id: number; verifiedBy: string }) =>
      archiveApi.update(id, { archive_verified: true, verified_by: verifiedBy, verified_date: new Date().toISOString().slice(0, 10) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["archive", "all"] }),
  });
  const projectName = (id: number) => projects?.find((p) => p.id === id)?.name ?? `#${id}`;

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-500">
        El archivo no equivale a entrega. La verificación final requiere confirmación humana explícita.
      </p>
      <select value={projectFilter} onChange={(e) => setProjectFilter(e.target.value ? Number(e.target.value) : "")} className="rounded-md border border-slate-300 px-2 py-1.5 text-sm">
        <option value="">Todos los proyectos</option>
        {projects?.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
      </select>

      {isLoading && <Spinner />}
      {isError && <ErrorState message="No se ha podido cargar el Archive Tracker." />}
      {records && records.length === 0 && <EmptyState message="Sin registros de archivo." />}

      {records && records.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
                <th className="py-2">Proyecto</th>
                {FIELDS.map((f) => <th key={f}>{f.toUpperCase()}</th>)}
                <th>Verificado</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id} className="border-b border-slate-100">
                  <td className="py-2 text-slate-500">{projectName(r.project_id)}</td>
                  {FIELDS.map((f) => (
                    <td key={f}>
                      <select
                        value={r[f]}
                        onChange={(e) => update.mutate({ id: r.id, field: f, value: e.target.value })}
                        className="rounded-md border border-slate-300 px-1 py-1 text-xs"
                      >
                        {ARCHIVE_COMPONENT_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                      </select>
                    </td>
                  ))}
                  <td>
                    {r.archive_verified ? (
                      <span className="text-xs text-emerald-700">✔ {r.verified_by}</span>
                    ) : (
                      <button
                        onClick={() => {
                          const name = prompt("Nombre de quien verifica el archivo:");
                          if (name) verify.mutate({ id: r.id, verifiedBy: name });
                        }}
                        className="text-xs text-brand-600 hover:underline"
                      >
                        Verificar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
