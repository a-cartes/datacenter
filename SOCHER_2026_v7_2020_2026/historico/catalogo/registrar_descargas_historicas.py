#!/usr/bin/env python3
"""Copia originales CMg DEF descargados y registra su integridad, sin analizarlos.

Busca solamente nombres CMg DEF de 202001–202407 en Downloads. Los archivos
sin enlace aún catalogado se conservan con URL nula y procedencia pendiente;
no se deduce una URL por el nombre. Un ZIP parcial/no legible no se copia.
"""
from pathlib import Path
import argparse, datetime as dt, hashlib, io, json, re, shutil, zipfile

HERE = Path(__file__).resolve().parent
HIST = HERE.parent
ROOT = HIST.parent.parent

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(2**20), b''):
            h.update(block)
    return h.hexdigest()

def verify_selected(z, month, depth=0):
    """Verifica CRC solo de libros CMg, homologaciones y ZIP CMg anidados."""
    if depth > 3:
        raise ValueError('ZIP anidado a más de tres niveles')
    checked = []
    for info in z.infolist():
        name = Path(info.filename).name.lower()
        isbook = re.fullmatch(r'cmg_?'+month+r'_def\.(xlsm|xlsx)', name)
        ishomo = 'homolog' in name and 'prg' not in name and name.endswith('.xlsx')
        if isbook or ishomo:
            z.read(info)
            checked.append(info.filename)
        elif name.endswith('.zip') and 'cmg' in name and 'fpen' not in name:
            with zipfile.ZipFile(io.BytesIO(z.read(info))) as nested:
                checked.extend(info.filename+'/'+s for s in verify_selected(nested, month, depth+1))
    return checked

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--downloads', type=Path, default=Path.home()/'Downloads')
    a = ap.parse_args()
    catalog = json.loads((HERE/'catalogo_cmg_oficial_2020_2024.json').read_text())
    urls = {Path(r['url_archivo']).name: r for r in catalog['definitivos'] if r['url_archivo']}
    output = HIST/'originales'
    output.mkdir(exist_ok=True)
    records = []
    added = []
    errors = []
    oldfile = HERE/'descargas_historicas_registradas.json'
    old = json.loads(oldfile.read_text()) if oldfile.exists() else {}
    checked_hashes = {r['sha256']: r['miembros_crc_verificado'] for r in old.get('archivos', []) if r.get('miembros_crc_verificado')}
    rejected_hashes = {r['sha256']: r['error'] for r in old.get('errores', []) if r.get('sha256')}
    for p in sorted(a.downloads.glob('cmg*.zip')):
        m = re.fullmatch(r'cmg_?(\d{4})_def(?:-\d+)?(?: \(\d+\))?\.zip', p.name, re.I)
        if not m or not '2001' <= m[1] <= '2407':
            continue
        # No se acepta silenciosamente un original diferente con igual nombre.
        checksum = None
        target = output/p.name
        try:
            before = p.stat()
            with zipfile.ZipFile(p) as z:
                members = [{'nombre': i.filename, 'bytes': i.file_size, 'comprimidos': i.compress_size,
                            'crc32': f'{i.CRC:08x}'} for i in z.infolist()]
            checksum = sha(p)
            if checksum in rejected_hashes:
                raise ValueError(rejected_hashes[checksum])
            checked = checked_hashes.get(checksum)
            if checked is None:
                with zipfile.ZipFile(p) as z:
                    checked = verify_selected(z, m[1])
                if not checked:
                    raise ValueError('No contiene libro CMg ni homologación pertinente')
                checked_hashes[checksum] = checked
            after = p.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ValueError('Archivo todavía cambia durante lectura')
            if target.exists():
                if sha(target) != checksum:
                    raise ValueError('Existe destino divergente; no se sobrescribe')
            else:
                shutil.copy2(p, target)
                if sha(target) != checksum:
                    raise ValueError('Copia divergente')
                added.append('20'+m[1])
            # El sufijo (n) solo se reconoce para buscar el URL previamente visto.
            key = re.sub(r' \(\d+\)(?=\.zip$)', '', p.name)
            source = urls.get(key)
            records.append({'mes': '20'+m[1], 'archivo': str(target.relative_to(ROOT)),
                'descarga_original': str(p), 'bytes': after.st_size, 'sha256': checksum,
                'url': source['url_archivo'] if source else None,
                'fecha_publicacion_literal': source['fecha_publicacion_literal'] if source else None,
                'estado_procedencia': 'enlace_catalogado' if source else 'enlace_pendiente_de_catalogar',
                'validacion_zip': 'CRC verificado de libros CMg, homologaciones y ZIP CMg anidados; otros miembros no extraídos',
                'miembros_crc_verificado': checked,
                'miembros_exteriores': members})
        except Exception as e:
            quarantine = None
            dest = output/'cuarentena'/target.name
            if target.exists():
                folder = output/'cuarentena';folder.mkdir(exist_ok=True)
                if not dest.exists():
                    target.rename(dest)
            if dest.exists():
                quarantine = str(dest.relative_to(ROOT))
            errors.append({'archivo': str(p), 'sha256': checksum,
                'error': str(e), 'cuarentena': quarantine})
    report = {'registrado_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'archivos': records, 'errores': errors}
    (HERE/'descargas_historicas_registradas.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'n_archivos': len(records), 'meses_nuevos': sorted(set(added)), 'errores': errors}, ensure_ascii=False))

if __name__ == '__main__':
    main()
