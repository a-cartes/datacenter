"""Archiva evidencias existentes de una prueba aislada; no ejecuta ni certifica la instalación."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prueba', type=Path, help='Carpeta con repo/, venv/, instalacion.log y dependencias_instaladas.txt')
    parser.add_argument('destino', type=Path, help='Carpeta nueva para conservar evidencia compacta')
    args = parser.parse_args()
    source = args.prueba.resolve()
    artifacts = source / 'repo/artifacts'
    run = json.loads((artifacts / 'registro_reproduccion.json').read_text())
    check = json.loads((artifacts / 'verificacion_exportacion_excel_csv.json').read_text())
    contract = json.loads((artifacts / 'verificacion_contrato.json').read_text())
    config = (source / 'venv/pyvenv.cfg').read_text()
    if not run['completado'] or check['estado'] != 'OK' or contract['estado'] != 'OK':
        raise SystemExit('No se archiva como satisfactoria una prueba incompleta o con fallos.')
    if 'include-system-site-packages = false' not in config:
        raise SystemExit('El entorno no declara aislamiento de paquetes del sistema.')
    for step in run['pasos']:
        if sha(source / 'repo' / step['script']) != step['sha256_script']:
            raise SystemExit('Un programa cambió después de ejecutarse: ' + step['script'])
    for key in ('exportacion_csv', 'exportacion_xlsx'):
        item = check['archivos'][key]
        path = source / 'repo' / item['ruta']
        if path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise SystemExit('Una exportación cambió después de verificarse: ' + key)
    args.destino.mkdir(parents=True, exist_ok=False)
    files = {
        'registro_reproduccion.json': artifacts / 'registro_reproduccion.json',
        'verificacion_exportacion_excel_csv.json': artifacts / 'verificacion_exportacion_excel_csv.json',
        'verificacion_contrato.json': artifacts / 'verificacion_contrato.json',
        'dependencias_instaladas.txt': source / 'dependencias_instaladas.txt',
        'pyvenv.cfg': source / 'venv/pyvenv.cfg',
        'instalacion.log': source / 'instalacion.log',
        'ejecucion.log': source / 'ejecucion.log',
    }
    manifest = {'inicio_utc': run['inicio_utc'], 'fin_utc': run['fin_utc'],
                'alcance': 'Entorno virtual nuevo en el mismo equipo; reconstrucción desde extractos conservados.',
                'incluye_paquetes_del_sistema': False,
                'adquisicion_original_ejecutada': False, 'estimacion_causal_ejecutada': False,
                'script_de_archivado_sha256': sha(Path(__file__)),
                'nota': 'El campo instalacion_limpia_verificada del ejecutor queda en false por diseño: el ejecutor no crea ni evalúa entornos. La prueba de instalación se conserva por separado.',
                'archivos': {}}
    for name, path in files.items():
        shutil.copyfile(path, args.destino / name)
        manifest['archivos'][name] = {'bytes': path.stat().st_size, 'sha256': sha(path)}
    (args.destino / 'manifiesto.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'estado': 'OK', 'archivos_archivados': len(files), 'destino': str(args.destino)}))


if __name__ == '__main__':
    main()
