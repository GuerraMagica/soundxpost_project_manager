const SEVERITY_STYLES: Record<string, string> = {
  CRITICAL: "bg-red-100 text-red-700 border-red-200",
  HIGH: "bg-orange-100 text-orange-700 border-orange-200",
  WARNING: "bg-amber-100 text-amber-700 border-amber-200",
  INFO: "bg-sky-100 text-sky-700 border-sky-200",
};

export function SeverityBadge({ severity }: { severity: string }) {
  const style = SEVERITY_STYLES[severity] ?? "bg-slate-100 text-slate-700 border-slate-200";
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold ${style}`}>
      {severity}
    </span>
  );
}

const STATUS_STYLES: Record<string, string> = {
  PENDIENTE: "bg-slate-100 text-slate-700",
  "EN PROGRESO": "bg-blue-100 text-blue-700",
  BLOQUEADO: "bg-red-100 text-red-700",
  "EN REVISIÓN": "bg-amber-100 text-amber-700",
  FINALIZADO: "bg-emerald-100 text-emerald-700",
  CANCELADO: "bg-slate-200 text-slate-500 line-through",
  DETECTED: "bg-amber-100 text-amber-700",
  ACKNOWLEDGED: "bg-blue-100 text-blue-700",
  IN_PROGRESS: "bg-blue-100 text-blue-700",
  RESOLVED_PENDING_VERIFICATION: "bg-violet-100 text-violet-700",
  CLOSED: "bg-emerald-100 text-emerald-700",
  PASSED: "bg-emerald-100 text-emerald-700",
  QC_FAIL: "bg-red-100 text-red-700",
  IN_QC: "bg-amber-100 text-amber-700",
  OUTPUT_READY: "bg-blue-100 text-blue-700",
  NOT_STARTED: "bg-slate-100 text-slate-600",
  WIP: "bg-blue-100 text-blue-700",
  DELIVERED: "bg-emerald-100 text-emerald-700",
  FINAL: "bg-violet-100 text-violet-700",
  READY: "bg-blue-100 text-blue-700",
  BUILDING: "bg-amber-100 text-amber-700",
  PENDING: "bg-slate-100 text-slate-600",
  LISTO: "bg-emerald-100 text-emerald-700",
  BLOQUEADO_ARCHIVO: "bg-red-100 text-red-700",
};

export function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLES[status] ?? "bg-slate-100 text-slate-700";
  return (
    <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${style}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}

const PRIORITY_STYLES: Record<string, string> = {
  URGENT: "text-red-600",
  HIGH: "text-orange-600",
  NORMAL: "text-slate-500",
  LOW: "text-slate-400",
};

export function PriorityDot({ priority }: { priority: string }) {
  return (
    <span className={`text-xs font-semibold ${PRIORITY_STYLES[priority] ?? "text-slate-500"}`}>● {priority}</span>
  );
}
