# Tasks

> Este archivo cumple dos funciones: registra las tareas de **esta documentación** (con checkboxes rastreables por OpenSpec) y deja un inventario verificable del estado del producto. Los ítems de estado del producto usan viñetas sin checkbox para no confundirse con tareas pendientes de este cambio documental.

## 1. Documentación generada

- [x] 1.1 Documentar propósito, problema, alcance y estado actual en `proposal.md`; verificado leyendo el README raíz y el código de ambos módulos.
- [x] 1.2 Documentar arquitectura, carpetas, componentes, modelo de datos, API, decisiones y riesgos en `design.md`; verificado contra `settings.py`, `urls.py`, modelos, serializers y vistas.
- [x] 1.3 Crear la especificación de autenticación en `specs/autenticacion/spec.md`; verificado contra `usuarios/models.py`, `serializers.py`, `views.py` y `settings.py`.
- [x] 1.4 Crear la especificación de catálogo en `specs/catalogo-productos/spec.md`; verificado contra `Producto` y `ProductoViewSet`.
- [x] 1.5 Crear la especificación de fincas en `specs/gestion-fincas/spec.md`; verificado contra `Finca`, `FincaSerializer` y `FincaViewSet`.
- [x] 1.6 Crear la especificación de lotes en `specs/gestion-lotes/spec.md`; verificado contra `Lote`, sus serializers y `LoteViewSet`.
- [x] 1.7 Crear la especificación de eventos en `specs/eventos-trazabilidad/spec.md`; verificado contra `Movimiento` y `MovimientoViewSet`.
- [x] 1.8 Crear la especificación de consulta pública en `specs/consulta-publica/spec.md`; verificado contra `TrazabilidadPublicaViewSet`, el serializer público y la ruta Angular.
- [x] 1.9 Crear la especificación de certificaciones en `specs/certificaciones/spec.md`; verificado contra `Certificacion` y `CertificacionViewSet`.
- [x] 1.10 Ejecutar `openspec validate documentacion-inicial --strict` y corregir hallazgos; verificado por salida del comando.
- [x] 1.11 Verificar que no se modificó código fuente; verificado con `git diff` limitado a `openspec/` y archivos generados por `openspec init`.

## 2. Funcionalidades implementadas

- ✅ **Registro de usuarios** (`POST /api/usuarios/registro/`) con contraseña cifrada y validación mínima de 8 caracteres.
- ✅ **Inicio de sesión por token** (`POST /api/token/`) y uso de `Authorization: Token`.
- ✅ **Modelo de roles** (`productor`, `acopiador`, `transportador`, `administrador`, `cliente`).
- ✅ **Catálogo de productos** con CRUD, categorías, filtro por categoría y búsqueda por nombre.
- ✅ **Gestión de fincas** con CRUD, ubicación, geolocalización opcional y filtro por municipio.
- ✅ **Gestión de lotes** con CRUD, código único, UUID, QR, estados, filtros y detalle anidado.
- ✅ **Publicación de lotes** (`POST /api/lotes/{id}/publicar/`) con fecha de publicación.
- ✅ **Movimientos por lote** con actor automático, fecha automática y filtro por lote.
- ✅ **Certificaciones** con CRUD, tipos, documento y asociación a finca o lote.
- ✅ **Consulta pública** por código para lotes publicados, sin autenticación.
- ✅ **Frontend de landing, login, registro, dashboard, listas, formularios, detalle y ficha pública**.
- ✅ **Generación y visualización de QR** en el detalle del lote con `angularx-qrcode`.
- ✅ **Django Admin** registrado para usuarios, productos, fincas, lotes, movimientos y certificaciones.
- ✅ **OpenAPI/Swagger/Redoc** configurados con drf-spectacular.
- ✅ **Datos de ejemplo** en SQLite (2 productos, 3 fincas, 3 lotes, 2 movimientos, 2 usuarios).

## 3. Funcionalidades parcialmente implementadas

- ⚠️ **Panel de administración Angular**: existen la ruta `/dashboard/admin` y el componente `AdminPanelComponent`, pero el endpoint `/api/estadisticas/` no está implementado y el backend no arranca por esa causa. El enlace del sidebar además nunca se muestra porque `rol` no está definido en `DashboardComponent`.
- ⚠️ **Autorización por rol**: solo filtra fincas y lotes por productor. No hay permisos por objeto; cualquier usuario autenticado puede editar o eliminar recursos ajenos.
- ⚠️ **Visibilidad de lotes publicados**: la ficha pública restringe a `publicado`, pero los endpoints CRUD permiten lectura anónima de borradores.
- ⚠️ **Rol en el cliente**: existe `setUserRole`/`getUserRole`, pero el rol nunca se guarda tras el login; no hay guard de rutas ni menú condicionado real.
- ⚠️ **Registro de distribuidores**: la UI ofrece `distribuidor`, valor que no existe en `Usuario.Rol`; el backend rechaza el registro.
- ⚠️ **Geolocalización**: se almacenan latitud, longitud y GeoJSON, pero no hay mapa, validación geoespacial ni Leaflet integrado.
- ⚠️ **QR**: se genera una URL fija a `localhost:4200`; no es configurable por entorno ni se valida su contenido.
- ⚠️ **Certificaciones en UI**: el backend está completo, pero no hay pantalla para crearlas o gestionarlas; solo se muestran en la ficha pública.
- ⚠️ **Catálogo de productos en UI**: no hay pantalla CRUD; solo aparece como selector al crear un lote.
- ⚠️ **Manejo de errores**: los componentes registran errores en consola y muestran mensajes genéricos; no hay interceptores ni feedback uniforme.

## 4. Funcionalidades pendientes

- ⏳ **Corregir el arranque del backend**: implementar `EstadisticasAdminView` o retirar la ruta `/api/estadisticas/`.
- ⏳ **Integración con Hyperledger Fabric**: la app `blockchain` está vacía y los campos `hash_blockchain` nunca se llenan.
- ⏳ **Auditoría**: la app `auditoria` está vacía; no hay bitácora de cambios ni trazabilidad de acciones.
- ⏳ **Verificación de usuarios**: el campo `verificado` existe, pero no hay flujo de verificación ni de correo.
- ⏳ **Recuperación de contraseña**: el enlace "¿Olvidaste tu contraseña?" no tiene implementación.
- ⏳ **Gestión de certificaciones desde la UI**.
- ⏳ **Gestión de productos desde la UI**.
- ⏳ **Mapa de fincas y validación de polígonos** (Leaflet/GeoJSON).
- ⏳ **Endpoint de perfil o `/me`** para recuperar rol y datos del usuario autenticado.
- ⏳ **Guards de autenticación y autorización en Angular**.
- ⏳ **Configuración de entornos Angular** (`environment.ts`) en lugar de URL fija.
- ⏳ **PostgreSQL en desarrollo/producción** y uso real de `DATABASE_URL`.
- ⏳ **Despliegue, CI/CD, Docker y monitoreo**.
- ⏳ **Documentación de API propia y guía de contribución** (hoy solo Swagger generado y README de producto).

## 5. Mejoras técnicas identificadas

- 🔧 Implementar permisos DRF por objeto y una matriz de permisos por rol (productor, acopiador, transportador, administrador, cliente).
- 🔧 Separar la lógica de generación de código/QR de `Lote.save()` hacia un servicio de dominio y hacer configurable la URL pública.
- 🔧 Añadir validación de que `Certificacion` tenga al menos `finca` o `lote`, y evitar certificaciones huérfanas.
- 🔧 Añadir validación de rangos de latitud/longitud y de estructura GeoJSON.
- 🔧 Incorporar filtros, ordenamiento y búsqueda con `django-filter`/`OrderingFilter` en lugar de parámetros manuales.
- 🔧 Usar `reverse()` o un setting para el contenido del QR.
- 🔧 Exponer solo los campos necesarios en listados públicos y impedir la lectura de borradores.
- 🔧 Centralizar el estado de sesión en un servicio Angular y añadir `HttpInterceptor`, `AuthGuard` y manejo global de errores.
- 🔧 Corregir `DashboardComponent` para declarar `rol` e importar `CommonModule` o migrar a `@if`.
- 🔧 Unificar la UI con el modelo de roles (eliminar `distribuidor` o agregarlo al modelo).
- 🔧 Sustituir `ChangeDetectorRef.detectChanges()` por el flujo reactivo de Angular (`async` pipe / signals).
- 🔧 Configurar un mailer SMTP real en `MAILERS` y el flujo de verificación por correo.
- 🔧 Añadir `pre-commit`, linters (ESLint/Ruff) y formateo automatizado.

## 6. Deuda técnica

- 🔴 **Bloqueante:** `ImportError` por `EstadisticasAdminView`; el backend no inicia.
- 🔴 **Seguridad:** ausencia de autorización por objeto; cualquier autenticado puede modificar recursos ajenos.
- 🔴 **Privacidad:** lectura anónima de lotes en borrador y de datos de fincas/productores no previstos para publicación.
- 🟠 **Pruebas:** `backend/*/tests.py` vacíos; los `*.spec.ts` son plantillas con imports incorrectos (por ejemplo `Login` en lugar de `LoginComponent`, `Api` en lugar de `ApiService`), por lo que no validan nada.
- 🟠 **Configuración:** `DATABASE_URL` documentada pero ignorada; `DEBUG` depende de `.env`; no hay settings por entorno.
- 🟠 **URLs hardcodeadas:** `API_URL` en el frontend y `qr_codigo` en el backend.
- 🟠 **Código muerto:** archivos `.html` de componentes que usan plantilla inline; `landing.html`, `lista-lotes.html`, `lista-fincas.html`, `trazabilidad-publica.html`, `dashboard.html`, `admin-panel.html` no se usan.
- 🟠 **Dependencias sin uso:** `ngx-echarts`/`echarts` se registran en `app.config.ts` pero no se usan; `psycopg2-binary` no se aprovecha.
- 🟡 **UX:** sin paginación en la UI (solo se lee `results`), sin estados de carga/errores consistentes, sin confirmación antes de publicar.
- 🟡 **Calidad:** serializers y vistas con lógica repetida; falta tipado fuerte en el frontend (`any` generalizado).
- 🟡 **Documentación:** README del frontend es el genérico de Angular CLI; `docs/wireframes/` está vacío.
- 🟡 **Accesibilidad/i18n:** `index.html` declara `lang="en"`; textos y fechas en español pero sin estrategia i18n.

## 7. Verificación de esta documentación

- [x] 7.1 Verificar que `openspec/specs/` contiene una especificación por cada capacidad declarada; comprobado con `openspec list --specs` tras la sincronización/archivo.
- [x] 7.2 Verificar que el frontend compila con `npx ng build`; ejecutado con salida en `/tmp/opencode/naritrace-dist` (sin tocar `dist/` del proyecto).
- [x] 7.3 Verificar el fallo del backend con `.venv/bin/python manage.py check`; documentado como deuda bloqueante.
- [x] 7.4 Verificar que los archivos de código fuente no fueron modificados por esta tarea; comprobado con `git status`.
