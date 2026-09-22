import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { projectsApi, adrApi } from "../api/endpoints";
import { ErrorState, Spinner } from "../components/Common";
import { StatusBadge } from "../components/Badges";
import type { Episode } from "../types";

export function MixesPage() {
  const { data: projects, isLoading, isError } = useQuery({ queryKey: ["projects"], queryFn: () => projectsApi.list() });

  if (isLoading) return <Spinner />;
  if (isError || !projects) return <ErrorState message="No se han podido cargar las mezclas." />;

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-500">Episodios con fecha de mezcla asignada, agrupados por proyecto.</p>
      {projects.map((project) => (
        <ProjectMixes key={project.id} projectId={project.id} projectName={project.name} />
      ))}
    </div>
  );
}

function ProjectMixes({ projectId, projectName }: { projectId: number; projectName: string }) {
  const { data: episodes } = useQuery({ queryKey: ["episodes", projectId], queryFn: () => projectsApi.episodes(projectId) });
  const { data: adrEntries } = useQuery({ queryKey: ["adr", projectId], queryFn: () => adrApi.list({ project_id: projectId }) });
  const withMix = (episodes ?? []).filter((e: Episode) => e.mix_date);
  if (withMix.length === 0) return null;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <h3 className="mb-2 text-sm font-semibold text-slate-800">
        <Link to={`/proyectos/${projectId}`} className="hover:text-brand-600">{projectName}</Link>
      </h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
            <th className="py-1">Episodio</th><th>Fecha mezcla</th><th>ADR pendiente</th>
          </tr>
        </thead>
        <tbody>
          {withMix.map((ep) => {
            const pending = (adrEntries ?? []).filter(
              (a) => a.episode_id === ep.id && !["FINALIZADO", "EN MEZCLA", "CANCELADO", "N/A"].includes(a.status),
            );
            return (
              <tr key={ep.id} className="border-b border-slate-100">
                <td className="py-1">{ep.code}</td>
                <td className="text-slate-500">{ep.mix_date}</td>
                <td>
                  {pending.length === 0 ? (
                    <StatusBadge status="LISTO" />
                  ) : (
                    <span className="text-xs text-amber-700">{pending.length} convocatoria(s) sin cerrar</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
