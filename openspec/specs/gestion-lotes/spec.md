# gestion-lotes Specification

## Purpose
Define la creación, identificación, clasificación por estados y publicación de los lotes, que son la unidad trazable central de NariTrace.

## Requirements

### Requirement: Registro de lotes
El sistema SHALL permitir crear lotes con `finca`, `producto`, `cantidad`, `fecha_cosecha` y `unidad`; opcionalmente `variedad`, `proceso` y `notas_produccion`. La cantidad MUST ser mayor o igual a cero y las relaciones con finca y producto MUST existir.

#### Scenario: Crear lote válido
- **WHEN** un usuario autenticado envía `POST /api/lotes/` con finca, producto, cantidad y fecha de cosecha válidos
- **THEN** el sistema crea el lote en estado `borrador` y responde `201`

#### Scenario: Cantidad inválida
- **WHEN** se envía una cantidad negativa
- **THEN** el sistema responde `400` y no crea el lote

#### Scenario: Finca o producto inexistente
- **WHEN** se envía el identificador de una finca o un producto que no existe
- **THEN** el sistema responde `400` y no crea el lote

### Requirement: Código único y UUID del lote
Al guardar un lote nuevo, el sistema SHALL generar un `codigo` único con el formato `NT-<año>-<primeros 6 caracteres del UUID en mayúsculas>` y SHALL asignarle un `uuid` único. Ambos campos SHALL ser de solo lectura.

#### Scenario: Generación automática de código
- **WHEN** se crea un lote sin código
- **THEN** el sistema genera un código con prefijo `NT-`, el año actual y seis caracteres hexadecimales derivados del UUID

#### Scenario: Código inmutable
- **WHEN** se intenta enviar un `codigo` o `uuid` en la creación o actualización
- **THEN** el sistema ignora el valor enviado y conserva el generado automáticamente

### Requirement: Contenido del código QR
Al crear un lote, el sistema SHALL generar el campo `qr_codigo` con la URL pública del frontend que apunta a la vista de trazabilidad del lote.

#### Scenario: QR generado
- **WHEN** un lote recibe su código único
- **THEN** el sistema completa `qr_codigo` con una URL con formato `http://localhost:4200/trazabilidad/<codigo>`

#### Scenario: Visualización del QR
- **WHEN** el productor abre el detalle de un lote
- **THEN** el frontend muestra un código QR construido a partir de `qr_codigo`

### Requirement: Estados del lote
Cada lote SHALL encontrarse en uno de los estados `borrador`, `publicado`, `en_transito`, `entregado` o `archivado`. Todo lote nuevo SHALL iniciar en `borrador`.

#### Scenario: Estado inicial
- **WHEN** se crea un lote
- **THEN** su estado es `borrador` y la fecha de publicación permanece vacía

#### Scenario: Estado legible
- **WHEN** se consulta un lote
- **THEN** la respuesta incluye `estado_display` con el nombre legible del estado

### Requirement: Publicación de un lote
El sistema SHALL exponer `POST /api/lotes/{id}/publicar/` para publicar un lote en estado `borrador`. La operación SHALL cambiar el estado a `publicado`, registrar la fecha de publicación y devolver el código y el contenido del QR.

#### Scenario: Publicar lote en borrador
- **WHEN** el usuario autenticado publica un lote en estado `borrador`
- **THEN** el sistema cambia el estado a `publicado`, guarda `fecha_publicacion` y responde con `mensaje` y `qr_codigo`

#### Scenario: Publicar lote ya publicado
- **WHEN** se intenta publicar un lote cuyo estado no es `borrador`
- **THEN** el sistema responde `400` con el error "Solo se pueden publicar lotes en borrador" y no modifica el lote

### Requirement: Consulta y filtrado de lotes
El sistema SHALL exponer el listado paginado de lotes y SHALL permitir filtrar por `estado`, `producto`, `finca` y buscar por `codigo`, nombre de producto o `variedad` mediante `search`.

#### Scenario: Filtrar por estado
- **WHEN** se consulta `/api/lotes/?estado=publicado`
- **THEN** el sistema devuelve únicamente lotes publicados

#### Scenario: Buscar por código
- **WHEN** se consulta `/api/lotes/?search=NT-2026`
- **THEN** el sistema devuelve los lotes cuyo código contiene ese texto

#### Scenario: Filtrar por finca y producto
- **WHEN** se consulta `/api/lotes/?finca=1&producto=2`
- **THEN** el sistema devuelve los lotes que cumplen ambos filtros

### Requirement: Visibilidad de lotes por rol
El sistema SHALL mostrar a un usuario con rol `productor` únicamente los lotes que le pertenecen. Los demás roles autenticados y las consultas anónimas SHALL ver el listado completo.

#### Scenario: Productor consulta sus lotes
- **WHEN** un productor consulta `GET /api/lotes/`
- **THEN** la respuesta contiene solo lotes cuyo `productor` es él

#### Scenario: Asignación automática al crear
- **WHEN** un usuario con rol `productor` crea un lote
- **THEN** el sistema lo asigna como `productor` del lote

### Requirement: Detalle compuesto del lote
La consulta de un lote individual SHALL devolver sus datos completos, el producto y la finca anidados, la lista de movimientos y la lista de certificaciones asociadas.

#### Scenario: Detalle de lote
- **WHEN** se consulta `GET /api/lotes/{id}/`
- **THEN** la respuesta incluye `producto`, `finca`, `movimientos` y `certificaciones` además de los datos del lote

#### Scenario: Representación resumida en listados
- **WHEN** se consulta el listado de lotes
- **THEN** cada elemento incluye `producto_nombre`, `finca_nombre`, `productor_nombre`, `estado_display` y `total_movimientos`
