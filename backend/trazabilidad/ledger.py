"""
Registro encadenado de solo-añadir ("blockchain" privado).

Qué garantiza
  * Cada lote publicado y cada movimiento se sellan con un hash SHA-256.
  * Cada bloque incluye el hash del anterior: alterar o borrar algo del pasado rompe la cadena.
  * `verificar_cadena()` y `verificar_lote()` recomputan todo y delatan cualquier cambio,
    incluso si se hizo directamente en la base de datos.

Qué NO es
  * No es una red distribuida: quien controla el servidor podría reescribir la cadena completa.
    Para blindarlo frente al operador se puede anclar periódicamente el último hash en una
    red pública (p. ej. OpenTimestamps o Polygon). Ver docs/PROGRESO.md.
"""
import hashlib
import json
from datetime import timezone as dt_timezone

from django.db import transaction
from django.utils import timezone

from .models import BloqueLedger, Lote, Movimiento

GENESIS = '0' * 64


def _canonico(datos) -> str:
    return json.dumps(datos, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()


def hash_contenido(contenido) -> str:
    return _sha(_canonico(contenido))


def _hash_bloque(indice, hash_anterior, h_contenido, fecha) -> str:
    return _sha(f"{indice}|{hash_anterior}|{h_contenido}|{fecha.astimezone(dt_timezone.utc).isoformat()}")


@transaction.atomic
def sellar(tipo: str, referencia, lote_id: int, contenido: dict) -> BloqueLedger:
    """Añade un bloque al final de la cadena."""
    ultimo = BloqueLedger.objects.order_by('-indice').first()
    indice = (ultimo.indice + 1) if ultimo else 1
    anterior = ultimo.hash if ultimo else GENESIS
    fecha = timezone.now()
    h_cont = hash_contenido(contenido)
    return BloqueLedger.objects.create(
        indice=indice, tipo=tipo, referencia=str(referencia), lote_id=lote_id,
        contenido=contenido, hash_contenido=h_cont, hash_anterior=anterior,
        hash=_hash_bloque(indice, anterior, h_cont, fecha), fecha=fecha,
    )


def sellar_lote(lote: Lote) -> BloqueLedger:
    """Sella un lote recién publicado y guarda la huella en `lote.hash_blockchain`."""
    lote = Lote.objects.get(pk=lote.pk)                 # datos tal como quedaron en la BD
    bloque = sellar('lote', lote.pk, lote.pk, lote.contenido_inmutable())
    Lote.objects.filter(pk=lote.pk).update(hash_blockchain=bloque.hash)
    return bloque


def sellar_movimiento(mov: Movimiento) -> BloqueLedger:
    mov = Movimiento.objects.select_related('lote').get(pk=mov.pk)
    bloque = sellar('movimiento', mov.pk, mov.lote_id, mov.contenido_inmutable())
    Movimiento.objects.filter(pk=mov.pk).update(hash_blockchain=bloque.hash)
    return bloque


# ------------------------------------------------------------------ verificación
def _estado_actual(bloque: BloqueLedger):
    """Contenido que hoy tiene en la BD el objeto sellado (None si ya no existe)."""
    if bloque.tipo == 'lote':
        obj = Lote.objects.filter(pk=bloque.referencia).first()
    else:
        obj = Movimiento.objects.select_related('lote').filter(pk=bloque.referencia).first()
    return obj.contenido_inmutable() if obj else None


def _revisar(bloque: BloqueLedger, anterior_hash: str):
    """Devuelve None si el bloque es válido o un texto con el motivo del fallo."""
    if bloque.hash_anterior != anterior_hash:
        return 'La cadena está rota: el bloque no enlaza con el anterior (¿se borró o insertó algo?).'
    if hash_contenido(bloque.contenido) != bloque.hash_contenido:
        return 'El contenido guardado en el bloque fue alterado.'
    if _hash_bloque(bloque.indice, bloque.hash_anterior, bloque.hash_contenido, bloque.fecha) != bloque.hash:
        return 'La huella del bloque no coincide con sus datos.'
    actual = _estado_actual(bloque)
    if actual is None:
        return 'El registro sellado fue eliminado de la base de datos.'
    if hash_contenido(actual) != bloque.hash_contenido:
        return 'Los datos actuales no coinciden con los que se sellaron: fueron modificados.'
    return None


def verificar_cadena() -> dict:
    """Revisa toda la cadena de principio a fin."""
    anterior = GENESIS
    total = 0
    ultimo = None
    esperado = 1
    for b in BloqueLedger.objects.order_by('indice').iterator():
        total += 1
        motivo = None
        if b.indice != esperado:
            motivo = f'Falta el bloque #{esperado}: se eliminó un bloque de la cadena.'
        motivo = motivo or _revisar(b, anterior)
        if motivo:
            return {'valida': False, 'bloques': total, 'ultimo_hash': ultimo,
                    'error': {'indice': b.indice, 'referencia': b.referencia, 'tipo': b.tipo, 'motivo': motivo},
                    'verificado_en': timezone.now()}
        anterior, ultimo, esperado = b.hash, b.hash, b.indice + 1
    return {'valida': True, 'bloques': total, 'ultimo_hash': ultimo, 'error': None, 'verificado_en': timezone.now()}


def verificar_lote(lote: Lote) -> dict:
    """Revisa solo los bloques de un lote y de sus movimientos (y su enlace con la cadena)."""
    bloques = list(BloqueLedger.objects.filter(lote_id=lote.pk).order_by('indice'))
    if not bloques:
        return {'valida': False, 'sellado': False, 'bloques': 0, 'hash': '', 'error': 'Este lote aún no está sellado.',
                'verificado_en': timezone.now()}
    for b in bloques:
        previo = BloqueLedger.objects.filter(indice=b.indice - 1).first()
        previo_hash = previo.hash if previo else GENESIS
        motivo = _revisar(b, previo_hash)
        if motivo:
            return {'valida': False, 'sellado': True, 'bloques': len(bloques), 'hash': bloques[0].hash,
                    'error': f'Bloque #{b.indice}: {motivo}', 'verificado_en': timezone.now()}
    return {'valida': True, 'sellado': True, 'bloques': len(bloques), 'hash': bloques[0].hash,
            'error': None, 'verificado_en': timezone.now()}
