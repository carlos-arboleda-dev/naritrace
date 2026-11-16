# NariTrace — Registro de progreso

> Archivo vivo: se actualiza en cada entrega.
> **Última actualización:** 16 nov 2026 · **Entrega #2**

## Estado general

| Área | Estado |
|---|---|
| Backend arranca (`runserver`) | ✅ Corregido |
| Resumen del productor (según diseño) | ✅ Implementado y verificado con captura |
| Datos del resumen desde la BD | ✅ KPIs, serie mensual y borrador reales |
| Registro de consultas QR | ✅ Modelo `ConsultaPublica` (**requiere `migrate`**) |
| Asistente "Registrar un nuevo lote" (4 pasos) | ✅ Implementado según diseño y probado en navegador |
| Código y QR al publicar (`NT-AAMMDD-NNN`) | ✅ Backend + frontend |
| Movimientos / Documentos (menú) | ⏳ Pantallas provisionales ("Próximamente") |
| Panel admin | ⚠️ Pendiente (ver abajo) |

## Entrega #2 — Error de estadísticas + registro de lote

### Error `no such table: trazabilidad_consultapublica`
No era un bug de código: la tabla nueva de la Entrega #1 todavía no existía en tu `db.sqlite3`.
Solución: `python manage.py migrate` (aplica las migraciones `0002` y `0003`).

### Asistente de 4 pasos (`/dashboard/lotes/nuevo`)
1. **Datos del lote** — producto, variedad (según el producto), cantidad, unidad, fecha de cosecha, proceso, origen y notas.
2. **Origen y ubicación** — finca, vereda, mapa ilustrativo, latitud, longitud y área (datos de la finca, solo lectura).
3. **Revisión y publicación** — resumen, qué es público/privado y casilla de confirmación obligatoria.
4. **Lote registrado** — código generado, QR real, enlace público (copiar / ver), descargar etiqueta, "Registrar primer evento".
- Panel lateral "Tu lote, de un vistazo" que se actualiza mientras escribes.
- "Guardar borrador" en cualquier paso; cada "Guardar y continuar" guarda el borrador, así no se pierde nada.
- Validación con mensajes por campo. Un borrador se retoma desde **Continúa donde quedaste** (`?borrador=ID`).
- "Descargar etiqueta PDF" abre el diálogo de impresión solo con la etiqueta (elige *Guardar como PDF*).

### Backend
- **El código se genera al publicar**, con el formato del diseño `NT-260918-001` (fecha de cosecha + consecutivo del día). Los borradores no tienen código (`codigo` ahora admite `null`; migración `0003`).
- El QR apunta a `FRONTEND_URL/trazabilidad/<código>` (nueva variable en `settings.py`, por defecto `http://localhost:4200`; agrégala a `.env` al desplegar).
- `POST /api/lotes/<id>/publicar/` valida que la cantidad sea mayor a 0 y devuelve código, QR y el lote completo.
- Los lotes aceptan ahora `variedad`, `proceso` y `notas_produccion`.
- **Seguridad:** el `estado` ya no se puede cambiar editando el lote (solo con `/publicar/`) y un productor no puede crear lotes en fincas de otro.
- **Privacidad (corregido):** la vista pública exponía las **coordenadas de la finca** y los **archivos de las certificaciones**. Ahora son privados, como promete el paso 3.

## Entrega #1 — qué se hizo

### 1. Error del backend
`ImportError: cannot import name 'Count' from 'django.db.models.functions'`.
`Count` es una función de agregación y vive en `django.db.models`.
Corregido en `trazabilidad/views.py`:
```python
from django.db.models.functions import TruncMonth
from django.db.models import Q, Count
```

### 2. Backend nuevo para el resumen
- **`ConsultaPublica`** (modelo + migración `0002_consultapublica.py` + admin): se guarda una fila cada vez que alguien consulta un lote público (`/api/publico/trazabilidad/<codigo>/` y `/api/lotes/por-codigo/<codigo>/`). No guarda datos personales.
- **`GET /api/estadisticas/`** reescrito: lotes registrados / disponibles / en tránsito / borrador, nuevos este mes, movimientos, lote destacado, consultas 30 días y semana, serie de 6 meses (con meses vacíos en 0 y nombres en español), borrador pendiente y finca principal.
- **Paginación** configurable (`?page_size=N`, máx. 500) en lotes y productos → `trazabilidad/pagination.py`.
- Bug corregido: antes contaba `estado='disponible'`, que no existe en el modelo (siempre daba 0). **"Disponible" en la interfaz = `publicado` en la BD.**

### 3. Frontend: interfaz del productor
- Fuente Manrope y paleta del diseño (`styles.css`): verde `#074832`, activo `#09714e`, menta `#83deb1`, crema `#f5f2e7`.
- **Layout** (`dashboard`): menú lateral con espacio de trabajo (finca real), navegación, centro de ayuda, usuario con botón de cerrar sesión; barra superior con migas, "Datos de demostración", campana y avatar.
- **Resumen** (`resumen`): saludo según la hora, 4 tarjetas, gráfico de barras, "Continúa donde quedaste", tabla "Mis lotes" con búsqueda (con retardo), filtros por estado y producto, paginación de 6 en 6 y **Exportar a CSV** (respeta filtros).
- Componente de íconos reutilizable (`icon`) y pantalla provisional (`proximamente`).
- Login ahora redirige a `/dashboard/resumen`.
- Rutas nuevas: `resumen`, `movimientos`, `documentos`.
- Corregido: el dashboard usaba `rol` sin definirlo y `*ngIf` sin importarlo; ahora el rol se carga desde `/api/me/`.

## Cómo aplicarlo

Extrae `naritrace_cambios.tar.gz` **en la carpeta que contiene `naritrace/`** (sobrescribe los archivos modificados) y luego:

```bash
# Backend
cd naritrace/backend
source .venv/bin/activate
python manage.py migrate          # crea la tabla de consultas
python manage.py runserver

# Frontend (otra terminal)
cd naritrace/frontend
npm start
```

## Decisiones y detalles a tener en cuenta
- Los **borradores anteriores** conservan su código viejo (`NT-2026-XXXXXX`) en la BD, pero la interfaz muestra "Borrador sin código" y al publicarse reciben el código nuevo.
- Los lotes **ya publicados** mantienen su código y QR anteriores.
- **Vereda, latitud, longitud y área** del paso 2 vienen de la finca y son de solo lectura (editarlas se hace en *Mi finca*). El mapa es ilustrativo, como en el diseño.
- **Ficha de cosecha (PDF) del paso 1:** el diseño la muestra, pero el backend aún no tiene dónde guardar documentos de un lote. No se incluyó para no simular algo que no funciona.
- El pie del paso 4 dice "Escanéala para abrir la vista pública" (no "no abre una página real") porque el QR sí abre la vista pública de tu sistema.
- **"Datos de demostración"** y el aviso inferior son texto fijo del diseño. Quítalos cuando pases a datos reales.
- Las consultas QR empiezan en 0: el gráfico se llena a medida que se escanean lotes publicados.
- "Productora" del diseño aparece como "Productor" (no hay campo de género en el usuario).

## Pendientes / siguiente paso sugerido
0. Ejecutar `python manage.py migrate` (si no, `/api/estadisticas/` da error 500).
1. **Panel admin:** `admin-panel` espera `productores_activos` y `lotes_por_municipio`, que `/api/estadisticas/` no devuelve. Hace falta un endpoint propio para el administrador.
2. Subida de documentos por lote (ficha de cosecha) con almacenamiento en el backend.
3. Rediseñar "Mis lotes", "Mi finca" y detalle del lote con el mismo estilo (el botón "Registrar primer evento" aún lleva al detalle antiguo).
4. Construir Movimientos y Documentos.
5. Pantallas de login/registro con la misma identidad visual.
