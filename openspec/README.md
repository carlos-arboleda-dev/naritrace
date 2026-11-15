# OpenSpec — NariTrace

Esta carpeta contiene la documentación de línea base del sistema NariTrace, generada con OpenSpec 2.0 (esquema `spec-driven`) a partir del código existente. No se modificó código fuente.

## Índice

### Especificaciones vigentes

| Capacidad | Qué cubre | Requisitos |
|---|---|---|
| [`autenticacion`](specs/autenticacion/spec.md) | Registro, login por token, roles y cierre de sesión | 5 |
| [`catalogo-productos`](specs/catalogo-productos/spec.md) | Catálogo de productos y filtros | 3 |
| [`gestion-fincas`](specs/gestion-fincas/spec.md) | Registro, ubicación y visibilidad de fincas | 5 |
| [`gestion-lotes`](specs/gestion-lotes/spec.md) | Lotes, código único, QR, estados y publicación | 8 |
| [`eventos-trazabilidad`](specs/eventos-trazabilidad/spec.md) | Movimientos y línea de tiempo | 6 |
| [`consulta-publica`](specs/consulta-publica/spec.md) | Consulta por QR sin autenticación | 5 |
| [`certificaciones`](specs/certificaciones/spec.md) | Certificaciones de fincas y lotes | 5 |

### Documento del cambio (archivado)

El cambio que produjo esta documentación está en:

[`changes/archive/2026-11-15-documentacion-inicial/`](changes/archive/2026-11-15-documentacion-inicial/)

- [`proposal.md`](changes/archive/2026-11-15-documentacion-inicial/proposal.md): propósito, problema, alcance, módulos y estado verificado.
- [`design.md`](changes/archive/2026-11-15-documentacion-inicial/design.md): arquitectura, tecnologías, carpetas, componentes, modelo de datos, API, decisiones y riesgos.
- [`tasks.md`](changes/archive/2026-11-15-documentacion-inicial/tasks.md): inventario de funcionalidades implementadas, parciales y pendientes, mejoras y deuda técnica.
- `specs/`: copia de los deltas que originaron las especificaciones vigentes.

Se archivó con `openspec archive documentacion-inicial`, por lo que `openspec/specs/` es ahora la fuente de verdad del comportamiento actual.

## Estado resumido

- **Implementado:** registro/login, roles, productos, fincas, lotes, QR, publicación, movimientos, certificaciones (backend), consulta pública y las pantallas principales de Angular.
- **Parcial:** panel de administración Angular (endpoint faltante), autorización por objeto, rol en el cliente, geolocalización/mapas, UI de certificaciones y productos.
- **Pendiente:** Hyperledger Fabric, auditoría, verificación de correo, recuperación de contraseña, PostgreSQL, entornos, guards, pruebas y despliegue.
- **Bloqueante actual:** `trazabilidad/urls.py` importa `EstadisticasAdminView`, que no existe; `manage.py check` falla y el backend no inicia. Ver `tasks.md`, deuda técnica.

## Comandos útiles

```bash
openspec list --specs                  # ver capacidades documentadas
openspec show gestion-lotes --type spec
openspec validate --specs --strict     # validar todas las especificaciones
openspec view                          # dashboard interactivo
```

## Fuentes de verdad

1. **Código** en `backend/` y `frontend/` (fuente primaria utilizada para esta documentación).
2. **Especificaciones** en `openspec/specs/` (contrato de comportamiento observable).
3. **Estado y deuda** en el `tasks.md` archivado.
4. **Documentación de API** generada en `/api/docs/` cuando el backend esté operativo.

Si el comportamiento cambia, el flujo correcto es crear un nuevo cambio OpenSpec (`openspec new change <nombre>`) con sus deltas de especificación, no editar directamente las specs sin pasar por el flujo.
