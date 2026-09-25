"""Exportación legible del panel sin alterar sus observaciones."""
import csv
import gzip
import json
import argparse
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', default=os.getenv('SOCHER_OUTPUT_DIR', 'artifacts'),
                    help='Salida; ruta relativa a la raíz del repositorio. También SOCHER_OUTPUT_DIR.')
args = parser.parse_args()
requested = Path(args.output_dir).expanduser()
OUT = requested.resolve() if requested.is_absolute() else (ROOT / requested).resolve()
WORK = OUT / 'preparacion'
WORK.mkdir(parents=True, exist_ok=True)
with (ROOT / 'SOCHER_2026_dataset/documentacion/diccionario_panel.csv').open(encoding='utf-8-sig', newline='') as f:
    definitions = list(csv.DictReader(f))
types = {d['variable']: d['tipo'] for d in definitions}

def typed(value, dtype):
    if value == '':
        return None
    if dtype.lower() in ('bool', 'boolean'):
        assert value.lower() in ('true', 'false'), value
        return value.lower() == 'true'
    if dtype.lower().startswith('int'):
        return int(value)
    if dtype.lower().startswith('float'):
        return float(value)
    return value

with gzip.open(ROOT / 'SOCHER_2026_dataset/tablas/panel_barra_hora.csv.gz', 'rt', encoding='utf-8-sig', newline='') as src, (OUT / 'Dataset_articulo.csv').open('w', encoding='utf-8-sig', newline='') as dest:
    reader = csv.reader(src)
    writer = csv.writer(dest)
    headers = next(reader)
    writer.writerow(headers)
    chunks, rows, count = [], [], 0
    for row in reader:
        assert len(row) == len(headers)
        writer.writerow(row)
        rows.append([typed(v, types[h]) for h, v in zip(headers, row)])
        count += 1
        if len(rows) == 5000:
            name = f'filas_{len(chunks):03}.json'
            (WORK / name).write_text(json.dumps(rows, ensure_ascii=False, allow_nan=False), encoding='utf-8')
            chunks.append(name)
            rows = []
    if rows:
        name = f'filas_{len(chunks):03}.json'
        (WORK / name).write_text(json.dumps(rows, ensure_ascii=False, allow_nan=False), encoding='utf-8')
        chunks.append(name)
assert count == 178016 and len(headers) == 66
metadata = {'headers': headers, 'types': types, 'chunks': chunks, 'rows': count, 'definitions': definitions}
(WORK / 'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False), encoding='utf-8')
print(json.dumps({'filas': count, 'columnas': len(headers), 'csv': str(OUT / 'Dataset_articulo.csv')}))
