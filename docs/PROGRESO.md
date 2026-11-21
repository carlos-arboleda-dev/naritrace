# NariTrace — Documento vivo del proyecto

> Se actualiza en cada entrega. **Última actualización:** 21 nov 2026 · **Entrega #3**
> Trazabilidad agropecuaria para Nariño: el productor registra, la cadena opera, el cliente verifica con un QR.

---

## 1. Qué es y cómo está organizado

| Capa | Tecnología | Carpeta |
|---|---|---|
| Backend / API | Django 6 + Django REST Framework (token auth) + SQLite | `backend/` |
| Frontend | Angular (standalone, signals, control flow `@if/@for`) | `frontend/` |
| Documentación | este archivo + wireframes | `docs/` |

### Apps de Django
```
backend/
├── naritrace/            settings, urls raíz (api/token/ → login auditado)
├── usuarios/             Usuario (roles), SolicitudRol, registro
└── trazabilidad/
    ├── models.py         Producto, Finca, Lote, Movimiento, Certificacion, ConsultaPublica,
    │                     BloqueLedger (registro encadenado), EventoAuditoria (bitácora)
    ├── ledger.py         ← sellado SHA-256 encadenado + verificación
    ├── operaciones.py    ← recibir / despachar / entregar (custodia) y movimientos sellados
    ├── auditoria.py      ← auditar(usuario, acción, recurso, detalle)
    ├── permissions.py    EsAdministrador, EsIntermediario
    ├── views.py          API del productor (lotes, fincas, movimientos…) + público
    ├── views_admin.py    API del panel de administración
    ├── views_operaciones.py  API del distribuidor / acopiador / transportador
    └── management/commands/  cargar_catalogo · cargar_demo · sellar_existentes · hacer_admin
```

### Frontend
```
frontend/src/
├── styles.css            tokens de diseño + piezas compartidas (.nt-*)
└── app/
    ├── app.routes.ts     rutas con guard por rol
    ├── guards/rol.guard.ts
    ├── services/         api.ts (productor) · panel-api.ts (admin y distribuidor) · sesion.ts (usuario/rol)
    └── components/
        ├── dashboard/            shell: menú lateral + barra superior, cambia según el rol
        ├── inicio/               /dashboard/resumen → muestra el panel del rol
        ├── resumen/              panel del PRODUCTOR
        ├── crear-lote/           asistente de 4 pasos del productor
        ├── admin-resumen/        portada del ADMINISTRADOR
        ├── admin-seccion/        Productores · Lotes · Municipios · Auditoría · Solicitudes
        ├── distribuidor-resumen/ centro de operaciones del DISTRIBUIDOR
        ├── distribuidor-lista/   Inventario e Historial del distribuidor
        ├── en-revision/          lo que ve una cuenta nueva sin rol aprobado
        ├── icon/ proximamente/ trazabilidad-publica/ + (antiguos) lista-lotes, detalle-lote, fincas…
```

---

## 2. Roles y qué ve cada uno

| Rol (BD) | Panel | Puede |
|---|---|---|
| `productor` | Resumen, Mis lotes, Mi finca, Movimientos*, Documentos* | Registrar lotes (4 pasos), publicar, añadir eventos propios |
| `administrador` | Resumen regional, Productores, Lotes, Municipios, Auditoría, Solicitudes | Ver todo el territorio, aprobar roles, verificar productores, verificar la cadena, exportar |
| `distribuidor` · `acopiador` · `transportador` | Centro de operaciones, Inventario, Historial | Buscar un lote por código, **recibir**, **despachar**, **entregar** |
| `cliente` | "Tu solicitud está en revisión" | Consultar la trazabilidad pública (QR) |

\* pantallas provisionales ("Próximamente").

**Registro:** todo usuario nuevo entra como `cliente` y, si pidió otro rol, se crea una **solicitud** que un administrador aprueba o rechaza. Nadie puede registrarse como administrador.

### Flujo de la cadena (custodia)
```
Productor publica ─► custodio = productor
   Distribuidor RECIBE  ─► custodio = distribuidor      (movimiento "Acopio")
   Distribuidor DESPACHA ─► estado "En tránsito"        (movimiento "Transporte/Distribución")
   Otro actor RECIBE lo en tránsito ─► nuevo custodio
   Custodio ENTREGA ─► estado "Entregado"               (movimiento "Entrega")
```

---

## 3. "Blockchain": inmutabilidad real (registro encadenado)

**Qué hace:** cada lote publicado y cada movimiento se **sellan** con una huella SHA-256 que incluye la del bloque anterior (`BloqueLedger`).

- Cambiar un dato sellado **por la app** está bloqueado (API 409, ORM `ValidationError`): un lote publicado no se edita ni se elimina; los movimientos no se editan ni se eliminan; los bloques y la bitácora son de solo lectura.
- Cambiarlo **directo en la base de datos** (SQL) o **borrar un movimiento o un bloque** se **detecta**: la verificación recomputa todo y señala el primer bloque roto.
- Quién puede verificar: el administrador (cadena completa y por lote), el distribuidor (ficha del lote) y **cualquier cliente** en la página pública del QR (sello "Registro protegido" + huella).
- Se sella lo declarado e inmutable (producto, cantidad, fecha de cosecha, finca, productor…). El **estado** y el **custodio** no, porque cambian legítimamente.

**Límites (honestos):** es una cadena privada, no una red distribuida. Quien controle el servidor *y* reescriba toda la cadena podría hacerlo sin que se note. Para blindarlo frente al operador, el siguiente paso es **anclar** periódicamente el último hash en una red pública (OpenTimestamps, Polygon…).

---

## 4. Diseño (sistema visual)

- **Fuente:** Manrope. **Tokens** en `styles.css`: verde `#074832`, activo `#09714e`, menta `#83deb1`, crema `#f5f2e7`, borde `#d9dccb`.
- **Productor y administrador:** paleta verde (diseños de Figma entregados).
- **Distribuidor:** tema propio — azul petróleo `#0c3c45` + menta azulada + acento **ámbar** `#f2b84b` (se activa con la clase `.tema-dist` del shell; todo el resto usa las mismas variables CSS).
- Piezas compartidas `.nt-*`: tarjetas, KPIs, tablas, botones, píldoras/estados, barras, avisos, campos.
- Ya se ven con el diseño: Resumen del productor, asistente de lote (4 pasos), portada del administrador. El centro de operaciones del distribuidor es diseño propio (no había Figma).

---

## 5. API (resumen)

| Grupo | Endpoints |
|---|---|
| Sesión | `POST /api/token/` (auditado, bloqueo tras 5 fallos/10 min) · `POST /api/usuarios/registro/` · `GET /api/me/` |
| Productor | `/api/lotes/` (+ `publicar/`, `verificar/`) · `/api/fincas/` · `/api/movimientos/` · `/api/productos/` · `/api/estadisticas/` |
| Público (QR) | `GET /api/publico/trazabilidad/<código>/` · `…/<código>/verificar/` |
| Admin | `/api/admin/` → `resumen/` · `auditoria/` · `productores/` (+`<id>/verificar/`) · `lotes/` (+`<id>/verificar/`) · `municipios/` · `solicitudes/` (+`<id>/resolver/`) · `cadena/` (GET/POST) |
| Operaciones | `/api/distribuidor/` → `resumen/` · `lotes/?vista=` · `historial/` · `/api/operaciones/buscar/<código>/` · `/api/operaciones/operar/` |

---

## 6. Qué tiene el panel del administrador (portada)

Fiel al diseño: periodo / departamento / municipio, 4 indicadores, **Lotes por municipio**, **Nuevos lotes publicados**, **Productores por municipio**, **Solicitudes por revisar**, **Registro de auditoría** (filtros, descarga CSV).
**Añadido para potenciarlo:** Integridad de la cadena (con "Verificar ahora"), Preparación **EUDR** (% fincas con coordenadas/polígono), Mix de productos, **Requiere atención** (alertas operativas), Actividad pública (QR más consultados) y **Exportar** el resumen. Las 5 secciones del menú son funcionales (verificar productores, verificar lote, aprobar/rechazar solicitudes, auditoría paginada).

## 7. Qué tiene el panel del distribuidor

**Operación rápida** (pega el código o el enlace del QR → ficha con sello de integridad y línea de tiempo → Recibir / Despachar / Entregar con un clic), 4 indicadores, **tablero por etapas** (Por recibir · En mi custodia · En tránsito), actividad reciente, operaciones por semana, alertas, **Inventario** por pestañas y **Historial** filtrable.

---

## 8. Seguridad corregida en esta entrega
- Cualquiera podía registrarse como administrador → ahora no (entra como cliente + solicitud).
- `/api/lotes/`, `/api/fincas/`, `/api/movimientos/` y certificaciones eran legibles sin iniciar sesión → ahora exigen sesión y filtran por rol.
- Cualquier usuario autenticado podía añadir movimientos a cualquier lote → ahora solo el productor del lote (o los intermediarios por `operar`).
- Movimientos y lotes publicados eran editables/borrables → ahora inmutables.
- Login sin huella ni límite → auditado y con bloqueo temporal.
- Los lotes `en tránsito` / `entregado` ya no desaparecen de la vista pública del QR.

---

## 9. Cómo aplicar esta entrega

Copia cada archivo listado en la sección 10 a su misma ruta dentro de tu proyecto (respeta las carpetas). Luego:

```bash
cd backend && source .venv/bin/activate
python manage.py migrate                 # aplica 0004, 0005 (trazabilidad) y 0002 (usuarios)
python manage.py cargar_catalogo         # catálogo de productos de Nariño
python manage.py sellar_existentes       # sella lotes/movimientos que ya tenías (IMPORTANTE)
python manage.py hacer_admin TU_USUARIO  # conviértete en administrador
python manage.py runserver

cd ../frontend && npm start
```

**¿Quieres verlo todo lleno de datos?** Con una BD nueva (`rm db.sqlite3 && python manage.py migrate`):
```bash
python manage.py cargar_demo
```
Usuarios (contraseña `demo12345`): `laura` (admin) · `maria` (productora) · `andres` (distribuidor) · `sofia` (acopiadora) · `pedro` (transportador) · `solicitante1…7` (cuentas en revisión).

---

## 10. Archivos de esta entrega

**NUEVOS (crear)**
```
backend/trazabilidad/auditoria.py · ledger.py · operaciones.py · permissions.py
backend/trazabilidad/views_admin.py · views_operaciones.py
backend/trazabilidad/management/__init__.py · commands/__init__.py
backend/trazabilidad/management/commands/cargar_catalogo.py · cargar_demo.py · hacer_admin.py · sellar_existentes.py
backend/trazabilidad/migrations/0004_roles_ledger_auditoria.py · 0005_categorias_catalogo.py
backend/usuarios/migrations/0002_roles_ledger_auditoria.py
frontend/src/app/guards/rol.guard.ts
frontend/src/app/services/panel-api.ts · sesion.ts
frontend/src/app/components/inicio/inicio.ts
frontend/src/app/components/en-revision/en-revision.ts
frontend/src/app/components/admin-resumen/ (.ts .html .css)
frontend/src/app/components/admin-seccion/ (.ts .html .css)
frontend/src/app/components/distribuidor-resumen/ (.ts .html .css)
frontend/src/app/components/distribuidor-lista/ (.ts .html .css)
```
**MODIFICADOS (reemplazar)**
```
backend/naritrace/urls.py · backend/trazabilidad/{admin,models,serializers,urls,views}.py
backend/usuarios/{admin,models,serializers,views}.py
frontend/src/styles.css · frontend/src/app/app.routes.ts · services/api.ts
frontend/src/app/components/{dashboard (.ts .html .css), icon/icon.ts, trazabilidad-publica/trazabilidad-publica.ts}
```

---

## 11. Lo que falta (priorizado)

**Cercano**
1. **Mapas reales:** Leaflet + Terra Draw para dibujar el polígono de la finca → `Finca.poligono_geojson` (validar con `shapely` en backend: área coherente y dentro de Nariño).
2. **Municipios de Nariño (64) por subregión:** modelo/endpoint `/api/municipios/` y selector con búsqueda (hoy el municipio es texto libre).
3. **Rediseñar** "Mis lotes", "Mi finca" y detalle del lote con el nuevo estilo (hoy usan el estilo antiguo con Bootstrap). El botón "Registrar primer evento" aún lleva al detalle antiguo.
4. **Productor:** pantallas Movimientos y Documentos (hoy "Próximamente"); subida de la *ficha de cosecha* (PDF) por lote.
5. **Distribuidor:** escáner de QR con la cámara (hoy se pega el código/enlace); que el productor **designe destinatario** al despachar.
6. Registro: mensaje claro "tu solicitud quedó en revisión" y correo de aviso al aprobar.

**Mediano**
7. **EUDR de verdad:** verificación satelital de no deforestación + exportar el "paquete de diligencia debida".
8. **Anclar la cadena** en una red pública (OpenTimestamps/Polygon) para inmutabilidad frente al operador.
9. Pasar de SQLite a PostgreSQL; tokens con expiración; rate-limit global.
10. Pruebas automáticas (hoy se probó con scripts de humo y navegador).

## 12. Decisiones y detalles a tener en cuenta
- "Disponible" en pantalla = `publicado` en la BD; "En custodia" (distribuidor) también es `publicado`.
- El código `NT-AAMMDD-NNN` se genera **al publicar**; los borradores no tienen código.
- El texto "Datos de demostración" y los avisos de pie son fijos del diseño: quítalos al pasar a datos reales.
- El ledger sella con la hora del servidor; los datos de `cargar_demo` tienen fechas de negocio pasadas pero bloques creados "hoy".
- Django admin: `Movimiento`, bloques y auditoría son de solo lectura por diseño; editar un lote publicado desde el admin lanzará un error.
- El build de producción (`ng build`) descarga la fuente de Google; necesita internet.
