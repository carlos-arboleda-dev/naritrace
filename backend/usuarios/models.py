from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para NariTrace.
    Extiende AbstractUser con un rol y datos básicos.
    """

    class Rol(models.TextChoices):
        PRODUCTOR = 'productor', 'Productor'
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

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']