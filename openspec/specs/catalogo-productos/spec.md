# catalogo-productos Specification

## Purpose
Define el catálogo maestro de productos agropecuarios que pueden asociarse a los lotes trazables y los filtros disponibles para consultarlo.

## Requirements

### Requirement: Catálogo de productos
El sistema SHALL permitir administrar productos agropecuarios con `nombre` único, `categoria`, `descripcion`, `unidad_medida`, indicador `activo` y fecha de creación. Las categorías válidas SHALL ser `cafe`, `cacao`, `acuicultura`, `frutas`, `pancoger` y `otro`.

#### Scenario: Crear producto
- **WHEN** un usuario autenticado envía `POST /api/productos/` con un nombre único y una categoría válida
- **THEN** el sistema crea el producto y lo devuelve con su categoría legible

#### Scenario: Nombre duplicado
- **WHEN** se intenta crear un producto cuyo nombre ya existe
- **THEN** el sistema responde `400` y no crea un duplicado

#### Scenario: Categoría inválida
- **WHEN** se envía una categoría fuera de las opciones permitidas
- **THEN** el sistema responde `400` y no crea el producto

### Requirement: Consulta y filtrado del catálogo
El sistema SHALL exponer `GET /api/productos/` con paginación de 20 elementos y SHALL permitir filtrar por `categoria` y buscar por coincidencia parcial de nombre mediante el parámetro `search`.

#### Scenario: Filtrar por categoría
- **WHEN** se consulta `/api/productos/?categoria=cafe`
- **THEN** el sistema devuelve únicamente productos de categoría café

#### Scenario: Buscar por nombre
- **WHEN** se consulta `/api/productos/?search=cacao`
- **THEN** el sistema devuelve los productos cuyo nombre contiene "cacao" sin distinguir mayúsculas

#### Scenario: Listado paginado
- **WHEN** existen más de 20 productos y se consulta la primera página
- **THEN** la respuesta incluye `count`, `next`, `previous` y `results` con hasta 20 productos

### Requirement: Representación legible de categoría
Cada producto devuelto por la API SHALL incluir el campo de solo lectura `categoria_display` con el nombre legible de la categoría.

#### Scenario: Categoría legible
- **WHEN** se consulta un producto de categoría `pancoger`
- **THEN** la respuesta incluye `categoria_display` con el valor "Pancoger"
