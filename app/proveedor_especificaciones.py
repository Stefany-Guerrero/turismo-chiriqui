from flask import json

ESPECIFICACIONES_SCHEMA = {
    'hotel': {
        'label': 'Hotel / Alojamiento',
        'campos': [
            {'name': 'categoria', 'label': 'Categoría', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('1_estrella', '1★'), ('2_estrellas', '2★'),
                ('3_estrellas', '3★'), ('4_estrellas', '4★'), ('5_estrellas', '5★')
            ]},
            {'name': 'habitaciones', 'label': 'Habitaciones disponibles', 'type': 'number', 'min': 0},
            {'name': 'capacidad_total', 'label': 'Capacidad total de huéspedes', 'type': 'number', 'min': 1},
            {'name': 'servicios', 'label': 'Servicios incluidos', 'type': 'checklist', 'options': [
                ('wifi', 'WiFi'), ('piscina', 'Piscina'), ('desayuno', 'Desayuno'),
                ('estacionamiento', 'Estacionamiento'), ('aire_acondicionado', 'Aire acondicionado'),
                ('restaurante', 'Restaurante'), ('lavanderia', 'Lavandería'),
                ('gimnasio', 'Gimnasio'), ('spa', 'Spa'), ('accesibilidad', 'Accesibilidad')
            ]},
            {'name': 'check_in', 'label': 'Check-in', 'type': 'time'},
            {'name': 'check_out', 'label': 'Check-out', 'type': 'time'},
            {'name': 'politicas', 'label': 'Políticas / Restricciones', 'type': 'textarea'}
        ]
    },
    'airbnb': {
        'label': 'Airbnb / Alquiler Vacacional',
        'campos': [
            {'name': 'tipo_propiedad', 'label': 'Tipo de propiedad', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('casa', 'Casa completa'), ('apartamento', 'Apartamento'),
                ('cabana', 'Cabaña'), ('villa', 'Villa'), ('estudio', 'Estudio'),
                ('habitacion', 'Habitación privada')
            ]},
            {'name': 'capacidad_maxima', 'label': 'Capacidad máxima de huéspedes', 'type': 'number', 'min': 1},
            {'name': 'habitaciones', 'label': 'Habitaciones', 'type': 'number', 'min': 0},
            {'name': 'banos', 'label': 'Baños', 'type': 'number', 'min': 0, 'step': '0.5'},
            {'name': 'servicios', 'label': 'Servicios / Amenidades', 'type': 'checklist', 'options': [
                ('wifi', 'WiFi'), ('cocina', 'Cocina equipada'), ('estacionamiento', 'Estacionamiento gratuito'),
                ('lavadora', 'Lavadora'), ('tv', 'TV / Streaming'), ('aire_acondicionado', 'Aire acondicionado'),
                ('calefaccion', 'Calefacción'), ('balcon', 'Balcón / Terraza'), ('jardin', 'Jardín'),
                ('piscina', 'Piscina'), ('mascotas', 'Acepta mascotas'), ('humo', 'Permite fumar')
            ]},
            {'name': 'check_in', 'label': 'Check-in', 'type': 'time'},
            {'name': 'check_out', 'label': 'Check-out', 'type': 'time'},
            {'name': 'reglas', 'label': 'Reglas de la casa', 'type': 'textarea'}
        ]
    },
    'cabana': {
        'label': 'Cabaña / Eco-Lodge',
        'campos': [
            {'name': 'tipo_cabana', 'label': 'Tipo', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('madera', 'Cabaña de madera'), ('bambu', 'Eco-cabaña de bambú'),
                ('lujo', 'Cabaña de lujo'), ('rustica', 'Cabaña rústica'), ('glamping', 'Glamping / Tienda de lujo')
            ]},
            {'name': 'capacidad', 'label': 'Capacidad máxima', 'type': 'number', 'min': 1},
            {'name': 'habitaciones', 'label': 'Habitaciones', 'type': 'number', 'min': 0},
            {'name': 'banos', 'label': 'Baños', 'type': 'number', 'min': 0},
            {'name': 'entorno', 'label': 'Entorno', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('montana', 'Montaña'), ('playa', 'Playa'),
                ('bosque', 'Bosque'), ('rio', 'Río'), ('campo', 'Campo abierto')
            ]},
            {'name': 'servicios', 'label': 'Servicios', 'type': 'checklist', 'options': [
                ('wifi', 'WiFi'), ('chimenea', 'Chimenea / Fogata'), ('cocina', 'Cocina'),
                ('desayuno', 'Desayuno incluido'), ('hamaca', 'Hamacas'), ('estacionamiento', 'Estacionamiento'),
                ('agua_caliente', 'Agua caliente'), ('electricidad', 'Generador eléctrico')
            ]},
            {'name': 'actividades', 'label': 'Actividades en el lugar', 'type': 'text'}
        ]
    },
    'transporte': {
        'label': 'Transporte',
        'campos': [
            {'name': 'tipo_vehiculo', 'label': 'Tipo de vehículo', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('auto', 'Auto ejecutivo'), ('van', 'Van / Minibús'),
                ('bus', 'Autobús'), ('lancha', 'Lancha / Bote'), ('avioneta', 'Avioneta'),
                ('4x4', '4x4 / Todo terreno')
            ]},
            {'name': 'capacidad_pasajeros', 'label': 'Capacidad de pasajeros', 'type': 'number', 'min': 1},
            {'name': 'flota', 'label': 'Cantidad de vehículos disponibles', 'type': 'number', 'min': 1},
            {'name': 'incluye_conductor', 'label': 'Incluye conductor', 'type': 'boolean'},
            {'name': 'tipos_viaje', 'label': 'Tipos de viaje', 'type': 'checklist', 'options': [
                ('local', 'Local (misma provincia)'), ('interprovincial', 'Interprovincial'),
                ('aeropuerto', 'Traslado al aeropuerto'), ('tour', 'Tour / Ruta turística'),
                ('larga_distancia', 'Larga distancia')
            ]},
            {'name': 'seguro', 'label': 'Seguro de pasajeros', 'type': 'boolean'}
        ]
    },
    'guia': {
        'label': 'Guía Turístico',
        'campos': [
            {'name': 'idiomas', 'label': 'Idiomas', 'type': 'checklist', 'options': [
                ('espanol', 'Español'), ('ingles', 'Inglés'), ('frances', 'Francés'),
                ('aleman', 'Alemán'), ('portugues', 'Portugués'), ('mandarin', 'Mandarín'),
                ('japones', 'Japonés'), ('ruso', 'Ruso')
            ]},
            {'name': 'certificaciones', 'label': 'Certificaciones', 'type': 'checklist', 'options': [
                ('guia_general', 'Guía general'), ('guia_naturaleza', 'Guía de naturaleza'),
                ('guia_aventura', 'Guía de aventura'), ('guia_cultural', 'Guía cultural'),
                ('guia_gastronomico', 'Guía gastronómico'), ('primeros_auxilios', 'Primeros auxilios'),
                ('bufeo', 'Buceo'), ('rafting', 'Rafting / Aguas bravas')
            ]},
            {'name': 'especialidad', 'label': 'Especialidad', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('aventura', 'Aventura'), ('naturaleza', 'Naturaleza / Ecoturismo'),
                ('cultural', 'Cultural / Histórico'), ('gastronomico', 'Gastronómico'),
                ('fotografia', 'Fotografía'), ('birdwatching', 'Birdwatching / Avistamiento de aves')
            ]},
            {'name': 'experiencia_anios', 'label': 'Años de experiencia', 'type': 'number', 'min': 0}
        ]
    },
    'restaurante': {
        'label': 'Restaurante / Alimentación',
        'campos': [
            {'name': 'tipo_cocina', 'label': 'Tipo de cocina', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('tipica', 'Comida típica panameña'), ('internacional', 'Internacional'),
                ('mariscos', 'Mariscos'), ('parrilla', 'Parrilla / Grill'), ('vegetariana', 'Vegetariana / Vegana'),
                ('fusion', 'Fusión'), ('cafeteria', 'Cafetería / Repostería')
            ]},
            {'name': 'capacidad_comensales', 'label': 'Capacidad de comensales', 'type': 'number', 'min': 1},
            {'name': 'horario_apertura', 'label': 'Horario de apertura', 'type': 'time'},
            {'name': 'horario_cierre', 'label': 'Horario de cierre', 'type': 'time'},
            {'name': 'servicios', 'label': 'Servicios de alimentación', 'type': 'checklist', 'options': [
                ('desayuno', 'Desayuno'), ('almuerzo', 'Almuerzo'), ('cena', 'Cena'),
                ('box_lunch', 'Box lunch / Empacado'), ('eventos', 'Eventos / Grupos grandes'),
                ('domicilio', 'Domicilio / Delivery')
            ]},
            {'name': 'dietas', 'label': 'Dietas especiales', 'type': 'checklist', 'options': [
                ('vegetariano', 'Vegetariano'), ('vegano', 'Vegano'), ('sin_gluten', 'Sin gluten'),
                ('celiaco', 'Apto para celíacos'), ('halal', 'Halal'), ('kosher', 'Kosher')
            ]}
        ]
    },
    'operador': {
        'label': 'Operador turístico',
        'campos': [
            {'name': 'actividades', 'label': 'Actividades principales', 'type': 'checklist', 'options': [
                ('senderismo', 'Senderismo / Hiking'), ('canopy', 'Canopy / Tirolesa'),
                ('rafting', 'Rafting'), ('kayak', 'Kayak'), ('snorkel', 'Snorkel / Buceo'),
                ('cabalgata', 'Cabalgata / Paseo a caballo'), ('ciclismo', 'Ciclismo de montaña'),
                ('escalada', 'Escalada / Rappel'), ('observacion_aves', 'Observación de aves'),
                ('fotografia', 'Tour fotográfico'), ('cultural', 'Tour cultural'),
                ('gastronomico', 'Tour gastronómico')
            ]},
            {'name': 'capacidad_grupo', 'label': 'Capacidad máxima por grupo', 'type': 'number', 'min': 1},
            {'name': 'duracion_tipica', 'label': 'Duración típica', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('2_horas', '2 horas'), ('4_horas', 'Medio día (4 hrs)'),
                ('8_horas', 'Día completo (8 hrs)'), ('2_dias', '2 días'), ('3_dias', '3 días'),
                ('mas', 'Más de 3 días')
            ]},
            {'name': 'dificultad', 'label': 'Nivel de dificultad', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('facil', 'Fácil'), ('moderado', 'Moderado'), ('dificil', 'Difícil')
            ]},
            {'name': 'equipo', 'label': 'Equipo que proporciona', 'type': 'checklist', 'options': [
                ('cascos', 'Cascos'), ('arneses', 'Arneses'), ('chalecos', 'Chalecos salvavidas'),
                ('bastones', 'Bastones de senderismo'), ('tiendas', 'Tiendas de campaña'),
                ('sacos', 'Sacos de dormir'), ('cuerdas', 'Cuerdas / equipo técnico')
            ]},
            {'name': 'incluye_seguro', 'label': 'Incluye seguro de accidentes', 'type': 'boolean'}
        ]
    },
    'transporte_maritimo': {
        'label': 'Transporte marítimo',
        'campos': [
            {'name': 'tipo_embarcacion', 'label': 'Tipo de embarcación', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('lancha', 'Lancha / Bote'), ('yate', 'Yate'), ('catamaran', 'Catamarán'),
                ('barco', 'Barco'), ('ferry', 'Ferry'), ('pangas', 'Pangas')
            ]},
            {'name': 'capacidad_pasajeros', 'label': 'Capacidad de pasajeros', 'type': 'number', 'min': 1},
            {'name': 'flota', 'label': 'Cantidad de embarcaciones', 'type': 'number', 'min': 1},
            {'name': 'incluye_tripulacion', 'label': 'Incluye tripulación', 'type': 'boolean'},
            {'name': 'rutas', 'label': 'Rutas / Zonas', 'type': 'checklist', 'options': [
                ('locales', 'Locales (misma costa)'), ('islas', 'Islas / Archipiélagos'),
                ('costeras', 'Recorridos costeros'), ('pesca', 'Pesca deportiva'),
                ('transporte_islas', 'Transporte a islas')
            ]},
            {'name': 'seguro', 'label': 'Seguro de pasajeros', 'type': 'boolean'}
        ]
    },
    'atraccion': {
        'label': 'Atracción turística / Entradas',
        'campos': [
            {'name': 'tipo_atraccion', 'label': 'Tipo de atracción', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('parque_nacional', 'Parque nacional / Reserva'),
                ('canopy', 'Canopy / Tirolesa'), ('aguas_termales', 'Aguas termales'),
                ('museo', 'Museo / Sitio histórico'), ('jardin', 'Jardín botánico'),
                ('mirador', 'Mirador'), ('cascada', 'Cascada / Río')
            ]},
            {'name': 'capacidad_visitantes', 'label': 'Capacidad de visitantes', 'type': 'number', 'min': 1},
            {'name': 'horario_apertura', 'label': 'Horario de apertura', 'type': 'time'},
            {'name': 'horario_cierre', 'label': 'Horario de cierre', 'type': 'time'},
            {'name': 'incluye_guia', 'label': 'Incluye guía en el lugar', 'type': 'boolean'},
            {'name': 'servicios', 'label': 'Servicios disponibles', 'type': 'checklist', 'options': [
                ('estacionamiento', 'Estacionamiento'), ('cafeteria', 'Cafetería / Snack'),
                ('banos', 'Baños públicos'), ('tienda', 'Tienda de souvenirs'),
                ('mirador', 'Mirador panorámico'), ('senderos', 'Senderos señalizados')
            ]}
        ]
    },
    'equipo': {
        'label': 'Alquiler de Equipo',
        'campos': [
            {'name': 'tipo_equipo', 'label': 'Tipo de equipo', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('camping', 'Equipo de camping'), ('deportes', 'Equipo deportivo'),
                ('playa', 'Equipo de playa'), ('montana', 'Equipo de montaña'), ('buceo', 'Equipo de buceo'),
                ('fotografia', 'Equipo fotográfico')
            ]},
            {'name': 'inventario', 'label': 'Inventario / Cantidad disponible', 'type': 'number', 'min': 0},
            {'name': 'deposito', 'label': 'Depósito requerido (B/.)', 'type': 'number', 'min': 0, 'step': '0.01'},
            {'name': 'condiciones', 'label': 'Condiciones de alquiler', 'type': 'textarea'},
            {'name': 'incluye_seguro', 'label': 'Incluye seguro contra daños', 'type': 'boolean'}
        ]
    },
    'seguros': {
        'label': 'Seguros',
        'campos': [
            {'name': 'tipo_seguro', 'label': 'Tipo de seguro', 'type': 'select', 'options': [
                ('', 'Seleccione'), ('viajero', 'Seguro de viajero'), ('equipaje', 'Seguro de equipaje'),
                ('cancelacion', 'Seguro de cancelación'), ('accidentes', 'Seguro de accidentes'),
                ('medico', 'Seguro médico'), ('vehiculo', 'Seguro de vehículo de alquiler')
            ]},
            {'name': 'cobertura_maxima', 'label': 'Cobertura máxima (B/.)', 'type': 'number', 'min': 0, 'step': '0.01'},
            {'name': 'deducible', 'label': 'Deducible (B/.)', 'type': 'number', 'min': 0, 'step': '0.01'},
            {'name': 'asistencia_247', 'label': 'Asistencia 24/7', 'type': 'boolean'},
            {'name': 'coberturas', 'label': 'Coberturas incluidas', 'type': 'textarea'}
        ]
    },
    'otro': {
        'label': 'Otro',
        'campos': [
            {'name': 'descripcion', 'label': 'Descripción del servicio', 'type': 'textarea'},
            {'name': 'notas', 'label': 'Notas adicionales', 'type': 'textarea'}
        ]
    }
}


def get_campos_por_tipo(tipo):
    return ESPECIFICACIONES_SCHEMA.get(tipo, {}).get('campos', [])


def get_label_por_tipo(tipo):
    return ESPECIFICACIONES_SCHEMA.get(tipo, {}).get('label', tipo)


def render_especificaciones_html(especificaciones, tipo):
    if not especificaciones or not tipo:
        return '<p class="text-muted">Sin especificaciones</p>'
    
    if isinstance(especificaciones, str):
        try:
            especificaciones = json.loads(especificaciones)
        except (json.JSONDecodeError, TypeError):
            return '<p class="text-muted">Sin especificaciones</p>'
    
    campos = get_campos_por_tipo(tipo)
    html_parts = ['<div class="especificaciones-list">']
    
    for campo in campos:
        name = campo['name']
        valor = especificaciones.get(name)
        if valor is None or valor == '' or valor == []:
            continue
        
        label = campo['label']
        
        if campo['type'] == 'checklist':
            if isinstance(valor, list) and valor:
                opciones_map = {k: v for k, v in campo['options']}
                items = ', '.join(opciones_map.get(v, v) for v in valor)
                html_parts.append(f'<div class="mb-1"><strong>{label}:</strong> {items}</div>')
        elif campo['type'] == 'boolean':
            html_parts.append(f'<div class="mb-1"><strong>{label}:</strong> {"✅ Sí" if valor else "❌ No"}</div>')
        elif campo['type'] == 'number' or campo['type'] == 'time':
            html_parts.append(f'<div class="mb-1"><strong>{label}:</strong> {valor}</div>')
        else:
            html_parts.append(f'<div class="mb-1"><strong>{label}:</strong> {valor}</div>')
    
    if len(html_parts) == 1:
        return '<p class="text-muted">Sin especificaciones registradas</p>'
    
    html_parts.append('</div>')
    return ''.join(html_parts)


CAMPO_CAPACIDAD_POR_TIPO = {
    'hotel': 'capacidad_total',
    'airbnb': 'capacidad_maxima',
    'cabana': 'capacidad',
    'transporte': 'capacidad_pasajeros',
    'transporte_maritimo': 'capacidad_pasajeros',
    'restaurante': 'capacidad_comensales',
    'operador': 'capacidad_grupo',
    'atraccion': 'capacidad_visitantes',
    'equipo': 'inventario',
}
DEFAULT_CAPACIDAD = 10


def obtener_capacidad_proveedor(proveedor):
    if not proveedor or not proveedor.tipo:
        return DEFAULT_CAPACIDAD
    campo = CAMPO_CAPACIDAD_POR_TIPO.get(proveedor.tipo)
    if not campo:
        return DEFAULT_CAPACIDAD
    especs = proveedor.get_especificaciones()
    valor = especs.get(campo)
    if valor is None:
        return DEFAULT_CAPACIDAD
    try:
        return int(valor)
    except (ValueError, TypeError):
        return DEFAULT_CAPACIDAD
