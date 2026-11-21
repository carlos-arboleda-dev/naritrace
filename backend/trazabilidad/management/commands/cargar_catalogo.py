from django.core.management.base import BaseCommand

from trazabilidad.models import Producto

CATALOGO = {
    'cafe': ['Café pergamino', 'Café verde (trillado)', 'Café tostado'],
    'cacao': ['Cacao en baba', 'Cacao seco (grano)'],
    'palma': ['Fruto de palma de aceite', 'Aceite crudo de palma'],
    'leguminosas': ['Arveja verde', 'Fríjol', 'Haba'],
    'tuberculos': ['Papa', 'Papa criolla', 'Yuca'],
    'hortalizas': ['Tomate', 'Repollo', 'Coliflor', 'Cebolla', 'Zanahoria'],
    'frutas': ['Fresa', 'Mora de Castilla', 'Lulo', 'Granadilla', 'Aguacate Hass', 'Tomate de árbol'],
    'acuicultura': ['Trucha arcoíris', 'Tilapia'],
    'pancoger': ['Maíz', 'Plátano'],
}


class Command(BaseCommand):
    help = 'Carga el catálogo de productos de Nariño (no duplica los existentes).'

    def handle(self, *args, **opts):
        nuevos = 0
        for categoria, nombres in CATALOGO.items():
            for nombre in nombres:
                _, creado = Producto.objects.get_or_create(nombre=nombre, defaults={'categoria': categoria})
                nuevos += creado
        self.stdout.write(self.style.SUCCESS(f'Catálogo listo: {nuevos} productos nuevos.'))
