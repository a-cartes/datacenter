#!/usr/bin/env python3
"""Read-only byte-integrity audit; writes one new report, never source or price files."""
import datetime as dt
import gzip
import hashlib
import json
import re
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.parquet as pq

B = Path('/Users/yo/Downloads/Medidas Transferencias económicas-selected/SOCHER_2026_v7_2020_2026/moderno')
OUT = B.parent / 'auditoria/control_descargas_20260927/moderno.json'

def digest(path):
    h = hashlib.sha256()
    total = 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(chunk)
            total += len(chunk)
    return total, h.hexdigest()

def audit_one(meta_path):
    meta = json.loads(meta_path.read_text())
    raw = B / meta['archivo']
    before = (raw.stat().st_size, raw.stat().st_mtime_ns)
    gzip_bytes, gzip_sha = digest(raw)
    h = hashlib.sha256()
    tsv_bytes = 0
    gzip_error = None
    try:
        # Reading to EOF also validates the gzip trailer / CRC via Python gzip.
        with gzip.open(raw, 'rb') as stream:
            for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
                h.update(chunk)
                tsv_bytes += len(chunk)
    except (EOFError, OSError) as error:
        gzip_error = f'{type(error).__name__}: {error}'
    after = (raw.stat().st_size, raw.stat().st_mtime_ns)
    header = {key.lower(): value for key, value in meta['cabeceras_http'].items()}
    expected_http_bytes = int(header['content-length'])
    stem = meta_path.stem
    extraction_path = meta_path.with_name(stem + '_extraccion.json')
    extraction = json.loads(extraction_path.read_text())
    references = []
    for resolution in ['15min', 'horario']:
        path = B / 'datos' / f'{stem}_{resolution}.parquet'
        _, parquet_sha = digest(path)
        table = pq.read_table(path, columns=['archivo_fuente', 'sha256_tsv_fuente', 'mes_fuente', 'version'])
        values = {name: pc.unique(table[name]).to_pylist() for name in table.column_names}
        valid = (
            set(values['archivo_fuente']) == {raw.name}
            and set(values['sha256_tsv_fuente']) == {meta['sha256_tsv_descomprimido']}
            and set(values['mes_fuente']) == {meta['mes']}
            and set(values['version']) == {'REAL-' + meta['version_solicitada']}
            and parquet_sha == extraction['outputs'][str(path.relative_to(B))]
        )
        references.append({'resolucion': resolution, 'filas': table.num_rows,
                           'fuentes_referidas': values, 'sha256_parquet_actual': parquet_sha,
                           'coincide_con_extraccion_y_original': valid})
    checks = {
        'gzip_tamano_coincide': gzip_bytes == meta['bytes_gzip_local'],
        'gzip_sha256_coincide': gzip_sha == meta['sha256_gzip_local'],
        'gzip_lectura_hasta_EOF_y_CRC_correctos': gzip_error is None,
        'tsv_tamano_coincide_metadato': tsv_bytes == meta['bytes_tsv_original'],
        'tsv_tamano_coincide_Content_Length_registrado': tsv_bytes == expected_http_bytes,
        'tsv_sha256_coincide': h.hexdigest() == meta['sha256_tsv_descomprimido'],
        'archivo_no_cambio_durante_lectura': before == after,
        'fuente_es_original_completo_y_no_parcial': raw.parent == B / 'fuentes/tsv_originales' and raw.name == stem + '.tsv.gz',
        'linaje_parquet_coincide': all(x['coincide_con_extraccion_y_original'] for x in references),
    }
    result = {
        'mes': meta['mes'], 'version': meta['version_solicitada'],
        'original': str(raw.relative_to(B)), 'url_registrada': meta['url'],
        'metadato': str(meta_path.relative_to(B)), 'sha256_metadato': digest(meta_path)[1],
        'etag_registrado': meta['etag'], 'consulta_original_utc': meta['consulta_fin_utc'],
        'gzip_bytes_actuales': gzip_bytes, 'gzip_sha256_actual': gzip_sha,
        'tsv_bytes_leidos': tsv_bytes, 'tsv_sha256_actual': h.hexdigest(),
        'content_length_http_registrado': expected_http_bytes,
        'error_descompresion': gzip_error, 'controles': checks,
        'linaje_analitico': references, 'resultado': 'OK' if all(checks.values()) else 'FALLA',
    }
    print(json.dumps({'mes': result['mes'], 'version': result['version'], 'resultado': result['resultado'], 'tsv_bytes': tsv_bytes}), flush=True)
    return result

def main():
    assert not OUT.exists(), 'El informe solicitado ya existe; no se sobrescribe.'
    expected = {f'{year}{month:02}_DEF' for year in [2024, 2025, 2026] for month in range(1, 13)
                if (2024, 7) <= (year, month) <= (2026, 9)} | {'202609_PRE'}
    metadata = sorted(p for p in (B / 'fuentes/metadatos').glob('*.json')
                      if re.fullmatch(r'\d{6}_(DEF|PRE)', p.stem))
    found = {p.stem for p in metadata}
    assert found == expected, {'faltan': sorted(expected-found), 'sobran': sorted(found-expected)}
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    rows = [audit_one(path) for path in metadata]
    raw_used = {row['original'] for row in rows}
    named_by_analytical = {name for row in rows for ref in row['linaje_analitico']
                           for name in ref['fuentes_referidas']['archivo_fuente']}
    interrupted_path = B / 'fuentes/descargas_interrumpidas/manifest_interrupcion.json'
    interrupted_manifest = {x['archivo']: x for x in json.loads(interrupted_path.read_text())}
    partials = []
    for path in sorted(B.rglob('*.partial*')):
        relative = str(path.relative_to(B))
        count, checksum = digest(path)
        saved = interrupted_manifest.get(relative, {})
        partials.append({'archivo': relative, 'bytes_actuales': count, 'sha256_actual': checksum,
                         'esta_fuera_de_originales_validos': path.parent != B / 'fuentes/tsv_originales',
                         'referido_como_original': relative in raw_used,
                         'referido_por_particiones_analiticas': path.name in named_by_analytical,
                         'coincide_con_manifest_de_interrupcion': checksum == saved.get('sha256_parcial') and count == saved.get('bytes_gzip_incompleto')})
    partials_excluded = all(x['esta_fuera_de_originales_validos'] and not x['referido_como_original']
                            and not x['referido_por_particiones_analiticas'] for x in partials)
    report = {
        'tipo_control': 'integridad_de_descarga_y_archivo_moderno_solo_lectura',
        'inicio_utc': started, 'fin_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'resultado': 'OK' if all(r['resultado'] == 'OK' for r in rows) and partials_excluded else 'FALLA',
        'fuentes_comprobadas': len(rows), 'definitivas': sum(r['version']=='DEF' for r in rows),
        'preliminares': sum(r['version']=='PRE' for r in rows),
        'bytes_gzip_comprobados': sum(r['gzip_bytes_actuales'] for r in rows),
        'bytes_tsv_leidos_integramente': sum(r['tsv_bytes_leidos'] for r in rows),
        'archivos_analiticos_parquet_con_linaje_comprobado': sum(len(r['linaje_analitico']) for r in rows),
        'parciales_interrumpidos_excluidos': partials_excluded,
        'alcance_confirmado': [
            'Los 28 originales gzip conservados coinciden en tamaño y SHA256 con sus metadatos de descarga.',
            'La lectura completa hasta EOF valida gzip/CRC y obtiene exactamente los bytes TSV registrados por Content-Length y por el SHA256 de la descarga.',
            'Los nombres y hashes de procedencia de las particiones analíticas verificadas apuntan a originales completos; no a parciales interrumpidos.',
        ],
        'limites': [
            'Es un control contra la versión preservada y las cabeceras HTTP registradas; no se realizó otra consulta a la versión remota actual.',
            'La integridad del archivo no demuestra que el proveedor haya publicado todas las horas, barras o fechas posibles ni excluye errores en los datos de origen.',
            'No valida la asociación entre barra y centro de datos, la fecha de tratamiento, la elegibilidad causal ni la conciliación de convenciones horarias.',
            'DEF y PRE siguen separados: DEF llega al 18/09/2026; PRE al 24/09/2026 solamente HRA 0, según la extracción previamente verificada.',
        ],
        'fuentes': rows, 'parciales': partials,
        'script_control_sha256': digest(Path(__file__))[1],
        'modificaciones_a_fuentes_o_tablas_publicadas': False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('x') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    print(json.dumps({'informe': str(OUT), 'resultado': report['resultado'], 'fuentes': len(rows), 'bytes_tsv': report['bytes_tsv_leidos_integramente'], 'parciales_excluidos': partials_excluded}), flush=True)
    if report['resultado'] != 'OK':
        raise SystemExit(1)

if __name__ == '__main__':
    main()
