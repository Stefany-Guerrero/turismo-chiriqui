from app import db
from app.utils import panama_now


class AuditoriaLog(db.Model):
    __tablename__ = 'auditoria_logs'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=True)
    usuario_nombre = db.Column(db.String(100), nullable=True)
    accion = db.Column(db.String(100), nullable=False)
    entidad = db.Column(db.String(100), nullable=True)
    entidad_id = db.Column(db.Integer, nullable=True)
    detalle = db.Column(db.String(500), nullable=True)
    ip = db.Column(db.String(50), nullable=True)
    fecha = db.Column(db.DateTime, default=panama_now, nullable=False)

    def __repr__(self):
        return f'<AuditoriaLog {self.id} {self.accion}>'
