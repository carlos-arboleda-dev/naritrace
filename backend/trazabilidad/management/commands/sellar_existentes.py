from django.core.management.base import BaseCommand
from django.db import transaction

from trazabilidad import ledger
from trazabilidad.models import BloqueLedger, Lote, Movimiento


class Command(BaseCommand):
    help = ('Sella en el registro encadenado los lotes publicados y movimientos creados ANTES de existir el sellado. '
            'Es seguro ejecutarlo varias veces: solo toca lo que aún no tiene bloque.')

    @transaction.atomic
    def handle(self, *args, **opts):
        lotes = 0
        for lote in Lote.objects.exclude(estado__in=['borrador']).order_by('fecha_publicacion', 'id'):
            if lote.fecha_publicacion is None:
                from django.utils import timezone
                Lote.objects.filter(pk=lote.pk).update(fecha_publicacion=lote.fecha_creacion or timezone.now())
                lote.refresh_from_db()
            if not lote.custodio_id:
                Lote.objects.filter(pk=lote.pk).update(custodio=lote.productor)
            if not BloqueLedger.objects.filter(tipo='lote', referencia=str(lote.pk)).exists():
                ledger.sellar_lote(lote)
                lotes += 1
        movs = 0
        for mov in Movimiento.objects.exclude(lote__estado='borrador').order_by('fecha', 'id'):
            if not BloqueLedger.objects.filter(tipo='movimiento', referencia=str(mov.pk)).exists():
                ledger.sellar_movimiento(mov)
                movs += 1
        r = ledger.verificar_cadena()
        self.stdout.write(self.style.SUCCESS(
            f"Sellados: {lotes} lotes y {movs} movimientos. Cadena: {r['bloques']} bloques, "
            f"{'ÍNTEGRA' if r['valida'] else 'CON ERRORES: ' + r['error']['motivo']}."))
