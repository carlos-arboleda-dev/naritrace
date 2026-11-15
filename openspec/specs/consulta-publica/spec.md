# consulta-publica Specification

## Purpose
Define la consulta pública, sin autenticación, que permite a cualquier consumidor verificar el origen y el recorrido de un lote publicado a partir de su código QR.

## Requirements

### Requirement: Consulta pública por código
El sistema SHALL exponer `GET /api/publico/trazabilidad/{codigo}/` sin requerir autenticación y SHALL devolver la información pública del lote cuyo `codigo` coincida y cuyo estado sea `publicado`.

#### Scenario: Código publicado
- **WHEN** un visitante consulta el código de un lote en estado `publicado`
- **THEN** el sistema responde `200` con el resumen del producto, el productor, la finca, la línea de tiempo y las certificaciones

#### Scenario: Código inexistente
- **WHEN** el visitante consulta un código que no existe
- **THEN** el sistema responde `404` con el mensaje "No existe un lote publicado con ese código"

#### Scenario: Lote no publicado
- **WHEN** el visitante consulta el código de un lote en estado `borrador`, `en_transito`, `entregado` o `archivado`
- **THEN** el sistema responde `404` y no revela información del lote

### Requirement: Ruta pública alternativa en el recurso de lotes
El sistema SHALL exponer `GET /api/lotes/por-codigo/{codigo}/` como ruta pública alternativa que aplica la misma regla de mostrar únicamente lotes publicados.

#### Scenario: Consulta por ruta alternativa
- **WHEN** se consulta un lote publicado mediante `/api/lotes/por-codigo/{codigo}/`
- **THEN** el sistema responde con el mismo contenido público que la ruta `/api/publico/trazabilidad/{codigo}/`

#### Scenario: Código no publicado por ruta alternativa
- **WHEN** se consulta un lote no publicado mediante la ruta alternativa
- **THEN** el sistema responde `404` con el mensaje "Lote no encontrado"

### Requirement: Contenido mínimo de la ficha pública
La ficha pública SHALL incluir `codigo`, datos del producto, `variedad`, `cantidad`, `unidad`, `fecha_cosecha`, `proceso`, `notas_produccion`, datos públicos del productor, datos de la finca, `linea_tiempo`, `certificaciones` y `fecha_publicacion`.

#### Scenario: Datos del productor
- **WHEN** se consulta un lote publicado
- **THEN** el productor se muestra con nombre completo o nombre de usuario, municipio e indicador de verificación, sin datos de contacto privados

#### Scenario: Datos de la finca
- **WHEN** se consulta un lote publicado con geolocalización registrada
- **THEN** la ficha incluye nombre, municipio, vereda, departamento, latitud y longitud de la finca

#### Scenario: Finca sin coordenadas
- **WHEN** la finca no tiene latitud o longitud registradas
- **THEN** la ficha devuelve `null` en esos campos sin fallar

### Requirement: Línea de tiempo pública
La ficha pública SHALL incluir los movimientos del lote ordenados cronológicamente de forma ascendente, con tipo legible, actor, origen, destino, descripción, fecha y geolocalización cuando exista.

#### Scenario: Recorrido cronológico
- **WHEN** un lote tiene movimientos de cosecha, transporte y entrega
- **THEN** la ficha los presenta en ese orden cronológico con el nombre legible de cada tipo

#### Scenario: Lote sin movimientos
- **WHEN** un lote publicado no tiene movimientos registrados
- **THEN** la ficha devuelve `linea_tiempo` como lista vacía

### Requirement: Acceso desde el código QR
El frontend SHALL ofrecer una ruta pública `/trazabilidad/:codigo` que consume la consulta pública y muestra la historia de origen del lote sin exigir inicio de sesión.

#### Scenario: Escaneo de QR
- **WHEN** un consumidor abre la URL contenida en el QR de un lote publicado
- **THEN** el frontend carga la ficha pública con el producto, la finca, el productor y la línea de tiempo

#### Scenario: QR de lote no disponible
- **WHEN** la consulta pública responde `404`
- **THEN** el frontend muestra un mensaje indicando que no se encontró información o que el lote no está publicado

#### Scenario: Consulta desde la landing
- **WHEN** un visitante usa el buscador de la landing con un código válido
- **THEN** el frontend navega a `/trazabilidad/<codigo>` y muestra la ficha pública
