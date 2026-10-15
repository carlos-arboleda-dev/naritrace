# NariTrace

> Trazabilidad agropecuaria desde el campo hasta tu mesa.

Plataforma web que permite registrar, seguir y verificar el recorrido completo de productos agropecuarios (cacao, café, acuicultura, entre otros) desde la finca hasta el consumidor final, mediante códigos QR y registros inmutables.

## Problema

En Colombia no existe una forma estandarizada de verificar el origen de un producto agropecuario. El ICA reconoce que su sistema de trazabilidad vegetal está incompleto. La regulación europea EUDR exigirá, a partir de 2025, geolocalización exacta y prueba de no deforestación para exportar.

## Solución

Cada lote de producto recibe un código QR único. Al escanearlo, cualquier consumidor accede al historial completo del producto: quién lo produjo, en qué finca, en qué fecha, qué procesos tuvo y por dónde pasó.

## Stack técnico

- **Backend:** Django + Django REST Framework
- **Frontend:** Angular 22
- **Base de datos:** PostgreSQL (SQLite en desarrollo)
- **Documentación API:** Swagger (drf-spectacular)
- **Inmutabilidad:** Hyperledger Fabric
- **Geolocalización:** Leaflet + polígonos GeoJSON

## Estructura del repositorio
