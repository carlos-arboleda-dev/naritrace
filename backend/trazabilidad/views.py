from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.views import APIView
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Q, Count

from django.core.exceptions import ValidationError as DjangoValidationError
from usuarios.models import ROLES_INTERMEDIARIOS
from . import ledger, operaciones
from .auditoria import auditar
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user
        if user.rol == 'productor':
            queryset = queryset.filter(productor=user)
        elif user.rol != 'administrador':
            queryset = queryset.none()

        municipio = self.request.query_params.get('municipio')
        if municipio:
            queryset = queryset.filter(municipio__icontains=municipio)

        return queryset

    def perform_create(self, serializer):
        # Solo productores (a su nombre) y administradores crean fincas
        if self.request.user.rol == 'productor':
            serializer.save(productor=self.request.user)
        elif self.request.user.rol == 'administrador':
            serializer.save()
        else:
            raise PermissionDenied('Tu rol no puede registrar fincas.')


# ============================================
# LOTE VIEWSET
# ============================================
class LoteViewSet(viewsets.ModelViewSet):
    """
    Lotes trazables. Generan QR automáticamente.
    Los lotes publicados quedan sellados: no se editan ni se eliminan.
    """
    queryset = Lote.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PaginacionEstandar

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LoteDetailSerializer
        return LoteListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.rol == 'productor':
            queryset = queryset.filter(productor=user)
        elif user.rol in ROLES_INTERMEDIARIOS:
            queryset = queryset.exclude(estado='borrador').filter(
                Q(custodio=user) | Q(movimientos__actor=user)).distinct()
        elif user.rol != 'administrador':
            queryset = queryset.none()

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
        if self.request.user.rol != 'productor':
            raise PermissionDenied('Solo los productores registran lotes.')
        lote = serializer.save(productor=self.request.user)
        auditar(self.request.user, 'Guardó borrador',
                f"{lote.producto.nombre} · {lote.finca.nombre}", lote.variedad)

    def update(self, request, *args, **kwargs):
        lote = self.get_object()
        if lote.estado != 'borrador':
            return Response({'error': 'Un lote publicado está sellado y no se puede modificar.'},
                            status=status.HTTP_409_CONFLICT)
        if request.user.rol != 'productor':
            raise PermissionDenied('Solo el productor edita sus borradores.')
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        lote = self.get_object()
        if lote.estado != 'borrador':
            return Response({'error': 'Un lote publicado no se puede eliminar.'},
                            status=status.HTTP_409_CONFLICT)
        if request.user.rol != 'productor':
            raise PermissionDenied('Solo el productor elimina sus borradores.')
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='publicar')
    def publicar(self, request, pk=None):
        """Publica un borrador: genera código y QR y lo sella en el registro encadenado."""
        lote = self.get_object()
        if request.user.rol != 'productor':
            raise PermissionDenied('Solo el productor publica sus lotes.')
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
        with transaction.atomic():
            lote.estado = 'publicado'
            lote.fecha_publicacion = timezone.now()
            lote.codigo = None      # se vuelve a generar en save() con el formato vigente
            lote.qr_codigo = ''
            lote.custodio = lote.productor
            lote.save()
            ledger.sellar_lote(lote)
        lote.refresh_from_db()
        auditar(request.user, 'Publicó lote', lote.codigo, f"{lote.producto.nombre} · {lote.finca.nombre}")
        return Response({
            'mensaje': f'Lote {lote.codigo} publicado',
            'codigo': lote.codigo,
            'qr_codigo': lote.qr_codigo,
            'hash_blockchain': lote.hash_blockchain,
            'lote': LoteDetailSerializer(lote, context={'request': request}).data,
        })

    @action(detail=True, methods=['get'], url_path='verificar')
    def verificar(self, request, pk=None):
        """Comprueba que los datos del lote y su historial no fueron alterados."""
        lote = self.get_object()
        resultado = ledger.verificar_lote(lote)
        return Response({'codigo': lote.codigo, **resultado})

    @action(detail=False, methods=['get'], url_path='por-codigo/(?P<codigo>[^/.]+)',
            permission_classes=[AllowAny])
    def por_codigo(self, request, codigo=None):
        """Busca un lote por su código público (para escaneo QR)"""
        try:
            lote = Lote.objects.exclude(estado__in=['borrador', 'archivado']).get(codigo=codigo)
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
    """
    Movimientos de un lote. Son inmutables: solo se pueden crear y consultar.
    Distribuidores, acopiadores y transportadores operan con /api/operaciones/.
    """
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.rol == 'productor':
            queryset = queryset.filter(lote__productor=user)
        elif user.rol in ROLES_INTERMEDIARIOS:
            queryset = queryset.filter(Q(lote__custodio=user) | Q(actor=user))
        elif user.rol != 'administrador':
            queryset = queryset.none()
        lote_id = self.request.query_params.get('lote')
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lote = serializer.validated_data['lote']
        # Aquí solo el productor del lote registra eventos propios (beneficio, secado, etc.)
        if request.user.rol != 'productor' or lote.productor_id != request.user.id:
            raise PermissionDenied('Solo el productor del lote puede registrar eventos aquí.')
        if lote.estado == 'borrador':
            raise ValidationError({'lote': 'Publica el lote antes de registrar eventos.'})
        d = serializer.validated_data
        mov = operaciones.crear_movimiento(
            lote, request.user, d['tipo'], d.get('origen', ''), d.get('destino', ''),
            d.get('descripcion', ''), d.get('latitud'), d.get('longitud'))
        return Response(self.get_serializer(mov).data, status=status.HTTP_201_CREATED)


# ============================================
# CERTIFICACION VIEWSET
# ============================================
class CertificacionViewSet(viewsets.ModelViewSet):
    """
    Certificaciones de fincas y lotes.
    """
    queryset = Certificacion.objects.all()
    serializer_class = CertificacionSerializer
    permission_classes = [IsAuthenticated]

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
            lote = Lote.objects.exclude(estado__in=['borrador', 'archivado']).get(codigo=pk)
        except Lote.DoesNotExist:
            return Response(
                {'error': 'No existe un lote publicado con ese código'},
                status=status.HTTP_404_NOT_FOUND
            )
        ConsultaPublica.objects.create(lote=lote)
        serializer = TrazabilidadPublicaSerializer(lote)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='verificar')
    def verificar(self, request, pk=None):
        """¿Los datos de este lote siguen siendo los que se sellaron? (no cuenta como consulta)"""
        lote = Lote.objects.exclude(estado__in=['borrador', 'archivado']).filter(codigo=pk).first()
        if not lote:
            return Response({'error': 'No existe un lote publicado con ese código'}, status=status.HTTP_404_NOT_FOUND)
        r = ledger.verificar_lote(lote)
        # Público: solo el veredicto y la huella, sin detalles internos
        return Response({'codigo': lote.codigo, 'valida': r['valida'], 'sellado': r['sellado'], 'bloques': r['bloques'],
                         'hash': r['hash'], 'verificado_en': r['verificado_en']})


class MeView(APIView):
    """Devuelve los datos del usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        solicitud = u.solicitudes.order_by('-fecha_solicitud').first()
        return Response({
            'codigo': u.codigo,
            'solicitud': {
                'rol_solicitado': solicitud.rol_solicitado,
                'rol_solicitado_display': solicitud.get_rol_solicitado_display(),
                'estado': solicitud.estado,
                'nota': solicitud.nota,
            } if solicitud else None,
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
