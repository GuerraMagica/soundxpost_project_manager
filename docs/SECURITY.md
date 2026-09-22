# Seguridad y limitaciones — SOUND X-POST (MVP)

## Advertencia principal

**La autenticación de este MVP es local y de laboratorio** (email + contraseña
con hash bcrypt, JWT propio firmado con un secreto de desarrollo). No hay SSO
corporativo, no hay rotación de secretos gestionada por IT, y el secreto JWT
por defecto (`JWT_SECRET`) **debe sobrescribirse** vía variable de entorno
fuera del laboratorio. Está pensado exclusivamente para datos ficticios.
**No apto para producción sin revisión de IT.**

## Qué se ha hecho

- **Autenticación**: login local (`POST /api/auth/login`) con contraseñas
  con hash `bcrypt` (nunca en texto plano) y tokens JWT de corta duración
  (8 h). Cada endpoint mutador exige `Authorization: Bearer <token>` válido;
  una llamada directa a la API sin token recibe `401`.
- **Autorización por rol verificada en backend** (`app/auth.py`): roles
  `ADMIN`, `SUPERVISOR`, `COORDINATOR`, `EDITOR`, `MIXER`, `QC`, `ARCHIVE`,
  `VIEWER`. La comprobación ocurre en el servidor (`require_roles`,
  `ensure_project_access`), no ocultando botones en el frontend — un usuario
  sin permiso recibe `403` al llamar directamente a la API.
- **Pertenencia a proyecto (`ProjectMembership`)**: solo ADMIN o un miembro
  activo del proyecto puede leer/escribir sus episodios, tareas, ADR,
  outputs, delivery packages, archivo y riesgos.
- **Gestión de usuarios restringida**: solo ADMIN puede crear usuarios,
  cambiar roles o desactivar cuentas (`is_active`).
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
  puede activarse sin indicar `verified_by`, y solo roles ARCHIVE/gestión
  pueden marcarlo; el backend lo rechaza (`400`/`403`) en caso contrario.
- **Separación de evidencia vs. inferencia**: cada `Risk` guarda
  `evidence` (qué se ha observado) y `suggested_action` por separado de la
  `severity`, para que un humano pueda verificar la base de cada alerta.
- **CORS restringido** a los orígenes de desarrollo del frontend
  (`localhost:5173`) — debe revisarse antes de cualquier despliegue.
- **Sin credenciales en el repositorio**: `.env.example` no contiene
  secretos; la configuración real (incluido `JWT_SECRET`) se inyecta por
  variables de entorno.
- **Datos DEMO**: ningún dato de producción, nombre real de cliente o ruta
  real de proyecto se usa en las semillas de demostración. La contraseña
  DEMO compartida (`DemoSoundXPost2026!`) es exclusivamente de laboratorio.

## Qué falta antes de cualquier uso real

| Área | Estado |
| --- | --- |
| SSO/OIDC corporativo | No implementado (arquitectura de `app/auth.py` aislada para poder sustituirlo) |
| Expiración/rotación de `JWT_SECRET` gestionada por IT | No implementado |
| Auditoría de operaciones sensibles más allá del event log de negocio | Parcial (ActivityLog cubre cambios de negocio, no accesos/logins) |
| Rate limiting / protección contra fuerza bruta en login | No implementado |
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
