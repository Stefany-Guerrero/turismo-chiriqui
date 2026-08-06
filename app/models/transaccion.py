from app import db
from datetime import datetime
from app.utils import panama_now

class Transaccion(db.Model):
    __tablename__ = 'transacciones'
    
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(50))
    comprobante_url = db.Column(db.String(200))
    fecha_pago = db.Column(db.DateTime, default=panama_now)
    estado_pago = db.Column(db.String(20), default='pendiente')
    json_generado = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Transaccion {self.id} - {self.estado_pago}>'