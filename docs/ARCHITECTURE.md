# Arquitectura — SOUND X-POST (MVP)

## Visión general

```mermaid
flowchart LR
  subgraph Frontend [React + TS + Vite + Tailwind]
    UI[Sidebar / Dashboard / Tabs de proyecto]
  end
  subgraph Backend [FastAPI]
    API[Routers REST]
    RE[Risk Engine\n(reglas Python deterministas)]
    ORM[SQLAlchemy models]
  end
  DB[(SQLite\n→ PostgreSQL futuro)]

  UI -- fetch JSON --> API
  API --> ORM
  ORM --> DB
  API -- POST /api/risks/run --> RE
  RE --> ORM
```

- El frontend **no contiene datos hardcodeados**: toda la información se
  obtiene de la API mediante TanStack Query.
- La autorización de negocio (crear, actualizar, verificar archivo, etc.) se
  valida en el backend, no solo ocultando botones en el frontend.
- El motor de riesgos es una función Python pura sobre el estado de la base
  de datos; no depende de IA ni de servicios externos.

## Modelo de datos (resumen)

- `Project` → `Episode` (1:N). Un proyecto de tipo `SERIES` puede tener
  varios episodios (`S01E01`, `S01E02`, ...); otros tipos de proyecto usan
  la misma tabla `Episode` como unidad de trabajo (film, promocional, etc.).
- `Task`: tareas ClickUp-like, con `origin_risk_id` opcional para trazar
  tareas generadas por el motor de riesgos.
- `ADREntry`: unidad de seguimiento = proyecto + episodio + personaje +
  convocatoria (nunca cue a cue).
- `Output`: ciclo de vida QC de un entregable (`PM_VO_5_1`, `MNE_2_0`,
  `DX_STEM`, etc.) — estados `NOT_STARTED…PASSED`.
- `DeliveryPackage`: independiente de `Output`; el motor de riesgos compara
  versiones entre ambos para detectar incoherencias.
- `ArchiveRecord`: componentes de archivo por episodio + verificación humana
  explícita (`archive_verified` solo se puede activar indicando
  `verified_by`).
- `Risk`: incluye `dedupe_key` único para garantizar idempotencia.
- `ActivityLog`: event log por proyecto/episodio, usado como fuente para
  futuras automatizaciones ("qué ha cambiado desde ayer").

Todas las columnas de estado son `String`, no `Enum` nativo de SQL, para
poder ampliar los valores permitidos sin migraciones de esquema.

## Motor de riesgos

Implementado en `backend/app/risk_engine/rules.py`. Cada regla:

1. Consulta el estado actual de la base de datos.
2. Genera `RiskCandidate` con una `dedupe_key` estable (p. ej.
   `f"ADR_RECORDED_NOT_RECEIVED:{entry.id}"`).
3. El motor (`run_risk_engine`) hace *upsert* de cada candidato: si ya existe
   un riesgo con esa clave, lo actualiza en vez de duplicarlo; si el riesgo
   ya no aplica (la condición desapareció), se marca `CLOSED`
   automáticamente mientras conserva su historial.

Reglas implementadas en el MVP:

1. Mezcla próxima sin ADR Composite confirmado.
2. ADR grabado pero no recibido.
3. Output aprobado ausente del Delivery Package.
4. Delivery Package con versión anterior al último output aprobado.
5. QC pendiente de cierre cerca de la entrega.
6. Archivo sin cuesheet / sin stems.

Reglas del enunciado pendientes para el siguiente milestone: "cambio de
imagen posterior al último output de mezcla" (requiere integración con
DaVinci/filesystem, fuera de alcance del MVP local).

## Por qué SQLite en el MVP

- Cero dependencias de infraestructura para correr en un Mac de desarrollo.
- SQLAlchemy + Alembic abstraen el dialecto SQL: migrar a PostgreSQL en el
  futuro solo requiere cambiar `DATABASE_URL` (ver `app/config.py`) y
  revisar tipos específicos de SQLite si los hubiera (no se usan en este
  esquema).

## Decisiones explícitas de esta iteración

Por petición del usuario, se eliminaron del alcance del MVP: Windmill,
Baserow, Supabase/Firebase, servicios de IA externos, servidores MCP,
integraciones reales con Outlook/Planner/almacenamiento corporativo, y
Docker como requisito de ejecución local.
