from app import db
from datetime import datetime
from app.utils import panama_now

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    mensaje = db.Column(db.Text, nullable=True)
    tipo = db.Column(db.String(50), default='info')
    referencia_id = db.Column(db.Integer, nullable=True)
    referencia_tipo = db.Column(db.String(50), nullable=True)
    leido = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=panama_now)

    usuario = db.relationship('Usuario', backref='notificaciones')

    def __repr__(self):
        return f'<Notificacion {self.id} - {self.titulo}>'
