from app import db
from datetime import datetime
from app.utils import panama_now

class Promocion(db.Model):
    __tablename__ = 'promociones'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='porcentaje')
    valor = db.Column(db.Float, nullable=False, default=0)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    activa = db.Column(db.Boolean, default=True)
    uso_maximo = db.Column(db.Integer, default=0)
    usos_actuales = db.Column(db.Integer, default=0)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=True)
    imagen = db.Column(db.String(200))
    fecha_creacion = db.Column(db.DateTime, default=panama_now)
    
    servicio = db.relationship('Servicio', back_populates='promociones')
    
    def calcular_descuento(self, precio):
        if self.tipo == 'porcentaje':
            return precio * (self.valor / 100)
        else:
            return self.valor
    
    def esta_vigente(self):
        hoy = datetime.now().date()
        return self.activa and self.fecha_inicio <= hoy <= self.fecha_fin
    
    def __repr__(self):
        return f'<Promocion {self.codigo} - {self.nombre}>'