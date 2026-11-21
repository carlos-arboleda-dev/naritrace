from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductoViewSet, FincaViewSet,
    LoteViewSet, MovimientoViewSet,
    CertificacionViewSet, TrazabilidadPublicaViewSet, 
    EstadisticasAdminView,
    MeView,
)
from . import views_admin as va
from . import views_operaciones as vo

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
    path('estadisticas/', EstadisticasAdminView.as_view(), name='estadisticas'),
    path('me/', MeView.as_view(), name='me'),

    # Panel de administración
    path('admin/resumen/', va.AdminResumenView.as_view()),
    path('admin/auditoria/', va.AdminAuditoriaView.as_view()),
    path('admin/productores/', va.AdminProductoresView.as_view()),
    path('admin/productores/<int:pk>/verificar/', va.AdminProductorVerificarView.as_view()),
    path('admin/lotes/', va.AdminLotesView.as_view()),
    path('admin/lotes/<int:pk>/verificar/', va.AdminLoteVerificarView.as_view()),
    path('admin/municipios/', va.AdminMunicipiosView.as_view()),
    path('admin/solicitudes/', va.AdminSolicitudesView.as_view()),
    path('admin/solicitudes/<int:pk>/resolver/', va.AdminSolicitudResolverView.as_view()),
    path('admin/cadena/', va.AdminCadenaView.as_view()),

    # Distribuidor / acopiador / transportador
    path('distribuidor/resumen/', vo.DistribuidorResumenView.as_view()),
    path('distribuidor/lotes/', vo.DistribuidorLotesView.as_view()),
    path('distribuidor/historial/', vo.DistribuidorHistorialView.as_view()),
    path('operaciones/buscar/<str:codigo>/', vo.BuscarLoteView.as_view()),
    path('operaciones/operar/', vo.OperarView.as_view()),
]