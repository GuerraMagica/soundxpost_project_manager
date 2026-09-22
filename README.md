# SOUND X-POST — Virtual Postproduction Coordinator

MVP local de una plataforma de coordinación de postproducción de sonido, con
la filosofía de producto de ClickUp (espacio centralizado, proyectos,
listas/board/calendario, estados, riesgos) aplicada al vocabulario técnico
real de un departamento de sonido (ADR, QC, Printmaster, M&E, Stems, Foley,
Delivery Package, etc.).

> **Entorno de laboratorio.** Todos los datos son ficticios (DEMO). La
> autenticación es local (email + contraseña, JWT) y **no** es apta para
> producción — ver [docs/SECURITY.md](docs/SECURITY.md).

## Stack

| Capa | Tecnología |
| --- | --- |
| Frontend | React + TypeScript + Vite + Tailwind CSS v4 + React Router + TanStack Query |
| Backend | Python + FastAPI + Pydantic |
| ORM / migraciones | SQLAlchemy 2.0 + Alembic |
| Base de datos | SQLite (MVP) — preparada para migrar a PostgreSQL sin cambios de código |
| Motor de riesgos | Reglas Python deterministas (sin IA) |

No se usa Windmill, Baserow, Supabase/Firebase, IA externa, MCP ni Docker
para esta primera versión. Ver [docs/BACKLOG.md](docs/BACKLOG.md) para el
plan de integraciones futuras.

## Estructura del repositorio

```
backend/          API FastAPI, modelos SQLAlchemy, motor de riesgos, migraciones Alembic, tests
  app/
    models.py      Entidades: Project, Episode, Task, ADREntry, Output, DeliveryPackage,
                    ArchiveRecord, Risk, ActivityLog, User
    routers/        Endpoints REST por módulo
    risk_engine/    Reglas deterministas + motor de evaluación idempotente
    demo_seed.py    Datos DEMO ficticios (PROYECTO_DEMO, S01, 6 episodios)
  alembic/          Migraciones de esquema
  tests/            Tests de motor de riesgos y flujo de API
frontend/          React + TS + Tailwind, consume la API real (sin datos hardcodeados)
docs/              Arquitectura, seguridad/limitaciones, backlog
```

## Requisitos

- Python 3.9+ (probado con el Python del sistema en macOS)
- Node.js 18+ y npm

## Puesta en marcha (macOS)

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # opcional, valores por defecto ya funcionan

# Crea el esquema de la base de datos SQLite
alembic upgrade head

# Carga datos DEMO ficticios (idempotente, no duplica si ya existen)
python -m app.demo_seed

# Arranca la API
uvicorn app.main:app --reload --port 8000
```

La API queda disponible en `http://127.0.0.1:8000` y la documentación
interactiva (Swagger) en `http://127.0.0.1:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # opcional; por defecto apunta a http://127.0.0.1:8000
npm run dev
```

Abre `http://localhost:5173` en el navegador. Serás redirigido a `/login`.

Usuarios DEMO disponibles (contraseña común, ver `backend/app/demo_seed.py`):
`demo.admin@soundxpost.local` (ADMIN), `demo.supervisor@...`, `demo.coordinator@...`,
`demo.dialogue@...`, `demo.foley@...`, `demo.mixer@...`, `demo.qc@...`, `demo.archive@...`.
Contraseña: `DemoSoundXPost2026!`.

### 3. Tests del backend

```bash
cd backend
source .venv/bin/activate
pytest -q
```

Los tests cubren: creación de proyectos/episodios/tareas/ADR vía API,
detección de riesgos por regla, idempotencia del motor de riesgos, cierre
automático de riesgos cuando la condición desaparece, login/JWT, creación de
usuarios y membresías de proyecto, y rechazo de escrituras no autorizadas.

## Flujo funcional verificado en este MVP

1. Iniciar sesión con un usuario DEMO (`/login`).
2. Crear un proyecto desde la interfaz (`Proyectos → + Nuevo proyecto`).
3. Añadir episodios y asignar fechas de mezcla/entrega.
4. Añadir miembros a un proyecto (pestaña `Miembros`) y comprobar que un
   usuario no perteneciente al proyecto recibe `403` al intentar modificarlo.
5. Crear tareas y moverlas entre estados (vista Lista, Board y Calendario).
6. Registrar y actualizar convocatorias ADR (personaje + convocatoria, no cue
   a cue).
7. Registrar Outputs/QC y Delivery Packages, y ver cómo el motor de riesgos
   detecta versiones inconsistentes u outputs aprobados sin entrega.
8. Consultar y reevaluar la Bandeja de riesgos (`Riesgos` / botón
   "Reevaluar riesgos"), verificando que no se duplican.
9. Revisar el histórico de actividad por proyecto.

Todo lo anterior persiste en `backend/soundxpost.db` (SQLite) y se sirve a
través de la API real — no hay datos hardcodeados en el frontend.

## Qué está implementado, simulado o pendiente

| Elemento | Estado |
| --- | --- |
| CRUD de proyectos, episodios, tareas, ADR, outputs, delivery, archivo | **Implementado** |
| Autenticación local (JWT) y matriz de permisos por rol | **Implementado** — ver docs/SECURITY.md |
| Membresías de proyecto (`ProjectMembership`), colaboradores de tarea | **Implementado** |
| Motor de riesgos determinista (9 reglas del enunciado → 6 implementadas en el MVP) | **Implementado** |
| Registro de actividad (event log) | **Implementado** |
| Dashboard "Centro Operativo" | **Implementado** |
| Datos DEMO ficticios | **Implementado** |
| Calendario interactivo (drag-and-drop), Gantt, notificaciones/email | **Pendiente** — ver docs/BACKLOG.md (Milestone 2.3+) |
| SSO/OIDC corporativo | **Pendiente** (requiere aprobación de IT) |
| Integración con Microsoft Graph / Outlook / Planner | **Pendiente de integración** (requiere aprobación de IT) |
| Filesystem Scanner (SMB) | **Pendiente de integración** |
| Importación PGPTSession / QC PDF | **Pendiente de integración** |
| MCP servers | **Pendiente** (fuera del alcance de este MVP) |
| Migración a PostgreSQL | **Preparado, no ejecutado** (basta con cambiar `DATABASE_URL`) |

Más detalle en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) y
[docs/BACKLOG.md](docs/BACKLOG.md).

## Limitaciones conocidas / no verificado en esta sesión

- No se ha probado el arranque en Windows con rutas UNC (fuera de alcance del MVP).
- No se ha verificado el comportamiento con datasets grandes (rendimiento).
- La autenticación es JWT local de laboratorio (sin SSO/OIDC corporativo, sin expiración configurable por IT).
- El motor de riesgos se ejecuta bajo demanda (botón "Reevaluar riesgos"), no hay scheduler en background en este MVP.
- No hay calendario interactivo con drag-and-drop, Gantt ni notificaciones todavía (Milestone 2.3+, ver docs/BACKLOG.md).
