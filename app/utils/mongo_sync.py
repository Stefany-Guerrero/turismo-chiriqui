try:
    import pymongo
    MONGO_AVAILABLE = True
except ImportError:
    pymongo = None
    MONGO_AVAILABLE = False

import json
from datetime import datetime, date
from decimal import Decimal
import os
import socket

MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    hostname = socket.gethostname().lower()
    if hostname in ('kali', 'kali-linux', 'kali.lan'):
        MONGO_URI = 'mongodb://192.168.56.1:27017'
    else:
        MONGO_URI = 'mongodb://localhost:27017'
MONGO_DB = 'turismo_chiriqui'

_client = None
_db = None

def _get_db():
    global _client, _db
    if not MONGO_AVAILABLE:
        return None
    try:
        _client.server_info()
    except Exception:
        if _client:
            try: _client.close()
            except Exception: pass
        _client = None
        _db = None
    if _db is None:
        _client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000, connectTimeoutMS=2000, socketTimeoutMS=2000)
        _db = _client[MONGO_DB]
    return _db

def _default_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='replace')
    return str(obj)

def _model_to_dict(model):
    columns = model.__table__.columns.keys()
    data = {}
    for col in columns:
        val = getattr(model, col)
        if val is not None:
            data[col] = json.loads(json.dumps(val, default=_default_serializer))
        else:
            data[col] = None
    return data

def sync_insert(model):
    try:
        db = _get_db()
        if db is None:
            return
        collection_name = model.__tablename__
        data = _model_to_dict(model)
        db[collection_name].insert_one(data)
    except Exception as e:
        print(f'[MONGO SYNC ERROR] insert {model.__class__.__name__}: {e}')

def sync_update(model):
    try:
        db = _get_db()
        if db is None:
            return
        collection_name = model.__tablename__
        data = _model_to_dict(model)
        pk = model.__table__.primary_key.columns.values()[0].name
        pk_value = getattr(model, pk)
        db[collection_name].update_one({pk: pk_value}, {'$set': data}, upsert=True)
    except Exception as e:
        print(f'[MONGO SYNC ERROR] update {model.__class__.__name__}: {e}')

def sync_delete(model):
    try:
        db = _get_db()
        if db is None:
            return
        collection_name = model.__tablename__
        pk = model.__table__.primary_key.columns.values()[0].name
        pk_value = getattr(model, pk)
        db[collection_name].delete_one({pk: pk_value})
    except Exception as e:
        print(f'[MONGO SYNC ERROR] delete {model.__class__.__name__}: {e}')
