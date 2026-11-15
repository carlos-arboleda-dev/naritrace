# Proposal: Documentación base del sistema NariTrace

## Why

NariTrace ya cuenta con un MVP funcional (backend Django REST + frontend Angular) pero no tiene documentación de arquitectura ni especificaciones formales. Esto obliga a cada desarrollador o agente de IA a redescubrir la estructura, los contratos de API y el estado real de cada módulo. Se necesita una línea base verificable, alineada con OpenSpec, que distinga lo implementado de lo parcial y lo pendiente antes de seguir construyendo.

## What Changes

- Se documenta el estado **actual** del sistema sin modificar código fuente, modelos, endpoints ni configuración.
- Se crean especificaciones de capacidades existentes en `openspec/specs/` como fuente de verdad del comportamiento observable.
- Se crea este cambio de documentación con `proposal.md`, `design.md`, `tasks.md` y los deltas de especificación correspondientes.
- Se registran explícitamente hallazgos, limitaciones, funcionalidades parciales y deuda técnica verificados en el código.

**No hay cambios de comportamiento.** Este cambio es exclusivamente documental.

## Descripción general del sistema

NariTrace es una plataforma web de trazabilidad agropecuaria orientada a Nariño, Colombia. Permite registrar fincas y lotes de productos (café, cacao, acuicultura, frutas, pancoger), asociar eventos de la cadena de suministro y publicar un lote para que cualquier consumidor consulte su historial mediante un código QR, sin autenticación.

## Problema que resuelve

En Colombia no existe una forma estandarizada de verificar el origen de un producto agropecuario. La regulación europea EUDR exigirá geolocalización y prueba de no deforestación para exportar. NariTrace propone un código único por lote y un historial consultable públicamente.

## Alcance funcional actual

- Registro de usuarios con rol y datos de contacto; autenticación por token.
- Catálogo de productos agropecuarios con categorías y filtros.
- Gestión de fincas con datos de ubicación y geolocalización.
- Gestión de lotes con código único autogenerado, estado y publicación.
- Registro de movimientos/eventos por lote con actor y línea de tiempo.
- Certificaciones asociadas a fincas o lotes (incluye carga de documento).
- Consulta pública de trazabilidad por código, pensada para el escaneo de QR.
- Interfaz Angular: landing, login, registro, dashboard, listas, formularios, detalle de lote con QR y vista pública.
- Administración de datos vía Django Admin.

## Módulos principales

| Módulo | Backend | Frontend | Estado |
|---|---|---|---|
| Usuarios y autenticación | `usuarios` | login, registro, guard de sesión básico | Implementado (autorización por rol parcial) |
| Productos | `trazabilidad.Producto` | selector en creación de lote | Implementado (sin pantalla CRUD propia) |
| Fincas | `trazabilidad.Finca` | lista y creación | Implementado |
| Lotes | `trazabilidad.Lote` | lista, creación, detalle, QR | Implementado |
| Movimientos | `trazabilidad.Movimiento` | alta y línea de tiempo en detalle | Implementado |
| Certificaciones | `trazabilidad.Certificacion` | visualización en vista pública | Backend implementado; UI de gestión ausente |
| Consulta pública | endpoint `/api/publico/trazabilidad/{codigo}/` | vista pública | Implementado |
| Panel administrativo | endpoint de estadísticas incompleto | `admin-panel` | Parcial / no funcional |
| Blockchain | app `blockchain` vacía; campos `hash_blockchain` | — | Pendiente |
| Auditoría | app `auditoria` vacía | — | Pendiente |

## Estado actual verificado

- El frontend Angular compila correctamente (`ng build`), con advertencias de presupuesto y de `*ngIf` sin `CommonModule` en el sidebar.
- El backend **no arranca** en el árbol de trabajo actual: `trazabilidad/urls.py` importa `EstadisticasAdminView`, que no existe en `trazabilidad/views.py` (`ImportError` confirmado con `manage.py check`).
- No hay pruebas automatizadas reales: los archivos `tests.py` y `*.spec.ts` son plantillas.
- SQLite contiene datos de ejemplo (2 productos, 3 fincas, 3 lotes, 2 movimientos, 2 usuarios).

## Capabilities

### New Capabilities

- `autenticacion`: registro de usuarios, inicio de sesión por token y modelo de roles.
- `catalogo-productos`: catálogo de productos agropecuarios y sus filtros.
- `gestion-fincas`: registro y consulta de fincas con ubicación y geolocalización.
- `gestion-lotes`: creación, codificación, estados y publicación de lotes trazables.
- `eventos-trazabilidad`: movimientos que componen la línea de tiempo de un lote.
- `consulta-publica`: consulta sin autenticación de un lote publicado por su código.
- `certificaciones`: certificaciones asociadas a fincas o lotes.

### Modified Capabilities

Ninguna. No existen especificaciones previas en `openspec/specs/` y este cambio no altera comportamiento.

## Impact

- **Código:** ninguno. Solo se agregan archivos bajo `openspec/` y artefactos de instrucciones de OpenCode (`.agents/skills/`, `AGENTS.md` si aplica).
- **APIs:** se documentan las existentes; no se crean ni modifican endpoints.
- **Dependencias:** ninguna nueva.
- **Sistemas:** Django 6.1.2 + DRF, Angular 22, SQLite en desarrollo, drf-spectacular, Bootstrap, ECharts, angularx-qrcode.
- **Riesgo documentado:** el backend está roto en el estado actual del repositorio; las especificaciones describen el comportamiento previsto por el código, no un sistema actualmente ejecutable de punta a punta.
