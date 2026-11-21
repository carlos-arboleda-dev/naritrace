from rest_framework import serializers
from .models import Producto, Finca, Lote, Movimiento, Certificacion
from usuarios.models import Usuario


# ============================================
# PRODUCTO
# ============================================
class ProductoSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(
        source='get_categoria_display', read_only=True
    )

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'categoria', 'categoria_display',
            'descripcion', 'unidad_medida', 'activo', 'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion']


# ============================================
# FINCA
# ============================================
class FincaSerializer(serializers.ModelSerializer):
    productor_nombre = serializers.CharField(
        source='productor.username', read_only=True
    )
    total_lotes = serializers.IntegerField(
        source='lotes.count', read_only=True
    )

    class Meta:
        model = Finca
        fields = [
            'id', 'productor', 'productor_nombre', 'nombre',
            'municipio', 'vereda', 'departamento',
            'latitud', 'longitud', 'area_hectareas', 'poligono_geojson',
            'activa', 'fecha_registro', 'total_lotes'
        ]
        read_only_fields = ['productor', 'fecha_registro']


# ============================================
# MOVIMIENTO
# ============================================
class MovimientoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(
        source='get_tipo_display', read_only=True
    )
    actor_nombre = serializers.CharField(
        source='actor.username', read_only=True
    )

    class Meta:
        model = Movimiento
        fields = [
            'id', 'lote', 'tipo', 'tipo_display',
            'actor', 'actor_nombre', 'origen', 'destino',
            'descripcion', 'latitud', 'longitud',
            'hash_blockchain', 'fecha'
        ]
        read_only_fields = ['actor', 'fecha', 'hash_blockchain']


# ============================================
# CERTIFICACIÓN
# ============================================
class CertificacionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(
        source='get_tipo_display', read_only=True
    )

    class Meta:
        model = Certificacion
        fields = [
            'id', 'finca', 'lote', 'tipo', 'tipo_display',
            'entidad_certificadora', 'numero_certificado',
            'fecha_emision', 'fecha_vencimiento',
            'documento', 'activa'
        ]


# ============================================
# LOTE (con anidamiento)
# ============================================
class LoteListSerializer(serializers.ModelSerializer):
    """Versión resumida para listas"""
    producto_nombre = serializers.CharField(
        source='producto.nombre', read_only=True
    )
    productor_nombre = serializers.CharField(
        source='productor.username', read_only=True
    )
    finca_nombre = serializers.CharField(
        source='finca.nombre', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    total_movimientos = serializers.IntegerField(
        source='movimientos.count', read_only=True
    )

    class Meta:
        model = Lote
        fields = [
            'id', 'codigo', 'producto', 'producto_nombre',
            'productor', 'productor_nombre', 'finca', 'finca_nombre',
            'variedad', 'cantidad', 'unidad', 'fecha_cosecha',
            'proceso', 'notas_produccion',
            'estado', 'estado_display', 'total_movimientos',
            'fecha_creacion'
        ]
        # El estado solo cambia con la acción /publicar/, nunca por edición directa
        read_only_fields = ['productor', 'codigo', 'estado', 'fecha_creacion']

    def validate_finca(self, finca):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and getattr(user, 'rol', None) == 'productor' \
                and finca.productor_id != user.id:
            raise serializers.ValidationError('Esa finca no pertenece a tu cuenta.')
        return finca


class LoteDetailSerializer(serializers.ModelSerializer):
    """Versión completa con movimientos y certificaciones anidados"""
    producto = ProductoSerializer(read_only=True)
    finca = FincaSerializer(read_only=True)
    productor_nombre = serializers.CharField(
        source='productor.username', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    movimientos = MovimientoSerializer(many=True, read_only=True)
    certificaciones = CertificacionSerializer(many=True, read_only=True)

    class Meta:
        model = Lote
        fields = [
            'id', 'codigo', 'uuid',
            'producto', 'finca', 'productor', 'productor_nombre',
            'variedad', 'cantidad', 'unidad', 'fecha_cosecha',
            'proceso', 'notas_produccion',
            'estado', 'estado_display',
            'qr_codigo', 'hash_blockchain',
            'fecha_creacion', 'fecha_publicacion',
            'movimientos', 'certificaciones'
        ]
        read_only_fields = [
            'codigo', 'uuid', 'qr_codigo',
            'hash_blockchain', 'fecha_creacion'
        ]


# ============================================
# TRAZABILIDAD PÚBLICA (lo que ve el cliente al escanear QR)
# ============================================
class CertificacionPublicaSerializer(CertificacionSerializer):
    """Certificación sin el archivo adjunto (los documentos son privados)."""
    class Meta(CertificacionSerializer.Meta):
        fields = [f for f in CertificacionSerializer.Meta.fields if f != 'documento']


class TrazabilidadPublicaSerializer(serializers.ModelSerializer):
    """
    Información pública que se muestra al escanear un QR.
    No requiere autenticación.
    """
    producto = ProductoSerializer(read_only=True)
    productor = serializers.SerializerMethodField()
    finca = serializers.SerializerMethodField()
    linea_tiempo = serializers.SerializerMethodField()
    certificaciones = CertificacionPublicaSerializer(many=True, read_only=True)

    class Meta:
        model = Lote
        fields = [
            'codigo', 'producto', 'variedad', 'cantidad', 'unidad',
            'fecha_cosecha', 'proceso', 'notas_produccion',
            'productor', 'finca', 'linea_tiempo', 'certificaciones',
            'fecha_publicacion', 'hash_blockchain'
        ]

    def get_productor(self, obj):
        return {
            'nombre': f"{obj.productor.first_name} {obj.productor.last_name}".strip() or obj.productor.username,
            'municipio': obj.productor.municipio,
            'verificado': obj.productor.verificado,
        }

    def get_finca(self, obj):
        return {
            'nombre': obj.finca.nombre,
            'municipio': obj.finca.municipio,
            'vereda': obj.finca.vereda,
            'departamento': obj.finca.departamento,
            # Las coordenadas exactas son privadas: no se publican.
        }

    def get_linea_tiempo(self, obj):
        movimientos = obj.movimientos.all().order_by('fecha')
        return [
            {
                'tipo': m.get_tipo_display(),
                'actor': m.actor.username,
                'origen': m.origen,
                'destino': m.destino,
                'descripcion': m.descripcion,
                'fecha': m.fecha,
                'latitud': str(m.latitud) if m.latitud else None,
                'longitud': str(m.longitud) if m.longitud else None,
            }
            for m in movimientos
        ]