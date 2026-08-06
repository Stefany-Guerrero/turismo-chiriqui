import os
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
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-turismo-chiriqui-2026'
    SESSION_PERMANENT = False
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_HTTPONLY = True

    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'admin2026')
    DB_HOST = _detect_db_host()
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'turismo_chiriqui')
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'itsdanhw14@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'ygsjxgfqagumhgrv')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'itsdanhw14@gmail.com')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'itsdanhw14@gmail.com')
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

    UPLOAD_FOLDER = 'uploads'
    JSON_FOLDER = 'json_transacciones'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024