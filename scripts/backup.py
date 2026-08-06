import os
import subprocess
import gzip
import shutil
from datetime import datetime
from scripts.config import Config
from scripts.logger import log_message

def check_database_connection():
    try:
        backup_cnf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backup.cnf')
        
        if not os.path.exists(backup_cnf):
            log_message(f'Error: No se encuentra el archivo {backup_cnf}')
            return False
        
        cmd = f'"{Config.MYSQL_PATH}" --defaults-extra-file="{backup_cnf}" -h {Config.DB_HOST} -P {Config.DB_PORT} -e "SELECT 1;"'
        
        print(f"DEBUG: backup_cnf = {backup_cnf}")
        print(f"DEBUG: Comando = {cmd}")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            log_message('Conexión a MariaDB exitosa')
            return True
        else:
            log_message(f'Error al conectar con MariaDB: {result.stderr}')
            return False
    except Exception as e:
        log_message(f'Error al conectar con MariaDB: {e}')
        return False

def validate_backup(file_path):
    if not os.path.exists(file_path):
        return False
    if os.path.getsize(file_path) == 0:
        return False
    return True

def validate_gzip_integrity(file_path):
    try:
        with gzip.open(file_path, 'rb') as f:
            f.read(1)
        return True
    except Exception:
        return False

def clean_old_backups():
    backup_dir = Config.get_backup_dir()
    files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith('.sql.gz')]
    files.sort(key=os.path.getctime)
    
    if len(files) > Config.KEEP_BACKUPS:
        for f in files[:-Config.KEEP_BACKUPS]:
            os.remove(f)
            log_message(f'Eliminado respaldo antiguo: {os.path.basename(f)}')

def create_backup():
    if not check_database_connection():
        log_message('No se puede crear respaldo: MariaDB no responde')
        return None
    
    backup_dir = Config.get_backup_dir()
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file = os.path.join(backup_dir, f'turismo_{timestamp}.sql')
    backup_gz = os.path.join(backup_dir, f'turismo_{timestamp}.sql.gz')
    backup_cnf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backup.cnf')
    
    try:
        log_message('Iniciando respaldo...')
        
        cmd = (
            f'"{Config.MYSQLDUMP_PATH}" '
            f'--defaults-extra-file="{backup_cnf}" '
            f'-h {Config.DB_HOST} '
            f'-P {Config.DB_PORT} '
            f'--no-create-db '
            f'{Config.DB_NAME} '
            f'--single-transaction '
            f'--routines '
            f'--triggers '
            f'> "{backup_file}"'
        )
        
        print(f"DEBUG: Comando mysqldump = {cmd}")
        
        subprocess.run(cmd, shell=True, check=True)
        
        if not validate_backup(backup_file):
            log_message('Error: El respaldo está vacío o no se creó correctamente')
            if os.path.exists(backup_file):
                os.remove(backup_file)
            return None
        
        with open(backup_file, 'rb') as f_in:
            with gzip.open(backup_gz, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        os.remove(backup_file)
        
        if not validate_gzip_integrity(backup_gz):
            log_message('Error: El archivo comprimido está corrupto')
            os.remove(backup_gz)
            return None
        
        clean_old_backups()
        
        log_message(f'Respaldo creado: {backup_gz}')
        return backup_gz
    except subprocess.CalledProcessError as e:
        log_message(f'Error al crear respaldo: {e}')
        return None
    except Exception as e:
        log_message(f'Error general creando backup: {e}')
        return None

if __name__ == '__main__':
    create_backup()