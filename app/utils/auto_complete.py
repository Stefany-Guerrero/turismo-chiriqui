from datetime import date
import logging

logger = logging.getLogger(__name__)

def completar_solicitudes_vencidas():
    """Marca como 'completada' las solicitudes cuya fecha_fin ya pasó"""
    from app import db
    from app.models.reserva import Reserva
    from app.models.notificacion import Notificacion
    from app.models.usuario import Usuario
    from app.utils import panama_now

    hoy = date.today()
    solicitudes = Reserva.query.filter(
        Reserva.tipo == 'solicitud',
        Reserva.estado.in_(['aprobada', 'cotizada']),
        Reserva.fecha_fin < hoy,
        Reserva.fecha_fin.isnot(None)
    ).all()

    if not solicitudes:
        return 0

    count = 0
    for s in solicitudes:
        try:
            s.estado = 'completada'

            if s.cliente and s.cliente.usuario:
                notif = Notificacion(
                    usuario_id=s.cliente.usuario.id,
                    titulo='Viaje completado',
                    mensaje=f'Tu viaje #{s.id} ({s.destino_preferido or "Personalizado"}) ha sido completado. ¡Esperamos que haya sido una gran experiencia!',
                    tipo='solicitud_completada',
                    referencia_id=s.id,
                    referencia_tipo='solicitud'
                )
                db.session.add(notif)

            count += 1
        except Exception as e:
            logger.error(f'Error completando solicitud #{s.id}: {e}')

    if count:
        try:
            db.session.commit()
            logger.info(f'{count} solicitud(es) completada(s) automáticamente')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error al commit auto-completar: {e}')

    return count
