import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { dashboardApi } from "../api/endpoints";
import { EmptyState, ErrorState, Spinner } from "../components/Common";

export function CalendarPage() {
  const { data, isLoading, isError } = useQuery({ queryKey: ["dashboard-summary"], queryFn: dashboardApi.summary });

  if (isLoading) return <Spinner />;
  if (isError || !data) return <ErrorState message="No se ha podido cargar el calendario." />;

  const events = [
    ...data.upcoming_mixes.map((e) => ({ date: e.mix_date!, label: `Mezcla — ${e.code}`, projectId: e.project_id })),
    ...data.upcoming_deliveries.map((e) => ({ date: e.delivery_date!, label: `Entrega — ${e.code}`, projectId: e.project_id })),
  ].sort((a, b) => (a.date < b.date ? -1 : 1));

  if (events.length === 0) return <EmptyState message="No hay mezclas ni entregas en los próximos 7 días." />;

  return (
    <div className="space-y-2">
      <p className="text-sm text-slate-500">Próximas mezclas y entregas (7 días).</p>
      {events.map((ev, idx) => (
        <div key={idx} className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm">
          <Link to={`/proyectos/${ev.projectId}`} className="hover:text-brand-600">{ev.label}</Link>
          <span className="text-slate-500">{ev.date}</span>
        </div>
      ))}
    </div>
  );
}
