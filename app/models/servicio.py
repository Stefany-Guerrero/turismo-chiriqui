from app import db
from datetime import datetime
from sqlalchemy import and_, or_, func, not_
import secrets
import string
from app.utils import panama_now

class Servicio(db.Model):
    __tablename__ = 'servicios'
    
    CATEGORIAS_DISPLAY = {
        'playa': 'Playa',
        'montana': 'Montaña',
        'ecoturismo': 'Ecoturismo',
        'aventura': 'Aventura',
        'cultural': 'Cultural',
        'gastronomica': 'Gastronómica',
        'islas': 'Islas',
        'historico': 'Histórico'
    }
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=True)
    provincia = db.Column(db.String(100), nullable=True)
    distrito = db.Column(db.String(100), nullable=True)
    destino = db.Column(db.String(100), nullable=True)
    punto_salida = db.Column(db.String(100), nullable=True)
    punto_llegada = db.Column(db.String(100), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    duracion_cantidad = db.Column(db.Integer, default=1)
    duracion_unidad = db.Column(db.String(10), default='horas')
    hora_inicio = db.Column(db.String(10), nullable=True)
    hora_estimada_regreso = db.Column(db.String(10), nullable=True)
    precio = db.Column(db.Float, nullable=False)
    cupo_maximo = db.Column(db.Integer, default=10)
    cupos_disponibles = db.Column(db.Integer, default=0)
    imagen = db.Column(db.String(200), nullable=True)
    itinerario = db.Column(db.Text, nullable=True)
    incluye = db.Column(db.Text, nullable=True)
    no_incluye = db.Column(db.Text, nullable=True)
    recomendaciones = db.Column(db.Text, nullable=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=True)
    incluye_transporte = db.Column(db.Boolean, default=False)
    incluye_alimentacion = db.Column(db.Boolean, default=False)
    incluye_hospedaje = db.Column(db.Boolean, default=False)
    incluye_guia = db.Column(db.Boolean, default=False)
    incluye_seguro = db.Column(db.Boolean, default=False)
    incluye_entradas = db.Column(db.Boolean, default=False)
    incluye_equipo = db.Column(db.Boolean, default=False)
    transporte = db.Column(db.String(100), nullable=True)
    transporte_precios = db.Column(db.Text, nullable=True)
    tipo_experiencia = db.Column(db.String(100), nullable=True)
    duracion_recomendada = db.Column(db.String(50), nullable=True)
    
    tipo_programacion = db.Column(db.String(20), default='recurrente')
    dias_operacion = db.Column(db.String(50), nullable=True)
    fecha_unica = db.Column(db.Date, nullable=True)
    vigencia_inicio = db.Column(db.Date, nullable=True)
    vigencia_fin = db.Column(db.Date, nullable=True)
    hora_salida_tour = db.Column(db.String(10), nullable=True)
    hora_regreso_tour = db.Column(db.String(10), nullable=True)
    
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=panama_now)
    
    @property
    def categoria_nombre(self):
        key = self.tipo_experiencia or self.categoria
        return self.CATEGORIAS_DISPLAY.get(key, key or 'Sin categoría')
    
    def get_proveedores_por_rol(self, rol=None):
        from app.models.proveedor import TourProveedor
        query = TourProveedor.query.filter_by(servicio_id=self.id)
        if rol:
            query = query.filter_by(rol=rol)
        return query.all()
    
    def get_todos_los_proveedores(self):
        from app.models.proveedor import TourProveedor
        return TourProveedor.query.filter_by(servicio_id=self.id).all()
    
    def get_proveedor_rol_display(self):
        from app.models.proveedor import TourProveedor
        proveedores = TourProveedor.query.filter_by(servicio_id=self.id).all()
        return [(tp.proveedor, tp.rol, TourProveedor.ROLES.get(tp.rol, tp.rol)) for tp in proveedores]
    
    reservas = db.relationship('Reserva', back_populates='servicio')
    proveedor = db.relationship('Proveedor', back_populates='servicios')
    tour_proveedores_list = db.relationship('TourProveedor', back_populates='servicio', cascade='all, delete-orphan')
    disponibilidad = db.relationship('Disponibilidad', back_populates='servicio')
    promociones = db.relationship('Promocion', back_populates='servicio')
    
    def get_transportes_list(self):
        if not self.transporte:
            return []
        return [t.strip() for t in self.transporte.split(',') if t.strip()]

    def get_transporte_precios(self):
        if not self.transporte_precios:
            return {}
        try:
            import json
            return json.loads(self.transporte_precios)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_transporte_precios(self, precios_dict):
        import json
        self.transporte_precios = json.dumps(precios_dict) if precios_dict else None

    def get_precio_transporte(self, codigo):
        precios = self.get_transporte_precios()
        return float(precios.get(codigo, 0))

    def set_transportes(self, transportes):
        if isinstance(transportes, list):
            self.transporte = ','.join(t for t in transportes if t)
        else:
            self.transporte = transportes

    def calcular_score(self, preferencias):
        score = 0
        transportes_tour = self.get_transportes_list()
        if preferencias.get('transporte') in transportes_tour:
            score += 30
        if self.tipo_experiencia == preferencias.get('experiencia'):
            score += 25
        if self.duracion_recomendada == preferencias.get('duracion'):
            score += 20
        if self.precio <= preferencias.get('presupuesto', 999999):
            score += 20
        if preferencias.get('requiere_hospedaje') == self.incluye_hospedaje:
            score += 10
        if preferencias.get('requiere_alimentacion') == self.incluye_alimentacion:
            score += 10
        if preferencias.get('requiere_guia') == self.incluye_guia:
            score += 5
        return score

    def calcular_score_solicitud(self, solicitud):
        score = 0
        destino_s = (solicitud.destino_preferido or '').lower()
        destino_t = (self.destino or '').lower()
        if destino_s and destino_t and any(p in destino_t for p in destino_s.split()):
            score += 40
        elif destino_s and destino_t and any(p in destino_s for p in destino_t.split()):
            score += 35
        presupuesto = solicitud.presupuesto_estimado or 0
        precio_pp = float(self.precio) * solicitud.numero_personas
        if presupuesto > 0 and precio_pp <= presupuesto * 1.2:
            score += 20
        if self.tipo_experiencia and solicitud.destino_preferido:
            score += 15
        if solicitud.hospedaje and self.incluye_hospedaje:
            score += 10
        if solicitud.guia and self.incluye_guia:
            score += 10
        if solicitud.transporte:
            transportes_tour = self.get_transportes_list()
            if solicitud.transporte in transportes_tour:
                score += 5
        return score
    
    def get_promocion_activa(self):
        from app.models.promocion import Promocion
        hoy = datetime.now().date()
        promocion = Promocion.query.filter(
            Promocion.servicio_id == self.id,
            Promocion.activa == True,
            Promocion.fecha_inicio <= hoy,
            Promocion.fecha_fin >= hoy
        ).first()
        return promocion
    
    @classmethod
    def query_activos_sin_promocion(cls):
        from app.models.promocion import Promocion
        hoy = datetime.now().date()
        subq = db.session.query(Promocion.servicio_id).filter(
            Promocion.activa == True,
            Promocion.fecha_inicio <= hoy,
            Promocion.fecha_fin >= hoy
        ).subquery()
        return cls.query.filter(
            cls.activo == True,
            not_(cls.id.in_(db.session.query(subq.c.servicio_id)))
        )
    
    def get_dias_operacion_list(self):
        if not self.dias_operacion:
            return []
        return [int(d) for d in self.dias_operacion.split(',') if d.isdigit()]
    
    def esta_disponible(self, fecha):
        if self.tipo_programacion == 'fecha_unica':
            return fecha == self.fecha_unica
        elif self.tipo_programacion == 'recurrente':
            if self.vigencia_inicio and self.vigencia_fin:
                if fecha < self.vigencia_inicio or fecha > self.vigencia_fin:
                    return False
            dias = self.get_dias_operacion_list()
            if not dias:
                return True
            return fecha.weekday() in dias
        return True
    
    def get_cupos_disponibles_fecha(self, fecha):
        disp = Disponibilidad.query.filter_by(servicio_id=self.id, fecha=fecha).first()
        if disp:
            return disp.cupos_disponibles
        return self.cupo_maximo
    
    def generar_codigo(self):
        if not self.codigo:
            self.codigo = f'TOUR-{secrets.token_hex(4).upper()}'
        return self.codigo
    
    def get_precio_con_descuento(self):
        promocion = self.get_promocion_activa()
        precio_original = float(self.precio)
        
        if promocion:
            if promocion.tipo == 'porcentaje':
                descuento = precio_original * (promocion.valor / 100)
            else:
                descuento = float(promocion.valor)
            
            precio_final = max(0, precio_original - descuento)
            return {
                'precio_original': precio_original,
                'precio_final': round(precio_final, 2),
                'descuento': round(descuento, 2),
                'porcentaje': round((descuento / precio_original) * 100, 1) if precio_original > 0 else 0,
                'promocion': promocion
            }
        
        return {
            'precio_original': precio_original,
            'precio_final': precio_original,
            'descuento': 0,
            'porcentaje': 0,
            'promocion': None
        }
    
    def verificar_disponibilidad_completa(self, fecha, cantidad=1):
        if not self.activo:
            return False, "Este tour no está disponible actualmente", 0
        
        if not self.esta_disponible(fecha):
            if self.tipo_programacion == 'fecha_unica':
                return False, f"Este tour solo opera el {self.fecha_unica.strftime('%d/%m/%Y')}", 0
            else:
                dias_nombres = self.get_dias_operacion_nombres()
                if dias_nombres:
                    return False, f"Este tour opera los dias: {', '.join(dias_nombres)}", 0
                return False, "Este tour no opera en la fecha seleccionada", 0
        
        cupos = self.get_cupos_disponibles_fecha(fecha)
        if cupos < cantidad:
            return False, f"Solo hay {cupos} cupos disponibles", cupos
        
        return True, "Disponible", cupos
    
    def get_dias_operacion_nombres(self):
        dias_map = {
            0: 'Lunes', 1: 'Martes', 2: 'Miercoles',
            3: 'Jueves', 4: 'Viernes', 5: 'Sabado', 6: 'Domingo'
        }
        dias_list = self.get_dias_operacion_list()
        return [dias_map.get(d, '') for d in dias_list if d in dias_map]
    
    def get_calendario_mes(self, mes=None, año=None, disp_map=None):
        import calendar
        from datetime import date, timedelta
        
        if not mes or not año:
            hoy = datetime.now()
            mes = hoy.month
            año = hoy.year
        
        primer_dia = date(año, mes, 1)
        if mes == 12:
            ultimo_dia = date(año + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia = date(año, mes + 1, 1) - timedelta(days=1)
        
        calendario = []
        hoy = datetime.now().date()
        
        for dia in range(1, ultimo_dia.day + 1):
            fecha = date(año, mes, dia)
            
            disponible_flag = self.esta_disponible(fecha)
            if not disponible_flag:
                if self.tipo_programacion == 'fecha_unica':
                    mensaje = f"Este tour solo opera el {self.fecha_unica.strftime('%d/%m/%Y')}"
                else:
                    dias_nombres = self.get_dias_operacion_nombres()
                    mensaje = f"Este tour opera los dias: {', '.join(dias_nombres)}" if dias_nombres else "Este tour no opera en la fecha seleccionada"
                cupos = 0
            else:
                if disp_map is not None:
                    cupos = disp_map.get((self.id, fecha), self.cupo_maximo)
                else:
                    cupos = self.get_cupos_disponibles_fecha(fecha)
                mensaje = "Disponible" if cupos > 0 else "Sin cupos"
            
            calendario.append({
                'fecha': fecha,
                'dia': dia,
                'disponible': disponible_flag and cupos > 0,
                'cupos': cupos,
                'mensaje': mensaje,
                'es_pasado': fecha < hoy,
                'dia_semana': fecha.weekday(),
                'es_hoy': fecha == hoy
            })
        
        return {
            'mes': mes,
            'año': año,
            'nombre_mes': self._get_nombre_mes(mes),
            'dias': calendario,
            'primer_dia_semana': primer_dia.weekday(),
            'total_dias': ultimo_dia.day,
            'total_disponibles': sum(1 for d in calendario if d['disponible'] and not d['es_pasado'])
        }
    
    def _get_nombre_mes(self, mes):
        meses = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        return meses.get(mes, '')
    
    def reservar_cupos(self, fecha, cantidad=1):
        try:
            disponible, mensaje, cupos = self.verificar_disponibilidad_completa(fecha, cantidad)
            if not disponible:
                return False, mensaje
            
            disp = Disponibilidad.query.filter_by(servicio_id=self.id, fecha=fecha).first()
            if not disp:
                disp = Disponibilidad(
                    servicio_id=self.id,
                    fecha=fecha,
                    cupos_disponibles=self.cupo_maximo - cantidad
                )
                db.session.add(disp)
            else:
                disp.cupos_disponibles -= cantidad
            
            db.session.commit()
            return True, "Cupos reservados exitosamente"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error al reservar: {str(e)}"
    
    def get_estadisticas(self):
        from app.models.reserva import Reserva
        
        total_reservas = Reserva.query.filter_by(servicio_id=self.id).count()
        reservas_confirmadas = Reserva.query.filter_by(servicio_id=self.id, estado='confirmada').count()
        
        return {
            'total_reservas': total_reservas,
            'confirmadas': reservas_confirmadas,
            'calificacion_promedio': self.get_calificacion_promedio(),
            'total_resenas': self.get_total_resenas(),
            'tiene_promocion': self.get_promocion_activa() is not None,
            'dias_operacion': self.get_dias_operacion_nombres()
        }
    
    def get_calificacion_promedio(self):
        promedio = db.session.query(func.avg(Resena.calificacion)).filter_by(servicio_id=self.id).scalar()
        return round(promedio, 1) if promedio else 0
    
    def get_total_resenas(self):
        return Resena.query.filter_by(servicio_id=self.id).count()
    
    def to_dict(self, incluir_promocion=True):
        data = {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'categoria': self.categoria,
            'provincia': self.provincia,
            'distrito': self.distrito,
            'destino': self.destino,
            'descripcion': self.descripcion[:200] + '...' if self.descripcion and len(self.descripcion) > 200 else self.descripcion,
            'duracion': f"{self.duracion_cantidad} {self.duracion_unidad}",
            'precio': self.precio,
            'cupo_maximo': self.cupo_maximo,
            'imagen': self.imagen,
            'incluye_transporte': self.incluye_transporte,
            'incluye_alimentacion': self.incluye_alimentacion,
            'incluye_hospedaje': self.incluye_hospedaje,
            'incluye_guia': self.incluye_guia,
            'tipo_experiencia': self.tipo_experiencia,
            'tipo_programacion': self.tipo_programacion,
            'dias_operacion': self.get_dias_operacion_nombres(),
            'fecha_unica': self.fecha_unica.strftime('%d/%m/%Y') if self.fecha_unica else None,
            'activo': self.activo,
            'calificacion': self.get_calificacion_promedio(),
            'total_resenas': self.get_total_resenas()
        }
        
        if incluir_promocion:
            data['promocion'] = self.get_precio_con_descuento()
        
        return data
    
    def __repr__(self):
        return f'<Servicio {self.nombre} - {self.codigo}>'

class Disponibilidad(db.Model):
    __tablename__ = 'disponibilidad'
    
    id = db.Column(db.Integer, primary_key=True)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    cupos_disponibles = db.Column(db.Integer, default=0)
    fecha_actualizacion = db.Column(db.DateTime, default=panama_now, onupdate=panama_now)
    
    servicio = db.relationship('Servicio', back_populates='disponibilidad')
    
    __table_args__ = (
        db.UniqueConstraint('servicio_id', 'fecha', name='uix_servicio_fecha'),
    )
    
    def __repr__(self):
        return f'<Disponibilidad Tour {self.servicio_id} - {self.fecha}: {self.cupos_disponibles} cupos>'

class Resena(db.Model):
    __tablename__ = 'resenas'
    
    id = db.Column(db.Integer, primary_key=True)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=True)
    calificacion = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=panama_now)
    activa = db.Column(db.Boolean, default=True)
    
    cliente = db.relationship('Cliente', backref='resenas')
    reserva = db.relationship('Reserva', backref='resena')
    
    def __repr__(self):
        return f'<Resena {self.id} - {self.calificacion} estrellas>'