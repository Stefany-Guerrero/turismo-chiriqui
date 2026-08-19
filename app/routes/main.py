from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.models.servicio import Servicio, Disponibilidad
from app.models.reserva import Reserva
from app.models.cliente import Cliente
from app.models.notificacion import Notificacion
from app.models.promocion import Promocion
from app.forms import AsistenteViajeForm
from app.email_utils import send_reservation_email, send_admin_new_reservation
from app.utils.archivos import validar_archivo
from datetime import datetime, timedelta, date
import secrets
import json
import os
import string
from sqlalchemy import or_, func

from app.utils import preload_promociones, preload_disponibilidad

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    servicios = Servicio.query_activos_sin_promocion().all()
    tours = servicios

    preload_promociones(servicios)
    for s in servicios:
        s.promocion_activa = getattr(s, '_promo_cache', None)

    ofertas = Servicio.query.filter_by(activo=True).all()
    preload_promociones(ofertas)
    ofertas = [s for s in ofertas if getattr(s, '_promo_cache', None)]
    for s in ofertas:
        s.promocion_activa = getattr(s, '_promo_cache', None)

    mas_vendidos = db.session.query(
        Servicio,
        func.count(Reserva.id).label('num_reservas')
    ).join(
        Reserva, Reserva.servicio_id == Servicio.id
    ).filter(
        Servicio.activo == True,
        Reserva.estado != 'cancelada'
    ).group_by(
        Servicio.id
    ).order_by(
        func.count(Reserva.id).desc()
    ).limit(4).all()
    
    return render_template('index.html', 
                         servicios=servicios, 
                         tours=tours,
                         ofertas=ofertas,
                         mas_vendidos=mas_vendidos,
                         destino='',
                         fecha_inicio='',
                         fecha_fin='',
                         personas='1',
                         categoria='',
                         tipo_duracion='')

def _escape_like(value):
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

@main_bp.route('/bx')
def buscar():
    destino = request.args.get('destino', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    personas = request.args.get('personas', '1')
    categoria = request.args.get('categoria', '')
    tipo_duracion = request.args.get('tipo_duracion', '')
    
    if tipo_duracion == 'oferta':
        query = Servicio.query.filter_by(activo=True)
    else:
        query = Servicio.query_activos_sin_promocion()
    
    if destino:
        destEsc = _escape_like(destino)
        query = query.filter(
            or_(
                Servicio.nombre.ilike(f'%{destEsc}%'),
                Servicio.destino.ilike(f'%{destEsc}%'),
                Servicio.provincia.ilike(f'%{destEsc}%'),
                Servicio.distrito.ilike(f'%{destEsc}%')
            )
        )
    
    if categoria:
        query = query.filter(Servicio.tipo_experiencia == categoria)
    
    if tipo_duracion == 'por_dia':
        query = query.filter(
            or_(
                Servicio.duracion_unidad == 'horas',
                db.and_(Servicio.duracion_unidad == 'dias', Servicio.duracion_cantidad == 1)
            )
        )
    elif tipo_duracion == 'extendido':
        query = query.filter(
            Servicio.duracion_unidad == 'dias',
            Servicio.duracion_cantidad > 1
        )
    elif tipo_duracion == 'oferta':
        hoy = datetime.now().date()
        query = query.filter(
            Servicio.id.in_(
                db.session.query(Promocion.servicio_id).filter(
                    Promocion.activa == True,
                    Promocion.fecha_inicio <= hoy,
                    Promocion.fecha_fin >= hoy
                )
            )
        )
    
    if personas and personas.isdigit():
        num_personas = int(personas)
        query = query.filter(Servicio.cupo_maximo >= num_personas)
    
    if fecha_inicio and fecha_fin:
        try:
            fecha_ini = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            if fecha_fin_obj < fecha_ini:
                flash('La fecha de fin debe ser posterior a la fecha de inicio.', 'warning')
                return redirect(url_for('main.index'))
            
            if (fecha_fin_obj - fecha_ini).days > 30:
                flash('El periodo de búsqueda no puede ser mayor a 30 días.', 'warning')
                return redirect(url_for('main.index'))
            
            num_personas = int(personas) if personas.isdigit() else 1
            dias_rango = (fecha_fin_obj - fecha_ini).days + 1
            minimo_dias = max(1, int(dias_rango * 0.7))
            
            todos_servicios = query.all()
            disp_map = preload_disponibilidad(todos_servicios, fecha_ini, fecha_fin_obj)
            dias_por_tour = {s.id: 0 for s in todos_servicios}
            
            d = fecha_ini
            while d <= fecha_fin_obj:
                for s in todos_servicios:
                    if s.esta_disponible(d):
                        cupos = disp_map.get((s.id, d), s.cupo_maximo)
                        if cupos >= num_personas:
                            dias_por_tour[s.id] += 1
                d += timedelta(days=1)
            
            ids_validos = [tid for tid, dias in dias_por_tour.items() if dias >= minimo_dias]
            query = query.filter(Servicio.id.in_(ids_validos))
            
        except ValueError:
            flash('Formato de fecha inválido.', 'warning')
    
    servicios = query.all()
    todos_tours = Servicio.query_activos_sin_promocion().all()
    
    preload_promociones(servicios)
    for servicio in servicios:
        servicio.promocion_activa = getattr(servicio, '_promo_cache', None)
    
    dias_info = {}
    if fecha_inicio and fecha_fin:
        try:
            fecha_ini = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            if not disp_map:
                disp_map = preload_disponibilidad(servicios, fecha_ini, fecha_fin_obj)
            num_p = int(personas) if personas and personas.isdigit() else 1
            for s in servicios:
                dias_disponibles = []
                d = fecha_ini
                while d <= fecha_fin_obj:
                    if s.esta_disponible(d):
                        cupos = disp_map.get((s.id, d), s.cupo_maximo)
                        if cupos >= num_p:
                            dias_disponibles.append(d)
                    d += timedelta(days=1)
                dias_info[s.id] = dias_disponibles
        except:
            pass
    
    if tipo_duracion == 'oferta':
        ofertas = servicios
    else:
        todos = Servicio.query.filter_by(activo=True).all()
        preload_promociones(todos)
        ofertas = [s for s in todos if getattr(s, '_promo_cache', None)]
        for s in ofertas:
            s.promocion_activa = getattr(s, '_promo_cache', None)
        if tipo_duracion == 'por_dia':
            ofertas = [s for s in ofertas if not (s.duracion_unidad == 'dias' and s.duracion_cantidad and s.duracion_cantidad > 1)]
        elif tipo_duracion == 'extendido':
            ofertas = [s for s in ofertas if s.duracion_unidad == 'dias' and s.duracion_cantidad and s.duracion_cantidad > 1]
    
    mas_vendidos = db.session.query(
        Servicio,
        func.count(Reserva.id).label('num_reservas')
    ).join(
        Reserva, Reserva.servicio_id == Servicio.id
    ).filter(
        Servicio.activo == True,
        Reserva.estado != 'cancelada'
    ).group_by(
        Servicio.id
    ).order_by(
        func.count(Reserva.id).desc()
    ).limit(4).all()
    
    return render_template('index.html', 
                         servicios=servicios,
                         tours=todos_tours,
                         ofertas=ofertas,
                         mas_vendidos=mas_vendidos,
                         destino=destino,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         personas=personas,
                         categoria=categoria,
                         tipo_duracion=tipo_duracion,
                         dias_info=dias_info)

@main_bp.route('/t/<int:id>')
def tour_detalle(id):
    servicio = Servicio.query.get_or_404(id)
    servicio.promocion_activa = servicio.get_promocion_activa()
    
    hoy = datetime.now().date()
    mes_actual = request.args.get('mes', hoy.month, type=int)
    año_actual = request.args.get('año', hoy.year, type=int)
    
    if mes_actual < 1 or mes_actual > 12:
        mes_actual = hoy.month
    if año_actual < 2000 or año_actual > 2100:
        año_actual = hoy.year
    
    primer_dia = date(año_actual, mes_actual, 1)
    if mes_actual == 12:
        ultimo_dia = date(año_actual + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(año_actual, mes_actual + 1, 1) - timedelta(days=1)
    disp_map = preload_disponibilidad([servicio], primer_dia, ultimo_dia)
    
    calendario = servicio.get_calendario_mes(mes_actual, año_actual, disp_map=disp_map)
    cupos_json = {d['fecha'].strftime('%Y-%m-%d'): d['cupos'] for d in calendario['dias']}
    
    promocion_info = servicio.get_precio_con_descuento()
    precio_a_usar = promocion_info['precio_final']
    
    es_extendido = servicio.duracion_unidad == 'dias' and servicio.duracion_cantidad > 1
    duracion_dias = servicio.duracion_cantidad if es_extendido else 1
        
    return render_template('tour_detalle.html', 
                         servicio=servicio, 
                         calendario=calendario,
                         mes_actual=mes_actual,
                         año_actual=año_actual,
                         cupos_json=cupos_json,
                         precio_a_usar=precio_a_usar,
                         es_extendido=es_extendido,
                         duracion_dias=duracion_dias)

@main_bp.route('/t/<int:id>/cal')
def tour_calendario(id):
    servicio = Servicio.query.get_or_404(id)
    
    hoy = datetime.now().date()
    mes_actual = request.args.get('mes', hoy.month, type=int)
    año_actual = request.args.get('año', hoy.year, type=int)
    
    if mes_actual < 1 or mes_actual > 12:
        mes_actual = hoy.month
    if año_actual < 2000 or año_actual > 2100:
        año_actual = hoy.year
    
    primer_dia = date(año_actual, mes_actual, 1)
    if mes_actual == 12:
        ultimo_dia = date(año_actual + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(año_actual, mes_actual + 1, 1) - timedelta(days=1)
    disp_map = preload_disponibilidad([servicio], primer_dia, ultimo_dia)
    
    calendario = servicio.get_calendario_mes(mes_actual, año_actual, disp_map=disp_map)
    cupos_json = {d['fecha'].strftime('%Y-%m-%d'): d['cupos'] for d in calendario['dias']}
    
    return render_template('tour_calendario.html',
                         calendario=calendario,
                         mes_actual=mes_actual,
                         año_actual=año_actual,
                         cupos_json=cupos_json)

@main_bp.route('/c/<token>')
def consulta_reserva_token(token):
    reserva = Reserva.query.filter_by(consulta_token=token).first()
    if not reserva:
        abort(404)
    if current_user.is_authenticated and current_user.rol != 'admin':
        cliente = current_user.get_cliente()
        if reserva.cliente_id != cliente.id:
            flash('No tienes permiso para ver esta reserva.', 'error')
            return redirect(url_for('main.mis_reservas'))
    elif not current_user.is_authenticated:
        pass
    return render_template('reservas/consulta_reserva.html', reserva=reserva)

@main_bp.route('/reserva/<int:id>/consulta')
@login_required
def consulta_reserva(id):
    reserva = db.session.get(Reserva, id)
    if not reserva:
        abort(404)
    if current_user.rol != 'admin':
        cliente = current_user.get_cliente()
        if reserva.cliente_id != cliente.id:
            flash('No tienes permiso para ver esta reserva.', 'error')
            return redirect(url_for('main.mis_reservas'))
    if reserva.consulta_token:
        return redirect(url_for('main.consulta_reserva_token', token=reserva.consulta_token))
    return render_template('reservas/consulta_reserva.html', reserva=reserva)

@main_bp.route('/ax', methods=['GET', 'POST'])
def asistente_viaje():
    form = AsistenteViajeForm()
    resultados = []
    mostrar_resultados = False
    es_exacto = False
    
    if form.validate_on_submit():
        mostrar_resultados = True
        
        presupuesto_map = {'hasta_50': 50, '50_100': 100, '100_250': 250, 'mas_250': 999999}
        presupuesto_max = presupuesto_map.get(form.presupuesto.data, 999999)
        
        preferencias = {
            'transporte': form.transporte.data,
            'experiencia': form.experiencia.data,
            'duracion': form.duracion.data,
            'presupuesto': presupuesto_max,
        }
        
        tours = Servicio.query_activos_sin_promocion().all()
        
        scored = []
        for tour in tours:
            score = tour.calcular_score(preferencias)
            
            if score > 0:
                aciertos = 0
                if preferencias['transporte'] in tour.get_transportes_list():
                    aciertos += 1
                if tour.tipo_experiencia == preferencias['experiencia']:
                    aciertos += 1
                if tour.duracion_recomendada == preferencias['duracion']:
                    aciertos += 1
                if tour.precio <= presupuesto_max:
                    aciertos += 1
                
                filtros_seleccionados = 4
                es_coincidencia_exacta = aciertos == filtros_seleccionados
                scored.append((tour, score, es_coincidencia_exacta))
        
        scored.sort(key=lambda x: (-x[2], -x[1]))
        
        resultados_usar = [r for r in scored if r[2]]
        if not resultados_usar:
            resultados_usar = scored[:20]
        
        resultados = [(r[0], r[1]) for r in resultados_usar]
        es_exacto = any(r[2] for r in resultados_usar)
        
        for servicio, _ in resultados:
            servicio.promocion_activa = servicio.get_promocion_activa()
    
    return render_template('asistente_viaje.html', 
                         form=form, 
                         resultados=resultados,
                         mostrar_resultados=mostrar_resultados,
                         es_exacto=es_exacto)

def generar_codigo_transaccion():
    fecha = datetime.now().strftime('%Y%m%d')
    rand = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f'TCH-{fecha}-{rand}'

@main_bp.route('/px/<int:servicio_id>', methods=['POST'])
def pagar(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)
    servicio.promocion_activa = servicio.get_promocion_activa()

    fecha_gira = request.form.get('fecha_gira')
    fecha_fin = request.form.get('fecha_fin')
    numero_personas = int(request.form.get('numero_personas', 1))
    if numero_personas < 1 or numero_personas > 50:
        flash('Número de personas inválido (1-50).', 'error')
        return redirect(url_for('main.tour_detalle', id=servicio_id))
    transporte = request.form.get('transporte', '')

    if not fecha_gira:
        flash('Por favor selecciona una fecha.', 'error')
        return redirect(url_for('main.tour_detalle', id=servicio_id))

    if not current_user.is_authenticated:
        session['reserva_pendiente'] = {
            'servicio_id': servicio_id,
            'fecha_gira': fecha_gira,
            'fecha_fin': fecha_fin,
            'numero_personas': numero_personas,
            'transporte': transporte
        }
        flash('Inicia sesión o regístrate para completar tu pago.', 'warning')
        return redirect(url_for('auth.login', next=url_for('main.procesar_pago_pendiente')))

    try:
        fecha_gira_obj = datetime.strptime(fecha_gira, '%Y-%m-%d').date()
    except ValueError:
        flash('Formato de fecha inválido.', 'error')
        return redirect(url_for('main.tour_detalle', id=servicio_id))

    if fecha_gira_obj < datetime.now().date():
        flash('No se puede reservar en una fecha pasada.', 'error')
        return redirect(url_for('main.tour_detalle', id=servicio_id))

    if not servicio.esta_disponible(fecha_gira_obj):
        flash('El tour no está disponible en esta fecha.', 'error')
        return redirect(url_for('main.tour_detalle', id=servicio_id))

    fecha_fin_obj = None
    es_extendido = servicio.duracion_unidad == 'dias' and servicio.duracion_cantidad > 1
    if es_extendido:
        if fecha_fin:
            try:
                fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            except ValueError:
                flash('Formato de fecha de fin inválido.', 'error')
                return redirect(url_for('main.tour_detalle', id=servicio_id))
        else:
            fecha_fin_obj = fecha_gira_obj + timedelta(days=servicio.duracion_cantidad - 1)

        d = fecha_gira_obj
        while d <= fecha_fin_obj:
            if not servicio.esta_disponible(d):
                flash(f'El tour no está disponible el día {d.strftime("%d/%m/%Y")}.', 'error')
                return redirect(url_for('main.tour_detalle', id=servicio_id))
            d += timedelta(days=1)

    promocion_info = servicio.get_precio_con_descuento()
    precio_base = promocion_info['precio_final']
    precio_transporte = servicio.get_precio_transporte(transporte) if transporte else 0
    precio_persona = round(precio_base + precio_transporte, 2)
    subtotal = round(precio_persona * numero_personas, 2)
    itbms = round(subtotal * 0.07, 2)
    total = round(subtotal + itbms, 2)

    return render_template('pagar.html',
                         servicio=servicio,
                         fecha_gira=fecha_gira,
                         fecha_fin=fecha_fin_obj.strftime('%Y-%m-%d') if fecha_fin_obj else fecha_gira,
                         numero_personas=numero_personas,
                         transporte=transporte,
                         precio_base=precio_base,
                         precio_transporte=precio_transporte,
                         precio_persona=precio_persona,
                         subtotal=subtotal,
                         itbms=itbms,
                         total=total)

@main_bp.route('/cx/<int:servicio_id>', methods=['POST'])
@login_required
def confirmar_pago(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)

    fecha_gira = request.form.get('fecha_gira')
    fecha_fin = request.form.get('fecha_fin')
    numero_personas = int(request.form.get('numero_personas', 1))
    if numero_personas < 1 or numero_personas > 50:
        flash('Número de personas inválido (1-50).', 'error')
        return redirect(url_for('main.tour_detalle', id=servicio_id))
    transporte = request.form.get('transporte', '')
    metodo_pago = request.form.get('metodo_pago', 'tarjeta')
    tipo_tarjeta = request.form.get('tipo_tarjeta')
    titular_tarjeta = request.form.get('titular_tarjeta')
    numero_tarjeta = request.form.get('numero_tarjeta', '').replace(' ', '').replace('-', '')
    telefono_contacto = ''

    promocion_info = servicio.get_precio_con_descuento()
    precio_base = promocion_info['precio_final']
    precio_transporte = servicio.get_precio_transporte(transporte) if transporte else 0
    precio_persona = round(precio_base + precio_transporte, 2)
    subtotal = round(precio_persona * numero_personas, 2)
    itbms = round(subtotal * 0.07, 2)
    total = round(subtotal + itbms, 2)

    if metodo_pago == 'yappy':
        telefono_contacto = request.form.get('telefono_contacto_yappy', '').strip()
        if 'comprobante_pago' not in request.files:
            flash('Debes subir el comprobante de pago.', 'error')
            return redirect(url_for('main.tour_detalle', id=servicio_id))
        archivo_comprobante = request.files['comprobante_pago']
        if archivo_comprobante.filename == '':
            flash('Debes seleccionar un archivo de comprobante.', 'error')
            return redirect(url_for('main.tour_detalle', id=servicio_id))
        valido, mensaje = validar_archivo(archivo_comprobante)
        if not valido:
            flash(f'Comprobante inválido: {mensaje}', 'error')
            return redirect(url_for('main.tour_detalle', id=servicio_id))
    else:
        telefono_contacto = request.form.get('telefono_contacto', '').strip()
        if not all([tipo_tarjeta, titular_tarjeta, numero_tarjeta]):
            flash('Completa todos los datos de pago.', 'error')
            return redirect(url_for('main.tour_detalle', id=servicio_id))

        if len(numero_tarjeta) < 13 or len(numero_tarjeta) > 19:
            flash('Número de tarjeta inválido.', 'error')
            return redirect(url_for('main.tour_detalle', id=servicio_id))

    try:
        fecha_gira_obj = datetime.strptime(fecha_gira, '%Y-%m-%d').date()
    except ValueError:
        flash('Formato de fecha inválido.', 'error')
        return redirect(url_for('main.tour_detalle', id=servicio_id))

    if fecha_gira_obj < datetime.now().date():
        flash('No se puede reservar en una fecha pasada.', 'error')
        return redirect(url_for('main.tour_detalle', id=servicio_id))

    if not servicio.esta_disponible(fecha_gira_obj):
        flash('El tour no está disponible en esta fecha.', 'error')
        return redirect(url_for('main.tour_detalle', id=servicio_id))

    fecha_fin_obj = None
    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de fecha de fin inválido.', 'error')
            return redirect(url_for('main.tour_detalle', id=servicio_id))

    cliente = current_user.get_cliente()

    try:

        if telefono_contacto:
            cliente.telefono = telefono_contacto

        d = fecha_gira_obj
        hasta = fecha_fin_obj if fecha_fin_obj else fecha_gira_obj
        while d <= hasta:
            disp = Disponibilidad.query.filter_by(
                servicio_id=servicio.id, 
                fecha=d
            ).with_for_update().first()
            if disp:
                if disp.cupos_disponibles < numero_personas:
                    db.session.rollback()
                    flash(f'No hay cupos disponibles para el día {d.strftime("%d/%m/%Y")}.', 'error')
                    return redirect(url_for('main.tour_detalle', id=servicio_id))
                disp.cupos_disponibles -= numero_personas
            else:
                if servicio.cupo_maximo < numero_personas:
                    db.session.rollback()
                    flash('No hay cupos disponibles.', 'error')
                    return redirect(url_for('main.tour_detalle', id=servicio_id))
                disp = Disponibilidad(
                    servicio_id=servicio.id,
                    fecha=d,
                    cupos_disponibles=servicio.cupo_maximo - numero_personas
                )
                db.session.add(disp)
            d += timedelta(days=1)

        promocion = servicio.get_promocion_activa()
        if promocion:
            from app.models.promocion import Promocion
            promocion = Promocion.query.filter_by(id=promocion.id).with_for_update().first()
        codigo = generar_codigo_transaccion()

        if promocion:
            if promocion.uso_maximo > 0 and promocion.usos_actuales >= promocion.uso_maximo:
                db.session.rollback()
                flash('Esta promoción se ha agotado.', 'error')
                return redirect(url_for('main.tour_detalle', id=servicio_id))
            promocion.usos_actuales += 1

        reserva = Reserva(
            cliente_id=cliente.id,
            servicio_id=servicio.id,
            fecha_gira=fecha_gira_obj,
            fecha_fin=fecha_fin_obj,
            numero_personas=numero_personas,
            subtotal=subtotal,
            itbms=itbms,
            total_pago=total,
            metodo_pago=metodo_pago,
            tipo_tarjeta=tipo_tarjeta if metodo_pago == 'tarjeta' else None,
            titular_tarjeta=titular_tarjeta if metodo_pago == 'tarjeta' else None,
            ultimos_digitos=numero_tarjeta[-4:] if metodo_pago == 'tarjeta' and numero_tarjeta else None,
            codigo_transaccion=codigo,
            transporte=transporte or None,
            estado='confirmada',
            promocion_id=promocion.id if promocion else None,
            descuento_aplicado=round(servicio.precio * promocion.valor / 100 if promocion and promocion.tipo == 'porcentaje' else (float(promocion.valor) if promocion else 0), 2)
        )

        db.session.add(reserva)
        db.session.flush()

        if metodo_pago == 'yappy' and archivo_comprobante:
            ext = archivo_comprobante.filename.rsplit('.', 1)[-1].lower()
            nombre_archivo = f'comprobante_{reserva.id}_{codigo}.{ext}'
            ruta_upload = os.path.join(current_app.root_path, 'static', 'comprobantes', nombre_archivo)
            archivo_comprobante.save(ruta_upload)
            reserva.comprobante_pago = nombre_archivo

            datos_json = {
                'id_reserva': reserva.id,
                'codigo_transaccion': codigo,
                'monto': total,
                'moneda': 'USD',
                'metodo_pago': 'Yappy',
                'telefono_contacto': telefono_contacto,
                'fecha_pago': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'nombre_cliente': cliente.usuario.nombre_completo,
                'email_cliente': cliente.usuario.email,
                'tour': servicio.nombre,
                'fecha_gira': fecha_gira,
                'numero_personas': numero_personas,
                'comprobante': nombre_archivo
            }
            json_dir = os.path.join(current_app.root_path, 'json_transacciones')
            os.makedirs(json_dir, exist_ok=True)
            ruta_json = os.path.join(json_dir, f'transaccion_{reserva.id}_{codigo}.json')
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(datos_json, f, ensure_ascii=False, indent=2)
            reserva.datos_transaccion = json.dumps(datos_json, ensure_ascii=False)

        db.session.commit()

        try:
            notif = Notificacion(
                usuario_id=current_user.id,
                titulo='Reserva confirmada',
                mensaje=f'Tu reserva para {servicio.nombre} el {fecha_gira} está confirmada. Código: {codigo}',
                tipo='reserva_confirmada',
                referencia_id=reserva.id,
                referencia_tipo='reserva'
            )
            db.session.add(notif)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'Error creando notificación: {e}')

        try:
            import threading
            app = current_app._get_current_object()
            _reserva_id = reserva.id
            _cliente_id = cliente.id
            def _enviar_emails():
                with app.app_context():
                    try:
                        from sqlalchemy.orm import joinedload
                        from app.models.reserva import Reserva as R
                        from app.models.cliente import Cliente as C
                        r = R.query.options(
                            joinedload(R.servicio),
                            joinedload(R.cliente).joinedload(C.usuario)
                        ).get(_reserva_id)
                        c = C.query.options(
                            joinedload(C.usuario)
                        ).get(_cliente_id)
                        if r and c:
                            send_reservation_email(c, r)
                            send_admin_new_reservation(c, r)
                    except Exception as e:
                        app.logger.error(f'Error enviando emails: {e}')
            threading.Thread(target=_enviar_emails, daemon=True).start()
        except Exception as e:
            current_app.logger.error(f'Error lanzando hilo de emails: {e}')

        flash(f'Pago procesado exitosamente. Código de transacción: {codigo}', 'success')
        session['detalle_reserva_id'] = reserva.id
        return redirect(url_for('reservas.detalle_pago'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al procesar el pago: {e}')
        flash('Error al procesar el pago. Intenta de nuevo.', 'error')
        return redirect(url_for('main.tour_detalle', id=servicio_id))

@main_bp.route('/pp')
@login_required
def procesar_pago_pendiente():
    datos = session.pop('reserva_pendiente', None)
    if not datos:
        flash('No hay ninguna reserva pendiente.', 'info')
        return redirect(url_for('main.index'))

    flash('Confirma los datos y procede al pago.', 'info')
    return redirect(url_for('main.tour_detalle', id=datos['servicio_id']))

@main_bp.route('/mr')
@login_required
def mis_reservas():
    cliente = current_user.get_cliente()
    
    reservas = Reserva.query.filter_by(cliente_id=cliente.id).order_by(Reserva.fecha_creacion.desc()).all()
    
    for reserva in reservas:
        if reserva.servicio:
            reserva.servicio.promocion_activa = reserva.servicio.get_promocion_activa()
    
    return render_template('mis_reservas.html', reservas=reservas)

@main_bp.route('/cr/<int:reserva_id>', methods=['POST'])
@login_required
def cancelar_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    
    if reserva.cliente.usuario_id != current_user.id:
        flash('No tienes permiso para cancelar esta reserva.', 'error')
        return redirect(url_for('main.mis_reservas'))
    
    if reserva.estado != 'pendiente':
        flash('Solo puedes cancelar reservas en estado pendiente.', 'error')
        return redirect(url_for('main.mis_reservas'))
    
    try:
        fecha_inicio = reserva.fecha_gira.date() if hasattr(reserva.fecha_gira, 'date') else reserva.fecha_gira
        fecha_fin = reserva.fecha_fin.date() if reserva.fecha_fin and hasattr(reserva.fecha_fin, 'date') else reserva.fecha_fin
        if not fecha_fin:
            fecha_fin = fecha_inicio

        d = fecha_inicio
        while d <= fecha_fin:
            disp = Disponibilidad.query.filter_by(
                servicio_id=reserva.servicio_id,
                fecha=d
            ).with_for_update().first()
            if disp:
                disp.cupos_disponibles = min(
                    disp.cupos_disponibles + reserva.numero_personas,
                    Servicio.query.get(reserva.servicio_id).cupo_maximo
                )
            d += timedelta(days=1)

        reserva.estado = 'cancelada'
        db.session.commit()

        flash('Reserva cancelada exitosamente.', 'success')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al cancelar la reserva: {e}')
        flash('Error al cancelar la reserva. Intenta de nuevo.', 'error')
    
    return redirect(url_for('main.mis_reservas'))