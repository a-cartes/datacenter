#!/usr/bin/env python3
"""Audita las particiones completas del módulo moderno y consolida cobertura (no versiones)."""
import datetime as dt, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from descargar_extraer_moderno import valid_identity
B=Path(__file__).resolve().parents[1];D=B/'datos';M=B/'fuentes/metadatos'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def roundtrip(parquet,csv_path):
 csv=pd.read_csv(csv_path,dtype={c:str for c in parquet.select_dtypes(include=['object','string']).columns},keep_default_na=False,low_memory=False,float_precision='round_trip')
 assert parquet.shape==csv.shape and list(parquet.columns)==list(csv.columns),csv_path
 worst=0.0
 for col in parquet.columns:
  if pd.api.types.is_float_dtype(parquet[col]):
   observed=pd.to_numeric(csv[col],errors='coerce').to_numpy();expected=parquet[col].to_numpy()
   assert np.array_equal(np.isnan(expected),np.isnan(observed)),(csv_path,col,'nulls')
   finite=np.isfinite(expected);error=float(np.max(np.abs(expected[finite]-observed[finite]))) if finite.any() else 0.0
   assert error<=1e-12,(csv_path,col,error)
   worst=max(worst,error)
  else:assert parquet[col].astype(str).equals(csv[col].astype(str)),(csv_path,col)
 return worst
def main():
 tests=[];coverage=[];daily=[];identities=[];sources=[];flags=[]
 for p in sorted(M.glob('*_extraccion.json')):
  e=json.loads(p.read_text());assert e.get('schema_version')=='moderno_v7.1',p
  stem=p.name.removesuffix('_extraccion.json');s=json.loads((M/(stem+'.json')).read_text());sources.append(s)
  q=pd.read_parquet(D/(stem+'_15min.parquet'));h=pd.read_parquet(D/(stem+'_horario.parquet'))
  err=roundtrip(h,D/(stem+'_horario.csv.gz'))
  err15=roundtrip(q,D/(stem+'_15min.csv.gz'))
  assert q.fecha.ge('2024-07-15').all() and q.fecha.le('2026-09-27').all()
  parsed_dates=pd.to_datetime(q.fecha,format='%Y-%m-%d',errors='raise')
  assert parsed_dates.dt.strftime('%Y-%m').eq(e['mes']).all(),(stem,'fecha fuera del mes publicado')
  assert q.hora_fuente.between(0,24).all() and q.minuto_fuente.isin([0,15,30,45]).all()
  assert set(q.version)=={'REAL-'+e['version']} and set(h.version)==set(q.version)
  assert not q.duplicated(['id_info','barra_cmg','fecha','hora_fuente','minuto_fuente','version']).any()
  assert h.n_intervalos.sum()==len(q)
  assert h.hora_completa_4_intervalos.equals(h.n_intervalos.eq(4)&h.minutos_observados.eq('0,15,30,45'))
  assert h.loc[~h.hora_completa_4_intervalos,'precio_usd_mwh_horario'].isna().all()
  for path,digest in e['outputs'].items():assert sha(B/path)==digest,path
  raw=B/s['archivo'];assert sha(raw)==s['sha256_gzip_local'],raw
  cv=pd.read_csv(D/(stem+'_cobertura.csv'),dtype={'id_info':str},keep_default_na=False)
  cv['mes_fuente']=e['mes'];cv['fuente_tsv_sha256']=s['sha256_tsv_descomprimido'];coverage.append(cv)
  day=q.groupby(['id_info','barra_cmg','fecha','version'],dropna=False).agg(n_intervalos=('minuto_fuente','size'),n_horas=('hora_fuente','nunique'),min_hora=('hora_fuente','min'),max_hora=('hora_fuente','max')).reset_index();daily.append(day)
  ident=q[['id_info','barra_cmg','barra_info','version','criterio_seleccion','identidad','marca_fuente','tension_kv_nombre']].drop_duplicates();ident['mes_fuente']=e['mes'];identities.append(ident)
  flagged=q.groupby(['barra_cmg','id_info','marca_fuente','identidad','version'],dropna=False).agg(n_intervalos=('fecha','size'),fecha_min=('fecha','min'),fecha_max=('fecha','max')).reset_index();flagged['mes_fuente']=e['mes'];flags.append(flagged)
  tests.append({'mes':e['mes'],'version':e['version'],'filas_15min':len(q),'filas_horario':len(h),
    'barras_etiquetas':int(q.barra_cmg.nunique()),'barras_con_id_y_nombre':int(q[valid_identity(q)].barra_cmg.nunique()),
    'fecha_min':q.fecha.min(),'fecha_max':q.fecha.max(),'n_dias':int(q.fecha.nunique()),
    'ultima_hora_fuente':int(q.loc[q.fecha.eq(q.fecha.max()),'hora_fuente'].max()),
    'ultimo_minuto_fuente':int(q.loc[q.fecha.eq(q.fecha.max()) & q.hora_fuente.eq(q.loc[q.fecha.eq(q.fecha.max()),'hora_fuente'].max()),'minuto_fuente'].max()),
    'n_horas_ultimo_dia':int(q.loc[q.fecha.eq(q.fecha.max()),'hora_fuente'].nunique()),
    'filas_sin_id_o_nombre':int((~valid_identity(q)).sum()),'horas_incompletas':int((~h.hora_completa_4_intervalos).sum()),
    'duplicados_etiqueta_tiempo_sin_id':int(q.duplicated(['barra_cmg','fecha','hora_fuente','minuto_fuente','version']).sum()),
    'max_error_csv_parquet':err,'max_error_csv_parquet_15min':err15,'cabeceras_originales':e['cabeceras_originales']})
  print(json.dumps({'fase':'verificado',**tests[-1]},ensure_ascii=False),flush=True)
 pd.concat(coverage,ignore_index=True).to_csv(D/'cobertura_barras_meses_moderno.csv',index=False,encoding='utf-8-sig')
 pd.concat(daily,ignore_index=True).to_csv(D/'cobertura_diaria_etiquetas_moderno.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 pd.concat(identities,ignore_index=True).to_csv(D/'identidades_publicadas_por_mes.csv',index=False,encoding='utf-8-sig')
 pd.concat(flags,ignore_index=True).to_csv(D/'resumen_marcas_fuente.csv',index=False,encoding='utf-8-sig')
 pd.DataFrame(tests).drop(columns='cabeceras_originales').to_csv(D/'resumen_particiones_moderno.csv',index=False,encoding='utf-8-sig')
 revision={}
 if (D/'202609_DEF_15min.parquet').exists() and (D/'202609_PRE_15min.parquet').exists():
  keys=['id_info','barra_cmg','fecha','hora_fuente','minuto_fuente']
  r=pd.read_parquet(D/'202609_DEF_15min.parquet',columns=keys+['precio_usd_mwh'])
  p=pd.read_parquet(D/'202609_PRE_15min.parquet',columns=keys+['precio_usd_mwh'])
  x=r.merge(p,on=keys,suffixes=('_def','_pre'),validate='one_to_one')
  x['diferencia_def_menos_pre']=x.precio_usd_mwh_def-x.precio_usd_mwh_pre
  different=x[x.diferencia_def_menos_pre.abs()>1e-9]
  different.to_csv(D/'diferencias_pre_def_septiembre2026.csv',index=False,encoding='utf-8-sig')
  revision={'n_observaciones_solapadas':len(x),'n_distintas':len(different),'max_diferencia_absoluta_usd_mwh':float(x.diferencia_def_menos_pre.abs().max()),'archivo':'datos/diferencias_pre_def_septiembre2026.csv','sha256':sha(D/'diferencias_pre_def_septiembre2026.csv')}
 report={'revision_pre_def_septiembre':revision,'fecha_verificacion_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'corte_estudio':'2026-09-27','particiones':tests,
  'n_meses_def':sum(x['version']=='DEF' for x in tests),'n_meses_pre':sum(x['version']=='PRE' for x in tests),
  'filas_15min_def':sum(x['filas_15min'] for x in tests if x['version']=='DEF'),'filas_horarias_def':sum(x['filas_horario'] for x in tests if x['version']=='DEF'),
  'fecha_max_def':max(x['fecha_max'] for x in tests if x['version']=='DEF'),
  'fecha_max_pre':max((x['fecha_max'] for x in tests if x['version']=='PRE'),default=None),
  'bytes_fuentes_tsv':sum(x['bytes_tsv_original'] for x in sources),'bytes_gzip_local':sum(x['bytes_gzip_local'] for x in sources),
  'script_sha256':sha(Path(__file__)),'seleccion_sha256':sha(B/'config/seleccion_barras_v6.csv'),
  'advertencias':['PRE y DEF se mantienen separados; no sumar como observaciones independientes.',
    'Capa de precios candidatos: disponibilidad e ID no prueban vínculo a centro ni evento.',
    'Campos horarios originales sin UTC; puente con régimen histórico pendiente de conciliación.',
    'Promedio horario aritmético de cuatro intervalos; no es precio ponderado por consumo.'],
  'resumenes_sha256':{str(p.relative_to(B)):sha(p) for p in [D/'cobertura_barras_meses_moderno.csv',D/'cobertura_diaria_etiquetas_moderno.csv.gz',D/'identidades_publicadas_por_mes.csv',D/'resumen_particiones_moderno.csv',D/'resumen_marcas_fuente.csv']}}
 verification=B/'verificacion_moderno.json';temporary=verification.with_suffix('.json.tmp')
 temporary.write_text(json.dumps(report,ensure_ascii=False,indent=2));temporary.replace(verification)
 print(json.dumps({k:v for k,v in report.items() if k not in ['particiones','resumenes_sha256']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
