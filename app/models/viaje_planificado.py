from app import db
from datetime import datetime
from app.utils import panama_now

class ViajePlanificado(db.Model):
    __tablename__ = 'viajes_planificados'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    numero_personas = db.Column(db.Integer, nullable=False)
    presupuesto = db.Column(db.Float)
    transporte_preferido = db.Column(db.String(50))
    experiencia_buscada = db.Column(db.String(50))
    requiere_hospedaje = db.Column(db.Boolean, default=False)
    requiere_alimentacion = db.Column(db.Boolean, default=False)
    requiere_guia = db.Column(db.Boolean, default=True)
    destino_preferido = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), default='planificando')
    fecha_creacion = db.Column(db.DateTime, default=panama_now)
    
    cliente = db.relationship('Cliente', back_populates='viajes_planificados')
    recomendaciones = db.relationship('RecomendacionViaje', back_populates='viaje')
    
    def get_dias_totales(self):
        return (self.fecha_fin - self.fecha_inicio).days
    
    def get_mejor_recomendacion(self):
        if self.recomendaciones:
            mejor = max(self.recomendaciones, key=lambda r: r.score)
            return mejor.servicio
        return None
    
    def __repr__(self):
        return f'<ViajePlanificado {self.id} - {self.cliente.nombre}>'