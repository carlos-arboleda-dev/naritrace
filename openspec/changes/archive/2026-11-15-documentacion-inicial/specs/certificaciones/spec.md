# Spec Delta

## Purpose

Define las certificaciones que respaldan prácticas o atributos de una finca o de un lote y que pueden mostrarse al consumidor en la ficha pública.

## ADDED Requirements

### Requirement: Registro de certificaciones
El sistema SHALL permitir crear certificaciones con `tipo`, `entidad_certificadora`, `numero_certificado`, `fecha_emision`, `fecha_vencimiento`, `documento` y estado `activa`. El `tipo` SHALL ser uno de `organica`, `comercio_justo`, `rainforest`, `utz`, `libre_deforestacion` u `otra`.

#### Scenario: Crear certificación válida
- **WHEN** un usuario autenticado envía `POST /api/certificaciones/` con un tipo válido
- **THEN** el sistema crea la certificación y responde `201`

#### Scenario: Tipo inválido
- **WHEN** se envía un tipo fuera de las opciones permitidas
- **THEN** el sistema responde `400` y no crea la certificación

#### Scenario: Carga de documento
- **WHEN** se adjunta un archivo en el campo `documento`
- **THEN** el sistema lo almacena en el directorio `certificaciones/` de los archivos media y devuelve su URL

### Requirement: Asociación a finca o lote
Una certificación SHALL poder asociarse a una finca, a un lote, o a ambos. Los campos `finca` y `lote` SHALL ser opcionales según el modelo actual.

#### Scenario: Certificación de finca
- **WHEN** se crea una certificación con `finca` y sin `lote`
- **THEN** la certificación queda asociada únicamente a esa finca

#### Scenario: Certificación de lote
- **WHEN** se crea una certificación con `lote` y sin `finca`
- **THEN** la certificación queda asociada únicamente a ese lote y aparece en su detalle

### Requirement: Consulta y filtrado de certificaciones
El sistema SHALL exponer el listado paginado de certificaciones y SHALL permitir filtrar por `finca` y por `lote`.

#### Scenario: Certificaciones de un lote
- **WHEN** se consulta `/api/certificaciones/?lote=3`
- **THEN** el sistema devuelve las certificaciones asociadas al lote 3

#### Scenario: Certificaciones de una finca
- **WHEN** se consulta `/api/certificaciones/?finca=1`
- **THEN** el sistema devuelve las certificaciones asociadas a la finca 1

### Requirement: Vigencia y estado
Cada certificación SHALL indicar si está `activa` y SHALL almacenar sus fechas de emisión y vencimiento cuando se conozcan. La API SHALL incluir `tipo_display` con el nombre legible del tipo.

#### Scenario: Certificación activa
- **WHEN** se crea una certificación sin especificar `activa`
- **THEN** la certificación queda activa por defecto

#### Scenario: Fechas opcionales
- **WHEN** se crea una certificación sin fecha de emisión o de vencimiento
- **THEN** el sistema la crea con esos campos vacíos sin fallar

### Requirement: Visualización pública de certificaciones
La ficha pública de un lote publicado SHALL incluir las certificaciones asociadas al lote y SHALL mostrar el nombre legible de cada tipo.

#### Scenario: Lote con certificaciones
- **WHEN** un consumidor consulta un lote publicado que tiene certificaciones
- **THEN** la ficha muestra cada certificación con su `tipo_display`

#### Scenario: Lote sin certificaciones
- **WHEN** un consumidor consulta un lote publicado sin certificaciones
- **THEN** la ficha no muestra la sección de certificaciones
