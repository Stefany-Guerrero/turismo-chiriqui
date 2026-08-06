from app import db
from datetime import datetime
from app.utils import panama_now

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=panama_now)
    
    usuario = db.relationship('Usuario', back_populates='cliente')
    reservas = db.relationship('Reserva', back_populates='cliente')
    viajes_planificados = db.relationship('ViajePlanificado', back_populates='cliente')
    
    def __repr__(self):
        return f'<Cliente {self.nombre}>'