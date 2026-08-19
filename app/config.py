import os
import secrets
import socket
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

def _detect_db_host():
    db_host = os.environ.get('DB_HOST')
    if db_host:
        return db_host
    hostname = socket.gethostname().lower()
    if hostname in ('kali', 'kali-linux', 'kali.lan'):
        return '192.168.56.1'
    return 'localhost'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SESSION_PERMANENT = False
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('COOKIE_SECURE', 'false').lower() == 'true'

    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = _detect_db_host()
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'turismo_chiriqui')
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'proyectosprueba8@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'proyectosprueba8@gmail.com')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'proyectosprueba8@gmail.com')
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

    UPLOAD_FOLDER = 'uploads'
    JSON_FOLDER = 'json_transacciones'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_BLOCK_MINUTES = 15