# Spec Delta

## Purpose

Define los eventos o movimientos que registran el recorrido de un lote a lo largo de la cadena de suministro y que alimentan su línea de tiempo.

## ADDED Requirements

### Requirement: Registro de movimientos
El sistema SHALL permitir registrar movimientos asociados a un lote con `tipo`, `descripcion`, `origen`, `destino` y geolocalización opcional. El `tipo` SHALL ser uno de `cosecha`, `beneficio`, `acopio`, `transporte`, `distribucion`, `entrega`, `certificacion` u `otro`.

#### Scenario: Registrar evento
- **WHEN** un usuario autenticado envía `POST /api/movimientos/` con un lote y un tipo válido
- **THEN** el sistema crea el movimiento, registra la fecha automáticamente y responde `201`

#### Scenario: Tipo inválido
- **WHEN** se envía un tipo que no pertenece a las opciones permitidas
- **THEN** el sistema responde `400` y no crea el movimiento

#### Scenario: Lote inexistente
- **WHEN** se envía el identificador de un lote que no existe
- **THEN** el sistema responde `400` y no crea el movimiento

### Requirement: Actor responsable del movimiento
El sistema SHALL asignar como `actor` del movimiento al usuario autenticado que lo crea. El campo `actor` SHALL ser de solo lectura y MUST rechazarse cualquier intento de suplantarlo desde la petición.

#### Scenario: Actor automático
- **WHEN** un usuario autenticado registra un movimiento
- **THEN** el movimiento queda asociado a ese usuario como responsable

#### Scenario: Actor enviado por el cliente
- **WHEN** la petición incluye un `actor` distinto al usuario autenticado
- **THEN** el sistema ignora el valor y conserva al usuario autenticado

### Requirement: Fecha y orden de los movimientos
Cada movimiento SHALL registrar su fecha de creación automáticamente y SHALL ser de solo lectura. El listado por defecto SHALL ordenarse del más reciente al más antiguo.

#### Scenario: Fecha automática
- **WHEN** se crea un movimiento
- **THEN** el sistema asigna la fecha y hora del servidor sin aceptar una fecha enviada por el cliente

#### Scenario: Orden descendente en la API
- **WHEN** se consulta `GET /api/movimientos/` sin filtros
- **THEN** los movimientos aparecen ordenados por fecha descendente

### Requirement: Consulta de movimientos por lote
El sistema SHALL permitir filtrar los movimientos por el parámetro `lote` y SHALL devolver en cada movimiento los campos legibles `tipo_display` y `actor_nombre`.

#### Scenario: Historial de un lote
- **WHEN** se consulta `/api/movimientos/?lote=5`
- **THEN** el sistema devuelve únicamente los movimientos del lote 5 con su tipo y actor legibles

#### Scenario: Lote sin movimientos
- **WHEN** se consulta el historial de un lote que no tiene movimientos
- **THEN** el sistema devuelve una lista vacía con `200`

### Requirement: Actualización y eliminación de movimientos
El sistema SHALL permitir actualizar y eliminar movimientos existentes mediante la API. Estas operaciones MUST requerir autenticación.

#### Scenario: Editar descripción
- **WHEN** un usuario autenticado actualiza la descripción de un movimiento
- **THEN** el sistema persiste el cambio y lo devuelve en la siguiente consulta

#### Scenario: Eliminar movimiento
- **WHEN** un usuario autenticado elimina un movimiento
- **THEN** el sistema lo retira del historial del lote y responde `204`

### Requirement: Hash de blockchain reservado
Cada movimiento SHALL disponer de un campo `hash_blockchain` de solo lectura, destinado a un futuro registro inmutable. En el estado actual el campo permanece vacío y no se calcula ningún hash.

#### Scenario: Movimiento sin hash
- **WHEN** se crea un movimiento en el estado actual del sistema
- **THEN** `hash_blockchain` queda vacío y el cliente no puede asignarle valor
