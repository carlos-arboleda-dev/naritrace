from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

from .models import Producto, Finca, Lote, Movimiento, Certificacion
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
        """Publica un lote y genera su QR"""
        lote = self.get_object()
        if lote.estado != 'borrador':
            return Response(
                {'error': 'Solo se pueden publicar lotes en borrador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        lote.estado = 'publicado'
        lote.fecha_publicacion = timezone.now()
        lote.save()
        return Response({
            'mensaje': f'Lote {lote.codigo} publicado',
            'qr_codigo': lote.qr_codigo
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
        serializer = TrazabilidadPublicaSerializer(lote)
        return Response(serializer.data)


# ============================================
# MOVIMIENTO VIEWSET
# ============================================
class MovimientoViewSet(viewsets.ModelViewSet):
    """
    Movimientos en la cadena de suministro.
    """
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        lote_id = self.request.query_params.get('lote')
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
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
        serializer = TrazabilidadPublicaSerializer(lote)
        return Response(serializer.data)