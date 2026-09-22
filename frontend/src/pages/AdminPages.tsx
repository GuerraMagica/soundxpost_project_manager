import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { usersApi } from "../api/endpoints";
import { EmptyState } from "../components/Common";
import { useAuth } from "../auth/AuthContext";

const ROLES = ["ADMIN", "SUPERVISOR", "COORDINATOR", "EDITOR", "MIXER", "QC", "ARCHIVE", "VIEWER"];

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

function NewUserForm({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("VIEWER");
  const [department, setDepartment] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const create = useMutation({
    mutationFn: () => usersApi.create({ name, email, role, department: department || undefined, password }),
    onSuccess: () => {
      setOpen(false);
      setName("");
      setEmail("");
      setPassword("");
      setDepartment("");
      onCreated();
    },
    onError: (e: Error) => setError(e.message),
  });

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700">
        + Nuevo usuario
      </button>
    );
  }

  return (
    <form
      className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm space-y-3"
      onSubmit={(e) => {
        e.preventDefault();
        create.mutate();
      }}
    >
      {error && <div className="rounded-md bg-red-50 p-2 text-xs text-red-700">{error}</div>}
      <div className="grid grid-cols-2 gap-3">
        <label className="text-xs font-medium text-slate-600">
          Nombre
          <input required value={name} onChange={(e) => setName(e.target.value)} className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
        </label>
        <label className="text-xs font-medium text-slate-600">
          Email
          <input required type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
        </label>
        <label className="text-xs font-medium text-slate-600">
          Rol
          <select value={role} onChange={(e) => setRole(e.target.value)} className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm">
            {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </label>
        <label className="text-xs font-medium text-slate-600">
          Departamento / disciplina
          <input value={department} onChange={(e) => setDepartment(e.target.value)} className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
        </label>
        <label className="text-xs font-medium text-slate-600 col-span-2">
          Contraseña inicial
          <input required type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm" />
        </label>
      </div>
      <div className="flex justify-end gap-2">
        <button type="button" onClick={() => setOpen(false)} className="rounded-md px-3 py-1.5 text-sm text-slate-600">Cancelar</button>
        <button type="submit" disabled={create.isPending} className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
          Crear usuario
        </button>
      </div>
    </form>
  );
}

export function UsersPage() {
  const { user: currentUser } = useAuth();
  const queryClient = useQueryClient();
  const { data } = useQuery({ queryKey: ["users"], queryFn: usersApi.list });
  const toggleActive = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) => usersApi.update(id, { is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          Usuarios del laboratorio. Los roles determinan los permisos verificados en el backend
          (ver docs/SECURITY.md). Solo ADMIN puede crear o desactivar usuarios.
        </p>
        {currentUser?.role === "ADMIN" && <NewUserForm onCreated={() => queryClient.invalidateQueries({ queryKey: ["users"] })} />}
      </div>
      {!data || data.length === 0 ? (
        <EmptyState message="Sin usuarios registrados." />
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
              <th className="py-2">Nombre</th><th>Email</th><th>Rol</th><th>Departamento</th><th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {data.map((u) => (
              <tr key={u.id} className="border-b border-slate-100">
                <td className="py-2">{u.name}</td>
                <td className="text-slate-500">{u.email}</td>
                <td className="text-slate-500">{u.role}</td>
                <td className="text-slate-500">{u.department ?? "—"}</td>
                <td>
                  {currentUser?.role === "ADMIN" ? (
                    <button
                      onClick={() => toggleActive.mutate({ id: u.id, is_active: !u.is_active })}
                      className={`text-xs ${u.is_active ? "text-emerald-700" : "text-slate-400"}`}
                    >
                      {u.is_active ? "Activo" : "Desactivado"}
                    </button>
                  ) : (
                    <span className="text-xs text-slate-500">{u.is_active ? "Activo" : "Desactivado"}</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
