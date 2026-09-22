import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { risksApi } from "../api/endpoints";
import { RiskCard } from "../components/RiskCard";
import { Card, EmptyState, ErrorState, Spinner } from "../components/Common";

export function RisksPage() {
  const queryClient = useQueryClient();
  const { data: risks, isLoading, isError } = useQuery({ queryKey: ["risks"], queryFn: () => risksApi.list() });
  const runEngine = useMutation({
    mutationFn: risksApi.run,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["risks"] }),
  });
  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => risksApi.updateStatus(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["risks"] }),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          Riesgos generados por reglas deterministas (sin IA). Cada riesgo indica evidencia y acción sugerida.
        </p>
        <button
          onClick={() => runEngine.mutate()}
          disabled={runEngine.isPending}
          className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {runEngine.isPending ? "Evaluando…" : "Reevaluar riesgos"}
        </button>
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorState message="No se han podido cargar los riesgos." />}
      {risks && risks.length === 0 && <EmptyState message="No hay riesgos abiertos." />}

      <div className="space-y-3">
        {risks?.map((risk) => (
          <Card key={risk.id}>
            <RiskCard risk={risk} />
            <div className="mt-2 flex justify-end gap-2 text-xs">
              {risk.status !== "ACKNOWLEDGED" && (
                <button onClick={() => updateStatus.mutate({ id: risk.id, status: "ACKNOWLEDGED" })} className="rounded px-2 py-1 text-slate-500 hover:bg-slate-100">
                  Reconocer
                </button>
              )}
              {risk.status !== "IN_PROGRESS" && (
                <button onClick={() => updateStatus.mutate({ id: risk.id, status: "IN_PROGRESS" })} className="rounded px-2 py-1 text-slate-500 hover:bg-slate-100">
                  Marcar acción en curso
                </button>
              )}
              <button onClick={() => updateStatus.mutate({ id: risk.id, status: "CLOSED" })} className="rounded px-2 py-1 text-slate-500 hover:bg-slate-100">
                Cerrar
              </button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
