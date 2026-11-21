from django.contrib.auth.models import AbstractUser
from django.db import models


# Roles que participan en la cadena después del productor (usan el panel de operaciones)
ROLES_INTERMEDIARIOS = ('distribuidor', 'acopiador', 'transportador')


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para NariTrace.
    Extiende AbstractUser con un rol y datos básicos.
    """

    class Rol(models.TextChoices):
        PRODUCTOR = 'productor', 'Productor'
        DISTRIBUIDOR = 'distribuidor', 'Distribuidor'
        ACOPIADOR = 'acopiador', 'Acopiador'
        TRANSPORTADOR = 'transportador', 'Transportador'
        ADMINISTRADOR = 'administrador', 'Administrador'
        CLIENTE = 'cliente', 'Cliente'

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.CLIENTE,
        verbose_name="Rol",
    )
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    municipio = models.CharField(max_length=100, blank=True, verbose_name="Municipio")
    verificado = models.BooleanField(default=False, verbose_name="Verificado")

    @property
    def codigo(self):
        """Identificador legible usado en la bitácora: USR-0148."""
        return f"USR-{self.pk:04d}" if self.pk else "USR-????"

    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def es_intermediario(self):
        return self.rol in ROLES_INTERMEDIARIOS

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']


class SolicitudRol(models.Model):
    """
    Un usuario nuevo entra como "cliente" y pide un rol (productor, distribuidor…).
    Un administrador la aprueba o la rechaza. La asignación de rol NO certifica al usuario.
    """

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADA = 'aprobada', 'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes')
    rol_solicitado = models.CharField(max_length=20, choices=Usuario.Rol.choices)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    nota = models.CharField(max_length=300, blank=True, verbose_name="Nota del administrador")
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    resuelta_por = models.ForeignKey(
        Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name='solicitudes_resueltas'
    )
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} → {self.rol_solicitado} ({self.estado})"

    class Meta:
        verbose_name = "Solicitud de rol"
        verbose_name_plural = "Solicitudes de rol"
        ordering = ['-fecha_solicitud']
