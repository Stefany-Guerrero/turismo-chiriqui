from flask import request
from app.utils import panama_now


def registrar_auditoria(accion, entidad=None, entidad_id=None, detalle=None):
    """Registra una acción administrativa en la tabla auditoria_logs."""
    try:
        from flask_login import current_user
        from app import db
        from app.models.auditoria import AuditoriaLog

        registro = AuditoriaLog(
            usuario_id=current_user.id if current_user.is_authenticated else None,
            usuario_nombre=current_user.nombre_completo if current_user.is_authenticated else None,
            accion=accion,
            entidad=entidad,
            entidad_id=entidad_id,
            detalle=(detalle or '')[:500],
            ip=request.headers.get('X-Forwarded-For', request.remote_addr or ''),
            fecha=panama_now()
        )
        db.session.add(registro)
        db.session.commit()
    except Exception as e:
        from flask import current_app
        try:
            from app import db
            db.session.rollback()
        except Exception:
            pass
        current_app.logger.error(f'Error registrando auditoría ({accion}): {e}')
