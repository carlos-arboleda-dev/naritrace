from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario
from .serializers import RegistroSerializer

class RegistroView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny] # Cualquiera puede registrarse

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        usuario = serializer.instance
        pendiente = usuario.solicitudes.filter(estado='pendiente').exists()
        return Response(
            {
                "mensaje": "Usuario creado exitosamente",
                "solicitud_pendiente": pendiente,
                "usuario": {k: v for k, v in serializer.data.items() if k != 'password'},
            },
            status=status.HTTP_201_CREATED
        )


class LoginAuditadoView(ObtainAuthToken):
    """
    Igual que /api/token/ pero deja huella en la bitácora y bloquea 10 minutos
    tras 5 intentos fallidos seguidos sobre la misma cuenta.
    """
    MAX_FALLOS = 5
    VENTANA = timedelta(minutes=10)

    def post(self, request, *args, **kwargs):
        from trazabilidad.auditoria import auditar
        from trazabilidad.models import EventoAuditoria

        ident = str(request.data.get('username', ''))[:150]
        cuenta = Usuario.objects.filter(username=ident).first()
        recurso = cuenta.codigo if cuenta else ident

        fallos = EventoAuditoria.objects.filter(
            accion='Intento de acceso fallido', recurso=recurso, fecha__gte=timezone.now() - self.VENTANA).count()
        if fallos >= self.MAX_FALLOS:
            auditar(None, 'Bloqueó acceso', recurso, 'Intentos repetidos', 'rechazado')
            return Response({'non_field_errors': ['Demasiados intentos. Espera unos minutos e inténtalo de nuevo.']},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():
            auditar(None, 'Intento de acceso fallido', recurso, 'Credenciales inválidas', 'rechazado')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=serializer.validated_data['user'])
        return Response({'token': token.key})
