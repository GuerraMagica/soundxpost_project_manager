import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deliveryApi, projectsApi } from "../api/endpoints";
import { EmptyState, ErrorState, Spinner } from "../components/Common";
import { StatusBadge } from "../components/Badges";

const OUTPUT_STATUSES = ["NOT_STARTED", "WIP", "OUTPUT_READY", "IN_QC", "QC_FAIL", "PASSED", "N_A"];
const DELIVERY_STATUSES = ["PENDING", "BUILDING", "READY", "FINAL", "DELIVERED", "N_A"];

export function DeliveryPage() {
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: () => projectsApi.list() });
  const [projectFilter, setProjectFilter] = useState<number | "">("");
  const filters = projectFilter === "" ? {} : { project_id: projectFilter };

  const { data: outputs, isLoading: loadingOutputs, isError: errorOutputs } = useQuery({
    queryKey: ["outputs", "all", projectFilter],
    queryFn: () => deliveryApi.listOutputs(filters),
  });
  const { data: packages, isLoading: loadingPackages, isError: errorPackages } = useQuery({
    queryKey: ["packages", "all", projectFilter],
    queryFn: () => deliveryApi.listPackages(filters),
  });
  const queryClient = useQueryClient();
  const updateOutput = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => deliveryApi.updateOutput(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["outputs", "all"] }),
  });
  const updatePackage = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => deliveryApi.updatePackage(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["packages", "all"] }),
  });

  const projectName = (id: number) => projects?.find((p) => p.id === id)?.name ?? `#${id}`;

  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-500">
        Los Outputs/QC y el Delivery Package se gestionan por separado. PASSED significa que el output ha superado QC;
        FINAL/DELIVERED se refieren al paquete de entrega, no al output en sí.
      </p>
      <select value={projectFilter} onChange={(e) => setProjectFilter(e.target.value ? Number(e.target.value) : "")} className="rounded-md border border-slate-300 px-2 py-1.5 text-sm">
        <option value="">Todos los proyectos</option>
        {projects?.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
      </select>

      <section>
        <h2 className="mb-2 text-sm font-semibold text-slate-800">Outputs / QC</h2>
        {loadingOutputs && <Spinner />}
        {errorOutputs && <ErrorState message="No se han podido cargar los outputs." />}
        {outputs && outputs.length === 0 && <EmptyState message="Sin outputs registrados." />}
        {outputs && outputs.length > 0 && (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
                <th className="py-2">Proyecto</th><th>Material</th><th>Versión</th><th>Ronda QC</th><th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {outputs.map((o) => (
                <tr key={o.id} className="border-b border-slate-100">
                  <td className="py-2 text-slate-500">{projectName(o.project_id)}</td>
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
      </section>

      <section>
        <h2 className="mb-2 text-sm font-semibold text-slate-800">Delivery Package</h2>
        {loadingPackages && <Spinner />}
        {errorPackages && <ErrorState message="No se han podido cargar los Delivery Packages." />}
        {packages && packages.length === 0 && <EmptyState message="Sin Delivery Packages registrados." />}
        {packages && packages.length > 0 && (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
                <th className="py-2">Proyecto</th><th>Material</th><th>Versión</th><th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {packages.map((p) => (
                <tr key={p.id} className="border-b border-slate-100">
                  <td className="py-2 text-slate-500">{projectName(p.project_id)}</td>
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
      </section>
    </div>
  );
}

export function QCPage() {
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: () => projectsApi.list() });
  const { data: outputs, isLoading, isError } = useQuery({
    queryKey: ["outputs", "qc-view"],
    queryFn: () => deliveryApi.listOutputs(),
  });
  const projectName = (id: number) => projects?.find((p) => p.id === id)?.name ?? `#${id}`;
  const inQc = (outputs ?? []).filter((o) => ["IN_QC", "QC_FAIL"].includes(o.status));

  if (isLoading) return <Spinner />;
  if (isError) return <ErrorState message="No se ha podido cargar el estado de QC." />;
  if (inQc.length === 0) return <EmptyState message="No hay materiales actualmente en QC." />;

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
          <th className="py-2">Proyecto</th><th>Material</th><th>Versión</th><th>Ronda</th><th>Estado</th>
        </tr>
      </thead>
      <tbody>
        {inQc.map((o) => (
          <tr key={o.id} className="border-b border-slate-100">
            <td className="py-2 text-slate-500">{projectName(o.project_id)}</td>
            <td>{o.material_type}</td>
            <td>{o.version}</td>
            <td>{o.qc_round}</td>
            <td><StatusBadge status={o.status} /></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
