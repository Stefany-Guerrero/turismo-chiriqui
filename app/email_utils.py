from flask import current_app, render_template
from flask_mail import Message
from app import mail
from datetime import datetime
import io
import os
import logging

logger = logging.getLogger(__name__)


def _fmt_hora(h):
    if not h:
        return ''
    s = str(h).strip()
    if ':' not in s:
        return s
    try:
        partes = s.split(':')
        hora, minutos = int(partes[0]), partes[1][:2]
        sufijo = 'AM' if hora < 12 else 'PM'
        hora12 = hora % 12 or 12
        return f'{hora12}:{minutos} {sufijo}'
    except Exception:
        return s[:5]


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
        admin_email = current_app.config.get('ADMIN_EMAIL', 'proyectosprueba8@gmail.com')

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
            cliente_username=cliente.usuario.username or '',
            cliente_desde=cliente.fecha_creacion.strftime('%d/%m/%Y') if cliente.fecha_creacion else '—',
            tour=servicio.nombre if servicio else 'Tour',
            tour_codigo=servicio.codigo if servicio else '',
            tour_categoria=servicio.categoria if servicio else '',
            tour_destino=servicio.destino if servicio else '',
            tour_provincia=servicio.provincia if servicio else '',
            tour_distrito=servicio.distrito if servicio else '',
            tour_duracion=(f"{servicio.duracion_cantidad} {servicio.duracion_unidad}" if servicio and servicio.duracion_cantidad else '—'),
            tour_precio=(f'B/.{servicio.precio:.2f}' if servicio and servicio.precio else '—'),
            tour_hora_salida=_fmt_hora((servicio.hora_salida_tour or servicio.hora_inicio) if servicio else None),
            tour_hora_regreso=_fmt_hora((servicio.hora_regreso_tour or servicio.hora_estimada_regreso) if servicio else None),
            tour_punto_salida=servicio.punto_salida if servicio else '',
            tour_punto_llegada=servicio.punto_llegada if servicio else '',
            tour_no_incluye=servicio.no_incluye if servicio else '',
            tour_recomendaciones=servicio.recomendaciones if servicio else '',
            incluye_tour=servicio.incluye if servicio else '',
            transporte_info=transporte_info,
            fecha=reserva.fecha_gira.strftime('%d/%m/%Y') if reserva.fecha_gira else '—',
            fecha_fin=reserva.fecha_fin.strftime('%d/%m/%Y') if reserva.fecha_fin else '',
            fecha_compra=reserva.fecha_creacion.strftime('%d/%m/%Y %I:%M %p') if reserva.fecha_creacion else '—',
            personas=reserva.numero_personas,
            estado=reserva.estado or '',
            subtotal=f'B/.{reserva.subtotal:.2f}' if reserva.subtotal else '',
            itbms=f'B/.{reserva.itbms:.2f}' if reserva.itbms else '',
            descuento=f'B/.{reserva.descuento_aplicado:.2f}' if reserva.descuento_aplicado else '',
            total=f'B/.{reserva.total_pago:.2f}',
            tipo_tarjeta=reserva.tipo_tarjeta or '',
            ultimos_digitos=reserva.ultimos_digitos or '',
            titular_tarjeta=reserva.titular_tarjeta or '',
            link=link,
            metodo_pago=reserva.metodo_pago,
            comprobante_pago=reserva.comprobante_pago
        )
        msg.html = html_content
        mail.send(msg)
    except Exception as e:
        logger.error(f'Error enviando correo al admin: {e}')
