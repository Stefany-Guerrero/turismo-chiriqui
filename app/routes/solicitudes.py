from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app, session
from flask_login import login_required, current_user
from app import db, mail
from flask_mail import Message
from app.models.reserva import Reserva
from app.models.cliente import Cliente
from app.models.viaje_planificado import ViajePlanificado
from app.models.servicio import Servicio
from app.models.notificacion import Notificacion
from app.models.usuario import Usuario
from app.forms import SolicitudForm
from datetime import datetime, date
import os
import json
import uuid

solicitudes_bp = Blueprint('solicitudes', __name__, url_prefix='/solicitudes')

@solicitudes_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    """Clientes crean solicitudes personalizadas"""
    if current_user.rol != 'cliente':
        flash('Solo los clientes pueden crear solicitudes personalizadas.', 'error')
        return redirect(url_for('main.index'))
    
    viaje_id = request.args.get('viaje_id', type=int)
    viaje = None
    
    if viaje_id:
        viaje = ViajePlanificado.query.get_or_404(viaje_id)
        cliente = current_user.get_cliente()
        if viaje.cliente_id != cliente.id:
            flash('No tienes permiso para usar este viaje planificado.', 'error')
            return redirect(url_for('main.index'))
    
    form = SolicitudForm()

    if viaje:
        form.fecha_inicio.data = viaje.fecha_inicio
        form.fecha_fin.data = viaje.fecha_fin
        form.numero_personas.data = viaje.numero_personas
        form.destino_preferido.data = viaje.destino_preferido
        form.transporte.data = viaje.transporte_preferido
        form.hospedaje.data = viaje.requiere_hospedaje
        form.guia.data = viaje.requiere_guia
    
    if form.validate_on_submit():
        try:
            cliente = current_user.get_cliente()
            
            if form.telefono.data:
                cliente.telefono = form.telefono.data
            
            solicitud = Reserva(
                tipo='solicitud',
                cliente_id=cliente.id,
                fecha_gira=form.fecha_inicio.data,
                fecha_fin=form.fecha_fin.data,
                numero_personas=form.numero_personas.data,
                presupuesto_estimado=form.presupuesto_estimado.data,
                presupuesto_tipo=form.presupuesto_tipo.data or None,
                destino_preferido=form.destino_preferido.data,
                lugar_recogida=form.lugar_recogida.data or None,
                lugares_visitar=form.lugares_visitar.data or None,
                tipo_alojamiento=form.tipo_alojamiento.data or None,
                transporte=form.transporte.data,
                alimentacion=form.alimentacion.data or None,
                hospedaje=form.hospedaje.data or False,
                guia=form.guia.data or False,
                contacto_preferido='correo',
                observaciones=form.observaciones.data,
                estado='pendiente'
            )
            db.session.add(solicitud)
            db.session.commit()
            
            # Email al admin
            try:
                admin_email = current_app.config.get('ADMIN_EMAIL', 'itsdanhw14@gmail.com')
                transporte_label = {'vehiculo_propio': 'Vehículo propio', 'autobus': 'Autobús', 'transporte_empresa': 'Transporte del proveedor', 'avion': 'Avión', 'lancha': 'Lancha', 'alquiler_auto': 'Alquiler de auto', 'no_requiere': 'No requiere'}.get(form.transporte.data, form.transporte.data or '—')
                msg = Message(
                    subject=f'Nueva solicitud #{solicitud.id} - {cliente.usuario.nombre_completo}',
                    recipients=[admin_email]
                )
                msg.html = render_template('emails/nueva_solicitud_admin.html',
                    solicitud_id=solicitud.id,
                    cliente_nombre=cliente.usuario.nombre_completo,
                    cliente_email=cliente.usuario.email,
                    cliente_telefono=cliente.telefono or form.telefono.data or 'No especificado',
                    fecha_inicio=form.fecha_inicio.data.strftime('%d/%m/%Y') if form.fecha_inicio.data else '—',
                    fecha_fin=form.fecha_fin.data.strftime('%d/%m/%Y') if form.fecha_fin.data else '—',
                    personas=form.numero_personas.data,
                    destino=form.destino_preferido.data or 'No especificado',
                    presupuesto=f'B/.{float(form.presupuesto_estimado.data):.2f}' if form.presupuesto_estimado.data else 'No especificado',
                    transporte=transporte_label,
                    observaciones=form.observaciones.data or 'Ninguna',
                    link=f'{current_app.config.get("BASE_URL", "http://localhost:5000")}/solicitudes/admin'
                )
                mail.send(msg)
            except Exception as e:
                current_app.logger.error(f'Error sending admin email for solicitud: {e}')
            
            # Notificaci\u00f3n al admin
            try:
                admins = Usuario.query.filter_by(rol='admin', activo=True).all()
                for admin_user in admins:
                    notif = Notificacion(
                        usuario_id=admin_user.id,
                        titulo='Nueva solicitud recibida',
                        mensaje=f'El cliente {cliente.usuario.nombre_completo} ha enviado la solicitud #{solicitud.id}.',
                        tipo='pendiente',
                        referencia_id=solicitud.id,
                        referencia_tipo='solicitud'
                    )
                    db.session.add(notif)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f'Error creating admin notification: {e}')
            
            flash('¡Solicitud enviada exitosamente! Un asesor se pondrá en contacto contigo pronto.', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al enviar la solicitud: {str(e)}', 'error')
    
    return render_template('solicitudes/crear.html', form=form, viaje=viaje, today=date.today().isoformat())

@solicitudes_bp.route('/mis-solicitudes')
@login_required
def mis_solicitudes():
    """Clientes ven sus solicitudes"""
    if current_user.rol != 'cliente':
        flash('No tienes permiso para acceder.', 'error')
        return redirect(url_for('main.index'))
    
    from app.utils.auto_complete import completar_solicitudes_vencidas
    completar_solicitudes_vencidas()
    
    cliente = current_user.get_cliente()
    
    solicitudes = Reserva.query.filter_by(cliente_id=cliente.id, tipo='solicitud').order_by(Reserva.fecha_creacion.desc()).all()
    return render_template('solicitudes/mis_solicitudes.html', solicitudes=solicitudes)

@solicitudes_bp.route('/admin')
@login_required
def admin_solicitudes():
    """Admin ve todas las solicitudes"""
    if current_user.rol != 'admin':
        flash('No tienes permiso para acceder.', 'error')
        return redirect(url_for('main.index'))

    solicitudes = Reserva.query.filter_by(tipo='solicitud').join(Cliente).order_by(Reserva.fecha_creacion.desc()).all()

    Reserva.query.filter_by(tipo='solicitud', leido=False).update({'leido': True})
    db.session.commit()

    pendientes = Reserva.query.filter_by(tipo='solicitud', estado='pendiente').count()
    en_proceso = Reserva.query.filter_by(tipo='solicitud', estado='en_proceso').count()
    cotizadas = Reserva.query.filter_by(tipo='solicitud', estado='cotizada').count()
    aprobadas = Reserva.query.filter_by(tipo='solicitud', estado='aprobada').count()
    rechazadas = Reserva.query.filter_by(tipo='solicitud', estado='rechazada').count()
    
    return render_template('admin/solicitudes.html', 
                         solicitudes=solicitudes,
                         pendientes=pendientes,
                         en_proceso=en_proceso,
                         cotizadas=cotizadas,
                         aprobadas=aprobadas,
                         rechazadas=rechazadas)

def crear_notificacion_solicitud(solicitud, nuevo_estado, cotizacion=None):
    if not solicitud.cliente or not solicitud.cliente.usuario:
        return
    usuario_id = solicitud.cliente.usuario.id
    tipo = nuevo_estado
    titulo = ''
    mensaje = ''
    
    if nuevo_estado == 'cotizada':
        titulo = 'Cotización recibida'
        monto = f'B/.{float(cotizacion):,.2f}' if cotizacion else '—'
        mensaje = f'Tu solicitud #{solicitud.id} tiene una cotización de {monto}.'
    elif nuevo_estado == 'aprobada':
        titulo = 'Solicitud aprobada'
        mensaje = f'Tu solicitud #{solicitud.id} ha sido aprobada. ¡Viaje confirmado!'
    elif nuevo_estado == 'en_proceso':
        titulo = 'Solicitud en revisión'
        mensaje = f'Tu solicitud #{solicitud.id} está siendo revisada por nuestro equipo.'
    elif nuevo_estado == 'rechazada':
        titulo = 'Solicitud rechazada'
        mensaje = f'Tu solicitud #{solicitud.id} ha sido rechazada. Contacta con nosotros para más información.'
    elif nuevo_estado == 'pendiente':
        titulo = 'Solicitud actualizada'
        mensaje = f'Tu solicitud #{solicitud.id} ha sido actualizada a pendiente.'
    
    if titulo:
        notif = Notificacion(
            usuario_id=usuario_id,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            referencia_id=solicitud.id,
            referencia_tipo='solicitud'
        )
        db.session.add(notif)

@ solicitudes_bp.route('/admin/actualizar/<int:id>', methods=['POST'])
@login_required
def actualizar_solicitud(id):
    """Admin actualiza estado de solicitud"""
    if current_user.rol != 'admin':
        flash('No tienes permiso.', 'error')
        return redirect(url_for('main.index'))
    
    solicitud = Reserva.query.get_or_404(id)
    estado_anterior = solicitud.estado
    
    nuevo_estado = request.form.get('estado')
    cotizacion = request.form.get('cotizacion')
    observaciones = request.form.get('observaciones')
    motivo_rechazo = request.form.get('motivo_rechazo')
    accion = request.form.get('accion', 'guardar')
    
    estados_validos = ['pendiente', 'en_proceso', 'cotizada', 'aprobada', 'rechazada']
    
    if nuevo_estado not in estados_validos:
        flash('Estado no válido.', 'error')
        return redirect(url_for('solicitudes.admin_solicitudes'))
    
    try:
        if accion == 'rechazar':
            if not motivo_rechazo or not motivo_rechazo.strip():
                flash('Debes escribir el motivo del rechazo.', 'error')
                return redirect(url_for('solicitudes.admin_solicitudes'))
            solicitud.estado = 'rechazada'
            solicitud.cotizacion = None
            solicitud.motivo_rechazo = motivo_rechazo.strip()
            flash(f'Solicitud #{id} rechazada.', 'warning')
            crear_notificacion_solicitud(solicitud, 'rechazada')
            
        elif accion == 'cotizar':
            if not cotizacion or not cotizacion.strip():
                flash('Debes ingresar un monto de cotización para enviarla.', 'error')
                return redirect(url_for('solicitudes.admin_solicitudes'))
            try:
                solicitud.cotizacion = float(cotizacion)
                solicitud.estado = 'cotizada'
                flash(f'💰 Cotización de B/.{float(cotizacion):,.2f} enviada al cliente.', 'success')
                crear_notificacion_solicitud(solicitud, 'cotizada', cotizacion)
            except ValueError:
                flash('El monto de cotización debe ser un número válido.', 'warning')
                return redirect(url_for('solicitudes.admin_solicitudes'))
        else:
            solicitud.estado = nuevo_estado
            
            if cotizacion and cotizacion.strip():
                try:
                    solicitud.cotizacion = float(cotizacion)
                except ValueError:
                    flash('El monto de cotización debe ser un número válido.', 'warning')
            
            if nuevo_estado != estado_anterior:
                crear_notificacion_solicitud(solicitud, nuevo_estado)
        
        if solicitud.estado != 'rechazada':
            solicitud.motivo_rechazo = None
        
        if observaciones:
            solicitud.observaciones = observaciones
        
        db.session.commit()
        
        if accion == 'guardar':
            flash(f'Solicitud #{id} actualizada a "{nuevo_estado}" exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar la solicitud: {str(e)}', 'error')
    
    return redirect(url_for('solicitudes.admin_solicitudes'))

@solicitudes_bp.route('/admin/cambiar-estado/<int:id>/<estado>', methods=['POST'])
@login_required
def cambiar_estado_solicitud(id, estado):
    """Admin cambia estado rapidamente"""
    if current_user.rol != 'admin':
        flash('No tienes permiso.', 'error')
        return redirect(url_for('main.index'))
    
    solicitud = Reserva.query.get_or_404(id)
    estados_validos = ['pendiente', 'en_proceso', 'cotizada', 'aprobada', 'rechazada']
    
    if estado in estados_validos:
        try:
            estado_anterior = solicitud.estado
            solicitud.estado = estado
            if estado != estado_anterior:
                crear_notificacion_solicitud(solicitud, estado)
            db.session.commit()
            flash(f'Solicitud #{id} actualizada a "{estado}"', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Estado no válido.', 'error')
    
    return redirect(url_for('solicitudes.admin_solicitudes'))

@solicitudes_bp.route('/notificaciones')
@login_required
def get_notificaciones():
    from app.models.notificacion import Notificacion
    notificaciones = Notificacion.query.filter_by(
        usuario_id=current_user.id
    ).order_by(Notificacion.fecha_creacion.desc()).limit(20).all()
    
    return jsonify([{
        'id': n.id,
        'titulo': n.titulo,
        'mensaje': n.mensaje,
        'tipo': n.tipo,
        'leido': n.leido,
        'referencia_id': n.referencia_id,
        'referencia_tipo': n.referencia_tipo,
        'fecha': n.fecha_creacion.strftime('%d/%m/%Y %I:%M %p') if n.fecha_creacion else ''
    } for n in notificaciones])

@solicitudes_bp.route('/notificaciones/no-leidas')
@login_required
def notificaciones_no_leidas():
    from app.models.notificacion import Notificacion
    count = Notificacion.query.filter_by(usuario_id=current_user.id, leido=False).count()
    return jsonify({'count': count})

@solicitudes_bp.route('/notificaciones/marcar-leido/<int:id>', methods=['POST'])
@login_required
def marcar_notificacion_leida(id):
    from app.models.notificacion import Notificacion
    notif = Notificacion.query.get_or_404(id)
    if notif.usuario_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    notif.leido = True
    db.session.commit()
    return jsonify({'success': True})

@solicitudes_bp.route('/notificaciones/marcar-todas-leido', methods=['POST'])
@login_required
def marcar_todas_notificaciones_leidas():
    from app.models.notificacion import Notificacion
    Notificacion.query.filter_by(usuario_id=current_user.id, leido=False).update({'leido': True})
    db.session.commit()
    return jsonify({'success': True})

@solicitudes_bp.route('/detalle/<int:id>')
@login_required
def detalle_solicitud(id):
    """Ver detalle de una solicitud específica"""
    from app.utils.auto_complete import completar_solicitudes_vencidas
    completar_solicitudes_vencidas()
    
    solicitud = Reserva.query.get_or_404(id)
    
    if current_user.rol == 'cliente':
        cliente = current_user.get_cliente()
        if solicitud.cliente_id != cliente.id:
            flash('No tienes permiso para ver esta solicitud.', 'error')
            return redirect(url_for('main.index'))
    
    return render_template('solicitudes/detalle.html', solicitud=solicitud)

@solicitudes_bp.route('/detalle/<int:id>/imprimir')
@login_required
def imprimir_itinerario(id):
    """Vista para imprimir itinerario de solicitud"""
    solicitud = Reserva.query.get_or_404(id)
    
    if current_user.rol == 'cliente':
        cliente = current_user.get_cliente()
        if solicitud.cliente_id != cliente.id:
            flash('No tienes permiso para ver esta solicitud.', 'error')
            return redirect(url_for('main.index'))
    
    return render_template('solicitudes/imprimir_itinerario.html', solicitud=solicitud)

def generar_codigo_transaccion():
    return 'TC-' + uuid.uuid4().hex[:12].upper()

@solicitudes_bp.route('/pagar/<int:id>')
@login_required
def pagar_solicitud(id):
    """Mostrar formulario de pago para solicitud cotizada"""
    solicitud = Reserva.query.get_or_404(id)
    
    if current_user.rol != 'cliente':
        flash('No tienes permiso.', 'error')
        return redirect(url_for('main.index'))
    
    cliente = current_user.get_cliente()
    if solicitud.cliente_id != cliente.id:
        flash('No tienes permiso para pagar esta solicitud.', 'error')
        return redirect(url_for('main.index'))
    
    if solicitud.estado != 'cotizada' or not solicitud.cotizacion:
        flash('Esta solicitud no está disponible para pago.', 'error')
        return redirect(url_for('solicitudes.detalle_solicitud', id=id))
    
    return render_template('solicitudes/pagar.html', solicitud=solicitud)

@solicitudes_bp.route('/confirmar-pago/<int:id>', methods=['POST'])
@login_required
def confirmar_pago_solicitud(id):
    """Procesar pago de solicitud"""
    solicitud = Reserva.query.get_or_404(id)
    
    if current_user.rol != 'cliente':
        flash('No tienes permiso.', 'error')
        return redirect(url_for('main.index'))
    
    cliente = current_user.get_cliente()
    if solicitud.cliente_id != cliente.id:
        flash('No tienes permiso para pagar esta solicitud.', 'error')
        return redirect(url_for('main.index'))
    
    if solicitud.estado != 'cotizada' or not solicitud.cotizacion:
        flash('Esta solicitud no está disponible para pago.', 'error')
        return redirect(url_for('solicitudes.detalle_solicitud', id=id))
    
    metodo_pago = request.form.get('metodo_pago', 'tarjeta')
    tipo_tarjeta = request.form.get('tipo_tarjeta')
    titular_tarjeta = request.form.get('titular_tarjeta')
    numero_tarjeta = request.form.get('numero_tarjeta', '').replace(' ', '').replace('-', '')
    telefono_contacto = ''
    comprobante_archivo = None
    
    if metodo_pago == 'yappy':
        telefono_contacto = request.form.get('telefono_contacto_yappy', '').strip()
        if 'comprobante_pago' not in request.files:
            flash('Debes subir el comprobante de pago.', 'error')
            return redirect(url_for('solicitudes.pagar_solicitud', id=id))
        comprobante_archivo = request.files['comprobante_pago']
        if comprobante_archivo.filename == '':
            flash('Debes seleccionar un archivo de comprobante.', 'error')
            return redirect(url_for('solicitudes.pagar_solicitud', id=id))
    else:
        telefono_contacto = request.form.get('telefono_contacto', '').strip()
        if not all([tipo_tarjeta, titular_tarjeta, numero_tarjeta]):
            flash('Completa todos los datos de pago.', 'error')
            return redirect(url_for('solicitudes.pagar_solicitud', id=id))
        
        if len(numero_tarjeta) < 13 or len(numero_tarjeta) > 19:
            flash('Número de tarjeta inválido.', 'error')
            return redirect(url_for('solicitudes.pagar_solicitud', id=id))
    
    try:
        if telefono_contacto:
            cliente.telefono = telefono_contacto
        
        codigo = generar_codigo_transaccion()
        total = solicitud.cotizacion
        subtotal = round(total / 1.07, 2)
        itbms = round(total - subtotal, 2)
        
        solicitud.metodo_pago = metodo_pago
        solicitud.tipo_tarjeta = tipo_tarjeta if metodo_pago == 'tarjeta' else None
        solicitud.titular_tarjeta = titular_tarjeta if metodo_pago == 'tarjeta' else None
        solicitud.ultimos_digitos = numero_tarjeta[-4:] if metodo_pago == 'tarjeta' and numero_tarjeta else None
        solicitud.codigo_transaccion = codigo
        solicitud.subtotal = subtotal
        solicitud.itbms = itbms
        solicitud.total_pago = total
        solicitud.estado = 'aprobada'
        
        if metodo_pago == 'yappy' and comprobante_archivo:
            ext = comprobante_archivo.filename.rsplit('.', 1)[-1].lower()
            nombre_archivo = f'comprobante_solicitud_{solicitud.id}_{codigo}.{ext}'
            ruta_upload = os.path.join(current_app.root_path, 'static', 'comprobantes', nombre_archivo)
            comprobante_archivo.save(ruta_upload)
            solicitud.comprobante_pago = nombre_archivo
            
            datos_json = {
                'id_solicitud': solicitud.id,
                'codigo_transaccion': codigo,
                'monto': total,
                'moneda': 'USD',
                'metodo_pago': 'Yappy',
                'telefono_contacto': telefono_contacto,
                'fecha_pago': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'nombre_cliente': cliente.usuario.nombre_completo,
                'email_cliente': cliente.usuario.email,
                'destino': solicitud.destino_preferido or 'Personalizado',
                'fecha_gira': solicitud.fecha_gira.strftime('%Y-%m-%d') if solicitud.fecha_gira else '',
                'numero_personas': solicitud.numero_personas,
                'comprobante': nombre_archivo
            }
            ruta_json = os.path.join(current_app.root_path, 'static', 'comprobantes', f'transaccion_solicitud_{solicitud.id}_{codigo}.json')
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(datos_json, f, ensure_ascii=False, indent=2)
            solicitud.datos_transaccion = json.dumps(datos_json, ensure_ascii=False)
        
        db.session.commit()
        
        try:
            notif = Notificacion(
                usuario_id=current_user.id,
                titulo='Solicitud pagada',
                mensaje=f'Tu solicitud #{solicitud.id} ha sido pagada. Código: {codigo}',
                tipo='solicitud_pagada',
                referencia_id=solicitud.id,
                referencia_tipo='solicitud'
            )
            db.session.add(notif)
            
            admins = Usuario.query.filter_by(rol='admin', activo=True).all()
            for admin_user in admins:
                notif_admin = Notificacion(
                    usuario_id=admin_user.id,
                    titulo='Solicitud pagada',
                    mensaje=f'El cliente {cliente.usuario.nombre_completo} ha pagado la solicitud #{solicitud.id}.',
                    tipo='solicitud_pagada',
                    referencia_id=solicitud.id,
                    referencia_tipo='solicitud'
                )
                db.session.add(notif_admin)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'Error creando notificación: {e}')
        
        flash(f'Pago procesado exitosamente. Código de transacción: {codigo}', 'success')
        return redirect(url_for('solicitudes.detalle_solicitud', id=solicitud.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar el pago: {str(e)}', 'error')
        return redirect(url_for('solicitudes.pagar_solicitud', id=id))
