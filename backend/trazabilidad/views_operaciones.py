"""Panel del distribuidor / acopiador / transportador y operaciones sobre lotes."""
from datetime import timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import F, Max, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import ROLES_INTERMEDIARIOS
from . import ledger, operaciones
from .models import Lote, Movimiento
from .permissions import EsIntermediario


def _num(valor):
    """96.00 → '96' ; 12.50 → '12.5'"""
    texto = format(valor, 'f')
    return texto.rstrip('0').rstrip('.') if '.' in texto else texto


def resumen_lote(l, usuario=None):
    d = {
        'id': l.id, 'codigo': l.codigo, 'producto': l.producto.nombre, 'variedad': l.variedad,
        'cantidad': _num(l.cantidad), 'unidad': l.unidad, 'estado': l.estado, 'estado_display': l.get_estado_display(),
        'productor': l.productor.nombre_completo, 'municipio': l.finca.municipio,
        'custodio': l.custodio.nombre_completo if l.custodio else '', 'fecha_publicacion': l.fecha_publicacion,
        'fecha_cosecha': l.fecha_cosecha,
    }
    if usuario is not None:
        d['acciones'] = operaciones.acciones_disponibles(usuario, l)
    return d


def _movimiento(m):
    return {'id': m.id, 'codigo': m.lote.codigo, 'producto': m.lote.producto.nombre, 'tipo': m.tipo,
            'tipo_display': m.get_tipo_display(), 'origen': m.origen, 'destino': m.destino,
            'descripcion': m.descripcion, 'actor': m.actor.nombre_completo, 'fecha': m.fecha, 'hash': m.hash_blockchain}


def _base():
    return Lote.objects.exclude(estado='borrador').select_related('producto', 'productor', 'finca', 'custodio')


def _por_recibir(usuario):
    return _base().filter(Q(estado='publicado', custodio=F('productor')) | Q(estado='en_transito')).exclude(custodio=usuario)


class DistribuidorResumenView(APIView):
    permission_classes = [EsIntermediario]

    def get(self, request):
        me = request.user
        ahora = timezone.now()
        hace30 = ahora - timedelta(days=30)
        base = _base()
        en_custodia = base.filter(custodio=me, estado='publicado')
        en_transito = base.filter(custodio=me, estado='en_transito')
        por_recibir = _por_recibir(me)
        mis_movs = Movimiento.objects.filter(actor=me).select_related('lote__producto', 'actor')

        # movimientos por semana (últimas 6)
        semanas = [0] * 6
        for fecha in mis_movs.filter(fecha__gte=ahora - timedelta(days=42)).values_list('fecha', flat=True):
            idx = (ahora - fecha).days // 7
            if 0 <= idx < 6:
                semanas[5 - idx] += 1

        antiguos = en_custodia.annotate(u=Max('movimientos__fecha')).filter(u__lt=ahora - timedelta(days=3)).count()
        alertas = []
        if antiguos:
            alertas.append({'nivel': 'media', 'texto': f'{antiguos} lote(s) llevan más de 3 días en tu custodia sin movimiento.'})
        if en_transito.exists():
            alertas.append({'nivel': 'baja', 'texto': f'{en_transito.count()} lote(s) tuyos siguen en tránsito: registra la entrega al llegar.'})

        return Response({
            'actualizado': ahora,
            'en_custodia': en_custodia.count(),
            'en_transito': en_transito.count(),
            'por_recibir': por_recibir.count(),
            'recibidos_30d': mis_movs.filter(tipo='acopio', fecha__gte=hace30).count(),
            'despachados_30d': mis_movs.filter(tipo__in=['transporte', 'distribucion'], fecha__gte=hace30).count(),
            'entregados_30d': mis_movs.filter(tipo='entrega', fecha__gte=hace30).count(),
            'lista_por_recibir': [resumen_lote(l) for l in por_recibir.order_by('-fecha_publicacion')[:6]],
            'lista_en_custodia': [resumen_lote(l) for l in en_custodia.order_by('-fecha_publicacion')[:6]],
            'lista_en_transito': [resumen_lote(l) for l in en_transito.order_by('-fecha_publicacion')[:6]],
            'movimientos_semanales': semanas,
            'actividad': [_movimiento(m) for m in mis_movs[:8]],
            'alertas': alertas,
        })


class DistribuidorLotesView(APIView):
    """GET /api/distribuidor/lotes/?vista=por_recibir|custodia|transito|entregados&buscar="""
    permission_classes = [EsIntermediario]

    def get(self, request):
        me = request.user
        vista = request.query_params.get('vista', 'custodia')
        base = _base()
        qs = {
            'por_recibir': _por_recibir(me),
            'custodia': base.filter(custodio=me, estado='publicado'),
            'transito': base.filter(custodio=me, estado='en_transito'),
            'entregados': base.filter(custodio=me, estado='entregado'),
        }.get(vista, base.none())
        b = request.query_params.get('buscar')
        if b:
            qs = qs.filter(Q(codigo__icontains=b) | Q(producto__nombre__icontains=b) | Q(finca__municipio__icontains=b))
        return Response([resumen_lote(l, me) for l in qs.order_by('-fecha_publicacion')[:300]])


class DistribuidorHistorialView(APIView):
    permission_classes = [EsIntermediario]

    def get(self, request):
        qs = Movimiento.objects.filter(actor=request.user).select_related('lote__producto', 'actor')
        tipo = request.query_params.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return Response([_movimiento(m) for m in qs[:300]])


class BuscarLoteView(APIView):
    """GET /api/operaciones/buscar/<codigo>/ — ficha operativa de un lote (no cuenta como consulta pública)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, codigo):
        l = _base().filter(codigo=codigo.strip().upper()).first()
        if not l or request.user.rol not in (('productor', 'administrador') + ROLES_INTERMEDIARIOS):
            return Response({'error': 'No encontramos un lote publicado con ese código.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.rol == 'productor' and l.productor_id != request.user.id:
            return Response({'error': 'No encontramos un lote publicado con ese código.'}, status=status.HTTP_404_NOT_FOUND)
        r = ledger.verificar_lote(l)
        movs = l.movimientos.select_related('actor', 'lote__producto').order_by('fecha')
        return Response({**resumen_lote(l, request.user),
                         'integridad': {'valida': r['valida'], 'sellado': r['sellado'], 'bloques': r['bloques'], 'hash': r['hash']},
                         'linea_tiempo': [_movimiento(m) for m in movs]})


class OperarView(APIView):
    """POST /api/operaciones/operar/  {codigo, accion: recibir|despachar|entregar, destino, descripcion, tipo_envio}"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        d = request.data
        l = _base().filter(codigo=str(d.get('codigo', '')).strip().upper()).first()
        if not l:
            return Response({'error': 'No encontramos un lote publicado con ese código.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            mov = operaciones.operar(l, request.user, d.get('accion', ''), str(d.get('destino', '')),
                                     str(d.get('descripcion', ''))[:500], d.get('tipo_envio', 'transporte'))
        except DjangoValidationError as e:
            return Response({'error': e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        l.refresh_from_db()
        return Response({'mensaje': f"Operación registrada: {mov.get_tipo_display()} · {l.codigo}", 'movimiento': _movimiento(mov),
                         'lote': resumen_lote(l, request.user)}, status=status.HTTP_201_CREATED)
