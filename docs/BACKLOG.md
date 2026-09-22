# Backlog — SOUND X-POST

## Milestone 2 — Coordinación multiusuario (en curso)

- [x] **M2.1** — Ruta de laboratorio sin `:`, `vite.config.ts` con `fs.strict`
  por defecto (sin workaround inseguro).
- [x] **M2.2** — Autenticación JWT local, `ProjectMembership`, colaboradores
  de tarea, matriz de roles verificada en backend (ver docs/SECURITY.md).
- [ ] **M2.3** — Modelo de eventos de calendario (`CalendarEvent`), vistas
  Día/Semana/Mes/Agenda, drag-and-drop con librería MIT (React Big Calendar +
  addon DnD), sincronización con `Episode.mix_date`/`delivery_date` sin
  duplicar la fuente de verdad, zona horaria Europe/Madrid.
- [ ] **M2.4** — Filtros de calendario (proyecto/episodio/usuario/departamento/
  tipo/estado) y vista Gantt (Frappe Gantt, MIT) con dependencias
  EDITORIAL→CONFORM→EDITING→MIX→OUTPUT→QC→DELIVERY.
- [ ] **M2.5** — Bandeja de notificaciones internas + Outbox de email
  simulado (modo DEMO, sin envíos externos reales), política de
  notificación por tipo de evento, preferencias por usuario,
  antiduplicados por `dedupe_key` de evento.
- [ ] **M2.6** — Documentación legal/compliance en `docs/compliance/`
  (borradores para evaluación de IT: privacidad, términos, cookies,
  tratamiento de datos, dependencias de terceros, checklist de aprobación).

Otros pendientes de MVP 1 no bloqueantes para M2:

- Scheduler en background para el motor de riesgos (hoy se ejecuta bajo
  demanda desde la UI o vía `POST /api/risks/run`).
- Regla de riesgo: "cambio de imagen posterior al último output de mezcla"
  (requiere señal de edición de imagen / DaVinci).
- Importador PGPTSession (ADR SUMMARY → `ADREntry`, sin sobrescribir
  convocatorias existentes).
- Plantillas de proyecto configurables por tipo (`SERIES`, `FEATURE_FILM`, …).

## Milestone 3 (integraciones corporativas — requieren aprobación de IT)

- Filesystem Scanner de solo lectura sobre rutas SMB/UNC autorizadas.
- Microsoft Graph: lectura de correo y calendario para proponer
  actualizaciones (nunca automáticas), envío real de email vía SMTP
  corporativo o Microsoft Graph (sustituyendo el Outbox simulado de M2.5).
- Microsoft Planner (si IT lo autoriza).
- Importador de QC PDF.
- SSO/OIDC corporativo (sustituyendo el login JWT local de M2.2).

## Milestone 4 (extensibilidad)

- Servidores MCP que reutilicen la misma API de negocio que ya usa el
  frontend (no lógica duplicada).
- Migración de SQLite a PostgreSQL en despliegue interno del facility.
- Panel de administración de plantillas y configuración.

## Explícitamente fuera de alcance hasta nueva decisión

- Windmill, Baserow, Supabase/Firebase u otros servicios cloud.
- Cualquier servicio de IA externo.
- Automatizaciones que escriban/borren/renombren archivos.
- Envío o borrado automático de correos reales (mientras no exista
  aprobación de IT; ver Milestone 3).
