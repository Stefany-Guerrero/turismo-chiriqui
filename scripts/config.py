import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)

print(f"DEBUG: Cargando .env desde: {env_path}")  # Línea de depuración

class Config:
    DB_NAME = os.getenv('DB_NAME', 'turismo_chiriqui')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    
    MYSQLDUMP_PATH = os.getenv('MYSQLDUMP_PATH', 'mysqldump')
    MYSQL_PATH = os.getenv('MYSQL_PATH', 'mysql')
    
    BACKUP_ROOT = os.getenv('BACKUP_ROOT', 'C:/Backups_Turismo')
    KEEP_BACKUPS = int(os.getenv('KEEP_BACKUPS', '30'))
    BACKUP_DAYS = int(os.getenv('BACKUP_DAYS', '1'))
    
    EXPECTED_TABLES = [
        'usuarios',
        'clientes',
        'servicios',
        'reservas',
        'promociones',
        'proveedores',
        'disponibilidad',
        'solicitudes',
        'transacciones',
        'viajes_planificados',
        'recomendaciones_viaje'
    ]
    
    @staticmethod
    def get_backup_dir():
        backup_dir = os.path.join(Config.BACKUP_ROOT, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    
    @staticmethod
    def get_log_dir():
        log_dir = os.path.join(Config.BACKUP_ROOT, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    @staticmethod
    def get_temp_dir():
        temp_dir = os.path.join(Config.BACKUP_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir