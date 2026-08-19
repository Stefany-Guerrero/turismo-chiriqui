import os

EXTENSIONES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'pdf'}
MAX_TAMANO_BYTES = 10 * 1024 * 1024


def validar_archivo(archivo):
    """Valida nombre, extensión y contenido real de un archivo de comprobante.

    Devuelve una tupla (ok: bool, mensaje: str).
    """
    if archivo is None:
        return False, 'No se recibió ningún archivo.'

    nombre = archivo.filename or ''
    if nombre == '':
        return False, 'El archivo no tiene nombre.'

    ext = nombre.rsplit('.', 1)[-1].lower() if '.' in nombre else ''
    if ext not in EXTENSIONES_PERMITIDAS:
        return False, f'Formato no permitido ("{ext or "sin extensión"}"). Usa PNG, JPG, JPEG, WEBP, GIF o PDF.'

    archivo.seek(0, os.SEEK_END)
    tamano = archivo.tell()
    archivo.seek(0)
    if tamano == 0:
        return False, 'El archivo está vacío.'
    if tamano > MAX_TAMANO_BYTES:
        return False, 'El archivo supera el tamaño máximo de 10 MB.'

    inicio = archivo.read(16)
    archivo.seek(0)

    if ext == 'webp':
        if not (inicio.startswith(b'RIFF') and inicio[8:12] == b'WEBP'):
            return False, 'El contenido no parece una imagen WebP válida.'
    elif ext in ('jpeg', 'jpg'):
        if not inicio.startswith(b'\xff\xd8\xff'):
            return False, 'El contenido no parece una imagen JPEG válida.'
    elif ext == 'png':
        if not inicio.startswith(b'\x89PNG\r\n\x1a\n'):
            return False, 'El contenido no parece una imagen PNG válida.'
    elif ext == 'gif':
        if not (inicio.startswith(b'GIF87a') or inicio.startswith(b'GIF89a')):
            return False, 'El contenido no parece una imagen GIF válida.'
    elif ext == 'pdf':
        if not inicio.startswith(b'%PDF'):
            return False, 'El contenido no parece un PDF válido.'

    return True, ''
