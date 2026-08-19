from datetime import datetime, timezone, timedelta, date
import time
from functools import wraps
from flask import request, flash, redirect, url_for

PANAMA_TZ = timezone(timedelta(hours=-5))

def panama_now():
    return datetime.now(PANAMA_TZ).replace(tzinfo=None)

class RateLimiter:
    _stores = {}

    @classmethod
    def is_limited(cls, key, max_attempts=5, window_seconds=300):
        now = time.time()
        if key not in cls._stores:
            cls._stores[key] = []
        cls._stores[key] = [t for t in cls._stores[key] if now - t < window_seconds]
        if len(cls._stores[key]) >= max_attempts:
            return True
        cls._stores[key].append(now)
        return False

def rate_limit(max_attempts=5, window_seconds=300, key_func=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if key_func:
                key = key_func()
            else:
                key = f'{f.__name__}:{request.remote_addr}'
            if RateLimiter.is_limited(key, max_attempts, window_seconds):
                flash('Demasiadas solicitudes. Intenta de nuevo más tarde.', 'error')
                return redirect(request.referrer or url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def preload_promociones(servicios, fecha_referencia=None):
    from app.models.promocion import Promocion
    hoy = fecha_referencia or date.today()
    svc_ids = [s.id for s in servicios]
    if not svc_ids:
        return {}
    promos = Promocion.query.filter(
        Promocion.servicio_id.in_(svc_ids),
        Promocion.activa == True,
        Promocion.fecha_inicio <= hoy,
        Promocion.fecha_fin >= hoy
    ).all()
    promo_map = {}
    for p in promos:
        if p.servicio_id not in promo_map:
            promo_map[p.servicio_id] = p
    for s in servicios:
        s._promo_cache = promo_map.get(s.id)
    return promo_map

def preload_disponibilidad(servicios, fecha_inicio, fecha_fin):
    from app.models.servicio import Disponibilidad
    from app import db
    svc_ids = [s.id for s in servicios]
    if not svc_ids:
        return {}
    disps = Disponibilidad.query.filter(
        Disponibilidad.servicio_id.in_(svc_ids),
        Disponibilidad.fecha >= fecha_inicio,
        Disponibilidad.fecha <= fecha_fin
    ).all()
    disp_map = {}
    for d in disps:
        disp_map[(d.servicio_id, d.fecha)] = d.cupos_disponibles
    return disp_map
