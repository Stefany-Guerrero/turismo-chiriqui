from app import db
from datetime import datetime
from app.utils import panama_now
import secrets

TRANSPORTE_MAP = {
    'vehiculo_propio': 'Vehículo propio',
    'autobus': 'Autobús',
    'transporte_empresa': 'Transporte del proveedor',
    'avion': 'Avión',
    'lancha': 'Lancha',
    'alquiler_auto': 'Alquiler de auto',
    'no_requiere': 'No requiere transporte'
}

ALIMENTACION_MAP = {
    'desayuno': 'Desayuno',
    'media_pension': 'Media pensión',
    'todo_incluido': 'Todo incluido',
    'sin_alimentacion': 'Sin alimentación'
}

ALOJAMIENTO_MAP = {
    'hotel': 'Hotel',
    'hostal': 'Hostal',
    'cabana': 'Cabaña',
    'airbnb': 'Airbnb',
    'resort': 'Resort',
    'camping': 'Camping'
}

CATEGORIA_ALOJAMIENTO_MAP = {
    'economico': 'Económico',
    '3_estrellas': '3★',
    '4_estrellas': '4★',
    '5_estrellas': '5★',
    'lujo': 'Lujo'
}

def transporte_label(valor):
    return TRANSPORTE_MAP.get(valor, valor.replace('_', ' ').title() if valor else 'No especificado')

def alimentacion_label(valor):
    return ALIMENTACION_MAP.get(valor, 'No especificado')

def alojamiento_label(valor):
    return ALOJAMIENTO_MAP.get(valor, valor.replace('_', ' ').title() if valor else 'No especificado')

class Reserva(db.Model):
    __tablename__ = 'reservas'

    __table_args__ = (
        db.Index('ix_reservas_servicio_estado', 'servicio_id', 'estado'),
        db.Index('ix_reservas_cliente_tipo', 'cliente_id', 'tipo'),
        db.Index('ix_reservas_estado_leido', 'estado', 'leido'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), default='reserva')
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=True)

    fecha_gira = db.Column(db.DateTime, nullable=True)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    fecha_solicitada = db.Column(db.DateTime, nullable=True)
    numero_personas = db.Column(db.Integer, default=1)
    total_pago = db.Column(db.Float, default=0.0)
    estado = db.Column(db.String(20), default='pendiente')
    observaciones = db.Column(db.Text)

    presupuesto_estimado = db.Column(db.Float, nullable=True)
    presupuesto_tipo = db.Column(db.String(20), nullable=True)
    destino_preferido = db.Column(db.String(200), nullable=True)
    lugar_recogida = db.Column(db.String(200), nullable=True)
    lugares_visitar = db.Column(db.Text, nullable=True)
    tipo_alojamiento = db.Column(db.String(50), nullable=True)
    categoria_alojamiento = db.Column(db.String(50), nullable=True)
    transporte = db.Column(db.String(100))
    hospedaje = db.Column(db.Boolean, default=False)
    alimentacion = db.Column(db.String(50), nullable=True)
    guia = db.Column(db.Boolean, default=False)
    contacto_preferido = db.Column(db.String(20), nullable=True)
    provincia_cliente = db.Column(db.String(100), nullable=True)
    archivo_adjunto = db.Column(db.String(200), nullable=True)
    cotizacion = db.Column(db.Float, nullable=True)

    promocion_id = db.Column(db.Integer, db.ForeignKey('promociones.id'), nullable=True)
    descuento_aplicado = db.Column(db.Float, default=0)

    metodo_pago = db.Column(db.String(20), nullable=True)
    tipo_tarjeta = db.Column(db.String(20), nullable=True)
    titular_tarjeta = db.Column(db.String(200), nullable=True)
    ultimos_digitos = db.Column(db.String(4), nullable=True)
    codigo_transaccion = db.Column(db.String(30), unique=True, nullable=True)
    subtotal = db.Column(db.Float, default=0.0)
    itbms = db.Column(db.Float, default=0.0)
    comprobante_pago = db.Column(db.String(200), nullable=True)
    datos_transaccion = db.Column(db.Text, nullable=True)

    motivo_rechazo = db.Column(db.Text, nullable=True)

    consulta_token = db.Column(db.String(64), unique=True, nullable=True, index=True,
                               default=lambda: secrets.token_urlsafe(32))

    leido = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=panama_now)

    cliente = db.relationship('Cliente', back_populates='reservas')
    servicio = db.relationship('Servicio', back_populates='reservas')

    def generate_consulta_token(self):
        self.consulta_token = secrets.token_urlsafe(32)
        return self.consulta_token

    def transporte_nombre(self):
        return transporte_label(self.transporte)

    def alimentacion_nombre(self):
        return alimentacion_label(self.alimentacion)

    def alojamiento_nombre(self):
        return alojamiento_label(self.tipo_alojamiento)

    def categoria_alojamiento_nombre(self):
        return CATEGORIA_ALOJAMIENTO_MAP.get(self.categoria_alojamiento, 'Sin preferencia')

    def duracion_dias(self):
        if self.fecha_gira and self.fecha_fin:
            return (self.fecha_fin - self.fecha_gira).days
        return 0

    def duracion_texto(self):
        dias = self.duracion_dias()
        if dias > 0:
            return f'{dias} días / {dias - 1} noches'
        return '—'

    def cotizacion_visible(self):
        return self.estado in ('cotizada', 'aprobada', 'en_proceso')

    def get_suggested_services(self, limit=8):
        from app.models.servicio import Servicio
        servicios = Servicio.query.filter_by(activo=True).all()
        scored = []
        for s in servicios:
            score = s.calcular_score_solicitud(self)
            if score > 0:
                scored.append((score, s))
        scored.sort(key=lambda x: -x[0])
        return scored[:limit]

    def __repr__(self):
        return f'<Reserva {self.id}>'
