# Seguridad y limitaciones — SOUND X-POST (MVP)

## Advertencia principal

**Este MVP no implementa autenticación ni autorización real.** Cualquier
proceso con acceso a la API puede leer y modificar cualquier proyecto. Está
pensado exclusivamente para un entorno de laboratorio con datos ficticios.
**No apto para producción.**

## Qué se ha hecho

- **Validación de entrada**: todos los endpoints usan esquemas Pydantic;
  no se aceptan payloads arbitrarios.
- **Sin SQL arbitrario**: no existe ningún endpoint que ejecute SQL directo
  proporcionado por el cliente. Todas las consultas usan el ORM
  (SQLAlchemy), lo que evita inyección SQL por construcción.
- **Sin acceso a filesystem arbitrario**: no hay endpoints que lean rutas de
  disco proporcionadas por el usuario. El futuro Filesystem Scanner deberá
  limitarse a *roots* autorizados y operar en solo lectura (ver
  docs/BACKLOG.md).
- **Verificación humana explícita**: `ArchiveRecord.archive_verified` no
  puede activarse sin indicar `verified_by`; el backend lo rechaza
  (`400 Bad Request`) si falta.
- **Separación de evidencia vs. inferencia**: cada `Risk` guarda
  `evidence` (qué se ha observado) y `suggested_action` por separado de la
  `severity`, para que un humano pueda verificar la base de cada alerta.
- **CORS restringido** a los orígenes de desarrollo del frontend
  (`localhost:5173`) — debe revisarse antes de cualquier despliegue.
- **Sin credenciales en el repositorio**: `.env.example` no contiene
  secretos; la configuración real se inyecta por variables de entorno.
- **Datos DEMO**: ningún dato de producción, nombre real de cliente o ruta
  real de proyecto se usa en las semillas de demostración.

## Qué falta antes de cualquier uso real

| Área | Estado |
| --- | --- |
| Autenticación de usuarios (login, sesiones/JWT) | No implementado |
| Autorización por rol (`ADMIN`, `SUPERVISOR`, `COORDINATOR`, `EDITOR`, `MIXER`, `QC`, `ARCHIVE`, `VIEWER`) | Modelo de datos preparado (`User.role`), **no aplicado** en los endpoints |
| Auditoría de operaciones sensibles más allá del event log de negocio | Parcial (ActivityLog cubre cambios de negocio, no accesos) |
| Rate limiting / protección contra abuso de la API | No implementado |
| HTTPS / despliegue detrás de proxy con TLS | Pendiente de decisión de IT |
| Revisión de dependencias (SCA) | No realizada en este MVP |

## Separación conceptual (según especificación)

- **PRODUCTION DATA**: no existe en este repositorio; solo datos DEMO.
- **OPERATIONAL METADATA**: modelo de datos de este MVP (proyectos, tareas,
  ADR, outputs, archivo, riesgos, actividad).
- **EXTERNAL INTEGRATIONS**: no implementadas; solo hay diseño de
  interfaces desacopladas pendiente de desarrollo (docs/BACKLOG.md).

## Recomendación antes de exponer esto fuera de un laboratorio local

1. Añadir autenticación real (OIDC/SSO corporativo si está disponible) y
   aplicar los roles ya modelados en el backend (no solo en el frontend).
2. Añadir HTTPS y CORS restringido al dominio real.
3. Ejecutar un análisis de dependencias y un pentest básico de la API.
4. Migrar a PostgreSQL con backups gestionados por IT.
