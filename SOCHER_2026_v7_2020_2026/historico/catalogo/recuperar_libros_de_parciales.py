#!/usr/bin/env python3
"""Preserva libros completos de contenedores ZIP incompletos, sin alterar Downloads.

Cada miembro requiere tamaño explícito, flujo completo, CRC32 coincidente y ZIP
OOXML interno íntegro. La copia parcial conserva hash, metadatos y offsets.
No declara íntegro el contenedor ni recupera datos de miembros truncados.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, re, shutil, struct, zipfile, zlib

HERE = Path(__file__).resolve().parent
HIST = HERE.parent

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()

def scan(path):
    size = path.stat().st_size; rows = []
    with path.open('rb') as f:
        while f.tell() + 30 <= size:
            offset = f.tell(); header = f.read(30)
            if header[:4] != b'PK\x03\x04': break
            h = struct.unpack('<I5H3I2H', header)
            flags, method, crc, comp, uncomp, nlen, xlen = h[2], h[3], h[6], h[7], h[8], h[9], h[10]
            name = f.read(nlen).decode('utf-8' if flags & 2048 else 'cp437')
            f.read(xlen); start = f.tell()
            explicit = not (flags & 8) and comp != 0xffffffff and uncomp != 0xffffffff
            row = dict(nombre=name, offset=offset, data_offset=start, flags=flags,
                       metodo=method, crc32=f'{crc:08x}', bytes_comprimidos=comp,
                       bytes_miembro=uncomp, tamanos_explicitos=explicit,
                       miembro_completo=explicit and start + comp <= size)
            rows.append(row)
            if not row['miembro_completo']: break
            f.seek(start + comp)
    return rows

def month_in(name):
    m = re.search(r'(?<!\d)(202[0-4][01]\d)(?:[0-3]\d)?(?!\d)', name)
    if m: return m[1]
    m = re.search(r'(?<!\d)(2[0-4][01]\d)(?!\d)', name)
    return '20' + m[1] if m else None

def role(name):
    base = Path(name).name.lower()
    if re.fullmatch(r'cmg_?\d{4}_def\.xls[mx]', base): return 'libro_precios'
    if 'homolog' in base and base.endswith('.xlsx') and 'prg' not in base: return 'homologacion'
    return None

def extract(snapshot, member, destination):
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / Path(member['nombre']).name
    tmp = destination / (target.name + '.recuperando')
    method = member['metodo']; crc = 0; size = 0
    if method not in (0, 8): raise ValueError('Método de compresión no admitido')
    decomp = zlib.decompressobj(-15) if method == 8 else None
    try:
        with snapshot.open('rb') as source, tmp.open('wb') as output:
            source.seek(member['data_offset']); left = member['bytes_comprimidos']
            while left:
                block = source.read(min(left, 1048576))
                if not block: raise ValueError('Miembro incompleto durante lectura')
                left -= len(block); plain = decomp.decompress(block) if decomp else block
                output.write(plain); crc = zlib.crc32(plain, crc); size += len(plain)
            if decomp:
                plain = decomp.flush(); output.write(plain)
                crc = zlib.crc32(plain, crc); size += len(plain)
                if not decomp.eof or decomp.unused_data: raise ValueError('Flujo deflate no íntegro')
        if size != member['bytes_miembro'] or f'{crc:08x}' != member['crc32']:
            raise ValueError('Tamaño o CRC del miembro no coincide')
        with zipfile.ZipFile(tmp) as z:
            bad = z.testzip()
            if bad or '[Content_Types].xml' not in z.namelist() or 'xl/workbook.xml' not in z.namelist():
                raise ValueError('Libro OOXML interno no válido: ' + str(bad))
        digest = sha(tmp)
        if target.exists():
            if sha(target) != digest: raise ValueError('Libro ya preservado tiene hash diferente; no sustituido')
            tmp.unlink()
        else: os.replace(tmp, target)
        return dict(archivo=str(target.relative_to(HIST)), bytes=size, sha256=digest,
                    crc32_verificado=f'{crc:08x}', zip_ooxml_interno_verificado=True)
    finally:
        if tmp.exists(): tmp.unlink()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--months', nargs='*')
    ap.add_argument('--downloads', type=Path, default=Path.home() / 'Downloads')
    args = ap.parse_args()
    catalog = {r['mes']: r for r in json.loads((HERE / 'catalogo_cmg_oficial_2020_2024.json').read_text())['definitivos']}
    months = set(args.months or json.loads((HERE / 'cobertura_historica_actual.json').read_text())['meses_pendientes'])
    observed = datetime.now(timezone.utc).isoformat(); records = []; errors = []; recovered = set()
    folder = HIST / 'originales/parciales_preservados'; folder.mkdir(parents=True, exist_ok=True)
    for source in sorted(args.downloads.glob('*.crdownload')):
        try:
            before = source.stat(); members = scan(source)
            possible = {month_in(m['nombre']) for m in members} - {None}
            if len(possible) != 1: continue
            month = next(iter(possible))
            if month not in months or month not in catalog: continue
            wanted = [m for m in members if m['miembro_completo'] and role(m['nombre'])]
            if not wanted: continue
            # An active transfer can change size/mtime while copying: reject that
            # snapshot, leaving both the source and any earlier valid books intact.
            temp = folder / (source.name + '.copiando')
            shutil.copyfile(source, temp); after = source.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                temp.unlink(); errors.append({'archivo':source.name,'error':'Descarga cambió; reintentar copia estable'}); continue
            digest = sha(temp); snapshot = folder / f'{month}_{digest[:16]}.zip.part'
            if snapshot.exists():
                if sha(snapshot) != digest: raise ValueError('Colisión de copia preservada')
                temp.unlink()
            else: os.replace(temp, snapshot)
            rec = dict(mes=month, observado_utc=observed, estado_contenedor='ZIP_INCOMPLETO_NO_VALIDADO_COMO_CONJUNTO',
                       fuente_parcial=str(source), bytes_parcial=before.st_size,
                       mtime_parcial_ns=before.st_mtime_ns,
                       mtime_parcial_utc=datetime.fromtimestamp(before.st_mtime,timezone.utc).isoformat(),
                       copia_estable=str(snapshot.relative_to(HIST)), copia_sha256=digest,
                       url_oficial_correspondiente=catalog[month]['url_archivo'],
                       metodo_asociacion_url='Mes del nombre de miembro DEF y catálogo de enlaces observados; nombre temporal del navegador no acredita URL de transporte.',
                       miembros_observados=members, recuperados=[])
            for member in wanted:
                result = extract(snapshot, member, HIST / 'libros' / month)
                rec['recuperados'].append(dict(tipo=role(member['nombre']), nombre_miembro=member['nombre'],
                                               offset=member['offset'], data_offset=member['data_offset'],
                                               bytes_comprimidos=member['bytes_comprimidos'], **result))
                if role(member['nombre']) == 'libro_precios': recovered.add(month)
            destination = HIST / 'manifiestos' / f'recuperacion_parcial_{month}_{digest[:16]}.json'
            destination.parent.mkdir(exist_ok=True)
            destination.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n')
            records.append({'mes':month,'manifest':str(destination.relative_to(HIST)),
                            'recuperados':[r['tipo'] for r in rec['recuperados']]})
        except Exception as exc:
            errors.append({'archivo':str(source),'error_tipo':type(exc).__name__,'error':str(exc)})
    result = dict(observado_utc=observed, meses_con_libro_recuperado=sorted(recovered), registros=records, errores=errors)
    (HERE / 'recuperacion_parciales_ultimo_lote.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))

if __name__ == '__main__': main()
