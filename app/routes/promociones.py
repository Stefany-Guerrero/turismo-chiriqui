from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.promocion import Promocion
from app.models.servicio import Servicio
from app.forms import PromocionForm
from datetime import datetime
import random
import string

promociones_bp = Blueprint('promociones', __name__, url_prefix='/promociones')

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            flash('Acceso denegado', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@promociones_bp.route('/')
@login_required
@admin_required
def index():
    promociones = Promocion.query.order_by(Promocion.fecha_creacion.desc()).all()
    now = datetime.now()
    return render_template('admin/promociones/index.html', promociones=promociones, now=now)

@promociones_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear():
    form = PromocionForm()
    servicios = Servicio.query.filter_by(activo=True).all()
    form.servicio_id.choices = [('', 'Seleccione un tour')] + [(s.id, s.nombre) for s in servicios]
    tours_data = [{'id': s.id, 'nombre': s.nombre, 'precio': s.precio, 'proveedor': s.proveedor.nombre if s.proveedor else ''} for s in servicios]
    
    if not form.codigo.data and request.method == 'GET':
        while True:
            codigo = 'PROMO-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Promocion.query.filter_by(codigo=codigo).first():
                break
        form.codigo.data = codigo
    
    if form.validate_on_submit():
        try:
            existing = Promocion.query.filter_by(codigo=form.codigo.data.upper()).first()
            if existing:
                flash('El codigo ya existe', 'danger')
                return render_template('admin/promociones/crear.html', form=form, tours_data=tours_data)
            
            promocion = Promocion(
                nombre=form.nombre.data,
                descripcion=form.descripcion.data,
                codigo=form.codigo.data.upper(),
                tipo=form.tipo.data,
                valor=form.valor.data,
                fecha_inicio=form.fecha_inicio.data,
                fecha_fin=form.fecha_fin.data,
                activa=form.activa.data,
                uso_maximo=form.uso_maximo.data,
                servicio_id=form.servicio_id.data,
                imagen=form.imagen.data
            )
            db.session.add(promocion)
            db.session.commit()
            from app.utils.audit import registrar_auditoria
            registrar_auditoria('CREAR_PROMOCION', 'Promocion', promocion.id, f'Promoción creada: {promocion.nombre} ({promocion.codigo})')
            flash('Promocion creada', 'success')
            return redirect(url_for('promociones.index'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear la promoción.', 'danger')
    
    return render_template('admin/promociones/crear.html', form=form, tours_data=tours_data)

@promociones_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    promocion = Promocion.query.get_or_404(id)
    form = PromocionForm(obj=promocion)
    from sqlalchemy import or_
    servicios = Servicio.query.filter(
        or_(Servicio.activo == True, Servicio.id == promocion.servicio_id)
    ).all()
    form.servicio_id.choices = [('', 'Seleccione un tour')] + [(s.id, s.nombre) for s in servicios]
    tours_data = [{'id': s.id, 'nombre': s.nombre, 'precio': s.precio, 'proveedor': s.proveedor.nombre if s.proveedor else ''} for s in servicios]
    
    if form.validate_on_submit():
        try:
            existing = Promocion.query.filter(Promocion.codigo == form.codigo.data.upper(), Promocion.id != id).first()
            if existing:
                flash('El codigo ya existe', 'danger')
                return render_template('admin/promociones/editar.html', form=form, promocion=promocion, tours_data=tours_data)
            
            promocion.nombre = form.nombre.data
            promocion.descripcion = form.descripcion.data
            promocion.codigo = form.codigo.data.upper()
            promocion.tipo = form.tipo.data
            promocion.valor = form.valor.data
            promocion.fecha_inicio = form.fecha_inicio.data
            promocion.fecha_fin = form.fecha_fin.data
            promocion.activa = form.activa.data
            promocion.uso_maximo = form.uso_maximo.data
            promocion.servicio_id = form.servicio_id.data
            promocion.imagen = form.imagen.data
            db.session.commit()
            from app.utils.audit import registrar_auditoria
            registrar_auditoria('EDITAR_PROMOCION', 'Promocion', promocion.id, f'Promoción actualizada: {promocion.nombre} ({promocion.codigo})')
            flash('Promocion actualizada', 'success')
            return redirect(url_for('promociones.index'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar la promoción.', 'danger')
    
    return render_template('admin/promociones/editar.html', form=form, promocion=promocion, tours_data=tours_data)

@promociones_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar(id):
    promocion = Promocion.query.get_or_404(id)
    try:
        nombre = promocion.nombre
        db.session.delete(promocion)
        db.session.commit()
        from app.utils.audit import registrar_auditoria
        registrar_auditoria('ELIMINAR_PROMOCION', 'Promocion', id, f'Promoción eliminada: {nombre}')
        flash('Promocion eliminada', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar la promoción.', 'danger')
    return redirect(url_for('promociones.index'))

@promociones_bp.route('/cambiar-estado/<int:id>', methods=['POST'])
@login_required
@admin_required
def cambiar_estado(id):
    promocion = Promocion.query.get_or_404(id)
    try:
        promocion.activa = not promocion.activa
        db.session.commit()
        from app.utils.audit import registrar_auditoria
        registrar_auditoria('CAMBIAR_ESTADO_PROMOCION', 'Promocion', promocion.id, f'Estado promoción "{promocion.nombre}": {"activa" if promocion.activa else "inactiva"}')
        flash('Estado cambiado', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al cambiar el estado.', 'danger')
    return redirect(url_for('promociones.index'))

@promociones_bp.route('/api/validar', methods=['POST'])
def api_validar():
    data = request.get_json()
    codigo = data.get('codigo', '').upper()
    promocion = Promocion.query.filter_by(codigo=codigo).first()
    if not promocion:
        return jsonify({'valido': False, 'mensaje': 'Codigo invalido'})
    if not promocion.esta_vigente():
        return jsonify({'valido': False, 'mensaje': 'Promocion no vigente'})
    if promocion.uso_maximo > 0 and promocion.usos_actuales >= promocion.uso_maximo:
        return jsonify({'valido': False, 'mensaje': 'Promocion agotada'})
    return jsonify({
        'valido': True,
        'mensaje': 'Codigo valido',
        'promocion': {
            'id': promocion.id,
            'nombre': promocion.nombre,
            'tipo': promocion.tipo,
            'valor': promocion.valor,
            'descripcion': promocion.descripcion
        }
    })