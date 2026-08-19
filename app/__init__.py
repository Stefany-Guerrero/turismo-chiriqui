from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf import CSRFProtect
import os
import threading
import logging
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.usuario import Usuario
        return Usuario.query.get(int(user_id))
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['JSON_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'comprobantes'), exist_ok=True)

    from app.routes import auth_bp, main_bp, servicios_bp, reservas_bp, promociones_bp, planificador_bp, solicitudes_bp, proveedores_bp, transacciones_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(servicios_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(promociones_bp)
    app.register_blueprint(planificador_bp)
    app.register_blueprint(solicitudes_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(transacciones_bp)
    
    @app.template_filter('local_datetime')
    def local_datetime_filter(dt, fmt='%d/%m/%Y %I:%M %p'):
        if dt is None:
            return '—'
        return dt.strftime(fmt)

    @app.template_filter('hora_12')
    def hora_12_filter(h):
        if not h:
            return '—'
        try:
            partes = str(h).strip().split(':')
            if len(partes) < 2:
                return h
            hora = int(partes[0])
            minutos = partes[1][:2]
            sufijo = 'AM' if hora < 12 else 'PM'
            hora12 = hora % 12
            if hora12 == 0:
                hora12 = 12
            return f'{hora12}:{minutos} {sufijo}'
        except Exception:
            return h

    @app.template_filter('fecha_larga')
    def fecha_larga_filter(dt):
        if dt is None:
            return '—'
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        try:
            d = dt.date() if hasattr(dt, 'date') else dt
            return f"{d.day} de {meses[d.month - 1]} de {d.year}"
        except Exception:
            return dt.strftime('%d/%m/%Y')

    @app.template_filter('nl2br')
    def nl2br_filter(s):
        if s is None:
            return ''
        from markupsafe import Markup
        texto = str(s)
        texto = (texto.replace('&', '&amp;')
                      .replace('<', '&lt;')
                      .replace('>', '&gt;')
                      .replace('"', '&quot;')
                      .replace("'", '&#39;'))
        return Markup(texto.replace('\n', '<br>'))

    _pendientes_cache = {'count': 0, 'ts': 0}

    @app.context_processor
    def inject_globals():
        import time
        now = time.time()
        if now - _pendientes_cache['ts'] > 30:
            from app.models.reserva import Reserva
            try:
                _pendientes_cache['count'] = Reserva.query.filter_by(tipo='solicitud', estado='pendiente', leido=False).count()
            except:
                _pendientes_cache['count'] = 0
            _pendientes_cache['ts'] = now
        return dict(solicitudes_pendientes=_pendientes_cache['count'])

    with app.app_context():
        db.create_all()

        from app.models.reserva import Reserva
        import secrets as _secrets
        try:
            reservas_sin_token = Reserva.query.filter(Reserva.consulta_token.is_(None)).all()
            for r in reservas_sin_token:
                r.consulta_token = _secrets.token_urlsafe(32)
            if reservas_sin_token:
                db.session.commit()
        except Exception:
            db.session.rollback()
        
        from sqlalchemy import event
        from app.utils.mongo_sync import sync_insert, sync_update, sync_delete
        
        MODELS_TO_SYNC = ['servicios', 'reservas', 'clientes', 'usuarios', 'proveedores', 
                          'promociones', 'notificaciones', 'transacciones', 'viajes_planificados',
                          'recomendaciones_viaje', 'disponibilidad', 'resenas', 'tour_proveedores']
        
        def _get_tablename(mapper, instance):
            return instance.__tablename__
        
        def _after_insert(mapper, connection, instance):
            if _get_tablename(mapper, instance) in MODELS_TO_SYNC:
                sync_insert(instance)
        
        def _after_update(mapper, connection, instance):
            if _get_tablename(mapper, instance) in MODELS_TO_SYNC:
                sync_update(instance)
        
        def _after_delete(mapper, connection, instance):
            if _get_tablename(mapper, instance) in MODELS_TO_SYNC:
                sync_delete(instance)
        
        from app.models.servicio import Servicio
        from app.models.reserva import Reserva
        from app.models.cliente import Cliente
        from app.models.usuario import Usuario
        from app.models.proveedor import Proveedor
        from app.models.promocion import Promocion
        from app.models.notificacion import Notificacion
        from app.models.transaccion import Transaccion
        from app.models.viaje_planificado import ViajePlanificado
        from app.models.recomendacion_viaje import RecomendacionViaje
        from app.models.proveedor import TourProveedor
        
        for Model in [Servicio, Reserva, Cliente, Usuario, Proveedor, Promocion, 
                      Notificacion, Transaccion, ViajePlanificado, RecomendacionViaje, TourProveedor]:
            event.listen(Model, 'after_insert', _after_insert)
            event.listen(Model, 'after_update', _after_update)
            event.listen(Model, 'after_delete', _after_delete)
        
        from app.models.usuario import Usuario
        import secrets as _secrets
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin_password = os.environ.get('ADMIN_INITIAL_PASSWORD') or _secrets.token_urlsafe(12)
            admin = Usuario(
                username='admin',
                email='admin@turismo.com',
                nombre_completo='Administrador',
                rol='admin',
                activo=True
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print('=' * 60)
            print('¡IMPORTANTE! Usuario admin creado. Guarda esta contraseña (solo se muestra una vez):')
            print(f'  Usuario: admin@turismo.com')
            print(f'  Contraseña: {admin_password}')
            print('=' * 60)

    def _auto_complete_scheduler():
        """Ejecuta la verificación de solicitudes completadas cada hora"""
        import time
        while True:
            time.sleep(3600)
            with app.app_context():
                try:
                    from app.utils.auto_complete import completar_solicitudes_vencidas
                    completar_solicitudes_vencidas()
                except Exception as e:
                    logging.getLogger(__name__).error(f'Error en auto-complete scheduler: {e}')

    scheduler_thread = threading.Thread(target=_auto_complete_scheduler, daemon=True)
    scheduler_thread.start()

    with app.app_context():
        from app.utils.auto_complete import completar_solicitudes_vencidas
        completar_solicitudes_vencidas()

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net cdnjs.cloudflare.com; img-src 'self' data: http: https:; font-src 'self' cdnjs.cloudflare.com cdn.jsdelivr.net;"

        path = request.path
        rutas_sensibles = ['/px/', '/cx/', '/mr', '/cr/',
                           '/auth/lx', '/auth/rx', '/auth/rp', '/auth/vc', '/auth/np',
                           '/reserva/', '/consultar/', '/pp',
                           '/solicitudes/pagar/', '/solicitudes/confirmar-pago/']
        if any(path.startswith(r) for r in rutas_sensibles):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
        else:
            response.headers['Cache-Control'] = 'private, max-age=300'

        return response

    return app

from app.models import usuario