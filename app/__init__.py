from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import os
import threading
import logging
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
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

    @app.context_processor
    def inject_globals():
        from app.models.reserva import Reserva
        try:
            pendientes = Reserva.query.filter_by(tipo='solicitud', estado='pendiente', leido=False).count()
        except:
            pendientes = 0
        return dict(solicitudes_pendientes=pendientes)

    with app.app_context():
        db.create_all()
        
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
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = Usuario(
                username='admin',
                email='admin@turismo.com',
                nombre_completo='Administrador',
                rol='admin',
                activo=True
            )
            admin.set_password('admin2026')
            db.session.add(admin)
            db.session.commit()
            print('Usuario admin creado: admin@turismo.com / admin2026')

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

    return app

from app.models import usuario