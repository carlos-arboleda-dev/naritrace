from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Q, Count

from .pagination import PaginacionEstandar
from .models import Producto, Finca, Lote, Movimiento, Certificacion, ConsultaPublica
from .serializers import (
    ProductoSerializer, FincaSerializer,
    LoteListSerializer, LoteDetailSerializer,
    MovimientoSerializer, CertificacionSerializer,
    TrazabilidadPublicaSerializer,
)


# ============================================
# PRODUCTO VIEWSET
# ============================================
class ProductoViewSet(viewsets.ModelViewSet):
    """
    Catálogo de productos agropecuarios.
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PaginacionEstandar

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria = self.request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        return queryset


# ============================================
# FINCA VIEWSET
# ============================================
class FincaViewSet(viewsets.ModelViewSet):
    """
    Fincas registradas. Un productor solo ve las suyas.
    """
    queryset = Finca.objects.all()
    serializer_class = FincaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrar por productor si no es admin
        user = self.request.user
        if user.is_authenticated and user.rol == 'productor':
            queryset = queryset.filter(productor=user)

        municipio = self.request.query_params.get('municipio')
        if municipio:
            queryset = queryset.filter(municipio__icontains=municipio)

        return queryset

    def perform_create(self, serializer):
        # Un productor solo puede crear fincas a su nombre
        if self.request.user.rol == 'productor':
            serializer.save(productor=self.request.user)
        else:
            serializer.save()


# ============================================
# LOTE VIEWSET
# ============================================
class LoteViewSet(viewsets.ModelViewSet):
    """
    Lotes trazables. Generan QR automáticamente.
    """
    queryset = Lote.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PaginacionEstandar

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LoteDetailSerializer
        return LoteListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtro por productor
        user = self.request.user
        if user.is_authenticated and user.rol == 'productor':
            queryset = queryset.filter(productor=user)

        # Filtros por query params
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        producto_id = self.request.query_params.get('producto')
        if producto_id:
            queryset = queryset.filter(producto_id=producto_id)

        finca_id = self.request.query_params.get('finca')
        if finca_id:
            queryset = queryset.filter(finca_id=finca_id)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) |
                Q(producto__nombre__icontains=search) |
                Q(variedad__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        # Asignar productor automáticamente
        if self.request.user.rol == 'productor':
            serializer.save(productor=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], url_path='publicar')
    def publicar(self, request, pk=None):
        """Publica un borrador: genera su código (NT-AAMMDD-NNN) y su QR."""
        lote = self.get_object()
        if lote.estado != 'borrador':
            return Response(
                {'error': 'Solo se pueden publicar lotes en borrador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not lote.cantidad or lote.cantidad <= 0:
            return Response(
                {'error': 'Define la cantidad del lote antes de publicarlo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        lote.estado = 'publicado'
        lote.fecha_publicacion = timezone.now()
        lote.codigo = None      # se vuelve a generar en save() con el formato vigente
        lote.qr_codigo = ''
        lote.save()
        return Response({
            'mensaje': f'Lote {lote.codigo} publicado',
            'codigo': lote.codigo,
            'qr_codigo': lote.qr_codigo,
            'lote': LoteDetailSerializer(lote, context={'request': request}).data,
        })

    @action(detail=False, methods=['get'], url_path='por-codigo/(?P<codigo>[^/.]+)',
            permission_classes=[AllowAny])
    def por_codigo(self, request, codigo=None):
        """Busca un lote por su código público (para escaneo QR)"""
        try:
            lote = Lote.objects.get(codigo=codigo, estado='publicado')
        except Lote.DoesNotExist:
            return Response(
                {'error': 'Lote no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        ConsultaPublica.objects.create(lote=lote)
        serializer = TrazabilidadPublicaSerializer(lote)
        return Response(serializer.data)


# ============================================
# MOVIMIENTO VIEWSET
# ============================================
class MovimientoViewSet(viewsets.ModelViewSet):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        lote_id = self.request.query_params.get('lote')
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        return queryset

    def perform_create(self, serializer):
        # El actor siempre es el usuario autenticado
        serializer.save(actor=self.request.user)

# ============================================
# CERTIFICACION VIEWSET
# ============================================
class CertificacionViewSet(viewsets.ModelViewSet):
    """
    Certificaciones de fincas y lotes.
    """
    queryset = Certificacion.objects.all()
    serializer_class = CertificacionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        finca_id = self.request.query_params.get('finca')
        if finca_id:
            queryset = queryset.filter(finca_id=finca_id)
        lote_id = self.request.query_params.get('lote')
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        return queryset


# ============================================
# VISTA PÚBLICA DE TRAZABILIDAD (sin auth)
# ============================================
class TrazabilidadPublicaViewSet(viewsets.ViewSet):
    """
    Endpoint público para escanear QR sin autenticación.
    GET /api/publico/trazabilidad/{codigo}/
    """
    permission_classes = [AllowAny]

    def retrieve(self, request, pk=None):
        try:
            lote = Lote.objects.get(codigo=pk, estado='publicado')
        except Lote.DoesNotExist:
            return Response(
                {'error': 'No existe un lote publicado con ese código'},
                status=status.HTTP_404_NOT_FOUND
            )
        ConsultaPublica.objects.create(lote=lote)
        serializer = TrazabilidadPublicaSerializer(lote)
        return Response(serializer.data)



class MeView(APIView):
    """Devuelve los datos del usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'rol': getattr(u, 'rol', 'cliente'),
            'rol_display': u.get_rol_display() if hasattr(u, 'get_rol_display') else getattr(u, 'rol', ''),
            'telefono': getattr(u, 'telefono', ''),
            'municipio': getattr(u, 'municipio', ''),
            'verificado': getattr(u, 'verificado', False),
        })


MESES_ES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun',
            'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
MESES_LARGO = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
               'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']


def _restar_meses(fecha, n):
    """Primer día del mes que queda n meses antes de `fecha`."""
    total = fecha.year * 12 + (fecha.month - 1) - n
    return fecha.replace(year=total // 12, month=total % 12 + 1, day=1)


class EstadisticasAdminView(APIView):
    """
    KPIs y series para el resumen del productor autenticado.
    Todo se calcula desde la base de datos; no hay valores estáticos.
    GET /api/estadisticas/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        es_productor = getattr(user, 'rol', None) == 'productor'

        lotes_qs = Lote.objects.all()
        fincas_qs = Finca.objects.all()
        if es_productor:
            lotes_qs = lotes_qs.filter(productor=user)
            fincas_qs = fincas_qs.filter(productor=user)

        ahora = timezone.localtime()
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # ---- KPIs de lotes ("Disponible" en la interfaz = estado publicado)
        total_lotes = lotes_qs.count()
        disponibles = lotes_qs.filter(estado='publicado').count()
        en_transito = lotes_qs.filter(estado='en_transito').count()
        borradores = lotes_qs.filter(estado='borrador').count()
        nuevos_mes = lotes_qs.filter(fecha_creacion__gte=inicio_mes).count()

        # ---- Movimientos y lote destacado (el que más eventos tiene)
        movimientos_total = Movimiento.objects.filter(lote__in=lotes_qs).count()
        destacado = (
            lotes_qs.annotate(n=Count('movimientos'))
            .filter(n__gt=0).order_by('-n', '-fecha_creacion').first()
        )
        movimientos_destacado = destacado.n if destacado else 0

        # ---- Consultas QR
        consultas_qs = ConsultaPublica.objects.filter(lote__in=lotes_qs)
        consultas_30d = consultas_qs.filter(fecha__gte=ahora - timedelta(days=30)).count()
        consultas_semana = consultas_qs.filter(fecha__gte=ahora - timedelta(days=7)).count()

        # ---- Serie mensual: últimos 6 meses completos incluyendo los vacíos
        inicio_serie = _restar_meses(inicio_mes, 5)
        por_mes = {
            (r['mes'].year, r['mes'].month): r['total']
            for r in (
                consultas_qs.filter(fecha__gte=inicio_serie)
                .annotate(mes=TruncMonth('fecha'))
                .values('mes').annotate(total=Count('id'))
            )
        }
        consultas_mensuales = []
        for i in range(5, -1, -1):
            m = _restar_meses(inicio_mes, i)
            consultas_mensuales.append({
                'mes': MESES_ES[m.month - 1].capitalize(),
                'total': por_mes.get((m.year, m.month), 0),
            })
        rango = f"{MESES_ES[inicio_serie.month - 1].capitalize()}–{MESES_ES[inicio_mes.month - 1]} {inicio_mes.year}"

        # ---- Borrador pendiente ("Continúa donde quedaste")
        borrador = lotes_qs.filter(estado='borrador').order_by('-fecha_creacion').first()
        borrador_data = None
        if borrador:
            fc = borrador.fecha_cosecha
            borrador_data = {
                'id': borrador.id,
                'codigo': borrador.codigo,
                'producto': borrador.producto.nombre if borrador.producto else '',
                'fecha': fc.isoformat() if fc else '',
                'mes_cosecha': MESES_LARGO[fc.month - 1] if fc else '',
            }

        # ---- Finca principal (para el "Espacio de trabajo" del menú)
        finca = fincas_qs.order_by('id').first()
        finca_data = {
            'id': finca.id, 'nombre': finca.nombre,
            'municipio': finca.municipio, 'departamento': finca.departamento,
        } if finca else None

        return Response({
            'lotes_registrados': total_lotes,
            'lotes_disponibles': disponibles,
            'lotes_borrador': borradores,
            'lotes_en_transito': en_transito,
            'nuevos_este_mes': nuevos_mes,
            'movimientos_registrados': movimientos_total,
            'movimientos_lote_destacado': movimientos_destacado,
            'consultas_30d': consultas_30d,
            'consultas_semana': consultas_semana,
            'consultas_mensuales': consultas_mensuales,
            'consultas_rango': rango,
            'fincas_registradas': fincas_qs.count(),
            'finca_principal': finca_data,
            'borrador_pendiente': borrador_data,
            'actualizado': ahora.isoformat(),
        })
