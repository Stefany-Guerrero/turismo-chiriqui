from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.reserva import Reserva
from sqlalchemy import desc

transacciones_bp = Blueprint('transacciones', __name__, url_prefix='/transacciones')


def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            flash('Acceso denegado', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@transacciones_bp.route('/')
@login_required
@admin_required
def index():
    filtro = request.args.get('filtro', 'todas')
    
    query = Reserva.query.filter(Reserva.codigo_transaccion.isnot(None))
    
    if filtro == 'pagadas':
        query = query.filter(Reserva.estado == 'confirmada')
    elif filtro == 'pendientes':
        query = query.filter(Reserva.estado == 'pendiente_pago')
    elif filtro == 'canceladas':
        query = query.filter(Reserva.estado == 'cancelada')
    
    transacciones = query.order_by(desc(Reserva.fecha_creacion)).all()
    
    total_monto = sum(t.total_pago or 0 for t in transacciones if t.estado == 'confirmada')
    
    return render_template('admin/transacciones/index.html',
                         transacciones=transacciones,
                         filtro=filtro,
                         total_monto=total_monto)


@transacciones_bp.route('/detalle/<int:id>')
@login_required
@admin_required
def detalle(id):
    reserva = Reserva.query.get_or_404(id)
    datos = None
    if reserva.datos_transaccion:
        import json
        try:
            datos = json.dumps(json.loads(reserva.datos_transaccion), indent=2, ensure_ascii=False)
        except Exception:
            datos = None
    return render_template('admin/transacciones/detalle.html',
                         reserva=reserva,
                         datos=datos)
