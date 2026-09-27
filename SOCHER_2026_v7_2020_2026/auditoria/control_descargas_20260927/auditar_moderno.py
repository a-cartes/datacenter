#!/usr/bin/env python3
"""Control portátil de integridad, sin red ni modificaciones de fuentes.

Dependencias: Python y pyarrow (entorno validado: Python3.13.15/pyarrow25.0.1).
Ejemplo desde la raíz v7:
  python auditoria/control_descargas_20260927/auditar_moderno.py \\
    --moderno-dir moderno \\
    --output auditoria/control_descargas_20260927/otro_informe.json

La salida debe ser nueva. La lista esperada de fuentes se obtiene del índice
preservado y los parciales se comparan con su manifiesto, sin fijar cantidades.
La copia auditar_moderno_ejecucion_original.py conserva los bytes del control
que produjo moderno.json; esta versión parametrizada tiene otra huella.
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
import re
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.parquet as pq

def digest(path):
    h = hashlib.sha256()
    total = 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(chunk)
            total += len(chunk)
    return total, h.hexdigest()

def audit_one(meta_path, B):
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
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--moderno-dir', required=True, type=Path, help='Directorio que contiene fuentes/ y datos/.')
    parser.add_argument('--output', required=True, type=Path, help='Nuevo informe JSON; no se sobrescribe una salida existente.')
    args = parser.parse_args()
    B = args.moderno_dir.expanduser().resolve()
    OUT = args.output.expanduser().resolve()
    if not B.is_dir():
        raise NotADirectoryError(f'No existe el módulo moderno: {B}')
    if OUT.exists():
        raise FileExistsError(f'El informe solicitado ya existe; no se sobrescribe: {OUT}')
    if any(OUT.is_relative_to(B / folder) for folder in ['fuentes', 'datos']):
        raise ValueError('La salida no puede ubicarse dentro de fuentes/ o datos/.')
    index_path = B / 'fuentes/indice_tsv_moderno.json'
    index = json.loads(index_path.read_text())
    if not isinstance(index, list) or not index:
        raise ValueError('El índice preservado debe contener una lista no vacía de fuentes.')
    expected = set()
    for item in index:
        month, version = item['mes'], item['version_solicitada']
        if not re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])', month) or version not in ['DEF', 'PRE']:
            raise ValueError(f'Entrada no válida en el índice preservado: {month}, {version}')
        expected.add(month.replace('-', '') + '_' + version)
    if len(expected) != len(index):
        raise ValueError('El índice preservado contiene meses/versiones duplicados.')
    metadata = sorted(p for p in (B / 'fuentes/metadatos').glob('*.json')
                      if re.fullmatch(r'\d{6}_(DEF|PRE)', p.stem))
    found = {p.stem for p in metadata}
    if found != expected:
        raise ValueError(f'Inventario de fuentes distinto del índice: faltan={sorted(expected-found)}, sobran={sorted(found-expected)}')
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    rows = [audit_one(path, B) for path in metadata]
    raw_used = {row['original'] for row in rows}
    named_by_analytical = {name for row in rows for ref in row['linaje_analitico']
                           for name in ref['fuentes_referidas']['archivo_fuente']}
    interrupted_path = B / 'fuentes/descargas_interrumpidas/manifest_interrupcion.json'
    interrupted_records = json.loads(interrupted_path.read_text())
    if not isinstance(interrupted_records, list):
        raise ValueError('El manifiesto de interrupciones debe contener una lista.')
    interrupted_manifest = {x['archivo']: x for x in interrupted_records}
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
    observed_partials = {x['archivo'] for x in partials}
    expected_partials = set(interrupted_manifest)
    partial_controls = {
        'manifest_sin_rutas_duplicadas': len(interrupted_manifest) == len(interrupted_records),
        'inventario_exacto': observed_partials == expected_partials,
        'todos_los_tamanos_y_hashes_coinciden': all(x['coincide_con_manifest_de_interrupcion'] for x in partials),
        'ningun_parcial_es_fuente_analitica': partials_excluded,
    }
    sources_ok = all(r['resultado'] == 'OK' for r in rows)
    all_ok = sources_ok and all(partial_controls.values())
    confirmed = []
    if sources_ok:
        confirmed.extend([
            f'Los {len(rows)} originales gzip conservados coinciden en tamaño y SHA256 con sus metadatos de descarga.',
            'La lectura completa hasta EOF valida gzip/CRC y obtiene exactamente los bytes TSV registrados por Content-Length y por el SHA256 de la descarga.',
            'Los nombres y hashes de procedencia de las particiones analíticas verificadas coinciden con los originales completos registrados.',
        ])
    if all(partial_controls.values()):
        confirmed.append('El inventario, los tamaños y los hashes de los parciales coinciden con el manifiesto de interrupciones y ninguno se utiliza como fuente analítica.')
    report = {
        'tipo_control': 'integridad_de_descarga_y_archivo_moderno_solo_lectura',
        'inicio_utc': started, 'fin_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'resultado': 'OK' if all_ok else 'FALLA',
        'fuentes_esperadas_segun_indice': len(expected),
        'indice_fuentes': str(index_path.relative_to(B)),
        'sha256_indice_fuentes': digest(index_path)[1],
        'fuentes_comprobadas': len(rows), 'definitivas': sum(r['version']=='DEF' for r in rows),
        'preliminares': sum(r['version']=='PRE' for r in rows),
        'bytes_gzip_comprobados': sum(r['gzip_bytes_actuales'] for r in rows),
        'bytes_tsv_leidos_integramente': sum(r['tsv_bytes_leidos'] for r in rows),
        'archivos_analiticos_parquet_con_linaje_comprobado': sum(len(r['linaje_analitico']) for r in rows),
        'parciales_interrumpidos_excluidos': partials_excluded,
        'control_manifest_parciales': {
            'archivo': str(interrupted_path.relative_to(B)),
            'sha256_manifest': digest(interrupted_path)[1],
            'cantidad_registrada': len(interrupted_records),
            'cantidad_observada': len(partials),
            'faltantes': sorted(expected_partials-observed_partials),
            'no_registrados': sorted(observed_partials-expected_partials),
            'controles': partial_controls,
        },
        'alcance_confirmado': confirmed,
        'limites': [
            'Es un control contra la versión preservada y las cabeceras HTTP registradas; no se realizó otra consulta a la versión remota actual.',
            'La integridad del archivo no demuestra que el proveedor haya publicado todas las horas, barras o fechas posibles ni excluye errores en los datos de origen.',
            'No valida la asociación entre barra y centro de datos, la fecha de tratamiento, la elegibilidad causal ni la conciliación de convenciones horarias.',
            'DEF y PRE se comprueban por separado. Este control de bytes no interpreta la cobertura temporal; ésta debe consultarse en los metadatos de extracción y en la auditoría de cobertura correspondiente.',
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
