from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid



class Producto(models.Model):
    """
    Catálogo de productos agropecuarios rastreables.
    Ej: Café Castillo, Cacao Fino de Aroma, Trucha Arcoíris.
    """

    class Categoria(models.TextChoices):
        CAFE = 'cafe', 'Café'
        CACAO = 'cacao', 'Cacao'
        ACUICULTURA = 'acuicultura', 'Acuicultura'
        FRUTAS = 'frutas', 'Frutas'
        PANCOGER = 'pancoger', 'Pancoger'
        OTRO = 'otro', 'Otro'

    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        verbose_name="Categoría",
    )
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    unidad_medida = models.CharField(
        max_length=20,
        default='kg',
        verbose_name="Unidad de medida",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['categoria', 'nombre']


class Finca(models.Model):

        """
        Predio del productor donde se cultiva o produce.
        Almacena geolocalización (punto y polígono).
        """

        productor = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='fincas',
            verbose_name="Productor",
        )
        nombre = models.CharField(max_length=150, verbose_name="Nombre de la finca")
        municipio = models.CharField(max_length=100, verbose_name="Municipio")
        vereda = models.CharField(max_length=100, blank=True, verbose_name="Vereda")
        departamento = models.CharField(
            max_length=100,
            default='Nariño',
            verbose_name="Departamento",
        )

        # Geolocalización
        latitud = models.DecimalField(
            max_digits=10,
            decimal_places=7,
            null=True,
            blank=True,
            verbose_name="Latitud",
        )
        longitud = models.DecimalField(
            max_digits=10,
            decimal_places=7,
            null=True,
            blank=True,
            verbose_name="Longitud",
        )
        area_hectareas = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            null=True,
            blank=True,
            verbose_name="Área (hectáreas)",
        )
        # Polígono de la finca en formato GeoJSON
        poligono_geojson = models.JSONField(
            null=True,
            blank=True,
            verbose_name="Polígono (GeoJSON)",
        )

        activa = models.BooleanField(default=True, verbose_name="Activa")
        fecha_registro = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.nombre} — {self.municipio}"

        class Meta:
            verbose_name = "Finca"
            verbose_name_plural = "Fincas"
            ordering = ['municipio', 'nombre']


class Lote(models.Model):
        """
        Unidad trazable. Cada lote tiene un código único y genera un QR.
        """

        class Estado(models.TextChoices):
            BORRADOR = 'borrador', 'Borrador'
            PUBLICADO = 'publicado', 'Publicado'
            EN_TRANSITO = 'en_transito', 'En tránsito'
            ENTREGADO = 'entregado', 'Entregado'
            ARCHIVADO = 'archivado', 'Archivado'

        # Identificación
        codigo = models.CharField(
            max_length=50,
            unique=True,
            editable=False,
            verbose_name="Código único",
        )
        uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

        # Relaciones
        finca = models.ForeignKey(
            Finca,
            on_delete=models.PROTECT,
            related_name='lotes',
            verbose_name="Finca de origen",
        )
        producto = models.ForeignKey(
            Producto,
            on_delete=models.PROTECT,
            related_name='lotes',
            verbose_name="Producto",
        )
        productor = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.PROTECT,
            related_name='lotes_producidos',
            verbose_name="Productor",
        )

        # Datos del lote
        variedad = models.CharField(max_length=100, blank=True, verbose_name="Variedad")
        cantidad = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            validators=[MinValueValidator(0)],
            verbose_name="Cantidad",
        )
        unidad = models.CharField(max_length=20, default='kg', verbose_name="Unidad")
        fecha_cosecha = models.DateField(verbose_name="Fecha de cosecha")
        proceso = models.CharField(
            max_length=100,
            blank=True,
            verbose_name="Proceso",
            help_text="Ej: Lavado, Secado, Fermentado",
        )
        notas_produccion = models.TextField(blank=True, verbose_name="Notas de producción")

        # Estado y QR
        estado = models.CharField(
            max_length=20,
            choices=Estado.choices,
            default=Estado.BORRADOR,
            verbose_name="Estado",
        )
        qr_codigo = models.CharField(
            max_length=255,
            blank=True,
            verbose_name="Contenido del QR",
        )
        hash_blockchain = models.CharField(
            max_length=255,
            blank=True,
            verbose_name="Hash en blockchain",
            help_text="Hash del registro en Hyperledger Fabric",
        )

        # Fechas
        fecha_creacion = models.DateTimeField(auto_now_add=True)
        fecha_publicacion = models.DateTimeField(null=True, blank=True)

        def save(self, *args, **kwargs):
            # Generar código único si no existe
            if not self.codigo:
                from django.utils import timezone
                year = timezone.now().year
                short_uuid = str(self.uuid)[:6].upper()
                self.codigo = f"NT-{year}-{short_uuid}"

            # Generar URL del QR
            if not self.qr_codigo and self.codigo:
                self.qr_codigo = f"https://naritrace.co/lote/{self.codigo}"

            super().save(*args, **kwargs)

        def __str__(self):
            return f"{self.codigo} — {self.producto.nombre}"

        class Meta:
            verbose_name = "Lote"
            verbose_name_plural = "Lotes"
            ordering = ['-fecha_creacion']


class Movimiento(models.Model):
        """
        Cada evento o transferencia del lote dentro de la cadena de suministro.
        """

        class Tipo(models.TextChoices):
            COSECHA = 'cosecha', 'Cosecha'
            BENEFICIO = 'beneficio', 'Beneficio'
            ACOPIO = 'acopio', 'Acopio'
            TRANSPORTE = 'transporte', 'Transporte'
            DISTRIBUCION = 'distribucion', 'Distribución'
            ENTREGA = 'entrega', 'Entrega al cliente'
            CERTIFICACION = 'certificacion', 'Certificación'
            OTRO = 'otro', 'Otro'

        lote = models.ForeignKey(
            Lote,
            on_delete=models.CASCADE,
            related_name='movimientos',
            verbose_name="Lote",
        )
        tipo = models.CharField(
            max_length=20,
            choices=Tipo.choices,
            verbose_name="Tipo de movimiento",
        )
        actor = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.PROTECT,
            related_name='movimientos_realizados',
            verbose_name="Responsable",
        )
        origen = models.CharField(max_length=200, blank=True, verbose_name="Origen")
        destino = models.CharField(max_length=200, blank=True, verbose_name="Destino")
        descripcion = models.TextField(blank=True, verbose_name="Descripción")

        # Geolocalización del evento
        latitud = models.DecimalField(
            max_digits=10, decimal_places=7, null=True, blank=True,
            verbose_name="Latitud",
        )
        longitud = models.DecimalField(
            max_digits=10, decimal_places=7, null=True, blank=True,
            verbose_name="Longitud",
        )

        # Blockchain
        hash_blockchain = models.CharField(
            max_length=255,
            blank=True,
            verbose_name="Hash en blockchain",
        )

        fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del movimiento")

        def __str__(self):
            return f"{self.get_tipo_display()} — {self.lote.codigo}"

        class Meta:
            verbose_name = "Movimiento"
            verbose_name_plural = "Movimientos"
            ordering = ['-fecha']


class Certificacion(models.Model):
        """
        Certificaciones asociadas a una finca o a un lote.
        Ej: Orgánica, Rainforest Alliance, Comercio Justo.
        """

        class Tipo(models.TextChoices):
            ORGANICA = 'organica', 'Orgánica'
            COMERCIO_JUSTO = 'comercio_justo', 'Comercio Justo'
            RAINFOREST = 'rainforest', 'Rainforest Alliance'
            UTZ = 'utz', 'UTZ Certified'
            LIBRE_DEFORESTACION = 'libre_deforestacion', 'Libre de deforestación'
            OTRA = 'otra', 'Otra'

        finca = models.ForeignKey(
            Finca,
            on_delete=models.CASCADE,
            related_name='certificaciones',
            null=True,
            blank=True,
            verbose_name="Finca",
        )
        lote = models.ForeignKey(
            Lote,
            on_delete=models.CASCADE,
            related_name='certificaciones',
            null=True,
            blank=True,
            verbose_name="Lote",
        )
        tipo = models.CharField(
            max_length=30,
            choices=Tipo.choices,
            verbose_name="Tipo",
        )
        entidad_certificadora = models.CharField(
            max_length=150,
            blank=True,
            verbose_name="Entidad certificadora",
        )
        numero_certificado = models.CharField(
            max_length=100,
            blank=True,
            verbose_name="Número de certificado",
        )
        fecha_emision = models.DateField(null=True, blank=True, verbose_name="Fecha de emisión")
        fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de vencimiento")
        documento = models.FileField(
            upload_to='certificaciones/',
            null=True,
            blank=True,
            verbose_name="Documento",
        )
        activa = models.BooleanField(default=True, verbose_name="Activa")

        def __str__(self):
            return f"{self.get_tipo_display()} — {self.entidad_certificadora}"

        class Meta:
            verbose_name = "Certificación"
            verbose_name_plural = "Certificaciones"
            ordering = ['-fecha_emision']

            