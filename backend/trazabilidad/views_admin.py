"""Endpoints del panel de administración (solo rol administrador)."""
from datetime import date, timedelta

from django.db.models import Count, Max, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import SolicitudRol, Usuario
from . import ledger
from .auditoria import auditar
from .models import BloqueLedger, ConsultaPublica, EventoAuditoria, Finca, Lote, Movimiento, Producto
from .pagination import PaginacionEstandar
from .permissions import EsAdministrador

MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
MESES_LARGO = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
               'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
LIMITE_VERIFICACION_AUTO = 3000   # por encima de esto la cadena solo se verifica a pedido


def _num(valor):
    """96.00 → '96' ; 12.50 → '12.5'"""
    texto = format(valor, 'f')
    return texto.rstrip('0').rstrip('.') if '.' in texto else texto


def _fecha(valor, defecto):
    try:
        return date.fromisoformat(valor) if valor else defecto
    except ValueError:
        return defecto


def _mes_atras(d, n):
    total = d.year * 12 + (d.month - 1) - n
    return d.replace(year=total // 12, month=total % 12 + 1, day=1)


def _nombre(u):
    return u.nombre_completo if u else 'Sistema'


class AdminResumenView(APIView):
    """GET /api/admin/resumen/?desde=&hasta=&departamento=&municipio="""
    permission_classes = [EsAdministrador]

    def get(self, request):
        p = request.query_params
        ahora = timezone.now()
        hoy = timezone.localdate()
        hasta = _fecha(p.get('hasta'), hoy)
        desde = _fecha(p.get('desde'), hasta - timedelta(days=30))
        depto = p.get('departamento', 'Nariño')
        muni = p.get('municipio', '')

        fincas = Finca.objects.all()
        if depto:
            fincas = fincas.filter(departamento__iexact=depto)
        if muni:
            fincas = fincas.filter(municipio__iexact=muni)
        lotes = Lote.objects.exclude(estado='borrador').filter(finca__in=fincas)
        movs = Movimiento.objects.filter(lote__in=lotes)

        # ---------- indicadores
        productores_ids = set(fincas.values_list('productor_id', flat=True))
        municipios_con_prod = fincas.values('municipio').distinct().count()
        total_lotes = lotes.count()
        lotes_periodo = lotes.filter(fecha_publicacion__date__range=(desde, hasta)).count()
        eventos = movs.count()
        eventos_periodo = movs.filter(fecha__date__range=(desde, hasta)).count()
        pend = SolicitudRol.objects.filter(estado='pendiente')
        pend_por_rol = [
            {'rol': r['rol_solicitado'], 'rol_display': dict(Usuario.Rol.choices).get(r['rol_solicitado'], r['rol_solicitado']),
             'total': r['n']}
            for r in pend.values('rol_solicitado').annotate(n=Count('id')).order_by('-n')
        ]

        # ---------- lotes por municipio (top 5)
        por_muni = list(lotes.values('finca__municipio').annotate(n=Count('id')).order_by('-n', 'finca__municipio')[:5])
        lotes_por_municipio = [{'municipio': r['finca__municipio'], 'total': r['n']} for r in por_muni]
        concentracion = round(por_muni[0]['n'] * 100 / total_lotes) if por_muni and total_lotes else 0

        # ---------- nuevos lotes por mes (6 meses terminando en `hasta`)
        inicio_serie = _mes_atras(hasta.replace(day=1), 5)
        crudo = {(r['m'].year, r['m'].month): r['n'] for r in
                 lotes.filter(fecha_publicacion__date__gte=inicio_serie)
                 .annotate(m=TruncMonth('fecha_publicacion')).values('m').annotate(n=Count('id'))}
        serie = []
        for i in range(5, -1, -1):
            m = _mes_atras(hasta.replace(day=1), i)
            serie.append({'mes': MESES[m.month - 1].capitalize(), 'total': crudo.get((m.year, m.month), 0)})
        ult, ant = serie[-1]['total'], serie[-2]['total']
        variacion = round((ult - ant) * 100 / ant) if ant else None
        anteriores = lotes.filter(fecha_publicacion__date__lt=inicio_serie).count()

        # ---------- productores por municipio (top 5)
        prod_muni = [{'municipio': r['municipio'], 'total': r['n']} for r in
                     fincas.values('municipio').annotate(n=Count('productor', distinct=True)).order_by('-n', 'municipio')[:5]]

        # ---------- preparación EUDR (geolocalización)
        lista = list(fincas.values('municipio', 'latitud', 'longitud', 'poligono_geojson'))
        n_f = len(lista)
        con_coord = sum(1 for f in lista if f['latitud'] is not None and f['longitud'] is not None)
        con_pol = sum(1 for f in lista if f['poligono_geojson'])
        faltan = {}
        for f in lista:
            if f['latitud'] is None or f['longitud'] is None:
                faltan[f['municipio']] = faltan.get(f['municipio'], 0) + 1
        eudr = {
            'fincas': n_f, 'con_coordenadas': con_coord, 'con_poligono': con_pol,
            'pct_coordenadas': round(con_coord * 100 / n_f) if n_f else 0,
            'pct_poligono': round(con_pol * 100 / n_f) if n_f else 0,
            'sin_coordenadas': [{'municipio': m, 'total': t} for m, t in sorted(faltan.items(), key=lambda x: -x[1])[:3]],
        }

        # ---------- mix de productos
        etiquetas = dict(Producto.Categoria.choices)
        mix = [{'categoria': etiquetas.get(r['producto__categoria'], r['producto__categoria']), 'total': r['n']}
               for r in lotes.values('producto__categoria').annotate(n=Count('id')).order_by('-n')]

        # ---------- actividad pública (consultas QR)
        cons = ConsultaPublica.objects.filter(lote__in=lotes)
        hace30 = ahora - timedelta(days=30)
        top_consultados = [{'codigo': r['lote__codigo'], 'producto': r['lote__producto__nombre'], 'total': r['n']}
                           for r in cons.filter(fecha__gte=hace30).values('lote__codigo', 'lote__producto__nombre')
                           .annotate(n=Count('id')).order_by('-n')[:5]]

        # ---------- integridad de la cadena
        total_bloques = BloqueLedger.objects.count()
        ultimo = BloqueLedger.objects.order_by('-indice').first()
        if total_bloques <= LIMITE_VERIFICACION_AUTO:
            ver = ledger.verificar_cadena()
            integridad_valida, integridad_error = ver['valida'], ver['error']
        else:
            integridad_valida, integridad_error = None, None
        integridad = {
            'valida': integridad_valida, 'error': integridad_error, 'bloques': total_bloques,
            'ultimo_hash': ultimo.hash if ultimo else '', 'ultimo_bloque_fecha': ultimo.fecha if ultimo else None,
        }

        # ---------- alertas operativas
        alertas = []
        if integridad_valida is False:
            alertas.append({'nivel': 'alta', 'texto': 'La cadena de registros presenta una alteración: ' + integridad_error['motivo'],
                            'ruta': '/dashboard/admin/lotes'})
        sin_eventos = lotes.filter(estado='publicado', fecha_publicacion__lt=ahora - timedelta(days=7)) \
            .annotate(n=Count('movimientos')).filter(n__lte=1).count()
        if sin_eventos:
            alertas.append({'nivel': 'media', 'texto': f'{sin_eventos} lote(s) publicados hace más de 7 días casi sin eventos.', 'ruta': '/dashboard/admin/lotes'})
        estancados = lotes.filter(estado='en_transito').annotate(u=Max('movimientos__fecha')) \
            .filter(u__lt=ahora - timedelta(days=5)).count()
        if estancados:
            alertas.append({'nivel': 'media', 'texto': f'{estancados} lote(s) en tránsito llevan más de 5 días sin recepción.', 'ruta': '/dashboard/admin/lotes'})
        if n_f - con_coord:
            alertas.append({'nivel': 'media', 'texto': f'{n_f - con_coord} finca(s) sin coordenadas: no cumplirían el requisito de geolocalización de la UE (EUDR).', 'ruta': '/dashboard/admin/municipios'})
        viejas = pend.filter(fecha_solicitud__lt=ahora - timedelta(days=3)).count()
        if viejas:
            alertas.append({'nivel': 'baja', 'texto': f'{viejas} solicitud(es) de rol llevan más de 3 días sin respuesta.', 'ruta': '/dashboard/admin/solicitudes'})

        # ---------- auditoría reciente
        ultimos = EventoAuditoria.objects.select_related('usuario')[:8]

        return Response({
            'periodo': {'desde': desde.isoformat(), 'hasta': hasta.isoformat()},
            'filtros': {'departamento': depto, 'municipio': muni},
            'actualizado': ahora,
            'productores_activos': len(productores_ids),
            'municipios_con_productores': municipios_con_prod,
            'lotes_publicados': total_lotes,
            'lotes_periodo': lotes_periodo,
            'eventos_registrados': eventos,
            'eventos_periodo': eventos_periodo,
            'solicitudes_pendientes': pend.count(),
            'solicitudes_por_rol': pend_por_rol,
            'lotes_por_municipio': lotes_por_municipio,
            'concentracion_pct': concentracion,
            'nuevos_lotes_mensual': serie,
            'nuevos_lotes_ultimo_mes': ult,
            'nuevos_lotes_mes_nombre': MESES_LARGO[hasta.month - 1],
            'variacion_pct': variacion,
            'lotes_anteriores': anteriores,
            'rango_serie': f"{serie[0]['mes']}–{serie[-1]['mes'].lower()} {hasta.year}",
            'productores_por_municipio': prod_muni,
            'integridad': integridad,
            'eudr': eudr,
            'mix_productos': mix,
            'consultas_30d': cons.filter(fecha__gte=hace30).count(),
            'top_consultados': top_consultados,
            'alertas': alertas,
            'auditoria_reciente': [_evento(e) for e in ultimos],
            'auditoria_total': EventoAuditoria.objects.count(),
        })


def _evento(e):
    return {'id': e.id, 'fecha': e.fecha, 'usuario': e.nombre_usuario, 'accion': e.accion,
            'recurso': e.recurso, 'detalle': e.detalle, 'resultado': e.resultado}


class AdminAuditoriaView(generics.ListAPIView):
    """GET /api/admin/auditoria/?buscar=&accion=&resultado=&page="""
    permission_classes = [EsAdministrador]
    pagination_class = PaginacionEstandar

    def get_queryset(self):
        qs = EventoAuditoria.objects.select_related('usuario')
        p = self.request.query_params
        if p.get('buscar'):
            b = p['buscar']
            qs = qs.filter(Q(usuario__username__icontains=b) | Q(usuario__first_name__icontains=b) | Q(usuario__last_name__icontains=b)
                           | Q(recurso__icontains=b) | Q(detalle__icontains=b) | Q(accion__icontains=b))
        if p.get('accion'):
            qs = qs.filter(accion=p['accion'])
        if p.get('resultado'):
            qs = qs.filter(resultado=p['resultado'])
        return qs

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        respuesta = self.get_paginated_response([_evento(e) for e in page])
        respuesta.data['acciones'] = list(EventoAuditoria.objects.order_by('accion').values_list('accion', flat=True).distinct())
        return respuesta


class AdminProductoresView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        b = request.query_params.get('buscar', '')
        qs = Usuario.objects.filter(rol='productor').annotate(
            n_fincas=Count('fincas', distinct=True),
            n_lotes=Count('lotes_producidos', filter=~Q(lotes_producidos__estado='borrador'), distinct=True),
        )
        if b:
            qs = qs.filter(Q(username__icontains=b) | Q(first_name__icontains=b) | Q(last_name__icontains=b) | Q(municipio__icontains=b))
        return Response([{
            'id': u.id, 'codigo': u.codigo, 'nombre': u.nombre_completo, 'username': u.username,
            'municipio': u.municipio, 'telefono': u.telefono, 'verificado': u.verificado, 'activo': u.is_active,
            'fincas': u.n_fincas, 'lotes': u.n_lotes, 'registro': u.date_joined,
        } for u in qs.order_by('-n_lotes', 'username')[:500]])


class AdminProductorVerificarView(APIView):
    """POST /api/admin/productores/<id>/verificar/  (alterna el sello de verificado)"""
    permission_classes = [EsAdministrador]

    def post(self, request, pk):
        try:
            u = Usuario.objects.get(pk=pk, rol='productor')
        except Usuario.DoesNotExist:
            return Response({'error': 'Productor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        u.verificado = not u.verificado
        u.save(update_fields=['verificado'])
        auditar(request.user, 'Verificó productor' if u.verificado else 'Retiró verificación', u.codigo, u.nombre_completo)
        return Response({'id': u.id, 'verificado': u.verificado})


class AdminLotesView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        p = request.query_params
        qs = Lote.objects.exclude(estado='borrador').select_related('producto', 'productor', 'finca') \
            .annotate(n_eventos=Count('movimientos'))
        if p.get('buscar'):
            b = p['buscar']
            qs = qs.filter(Q(codigo__icontains=b) | Q(producto__nombre__icontains=b) | Q(productor__username__icontains=b)
                           | Q(finca__municipio__icontains=b))
        if p.get('estado'):
            qs = qs.filter(estado=p['estado'])
        return Response([{
            'id': l.id, 'codigo': l.codigo, 'producto': l.producto.nombre, 'productor': l.productor.nombre_completo,
            'municipio': l.finca.municipio, 'cantidad': _num(l.cantidad), 'unidad': l.unidad,
            'estado': l.estado, 'estado_display': l.get_estado_display(), 'eventos': l.n_eventos,
            'hash': l.hash_blockchain, 'fecha_publicacion': l.fecha_publicacion,
        } for l in qs.order_by('-fecha_publicacion')[:500]])


class AdminLoteVerificarView(APIView):
    """GET /api/admin/lotes/<id>/verificar/"""
    permission_classes = [EsAdministrador]

    def get(self, request, pk):
        lote = Lote.objects.filter(pk=pk).exclude(estado='borrador').first()
        if not lote:
            return Response({'error': 'Lote no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        r = ledger.verificar_lote(lote)
        auditar(request.user, 'Verificó integridad', lote.codigo, 'Íntegro' if r['valida'] else 'ALTERADO',
                'completado' if r['valida'] else 'rechazado')
        return Response({'codigo': lote.codigo, **r})


class AdminMunicipiosView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        fincas = list(Finca.objects.values('id', 'municipio', 'departamento', 'productor_id', 'latitud', 'longitud', 'poligono_geojson'))
        por_finca = {r['finca_id']: r['n'] for r in
                     Lote.objects.exclude(estado='borrador').values('finca_id').annotate(n=Count('id'))}
        eventos = {r['lote__finca_id']: r['n'] for r in
                   Movimiento.objects.values('lote__finca_id').annotate(n=Count('id'))}
        filas = {}
        for f in fincas:
            m = filas.setdefault(f['municipio'], {'municipio': f['municipio'], 'departamento': f['departamento'], 'productores': set(),
                                                  'fincas': 0, 'lotes': 0, 'eventos': 0, 'geo': 0, 'poligono': 0})
            m['productores'].add(f['productor_id'])
            m['fincas'] += 1
            m['lotes'] += por_finca.get(f['id'], 0)
            m['eventos'] += eventos.get(f['id'], 0)
            m['geo'] += 1 if f['latitud'] is not None and f['longitud'] is not None else 0
            m['poligono'] += 1 if f['poligono_geojson'] else 0
        salida = []
        for m in filas.values():
            salida.append({**m, 'productores': len(m['productores']),
                           'pct_geo': round(m['geo'] * 100 / m['fincas']) if m['fincas'] else 0})
        return Response(sorted(salida, key=lambda x: (-x['lotes'], x['municipio'])))


class AdminSolicitudesView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        estado = request.query_params.get('estado', 'pendiente')
        qs = SolicitudRol.objects.select_related('usuario', 'resuelta_por')
        if estado != 'todas':
            qs = qs.filter(estado=estado)
        return Response([{
            'id': s.id, 'usuario_id': s.usuario_id, 'codigo': s.usuario.codigo, 'nombre': s.usuario.nombre_completo,
            'username': s.usuario.username, 'email': s.usuario.email, 'municipio': s.usuario.municipio,
            'telefono': s.usuario.telefono, 'rol_solicitado': s.rol_solicitado,
            'rol_solicitado_display': s.get_rol_solicitado_display(), 'estado': s.estado, 'nota': s.nota,
            'fecha': s.fecha_solicitud, 'resuelta_por': _nombre(s.resuelta_por) if s.resuelta_por else '',
        } for s in qs[:300]])


class AdminSolicitudResolverView(APIView):
    """POST /api/admin/solicitudes/<id>/resolver/  {decision: 'aprobar'|'rechazar', nota}"""
    permission_classes = [EsAdministrador]

    def post(self, request, pk):
        s = SolicitudRol.objects.select_related('usuario').filter(pk=pk).first()
        if not s:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        if s.estado != 'pendiente':
            return Response({'error': 'Esta solicitud ya fue resuelta.'}, status=status.HTTP_409_CONFLICT)
        decision = request.data.get('decision')
        if decision not in ('aprobar', 'rechazar'):
            return Response({'error': "decision debe ser 'aprobar' o 'rechazar'"}, status=status.HTTP_400_BAD_REQUEST)
        s.nota = str(request.data.get('nota', ''))[:300]
        s.resuelta_por = request.user
        s.fecha_resolucion = timezone.now()
        if decision == 'aprobar':
            s.estado = 'aprobada'
            s.usuario.rol = s.rol_solicitado
            s.usuario.save(update_fields=['rol'])
            auditar(request.user, 'Actualizó rol', s.usuario.codigo, s.get_rol_solicitado_display())
        else:
            s.estado = 'rechazada'
            auditar(request.user, 'Rechazó solicitud', s.usuario.codigo, s.get_rol_solicitado_display())
        s.save()
        return Response({'id': s.id, 'estado': s.estado})


class AdminCadenaView(APIView):
    """GET: últimos bloques. POST: verifica toda la cadena ahora."""
    permission_classes = [EsAdministrador]

    def get(self, request):
        bloques = BloqueLedger.objects.order_by('-indice')[:20]
        return Response({'total': BloqueLedger.objects.count(), 'bloques': [
            {'indice': b.indice, 'tipo': b.tipo, 'referencia': b.referencia, 'hash': b.hash,
             'hash_anterior': b.hash_anterior, 'fecha': b.fecha} for b in bloques]})

    def post(self, request):
        r = ledger.verificar_cadena()
        auditar(request.user, 'Verificó la cadena', f"{r['bloques']} bloques",
                'Íntegra' if r['valida'] else r['error']['motivo'], 'completado' if r['valida'] else 'rechazado')
        return Response(r)
