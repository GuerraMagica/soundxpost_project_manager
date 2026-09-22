import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { dashboardApi, risksApi } from "../api/endpoints";
import { RiskCard } from "../components/RiskCard";
import { Card, EmptyState, ErrorState, Spinner } from "../components/Common";
import { StatusBadge } from "../components/Badges";

export function Dashboard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: dashboardApi.summary,
  });
  const queryClient = useQueryClient();
  const runEngine = useMutation({
    mutationFn: risksApi.run,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["risks"] });
    },
  });

  if (isLoading) return <Spinner />;
  if (isError || !data) return <ErrorState message="No se ha podido cargar el Centro Operativo." />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          Excepciones y decisiones que requieren atención hoy. {data.active_projects.length} proyectos activos.
        </p>
        <button
          onClick={() => runEngine.mutate()}
          disabled={runEngine.isPending}
          className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {runEngine.isPending ? "Evaluando reglas…" : "Reevaluar riesgos"}
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-3">
          <h2 className="text-sm font-semibold text-slate-800">Riesgos urgentes</h2>
          {data.risks.length === 0 ? (
            <EmptyState message="No hay riesgos abiertos detectados." />
          ) : (
            <div className="space-y-3">
              {data.risks.slice(0, 6).map((risk) => (
                <RiskCard key={risk.id} risk={risk} />
              ))}
            </div>
          )}
        </div>

        <div className="space-y-4">
          <Card title="Próximas mezclas">
            {data.upcoming_mixes.length === 0 ? (
              <EmptyState message="Sin mezclas en los próximos 7 días." />
            ) : (
              <ul className="space-y-2 text-sm">
                {data.upcoming_mixes.map((ep) => (
                  <li key={ep.id} className="flex items-center justify-between">
                    <Link to={`/proyectos/${ep.project_id}`} className="hover:text-brand-600">
                      {ep.code}
                    </Link>
                    <span className="text-slate-500">{ep.mix_date}</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card title="Próximas entregas">
            {data.upcoming_deliveries.length === 0 ? (
              <EmptyState message="Sin entregas en los próximos 7 días." />
            ) : (
              <ul className="space-y-2 text-sm">
                {data.upcoming_deliveries.map((ep) => (
                  <li key={ep.id} className="flex items-center justify-between">
                    <Link to={`/proyectos/${ep.project_id}`} className="hover:text-brand-600">
                      {ep.code}
                    </Link>
                    <span className="text-slate-500">{ep.delivery_date}</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Tareas pendientes">
          {data.pending_tasks.length === 0 ? (
            <EmptyState message="No hay tareas pendientes." />
          ) : (
            <ul className="space-y-2 text-sm">
              {data.pending_tasks.slice(0, 6).map((task) => (
                <li key={task.id} className="flex items-center justify-between gap-2">
                  <span className="truncate">{task.title}</span>
                  <StatusBadge status={task.status} />
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="QC recientes">
          {data.recent_qc.length === 0 ? (
            <EmptyState message="Sin actividad de QC reciente." />
          ) : (
            <ul className="space-y-2 text-sm">
              {data.recent_qc.slice(0, 6).map((o) => (
                <li key={o.id} className="flex items-center justify-between gap-2">
                  <span className="truncate">{o.material_type} · {o.version}</span>
                  <StatusBadge status={o.status} />
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="ADR pendiente">
          {data.pending_adr.length === 0 ? (
            <EmptyState message="Sin convocatorias ADR pendientes." />
          ) : (
            <ul className="space-y-2 text-sm">
              {data.pending_adr.slice(0, 6).map((a) => (
                <li key={a.id} className="flex items-center justify-between gap-2">
                  <span className="truncate">{a.character_name} · conv. {a.convocatoria}</span>
                  <StatusBadge status={a.status} />
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <Card title="Actividad reciente">
        {data.recent_activity.length === 0 ? (
          <EmptyState message="Sin actividad registrada." />
        ) : (
          <ul className="divide-y divide-slate-100 text-sm">
            {data.recent_activity.map((a) => (
              <li key={a.id} className="flex items-center justify-between py-1.5">
                <span className="text-slate-700">{a.event_type.replace(/_/g, " ")}</span>
                <span className="text-xs text-slate-400">{new Date(a.created_at).toLocaleString("es-ES")}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
