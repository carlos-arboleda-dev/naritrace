from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'rol', 'municipio', 'verificado', 'is_staff')
    list_filter = ('rol', 'verificado', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'municipio')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Información NariTrace', {
            'fields': ('rol', 'telefono', 'municipio', 'verificado'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información NariTrace', {
            'fields': ('rol', 'telefono', 'municipio', 'verificado'),
        }),
    )