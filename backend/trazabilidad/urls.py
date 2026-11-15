from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductoViewSet, FincaViewSet,
    LoteViewSet, MovimientoViewSet,
    CertificacionViewSet, TrazabilidadPublicaViewSet,EstadisticasAdminView
)

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'fincas', FincaViewSet, basename='finca')
router.register(r'lotes', LoteViewSet, basename='lote')
router.register(r'movimientos', MovimientoViewSet, basename='movimiento')
router.register(r'certificaciones', CertificacionViewSet, basename='certificacion')

# Endpoint público
public_router = DefaultRouter()
public_router.register(r'trazabilidad', TrazabilidadPublicaViewSet, basename='trazabilidad-publica')

urlpatterns = [
    path('', include(router.urls)),
    path('publico/', include(public_router.urls)),
    path('estadisticas/', EstadisticasAdminView.as_view(), name='estadisticas_admin'),
]