# Spec Delta

## Purpose

Define cómo se registran los usuarios de NariTrace, cómo se autentican mediante token y qué roles determinan su acceso al sistema.

## ADDED Requirements

### Requirement: Registro público de usuarios
El sistema SHALL permitir crear una cuenta sin autenticación mediante `POST /api/usuarios/registro/`, aceptando `username`, `email`, `password`, `first_name`, `last_name`, `rol`, `telefono` y `municipio`. La contraseña SHALL almacenarse cifrada y MUST tener al menos 8 caracteres.

#### Scenario: Registro exitoso
- **WHEN** un visitante envía datos válidos a `/api/usuarios/registro/`
- **THEN** el sistema crea el usuario, cifra la contraseña y responde `201` con un mensaje de confirmación y los datos del usuario sin exponer la contraseña

#### Scenario: Contraseña demasiado corta
- **WHEN** el visitante envía una contraseña de menos de 8 caracteres
- **THEN** el sistema responde con error de validación `400` y no crea el usuario

#### Scenario: Nombre de usuario duplicado
- **WHEN** el visitante intenta registrarse con un `username` ya existente
- **THEN** el sistema responde con error de validación `400` y no crea un segundo usuario

### Requirement: Inicio de sesión por token
El sistema SHALL exponer `POST /api/token/` para intercambiar `username` y `password` por un token de autenticación de Django REST Framework. Las peticiones autenticadas SHALL enviar el token en la cabecera `Authorization: Token <token>`.

#### Scenario: Credenciales válidas
- **WHEN** un usuario envía credenciales correctas a `/api/token/`
- **THEN** el sistema responde `200` con un objeto que contiene la propiedad `token`

#### Scenario: Credenciales inválidas
- **WHEN** un usuario envía credenciales incorrectas a `/api/token/`
- **THEN** el sistema responde `400` y no emite token

#### Scenario: Cliente almacena la sesión
- **WHEN** el frontend recibe un token válido
- **THEN** lo guarda en `localStorage` bajo la clave `token` y lo adjunta a las peticiones privadas

### Requirement: Roles de usuario
Cada usuario SHALL tener exactamente un rol entre `productor`, `acopiador`, `transportador`, `administrador` y `cliente`. Si no se especifica, el rol SHALL ser `cliente`. El sistema MUST rechazar valores de rol fuera de esa lista.

#### Scenario: Rol por defecto
- **WHEN** se crea un usuario sin enviar `rol`
- **THEN** el usuario queda con rol `cliente`

#### Scenario: Rol inválido
- **WHEN** se envía un rol que no pertenece a las opciones definidas, por ejemplo `distribuidor`
- **THEN** el sistema responde `400` y no crea el usuario

### Requirement: Cierre de sesión en el cliente
El frontend SHALL permitir cerrar la sesión eliminando el token almacenado y redirigiendo al inicio de sesión.

#### Scenario: Cierre de sesión
- **WHEN** el usuario autenticado pulsa "Cerrar Sesión" en el dashboard
- **THEN** el frontend elimina el token de `localStorage` y navega a `/login`

### Requirement: Acceso de lectura pública y escritura autenticada
Los endpoints de consulta SHALL ser accesibles sin autenticación, mientras que las operaciones de escritura SHALL requerir un usuario autenticado. Las excepciones SHALL ser el registro y la consulta pública de trazabilidad, que son abiertos.

#### Scenario: Lectura anónima
- **WHEN** un visitante sin token consulta un listado de productos, fincas, lotes, movimientos o certificaciones
- **THEN** el sistema responde `200` con la información permitida

#### Scenario: Escritura anónima
- **WHEN** un visitante sin token intenta crear o modificar un recurso protegido
- **THEN** el sistema responde `401` o `403` y no persiste el cambio
