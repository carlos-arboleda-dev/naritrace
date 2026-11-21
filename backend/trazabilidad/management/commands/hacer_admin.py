from django.core.management.base import BaseCommand, CommandError

from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Convierte un usuario existente en administrador: python manage.py hacer_admin <usuario>'

    def add_arguments(self, parser):
        parser.add_argument('username')

    def handle(self, *args, **opts):
        try:
            u = Usuario.objects.get(username=opts['username'])
        except Usuario.DoesNotExist:
            raise CommandError(f"No existe el usuario '{opts['username']}'.")
        u.rol = 'administrador'
        u.is_staff = True
        u.verificado = True
        u.save(update_fields=['rol', 'is_staff', 'verificado'])
        self.stdout.write(self.style.SUCCESS(f"{u.username} ahora es administrador."))
