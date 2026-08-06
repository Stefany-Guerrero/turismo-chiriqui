#!/usr/bin/env python3
import os
import gzip
import re
import sys
from datetime import datetime
from collections import Counter
from scripts.config import Config
from scripts.logger import log_message

def get_latest_backup():
    backup_dir = Config.get_backup_dir()
    files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith('.sql.gz')]
    if not files:
        return None
    files.sort(key=os.path.getctime, reverse=True)
    return files[0]

def count_insert_records(content, table_name):
    pattern = rf"INSERT INTO `{table_name}` VALUES\s*\((.+?)\);"
    matches = re.findall(pattern, content, re.DOTALL)
    total = 0
    for match in matches:
        records = re.findall(r'\([^)]+\)', match)
        total += len(records) if records else 1
    return total

def inspect_backup(backup_file):
    print(f"\n{'='*60}")
    print(f"INSPECCION DE RESPALDO")
    print(f"{'='*60}")
    print(f"Archivo: {os.path.basename(backup_file)}")
    print(f"Fecha: {datetime.fromtimestamp(os.path.getctime(backup_file)).strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Tamanio: {os.path.getsize(backup_file) / 1024:.2f} KB")
    print(f"{'='*60}\n")
    
    try:
        with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
            content = f.read()
        
        print("VERIFICANDO INTEGRIDAD...")
        if not content.strip():
            print("ERROR: El backup esta vacio")
            return False
        
        print("El backup contiene datos\n")
        
        tables = re.findall(r'CREATE TABLE `([^`]+)`', content)
        print(f"TABLAS ENCONTRADAS: {len(tables)}")
        for t in tables:
            print(f"   - `{t}`")
        
        inserts = re.findall(r'INSERT INTO `([^`]+)`', content)
        insert_counts = Counter(inserts)
        
        print(f"\nREGISTROS POR TABLA:")
        if insert_counts:
            for table, count in insert_counts.most_common():
                real_records = count_insert_records(content, table)
                print(f"   - `{table}`: {real_records} registros ({count} sentencias INSERT)")
        else:
            print("   - No se encontraron registros (base de datos vacia)")
        
        has_create_db = 'CREATE DATABASE' in content.upper()
        print(f"\nContiene CREATE DATABASE: {'Si' if has_create_db else 'No'}")
        
        if has_create_db:
            print("   Este backup creara/sobrescribira la base de datos 'turismo_chiriqui'")
        
        expected_tables = Config.EXPECTED_TABLES
        missing = [t for t in expected_tables if t not in tables]
        
        if missing:
            print(f"\nFALTAN TABLAS ESPERADAS:")
            for t in missing:
                print(f"   - {t}")
        else:
            print(f"\nTodas las tablas esperadas estan presentes ({len(expected_tables)})")
        
        size_kb = len(content) / 1024
        print(f"\nTAMANIO DEL CONTENIDO SQL: {size_kb:.2f} KB")
        
        if 'INSERT INTO `usuarios`' in content:
            print("\nLa tabla `usuarios` tiene datos")
        else:
            print("\nLa tabla `usuarios` esta vacia")
        
        print(f"\n{'='*60}")
        print("INSPECCION COMPLETADA")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"Error al leer el backup: {e}")
        return False

if __name__ == '__main__':
    backup_file = get_latest_backup()
    if not backup_file:
        print("No hay respaldos disponibles en la carpeta de backups")
        sys.exit(1)
    
    inspect_backup(backup_file)