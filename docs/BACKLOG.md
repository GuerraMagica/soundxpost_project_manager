# Backlog — SOUND X-POST

## Milestone 2 (próximo, tras validar el MVP 1)

- Autenticación real + aplicación de roles en el backend (no solo en la UI).
- Scheduler en background para el motor de riesgos (hoy se ejecuta bajo
  demanda desde la UI).
- Regla de riesgo: "cambio de imagen posterior al último output de mezcla"
  (requiere señal de edición de imagen / DaVinci).
- Importador PGPTSession (ADR SUMMARY → `ADREntry`, sin sobrescribir
  convocatorias existentes).
- Vista de calendario mensual completa (hoy es una lista de próximos 7 días).
- Plantillas de proyecto configurables por tipo (`SERIES`, `FEATURE_FILM`, …).

## Milestone 3 (integraciones corporativas — requieren aprobación de IT)

- Filesystem Scanner de solo lectura sobre rutas SMB/UNC autorizadas.
- Microsoft Graph: lectura de correo y calendario para proponer
  actualizaciones (nunca automáticas).
- Microsoft Planner (si IT lo autoriza).
- Importador de QC PDF.

## Milestone 4 (extensibilidad)

- Servidores MCP que reutilicen la misma API de negocio que ya usa el
  frontend (no lógica duplicada).
- Migración de SQLite a PostgreSQL en despliegue interno del facility.
- Panel de administración de plantillas y configuración.

## Explícitamente fuera de alcance hasta nueva decisión

- Windmill, Baserow, Supabase/Firebase u otros servicios cloud.
- Cualquier servicio de IA externo.
- Automatizaciones que escriban/borren/renombren archivos.
- Envío o borrado automático de correos.
