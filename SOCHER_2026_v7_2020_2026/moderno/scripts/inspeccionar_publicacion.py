#!/usr/bin/env python3
"""Inspecciona el patrón TSV que implementa el botón oficial, sin descargar el universo."""
import datetime as dt, json, urllib.request, urllib.error, concurrent.futures
from pathlib import Path
B=Path(__file__).resolve().parents[1]
BASE='https://cen-datalake-public.s3.amazonaws.com/costos_marginales/CMG_REAL'
def url(y,m,version='DEF'): return f'{BASE}/{y}/{m}/{y}_{m:02}_REAL-{version}.tsv'
def inspect(args):
 y,m,version=args;u=url(y,m,version)
 rec={'mes':f'{y}-{m:02}','version_solicitada':version,'url':u,'fecha_consulta_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(u,method='HEAD'),timeout=45) as r:
   rec.update(status=r.status,bytes=int(r.headers.get('Content-Length',0)),last_modified=r.headers.get('Last-Modified'),etag=r.headers.get('ETag'),content_type=r.headers.get('Content-Type'))
 except urllib.error.HTTPError as e:rec.update(status=e.code,error=e.reason)
 except Exception as e:rec.update(status=None,error=str(e))
 return rec
if __name__=='__main__':
 pairs=[(y,m,'DEF') for y in [2024,2025,2026] for m in range(1,13) if (y,m)>=(2024,7) and (y,m)<=(2026,9)]
 pairs += [(2026,9,'PRE')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:rows=list(p.map(inspect,pairs))
 (B/'fuentes/indice_tsv_moderno.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 print(json.dumps(rows,ensure_ascii=False,indent=2))
 for y,m,v in [(2025,6,'DEF'),(2026,9,'DEF'),(2026,9,'PRE')]:
  try:
   with urllib.request.urlopen(urllib.request.Request(url(y,m,v),headers={'Range':'bytes=0-4095'}),timeout=45) as r:
    data=r.read(4096);print('SAMPLE',y,m,v,r.status,r.headers.get('Content-Range'))
   (B/f'fuentes/muestra_{y}{m:02}_{v}_primeros4096bytes.tsv').write_bytes(data)
   print(data.decode(errors='replace')[:2000])
  except Exception as e:print('SAMPLE_FAILED',y,m,v,str(e))
