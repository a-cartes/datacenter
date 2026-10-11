"""Generación real por central; respuestas originales y metadatos sin credenciales."""
from pathlib import Path
import argparse,json,gzip,hashlib,time
from datetime import datetime,timezone
import requests
from descargar_operacion_api import getkey
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--proyecto',type=Path,required=True);ap.add_argument('--ejecucion',required=True);ap.add_argument('--piloto',action='store_true');a=ap.parse_args()
 out=S/'fuentes_operacion'/a.ejecucion;assert out.parent.resolve()==(S/'fuentes_operacion').resolve();out.mkdir();key=getkey(a.proyecto);pages=[];status='incompleto'
 def request(cid,page,size,start,end):
  if pages:time.sleep(10)
  params=dict(idCentral=cid,page=page,pageSize=size,startDate=start,endDate=end,user_key=key)
  try:r=requests.get('https://sipub.api.coordinador.cl/generacion-real/v3/findByDate',params=params,timeout=90)
  except requests.RequestException as e:raise RuntimeError(type(e).__name__) from None
  if r.status_code!=200:raise RuntimeError('HTTP '+str(r.status_code))
  try:o=r.json()
  except ValueError:raise RuntimeError('JSON inválido') from None
  raw=json.dumps(o,ensure_ascii=False,sort_keys=True).encode();assert key.encode() not in raw
  file=out/f'central_{cid}_pagina_{page:03}_{size}.json.gz'
  with gzip.open(file,'wb') as f:f.write(raw)
  data=o.get('data',o.get('content',[]));meta={k:v for k,v in o.items() if k not in ['data','content']}
  pages.append(dict(archivo=file.name,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),idCentral=cid,page=page,pageSize=size,inicio=start,fin=end,filas=len(data),metadatos=meta))
  print(json.dumps(dict(central=cid,page=page,filas=len(data),meta=meta,muestra=data[:1]),ensure_ascii=False),flush=True)
  return o,data
 try:
  for cid in [364,2209]:
   if a.piloto:
    request(cid,0,3,'2025-01-22','2025-01-22');request(cid,1,3,'2025-01-22','2025-01-22')
   else:
    first,data=request(cid,1,10000,'2024-08-01','2026-08-31');n=int(first['totalPages']);assert n<100
    for page in range(2,n+1):request(cid,page,10000,'2024-08-01','2026-08-31')
    _,extra=request(cid,n+1,10000,'2024-08-01','2026-08-31');assert not extra,'Página extra con datos'
  status='piloto' if a.piloto else 'descarga_completa_pendiente_validacion'
 except Exception as e:
  status='error:'+str(e) if isinstance(e,(RuntimeError,AssertionError)) else 'error:'+type(e).__name__;print(status,flush=True)
 finally:
  (out/'manifiesto.json').write_text(json.dumps(dict(ruta='/generacion-real/v3/findByDate',consulta_UTC=datetime.now(timezone.utc).isoformat(),estado=status,paginas=pages),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
