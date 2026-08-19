"""Limpia respaldos manuales viejos del repositorio.

Conserva los N respaldos SQL más recientes (por fecha de modificación) entre
la raíz del proyecto y la carpeta backups/, y elimina el resto.

Uso:
    venv/Scripts/python scripts/limpiar_backups.py            # borra, conserva 5
    venv/Scripts/python scripts/limpiar_backups.py --keep 8   # conserva 8
    venv/Scripts/python scripts/limpiar_backups.py --dry-run  # solo muestra qué borraría
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUFFIXES = ('.sql', '.sql.gz')
DEFAULT_KEEP = 5


def collect_backups():
    archivos = []
    carpetas = [BASE_DIR, os.path.join(BASE_DIR, 'backups')]
    for carpeta in carpetas:
        if not os.path.isdir(carpeta):
            continue
        for nombre in os.listdir(carpeta):
            ruta = os.path.join(carpeta, nombre)
            if os.path.isfile(ruta) and nombre.endswith(SUFFIXES):
                archivos.append(ruta)
    archivos.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return archivos


def main():
    keep = DEFAULT_KEEP
    dry_run = False
    args = sys.argv[1:]
    if '--dry-run' in args:
        dry_run = True
        args.remove('--dry-run')
    if '--keep' in args:
        idx = args.index('--keep')
        try:
            keep = max(1, int(args[idx + 1]))
        except (ValueError, IndexError):
            print('Error: --keep requiere un número entero.')
            return 1

    respaldos = collect_backups()
    total = len(respaldos)
    if total == 0:
        print('No se encontraron respaldos.')
        return 0

    conservar = respaldos[:keep]
    eliminar = respaldos[keep:]

    print(f'Respaldos encontrados: {total}')
    print(f'Conservar los {len(conservar)} más recientes:')
    for p in conservar:
        print(f'  [KEEP] {os.path.relpath(p, BASE_DIR)}')
    print(f'Eliminar {len(eliminar)}:')
    for p in eliminar:
        print(f'  [DEL] {os.path.relpath(p, BASE_DIR)}')

    if dry_run:
        print('\n(dry-run: no se borró nada)')
        return 0

    for p in eliminar:
        try:
            os.remove(p)
        except OSError as e:
            print(f'  Error al eliminar {os.path.basename(p)}: {e}')
    print(f'\nListo: se conservaron {len(conservar)} y se eliminaron {len(eliminar)}.')


if __name__ == '__main__':
    sys.exit(main())
