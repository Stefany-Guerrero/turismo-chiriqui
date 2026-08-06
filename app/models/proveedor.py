from app import db
from datetime import datetime
from app.utils import panama_now
import json

class TourProveedor(db.Model):
    __tablename__ = 'tour_proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    rol = db.Column(db.String(50), nullable=False)
    
    servicio = db.relationship('Servicio', back_populates='tour_proveedores_list')
    proveedor = db.relationship('Proveedor', back_populates='tours_asignados')
    
    ROLES = {
        'hospedaje': 'Hospedaje',
        'transporte': 'Transporte',
        'alimentacion': 'Alimentación',
        'guia': 'Guía turístico',
        'restaurante': 'Restaurante',
        'entretenimiento': 'Entretenimiento',
        'operador': 'Operador turístico'
    }
    
    ROLES_DESCRIPCION = {
        'hospedaje': 'Hotel, posada, finca o alojamiento donde se quedan los turistas',
        'transporte': 'Empresa o persona que provee el transporte terrestre/marítimo/aéreo',
        'alimentacion': 'Catering, almuerzos incluidos o servicio de comida general',
        'guia': 'Guía turístico que acompaña y educa durante el tour',
        'restaurante': 'Restaurante específico donde se come durante el tour',
        'entretenimiento': 'Actividades extra: canopy, pesca, tours acuáticos, etc.',
        'operador': 'Operador que organiza y coordina todo el tour'
    }
    
    __table_args__ = (
        db.UniqueConstraint('servicio_id', 'proveedor_id', 'rol', name='uix_servicio_proveedor_rol'),
    )
    
    def __repr__(self):
        return f'<TourProveedor {self.proveedor.nombre} - {self.rol}>'

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=True)
    provincia = db.Column(db.String(100), nullable=True)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    especificaciones = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=panama_now)
    
    servicios = db.relationship('Servicio', back_populates='proveedor')
    tours_asignados = db.relationship('TourProveedor', back_populates='proveedor')
    
    def get_especificaciones(self):
        if not self.especificaciones:
            return {}
        try:
            return json.loads(self.especificaciones)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_especificaciones(self, data):
        self.especificaciones = json.dumps(data) if data else None
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'