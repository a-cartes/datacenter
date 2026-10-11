"""Completa descarga mensual con dos consultas concurrentes espaciadas; sin sobrescribir."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import argparse,calendar,json,subprocess,sys
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--proyecto',type=Path,required=True);a=ap.parse_args();jobs=[]
 for year in [2024,2025,2026]:
  for month in range(1,13):
   if (year,month)<(2024,8) or (year,month)>(2026,8):continue
   name=f'20261011_rio_{year}{month:02}_completo';dest=S/'fuentes_operacion'/name
   if dest.exists():
    print('Conservar existente '+name,flush=True);continue
   jobs.append((name,f'{year}-{month:02}-01',f'{year}-{month:02}-{calendar.monthrange(year,month)[1]}'))
 def run(item):
  name,start,end=item
  prior=S/'fuentes_operacion'/name.replace('_completo','')
  cmd=[sys.executable,'-B',str(S/'scripts/descargar_operacion_api.py'),'--proyecto',str(a.proyecto),'--recurso','rio','--inicio',start,'--fin',end,'--ejecucion',name,'--pausa','10']
  if prior.exists():cmd+=['--resume-from',str(prior)]
  result=subprocess.run(cmd,capture_output=True,text=True)
  manifest=S/'fuentes_operacion'/name/'manifiesto.json'
  if manifest.exists():
   m=json.loads(manifest.read_text());return dict(ejecucion=name,estado=m['estado'],paginas=len(m['paginas']),filas=sum(p['filas'] for p in m['paginas']))
  return dict(ejecucion=name,estado='fallo_proceso',codigo=result.returncode)
 with ThreadPoolExecutor(max_workers=2) as pool:
  for f in as_completed([pool.submit(run,j) for j in jobs]):print(json.dumps(f.result()),flush=True)
if __name__=='__main__':main()
