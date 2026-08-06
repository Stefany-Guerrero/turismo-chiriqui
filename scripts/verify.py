#!/usr/bin/env python3
import os
import subprocess
from scripts.config import Config
from scripts.logger import log_message

def verify_database():
    try:
        log_message('Verificando base de datos...')
        print('\n' + '=' * 50)
        print('VERIFICACIÓN DE BASE DE DATOS')
        print('=' * 50 + '\n')
        
        verify_cnf = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'verify.cnf')
        
        test_cmd = f'"{Config.MYSQL_PATH}" --defaults-extra-file="{verify_cnf}" -h {Config.DB_HOST} -P {Config.DB_PORT} -e "SELECT 1;"'
        test_result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
        
        if test_result.returncode != 0:
            log_message('Error al conectar con MariaDB')
            print(test_result.stderr)
            return False
        
        log_message('Conexión a MariaDB exitosa')
        print('Conexión a MariaDB: CORRECTA')
        
        db_cmd = f'"{Config.MYSQL_PATH}" --defaults-extra-file="{verify_cnf}" -h {Config.DB_HOST} -P {Config.DB_PORT} -e "USE {Config.DB_NAME}; SHOW TABLES;"'
        db_result = subprocess.run(db_cmd, shell=True, capture_output=True, text=True)
        
        if db_result.returncode != 0:
            log_message(f'Error al acceder a la base de datos {Config.DB_NAME}')
            print(db_result.stderr)
            return False
        
        existing_tables = [t.strip() for t in db_result.stdout.strip().split('\n')[1:] if t.strip()]
        
        print(f'\nVerificando tablas esperadas:')
        print('-' * 40)
        
        success = True
        
        for expected in Config.EXPECTED_TABLES:
            if expected in existing_tables:
                count_cmd = f'"{Config.MYSQL_PATH}" --defaults-extra-file="{verify_cnf}" -h {Config.DB_HOST} -P {Config.DB_PORT} -e "USE {Config.DB_NAME}; SELECT COUNT(*) FROM {expected};"'
                count_result = subprocess.run(count_cmd, shell=True, capture_output=True, text=True)
                
                if count_result.returncode == 0:
                    count_lines = count_result.stdout.strip().split('\n')
                    if len(count_lines) > 1:
                        try:
                            count = int(count_lines[1].strip())
                            if count > 0:
                                print(f'  OK {expected}: {count} registros')
                            else:
                                print(f'  WARNING {expected}: {count} registros (tabla vacía)')
                        except ValueError:
                            print(f'  WARNING {expected}: No se pudo obtener el conteo')
                    else:
                        print(f'  OK {expected}: 0 registros')
                else:
                    print(f'  WARNING {expected}: Existe pero no se pudo contar')
            else:
                print(f'  ERROR {expected}: NO EXISTE')
                success = False
        
        if success:
            log_message('Verificación completada: Base de datos OK')
            print('\n' + '=' * 50)
            print('BASE DE DATOS VERIFICADA CORRECTAMENTE')
            print('=' * 50)
        else:
            log_message('Verificación completada: Faltan tablas')
            print('\n' + '=' * 50)
            print('BASE DE DATOS CON PROBLEMAS')
            print('=' * 50)
        
        return success
    except Exception as e:
        log_message(f'Error en verificación: {e}')
        return False

if __name__ == '__main__':
    verify_database()
