"""Operaciones de la cadena: crear movimientos sellados y traspasos de custodia."""
from django.core.exceptions import ValidationError
from django.db import transaction

from usuarios.models import ROLES_INTERMEDIARIOS
from . import ledger
from .auditoria import auditar
from .models import Lote, Movimiento


@transaction.atomic
def crear_movimiento(lote, actor, tipo, origen='', destino='', descripcion='', latitud=None, longitud=None):
    """Crea un movimiento inmutable, lo sella en el registro encadenado y lo audita."""
    mov = Movimiento.objects.create(
        lote=lote, actor=actor, tipo=tipo, origen=origen, destino=destino,
        descripcion=descripcion, latitud=latitud, longitud=longitud,
    )
    ledger.sellar_movimiento(mov)
    mov.refresh_from_db()
    auditar(actor, f"Registró {mov.get_tipo_display().lower()}", lote.codigo,
            destino or descripcion[:60] or lote.producto.nombre)
    return mov


def _ubicacion(usuario):
    return usuario.municipio or usuario.nombre_completo


def puede_operar(usuario, lote, accion):
    """Reglas de quién puede hacer qué con un lote. Devuelve (ok, motivo_si_no)."""
    if lote.estado == 'borrador':
        return False, 'El lote aún es un borrador.'
    if lote.estado == 'archivado':
        return False, 'El lote está archivado.'
    if accion == 'recibir':
        if usuario.rol not in ROLES_INTERMEDIARIOS:
            return False, 'Solo distribuidores, acopiadores y transportadores reciben lotes.'
        if lote.custodio_id == usuario.id:
            return False, 'Este lote ya está en tu custodia.'
        if lote.estado == 'entregado':
            return False, 'Este lote ya fue entregado al cliente final.'
        if lote.custodio_id != lote.productor_id and lote.estado != 'en_transito':
            return False, 'Otro actor lo tiene en custodia y aún no lo despacha.'
        return True, ''
    if accion in ('despachar', 'entregar'):
        if lote.custodio_id != usuario.id:
            return False, 'Solo quien tiene el lote en custodia puede registrar esta operación.'
        if lote.estado != 'publicado':
            return False, 'El lote debe estar en custodia (no en tránsito ni entregado).'
        return True, ''
    return False, 'Operación desconocida.'


def acciones_disponibles(usuario, lote):
    return [a for a in ('recibir', 'despachar', 'entregar') if puede_operar(usuario, lote, a)[0]]


@transaction.atomic
def operar(lote, usuario, accion, destino='', descripcion='', tipo_envio='transporte'):
    """Ejecuta recibir / despachar / entregar. Lanza ValidationError si no está permitido."""
    lote = Lote.objects.select_for_update().get(pk=lote.pk)
    ok, motivo = puede_operar(usuario, lote, accion)
    if not ok:
        raise ValidationError(motivo)

    if accion == 'recibir':
        previo = lote.custodio or lote.productor
        mov = crear_movimiento(lote, usuario, Movimiento.Tipo.ACOPIO, origen=previo.nombre_completo,
                               destino=_ubicacion(usuario), descripcion=descripcion or 'Recepción del lote')
        Lote.objects.filter(pk=lote.pk).update(custodio=usuario, estado=Lote.Estado.PUBLICADO)
    elif accion == 'despachar':
        if not destino.strip():
            raise ValidationError('Indica el destino del despacho.')
        tipo = Movimiento.Tipo.DISTRIBUCION if tipo_envio == 'distribucion' else Movimiento.Tipo.TRANSPORTE
        mov = crear_movimiento(lote, usuario, tipo, origen=_ubicacion(usuario), destino=destino.strip(),
                               descripcion=descripcion)
        Lote.objects.filter(pk=lote.pk).update(estado=Lote.Estado.EN_TRANSITO)
    else:  # entregar
        if not destino.strip():
            raise ValidationError('Indica a quién o dónde se entregó el lote.')
        mov = crear_movimiento(lote, usuario, Movimiento.Tipo.ENTREGA, origen=_ubicacion(usuario),
                               destino=destino.strip(), descripcion=descripcion)
        Lote.objects.filter(pk=lote.pk).update(estado=Lote.Estado.ENTREGADO)
    return mov
