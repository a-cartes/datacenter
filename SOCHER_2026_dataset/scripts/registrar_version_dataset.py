"""Registra huellas de una versión local; no modifica ni duplica los datos."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys

B = Path(__file__).resolve().parents[1]
ROOT = B.parent
OUT = ROOT / 'outputs/01a0d6c3-09cd-7aa3-903d-5ee59e65c071'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nombre', default='base_observada_2026-09-25')
    args = parser.parse_args()
    if not args.nombre or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.nombre):
        parser.error('El nombre solo admite letras, números, guiones y guiones bajos.')
    target = B / 'controles/versiones' / (args.nombre + '.json')
    if target.exists():
        raise SystemExit('La versión ya existe: use otro nombre; no se sobrescriben registros.')
    paths = set()
    for folder in ['scripts', 'tablas', 'documentacion', 'controles']:
        paths.update(p for p in (B / folder).iterdir() if p.is_file() and not p.is_symlink())
    paths.update(p for p in B.iterdir() if p.is_file())
    paths.update([OUT / 'Dataset_articulo.csv', OUT / 'Dataset_articulo.xlsx'])
    report = json.loads((B / 'controles/verificacion_exportacion_excel_csv.json').read_text())
    if report['estado'] != 'OK' or report['n_errores'] != 0:
        raise SystemExit('La verificación de exportaciones no está aprobada.')
    fingerprints = {p: digest(p) for p in sorted(paths)}
    for key in ['fuente_csv_gz', 'diccionario_fuente', 'exportacion_csv', 'exportacion_xlsx']:
        entry = report['archivos'][key]
        path = ROOT / entry['ruta']
        actual = fingerprints.get(path) or digest(path)
        if actual != entry['sha256']:
            raise SystemExit(f'Archivo modificado desde su verificación: {entry["ruta"]}')
    packages = {}
    for name in ['pandas', 'numpy', 'pyarrow', 'openpyxl']:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    record = {
        'version_local': args.nombre,
        'fecha_registro_utc': datetime.now(timezone.utc).isoformat(),
        'tipo': 'manifiesto_de_huellas_no_es_commit_ni_backup',
        'alcance': 'Capa dataset y entregas finales actuales. No inventaría todos los originales de versiones previas.',
        'estado_causal': 'asignacion_de_tratamientos_y_exposicion_pendiente',
        'reproduccion_en_entorno_limpio': False,
        'filas_panel': 178016, 'columnas_panel': 66,
        'entorno_del_registro': {'python': sys.version.split()[0], 'plataforma': platform.platform(), 'paquetes': packages},
        'validacion_exportaciones_preexistente': {'estado': report['estado'], 'n_errores': report['n_errores'], 'fecha_fin_utc': report['fecha_fin_utc']},
        'archivos': [{'ruta': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': fingerprints[p]} for p in sorted(paths)],
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'registro': str(target.relative_to(ROOT)), 'archivos': len(record['archivos'])}, ensure_ascii=False))

if __name__ == '__main__':
    main()
