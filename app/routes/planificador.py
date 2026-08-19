from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.servicio import Servicio
from app.models.cliente import Cliente
from app.models.viaje_planificado import ViajePlanificado
from app.models.recomendacion_viaje import RecomendacionViaje
from app.forms import PlanificadorForm, EXPERIENCIAS
from datetime import datetime, timedelta
from sqlalchemy import func
import json

planificador_bp = Blueprint('planificador', __name__, url_prefix='/planificador')

@planificador_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = PlanificadorForm()
    destinos = db.session.query(
        Servicio.destino,
        func.group_concat(func.distinct(Servicio.tipo_experiencia))
    ).filter(Servicio.activo == True, Servicio.destino.isnot(None), Servicio.destino != '').group_by(Servicio.destino).order_by(Servicio.destino).all()
    form.destino.choices = [('', 'Todos los destinos')] + [
        (d[0], f"{d[0]} ({d[1].replace(',', ', ')})" if d[1] else d[0]) for d in destinos if d[0]
    ]
    
    counts = dict(
        db.session.query(Servicio.tipo_experiencia, func.count(Servicio.id))
        .filter(Servicio.activo == True, Servicio.tipo_experiencia.isnot(None), Servicio.tipo_experiencia != '')
        .group_by(Servicio.tipo_experiencia).all()
    )
    form.experiencia.choices = [('', 'Selecciona una opcion')] + [
        (val, f"{label} ({counts.get(val, 0)} tours)") for val, label in EXPERIENCIAS if val
    ]
    
    dest_exp_map = {}
    for d in destinos:
        if d[0] and d[1]:
            dest_exp_map[d[0]] = d[1].split(',')[0].strip()
    
    resultados = []
    viaje = None
    
    if form.validate_on_submit():
        cliente = current_user.get_cliente()
        
        fecha_inicio = form.fecha_inicio.data
        fecha_fin = form.fecha_fin.data
        dias = (fecha_fin - fecha_inicio).days
        
        viaje = ViajePlanificado(
            cliente_id=cliente.id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            numero_personas=form.numero_personas.data,
            presupuesto=form.presupuesto.data,
            transporte_preferido=form.transporte.data,
            experiencia_buscada=form.experiencia.data,
            requiere_hospedaje=form.requiere_hospedaje.data,
            requiere_alimentacion=form.requiere_alimentacion.data,
            requiere_guia=form.requiere_guia.data,
            destino_preferido=form.destino.data,
            observaciones=form.observaciones.data,
            estado='recomendado'
        )
        db.session.add(viaje)
        db.session.commit()
        
        preferencias = {
            'transporte': form.transporte.data,
            'experiencia': form.experiencia.data,
            'presupuesto': form.presupuesto.data or 999999,
            'requiere_hospedaje': form.requiere_hospedaje.data,
            'requiere_alimentacion': form.requiere_alimentacion.data,
            'requiere_guia': form.requiere_guia.data,
            'dias': dias
        }
        
        tours = Servicio.query.filter(Servicio.activo == True).all()
        resultados = []
        
        for tour in tours:
            dias_disponibles = 0
            d = fecha_inicio
            total_dias = max(1, dias)
            while d <= fecha_fin:
                if tour.esta_disponible(d):
                    cupos = tour.get_cupos_disponibles_fecha(d)
                    if cupos >= form.numero_personas.data:
                        dias_disponibles += 1
                d += timedelta(days=1)
            
            if dias_disponibles < max(1, int(total_dias * 0.5)):
                continue
            
            if form.experiencia.data and tour.tipo_experiencia and form.experiencia.data != tour.tipo_experiencia:
                continue
            destino_match = True
            if form.destino.data and tour.destino:
                if form.destino.data.lower() not in tour.destino.lower() and form.destino.data.lower() not in (tour.nombre.lower() if tour.nombre else ''):
                    destino_match = False
            score = tour.calcular_score(preferencias)
            if not destino_match:
                score = max(1, score - 2)
            if score == 0:
                score = 1
            resultados.append((tour, score))
        
        resultados.sort(key=lambda x: x[1], reverse=True)
        
        for tour, score in resultados[:10]:
            recomendacion = RecomendacionViaje(
                viaje_planificado_id=viaje.id,
                servicio_id=tour.id,
                score=score
            )
            db.session.add(recomendacion)
        
        db.session.commit()
        
        if not resultados:
            flash('No encontramos tours que coincidan con tus preferencias. Puedes solicitar un viaje personalizado.', 'info')
            return render_template('planificador/resultados.html', 
                                 viaje=viaje, 
                                 resultados=[],
                                 mostrar_personalizado=True)
        
        flash(f'Encontramos {len(resultados)} tours recomendados para ti.', 'success')
        return render_template('planificador/resultados.html', 
                             viaje=viaje, 
                             resultados=resultados[:10],
                             mostrar_personalizado=False)
    
    return render_template('planificador/index.html', form=form, dest_exp_map=dest_exp_map)

@planificador_bp.route('/mis-viajes')
@login_required
def mis_viajes():
    cliente = current_user.get_cliente()
    
    viajes = ViajePlanificado.query.filter_by(cliente_id=cliente.id).order_by(ViajePlanificado.fecha_creacion.desc()).all()
    return render_template('planificador/mis_viajes.html', viajes=viajes)

@planificador_bp.route('/recomendaciones/<int:viaje_id>')
@login_required
def ver_recomendaciones(viaje_id):
    viaje = ViajePlanificado.query.get_or_404(viaje_id)
    
    cliente = current_user.get_cliente()
    if viaje.cliente_id != cliente.id:
        flash('No tienes permiso para ver este viaje.', 'error')
        return redirect(url_for('planificador.mis_viajes'))
    
    recomendaciones = RecomendacionViaje.query.filter_by(viaje_planificado_id=viaje.id).order_by(RecomendacionViaje.score.desc()).all()
    
    return render_template('planificador/recomendaciones.html', viaje=viaje, recomendaciones=recomendaciones)