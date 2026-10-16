from django.contrib import admin
from .models import Producto, Finca, Lote, Movimiento, Certificacion


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'unidad_medida', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre',)
    ordering = ('categoria', 'nombre')


@admin.register(Finca)
class FincaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'productor', 'municipio', 'area_hectareas', 'activa')
    list_filter = ('municipio', 'departamento', 'activa')
    search_fields = ('nombre', 'productor__username', 'municipio')
    ordering = ('municipio', 'nombre')


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = (
        'codigo', 'producto', 'productor',
        'cantidad', 'unidad', 'fecha_cosecha', 'estado'
    )
    list_filter = ('estado', 'producto', 'productor__municipio')
    search_fields = ('codigo', 'producto__nombre', 'productor__username')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('codigo', 'uuid', 'qr_codigo', 'fecha_creacion')


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('lote', 'tipo', 'actor', 'origen', 'destino', 'fecha')
    list_filter = ('tipo', 'fecha')
    search_fields = ('lote__codigo', 'actor__username', 'origen', 'destino')
    ordering = ('-fecha',)
    readonly_fields = ('fecha',)


@admin.register(Certificacion)
class CertificacionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'entidad_certificadora', 'finca', 'lote', 'activa')
    list_filter = ('tipo', 'activa', 'entidad_certificadora')
    search_fields = ('numero_certificado', 'entidad_certificadora')
    ordering = ('-fecha_emision',)