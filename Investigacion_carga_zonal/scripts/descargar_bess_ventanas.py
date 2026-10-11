"""Adquisición paginada BESS; ventanas diagnósticas fijadas antes del análisis."""
from pathlib import Path
import argparse,json,gzip,time,hashlib
from datetime import datetime,timezone
import requests
from descargar_operacion_api import getkey
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--inicio',required=True);ap.add_argument('--fin',required=True);ap.add_argument('--ejecucion',required=True);ap.add_argument('--max-paginas',type=int,default=100);a=ap.parse_args();o=S/'fuentes_operacion'/a.ejecucion;assert o.parent.resolve()==(S/'fuentes_operacion').resolve();o.mkdir();key=getkey(Path.cwd());pages=[];status='incompleto'
 def get(page):
  if pages:time.sleep(10)
  params=dict(startDate=a.inicio,endDate=a.fin,tipoTecnologia='BESS',page=page,pageSize=10000,user_key=key)
  for attempt in range(3):
   try:r=requests.get('https://sipub.api.coordinador.cl/generacion-real/v3/findByDate',params=params,timeout=90)
   except requests.RequestException as e:
    if attempt==2:raise RuntimeError(type(e).__name__) from None
    time.sleep(15);continue
   if r.status_code==200:break
   if attempt==2:raise RuntimeError('HTTP '+str(r.status_code))
   time.sleep(20)
  obj=r.json();data=obj.get('data',obj.get('content',[]));raw=json.dumps(obj,ensure_ascii=False,sort_keys=True).encode();assert key.encode() not in raw;f=o/f'pagina_{page:04}.json.gz'
  with gzip.open(f,'wb') as z:z.write(raw)
  meta={k:v for k,v in obj.items() if k not in ['data','content']};pages.append(dict(archivo=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),pagina=page,filas=len(data),metadatos=meta));(o/'avance.json').write_text(json.dumps(pages,indent=2));print(json.dumps(dict(pagina=page,filas=len(data),totalPages=obj.get('totalPages')),ensure_ascii=False),flush=True);return obj,data
 try:
  obj,_=get(1);n=int(obj['totalPages']);assert n<=a.max_paginas,'Tope de páginas diagnósticas'
  for i in range(2,n+1):get(i)
  _,extra=get(n+1);assert not extra;status='completo_pendiente_auditoria'
 except Exception as e:status='error:'+str(e) if isinstance(e,(RuntimeError,AssertionError)) else 'error:'+type(e).__name__;print(status,flush=True)
 finally:(o/'manifiesto.json').write_text(json.dumps(dict(ruta='/generacion-real/v3/findByDate',filtro='tipoTecnologia=BESS',inicio=a.inicio,fin=a.fin,consulta_UTC=datetime.now(timezone.utc).isoformat(),estado=status,paginas=pages),indent=2))
if __name__=='__main__':main()
