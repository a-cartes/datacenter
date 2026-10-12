"""Comprobación pública independiente de detección, conciliación y procedencia."""
from pathlib import Path
import argparse,json,statistics
import pandas as pd
import numpy as np
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args();assert not a.salida.exists();checks=[]
 for folder in ['20261011_humberto_largo_panel_v1','20261011_estimacion_larga_v1','20261011_diagnostico_variaciones_v1']:
  for _,r in pd.read_csv(S/'resultados'/folder/'insumos_sha256.csv').iterrows():assert sha(S/r.archivo)==r.sha256;checks.append(r.archivo)
 q=pd.read_csv(S/'resultados/20261011_variaciones_carga/carga_fisica_horaria.csv.gz');assert np.nanmax(np.abs(q.MW-q.HT1-q.HT2))<1e-9;q['date']=pd.to_datetime(q.fecha);day=q.groupby('date').MW.agg(['median','count']);day.loc[day['count'].ne(24),'median']=np.nan
 arr=day['median'].to_numpy();dates=day.index;det=[]
 for i in range(len(arr)):
  before=arr[max(0,i-7):i];after=arr[i:i+7];b=before[np.isfinite(before)];c=after[np.isfinite(after)]
  if len(b)<6 or len(c)<6:continue
  b=statistics.median(b);c=statistics.median(c);delta=c-b
  for rule,x,y in [('principal',.5,.2),('bajo',.25,.1),('alto',1,.3)]:
   if abs(delta)>=x and abs(delta/b)>=y:det.append(dict(regla=rule,fecha=dates[i],delta=delta,antes=b,despues=c))
 candidates=[]
 for rule in ['principal','bajo','alto']:
  raw=[x for x in det if x['regla']==rule];groups=[]
  for r in raw:
   if not groups or (r['fecha']-groups[-1][-1]['fecha']).days>14:groups.append([])
   groups[-1].append(r)
  candidates += [max(g,key=lambda r:abs(r['delta'])) for g in groups]
 target=pd.read_csv(S/'resultados/20261011_variaciones_carga/escalones_candidatos.csv');assert len(target)==len(candidates)
 for r in candidates:
  z=target[(target.regla==r['regla'])&(target.fecha==r['fecha'].strftime('%Y-%m-%d'))].iloc[0];assert abs(z.delta_MW-r['delta'])<1e-10
 case=pd.read_csv(S/'resultados/20261011_diagnostico_variaciones_v1/episodio_documentado.csv');assert abs(case.fraccion_barra23_fuera.sum()*60-943)<1e-8
 fits=json.loads((S/'resultados/20261011_estimacion_larga_v1/verificacion.json').read_text());assert fits['estado']=='OK'
 info=dict(estado='OK',hashes_insumos=len(checks),escalones_reproducidos=len(candidates),deteccion_independiente='medianas con statistics y agrupación manual; solo carga',minutos_evento=943,estimaciones=fits,requiere_originales_locales=False);a.salida.write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
if __name__=='__main__':main()
