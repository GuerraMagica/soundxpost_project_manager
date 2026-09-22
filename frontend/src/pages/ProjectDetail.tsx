import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import {
  activityApi,
  adrApi,
  archiveApi,
  deliveryApi,
  episodesApi,
  projectsApi,
  tasksApi,
} from "../api/endpoints";
import { Card, EmptyState, ErrorState, Spinner } from "../components/Common";
import { StatusBadge } from "../components/Badges";
import type { Episode, Project } from "../types";

const TABS = ["Resumen", "Episodios", "Tareas", "ADR", "Delivery", "Archivo", "Actividad"] as const;
type Tab = (typeof TABS)[number];

const TASK_STATUSES = ["PENDIENTE", "EN PROGRESO", "BLOQUEADO", "EN REVISIÓN", "FINALIZADO", "CANCELADO"];
const ADR_STATUSES = [
  "PENDIENTE",
  "CONVOCADO",
  "GRABADO",
  "NO RECIBIDO",
  "RECIBIDO",
  "PENDIENTE EDICIÓN",
  "EDITANDO",
  "EDITADO",
  "AÑADIDO EN SESIÓN",
  "EN MEZCLA",
  "FINALIZADO",
  "CANCELADO",
  "N/A",
];
const OUTPUT_STATUSES = ["NOT_STARTED", "WIP", "OUTPUT_READY", "IN_QC", "QC_FAIL", "PASSED", "N_A"];
const DELIVERY_STATUSES = ["PENDING", "BUILDING", "READY", "FINAL", "DELIVERED", "N_A"];
const ARCHIVE_COMPONENT_STATUSES = ["PENDIENTE", "LISTO", "N/A", "BLOQUEADO"];

export function ProjectDetail() {
  const { id } = useParams();
  const projectId = Number(id);
  const [tab, setTab] = useState<Tab>("Resumen");

  const { data: project, isLoading, isError } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectsApi.get(projectId),
  });
  const { data: episodes } = useQuery({
    queryKey: ["episodes", projectId],
    queryFn: () => projectsApi.episodes(projectId),
  });

  if (isLoading) return <Spinner />;
  if (isError || !project) return <ErrorState message="Proyecto no encontrado." />;

  return (
    <div className="space-y-4">
      <div>
        <div className="text-xs text-slate-400">{project.code}</div>
        <h2 className="text-xl font-semibold text-slate-900">{project.name}</h2>
        <div className="mt-1 flex items-center gap-2 text-sm text-slate-500">
          <StatusBadge status={project.status} />
          <span>{project.project_type}</span>
          {project.client_name && <span>· {project.client_name}</span>}
        </div>
      </div>

      <div className="flex gap-1 border-b border-slate-200">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-3 py-2 text-sm font-medium border-b-2 -mb-px ${
              tab === t ? "border-brand-600 text-brand-700" : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "Resumen" && <ResumenTab project={project} episodes={episodes ?? []} />}
      {tab === "Episodios" && <EpisodiosTab projectId={projectId} episodes={episodes ?? []} />}
      {tab === "Tareas" && <TareasTab projectId={projectId} episodes={episodes ?? []} />}
      {tab === "ADR" && <ADRTab projectId={projectId} episodes={episodes ?? []} />}
      {tab === "Delivery" && <DeliveryTab projectId={projectId} episodes={episodes ?? []} />}
      {tab === "Archivo" && <ArchivoTab projectId={projectId} episodes={episodes ?? []} />}
      {tab === "Actividad" && <ActividadTab projectId={projectId} />}
    </div>
  );
}

function ResumenTab({ project, episodes }: { project: Project; episodes: Episode[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <Card title="Datos del proyecto">
        <dl className="space-y-1 text-sm">
          <div className="flex justify-between"><dt className="text-slate-500">Plataforma de entrega</dt><dd>{project.delivery_platform ?? "—"}</dd></div>
          <div className="flex justify-between"><dt className="text-slate-500">Inicio</dt><dd>{project.start_date ?? "—"}</dd></div>
          <div className="flex justify-between"><dt className="text-slate-500">Fin previsto</dt><dd>{project.end_date ?? "—"}</dd></div>
          <div className="flex justify-between"><dt className="text-slate-500">Episodios</dt><dd>{episodes.length}</dd></div>
        </dl>
        {project.notes && <p className="mt-3 text-xs text-slate-500">{project.notes}</p>}
      </Card>
      <Card title="Episodios">
        {episodes.length === 0 ? (
          <EmptyState message="Sin episodios todavía." />
        ) : (
          <ul className="space-y-1 text-sm">
            {episodes.map((ep) => (
              <li key={ep.id} className="flex justify-between">
                <span>{ep.code} {ep.title ? `— ${ep.title}` : ""}</span>
                <StatusBadge status={ep.status} />
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}

function EpisodiosTab({ projectId, episodes }: { projectId: number; episodes: Episode[] }) {
  const queryClient = useQueryClient();
  const [code, setCode] = useState("");
  const [title, setTitle] = useState("");

  const create = useMutation({
    mutationFn: () => episodesApi.create({ project_id: projectId, code, title: title || undefined }),
    onSuccess: () => {
      setCode("");
      setTitle("");
      queryClient.invalidateQueries({ queryKey: ["episodes", projectId] });
    },
  });

  const updateDate = useMutation({
    mutationFn: ({ id, field, value }: { id: number; field: "mix_date" | "delivery_date"; value: string }) =>
      episodesApi.update(id, { [field]: value || null }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["episodes", projectId] }),
  });

  return (
    <div className="space-y-4">
      <form
        className="flex flex-wrap items-end gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          if (code) create.mutate();
        }}
      >
        <label className="text-xs font-medium text-slate-600">
          Código (S01E01)
          <input value={code} onChange={(e) => setCode(e.target.value)} className="mt-1 block rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
        </label>
        <label className="text-xs font-medium text-slate-600">
          Título
          <input value={title} onChange={(e) => setTitle(e.target.value)} className="mt-1 block rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
        </label>
        <button type="submit" className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700">
          + Añadir episodio
        </button>
      </form>

      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
            <th className="py-2">Episodio</th>
            <th>Estado</th>
            <th>Fecha de mezcla</th>
            <th>Fecha de entrega</th>
          </tr>
        </thead>
        <tbody>
          {episodes.map((ep) => (
            <tr key={ep.id} className="border-b border-slate-100">
              <td className="py-2">{ep.code} {ep.title && <span className="text-slate-400">— {ep.title}</span>}</td>
              <td><StatusBadge status={ep.status} /></td>
              <td>
                <input
                  type="date"
                  defaultValue={ep.mix_date ?? ""}
                  onBlur={(e) => updateDate.mutate({ id: ep.id, field: "mix_date", value: e.target.value })}
                  className="rounded-md border border-slate-300 px-2 py-1 text-xs"
                />
              </td>
              <td>
                <input
                  type="date"
                  defaultValue={ep.delivery_date ?? ""}
                  onBlur={(e) => updateDate.mutate({ id: ep.id, field: "delivery_date", value: e.target.value })}
                  className="rounded-md border border-slate-300 px-2 py-1 text-xs"
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {episodes.length === 0 && <EmptyState message="Sin episodios todavía." />}
    </div>
  );
}

function TareasTab({ projectId, episodes }: { projectId: number; episodes: Episode[] }) {
  const queryClient = useQueryClient();
  const { data: tasks } = useQuery({ queryKey: ["tasks", projectId], queryFn: () => tasksApi.list({ project_id: projectId }) });
  const [title, setTitle] = useState("");
  const [episodeId, setEpisodeId] = useState<number | "">("");

  const create = useMutation({
    mutationFn: () => tasksApi.create({ title, project_id: projectId, episode_id: episodeId === "" ? undefined : episodeId }),
    onSuccess: () => {
      setTitle("");
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
    },
  });
  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => tasksApi.update(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasks", projectId] }),
  });

  return (
    <div className="space-y-4">
      <form
        className="flex flex-wrap items-end gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          if (title) create.mutate();
        }}
      >
        <label className="text-xs font-medium text-slate-600">
          Nueva tarea
          <input value={title} onChange={(e) => setTitle(e.target.value)} className="mt-1 block w-64 rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
        </label>
        <label className="text-xs font-medium text-slate-600">
          Episodio
          <select value={episodeId} onChange={(e) => setEpisodeId(e.target.value ? Number(e.target.value) : "")} className="mt-1 block rounded-md border border-slate-300 px-2 py-1.5 text-sm">
            <option value="">—</option>
            {episodes.map((ep) => <option key={ep.id} value={ep.id}>{ep.code}</option>)}
          </select>
        </label>
        <button type="submit" className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700">
          + Crear tarea
        </button>
      </form>

      {!tasks || tasks.length === 0 ? (
        <EmptyState message="Sin tareas en este proyecto." />
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
              <th className="py-2">Título</th>
              <th>Episodio</th>
              <th>Prioridad</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.id} className="border-b border-slate-100">
                <td className="py-2">{task.title}</td>
                <td className="text-slate-500">{episodes.find((e) => e.id === task.episode_id)?.code ?? "—"}</td>
                <td className="text-slate-500">{task.priority}</td>
                <td>
                  <select
                    value={task.status}
                    onChange={(e) => updateStatus.mutate({ id: task.id, status: e.target.value })}
                    className="rounded-md border border-slate-300 px-2 py-1 text-xs"
                  >
                    {TASK_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function ADRTab({ projectId, episodes }: { projectId: number; episodes: Episode[] }) {
  const queryClient = useQueryClient();
  const { data: entries } = useQuery({ queryKey: ["adr", projectId], queryFn: () => adrApi.list({ project_id: projectId }) });
  const [characterName, setCharacterName] = useState("");
  const [episodeId, setEpisodeId] = useState<number | "">(episodes[0]?.id ?? "");
  const [convocatoria, setConvocatoria] = useState(1);

  const create = useMutation({
    mutationFn: () =>
      adrApi.create({ project_id: projectId, episode_id: Number(episodeId), character_name: characterName, convocatoria }),
    onSuccess: () => {
      setCharacterName("");
      queryClient.invalidateQueries({ queryKey: ["adr", projectId] });
    },
  });
  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => adrApi.update(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["adr", projectId] }),
  });

  return (
    <div className="space-y-4">
      <form
        className="flex flex-wrap items-end gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          if (characterName && episodeId) create.mutate();
        }}
      >
        <label className="text-xs font-medium text-slate-600">
          Episodio
          <select value={episodeId} onChange={(e) => setEpisodeId(Number(e.target.value))} className="mt-1 block rounded-md border border-slate-300 px-2 py-1.5 text-sm">
            {episodes.map((ep) => <option key={ep.id} value={ep.id}>{ep.code}</option>)}
          </select>
        </label>
        <label className="text-xs font-medium text-slate-600">
          Personaje
          <input value={characterName} onChange={(e) => setCharacterName(e.target.value)} className="mt-1 block rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
        </label>
        <label className="text-xs font-medium text-slate-600">
          Convocatoria
          <input type="number" min={1} value={convocatoria} onChange={(e) => setConvocatoria(Number(e.target.value))} className="mt-1 block w-20 rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
        </label>
        <button type="submit" className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700">
          + Añadir convocatoria
        </button>
      </form>

      {!entries || entries.length === 0 ? (
        <EmptyState message="Sin convocatorias ADR registradas." />
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
              <th className="py-2">Episodio</th>
              <th>Character Name</th>
              <th>Actor</th>
              <th>Convocatoria</th>
              <th>Total Cues</th>
              <th>ADD</th>
              <th>TBW</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={entry.id} className="border-b border-slate-100">
                <td className="py-2">{episodes.find((e) => e.id === entry.episode_id)?.code ?? "—"}</td>
                <td>{entry.character_name}</td>
                <td className="text-slate-500">{entry.actor_name ?? "—"}</td>
                <td>{entry.convocatoria}</td>
                <td>{entry.total_cues ?? "—"}</td>
                <td>{entry.add_flag ? "Y" : ""}</td>
                <td>{entry.tbw_flag ? "Y" : ""}</td>
                <td>
                  <select
                    value={entry.status}
                    onChange={(e) => updateStatus.mutate({ id: entry.id, status: e.target.value })}
                    className="rounded-md border border-slate-300 px-2 py-1 text-xs"
                  >
                    {ADR_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function DeliveryTab({ projectId, episodes }: { projectId: number; episodes: Episode[] }) {
  const queryClient = useQueryClient();
  const { data: outputs } = useQuery({ queryKey: ["outputs", projectId], queryFn: () => deliveryApi.listOutputs({ project_id: projectId }) });
  const { data: packages } = useQuery({ queryKey: ["packages", projectId], queryFn: () => deliveryApi.listPackages({ project_id: projectId }) });

  const [materialType, setMaterialType] = useState("");
  const [episodeId, setEpisodeId] = useState<number | "">(episodes[0]?.id ?? "");

  const createOutput = useMutation({
    mutationFn: () => deliveryApi.createOutput({ project_id: projectId, episode_id: Number(episodeId), material_type: materialType }),
    onSuccess: () => {
      setMaterialType("");
      queryClient.invalidateQueries({ queryKey: ["outputs", projectId] });
    },
  });
  const updateOutput = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => deliveryApi.updateOutput(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["outputs", projectId] }),
  });
  const updatePackage = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => deliveryApi.updatePackage(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["packages", projectId] }),
  });

  return (
    <div className="space-y-6">
      <Card title="Outputs / QC" action={
        <form
          className="flex items-end gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            if (materialType && episodeId) createOutput.mutate();
          }}
        >
          <select value={episodeId} onChange={(e) => setEpisodeId(Number(e.target.value))} className="rounded-md border border-slate-300 px-2 py-1 text-xs">
            {episodes.map((ep) => <option key={ep.id} value={ep.id}>{ep.code}</option>)}
          </select>
          <input placeholder="PM_VO_5_1" value={materialType} onChange={(e) => setMaterialType(e.target.value)} className="rounded-md border border-slate-300 px-2 py-1 text-xs w-32" />
          <button type="submit" className="rounded-md bg-brand-600 px-2 py-1 text-xs font-medium text-white">+ Output</button>
        </form>
      }>
        {!outputs || outputs.length === 0 ? (
          <EmptyState message="Sin outputs registrados." />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
                <th className="py-2">Episodio</th><th>Material</th><th>Versión</th><th>Ronda QC</th><th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {outputs.map((o) => (
                <tr key={o.id} className="border-b border-slate-100">
                  <td className="py-2">{episodes.find((e) => e.id === o.episode_id)?.code ?? "—"}</td>
                  <td>{o.material_type}</td>
                  <td>{o.version}</td>
                  <td>{o.qc_round}</td>
                  <td>
                    <select value={o.status} onChange={(e) => updateOutput.mutate({ id: o.id, status: e.target.value })} className="rounded-md border border-slate-300 px-2 py-1 text-xs">
                      {OUTPUT_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      <Card title="Delivery Package">
        {!packages || packages.length === 0 ? (
          <EmptyState message="Sin Delivery Packages registrados." />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
                <th className="py-2">Episodio</th><th>Material</th><th>Versión</th><th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {packages.map((p) => (
                <tr key={p.id} className="border-b border-slate-100">
                  <td className="py-2">{episodes.find((e) => e.id === p.episode_id)?.code ?? "—"}</td>
                  <td>{p.material_type}</td>
                  <td>{p.version}</td>
                  <td>
                    <select value={p.status} onChange={(e) => updatePackage.mutate({ id: p.id, status: e.target.value })} className="rounded-md border border-slate-300 px-2 py-1 text-xs">
                      {DELIVERY_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}

function ArchivoTab({ projectId, episodes }: { projectId: number; episodes: Episode[] }) {
  const queryClient = useQueryClient();
  const { data: records } = useQuery({ queryKey: ["archive", projectId], queryFn: () => archiveApi.list(projectId) });
  const fields = ["pt_session", "pm", "mne", "stems", "cuesheet", "qc_docs"] as const;

  const update = useMutation({
    mutationFn: ({ id, field, value }: { id: number; field: string; value: string }) => archiveApi.update(id, { [field]: value }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["archive", projectId] }),
  });
  const verify = useMutation({
    mutationFn: ({ id, verifiedBy }: { id: number; verifiedBy: string }) =>
      archiveApi.update(id, { archive_verified: true, verified_by: verifiedBy, verified_date: new Date().toISOString().slice(0, 10) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["archive", projectId] }),
  });

  const episodeCode = useMemo(() => (id: number) => episodes.find((e) => e.id === id)?.code ?? "—", [episodes]);

  if (!records || records.length === 0) return <EmptyState message="Sin registros de archivo todavía." />;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
            <th className="py-2">Episodio</th>
            {fields.map((f) => <th key={f}>{f.toUpperCase()}</th>)}
            <th>Verificado</th>
          </tr>
        </thead>
        <tbody>
          {records.map((r) => (
            <tr key={r.id} className="border-b border-slate-100">
              <td className="py-2">{episodeCode(r.episode_id)}</td>
              {fields.map((f) => (
                <td key={f}>
                  <select
                    value={r[f]}
                    onChange={(e) => update.mutate({ id: r.id, field: f, value: e.target.value })}
                    className="rounded-md border border-slate-300 px-1 py-1 text-xs"
                  >
                    {ARCHIVE_COMPONENT_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </td>
              ))}
              <td>
                {r.archive_verified ? (
                  <span className="text-xs text-emerald-700">✔ {r.verified_by}</span>
                ) : (
                  <button
                    onClick={() => {
                      const name = prompt("Nombre de quien verifica el archivo:");
                      if (name) verify.mutate({ id: r.id, verifiedBy: name });
                    }}
                    className="text-xs text-brand-600 hover:underline"
                  >
                    Verificar
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ActividadTab({ projectId }: { projectId: number }) {
  const { data } = useQuery({ queryKey: ["activity", projectId], queryFn: () => activityApi.list(projectId) });
  if (!data || data.length === 0) return <EmptyState message="Sin actividad registrada en este proyecto." />;
  return (
    <ul className="divide-y divide-slate-100 text-sm">
      {data.map((a) => (
        <li key={a.id} className="flex items-center justify-between py-2">
          <div>
            <span className="font-medium text-slate-700">{a.event_type.replace(/_/g, " ")}</span>
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
