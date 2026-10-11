"""Comprueba insumos contra la instantánea. Solo lectura; no actualiza hashes."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parent

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(2**20), b''):
            digest.update(block)
    return digest.hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proyecto', type=Path, required=True)
    parser.add_argument('--mediciones-legacy', type=Path, required=True)
    parser.add_argument('--ejecucion', default='20261011_inventario_v2')
    args = parser.parse_args()
    execution = STAGE/'resultados'/args.ejecucion
    if execution.parent.resolve() != (STAGE/'resultados').resolve():
        raise SystemExit('Ejecución fuera de resultados.')
    roots = {'proyecto': args.proyecto.resolve(), 'repositorio': REPO,
             'mediciones_legacy': args.mediciones_legacy.resolve()}
    with (execution/'insumos_estado_inicial.csv').open() as stream:
        records = list(csv.DictReader(stream))
    errors = []
    for row in records:
        prefix, relative = row['referencia'].split(':', 1)
        root = roots[prefix]
        path = (root/relative).resolve()
        if not path.is_relative_to(root):
            raise SystemExit('Referencia externa en manifiesto.')
        if not path.is_file() or path.stat().st_size != int(row['bytes']) or sha(path) != row['sha256']:
            errors.append(row['referencia'])
    baseline = json.loads((execution/'estado_inicial.json').read_text())
    tag = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'v0.3.0^{}'], text=True).strip()
    if tag != baseline['commit_version_preservada']:
        errors.append('El tag anterior cambió de commit')
    # Permite la etapa nueva y README editorial autorizado (CZ-012); protege archivos científicos históricos.
    changed = subprocess.check_output(['git', '-C', str(REPO), 'diff', '--name-only', tag], text=True).splitlines()
    errors.extend('Cambio fuera de etapa: '+p for p in changed if not p.startswith('Investigacion_carga_zonal/') and p != 'README.md')
    print(json.dumps({'estado': 'ERROR' if errors else 'OK', 'insumos_comprobados': len(records),
        'tag_anterior': tag, 'diferencias': errors,
        'alcance': 'SHA-256 de insumos seleccionados y archivos históricos versionados; solo lectura'}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
