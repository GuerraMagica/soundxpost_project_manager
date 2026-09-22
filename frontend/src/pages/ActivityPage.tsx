import { useQuery } from "@tanstack/react-query";
import { activityApi, projectsApi } from "../api/endpoints";
import { EmptyState, ErrorState, Spinner } from "../components/Common";

export function ActivityPage() {
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: () => projectsApi.list() });
  const { data, isLoading, isError } = useQuery({ queryKey: ["activity", "all"], queryFn: () => activityApi.list(undefined, 100) });
  const projectName = (id: number) => projects?.find((p) => p.id === id)?.name ?? `#${id}`;

  if (isLoading) return <Spinner />;
  if (isError) return <ErrorState message="No se ha podido cargar la actividad." />;
  if (!data || data.length === 0) return <EmptyState message="Sin actividad registrada." />;

  return (
    <ul className="divide-y divide-slate-100 text-sm">
      {data.map((a) => (
        <li key={a.id} className="flex items-center justify-between py-2">
          <div>
            <span className="font-medium text-slate-700">{a.event_type.replace(/_/g, " ")}</span>
            <span className="ml-2 text-xs text-slate-400">{projectName(a.project_id)}</span>
            {a.old_state && a.new_state && (
              <span className="ml-2 text-xs text-slate-400">{a.old_state} → {a.new_state}</span>
            )}
          </div>
          <span className="text-xs text-slate-400">{new Date(a.created_at).toLocaleString("es-ES")}</span>
        </li>
      ))}
    </ul>
  );
}
