from app import db
from datetime import datetime
from app.utils import panama_now

class RecomendacionViaje(db.Model):
    __tablename__ = 'recomendaciones_viaje'
    
    id = db.Column(db.Integer, primary_key=True)
    viaje_planificado_id = db.Column(db.Integer, db.ForeignKey('viajes_planificados.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    creado_en = db.Column(db.DateTime, default=panama_now)
    
    viaje = db.relationship('ViajePlanificado', back_populates='recomendaciones')
    servicio = db.relationship('Servicio', backref='recomendaciones_list', lazy=True)
    
    def __repr__(self):
        return f'<RecomendacionViaje {self.id} - Score: {self.score}>'