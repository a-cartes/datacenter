#!/usr/bin/env python3
"""Lee metadatos de descargas CMg truncadas sin modificarlas ni recuperarlas.

El mes sugerido procede sólo del primer nombre de miembro ZIP y nunca sirve
para completar precios, homologaciones o cobertura del dataset.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, re, struct

HERE=Path(__file__).resolve().parent

def main():
    rows=[]; observed=datetime.now(timezone.utc).isoformat()
    for p in sorted((Path.home()/'Downloads').glob('*.crdownload')):
        s=p.stat()
        with p.open('rb') as f:
            header=f.read(30)
            if header[:4]!=b'PK\x03\x04':continue
            fields=struct.unpack('<IHHHHHIIIHH',header)
            name=f.read(fields[-2]).decode('utf-8' if fields[2]&2048 else 'cp437',errors='replace')
        if not any(x in name.lower() for x in ['cmg','fpen','marginales']):continue
        match=re.search(r'(?<!\d)(2[0-4][01]\d)(?!\d)',name)
        yearmatch=re.search(r'(?<!\d)(202[0-4][01]\d)[0-3]\d(?!\d)',name)
        month='20'+match[1] if match else yearmatch[1] if yearmatch else None
        rows.append({'observado_utc':observed,'archivo':p.name,'bytes':s.st_size,
            'modificado_utc':datetime.fromtimestamp(s.st_mtime,timezone.utc).isoformat(),
            'primer_miembro_zip':name,'mes_sugerido_solo_por_nombre':month,
            'estado':'parcial_no_utilizado'})
    (HERE/'descargas_parciales_observadas.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'parciales_cmg_observados':len(rows),'meses_sugeridos':sorted({r['mes_sugerido_solo_por_nombre'] for r in rows if r['mes_sugerido_solo_por_nombre']})},ensure_ascii=False))

if __name__=='__main__':
    main()
