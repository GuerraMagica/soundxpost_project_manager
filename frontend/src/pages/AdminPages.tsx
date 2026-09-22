import { useQuery } from "@tanstack/react-query";
import { usersApi } from "../api/endpoints";
import { EmptyState } from "../components/Common";

export function PlaceholderPage({ title, note }: { title: string; note: string }) {
  return (
    <div className="space-y-3">
      <h2 className="text-base font-semibold text-slate-800">{title}</h2>
      <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        PENDIENTE DE INTEGRACIÓN — {note}
      </div>
    </div>
  );
}

export function UsersPage() {
  const { data } = useQuery({ queryKey: ["users"], queryFn: usersApi.list });
  return (
    <div className="space-y-3">
      <p className="text-sm text-slate-500">
        Usuarios DEMO del laboratorio. La gestión de roles/permisos reales requiere autenticación de producción
        (no implementada en este MVP).
      </p>
      {!data || data.length === 0 ? (
        <EmptyState message="Sin usuarios registrados." />
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
              <th className="py-2">Nombre</th><th>Email</th><th>Rol</th>
            </tr>
          </thead>
          <tbody>
            {data.map((u) => (
              <tr key={u.id} className="border-b border-slate-100">
                <td className="py-2">{u.name}</td>
                <td className="text-slate-500">{u.email}</td>
                <td className="text-slate-500">{u.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
