"""Descarga pública autenticada del CEN. Nunca registra clave, URL autenticada ni headers."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,hashlib,gzip,time,shutil
import requests
S=Path(__file__).resolve().parents[1]
ROUTES={'rio':'/instrucciones-operacionales-cmg/v4/findByDate','limitaciones':'/limitaciones-transmision/v4/findByDate','flujos':'/potencia-transitada/v4/findByDate','generacion':'/generacion-real/v3/findByDate'}
def getkey(project):
 key=os.environ.get('COORDINADOR_API_KEY')
 if not key:
  for line in (project/'.env').read_text().splitlines():
   if line.strip().startswith('COORDINADOR_API_KEY='):key=line.split('=',1)[1].strip().strip('\"').strip("'");break
 if not key:raise RuntimeError('Credencial del Coordinador no disponible')
 return key
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--proyecto',type=Path,required=True);ap.add_argument('--recurso',choices=ROUTES,required=True);ap.add_argument('--inicio',required=True);ap.add_argument('--fin',required=True);ap.add_argument('--ejecucion',required=True);ap.add_argument('--piloto',action='store_true');ap.add_argument('--limite',type=int,default=10000);ap.add_argument('--pausa',type=float,default=10);ap.add_argument('--resume-from',type=Path);a=ap.parse_args()
 out=S/'fuentes_operacion'/a.ejecucion
 if out.exists() or out.parent.resolve()!=(S/'fuentes_operacion').resolve():raise ValueError('Carpeta nueva requerida')
 out.mkdir(parents=True);key=getkey(a.proyecto);session=requests.Session();route=ROUTES[a.recurso];manifest=[]
 def request(page,limit):
  dest=out/f'pagina_{page:05}_{limit}.json.gz'
  cached=a.resume_from/dest.name if a.resume_from else None
  if cached and cached.exists():
   obj=json.loads(gzip.open(cached).read());data=obj.get('data',obj.get('content',[]));shutil.copyfile(cached,dest)
   manifest.append(dict(archivo=dest.name,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),filas=len(data),pagina_solicitada=page,limite_solicitado=limit,recuperado_de=str(cached.relative_to(S)),metadatos={k:v for k,v in obj.items() if k not in ['data','content']}));return obj,data
  if manifest:time.sleep(a.pausa)
  params=dict(startDate=a.inicio,endDate=a.fin,page=page,limit=limit,user_key=key)
  if a.recurso=='generacion':params['pageSize']=limit
  try:r=session.get('https://sipub.api.coordinador.cl'+route,params=params,timeout=50)
  except requests.RequestException as exc:raise RuntimeError(type(exc).__name__) from None
  if r.status_code!=200:raise RuntimeError('HTTP '+str(r.status_code))
  try:obj=r.json()
  except ValueError:raise RuntimeError('Respuesta no JSON') from None
  raw=json.dumps(obj,ensure_ascii=False,sort_keys=True).encode();assert key.encode() not in raw
  with gzip.open(dest,'wb') as f:f.write(raw)
  data=obj.get('data',obj.get('content',[]));manifest.append(dict(archivo=dest.name,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),filas=len(data),pagina_solicitada=page,limite_solicitado=limit,metadatos={k:v for k,v in obj.items() if k not in ['data','content']}))
  print(json.dumps(dict(recurso=a.recurso,pagina=page,filas=len(data),metadatos=manifest[-1]['metadatos']),ensure_ascii=False),flush=True)
  return obj,data
 status='incompleto'
 try:
  if a.piloto:
   request(0,10);request(1,10);status='piloto'
  else:
   first,data=request(1,a.limite);pages=int(first.get('totalPages',0));assert pages<=500, 'Rango demasiado extenso'
   for page in range(2,pages+1):request(page,a.limite)
   _,extra=request(pages+1,a.limite)
   status='descargado_requiere_validacion' if not extra else 'pagina_extra_con_datos'
 except Exception as exc:status='error:'+str(exc) if isinstance(exc,(RuntimeError,AssertionError)) else 'error:'+type(exc).__name__;print(status,flush=True)
 finally:
  (out/'manifiesto.json').write_text(json.dumps(dict(recurso=a.recurso,ruta=route,inicio=a.inicio,fin=a.fin,consultado_UTC=datetime.now(timezone.utc).isoformat(),estado=status,paginas=manifest),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
