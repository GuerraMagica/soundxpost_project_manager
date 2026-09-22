import { useMemo, useState } from "react";
import type { ComponentType } from "react";
import type { EventProps } from "react-big-calendar";
import { Calendar, dateFnsLocalizer, Views } from "react-big-calendar";
// Importing the concrete implementation file (not the index re-export) and
// unwrapping defensively below works around a double CJS-interop wrapping
// quirk observed with this project's Rolldown-based Vite build.
// @ts-expect-error — no type declarations for this deep subpath
import * as WithDragAndDropModule from "react-big-calendar/lib/addons/dragAndDrop/withDragAndDrop";
import { format } from "date-fns/format";
import { parse } from "date-fns/parse";
import { startOfWeek } from "date-fns/startOfWeek";
import { getDay } from "date-fns/getDay";
import { es } from "date-fns/locale/es";
import "react-big-calendar/lib/css/react-big-calendar.css";
import "react-big-calendar/lib/addons/dragAndDrop/styles.css";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { calendarApi, episodesApi, projectsApi, tasksApi } from "../api/endpoints";
import { useAuth } from "../auth/AuthContext";
import { ErrorState, Spinner } from "../components/Common";
import { NewEventForm } from "../components/NewEventForm";
import type { CalendarFeedItem } from "../types";

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { locale: es }),
  getDay,
  locales: { es },
});

function unwrapDefault(mod: unknown): (calendar: unknown) => ComponentType<Record<string, unknown>> {
  let current = mod as { default?: unknown } | ((c: unknown) => unknown);
  while (typeof current !== "function" && current && "default" in current) {
    current = current.default as typeof current;
  }
  return current as (calendar: unknown) => ComponentType<Record<string, unknown>>;
}

// react-big-calendar's addon typings are loose; a permissive component type
// keeps drag-and-drop props (onEventDrop/onEventResize) usable below.
const withDragAndDrop = unwrapDefault(WithDragAndDropModule);
const DnDCalendar = withDragAndDrop(Calendar) as unknown as ComponentType<Record<string, unknown>>;

const EVENT_COLORS: Record<string, string> = {
  MIX: "#2747cf",
  DELIVERY: "#b91c1c",
  TASK: "#0f766e",
  ADR_SESSION: "#a16207",
  QC: "#7c3aed",
  RECONFORM: "#be185d",
  CUSTOM: "#475569",
};

interface CalEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  allDay: boolean;
  resource: CalendarFeedItem;
}

export function CalendarPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [scope, setScope] = useState<"TODOS" | "MIO">("TODOS");
  const [projectFilter, setProjectFilter] = useState<number | "">("");
  const [view, setView] = useState<(typeof Views)[keyof typeof Views]>(Views.MONTH);
  const [date, setDate] = useState(new Date());

  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: () => projectsApi.list() });

  const filters = useMemo(() => {
    const f: { project_ids?: string; user_id?: number } = {};
    if (projectFilter) f.project_ids = String(projectFilter);
    if (scope === "MIO" && user) f.user_id = user.id;
    return f;
  }, [projectFilter, scope, user]);

  const { data: feed, isLoading, isError } = useQuery({
    queryKey: ["calendar-feed", filters],
    queryFn: () => calendarApi.feed(filters),
  });

  const invalidateFeed = () => {
    queryClient.invalidateQueries({ queryKey: ["calendar-feed"] });
    queryClient.invalidateQueries({ queryKey: ["risks"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
  };

  const moveEpisode = useMutation({
    mutationFn: ({ episodeId, field, value }: { episodeId: number; field: "mix_date" | "delivery_date"; value: string }) =>
      episodesApi.update(episodeId, { [field]: value }),
    onSuccess: invalidateFeed,
  });
  const moveTask = useMutation({
    mutationFn: ({ taskId, value }: { taskId: number; value: string }) => tasksApi.update(taskId, { due_date: value }),
    onSuccess: invalidateFeed,
  });
  const moveCustomEvent = useMutation({
    mutationFn: ({ eventId, start, end }: { eventId: number; start: string; end?: string }) =>
      calendarApi.updateEvent(eventId, { start, end }),
    onSuccess: invalidateFeed,
  });

  const events: CalEvent[] = useMemo(
    () =>
      (feed ?? []).map((item) => ({
        id: item.id,
        title: item.title,
        start: new Date(item.start),
        end: item.end ? new Date(item.end) : new Date(item.start),
        allDay: item.all_day,
        resource: item,
      })),
    [feed],
  );

  const applyMove = (item: CalendarFeedItem, start: Date, end: Date) => {
    // Don't fire a network call (or a notification) if the user drops the
    // event back on its original date — the spec explicitly forbids this.
    const unchanged = start.getTime() === new Date(item.start).getTime();
    if (unchanged) return;

    if (item.source === "EPISODE_MIX") {
      moveEpisode.mutate({ episodeId: item.source_id, field: "mix_date", value: start.toISOString().slice(0, 10) });
    } else if (item.source === "EPISODE_DELIVERY") {
      moveEpisode.mutate({ episodeId: item.source_id, field: "delivery_date", value: start.toISOString().slice(0, 10) });
    } else if (item.source === "TASK") {
      moveTask.mutate({ taskId: item.source_id, value: start.toISOString().slice(0, 10) });
    } else if (item.source === "CALENDAR_EVENT") {
      moveCustomEvent.mutate({ eventId: item.source_id, start: start.toISOString(), end: item.end ? end.toISOString() : undefined });
    }
  };

  const handleEventDrop = ({ event, start, end }: { event: CalEvent; start: Date; end: Date }) => {
    applyMove(event.resource, start, end);
  };
  const handleEventResize = ({ event, start, end }: { event: CalEvent; start: Date; end: Date }) => {
    if (event.resource.source === "CALENDAR_EVENT") {
      moveCustomEvent.mutate({ eventId: event.resource.source_id, start: start.toISOString(), end: end.toISOString() });
    }
  };

  const eventPropGetter = (event: CalEvent) => ({
    style: {
      backgroundColor: EVENT_COLORS[event.resource.event_type] ?? "#475569",
      borderRadius: 4,
      border: "none",
    },
  });

  if (isLoading) return <Spinner />;
  if (isError) return <ErrorState message="No se ha podido cargar el calendario." />;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex gap-1 rounded-md border border-slate-200 bg-white p-1">
          {(["TODOS", "MIO"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setScope(s)}
              className={`rounded px-3 py-1 text-xs font-medium ${scope === s ? "bg-brand-600 text-white" : "text-slate-500 hover:bg-slate-100"}`}
            >
              {s === "TODOS" ? "Todos los proyectos" : "Mi calendario"}
            </button>
          ))}
        </div>
        <select
          value={projectFilter}
          onChange={(e) => setProjectFilter(e.target.value ? Number(e.target.value) : "")}
          className="rounded-md border border-slate-300 px-2 py-1.5 text-xs"
        >
          <option value="">Filtrar por proyecto…</option>
          {projects?.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        {projectFilter && <NewEventForm projectId={projectFilter} onCreated={invalidateFeed} />}
        <div className="ml-auto flex flex-wrap gap-2 text-xs text-slate-500">
          {Object.entries(EVENT_COLORS).map(([k, color]) => (
            <span key={k} className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
              {k}
            </span>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-3" style={{ height: 700 }}>
        <DnDCalendar
          localizer={localizer}
          events={events}
          view={view}
          onView={(v: (typeof Views)[keyof typeof Views]) => setView(v)}
          date={date}
          onNavigate={setDate}
          views={[Views.MONTH, Views.WEEK, Views.DAY, Views.AGENDA]}
          startAccessor="start"
          endAccessor="end"
          onEventDrop={handleEventDrop}
          onEventResize={handleEventResize}
          resizable
          draggableAccessor={() => true}
          eventPropGetter={eventPropGetter as (event: object) => { style: object }}
          components={{
            event: ({ event }: EventProps<CalEvent>) => (
              <span title={event.resource.status ?? undefined}>{event.title}</span>
            ),
          }}
          messages={{
            month: "Mes",
            week: "Semana",
            day: "Día",
            agenda: "Agenda",
            today: "Hoy",
            previous: "Anterior",
            next: "Siguiente",
            noEventsInRange: "Sin eventos en este rango.",
            showMore: (count: number) => `+${count} más`,
          }}
        />
      </div>
    </div>
  );
}
