"""
Carga datos de demostración para ver los tres paneles con información.

Usuarios (contraseña de todos: demo12345)
  laura                      → administradora
  maria, luis, rosa, jorge…  → productores
  andres → distribuidor · sofia → acopiadora · pedro → transportador

Solo se ejecuta una vez (si ya existe 'laura' no hace nada).
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from trazabilidad import ledger
from trazabilidad.models import ConsultaPublica, EventoAuditoria, Finca, Lote, Movimiento, Producto
from usuarios.models import SolicitudRol, Usuario

PASS = 'demo12345'
MUNICIPIOS = {  # nombre: (peso, latitud, longitud)
    'Buesaco': (32, 1.3862, -77.1568), 'Pasto': (24, 1.2136, -77.2811), 'La Unión': (18, 1.6000, -77.1300),
    'Sandoná': (15, 1.2856, -77.4719), 'Consacá': (11, 1.2000, -77.4600),
}
PRODUCTORES = [
    ('maria', 'María', 'Rodríguez', 'Buesaco'), ('luis', 'Luis', 'Chamorro', 'Buesaco'),
    ('rosa', 'Rosa', 'Benavides', 'Pasto'), ('jorge', 'Jorge', 'Erazo', 'Pasto'),
    ('ana', 'Ana', 'Guerrero', 'La Unión'), ('carlos', 'Carlos', 'Mora', 'La Unión'),
    ('elena', 'Elena', 'Cuaical', 'Sandoná'), ('mario', 'Mario', 'Insuasty', 'Consacá'),
]
VARIEDADES = {'Café pergamino': ['Castillo', 'Caturra', 'Colombia'], 'Cacao seco (grano)': ['Criollo', 'CCN-51'],
              'Arveja verde': ['Santa Isabel'], 'Papa criolla': ['Criolla'], 'Fresa': ['Albión'], 'Aguacate Hass': ['Hass']}
PRODUCTOS_PESO = ['Café pergamino'] * 6 + ['Cacao seco (grano)', 'Arveja verde', 'Papa criolla', 'Fresa', 'Aguacate Hass']


def _evento(usuario, accion, recurso, detalle, cuando, resultado='completado', texto=''):
    e = EventoAuditoria.objects.create(usuario=usuario, usuario_texto=texto, accion=accion, recurso=recurso,
                                       detalle=detalle, resultado=resultado)
    EventoAuditoria.objects.filter(pk=e.pk).update(fecha=cuando)      # la bitácora fija la fecha al crear


def _movimiento(lote, actor, tipo, origen, destino, desc, cuando):
    m = Movimiento.objects.create(lote=lote, actor=actor, tipo=tipo, origen=origen, destino=destino, descripcion=desc)
    Movimiento.objects.filter(pk=m.pk).update(fecha=cuando)
    ledger.sellar_movimiento(m)
    _evento(actor, f"Registró {m.get_tipo_display().lower()}", lote.codigo, destino or desc, cuando)


class Command(BaseCommand):
    help = 'Carga usuarios, fincas, lotes, movimientos sellados y bitácora de demostración.'

    def handle(self, *args, **opts):
        if Usuario.objects.filter(username='laura').exists():
            self.stdout.write('Los datos de demostración ya existen; no se hizo nada.')
            return
        nombres = ['laura', 'andres', 'sofia', 'pedro'] + [u for u, *_ in PRODUCTORES]
        choque = list(Usuario.objects.filter(username__in=nombres).values_list('username', flat=True))
        if choque:
            self.stdout.write(self.style.ERROR(
                f"No se cargó la demo: ya existen usuarios con esos nombres ({', '.join(choque)}). "
                "Usa una base de datos nueva (borra db.sqlite3 y corre migrate) para la demostración."))
            return
        random.seed(7)
        call_command('cargar_catalogo', verbosity=0)
        ahora = timezone.now()

        laura = Usuario.objects.create_user('laura', password=PASS, first_name='Laura', last_name='Castro',
                                            rol='administrador', is_staff=True, municipio='Pasto', verificado=True)
        inter = [Usuario.objects.create_user(u, password=PASS, first_name=n, last_name=a, rol=r, municipio=m, verificado=True)
                 for u, n, a, r, m in [('andres', 'Andrés', 'Ibarra', 'distribuidor', 'Pasto'),
                                       ('sofia', 'Sofía', 'Realpe', 'acopiador', 'Buesaco'),
                                       ('pedro', 'Pedro', 'Burbano', 'transportador', 'Pasto')]]

        # ---- productores y fincas (algunas sin coordenadas, para el indicador EUDR)
        fincas = []
        for i, (u, n, a, m) in enumerate(PRODUCTORES):
            prod = Usuario.objects.create_user(u, password=PASS, first_name=n, last_name=a, rol='productor',
                                               municipio=m, verificado=(i % 3 != 2))
            _, lat, lon = MUNICIPIOS[m]
            nombre = 'Finca El Mirador' if u == 'maria' else 'Finca ' + random.choice(
                ['La Esperanza', 'Buenos Aires', 'El Paraíso', 'San José', 'Los Naranjos'])
            con_geo = i % 4 != 3
            poligono = {'type': 'Polygon', 'coordinates': [[[lon, lat], [lon + .002, lat], [lon + .002, lat + .002],
                                                            [lon, lat + .002], [lon, lat]]]} if i % 3 == 0 else None
            fincas.append(Finca.objects.create(
                productor=prod, nombre=nombre, municipio=m, vereda='San Antonio' if u == 'maria' else random.choice(['El Placer', 'La Cocha', 'Altamira']),
                latitud=Decimal(str(round(lat + random.uniform(-.03, .03), 6))) if con_geo else None,
                longitud=Decimal(str(round(lon + random.uniform(-.03, .03), 6))) if con_geo else None,
                area_hectareas=Decimal(str(round(random.uniform(0.8, 6), 2))), poligono_geojson=poligono))
        pesos = [MUNICIPIOS[f.municipio][0] for f in fincas]
        productos = {p.nombre: p for p in Producto.objects.filter(nombre__in=list(VARIEDADES))}

        # ---- lotes publicados en 6 meses, sellados en la cadena, con recorrido por la cadena
        for _ in range(96):
            dias = int(random.triangular(0, 175, 5))
            f = random.choices(fincas, weights=pesos)[0]
            nombre_p = random.choice(PRODUCTOS_PESO)
            publicado = ahora - timedelta(days=dias, hours=random.randint(0, 6))
            lote = Lote.objects.create(
                finca=f, producto=productos[nombre_p], productor=f.productor, variedad=random.choice(VARIEDADES[nombre_p]),
                cantidad=Decimal(random.choice([48, 72, 84, 96, 120, 160, 240, 320])), unidad='kg',
                fecha_cosecha=(publicado - timedelta(days=3)).date(),
                proceso=random.choice(['Lavado', 'Honey', 'Natural']) if nombre_p == 'Café pergamino' else '',
                estado='publicado', fecha_publicacion=publicado, custodio=f.productor)
            ledger.sellar_lote(lote)
            _evento(f.productor, 'Publicó lote', lote.codigo, f"{lote.producto.nombre} · {f.nombre}", publicado)

            t = publicado + timedelta(hours=5)
            if random.random() < .8 and t < ahora:
                _movimiento(lote, f.productor, 'beneficio', f.nombre, '', 'Beneficio húmedo y secado', t)
            suerte = random.random()
            if suerte > .30 and dias >= 1:
                a = random.choices(inter, weights=[5, 3, 2])[0]
                t += timedelta(days=random.randint(0, 1), hours=3)
                _movimiento(lote, a, 'acopio', f.productor.nombre_completo, a.municipio, 'Recepción del lote', min(t, ahora - timedelta(minutes=5)))
                estado = 'publicado'
                if suerte > .55 and dias >= 2:
                    t += timedelta(days=1)
                    _movimiento(lote, a, 'transporte', a.municipio, random.choice(['Pasto', 'Bogotá', 'Cali', 'Ipiales']), '', min(t, ahora - timedelta(minutes=4)))
                    estado = 'en_transito'
                    if suerte > .70 and dias >= 4:
                        t += timedelta(days=2)
                        _movimiento(lote, a, 'entrega', a.municipio, random.choice(['Cafetería Andina', 'Tienda Origen', 'Exportadora Pacífico']), '', min(t, ahora - timedelta(minutes=3)))
                        estado = 'entregado'
                Lote.objects.filter(pk=lote.pk).update(custodio=a, estado=estado)
            for _ in range(random.choice([0, 0, 1, 2, 4, 6])):
                c = ConsultaPublica.objects.create(lote=lote)
                ConsultaPublica.objects.filter(pk=c.pk).update(
                    fecha=ahora - timedelta(days=random.triangular(0, min(dias + 1, 90), 2), hours=random.randint(0, 20)))

        # ---- borrador de María ("Continúa donde quedaste")
        maria = Usuario.objects.get(username='maria')
        fm = Finca.objects.get(productor=maria)
        Lote.objects.create(finca=fm, producto=productos['Café pergamino'], productor=maria, variedad='Castillo',
                            cantidad=0, unidad='kg', fecha_cosecha=(ahora - timedelta(days=1)).date(), estado='borrador')

        # ---- solicitudes de rol pendientes (5 distribuidores, 2 productores)
        for i, rol in enumerate(['distribuidor'] * 5 + ['productor'] * 2):
            u = Usuario.objects.create_user(f'solicitante{i + 1}', password=PASS, first_name=random.choice(['Camilo', 'Diana', 'Hugo', 'Paula', 'Iván', 'Lucía', 'Tomás']),
                                            last_name=random.choice(['Ortiz', 'Pantoja', 'Cabrera', 'Villota']), rol='cliente',
                                            municipio=random.choice(list(MUNICIPIOS)), email=f'solicitante{i + 1}@ejemplo.co')
            s = SolicitudRol.objects.create(usuario=u, rol_solicitado=rol)
            SolicitudRol.objects.filter(pk=s.pk).update(fecha_solicitud=ahora - timedelta(days=random.choice([0, 1, 2, 5, 6])))
            _evento(u, 'Solicitó rol', u.codigo, u.get_rol_display() if False else dict(Usuario.Rol.choices)[rol], ahora - timedelta(days=1))

        # ---- eventos recientes de la bitácora (para la tabla del resumen)
        d = Usuario.objects.get(username='andres')
        _evento(laura, 'Actualizó rol', d.codigo, 'Distribuidor', ahora - timedelta(hours=2))
        _evento(None, 'Bloqueó acceso', 'USR-0093', 'Intentos repetidos', ahora - timedelta(hours=2, minutes=20), 'rechazado', 'Sistema')
        _evento(maria, 'Guardó borrador', 'Café Castillo · El Mirador', 'Castillo', ahora - timedelta(hours=18))

        n = ledger.verificar_cadena()
        self.stdout.write(self.style.SUCCESS(
            f"Demo lista: {Lote.objects.count()} lotes, {Movimiento.objects.count()} movimientos, "
            f"{n['bloques']} bloques (cadena {'íntegra' if n['valida'] else 'ALTERADA'})."))
        self.stdout.write('Usuarios: laura (admin) · maria (productora) · andres (distribuidor) — contraseña: demo12345')
