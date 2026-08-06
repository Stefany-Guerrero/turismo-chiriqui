#!/usr/bin/env python3
import os
import subprocess
import gzip
import shutil
from datetime import datetime
from scripts.config import Config
from scripts.logger import log_message
from scripts.backup import create_backup, validate_gzip_integrity
from scripts.verify import verify_database

def list_backups():
    backup_dir = Config.get_backup_dir()
    files = [f for f in os.listdir(backup_dir) if f.endswith('.sql.gz')]
    files.sort(reverse=True)
    return files

def restore_backup(backup_file):
    temp_dir = Config.get_temp_dir()
    temp_file = os.path.join(temp_dir, 'restore_temp.sql')
    restore_cnf = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'restore.cnf')
    
    try:
        log_message('Descomprimiendo respaldo...')
        
        if not validate_gzip_integrity(backup_file):
            log_message('El archivo de respaldo está corrupto')
            return False
        
        with gzip.open(backup_file, 'rb') as f_in:
            with open(temp_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified_content = "SET FOREIGN_KEY_CHECKS=0;\n" + content + "\nSET FOREIGN_KEY_CHECKS=1;"
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        log_message('Restaurando base de datos...')
        
        cmd = f'"{Config.MYSQL_PATH}" --defaults-extra-file="{restore_cnf}" {Config.DB_NAME}'
        
        with open(temp_file, 'r', encoding='utf-8') as sql_file:
            subprocess.run(cmd, shell=True, check=True, stdin=sql_file)
        
        os.remove(temp_file)
        
        log_message('Base de datos restaurada exitosamente')
        
        log_message('Verificando integridad...')
        if verify_database():
            log_message('Verificación completada: La base de datos está correcta')
            return True
        else:
            log_message('Verificación completada: La base de datos tiene problemas')
            return False
    except Exception as e:
        log_message(f'Error al restaurar: {e}')
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

if __name__ == '__main__':
    print('=' * 50)
    print('RESTAURACIÓN DE BASE DE DATOS')
    print('=' * 50)
    
    backups = list_backups()
    if not backups:
        print('No hay respaldos disponibles')
        exit(1)
    
    print('\nRespaldos disponibles:')
    for i, b in enumerate(backups):
        file_path = os.path.join(Config.get_backup_dir(), b)
        size = os.path.getsize(file_path)
        date = datetime.fromtimestamp(os.path.getctime(file_path))
        print(f'  {i+1}. {b} ({size/1024:.2f} KB) - {date.strftime("%d/%m/%Y %H:%M:%S")}')
    
    try:
        choice = int(input('\nSelecciona el número del respaldo a restaurar: ')) - 1
        if choice < 0 or choice >= len(backups):
            print('Opción inválida')
            exit(1)
        
        backup_file = os.path.join(Config.get_backup_dir(), backups[choice])
        
        confirm = input(f'\n¿Estás seguro de restaurar {backups[choice]}? (s/n): ')
        if confirm.lower() != 's':
            print('Restauración cancelada')
            exit(0)
        
        print('\nCreando backup de seguridad antes de restaurar...')
        emergency_backup = create_backup()
        if emergency_backup:
            print(f'Backup de seguridad creado: {os.path.basename(emergency_backup)}')
        else:
            print('No se pudo crear backup de seguridad. ¿Continuar?')
            if input('Continuar de todas formas? (s/n): ').lower() != 's':
                exit(0)
        
        restore_backup(backup_file)
    except ValueError:
        print('Entrada inválida')
        exit(1)
