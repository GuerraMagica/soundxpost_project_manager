import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { calendarApi } from "../api/endpoints";

const CUSTOM_EVENT_TYPES = ["ADR_SESSION", "QC", "RECONFORM", "CUSTOM"];

export function NewEventForm({ projectId, onCreated }: { projectId: number; onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [eventType, setEventType] = useState("ADR_SESSION");
  const [start, setStart] = useState("");

  const create = useMutation({
    mutationFn: () => calendarApi.createEvent({ project_id: projectId, title, event_type: eventType, start }),
    onSuccess: () => {
      setOpen(false);
      setTitle("");
      setStart("");
      onCreated();
    },
  });

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="rounded-md bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700">
        + Evento
      </button>
    );
  }

  return (
    <form
      className="flex flex-wrap items-end gap-2 rounded-md border border-slate-200 bg-white p-2"
      onSubmit={(e) => {
        e.preventDefault();
        if (title && start) create.mutate();
      }}
    >
      <label className="text-[11px] font-medium text-slate-600">
        Título
        <input required value={title} onChange={(e) => setTitle(e.target.value)} className="mt-1 block w-40 rounded-md border border-slate-300 px-2 py-1 text-xs" />
      </label>
      <label className="text-[11px] font-medium text-slate-600">
        Tipo
        <select value={eventType} onChange={(e) => setEventType(e.target.value)} className="mt-1 block rounded-md border border-slate-300 px-2 py-1 text-xs">
          {CUSTOM_EVENT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </label>
      <label className="text-[11px] font-medium text-slate-600">
        Fecha y hora
        <input required type="datetime-local" value={start} onChange={(e) => setStart(e.target.value)} className="mt-1 block rounded-md border border-slate-300 px-2 py-1 text-xs" />
      </label>
      <button type="button" onClick={() => setOpen(false)} className="rounded-md px-2 py-1 text-xs text-slate-500">Cancelar</button>
      <button type="submit" className="rounded-md bg-brand-600 px-2 py-1 text-xs font-medium text-white">Guardar</button>
    </form>
  );
}
