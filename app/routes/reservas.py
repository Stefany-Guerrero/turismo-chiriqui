from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
from app.models.reserva import Reserva
from app.models.servicio import Servicio
from app.models.cliente import Cliente
from app.forms import ReservaForm
from datetime import datetime

reservas_bp = Blueprint('reservas', __name__, url_prefix='/reservas')

@reservas_bp.route('/')
@login_required
def index():
    tipo_filtro = request.args.get('tipo', 'todas')
    
    if current_user.rol == 'admin':
        query = Reserva.query
        if tipo_filtro == 'reserva':
            query = query.filter_by(tipo='reserva')
        elif tipo_filtro == 'solicitud':
            query = query.filter_by(tipo='solicitud')
        reservas = query.order_by(Reserva.fecha_creacion.desc()).all()
        Reserva.query.filter_by(tipo='solicitud', leido=False).update({'leido': True})
        db.session.commit()
    else:
        cliente = current_user.get_cliente()
        query = Reserva.query.filter_by(cliente_id=cliente.id)
        if tipo_filtro == 'reserva':
            query = query.filter_by(tipo='reserva')
        elif tipo_filtro == 'solicitud':
            query = query.filter_by(tipo='solicitud')
        reservas = query.order_by(Reserva.fecha_creacion.desc()).all()
    
    return render_template('reservas/index.html', reservas=reservas, tipo_filtro=tipo_filtro)

@reservas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    if current_user.rol != 'admin':
        flash('No tienes permiso para acceder.', 'error')
        return redirect(url_for('auth.dashboard'))
    
    form = ReservaForm()
    form.cliente_id.choices = [('', 'Seleccione un cliente')] + [(c.id, c.nombre) for c in Cliente.query.all()]
    form.servicio_id.choices = [('', 'Seleccione un tour')] + [(s.id, f"{s.nombre} - ${s.precio}") for s in Servicio.query.filter_by(activo=True).all()]
    
    if form.validate_on_submit():
        reserva = Reserva(
            cliente_id=form.cliente_id.data,
            servicio_id=form.servicio_id.data,
            fecha_gira=form.fecha_gira.data,
            numero_personas=form.numero_personas.data,
            total_pago=form.total_pago.data,
            observaciones=form.observaciones.data
        )
        db.session.add(reserva)
        db.session.commit()
        flash('Reserva creada exitosamente.', 'success')
        return redirect(url_for('reservas.index'))
    
    return render_template('reservas/crear.html', form=form,
                           sin_clientes=Cliente.query.count() == 0,
                           sin_servicios=Servicio.query.filter_by(activo=True).count() == 0)

@reservas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    if current_user.rol != 'admin':
        flash('No tienes permiso para acceder.', 'error')
        return redirect(url_for('auth.dashboard'))
    
    reserva = Reserva.query.get_or_404(id)
    form = ReservaForm(obj=reserva)
    form.cliente_id.choices = [(c.id, c.nombre) for c in Cliente.query.all()]
    from sqlalchemy import or_
    servicios = Servicio.query.filter(
        or_(Servicio.activo == True, Servicio.id == reserva.servicio_id)
    ).all()
    form.servicio_id.choices = [(s.id, f"{s.nombre} - ${s.precio}") for s in servicios]
    
    if form.validate_on_submit():
        reserva.cliente_id = form.cliente_id.data
        reserva.servicio_id = form.servicio_id.data
        reserva.fecha_gira = form.fecha_gira.data
        reserva.numero_personas = form.numero_personas.data
        reserva.total_pago = form.total_pago.data
        reserva.observaciones = form.observaciones.data
        db.session.commit()
        flash('Reserva actualizada exitosamente.', 'success')
        return redirect(url_for('reservas.index'))
    
    return render_template('reservas/editar.html', form=form, reserva=reserva,
                           sin_clientes=Cliente.query.count() == 0,
                           sin_servicios=Servicio.query.filter_by(activo=True).count() == 0)

@reservas_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    if current_user.rol != 'admin':
        flash('No tienes permiso para acceder.', 'error')
        return redirect(url_for('auth.dashboard'))
    
    reserva = Reserva.query.get_or_404(id)
    db.session.delete(reserva)
    db.session.commit()
    flash('Reserva eliminada exitosamente.', 'success')
    return redirect(url_for('reservas.index'))

@reservas_bp.route('/cancelar/<int:id>', methods=['POST'])
@login_required
def cancelar(id):
    reserva = Reserva.query.get_or_404(id)
    
    if current_user.rol != 'admin':
        cliente = current_user.get_cliente()
        if reserva.cliente_id != cliente.id:
            flash('No tienes permiso para cancelar esta reserva.', 'error')
            return redirect(url_for('reservas.index'))
    
    if reserva.estado == 'cancelada':
        flash('Esta reserva ya está cancelada.', 'warning')
        return redirect(url_for('reservas.index'))
    
    reserva.estado = 'cancelada'
    db.session.commit()
    from app.utils.audit import registrar_auditoria
    registrar_auditoria('CANCELAR_RESERVA', 'Reserva', reserva.id, f'Reserva #{reserva.id} cancelada')
    flash('Reserva cancelada exitosamente.', 'success')
    return redirect(url_for('reservas.index'))

@reservas_bp.route('/detalle-pago', methods=['GET', 'POST'])
@login_required
def detalle_pago():
    if request.method == 'POST':
        rid = request.form.get('reserva_id', type=int)
        if rid:
            session['detalle_reserva_id'] = rid
        return redirect(url_for('reservas.detalle_pago'))
    reserva_id = session.get('detalle_reserva_id')
    if not reserva_id:
        flash('No hay reserva seleccionada.', 'error')
        return redirect(url_for('main.mis_reservas'))
    reserva = db.session.get(Reserva, reserva_id)
    if not reserva:
        flash('Reserva no encontrada.', 'error')
        return redirect(url_for('main.mis_reservas'))
    if current_user.rol == 'cliente':
        cliente = current_user.get_cliente()
        if reserva.cliente_id != cliente.id:
            flash('No tienes permiso para acceder.', 'error')
            return redirect(url_for('main.index'))
    reserva.servicio.promocion_activa = reserva.servicio.get_promocion_activa() if reserva.servicio else None
    if current_user.rol == 'admin':
        return render_template('reservas/detalle_pago_admin.html', reserva=reserva)
    return render_template('reservas/detalle_pago.html', reserva=reserva)

@reservas_bp.route('/imprimir')
@login_required
def imprimir():
    reserva_id = session.get('detalle_reserva_id')
    if not reserva_id:
        flash('No hay reserva seleccionada.', 'error')
        return redirect(url_for('main.mis_reservas'))
    reserva = db.session.get(Reserva, reserva_id)
    if not reserva:
        flash('Reserva no encontrada.', 'error')
        return redirect(url_for('main.mis_reservas'))
    if current_user.rol == 'cliente':
        cliente = current_user.get_cliente()
        if reserva.cliente_id != cliente.id:
            flash('No tienes permiso para acceder.', 'error')
            return redirect(url_for('main.index'))
    return render_template('reservas/imprimir.html', reserva=reserva)

@reservas_bp.route('/cambiar-estado/<int:id>/<estado>', methods=['POST'])
@login_required
def cambiar_estado(id, estado):
    if current_user.rol != 'admin':
        flash('No tienes permiso para acceder.', 'error')
        return redirect(url_for('auth.dashboard'))
    
    reserva = Reserva.query.get_or_404(id)
    estados_validos = ['pendiente', 'confirmada', 'cancelada', 'completada']
    
    if estado in estados_validos:
        reserva.estado = estado
        db.session.commit()
        from app.utils.audit import registrar_auditoria
        registrar_auditoria('CAMBIAR_ESTADO_RESERVA', 'Reserva', reserva.id, f'Reserva #{reserva.id}: estado -> {estado}')
        flash(f'Estado cambiado a {estado}.', 'success')
    else:
        flash('Estado no válido.', 'error')
    
    return redirect(url_for('reservas.index'))