from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.servicio import Servicio
from app.models.proveedor import Proveedor
from app.forms import ServicioForm, DISTRITOS_POR_PROVINCIA, DESTINOS_POR_PROVINCIA
import json

servicios_bp = Blueprint('servicios', __name__, url_prefix='/servicios')

@servicios_bp.route('/')
@login_required
def index():
    if current_user.rol != 'admin':
        flash('No tienes permiso', 'error')
        return redirect(url_for('auth.dashboard'))
    
    servicios = Servicio.query.all()
    return render_template('admin/servicios/index.html', servicios=servicios)

@servicios_bp.route('/get_distritos/<provincia>')
def get_distritos(provincia):
    distritos = DISTRITOS_POR_PROVINCIA.get(provincia, [])
    return jsonify(distritos)

@servicios_bp.route('/get_destinos/<provincia>')
def get_destinos(provincia):
    destinos = DESTINOS_POR_PROVINCIA.get(provincia, [])
    return jsonify(destinos)

@servicios_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    if current_user.rol != 'admin':
        flash('No tienes permiso', 'error')
        return redirect(url_for('auth.dashboard'))
    
    form = ServicioForm()
    form.proveedor_id.choices = [(0, 'Sin proveedor')] + [(p.id, p.nombre) for p in Proveedor.query.filter_by(activo=True).all()]
    proveedores_activos = Proveedor.query.filter_by(activo=True).order_by(Proveedor.nombre).all()
    
    if request.method == 'POST':
        dias = request.form.getlist('dias_operacion')
        if dias:
            form.dias_operacion.data = [int(d) for d in dias if d.isdigit()]
        else:
            form.dias_operacion.data = []
    
    if form.validate_on_submit():
        try:
            precios_transporte = {}
            for value, label in form.transporte.choices:
                precio_key = f'transporte_precio_{value}'
                precio_val = request.form.get(precio_key, '0')
                try:
                    p = float(precio_val)
                    if p >= 0 and value in form.transporte.data:
                        precios_transporte[value] = p
                except (ValueError, TypeError):
                    pass
            
            servicio = Servicio(
                codigo=form.codigo.data or form.generate_codigo(),
                nombre=form.nombre.data,
                categoria=form.tipo_experiencia.data,
                provincia=form.provincia.data,
                distrito=form.distrito.data,
                destino=form.destino.data,
                punto_salida=form.punto_salida.data,
                punto_llegada=form.punto_llegada.data,
                descripcion=form.descripcion.data,
                duracion_cantidad=form.duracion_cantidad.data,
                duracion_unidad=form.duracion_unidad.data,
                hora_inicio=form.hora_inicio.data,
                hora_estimada_regreso=form.hora_estimada_regreso.data,
                precio=form.precio.data,
                cupo_maximo=form.cupo_maximo.data,
                cupos_disponibles=form.cupo_maximo.data,
                imagen=form.imagen.data,
                itinerario=form.itinerario.data,
                incluye=form.incluye.data,
                no_incluye=form.no_incluye.data,
                recomendaciones=form.recomendaciones.data,
                incluye_transporte=form.incluye_transporte.data,
                incluye_alimentacion=form.incluye_alimentacion.data,
                incluye_hospedaje=form.incluye_hospedaje.data,
                incluye_guia=form.incluye_guia.data,
                incluye_seguro=form.incluye_seguro.data,
                incluye_entradas=form.incluye_entradas.data,
                incluye_equipo=form.incluye_equipo.data,
                proveedor_id=form.proveedor_id.data if form.proveedor_id.data != 0 else None,
                activo=form.activo.data,
                transporte=form.get_transporte_as_string() or None,
                transporte_precios=json.dumps(precios_transporte),
                tipo_experiencia=form.tipo_experiencia.data,
                duracion_recomendada=form.duracion_recomendada.data,
                tipo_programacion=form.tipo_programacion.data,
                fecha_unica=form.fecha_unica.data,
                vigencia_inicio=form.vigencia_inicio.data,
                vigencia_fin=form.vigencia_fin.data,
                dias_operacion=','.join(str(d) for d in form.dias_operacion.data) if form.dias_operacion.data else None
            )
            db.session.add(servicio)
            db.session.flush()
            
            proveedor_ids = request.form.getlist('tour_proveedor_id')
            proveedor_roles = request.form.getlist('tour_proveedor_rol')
            for pid, rol in zip(proveedor_ids, proveedor_roles):
                if pid and pid.strip() and rol and rol.strip():
                    from app.models.proveedor import TourProveedor
                    tp = TourProveedor(
                        servicio_id=servicio.id,
                        proveedor_id=int(pid),
                        rol=rol.strip()
                    )
                    db.session.add(tp)
            
            db.session.commit()
            flash('Tour creado exitosamente', 'success')
            return redirect(url_for('servicios.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el tour: {str(e)}', 'error')
    
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    distritos_json = json.dumps(DISTRITOS_POR_PROVINCIA)
    destinos_json = json.dumps(DESTINOS_POR_PROVINCIA)
    
    from app.models.proveedor import TourProveedor
    
    return render_template('admin/servicios/crear.html', 
                         form=form, 
                         distritos_json=distritos_json, 
                         destinos_json=destinos_json,
                         provincia_seleccionada=form.provincia.data,
                         distrito_seleccionado=form.distrito.data,
                         destino_seleccionado=form.destino.data,
                         transporte_precios={},
                         proveedores_activos=proveedores_activos,
                         roles_proveedor=TourProveedor.ROLES,
                         roles_descripcion=TourProveedor.ROLES_DESCRIPCION)

@servicios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    if current_user.rol != 'admin':
        flash('No tienes permiso', 'error')
        return redirect(url_for('auth.dashboard'))
    
    servicio = Servicio.query.get_or_404(id)
    form = ServicioForm(obj=servicio)
    form.proveedor_id.choices = [(0, 'Sin proveedor')] + [(p.id, p.nombre) for p in Proveedor.query.filter_by(activo=True).all()]
    proveedores_activos = Proveedor.query.filter_by(activo=True).order_by(Proveedor.nombre).all()
    
    if request.method == 'POST':
        dias_submit = request.form.getlist('dias_operacion')
        if dias_submit:
            form.dias_operacion.data = [int(d) for d in dias_submit if d.isdigit()]
        else:
            form.dias_operacion.data = []
        
        transporte_submit = request.form.getlist('transporte')
        form.transporte.data = transporte_submit if transporte_submit else []
    else:
        if servicio.dias_operacion:
            if isinstance(servicio.dias_operacion, str):
                try:
                    form.dias_operacion.data = [int(d.strip()) for d in servicio.dias_operacion.split(',') if d.strip().isdigit()]
                except Exception:
                    form.dias_operacion.data = []
            elif isinstance(servicio.dias_operacion, list):
                form.dias_operacion.data = servicio.dias_operacion
            else:
                form.dias_operacion.data = []
        else:
            form.dias_operacion.data = []
        
        if servicio.transporte:
            if isinstance(servicio.transporte, str):
                form.transporte.data = [t.strip() for t in servicio.transporte.split(',') if t.strip()]
            elif isinstance(servicio.transporte, list):
                form.transporte.data = servicio.transporte
            else:
                form.transporte.data = []
        else:
            form.transporte.data = []
    
    if form.validate_on_submit():
        try:
            from sqlalchemy import text
            from app.models.proveedor import TourProveedor
            
            precios_transporte = {}
            for value, label in form.transporte.choices:
                precio_key = f'transporte_precio_{value}'
                precio_val = request.form.get(precio_key, '0')
                try:
                    p = float(precio_val)
                    if p >= 0 and value in form.transporte.data:
                        precios_transporte[value] = p
                except (ValueError, TypeError):
                    pass
            
            servicio.codigo = form.codigo.data
            servicio.nombre = form.nombre.data
            servicio.categoria = form.tipo_experiencia.data
            servicio.provincia = form.provincia.data
            servicio.distrito = form.distrito.data
            servicio.destino = form.destino.data
            servicio.punto_salida = form.punto_salida.data
            servicio.punto_llegada = form.punto_llegada.data
            servicio.descripcion = form.descripcion.data
            servicio.duracion_cantidad = form.duracion_cantidad.data
            servicio.duracion_unidad = form.duracion_unidad.data
            servicio.hora_inicio = form.hora_inicio.data
            servicio.hora_estimada_regreso = form.hora_estimada_regreso.data
            servicio.precio = form.precio.data
            servicio.cupo_maximo = form.cupo_maximo.data
            servicio.imagen = form.imagen.data
            servicio.itinerario = form.itinerario.data
            servicio.incluye = form.incluye.data
            servicio.no_incluye = form.no_incluye.data
            servicio.recomendaciones = form.recomendaciones.data
            servicio.incluye_transporte = form.incluye_transporte.data
            servicio.incluye_alimentacion = form.incluye_alimentacion.data
            servicio.incluye_hospedaje = form.incluye_hospedaje.data
            servicio.incluye_guia = form.incluye_guia.data
            servicio.incluye_seguro = form.incluye_seguro.data
            servicio.incluye_entradas = form.incluye_entradas.data
            servicio.incluye_equipo = form.incluye_equipo.data
            servicio.proveedor_id = form.proveedor_id.data if form.proveedor_id.data != 0 else None
            servicio.activo = form.activo.data
            servicio.transporte = form.get_transporte_as_string() or None
            servicio.transporte_precios = json.dumps(precios_transporte)
            servicio.tipo_experiencia = form.tipo_experiencia.data
            servicio.duracion_recomendada = form.duracion_recomendada.data
            servicio.tipo_programacion = form.tipo_programacion.data
            servicio.fecha_unica = form.fecha_unica.data
            servicio.vigencia_inicio = form.vigencia_inicio.data
            servicio.vigencia_fin = form.vigencia_fin.data
            
            # === SOLUCIÓN DEFINITIVA PARA días_operacion ===
            if form.dias_operacion.data and isinstance(form.dias_operacion.data, list):
                dias_str = ','.join(str(d) for d in form.dias_operacion.data)
            else:
                dias_str = None
            
            db.session.execute(
                text("UPDATE servicios SET dias_operacion = :dias WHERE id = :id"),
                {"dias": dias_str, "id": servicio.id}
            )
            
            TourProveedor.query.filter_by(servicio_id=servicio.id).delete()
            
            proveedor_ids = request.form.getlist('tour_proveedor_id')
            proveedor_roles = request.form.getlist('tour_proveedor_rol')
            for pid, rol in zip(proveedor_ids, proveedor_roles):
                if pid and pid.strip() and rol and rol.strip():
                    tp = TourProveedor(
                        servicio_id=servicio.id,
                        proveedor_id=int(pid),
                        rol=rol.strip()
                    )
                    db.session.add(tp)
            
            db.session.commit()
            flash('Tour actualizado exitosamente', 'success')
            return redirect(url_for('servicios.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el tour: {str(e)}', 'error')
    
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    distritos_json = json.dumps(DISTRITOS_POR_PROVINCIA)
    destinos_json = json.dumps(DESTINOS_POR_PROVINCIA)
    
    from app.models.proveedor import TourProveedor
    proveedores_tour = TourProveedor.query.filter_by(servicio_id=servicio.id).all()
    
    return render_template('admin/servicios/editar.html', 
                         form=form, 
                         servicio=servicio,
                         distritos_json=distritos_json, 
                         destinos_json=destinos_json,
                         provincia_seleccionada=form.provincia.data,
                         distrito_seleccionado=form.distrito.data,
                         destino_seleccionado=form.destino.data,
                         transporte_precios=servicio.get_transporte_precios(),
                         proveedores_activos=proveedores_activos,
                         roles_proveedor=TourProveedor.ROLES,
                         roles_descripcion=TourProveedor.ROLES_DESCRIPCION,
                         proveedores_tour=proveedores_tour)

@servicios_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    if current_user.rol != 'admin':
        flash('No tienes permiso', 'error')
        return redirect(url_for('auth.dashboard'))
    
    servicio = Servicio.query.get_or_404(id)
    
    if servicio.reservas and servicio.reservas.count() > 0:
        flash('No se puede eliminar el tour porque tiene reservas asociadas.', 'error')
        return redirect(url_for('servicios.index'))
    
    try:
        db.session.delete(servicio)
        db.session.commit()
        flash('Tour eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el tour: {str(e)}', 'error')
    
    return redirect(url_for('servicios.index'))