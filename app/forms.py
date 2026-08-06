from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, TextAreaField, IntegerField, FloatField, SelectField, DateField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from app.models.usuario import Usuario

def validar_presupuesto(form, field):
    if field.data is not None:
        if field.data < 0:
            raise ValidationError(f'El presupuesto no puede ser negativo (ingresaste B/. {field.data:,.2f}).')
        if field.data > 100000:
            raise ValidationError(f'El presupuesto máximo es B/. 100,000.00 — ingresaste B/. {field.data:,.2f}, una cantidad demasiado elevada.')

class LoginForm(FlaskForm):
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    nombre_completo = StringField('Nombre Completo', validators=[DataRequired(), Length(min=3, max=100)])
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=50)])
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Crear Cuenta')
    
    def validate_username(self, username):
        usuario = Usuario.query.filter_by(username=username.data).first()
        if usuario:
            raise ValidationError('Este nombre de usuario ya está registrado.')
    
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este correo electrónico ya está registrado.')

class ResetPasswordForm(FlaskForm):
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar Código de Recuperación')

class VerifyCodeForm(FlaskForm):
    codigo = StringField('Código de Verificación', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verificar Código')

class NewPasswordForm(FlaskForm):
    new_password = PasswordField('Nueva Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Cambiar Contraseña')

EXPERIENCIAS = [
    ('', 'Selecciona una opción'),
    ('playa', 'Playa'),
    ('montana', 'Montaña'),
    ('ecoturismo', 'Ecoturismo'),
    ('aventura', 'Aventura'),
    ('cultural', 'Cultural'),
    ('gastronomica', 'Gastronómica'),
    ('islas', 'Islas'),
    ('historico', 'Histórico')
]

PROVINCIAS = [
    ('', 'Seleccione una provincia'),
    ('Bocas del Toro', 'Bocas del Toro'),
    ('Coclé', 'Coclé'),
    ('Colón', 'Colón'),
    ('Chiriquí', 'Chiriquí'),
    ('Darién', 'Darién'),
    ('Herrera', 'Herrera'),
    ('Los Santos', 'Los Santos'),
    ('Panamá', 'Panamá'),
    ('Panamá Oeste', 'Panamá Oeste'),
    ('Veraguas', 'Veraguas')
]

DISTRITOS_POR_PROVINCIA = {
    'Bocas del Toro': ['Almirante', 'Bocas del Toro', 'Changuinola', 'Chiriquí Grande'],
    'Coclé': ['Aguadulce', 'Antón', 'La Pintada', 'Natá', 'Olá', 'Penonomé'],
    'Colón': ['Colón', 'Chagres', 'Donoso', 'Portobelo', 'Santa Isabel'],
    'Chiriquí': ['Alanje', 'Barú', 'Boquerón', 'Boquete', 'Bugaba', 'David', 'Dolega', 'Guayabal', 'Remedios', 'Renacimiento', 'San Félix', 'San Lorenzo', 'Tierras Altas', 'Tolé'],
    'Darién': ['Chepigana', 'Pinogana', 'Santa Fe'],
    'Herrera': ['Chitré', 'Las Minas', 'Los Pozos', 'Ocú', 'Parita', 'Pesé', 'Santa María'],
    'Los Santos': ['Guararé', 'Las Tablas', 'Los Santos', 'Macaracas', 'Pedasí', 'Pocrí', 'Tonosí'],
    'Panamá': ['Balboa', 'Chepo', 'Chimán', 'Panamá', 'San Miguelito', 'Taboga'],
    'Panamá Oeste': ['Arraiján', 'Capira', 'Chame', 'La Chorrera', 'San Carlos'],
    'Veraguas': ['Atalaya', 'Calobre', 'Cañazas', 'La Mesa', 'Las Palmas', 'Mariato', 'Montijo', 'Río de Jesús', 'San Francisco', 'Santa Fe', 'Santiago', 'Soná']
}

DESTINOS_POR_PROVINCIA = {
    'Bocas del Toro': ['Bocas del Toro', 'Isla Colón', 'Isla Carenero', 'Isla Bastimentos'],
    'Coclé': ['Penonomé', 'Aguadulce', 'Antón', 'Natá'],
    'Colón': ['Colón', 'Portobelo', 'Santa Isabel'],
    'Chiriquí': ['Volcán Barú', 'Boquete', 'David', 'Golfo de Chiriquí', 'Parque Nacional La Amistad'],
    'Darién': ['Yaviza', 'Pucuro', 'Parque Nacional Darién'],
    'Herrera': ['Chitré', 'Ocú', 'Parita'],
    'Los Santos': ['Las Tablas', 'Pedasí', 'Guararé'],
    'Panamá': ['Ciudad de Panamá', 'Casco Antiguo', 'Panamá Viejo', 'Taboga'],
    'Panamá Oeste': ['La Chorrera', 'Arraiján', 'San Carlos', 'Chame'],
    'Veraguas': ['Santiago', 'Santa Fe', 'Montijo', 'Mariato']
}

class ServicioForm(FlaskForm):
    codigo = StringField('Código del Tour', validators=[Length(max=20)])
    nombre = StringField('Nombre del Tour', validators=[DataRequired(), Length(max=100)])
    tipo_experiencia = SelectField('Categoría / Experiencia', choices=EXPERIENCIAS, validators=[DataRequired()])
    provincia = SelectField('Provincia', choices=PROVINCIAS, validators=[DataRequired()])
    distrito = SelectField('Distrito', choices=[], validators=[DataRequired()], validate_choice=False)
    destino = SelectField('Destino', choices=[], validators=[DataRequired()], validate_choice=False)
    punto_salida = StringField('Punto de Salida', validators=[DataRequired(), Length(max=100)])
    punto_llegada = StringField('Punto de Llegada', validators=[Length(max=100)])
    
    descripcion = TextAreaField('Descripción', validators=[DataRequired(), Length(max=500)])
    
    duracion_cantidad = IntegerField('Cantidad', default=1, validators=[DataRequired()])
    duracion_unidad = SelectField('Unidad', choices=[
        ('horas', 'Horas'),
        ('dias', 'Días')
    ], default='horas', validators=[DataRequired()])
    
    def validate_duracion_cantidad(self, field):
        unidad = self.duracion_unidad.data
        valor = field.data
        
        if valor is None:
            raise ValidationError('La cantidad es requerida')
        
        if unidad == 'horas' and (valor < 1 or valor > 23):
            raise ValidationError('Para horas, la cantidad debe estar entre 1 y 23')
        
        if unidad == 'dias' and (valor < 1 or valor > 15):
            raise ValidationError('Para días, la cantidad debe estar entre 1 y 15')
    
    hora_inicio = StringField('Hora de Inicio', validators=[DataRequired(), Length(max=10)])
    hora_estimada_regreso = StringField('Hora Estimada de Regreso', validators=[DataRequired(), Length(max=10)])
    
    precio = FloatField('Precio por Persona (B/.)', validators=[DataRequired(), NumberRange(min=0.01)])
    cupo_maximo = IntegerField('Cupo Máximo', default=10, validators=[DataRequired(), NumberRange(min=1)])
    
    imagen = StringField('URL de la Imagen', validators=[DataRequired(), Length(max=200)])
    itinerario = TextAreaField('Itinerario', validators=[DataRequired()])
    incluye = TextAreaField('Servicios Incluidos', validators=[DataRequired()])
    no_incluye = TextAreaField('Qué NO Incluye', validators=[DataRequired()])
    recomendaciones = TextAreaField('Recomendaciones', validators=[DataRequired()])
    
    incluye_transporte = BooleanField('Transporte')
    incluye_alimentacion = BooleanField('Alimentación')
    incluye_hospedaje = BooleanField('Hospedaje')
    incluye_guia = BooleanField('Guía Turístico')
    incluye_seguro = BooleanField('Seguro')
    incluye_entradas = BooleanField('Entradas')
    incluye_equipo = BooleanField('Equipo')
    
    proveedor_id = SelectField('Proveedor', coerce=int, choices=[], validators=[DataRequired()])
    activo = BooleanField('Activo', default=True)
    
    transporte = SelectMultipleField('Transporte disponible para llegar', choices=[
        ('vehiculo_propio', 'Vehículo propio'),
        ('autobus', 'Autobús'),
        ('transporte_empresa', 'Transporte de la empresa'),
        ('avion', 'Avión'),
        ('lancha', 'Lancha')
    ], validators=[Optional()], default=[])
    
    duracion_recomendada = SelectField('Duración recomendada', choices=[
        ('', 'Selecciona una opción'),
        ('medio_dia', 'Medio día'),
        ('1_dia', '1 día'),
        ('2_3_dias', '2-3 días'),
        ('mas_3_dias', 'Más de 3 días')
    ])

    tipo_programacion = SelectField('Tipo de Programación', choices=[
        ('fecha_unica', 'Fecha única'),
        ('recurrente', 'Recurrente (semanal)')
    ], default='recurrente', validators=[DataRequired()])
    
    fecha_unica = DateField('Fecha única', format='%Y-%m-%d', validators=[Optional()])
    
    vigencia_inicio = DateField('Vigencia - Desde', format='%Y-%m-%d', validators=[Optional()])
    vigencia_fin = DateField('Vigencia - Hasta', format='%Y-%m-%d', validators=[Optional()])
    
    dias_operacion = SelectMultipleField('Días de operación', choices=[
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo')
    ], validators=[Optional()], coerce=int, default=[])
    
    def process_formdata(self, valuelist):
        if valuelist is None or not valuelist:
            self.data = []
            return
        try:
            self.data = [int(x) for x in valuelist if x is not None and str(x).strip().isdigit()]
        except (ValueError, TypeError):
            self.data = []
    
    submit = SubmitField('Guardar Tour')
    
    def generate_codigo(self):
        import secrets
        return f'TOUR-{secrets.token_hex(4).upper()}'
    
    def set_dias_operacion_from_string(self, dias_string):
        if dias_string and isinstance(dias_string, str):
            self.dias_operacion.data = [int(d) for d in dias_string.split(',') if d.isdigit()]
        else:
            self.dias_operacion.data = []
    
    def get_dias_operacion_as_string(self):
        if self.dias_operacion.data and isinstance(self.dias_operacion.data, list):
            return ','.join(str(d) for d in self.dias_operacion.data)
        return ''
    
    def set_transporte_from_string(self, transporte_string):
        if transporte_string and isinstance(transporte_string, str):
            self.transporte.data = [t.strip() for t in transporte_string.split(',') if t.strip()]
        else:
            self.transporte.data = []
    
    def get_transporte_as_string(self):
        if self.transporte.data and isinstance(self.transporte.data, list):
            return ','.join(self.transporte.data)
        return ''

class ReservaForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    servicio_id = SelectField('Tour', coerce=int, validators=[DataRequired()])
    fecha_gira = DateField('Fecha de la Gira', validators=[DataRequired()])
    numero_personas = IntegerField('Número de Personas', validators=[DataRequired()])
    total_pago = FloatField('Total a Pagar', validators=[DataRequired()])
    observaciones = TextAreaField('Observaciones')
    submit = SubmitField('Guardar Reserva')

class PromocionForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=100)])
    descripcion = TextAreaField('Descripción', validators=[DataRequired(), Length(min=10)])
    codigo = StringField('Código', validators=[DataRequired(), Length(min=3, max=50)])
    tipo = SelectField('Tipo', choices=[('porcentaje', 'Porcentaje'), ('monto_fijo', 'Monto Fijo')], validators=[DataRequired()])
    valor = FloatField('Valor', validators=[DataRequired(), NumberRange(min=0.01)])
    fecha_inicio = DateField('Fecha Inicio', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_fin = DateField('Fecha Fin', format='%Y-%m-%d', validators=[DataRequired()])
    activa = BooleanField('Activa', default=True)
    uso_maximo = IntegerField('Uso Máximo', default=0)
    servicio_id = SelectField('Servicio', coerce=int, choices=[], validators=[DataRequired()])
    imagen = StringField('URL de la Imagen', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Guardar')
    
    def validate_codigo(self, field):
        if ' ' in field.data:
            raise ValidationError('El código no debe contener espacios')
        if not field.data.replace('-', '').isalnum():
            raise ValidationError('Solo letras, números y guiones')
    
    def validate_fecha_fin(self, field):
        if self.fecha_inicio.data and field.data and field.data < self.fecha_inicio.data:
            raise ValidationError('La fecha fin debe ser posterior a la fecha inicio')

class AsistenteViajeForm(FlaskForm):
    transporte = SelectField('¿Cómo deseas viajar?', choices=[
        ('', 'Selecciona una opción'),
        ('vehiculo_propio', 'Vehículo propio'),
        ('autobus', 'Autobús'),
        ('transporte_empresa', 'Transporte de la empresa'),
        ('avion', 'Avión'),
        ('lancha', 'Lancha')
    ], validators=[DataRequired()])
    
    experiencia = SelectField('¿Qué tipo de experiencia buscas?', choices=EXPERIENCIAS, validators=[DataRequired()])
    
    duracion = SelectField('¿Cuántos días tienes disponibles?', choices=[
        ('', 'Selecciona una opción'),
        ('medio_dia', 'Medio día'),
        ('1_dia', '1 día'),
        ('2_3_dias', '2-3 días'),
        ('mas_3_dias', 'Más de 3 días')
    ], validators=[DataRequired()])
    
    presupuesto = SelectField('¿Cuál es tu presupuesto?', choices=[
        ('', 'Selecciona una opción'),
        ('hasta_50', 'Hasta B/.50'),
        ('50_100', 'B/.50 - B/.100'),
        ('100_250', 'B/.100 - B/.250'),
        ('mas_250', 'Más de B/.250')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Buscar experiencias')

class SolicitudForm(FlaskForm):
    fecha_inicio = DateField('Fecha de llegada', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_fin = DateField('Fecha de salida', format='%Y-%m-%d', validators=[Optional()])
    numero_personas = IntegerField('Número de personas', validators=[DataRequired(), NumberRange(min=1, max=50)])
    
    lugar_recogida = StringField('Lugar de recogida', validators=[Optional(), Length(max=200)],
        render_kw={"placeholder": "Ej: Hotel Continental, Aeropuerto, Casa particular..."} )
    lugares_visitar = TextAreaField('Lugares que desea visitar', validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "Ej: Volcán Barú, Los Cangilones, Finca Lérida, Playa Las Lajas..."})
    
    presupuesto_estimado = FloatField('Presupuesto estimado (B/.)', validators=[Optional(), validar_presupuesto])
    presupuesto_tipo = SelectField('Tipo de presupuesto', choices=[
        ('', 'Selecciona'),
        ('total', 'Presupuesto total'),
        ('por_persona', 'Por persona')
    ])
    
    destino_preferido = StringField('Destino preferido', validators=[Optional(), Length(max=200)])
    tipo_alojamiento = SelectField('Tipo de alojamiento', choices=[
        ('', 'Sin preferencia'),
        ('hotel', 'Hotel'),
        ('hostal', 'Hostal'),
        ('cabana', 'Cabaña'),
        ('airbnb', 'Airbnb'),
        ('resort', 'Resort'),
        ('camping', 'Camping')
    ])
    
    transporte = SelectField('Transporte', choices=[
        ('', 'Selecciona'),
        ('transporte_empresa', 'Transporte del proveedor'),
        ('vehiculo_propio', 'Vehículo propio'),
        ('alquiler_auto', 'Alquiler de auto'),
        ('autobus', 'Autobús'),
        ('avion', 'Avión'),
        ('lancha', 'Lancha'),
        ('no_requiere', 'No requiere transporte')
    ], validators=[DataRequired()])
    
    alimentacion = SelectField('Régimen de alimentación', choices=[
        ('', 'Sin preferencia'),
        ('desayuno', 'Desayuno'),
        ('media_pension', 'Media pensión (desayuno + almuerzo/cena)'),
        ('todo_incluido', 'Todo incluido'),
        ('sin_alimentacion', 'Sin alimentación')
    ])
    
    hospedaje = BooleanField('Necesito hospedaje')
    guia = BooleanField('Necesito guía turístico')
    
    telefono = StringField('Teléfono (opcional)', validators=[Optional(), Length(max=20)],
        render_kw={"placeholder": "Ej: +507 6000-0000"})
    
    observaciones = TextAreaField('Observaciones adicionales', validators=[Length(max=500)],
        render_kw={"placeholder": "Describe qué tipo de experiencia te gustaría vivir, requisitos especiales, etc..."})
    
    submit = SubmitField('Enviar solicitud')

    def validate_fecha_inicio(self, field):
        from datetime import date
        if field.data and field.data < date.today():
            raise ValidationError('La fecha de llegada no puede ser en el pasado.')

    def validate_fecha_fin(self, field):
        if self.fecha_inicio.data and field.data and field.data < self.fecha_inicio.data:
            raise ValidationError('La fecha de salida debe ser posterior a la de llegada.')

    def validate_numero_personas(self, field):
        if field.data and field.data < 1:
            raise ValidationError('Debe haber al menos 1 persona.')
        if field.data and field.data > 50:
            raise ValidationError('El máximo de personas es 50.')

class PlanificadorForm(FlaskForm):
    fecha_inicio = DateField('Fecha de inicio del viaje', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_fin = DateField('Fecha de fin del viaje', format='%Y-%m-%d', validators=[DataRequired()])
    numero_personas = IntegerField('Número de personas', validators=[DataRequired(), NumberRange(min=1, max=50)])
    presupuesto = FloatField('Presupuesto total (B/.)', validators=[Optional(), NumberRange(min=0)])
    
    destino = SelectField('Destino preferido', choices=[], validators=[Optional()])
    
    transporte = SelectField('Transporte preferido', choices=[
        ('', 'Selecciona una opción'),
        ('vehiculo_propio', 'Vehículo propio'),
        ('autobus', 'Autobús'),
        ('transporte_empresa', 'Transporte de la empresa'),
        ('avion', 'Avión'),
        ('lancha', 'Lancha')
    ])
    
    experiencia = SelectField('Tipo de experiencia', choices=EXPERIENCIAS, validators=[DataRequired()])
    
    requiere_hospedaje = BooleanField('Necesito hospedaje')
    requiere_alimentacion = BooleanField('Necesito alimentación incluida')
    requiere_guia = BooleanField('Necesito guía turístico')
    
    observaciones = TextAreaField('Observaciones adicionales')
    submit = SubmitField('Planificar mi viaje')
    
    def validate_fecha_fin(self, field):
        if self.fecha_inicio.data and field.data and field.data < self.fecha_inicio.data:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio')
        if self.fecha_inicio.data and field.data:
            dias = (field.data - self.fecha_inicio.data).days
            if dias < 0:
                raise ValidationError('El viaje debe durar al menos 1 día')
            if dias > 30:
                raise ValidationError('El viaje no puede durar más de 30 días')

TIPOS_PROVEEDOR = [
    ('', 'Seleccione un tipo'),
    ('hotel', 'Hotel / Alojamiento'),
    ('transporte', 'Transporte'),
    ('transporte_maritimo', 'Transporte marítimo'),
    ('guia', 'Guía turístico'),
    ('restaurante', 'Restaurante / Alimentación'),
    ('operador', 'Operador turístico'),
    ('atraccion', 'Atracción turística / Entradas'),
    ('equipo', 'Alquiler de equipo'),
    ('seguros', 'Seguros'),
    ('otro', 'Otro')
]

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=100)])
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    activo = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar')

class ProveedorForm(FlaskForm):
    nombre = StringField('Nombre del proveedor', validators=[DataRequired(), Length(max=100)])
    tipo = SelectField('Tipo de proveedor', choices=TIPOS_PROVEEDOR, validators=[DataRequired()])
    provincia = SelectField('Provincia', choices=PROVINCIAS, validators=[DataRequired()])
    contacto = StringField('Persona de contacto', validators=[Length(max=100)])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    email = EmailField('Correo electrónico', validators=[Length(max=100)])
    direccion = StringField('Dirección', validators=[Length(max=200)])
    especificaciones_json = TextAreaField('Especificaciones', validators=[Optional()])
    activo = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar')