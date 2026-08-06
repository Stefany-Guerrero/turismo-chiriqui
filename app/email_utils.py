from flask import current_app, render_template
from flask_mail import Message
from app import mail
from datetime import datetime
import io
import os
import logging

logger = logging.getLogger(__name__)


def generar_pdf_factura(reserva):
    logo_url = 'file:///' + os.path.join(current_app.root_path, 'static', 'img', 'logo.png').replace('\\', '/')
    html = render_template('reservas/factura_pdf.html', reserva=reserva, logo_url=logo_url)
    try:
        from xhtml2pdf import pisa
        buf = io.BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=buf, encoding='utf-8')
        if pisa_status.err:
            logger.error(f'Error generando PDF: {pisa_status.err}')
            return None
        return buf.getvalue()
    except Exception as e:
        logger.error(f'Error generando PDF: {e}')
        return None


def send_reservation_email(cliente, reserva):
    try:
        servicio = reserva.servicio

        msg = Message(
            subject='Reserva confirmada - Turismo Chiriqui',
            recipients=[cliente.usuario.email]
        )

        pdf_data = generar_pdf_factura(reserva)
        if pdf_data:
            msg.attach('factura-turismo-chiriqui.pdf', 'application/pdf', pdf_data)

        if reserva.metodo_pago == 'yappy' and reserva.comprobante_pago:
            ruta = os.path.join(current_app.root_path, 'static', 'comprobantes', reserva.comprobante_pago)
            if os.path.exists(ruta):
                with open(ruta, 'rb') as f:
                    msg.attach(reserva.comprobante_pago, 'image/png' if reserva.comprobante_pago.endswith('.png') else 'image/jpeg', f.read())

        transporte_info = ''
        if reserva.transporte and reserva.transporte not in ('no_requiere', ''):
            t_label = {'vehiculo_propio': 'Vehiculo propio', 'autobus': 'Autobus', 'transporte_empresa': 'Transporte del proveedor', 'avion': 'Avion', 'lancha': 'Lancha', 'alquiler_auto': 'Alquiler de auto'}.get(reserva.transporte, reserva.transporte)
            if servicio and servicio.get_precio_transporte(reserva.transporte) > 0:
                transporte_info = f'Transporte: {t_label} (+B/.{servicio.get_precio_transporte(reserva.transporte):.2f} por persona)'
            elif servicio and servicio.incluye_transporte:
                transporte_info = f'Transporte: {t_label} (Incluido en el tour)'
            else:
                transporte_info = f'Transporte: {t_label} (Sin costo)'
        elif servicio and servicio.incluye_transporte:
            transporte_info = 'Transporte incluido en el tour'

        html_content = render_template(
            'emails/confirmacion_reserva.html',
            nombre=cliente.usuario.nombre_completo,
            reserva_id=reserva.id if reserva.id else '',
            transaccion=reserva.codigo_transaccion or '',
            tour=servicio.nombre if servicio else 'Tour',
            tour_categoria=servicio.categoria_nombre if servicio else '',
            tour_imagen=servicio.imagen if servicio else '',
            incluye_tour=servicio.incluye if servicio else '',
            transporte_info=transporte_info,
            fecha=reserva.fecha_gira.strftime('%d/%m/%Y') if reserva.fecha_gira else '—',
            fecha_fin=reserva.fecha_fin.strftime('%d/%m/%Y') if reserva.fecha_fin else '',
            personas=reserva.numero_personas,
            subtotal=f'B/.{reserva.subtotal:.2f}' if reserva.subtotal else '',
            itbms=f'B/.{reserva.itbms:.2f}' if reserva.itbms else '',
            total=f'B/.{reserva.total_pago:.2f}',
            tipo_tarjeta=reserva.tipo_tarjeta or '',
            ultimos_digitos=reserva.ultimos_digitos or '',
            cliente_email=cliente.usuario.email,
            cliente_telefono=cliente.telefono or '',
            fecha_actual=datetime.now().strftime('%d/%m/%Y'),
            metodo_pago=reserva.metodo_pago,
            comprobante_pago=reserva.comprobante_pago
        )
        msg.html = html_content
        mail.send(msg)
    except Exception as e:
        logger.error(f'Error enviando correo de reserva: {e}')


def send_admin_new_reservation(cliente, reserva):
    try:
        link = f'{current_app.config.get("BASE_URL", "http://localhost:5000")}/reservas'
        admin_email = current_app.config.get('ADMIN_EMAIL', 'itsdanhw14@gmail.com')

        servicio = reserva.servicio

        msg = Message(
            subject=f'Nueva reserva #{reserva.id} - {cliente.usuario.nombre_completo}',
            recipients=[admin_email]
        )

        pdf_data = generar_pdf_factura(reserva)
        if pdf_data:
            msg.attach('factura-turismo-chiriqui.pdf', 'application/pdf', pdf_data)

        if reserva.metodo_pago == 'yappy' and reserva.comprobante_pago:
            ruta = os.path.join(current_app.root_path, 'static', 'comprobantes', reserva.comprobante_pago)
            if os.path.exists(ruta):
                with open(ruta, 'rb') as f:
                    msg.attach(reserva.comprobante_pago, 'image/png' if reserva.comprobante_pago.endswith('.png') else 'image/jpeg', f.read())

        transporte_info = ''
        if reserva.transporte and reserva.transporte not in ('no_requiere', ''):
            t_label = {'vehiculo_propio': 'Vehiculo propio', 'autobus': 'Autobus', 'transporte_empresa': 'Transporte del proveedor', 'avion': 'Avion', 'lancha': 'Lancha', 'alquiler_auto': 'Alquiler de auto'}.get(reserva.transporte, reserva.transporte)
            if servicio and servicio.get_precio_transporte(reserva.transporte) > 0:
                transporte_info = f'Transporte: {t_label} (+B/.{servicio.get_precio_transporte(reserva.transporte):.2f} por persona)'
            elif servicio and servicio.incluye_transporte:
                transporte_info = f'Transporte: {t_label} (Incluido en el tour)'
            else:
                transporte_info = f'Transporte: {t_label} (Sin costo)'
        elif servicio and servicio.incluye_transporte:
            transporte_info = 'Transporte incluido en el tour'

        html_content = render_template(
            'emails/nueva_reserva_admin.html',
            reserva_id=reserva.id if reserva.id else '',
            transaccion=reserva.codigo_transaccion or '',
            cliente_nombre=cliente.usuario.nombre_completo,
            cliente_email=cliente.usuario.email,
            cliente_telefono=cliente.telefono or '',
            tour=servicio.nombre if servicio else 'Tour',
            tour_categoria=servicio.categoria if servicio else '',
            incluye_tour=servicio.incluye if servicio else '',
            transporte_info=transporte_info,
            fecha=reserva.fecha_gira.strftime('%d/%m/%Y') if reserva.fecha_gira else '—',
            fecha_fin=reserva.fecha_fin.strftime('%d/%m/%Y') if reserva.fecha_fin else '',
            personas=reserva.numero_personas,
            subtotal=f'B/.{reserva.subtotal:.2f}' if reserva.subtotal else '',
            itbms=f'B/.{reserva.itbms:.2f}' if reserva.itbms else '',
            total=f'B/.{reserva.total_pago:.2f}',
            tipo_tarjeta=reserva.tipo_tarjeta or '',
            ultimos_digitos=reserva.ultimos_digitos or '',
            link=link,
            metodo_pago=reserva.metodo_pago,
            comprobante_pago=reserva.comprobante_pago
        )
        msg.html = html_content
        mail.send(msg)
    except Exception as e:
        logger.error(f'Error enviando correo al admin: {e}')
