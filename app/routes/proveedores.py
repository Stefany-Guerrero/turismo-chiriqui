from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.proveedor import Proveedor
from app.forms import ProveedorForm
from app.proveedor_especificaciones import ESPECIFICACIONES_SCHEMA, obtener_capacidad_proveedor
import json

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

@proveedores_bp.before_request
@login_required
def require_admin():
    if current_user.rol != 'admin':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.index'))

@proveedores_bp.route('/')
def index():
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    proveedores_json = [{
        'id': p.id,
        'nombre': p.nombre,
        'tipo': p.tipo or '',
        'provincia': p.provincia or '',
        'contacto': p.contacto or '',
        'telefono': p.telefono or '',
        'email': p.email or '',
        'direccion': p.direccion or '',
        'tours': [s.nombre for s in p.servicios]
    } for p in proveedores]
    return render_template('admin/proveedores/index.html', proveedores=proveedores, proveedores_json=proveedores_json)

@proveedores_bp.route('/capacidad/<int:id>')
def capacidad(id):
    proveedor = Proveedor.query.get_or_404(id)
    capacidad = obtener_capacidad_proveedor(proveedor)
    return jsonify({'capacidad': capacidad, 'tipo': proveedor.tipo})

@proveedores_bp.route('/crear', methods=['GET', 'POST'])
def crear():
    form = ProveedorForm()
    if form.validate_on_submit():
        try:
            proveedor = Proveedor(
                nombre=form.nombre.data,
                tipo=form.tipo.data,
                provincia=form.provincia.data,
                contacto=form.contacto.data,
                telefono=form.telefono.data,
                email=form.email.data,
                direccion=form.direccion.data,
                activo=form.activo.data
            )
            espec_json = request.form.get('especificaciones_json', '{}')
            try:
                espec_data = json.loads(espec_json)
            except json.JSONDecodeError:
                espec_data = {}
            proveedor.set_especificaciones(espec_data)
            db.session.add(proveedor)
            db.session.commit()
            from app.utils.audit import registrar_auditoria
            registrar_auditoria('CREAR_PROVEEDOR', 'Proveedor', proveedor.id, f'Proveedor creado: {proveedor.nombre}')
            flash('Proveedor creado exitosamente', 'success')
            return redirect(url_for('proveedores.index'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear proveedor.', 'danger')
    return render_template('admin/proveedores/crear.html', form=form, espec_schema=ESPECIFICACIONES_SCHEMA)

@proveedores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    proveedor = Proveedor.query.get_or_404(id)
    form = ProveedorForm(obj=proveedor)
    if form.validate_on_submit():
        try:
            proveedor.nombre = form.nombre.data
            proveedor.tipo = form.tipo.data
            proveedor.provincia = form.provincia.data
            proveedor.contacto = form.contacto.data
            proveedor.telefono = form.telefono.data
            proveedor.email = form.email.data
            proveedor.direccion = form.direccion.data
            proveedor.activo = form.activo.data
            espec_json = request.form.get('especificaciones_json', '{}')
            try:
                espec_data = json.loads(espec_json)
            except json.JSONDecodeError:
                espec_data = {}
            proveedor.set_especificaciones(espec_data)
            db.session.commit()
            from app.utils.audit import registrar_auditoria
            registrar_auditoria('EDITAR_PROVEEDOR', 'Proveedor', proveedor.id, f'Proveedor actualizado: {proveedor.nombre}')
            flash('Proveedor actualizado exitosamente', 'success')
            return redirect(url_for('proveedores.index'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar proveedor.', 'danger')
    return render_template('admin/proveedores/editar.html', form=form, proveedor=proveedor, espec_schema=ESPECIFICACIONES_SCHEMA, espec_data=proveedor.get_especificaciones())

@proveedores_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    proveedor = Proveedor.query.get_or_404(id)
    try:
        if proveedor.servicios:
            flash(f'No se puede eliminar: el proveedor tiene {len(proveedor.servicios)} tour(s) asociado(s)', 'danger')
            return redirect(url_for('proveedores.index'))
        nombre = proveedor.nombre
        db.session.delete(proveedor)
        db.session.commit()
        from app.utils.audit import registrar_auditoria
        registrar_auditoria('ELIMINAR_PROVEEDOR', 'Proveedor', id, f'Proveedor eliminado: {nombre}')
        flash('Proveedor eliminado', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el proveedor.', 'danger')
    return redirect(url_for('proveedores.index'))
