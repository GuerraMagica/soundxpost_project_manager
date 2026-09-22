import { Link } from "react-router-dom";
import type { Risk } from "../types";
import { SeverityBadge } from "./Badges";

export function RiskCard({ risk }: { risk: Risk }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm hover:shadow transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <SeverityBadge severity={risk.severity} />
          <span className="text-xs uppercase tracking-wide text-slate-400">{risk.rule_id}</span>
        </div>
        {risk.due_date && (
          <span className="text-xs text-slate-500">Vence: {risk.due_date}</span>
        )}
      </div>
      <Link
        to={`/proyectos/${risk.project_id}`}
        className="mt-2 block text-sm font-semibold text-slate-900 hover:text-brand-600"
      >
        {risk.title}
      </Link>
      <p className="mt-1 text-sm text-slate-600">{risk.description}</p>
      <div className="mt-2 rounded-md bg-slate-50 px-2 py-1 text-xs text-slate-500">
        <span className="font-semibold">Evidencia: </span>
        {risk.evidence}
      </div>
      <div className="mt-2 text-xs text-brand-700">
        <span className="font-semibold">Acción sugerida: </span>
        {risk.suggested_action}
      </div>
    </div>
  );
}
