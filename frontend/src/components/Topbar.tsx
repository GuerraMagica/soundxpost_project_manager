import { useLocation } from "react-router-dom";

const TITLES: Record<string, string> = {
  "/": "Centro Operativo",
  "/riesgos": "Bandeja de riesgos",
  "/calendario": "Calendario",
  "/proyectos": "Proyectos",
  "/adr": "ADR Tracker",
  "/mezclas": "Mezclas",
  "/qc": "QC",
  "/entregas": "Delivery Tracker",
  "/archivo": "Archive Tracker",
  "/tareas": "Tareas",
  "/actividad": "Actividad",
};

export function Topbar() {
  const location = useLocation();
  const base = "/" + (location.pathname.split("/")[1] ?? "");
  const title = TITLES[location.pathname] ?? TITLES[base] ?? "SOUND X-POST";

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-6">
      <h1 className="text-base font-semibold text-slate-900">{title}</h1>
      <div className="flex items-center gap-3">
        <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700 border border-amber-200">
          LABORATORIO · NO APTO PARA PRODUCCIÓN
        </span>
        <div className="h-8 w-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-xs font-semibold">
          DM
        </div>
      </div>
    </header>
  );
}
