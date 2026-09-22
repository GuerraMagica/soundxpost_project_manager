import { Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { Dashboard } from "./pages/Dashboard";
import { ProjectsList } from "./pages/ProjectsList";
import { ProjectDetail } from "./pages/ProjectDetail";
import { TasksPage } from "./pages/TasksPage";
import { ADRPage } from "./pages/ADRPage";
import { DeliveryPage, QCPage } from "./pages/DeliveryPage";
import { ArchivePage } from "./pages/ArchivePage";
import { RisksPage } from "./pages/RisksPage";
import { ActivityPage } from "./pages/ActivityPage";
import { CalendarPage } from "./pages/CalendarPage";
import { MixesPage } from "./pages/MixesPage";
import { PlaceholderPage, UsersPage } from "./pages/AdminPages";

function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/riesgos" element={<RisksPage />} />
        <Route path="/calendario" element={<CalendarPage />} />
        <Route path="/proyectos" element={<ProjectsList />} />
        <Route path="/proyectos/:id" element={<ProjectDetail />} />
        <Route path="/adr" element={<ADRPage />} />
        <Route path="/mezclas" element={<MixesPage />} />
        <Route path="/qc" element={<QCPage />} />
        <Route path="/entregas" element={<DeliveryPage />} />
        <Route path="/archivo" element={<ArchivePage />} />
        <Route path="/tareas" element={<TasksPage />} />
        <Route path="/actividad" element={<ActivityPage />} />
        <Route
          path="/admin/plantillas"
          element={<PlaceholderPage title="Plantillas de proyecto" note="Configuración de plantillas por tipo de proyecto. Disponible en un milestone futuro." />}
        />
        <Route
          path="/admin/integraciones"
          element={<PlaceholderPage title="Integraciones" note="Microsoft Graph, Planner, Filesystem Scanner, PGPTSession y QC PDF requieren aprobación de IT y credenciales reales." />}
        />
        <Route path="/admin/usuarios" element={<UsersPage />} />
        <Route
          path="/admin/configuracion"
          element={<PlaceholderPage title="Configuración" note="Ajustes generales del laboratorio. Disponible en un milestone futuro." />}
        />
      </Routes>
    </AppShell>
  );
}

export default App;
