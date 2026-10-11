"""Diagnósticos exploratorios declarados en adenda; no altera conciliación principal."""
import argparse,hashlib,json,os
from pathlib import Path
import numpy as np
import pandas as pd
STAGE=Path(__file__).resolve().parents[1]; REPO=STAGE.parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--proyecto',type=Path,required=True);ap.add_argument('--mediciones-legacy',type=Path,required=True);ap.add_argument('--ejecucion',default='20261011_diagnosticos_adicionales_v1');a=ap.parse_args()
 project=a.proyecto.resolve();legacy=a.mediciones_legacy.resolve();prior=STAGE/'resultados/20261011_conciliacion_v1';out=STAGE/'resultados'/a.ejecucion
 if out.exists() or out.parent.resolve()!=(STAGE/'resultados').resolve():raise SystemExit('Ejecución nueva requerida')
 rawdir=project/'.claude/worktrees/sip-api/Panel_datos/sip_api/barrido_v2'
 raw=[rawdir/f'focal_2026-07-{day}.csv.gz' for day in ['05','15','25']]
 files=[prior/'fronteras_diarias.csv',prior/'precios_diarios_zonas_candidatas.csv.gz',prior/'conciliacion_diaria.csv',prior/'panel_zonal_mensual_exploratorio.csv',project/'Panel_datos/codex_panel_nacional/data/withdrawals/cliente_hora.parquet',legacy/'tablas/mediciones_candidatos_15min.parquet',STAGE/'ADENDA_DIAGNOSTICOS_20261011.md',Path(__file__).resolve()]+raw
 hashes=[{'archivo':str(p.relative_to(REPO)) if p.is_relative_to(REPO) else ('mediciones_legacy/'+str(p.relative_to(legacy)) if p.is_relative_to(legacy) else 'proyecto/'+str(p.relative_to(project))),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
 out.mkdir(parents=True);pd.DataFrame(hashes).to_csv(out/'insumos_sha256.csv',index=False)
 p=pd.read_csv(prior/'precios_diarios_zonas_candidatas.csv.gz');p=p[p.elegible]
 names=['CANTERAS_110','BATUCO_110','TLIBERTADORES_110','C.NAVIA_110']
 w=p[p.barra.isin(names)].pivot(index='fecha',columns='barra',values='P').reindex(columns=names).dropna()
 w['corredor']=w[['BATUCO_110','TLIBERTADORES_110','C.NAVIA_110']].mean(axis=1)
 qref=p[p.barra.eq('QUILLOTA_220')].set_index('fecha').P
 d=pd.read_csv(prior/'fronteras_diarias.csv');d=d[d.frontera.eq('Canteras_HT12_D') & d.completo].set_index('fecha')
 z=w.join(qref.rename('Q')).join((d.MWh/24).rename('MW')).dropna()
 z['D_canteras']=z.CANTERAS_110-z.Q;z['D_corredor']=z.corredor-z.Q;z['brecha_canteras_corredor']=z.CANTERAS_110-z.corredor;z['mes']=z.index.str[:7]
 z.to_csv(out/'comparacion_corredor_diaria.csv')
 m=z.groupby('mes').agg(dias=('MW','size'),MW=('MW','mean'),Q=('Q','mean'),D_canteras=('D_canteras','mean'),D_corredor=('D_corredor','mean'),brecha_canteras_corredor=('brecha_canteras_corredor','mean'))
 m=m[m.dias.ge(20)];m.to_csv(out/'comparacion_corredor_mensual.csv')
 result=[]
 for y in ['D_canteras','D_corredor','brecha_canteras_corredor']:
  for spec in ['niveles','tendencia_lineal','primeras_diferencias','diferencias_12_meses','condicional_Q']:
   x=m[['MW','Q',y]].copy()
   if spec=='primeras_diferencias':x=x.diff()
   if spec=='diferencias_12_meses':x=x.diff(12)
   x=x.dropna();X=np.column_stack([np.ones(len(x)),x.MW])
   if spec=='tendencia_lineal':X=np.column_stack([X,np.arange(len(x))])
   if spec=='condicional_Q':X=np.column_stack([X,x.Q])
   coef=np.linalg.lstsq(X,x[y],rcond=None)[0]
   result.append({'resultado':y,'especificacion':spec,'n_meses':len(x),'beta_USD_MWh_por_MW':coef[1]})
 pd.DataFrame(result).to_csv(out/'sensibilidad_espacial.csv',index=False)
 loo=[]
 for month in m.index:
  x=m.drop(index=month);X=np.column_stack([np.ones(len(x)),x.MW]);coef=np.linalg.lstsq(X,x.D_canteras,rcond=None)[0]
  loo.append({'mes_excluido':month,'beta_niveles':coef[1]})
 pd.DataFrame(loo).to_csv(out/'exclusion_mes_canteras.csv',index=False)
 # Originales ST02: diagnóstico de dos componentes, sin sustituir la clave ambigua.
 original=[]
 for f in raw:
  x=pd.read_csv(f).drop_duplicates();x=x[x.retiro.astype(str).str.contains('ESPEJO DATA',case=False)&x.barra.str.contains('ESPEJO')].copy();x['fuente']=f.name;original.append(x)
 rawx=pd.concat(original);rawx['MWh']=-rawx.medida_kwh/1000
 rawx.to_csv(out/'ST02_filas_comerciales_originales_julio.csv',index=False)
 physical=pd.read_parquet(legacy/'tablas/mediciones_candidatos_15min.parquet',columns=['IDSOCKET','etiqueta_utc','energia_D_kwh'])
 physical=physical[physical.IDSOCKET.isin(['ODATA_013_CT1_LED','ODATA_013_CT2_LED'])].copy();physical['fecha_hora']=physical.etiqueta_utc.dt.tz_convert('America/Santiago').dt.strftime('%Y-%m-%d %H:00:00')
 ph=physical.groupby(['fecha_hora','IDSOCKET']).agg(n=('energia_D_kwh','count'),MWh=('energia_D_kwh',lambda s:s.sum()/1000)).reset_index();ph=ph[ph.n.eq(4)]
 ph=ph.pivot(index='fecha_hora',columns='IDSOCKET',values='MWh').dropna()
 records=[]
 for time,x in rawx.groupby('fecha_hora'):
  if time not in ph.index:continue
  values=sorted(x.MWh);cts=sorted(ph.loc[time].tolist())
  row={'fecha_hora':time,'filas_SIP':len(values),'SIP_suma_condicional_MWh':sum(values),'CT_suma_D_MWh':sum(cts),'diferencia_MWh':sum(cts)-sum(values),'asignacion':'sin identificador individual; comparación de conjuntos, no asignación documental'}
  if len(values)==2:
   row['error_max_componentes_MWh']=max(abs(a-b) for a,b in zip(values,cts))
   row['error_componentes_abs_MWh']=sum(abs(a-b) for a,b in zip(values,cts))
  records.append(row)
 r=pd.DataFrame(records);r['fecha']=r.fecha_hora.str[:10];r.to_csv(out/'ST02_hipotesis_dos_componentes.csv',index=False)
 rd=r.groupby('fecha').agg(horas=('fecha_hora','size'),filas_SIP_por_hora=('filas_SIP','min'),SIP_MWh_condicional=('SIP_suma_condicional_MWh','sum'),CT_MWh=('CT_suma_D_MWh','sum'),error_abs_horario=('diferencia_MWh',lambda s:s.abs().sum()),error_componentes_abs=('error_componentes_abs_MWh',lambda s:s.sum(min_count=1))).reset_index()
 rd['sesgo_pct']=100*(rd.CT_MWh-rd.SIP_MWh_condicional)/rd.SIP_MWh_condicional;rd['WAPE_horario_pct']=100*rd.error_abs_horario/rd.SIP_MWh_condicional
 rd['WAPE_componentes_pct']=100*rd.error_componentes_abs/rd.SIP_MWh_condicional;rd.to_csv(out/'ST02_alternativa_condicional_resumen.csv',index=False)
 # SIP mensual es media de días muestreados completos, no energía mensual extrapolada.
 sip=pd.read_parquet(project/'Panel_datos/codex_panel_nacional/data/withdrawals/cliente_hora.parquet');sip=sip[sip.empresa.str.contains('ODATA|EdgeConneX')].copy();sip['ok']=~sip.clave_ambigua & sip.retiro_mwh.notna()
 sd=sip.groupby(['empresa','barra','fecha']).agg(n=('hora0','size'),nh=('hora0','nunique'),validas=('ok','sum'),MWh=('retiro_mwh',lambda s:s.sum(min_count=1))).reset_index()
 sd=sd[sd.n.eq(24)&sd.nh.eq(24)&sd.validas.eq(24)]
 from conciliar_canteras_odata import normal_day
 sd=sd[sd.fecha.map(normal_day)];sd['mes']=sd.fecha.str[:7]
 sm=sd.groupby(['empresa','barra','mes']).agg(dias_muestra=('fecha','size'),MW_medio_dias_muestra=('MWh',lambda x:x.mean()/24)).reset_index();sm.to_csv(out/'SIP_medias_dias_muestra_por_mes.csv',index=False)
 # Verificación puntual independiente con cifras archivadas en auditoría precedente.
 c=pd.read_csv(prior/'conciliacion_diaria.csv');c=c[c.frontera.eq('Canteras_HT12_D')&c.barra.eq('CANTERAS_110')&c.fecha.eq('2024-10-15')].iloc[0]
 if abs(c.fis_MWh-49.3030620429)>1e-8 or abs(c.SIP_MWh-49.31936523437501)>1e-8:raise ValueError('No coincide con día auditado previo')
 after=[{'archivo':r['archivo'],'sin_cambios':sha(p)==r['sha256']} for p,r in zip(files,hashes)]
 if not all(r['sin_cambios'] for r in after):raise ValueError('Insumo modificado')
 pd.DataFrame(after).to_csv(out/'verificacion_insumos.csv',index=False)
 (out/'verificacion.json').write_text(json.dumps({'estado':'OK','insumos_preservados':len(files),'originales_modificados':0,'comprobacion_20241015':'coincide con auditoría anterior','nota':'los datos comerciales ambiguos conservan esa condición; alternativa separada'},ensure_ascii=False,indent=2))
 print(pd.DataFrame(result).to_string(index=False));print(rd.to_string(index=False));print('LOO',pd.DataFrame(loo).beta_niveles.min(),pd.DataFrame(loo).beta_niveles.max())

if __name__=='__main__':main()
