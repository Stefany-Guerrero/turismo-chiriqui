#!/usr/bin/env python3
import os
from datetime import datetime
from scripts.config import Config
from scripts.backup import create_backup
from scripts.logger import log_message

def check_and_backup():
    backup_dir = Config.get_backup_dir()
    files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith('.sql.gz')]
    files.sort(key=os.path.getctime, reverse=True)
    
    log_message('Verificando respaldos...')
    
    if files:
        latest = files[0]
        backup_time = datetime.fromtimestamp(os.path.getctime(latest))
        days_diff = (datetime.now() - backup_time).days
        
        if days_diff >= Config.BACKUP_DAYS:
            log_message(f'Último respaldo hace {days_diff} días. Creando nuevo...')
            create_backup()
        else:
            log_message(f'Respaldo reciente: {os.path.basename(latest)}')
    else:
        log_message('No hay respaldos. Creando uno...')
        create_backup()

if __name__ == '__main__':
    check_and_backup()
