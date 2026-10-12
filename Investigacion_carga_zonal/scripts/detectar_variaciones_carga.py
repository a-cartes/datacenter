"""Candidatos por carga exclusivamente; no lee precios ni el resultado de regresiones."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mediciones',type=Path,required=True);a=ap.parse_args();out=S/'resultados/20261011_variaciones_carga';out.mkdir();before=sha(a.mediciones);q=pd.read_parquet(a.mediciones,columns=['IDSOCKET','etiqueta_utc','energia_D_kwh','energia_R_kwh']);ids={f'LSCANTRS_110_HT{i}_EDG':f'HT{i}' for i in (1,2,3)};q=q[q.IDSOCKET.isin(ids)].copy();assert not q.duplicated(['IDSOCKET','etiqueta_utc']).any();q['hora_utc']=q.etiqueta_utc.dt.floor('h');q['canal']=q.IDSOCKET.map(ids)
 h=q.groupby(['hora_utc','canal']).agg(n=('etiqueta_utc','size'),nd=('energia_D_kwh','count'),D=('energia_D_kwh','sum'),R=('energia_R_kwh','sum'));h['D']=h.D.where(h.n.eq(4)&h.nd.eq(4))/1000;w=h.D.unstack('canal');idx=pd.date_range('2024-08-01','2026-09-01',freq='h',inclusive='left',tz='America/Santiago').tz_convert('UTC');w=w.reindex(idx);w.index.name='hora_utc';w['MW']=w.HT1+w.HT2;ll=w.index.tz_convert('America/Santiago');w['fecha']=ll.strftime('%Y-%m-%d');w['hora0']=ll.hour;w.reset_index().to_csv(out/'carga_fisica_horaria.csv.gz',index=False)
 day=w.groupby('fecha').agg(MW=('MW','median'),horas=('MW','count'),HT1=('HT1','median'),HT2=('HT2','median'),HT3=('HT3','median'));day.loc[day.horas.ne(24),'MW']=np.nan;day.index=pd.to_datetime(day.index);day=day.reindex(pd.date_range('2024-08-01','2026-08-31',freq='D'));day.index.name='fecha';x=day.MW
 day['antes7']=x.shift(1).rolling(7,min_periods=6).median();day['despues7']=x.iloc[::-1].rolling(7,min_periods=6).median().iloc[::-1];day['delta7']=day.despues7-day.antes7;day['relativo']=day.delta7/day.antes7;day.to_csv(out/'carga_diaria.csv')
 candidates=[];raw=[]
 for label,abs_,rel in [('principal',.5,.2),('bajo',.25,.1),('alto',1,.3)]:
  z=day[day.delta7.abs().ge(abs_)&day.relativo.abs().ge(rel)].copy();z['grupo']=(z.index.to_series().diff().dt.days.gt(14)).cumsum().to_numpy()
  for group,zz in z.groupby('grupo'):
   t=zz.delta7.abs().idxmax();r=zz.loc[t];candidates.append(dict(regla=label,fecha=t.strftime('%Y-%m-%d'),antes7=r.antes7,despues7=r.despues7,delta_MW=r.delta7,relativo=r.relativo,candidatos_grupo=len(zz),inicio_grupo=zz.index.min().strftime('%Y-%m-%d'),fin_grupo=zz.index.max().strftime('%Y-%m-%d')))
  zz=z.reset_index();zz['regla']=label;raw.append(zz)
 pd.DataFrame(candidates).to_csv(out/'escalones_candidatos.csv',index=False);pd.concat(raw).to_csv(out/'escalones_detecciones_completas.csv',index=False)
 w['base24']=w.MW.shift(1).rolling(24,min_periods=20).median();flag=(w.MW-w.base24).le(-.5)&(w.MW/w.base24).le(.8);starts=flag&~flag.shift(1,fill_value=False);events=[]
 for start in w.index[starts]:
  base=w.at[start,'base24'];position=w.index.get_loc(start);tail=w.iloc[position:];rec=tail[tail.MW.ge(.9*base)]
  end=rec.index[0] if len(rec) else None;duration=(end-start).total_seconds()/3600 if end is not None else np.nan
  # Conservar toda detección de regla; distinguir recuperación, duración y solapamiento.
  seg=w.loc[start:end] if end is not None else tail
  events.append(dict(inicio_utc=str(start),inicio_local=str(start.tz_convert('America/Santiago')),recuperacion_utc=str(end) if end is not None else '',base24_MW=base,minimo_MW=seg.MW.min(),duracion_horas=duration,horas_sin_medicion=int(seg.MW.isna().sum()),HT1_inicio=w.at[start,'HT1'],HT2_inicio=w.at[start,'HT2']))
 pd.DataFrame(events).to_csv(out/'caidas_horarias_todas.csv',index=False);assert sha(a.mediciones)==before;info=dict(estado='OK',fuente='mediciones_legacy:tablas/mediciones_candidatos_15min.parquet',sha256=before,lee_precios=False,horas=int(w.MW.notna().sum()),dias_completos=int(day.MW.notna().sum()),escalones_por_regla=pd.DataFrame(candidates).regla.value_counts().to_dict(),caidas_horarias=len(events));(out/'verificacion.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2));print(pd.DataFrame(candidates).to_string(index=False));print(pd.DataFrame(events).head(20).to_string(index=False))
if __name__=='__main__':main()
