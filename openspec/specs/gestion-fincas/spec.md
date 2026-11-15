# gestion-fincas Specification

## Purpose
Define el registro y la consulta de las fincas donde se originan los lotes, incluyendo su ubicación y datos geográficos opcionales.

## Requirements

### Requirement: Registro de fincas
El sistema SHALL permitir crear fincas con `nombre`, `municipio`, `vereda` y `departamento`; opcionalmente `latitud`, `longitud`, `area_hectareas` y `poligono_geojson`. El departamento SHALL tomar "Nariño" por defecto y la finca SHALL quedar activa al crearse.

#### Scenario: Crear finca con datos mínimos
- **WHEN** un productor autenticado envía `POST /api/fincas/` con nombre y municipio
- **THEN** el sistema crea la finca, la marca como activa y responde `201`

#### Scenario: Crear finca con geolocalización
- **WHEN** el productor envía latitud, longitud, área y polígono GeoJSON válidos
- **THEN** el sistema almacena esos valores y los devuelve en la consulta de la finca

#### Scenario: Datos obligatorios ausentes
- **WHEN** se intenta crear una finca sin nombre o sin municipio
- **THEN** el sistema responde `400` y no crea la finca

### Requirement: Asignación automática del productor
Al crear una finca mediante la API con un usuario de rol `productor`, el sistema SHALL asignar automáticamente a ese usuario como `productor` de la finca, ignorando cualquier valor enviado en ese campo.

#### Scenario: Productor crea su finca
- **WHEN** un usuario con rol `productor` crea una finca
- **THEN** la finca queda asociada a ese usuario y el campo `productor` no puede ser suplantado desde la petición

### Requirement: Visibilidad de fincas por rol
El sistema SHALL mostrar a un usuario con rol `productor` únicamente sus propias fincas. Los demás roles autenticados y las consultas anónimas SHALL ver el listado completo.

#### Scenario: Productor consulta sus fincas
- **WHEN** un productor consulta `GET /api/fincas/`
- **THEN** la respuesta contiene solo fincas cuyo `productor` es él

#### Scenario: Consulta anónima
- **WHEN** un visitante sin autenticación consulta `GET /api/fincas/`
- **THEN** el sistema devuelve el listado paginado de fincas activas e inactivas registradas

### Requirement: Filtro por municipio y conteo de lotes
El sistema SHALL permitir filtrar fincas por coincidencia parcial de `municipio` y SHALL incluir en cada finca el número total de lotes asociados.

#### Scenario: Filtrar por municipio
- **WHEN** se consulta `/api/fincas/?municipio=Buesaco`
- **THEN** el sistema devuelve las fincas cuyo municipio contiene "Buesaco"

#### Scenario: Conteo de lotes
- **WHEN** se consulta una finca que tiene tres lotes
- **THEN** la respuesta incluye `total_lotes` con el valor `3`

### Requirement: Actualización y eliminación de fincas
El sistema SHALL permitir actualizar y eliminar fincas mediante los métodos `PUT`, `PATCH` y `DELETE` del recurso. La eliminación SHALL estar protegida cuando existan lotes asociados.

#### Scenario: Actualizar ubicación
- **WHEN** se actualiza la latitud y longitud de una finca existente
- **THEN** el sistema persiste los nuevos valores y los devuelve en la siguiente consulta

#### Scenario: Eliminar finca con lotes
- **WHEN** se intenta eliminar una finca que tiene lotes asociados
- **THEN** el sistema rechaza la operación y conserva la finca y sus lotes
