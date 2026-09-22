import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

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

function initials(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join("");
}

export function Topbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const base = "/" + (location.pathname.split("/")[1] ?? "");
  const title = TITLES[location.pathname] ?? TITLES[base] ?? "SOUND X-POST";

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-6">
      <h1 className="text-base font-semibold text-slate-900">{title}</h1>
      <div className="flex items-center gap-3">
        <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700 border border-amber-200">
          LABORATORIO · NO APTO PARA PRODUCCIÓN
        </span>
        {user && (
          <div className="flex items-center gap-2">
            <div className="text-right leading-tight">
              <div className="text-xs font-semibold text-slate-700">{user.name}</div>
              <div className="text-[10px] text-slate-400">{user.role}</div>
            </div>
            <div className="h-8 w-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-xs font-semibold">
              {initials(user.name)}
            </div>
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
              className="rounded-md px-2 py-1 text-xs text-slate-500 hover:bg-slate-100"
            >
              Salir
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
