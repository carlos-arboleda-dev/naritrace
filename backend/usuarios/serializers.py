from rest_framework import serializers
from .models import Usuario, SolicitudRol

# Roles que una persona puede pedir al registrarse. "administrador" nunca se autoasigna.
ROLES_AUTOSERVICIO = ['productor', 'distribuidor', 'acopiador', 'transportador', 'cliente']


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    rol = serializers.ChoiceField(choices=ROLES_AUTOSERVICIO, default='cliente')

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'rol', 'telefono', 'municipio']

    def create(self, validated_data):
        password = validated_data.pop('password')
        rol_pedido = validated_data.pop('rol', 'cliente')

        # Todo usuario nuevo entra como cliente; el rol operativo lo aprueba un administrador.
        usuario = Usuario(**validated_data, rol=Usuario.Rol.CLIENTE)
        usuario.set_password(password)
        usuario.save()

        if rol_pedido != 'cliente':
            SolicitudRol.objects.create(usuario=usuario, rol_solicitado=rol_pedido)
            from trazabilidad.auditoria import auditar
            auditar(usuario, 'Solicitó rol', usuario.codigo, dict(Usuario.Rol.choices)[rol_pedido])
        return usuario
