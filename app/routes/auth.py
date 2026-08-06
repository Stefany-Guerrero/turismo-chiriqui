from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app import db, mail
from app.models.usuario import Usuario
import logging

logger = logging.getLogger(__name__)

from app.forms import LoginForm, RegisterForm, ResetPasswordForm, VerifyCodeForm, NewPasswordForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.rol == 'admin':
            return redirect(url_for('auth.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        if usuario and usuario.check_password(form.password.data):
            if not usuario.activo:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'error')
                return render_template('auth/login.html', form=form)
            
            login_user(usuario, remember=form.remember_me.data)
            flash(f'¡Bienvenido {usuario.nombre_completo}!', 'success')
            
            next_page = request.args.get('next')
            
            if usuario.rol == 'admin':
                return redirect(next_page) if next_page else redirect(url_for('auth.dashboard'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Correo electrónico o contraseña incorrectos.', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.rol == 'admin':
            return redirect(url_for('auth.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        usuario = Usuario(
            username=form.username.data,
            email=form.email.data,
            nombre_completo=form.nombre_completo.data,
            telefono=form.telefono.data,
            rol='cliente'
        )
        usuario.set_password(form.password.data)
        
        db.session.add(usuario)
        db.session.flush()
        
        from app.models.cliente import Cliente
        cliente = Cliente(
            nombre=usuario.nombre_completo,
            email=usuario.email,
            telefono=usuario.telefono,
            usuario_id=usuario.id
        )
        db.session.add(cliente)
        db.session.commit()
        
        try:
            send_welcome_email(usuario)
            flash('¡Cuenta creada exitosamente! Revisa tu correo de bienvenida.', 'success')
        except Exception as e:
            flash('¡Cuenta creada exitosamente! No pudimos enviar el correo de bienvenida, pero ya puedes iniciar sesión.', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        if current_user.rol == 'admin':
            return redirect(url_for('auth.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario:
            codigo = usuario.generar_token_reset()
            try:
                send_reset_email(usuario, codigo)
                session['reset_email'] = usuario.email
                flash('Te hemos enviado un código de verificación a tu correo.', 'success')
                return redirect(url_for('auth.verify_code'))
            except Exception as e:
                flash('Error al enviar el código. Intenta nuevamente.', 'error')
        else:
            flash('No existe una cuenta con este correo electrónico.', 'error')
    
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    if current_user.is_authenticated:
        if current_user.rol == 'admin':
            return redirect(url_for('auth.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    if 'reset_email' not in session:
        flash('Por favor, solicita primero la recuperación de contraseña.', 'warning')
        return redirect(url_for('auth.reset_password'))
    
    form = VerifyCodeForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=session['reset_email']).first()
        if usuario and usuario.verificar_token_reset(form.codigo.data):
            session['reset_verified'] = True
            flash('Código verificado correctamente. Ahora puedes cambiar tu contraseña.', 'success')
            return redirect(url_for('auth.new_password'))
        else:
            flash('Código inválido o expirado.', 'error')
    
    return render_template('auth/verify_code.html', form=form)


@auth_bp.route('/new-password', methods=['GET', 'POST'])
def new_password():
    if current_user.is_authenticated:
        if current_user.rol == 'admin':
            return redirect(url_for('auth.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    if not session.get('reset_verified'):
        flash('Por favor, verifica tu identidad primero.', 'warning')
        return redirect(url_for('auth.reset_password'))
    
    form = NewPasswordForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=session['reset_email']).first()
        if usuario:
            usuario.set_password(form.new_password.data)
            usuario.reset_token = None
            usuario.reset_token_expira = None
            db.session.commit()
            
            session.pop('reset_email', None)
            session.pop('reset_verified', None)
            
            flash('¡Contraseña actualizada exitosamente!', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/new_password.html', form=form)


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol != 'admin':
        flash('No tienes permiso para acceder.', 'error')
        return redirect(url_for('main.index'))
    
    from app.models.servicio import Servicio
    from app.models.reserva import Reserva
    from app.models.cliente import Cliente
    total_tours = Servicio.query.count()
    total_reservas = Reserva.query.filter_by(estado='confirmada').count()
    reservas_pendientes = Reserva.query.filter_by(estado='pendiente').count()
    total_clientes = Cliente.query.count()
    
    total_pagos = db.session.query(db.func.coalesce(db.func.sum(Reserva.total_pago), 0)).filter(
        Reserva.estado == 'confirmada'
    ).scalar()
    
    ultimas_reservas = Reserva.query.filter_by(estado='confirmada').order_by(Reserva.fecha_creacion.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         total_tours=total_tours,
                         total_reservas=total_reservas,
                         reservas_pendientes=reservas_pendientes,
                         total_clientes=total_clientes,
                         total_pagos=total_pagos,
                         ultimas_reservas=ultimas_reservas)


@auth_bp.route('/clientes')
@login_required
def clientes():
    if current_user.rol != 'admin':
        flash('No tienes permiso para acceder.', 'error')
        return redirect(url_for('main.index'))
    
    from app.models.cliente import Cliente
    clientes = Cliente.query.order_by(Cliente.fecha_creacion.desc()).all()
    return render_template('admin/clientes.html', clientes=clientes)


@auth_bp.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    if current_user.rol != 'admin':
        flash('No tienes permiso.', 'error')
        return redirect(url_for('main.index'))
    
    from app.models.cliente import Cliente
    from app.forms import ClienteForm
    cliente = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=cliente)
    
    if form.validate_on_submit():
        try:
            cliente.nombre = form.nombre.data
            cliente.email = form.email.data
            cliente.telefono = form.telefono.data
            if cliente.usuario:
                cliente.usuario.activo = form.activo.data
            db.session.commit()
            flash('Cliente actualizado correctamente.', 'success')
            return redirect(url_for('auth.clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('admin/clientes_editar.html', form=form, cliente=cliente)


@auth_bp.route('/clientes/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_cliente(id):
    if current_user.rol != 'admin':
        flash('No tienes permiso.', 'error')
        return redirect(url_for('main.index'))
    
    from app.models.cliente import Cliente
    cliente = Cliente.query.get_or_404(id)
    try:
        if cliente.reservas:
            flash('No se puede eliminar: el cliente tiene reservas activas.', 'danger')
            return redirect(url_for('auth.clientes'))
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('auth.clientes'))


def send_welcome_email(usuario):
    try:
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        msg = Message(
            subject='Bienvenido a Turismo Chiriqui',
            recipients=[usuario.email]
        )
        html_content = render_template(
            'emails/bienvenida.html',
            nombre=usuario.nombre_completo,
            username=usuario.username,
            email=usuario.email
        )
        msg.html = html_content
        mail.send(msg)
    except Exception as e:
        logger.error(f'Error enviando correo de bienvenida: {e}')


def send_reset_email(usuario, codigo):
    try:
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        msg = Message(
            subject='Recuperacion de Contrasena - Turismo Chiriqui',
            recipients=[usuario.email]
        )
        html_content = render_template(
            'emails/recuperacion.html',
            nombre=usuario.nombre_completo,
            codigo=codigo,
            link=f'{base_url}/auth/reset-password'
        )
        msg.html = html_content
        mail.send(msg)
    except Exception as e:
        logger.error(f'Error enviando correo de reset: {e}')