"""Conciliación y panel exploratorio: lee insumos previos y escribe una ejecución nueva."""
from pathlib import Path
from datetime import datetime
import argparse, hashlib, json, subprocess
import numpy as np
import pandas as pd

STAGE=Path(__file__).resolve().parents[1]
REPO=STAGE.parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()

def normal_day(day):
 d=pd.Timestamp(day)
 return (d+pd.Timedelta(days=1)).tz_localize('America/Santiago',nonexistent='shift_forward').tz_convert('UTC')-d.tz_localize('America/Santiago',nonexistent='shift_forward').tz_convert('UTC')==pd.Timedelta(hours=24)

def daily_physical(h):
 x=h.copy(); local=x.index.tz_convert('America/Santiago')
 x['fecha']=local.strftime('%Y-%m-%d'); x['hora0']=local.hour
 d=x.groupby('fecha').agg(filas=('MWh','size'),horas=('hora0','nunique'),validas=('MWh','count'),MWh=('MWh',lambda s:s.sum(min_count=1)))
 d['completo']=d.filas.eq(24)&d.horas.eq(24)&d.validas.eq(24)&pd.Series(d.index.map(normal_day),index=d.index)
 return d

def finite_json(obj):
 return json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--proyecto',type=Path,required=True)
 ap.add_argument('--mediciones-legacy',type=Path,required=True)
 ap.add_argument('--ejecucion',default='20261011_conciliacion_v1')
 a=ap.parse_args(); project=a.proyecto.resolve(); legacy=a.mediciones_legacy.resolve()
 out=STAGE/'resultados'/a.ejecucion
 if out.exists() or out.parent.resolve()!=(STAGE/'resultados').resolve():raise SystemExit('Se requiere ejecución nueva dentro de resultados')
 national=project/'Panel_datos/codex_panel_nacional'
 period=pd.period_range('2024-08','2026-08',freq='M')
 pricefiles=[national/f'data/hourly/REAL_{p.strftime("%Y%m")}.parquet' for p in period]
 inputs=[legacy/'tablas/mediciones_candidatos_15min.parquet',national/'data/withdrawals/cliente_hora.parquet',
   project/'Panel_datos/topologia/aristas.csv',STAGE/'PROTOCOLO_CONCILIACION_20261011.md',Path(__file__).resolve(),
   REPO/'SOCHER_2026_v3/mapeo/Memo_mapeo_electrico_y_unidades.md',
   REPO/'SOCHER_2026_v6_multicentros/mapeo/relacion_centros_barras.csv',
   REPO/'SOCHER_2026_v8_panel_causal/investigacion_odata_20260927/medicion/catalogo_sockets_lampa_odata.csv']+pricefiles
 def ref(p):
  for prefix,root in [('repositorio',REPO),('mediciones_legacy',legacy),('proyecto',project)]:
   if p.is_relative_to(root):return prefix+':'+str(p.relative_to(root))
  raise ValueError(p)
 before=[{'referencia':ref(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in inputs]
 out.mkdir(parents=True)
 pd.DataFrame(before).to_csv(out/'insumos_sha256.csv',index=False)
 (out/'inicio.json').write_text(finite_json({'fecha':datetime.now().isoformat(),'commit_previo':subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),'protocolo_sha256':sha(STAGE/'PROTOCOLO_CONCILIACION_20261011.md')}))
 q=pd.read_parquet(inputs[0],columns=['IDSOCKET','etiqueta_utc','energia_D_kwh','energia_R_kwh'])
 if q.duplicated(['IDSOCKET','etiqueta_utc']).any():raise ValueError('Medición repetida')
 q['hora_utc']=q.etiqueta_utc.dt.floor('h')
 q['minuto']=q.etiqueta_utc.dt.minute
 hour=q.groupby(['IDSOCKET','hora_utc']).agg(n=('minuto','size'),nmin=('minuto','nunique'),D_n=('energia_D_kwh','count'),R_n=('energia_R_kwh','count'),D=('energia_D_kwh','sum'),R=('energia_R_kwh','sum')).reset_index()
 for c in ['D','R']:hour[c]=hour[c].where(hour.n.eq(4)&hour.nmin.eq(4)&hour[c+'_n'].eq(4))/1000
 configs={
  'Canteras_HT12_D':(['LSCANTRS_110_HT1_EDG','LSCANTRS_110_HT2_EDG'],'D'),
  'Canteras_HT3_R':(['LSCANTRS_110_HT3_EDG'],'R'),
  'ST01_J9_D':(['NUELAMPA_220_J9_ODT'],'D'),
  'ST01_JT5_D':(['LAMPA_220_JT5_ODT'],'D'),
  'ST01_JT5_R':(['LAMPA_220_JT5_ODT'],'R'),
  'ST01_ET5_D':(['LAMPA_023_ET5_ODT'],'D'),
  'ST02_CT12_D':(['ODATA_013_CT1_LED','ODATA_013_CT2_LED'],'D'),
  'ST02_HT12_R':(['ODATA_110_HT1_LED','ODATA_110_HT2_LED'],'R'),
  'ST02_HT12_D':(['ODATA_110_HT1_LED','ODATA_110_HT2_LED'],'D'),
  'ST02_SA_D':(['ODATA_000_SA_LED'],'D'),
  'ST02_Panamericana_H34_D':(['PNMRCANA_110_H3_LED','PNMRCANA_110_H4_LED'],'D')}
 phys={}; days={}; monthly=[]; hour_output=[]; day_output=[]
 for case,(sockets,channel) in configs.items():
  wide=hour[hour.IDSOCKET.isin(sockets)].pivot(index='hora_utc',columns='IDSOCKET',values=channel).reindex(columns=sockets)
  h=wide.sum(axis=1,min_count=len(sockets)).rename('MWh').to_frame();phys[case]=h
  dd=daily_physical(h);days[case]=dd
  day_output.append(dd.reset_index().assign(frontera=case))
  hour_output.append(h.reset_index().assign(frontera=case))
  valid=dd[dd.completo].copy(); valid['mes']=valid.index.str[:7]
  mm=valid.groupby('mes').agg(dias_validos=('MWh','size'),MWh_dias_validos=('MWh','sum'),MW_medio=('MWh',lambda s:s.mean()/24)).reset_index()
  mm['frontera']=case;monthly.append(mm)
 pd.concat(hour_output).to_csv(out/'fronteras_horarias.csv.gz',index=False)
 pd.concat(day_output).to_csv(out/'fronteras_diarias.csv',index=False)
 fm=pd.concat(monthly);fm.to_csv(out/'carga_mensual_dias_24h.csv',index=False)
 pd.DataFrame([{'frontera':k,'sockets':';'.join(v[0]),'canal':v[1],'calidad':'selección documental/diagnóstico; no fronteras sumables entre sí'} for k,v in configs.items()]).to_csv(out/'fronteras_definidas.csv',index=False)
 # SIP se conserva sin sumar claves ambiguas ni extrapolar meses.
 sip=pd.read_parquet(inputs[1]);sip['valido']=~sip.clave_ambigua & sip.retiro_mwh.notna()
 if sip.duplicated(['empresa','barra','fecha','hora0']).any():raise ValueError('Clave comercial repetida')
 pairs=[('Canteras_HT12_D','EdgeConneX','CANTERAS_110','principal'),
 ('Canteras_HT12_D','EdgeConneX','BATUCO_013','transicion_no_identidad'),
 ('ST01_J9_D','ODATA','LAMPA_220','principal_candidato'),
 ('ST01_JT5_D','ODATA','LAMPA_220','balance_canal'),
 ('ST01_ET5_D','ODATA','LAMPA_220','balance_canal'),
 ('ST01_J9_D','ODATA','BATUCO_013','transicion_no_identidad'),
 ('ST02_CT12_D','ODATA ST02 (Lo Espejo Data Center)','PANAMERICANA_012','suministro_previo_candidato'),
 ('ST02_CT12_D','ODATA ST02 (Lo Espejo Data Center)','LO_ESPEJO_110','principal_candidato')]
 daycomparisons=[]; hours_comparisons=[]; stats=[]; shifts=[]
 for case,company,bar,role in pairs:
  x=sip[(sip.empresa==company)&(sip.barra==bar)].copy()
  dd=x.groupby('fecha').agg(n=('hora0','size'),nh=('hora0','nunique'),nv=('valido','sum'),SIP_MWh=('retiro_mwh',lambda s:s.sum(min_count=1)))
  dd['completo_SIP']=dd.n.eq(24)&dd.nh.eq(24)&dd.nv.eq(24)&pd.Series(dd.index.map(normal_day),index=dd.index)
  joint=days[case].add_prefix('fis_').join(dd,how='inner')
  joint['elegible']=joint.fis_completo & joint.completo_SIP
  joint['diferencia_MWh']=joint.fis_MWh-joint.SIP_MWh
  joint['error_rel_pct']=100*joint.diferencia_MWh/joint.SIP_MWh.replace(0,np.nan)
  joint['frontera']=case;joint['empresa']=company;joint['barra']=bar;joint['rol']=role
  daycomparisons.append(joint.reset_index())
  usable=joint[joint.elegible]
  stat={'frontera':case,'barra':bar,'rol':role,'dias_solapados':len(joint),'dias_elegibles':len(usable)}
  if len(usable):
   den=usable.SIP_MWh.sum();stat.update({'fis_MWh':usable.fis_MWh.sum(),'SIP_MWh':den,'sesgo_pct':100*usable.diferencia_MWh.sum()/den if den else None,
     'WAPE_diario_pct':100*usable.diferencia_MWh.abs().sum()/den if den else None,
     'dias_error_hasta_1pct':int(usable.error_rel_pct.abs().le(1).sum()),'dias_error_hasta_5pct':int(usable.error_rel_pct.abs().le(5).sum()),
     'desde':usable.index.min(),'hasta':usable.index.max()})
  stats.append(stat)
  # Hipótesis de reloj, no selección de la de menor error.
  for clock,delta in [('local',0),('UTC',0),('local',-1),('local',1)]:
   h=phys[case].copy();dt=h.index.tz_convert('America/Santiago') if clock=='local' else h.index
   dt=dt+pd.Timedelta(hours=delta);h['fecha']=dt.strftime('%Y-%m-%d');h['hora0']=dt.hour
   h=h[~h.duplicated(['fecha','hora0'],keep=False)]
   z=x[x.valido].merge(h,on=['fecha','hora0'],how='inner',validate='one_to_one').dropna(subset=['MWh'])
   z=z[z.fecha.isin(usable.index)]
   den=z.retiro_mwh.sum();error=z.MWh-z.retiro_mwh
   shifts.append({'frontera':case,'barra':bar,'reloj_fisico':clock,'desplazamiento_etiqueta_h':delta,'pares':len(z),'WAPE_horario_pct':100*error.abs().sum()/den if den else None,'sesgo_pct':100*error.sum()/den if den else None})
   if clock=='local' and delta==0:
    hours_comparisons.append(z[['fecha','hora0','retiro_mwh','MWh']].assign(frontera=case,barra=bar))
 pd.concat(daycomparisons).to_csv(out/'conciliacion_diaria.csv',index=False)
 pd.concat(hours_comparisons).to_csv(out/'conciliacion_horaria_local.csv.gz',index=False)
 pd.DataFrame(stats).to_csv(out/'resumen_conciliacion.csv',index=False)
 pd.DataFrame(shifts).to_csv(out/'sensibilidad_reloj.csv',index=False)
 # Balances internos: diferencia de canales publicados, sin inferir causa ni cambiar signos.
 balances=[]
 for left,right in [('ST01_J9_D','ST01_JT5_D'),('ST01_JT5_D','ST01_ET5_D'),('ST02_HT12_R','ST02_CT12_D'),('ST02_Panamericana_H34_D','ST02_HT12_R')]:
  z=days[left][days[left].completo][['MWh']].join(days[right][days[right].completo][['MWh']],lsuffix='_A',rsuffix='_B',how='inner')
  z['A']=left;z['B']=right;z['diferencia_MWh']=z.MWh_A-z.MWh_B
  z['mes']=z.index.str[:7];balances.append(z.reset_index())
 b=pd.concat(balances);b.to_csv(out/'balances_canales_diarios.csv',index=False)
 b.groupby(['A','B','mes']).agg(dias=('fecha','size'),MWh_A=('MWh_A','sum'),MWh_B=('MWh_B','sum'),diferencia_MWh=('diferencia_MWh','sum')).reset_index().to_csv(out/'balances_canales_mensuales.csv',index=False)
 # Precios por nodo de las zonas candidatas; no controles independientes por decreto.
 bars=['CANTERAS_110','CANTERAS_023','BATUCO_110','BATUCO_013','TLIBERTADORES_110','C.NAVIA_110','C.NAVIA_220','LAMPA_220','LAMPA_023','NVALAMPA_220','POLPAICO_220','PANAMERICANA_110','PANAMERICANA_012','LO_ESPEJO_110','QUILLOTA_220']
 priceparts=[]
 for f in pricefiles:
  d=pd.read_parquet(f,columns=['barra','fecha','hora0','cmg_usd_mwh','quillota_220_usd_mwh','spread_usd_mwh'],filters=[('barra','in',bars)])
  if d.duplicated(['barra','fecha','hora0']).any():raise ValueError('Precio duplicado')
  if (d.cmg_usd_mwh-d.quillota_220_usd_mwh-d.spread_usd_mwh).abs().max()>1e-7:raise ValueError('D no coincide')
  d['valido']=d[['cmg_usd_mwh','quillota_220_usd_mwh']].notna().all(axis=1)
  daily=d.groupby(['barra','fecha']).agg(filas=('hora0','size'),horas=('hora0','nunique'),validas=('valido','sum'),P=('cmg_usd_mwh','mean'),Q=('quillota_220_usd_mwh','mean'),D=('spread_usd_mwh','mean')).reset_index()
  daily['elegible']=daily.filas.eq(24)&daily.horas.eq(24)&daily.validas.eq(24)&daily.fecha.map(normal_day)
  priceparts.append(daily)
 prices=pd.concat(priceparts);prices.to_csv(out/'precios_diarios_zonas_candidatas.csv.gz',index=False)
 price_month=prices[prices.elegible].assign(mes=lambda d:d.fecha.str[:7]).groupby(['barra','mes']).agg(dias=('fecha','size'),P=('P','mean'),D=('D','mean'),Q=('Q','mean')).reset_index()
 price_month.to_csv(out/'precios_mensuales_zonas_candidatas.csv',index=False)
 # Panel mensual de carga/precios calculado sobre los mismos días válidos por pareja.
 links=[('Canteras_HT12_D','CANTERAS_110','enlace_documentado_BP1'),('ST01_J9_D','LAMPA_220','proxy_conexion_BP_pendiente'),('ST01_J9_D','NVALAMPA_220','proxy_conexion_BP_pendiente'),('ST02_CT12_D','LO_ESPEJO_110','proxy_comercial_fisico_pendiente'),('ST02_CT12_D','PANAMERICANA_110','aguas_arriba_no_consumo_exclusivo')]
 panels=[]
 for case,bar,quality in links:
  d=days[case][days[case].completo][['MWh']].reset_index().merge(prices[(prices.barra==bar)&prices.elegible],on='fecha',validate='one_to_one')
  d['mes']=d.fecha.str[:7];d['MW']=d.MWh/24
  m=d.groupby('mes').agg(dias_comunes=('fecha','size'),MW=('MW','mean'),P=('P','mean'),D=('D','mean'),Q=('Q','mean')).reset_index()
  m['frontera']=case;m['barra']=bar;m['calidad_enlace']=quality;panels.append(m)
 panel=pd.concat(panels);panel.to_csv(out/'panel_zonal_mensual_exploratorio.csv',index=False)
 # Diagnóstico predefinido: solo Canteras, sin intervalos o p-values causales.
 z=panel[(panel.frontera=='Canteras_HT12_D')&(panel.dias_comunes>=20)].set_index('mes').sort_index()
 results=[]
 for outcome in ['P','D']:
  for mode in ['niveles','tendencia_lineal','primeras_diferencias','diferencias_12_meses']:
   xy=z[['MW',outcome]].copy()
   if mode=='primeras_diferencias':xy=xy.diff()
   if mode=='diferencias_12_meses':xy=xy.diff(12)
   xy=xy.dropna(); t=np.arange(len(xy));X=np.column_stack([np.ones(len(xy)),xy.MW])
   if mode=='tendencia_lineal':X=np.column_stack([X,t])
   coef=np.linalg.lstsq(X,xy[outcome],rcond=None)[0]
   results.append({'resultado':outcome,'especificacion':mode,'meses':len(xy),'coeficiente_USD_MWh_por_MW':coef[1],'correlacion_simple':xy.MW.corr(xy[outcome]),'interpretacion':'asociación exploratoria; no ATT ni efecto causal'})
 pd.DataFrame(results).to_csv(out/'diagnostico_canteras_carga_precio.csv',index=False)
 after=[{'referencia':r['referencia'],'sha256_igual':sha(p)==r['sha256']} for p,r in zip(inputs,before)]
 if not all(r['sha256_igual'] for r in after):raise ValueError('Insumo modificado')
 pd.DataFrame(after).to_csv(out/'verificacion_insumos.csv',index=False)
 (out/'verificacion.json').write_text(finite_json({'estado':'OK','insumos_preservados':len(inputs),'originales_modificados':0,'nuevas_descargas':0,'regresiones_causales':0,'meses_canteras_diagnostico':len(z),'protocolo_sha256':sha(STAGE/'PROTOCOLO_CONCILIACION_20261011.md')}))
 print(pd.DataFrame(stats).to_string(index=False));print(pd.DataFrame(results).to_string(index=False))

if __name__=='__main__':main()
