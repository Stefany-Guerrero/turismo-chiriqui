import os
from datetime import datetime
from scripts.config import Config

def log_message(message):
    log_dir = Config.get_log_dir()
    log_file = os.path.join(log_dir, 'backup.log')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {message}\n')
    
    print(f'[{timestamp}] {message}')
