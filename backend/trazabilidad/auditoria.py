"""Registro de auditoría: quién hizo qué y cuándo."""
from .models import EventoAuditoria


def auditar(usuario, accion, recurso='', detalle='', resultado='completado'):
    """Guarda un evento. `usuario` puede ser None (se registra como 'Sistema')."""
    autenticado = usuario is not None and getattr(usuario, 'is_authenticated', False)
    return EventoAuditoria.objects.create(
        usuario=usuario if autenticado else None,
        usuario_texto='' if autenticado else 'Sistema',
        accion=accion[:80],
        recurso=str(recurso)[:120],
        detalle=str(detalle)[:250],
        resultado=resultado,
    )
