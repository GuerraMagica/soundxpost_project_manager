import { NavLink } from "react-router-dom";

interface NavItem {
  label: string;
  to: string;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

const NAV: NavGroup[] = [
  {
    title: "INICIO",
    items: [
      { label: "Mi día", to: "/" },
      { label: "Bandeja de atención", to: "/riesgos" },
      { label: "Calendario", to: "/calendario" },
    ],
  },
  {
    title: "PROYECTOS",
    items: [
      { label: "Todos los proyectos", to: "/proyectos" },
      { label: "Proyectos activos", to: "/proyectos?status=ACTIVE" },
      { label: "Proyectos archivados", to: "/proyectos?status=ARCHIVED" },
    ],
  },
  {
    title: "OPERACIONES",
    items: [
      { label: "ADR", to: "/adr" },
      { label: "Mezclas", to: "/mezclas" },
      { label: "QC", to: "/qc" },
      { label: "Entregas", to: "/entregas" },
      { label: "Archivo", to: "/archivo" },
    ],
  },
  {
    title: "GESTIÓN",
    items: [
      { label: "Tareas", to: "/tareas" },
      { label: "Riesgos", to: "/riesgos" },
      { label: "Actividad", to: "/actividad" },
    ],
  },
  {
    title: "ADMINISTRACIÓN",
    items: [
      { label: "Plantillas de proyecto", to: "/admin/plantillas" },
      { label: "Integraciones", to: "/admin/integraciones" },
      { label: "Usuarios y roles", to: "/admin/usuarios" },
      { label: "Configuración", to: "/admin/configuracion" },
    ],
  },
];

export function Sidebar() {
  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-slate-200 bg-ink-950 text-slate-200">
      <div className="flex items-center gap-2 px-5 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500 text-sm font-bold text-white">
          SX
        </div>
        <div>
          <div className="text-sm font-semibold text-white leading-tight">SOUND X-POST</div>
          <div className="text-[10px] text-slate-400 leading-tight">Virtual Postproduction Coordinator</div>
        </div>
      </div>
      <nav className="flex-1 overflow-y-auto px-3 pb-6">
        {NAV.map((group) => (
          <div key={group.title} className="mb-4">
            <div className="px-2 pb-1 text-[11px] font-semibold tracking-wider text-slate-500">{group.title}</div>
            <div className="space-y-0.5">
              {group.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) =>
                    `block rounded-md px-2.5 py-1.5 text-sm transition-colors ${
                      isActive
                        ? "bg-brand-600/90 text-white font-medium"
                        : "text-slate-300 hover:bg-white/5 hover:text-white"
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>
      <div className="border-t border-white/10 px-4 py-3 text-[11px] text-slate-500">
        Entorno LAB — datos DEMO ficticios
      </div>
    </aside>
  );
}
