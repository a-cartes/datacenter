#!/usr/bin/env python3
"""Descarga TSV públicos del botón oficial CEN y preserva versiones y granularidad.

Ejemplo: python descargar_extraer_moderno.py --months 2025-06 2026-09 --include-pre-septiembre
No necesita API key. Utiliza el patrón validado del JavaScript público temporal.js.
No mezcla PRE con DEF ni convierte ID_INFO a nemotécnico histórico.
"""
from __future__ import annotations
import argparse, collections, concurrent.futures, csv, datetime as dt, gzip, hashlib, json, os, re, sys, time, unicodedata, urllib.request, urllib.error
from pathlib import Path
import pandas as pd
import numpy as np
B=Path(__file__).resolve().parents[1];ROOT=B.parents[1]
RAW=B/'fuentes/tsv_originales';DATA=B/'datos';META=B/'fuentes/metadatos'
CUTOFF='2026-09-27'
BASEURL='https://cen-datalake-public.s3.amazonaws.com/costos_marginales/CMG_REAL'
V6=B/'config/seleccion_barras_v6.csv' # Copia exacta preservada para reproducción fuera del proyecto original
# Búsqueda ampliada para equipos sin código adjudicado en v6; solo selecciona precios, no prueba vínculo a un centro.
EXTRA=['NUEVALAMPA','NUELAMPA','SANTATERESA','STATERESA','SNTERESA','ODATA','LOCAMPINO','PUNTAVERDE','PUDAHUEL','COLINA','CURAUMA','QUILICURA']
HEAD=['ID_INFO','BARRA_INFO','BARRA_TRANSF','FECHA','HRA','MIN','CMg[USD/MWh]','CMg[CLP/KWh]','VERSION']

def emit(x):print(json.dumps(x,ensure_ascii=False),flush=True)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def url(month,version):
 y,m=map(int,month.split('-'));return f'{BASEURL}/{y}/{m}/{y}_{m:02}_REAL-{version}.tsv'
def pathstem(month,version):return month.replace('-','')+'_'+version

def download_unlocked(month,version):
 stem=pathstem(month,version);u=url(month,version);raw=RAW/(stem+'.tsv.gz');meta=META/(stem+'.json')
 if raw.exists() and meta.exists():
  record=json.loads(meta.read_text());assert sha(raw)==record['sha256_gzip_local'];emit({'fase':'fuente_preservada','mes':month,'version':version});return record
 frozen=json.loads(meta.read_text()) if meta.exists() else None
 with urllib.request.urlopen(urllib.request.Request(u,method='HEAD'),timeout=60) as r:
  head=dict(r.headers.items());etag=r.headers.get('ETag');expected=int(r.headers.get('Content-Length'));last=r.headers.get('Last-Modified')
 if frozen and (frozen['etag']!=etag or frozen['bytes_tsv_original']!=expected):
  raise ValueError('Fuente remota cambió respecto del manifiesto preservado; no sobrescribir: '+stem)
 start=dt.datetime.now(dt.timezone.utc).isoformat();h=hashlib.sha256();count=0;t0=time.monotonic();lastout=t0
 partial=raw.with_suffix('.gz.partial.'+str(os.getpid()))
 with urllib.request.urlopen(urllib.request.Request(u,headers={'If-Match':etag}),timeout=60) as r:
  assert r.status==200 and r.headers.get('ETag')==etag
  with partial.open('wb') as target,gzip.GzipFile(filename='',mode='wb',fileobj=target,compresslevel=1,mtime=0) as zipped:
   for chunk in iter(lambda:r.read(1048576),b''):
    h.update(chunk);count+=len(chunk);zipped.write(chunk)
    if time.monotonic()-lastout>20:emit({'fase':'descarga','mes':month,'version':version,'MB':round(count/1e6,1),'de_MB':round(expected/1e6,1)});lastout=time.monotonic()
 assert count==expected,(count,expected)
 if frozen:assert h.hexdigest()==frozen['sha256_tsv_descomprimido'],'SHA256 TSV no coincide con versión preservada'
 partial.replace(raw)
 rec={'mes':month,'version_solicitada':version,'url':u,'origen_patron':'https://www.coordinador.cl/wp-content/themes/coordinador-electrico/assets/js/temporal.js?v=2.0; líneas1458–1522 observadas el2026-09-27',
  'consulta_inicio_utc':start,'consulta_fin_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'http_status':200,
  'etag':etag,'last_modified':last,'bytes_tsv_original':count,'bytes_gzip_local':raw.stat().st_size,
  'sha256_tsv_descomprimido':h.hexdigest(),'sha256_gzip_local':sha(raw),'archivo':str(raw.relative_to(B)),
  'precaucion':'ETag multipart no equivale a MD5; SHA256 calculado sobre todos los bytes TSV recibidos',
  'cabeceras_http':head,'segundos':round(time.monotonic()-t0,1)}
 meta.write_text(json.dumps(rec,ensure_ascii=False,indent=2));emit({'fase':'descarga_completa','mes':month,'version':version,'MB_red':round(count/1e6,1),'MB_gzip':round(raw.stat().st_size/1e6,1),'segundos':rec['segundos']});return rec

def download(month,version):
 stem=pathstem(month,version);raw=RAW/(stem+'.tsv.gz');meta=META/(stem+'.json');lock=RAW/(stem+'.download.lock')
 started=time.monotonic()
 while True:
  if raw.exists() and meta.exists():return download_unlocked(month,version)
  # Respeta también el parcial del primer proceso de esta ejecución, anterior a los locks.
  if raw.with_suffix('.gz.partial').exists():
   if time.monotonic()-started>10800:raise TimeoutError('Fuente aún ocupada por otro proceso: '+stem)
   time.sleep(10);continue
  try:
   fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
   os.write(fd,str(os.getpid()).encode());os.close(fd);break
  except FileExistsError:
   if time.monotonic()-started>10800:raise TimeoutError('Lock de descarga persistente: '+stem)
   time.sleep(10)
 try:
  for attempt in range(3):
   try:return download_unlocked(month,version)
   except (TimeoutError,urllib.error.URLError) as err:
    if isinstance(err,urllib.error.HTTPError) and err.code in [401,403,404,412]:raise
    emit({'fase':'error_transitorio_descarga','mes':month,'version':version,'intento':attempt+1,'error':str(err)})
    if attempt==2:raise
    time.sleep([5,20][attempt])
 finally:
  lock.unlink(missing_ok=True)

def norm(value):return ''.join(c for c in unicodedata.normalize('NFKD',str(value).upper()) if c.isalnum())
def valid_identity(frame):
 # Preserva marcadores literales de la fuente; 0 y nombres de relleno no acreditan identidad.
 ids=frame.id_info.str.strip();names=frame.barra_info.str.strip().str.lower()
 return ids.str.fullmatch(r'[1-9][0-9]*') & ~names.isin(['','-','nan','null','none'])
def extract(month,version):
 stem=pathstem(month,version);raw=RAW/(stem+'.tsv.gz');meta=json.loads((META/(stem+'.json')).read_text())
 assert sha(raw)==meta['sha256_gzip_local'],'Fuente gzip alterada antes de extraer'
 inv=pd.read_csv(V6,keep_default_na=False);fixed={x.strip() for entry in inv.etiquetas_cmg_halladas for x in entry.split('|') if x.strip()}
 aliases={x.strip() for entry in inv.aliases_busqueda_literales for x in entry.split('|') if x.strip()}
 selected=[];catalog=[];nraw=0;all_dates=set();minutes=set();versions=set();selected_map={};started=time.monotonic();original_headers=None
 # Los tipos se leen como texto antes de convertir precios y horarios; preserva ID_INFO sin decimales.
 for chunk in pd.read_csv(raw,sep='\t',compression='gzip',dtype=str,keep_default_na=False,chunksize=300000):
  if original_headers is None:original_headers=list(chunk.columns)
  assert list(chunk.columns)==original_headers,'Cabecera cambia entre bloques del mismo archivo'
  chunk=chunk.rename(columns={'CMg[mills/kWh]':'CMg[USD/MWh]','CMg[$/KWh]':'CMg[CLP/KWh]'})
  assert list(chunk.columns)==HEAD,list(chunk.columns)
  nraw+=len(chunk);all_dates.update(chunk.FECHA.unique());minutes.update(chunk.MIN.unique());versions.update(chunk.VERSION.unique())
  u=chunk[['ID_INFO','BARRA_INFO','BARRA_TRANSF']].drop_duplicates()
  for row in u.itertuples(index=False,name=None):
   if row not in selected_map:
    fixed_match=row[2] in fixed
    family_match=re.sub(r'_?\d{3}$','',row[2]).rstrip('_') in aliases
    text=norm(row[1])+norm(row[2]);terms=[t for t in EXTRA if t in text]
    selected_map[row]=(fixed_match or family_match or bool(terms),'etiqueta_literal_v6' if fixed_match else 'familia_etiqueta_v6_nivel_tension_publicado' if family_match else 'busqueda_candidata:'+','.join(terms))
  mask=[selected_map[(i,n,b)][0] for i,n,b in zip(chunk.ID_INFO,chunk.BARRA_INFO,chunk.BARRA_TRANSF)]
  subset=chunk.loc[mask].copy()
  if len(subset):selected.append(subset)
  cat=chunk.groupby(['ID_INFO','BARRA_INFO','BARRA_TRANSF'],sort=False).agg(fecha_min=('FECHA','min'),fecha_max=('FECHA','max'),n_observaciones=('FECHA','size')).reset_index();catalog.append(cat)
 assert min(all_dates)>='2024-07-15',min(all_dates)
 assert max(all_dates)<=CUTOFF,(max(all_dates),CUTOFF)
 assert versions=={'REAL-'+version},versions
 assert minutes<={'0','15','30','45'},minutes
 d=pd.concat(selected,ignore_index=True)
 for field in ['HRA','MIN']:d[field]=pd.to_numeric(d[field],errors='raise').astype('int16')
 for field in ['CMg[USD/MWh]','CMg[CLP/KWh]']:d[field]=pd.to_numeric(d[field].str.replace(',','.',regex=False),errors='raise')
 assert np.isfinite(d[['CMg[USD/MWh]','CMg[CLP/KWh]']].to_numpy()).all()
 assert not d.duplicated(['ID_INFO','BARRA_TRANSF','FECHA','HRA','MIN','VERSION']).any()
 # Mantener nombres publicados y etiqueta horaria original 0..24. No asumir UTC ni cambiar fecha de HRA24.
 d=d.rename(columns={'ID_INFO':'id_info','BARRA_INFO':'barra_info','BARRA_TRANSF':'barra_cmg','FECHA':'fecha','HRA':'hora_fuente','MIN':'minuto_fuente','CMg[USD/MWh]':'precio_usd_mwh','CMg[CLP/KWh]':'precio_clp_kwh','VERSION':'version'})
 d['criterio_seleccion']=[selected_map[(i,n,b)][1] for i,n,b in zip(d.id_info,d.barra_info,d.barra_cmg)]
 d['regimen']='CMg_Real_nuevo_desde_2024-07-15';d['mes_fuente']=month;d['archivo_fuente']=raw.name
 d['unidad_precio_fuente']=original_headers[6];d['unidad_precio_local_fuente']=original_headers[7];d['factor_numerico_usd_mwh']=1
 d['canal_publicacion']='TSV_mensual_CMG_REAL';d['resolucion_minutos']=15;d['convencion_hora']='HRA0_a24_y_MIN_originales_sin_UTC'
 d['sha256_tsv_fuente']=meta['sha256_tsv_descomprimido'];d['fecha_consulta_utc']=meta['consulta_fin_utc']
 d['marca_fuente']=d.barra_info.str.findall(r'\[[^\]]+\]').str.join('|')
 d['tension_kv_nombre']=pd.to_numeric(d.barra_info.str.extract(r'(\d+(?:[.,]\d+)?)\s*[kK][vV]',expand=False).str.replace(',','.',regex=False),errors='coerce')
 d['identidad']=np.where(valid_identity(d),'ID_INFO_y_nombre_publicados_en_TSV;sin_conversion_a_nemotecnico_historico','candidato_sin_ID_INFO_o_nombre_no_elegible_automaticamente')
 d=d.sort_values(['barra_cmg','id_info','fecha','hora_fuente','minuto_fuente']).reset_index(drop=True)
 p15=DATA/(stem+'_15min.parquet');d.to_parquet(p15,index=False,compression='zstd')
 csv15=DATA/(stem+'_15min.csv.gz');d.to_csv(csv15,index=False,compression={'method':'gzip','mtime':0})
 keys=['id_info','barra_cmg','barra_info','fecha','hora_fuente','version']
 h=d.groupby(keys,sort=True,dropna=False).agg(precio_usd_mwh_media=('precio_usd_mwh','mean'),precio_clp_kwh_media=('precio_clp_kwh','mean'),n_intervalos=('minuto_fuente','size'),minutos_observados=('minuto_fuente',lambda x:','.join(map(str,sorted(set(x)))))).reset_index()
 h['hora_completa_4_intervalos']=h.n_intervalos.eq(4)&h.minutos_observados.eq('0,15,30,45')
 # Horas incompletas se preservan con media observada y bandera; no se llaman promedios horarios completos.
 h['precio_usd_mwh_horario']=h.precio_usd_mwh_media.where(h.hora_completa_4_intervalos)
 h['precio_clp_kwh_horario']=h.precio_clp_kwh_media.where(h.hora_completa_4_intervalos)
 h['regimen']='CMg_Real_nuevo_desde_2024-07-15';h['unidad_temporal_fuente']='15_minutos;HRA0_a24_y_MIN_originales_sin_UTC'
 h['unidad_precio_fuente']=original_headers[6];h['unidad_precio_local_fuente']=original_headers[7];h['factor_numerico_usd_mwh']=1
 h['canal_publicacion']='TSV_mensual_CMG_REAL';h['resolucion_minutos']=60;h['fecha_consulta_utc']=meta['consulta_fin_utc']
 h['criterio_seleccion']=[selected_map[(i,n,b)][1] for i,n,b in zip(h.id_info,h.barra_info,h.barra_cmg)]
 h['identidad']=np.where(valid_identity(h),'ID_INFO_y_nombre_publicados_en_TSV;sin_conversion_a_nemotecnico_historico','candidato_sin_ID_INFO_o_nombre_no_elegible_automaticamente')
 h['marca_fuente']=h.barra_info.str.findall(r'\[[^\]]+\]').str.join('|')
 h['mes_fuente']=month;h['archivo_fuente']=raw.name;h['sha256_tsv_fuente']=meta['sha256_tsv_descomprimido']
 hp=DATA/(stem+'_horario.parquet');h.to_parquet(hp,index=False,compression='zstd')
 hc=DATA/(stem+'_horario.csv.gz');h.to_csv(hc,index=False,compression={'method':'gzip','mtime':0})
 cats=pd.concat(catalog).groupby(['ID_INFO','BARRA_INFO','BARRA_TRANSF'],sort=True).agg(fecha_min=('fecha_min','min'),fecha_max=('fecha_max','max'),n_observaciones=('n_observaciones','sum')).reset_index()
 cats['seleccionado']=[selected_map[(i,n,b)][0] for i,n,b in zip(cats.ID_INFO,cats.BARRA_INFO,cats.BARRA_TRANSF)]
 cp=DATA/(stem+'_catalogo_barras.csv');cats.to_csv(cp,index=False,encoding='utf-8-sig')
 cov=d.groupby(['barra_cmg','id_info','barra_info','version'],sort=True).agg(fecha_min=('fecha','min'),fecha_max=('fecha','max'),n_dias=('fecha','nunique'),n_intervalos=('fecha','size'),marca_fuente=('marca_fuente','first')).reset_index()
 cv=DATA/(stem+'_cobertura.csv');cov.to_csv(cv,index=False,encoding='utf-8-sig')
 check={'mes':month,'version':version,'cabeceras_originales':original_headers,'schema_version':'moderno_v7.1','normalizacion_unidades':'mills/kWh numéricamente USD/MWh, factor1; signo$ fuenteCEN: pesos chilenos; etiquetasoriginalespreservadas','filas_nacionales':nraw,'filas_seleccionadas_15min':len(d),'filas_horarias':len(h),'barras_etiquetas':int(d.barra_cmg.nunique()),'pares_barra_id':len(cov),
  'fecha_min_nacional':min(all_dates),'fecha_max_nacional':max(all_dates),'fecha_min_seleccionada':d.fecha.min(),'fecha_max_seleccionada':d.fecha.max(),'minutos_publicados':sorted(minutes),'versiones':sorted(versions),
  'horas_fuente':sorted(int(x) for x in d.hora_fuente.unique()),'horas_incompletas':int((~h.hora_completa_4_intervalos).sum()),'filas_sin_id_o_nombre':int((~valid_identity(d)).sum()),'duplicados_clave':0,'seleccion_v6_sha256':sha(V6),
  'script_sha256':sha(Path(__file__)),'outputs':{str(p.relative_to(B)):sha(p) for p in [p15,csv15,hp,hc,cp,cv]},'segundos_extraccion':round(time.monotonic()-started,1)}
 (META/(stem+'_extraccion.json')).write_text(json.dumps(check,ensure_ascii=False,indent=2));emit({'fase':'extraccion_completa',**{k:check[k] for k in ['mes','version','filas_seleccionadas_15min','filas_horarias','barras_etiquetas','fecha_max_nacional','horas_incompletas','segundos_extraccion']}});return check

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--months',nargs='+',required=True);p.add_argument('--include-pre-septiembre',action='store_true');p.add_argument('--phase',choices=['all','download','extract'],default='all');p.add_argument('--workers',type=int,default=2)
 a=p.parse_args();assert 1<=a.workers<=3
 assert all(re.fullmatch(r'202[456]-(?:0[1-9]|1[012])',m) and '2024-07'<=m<='2026-09' for m in a.months),'Mes fuera del corte del estudio2024-07..2026-09'
 for path in [RAW,DATA,META]:path.mkdir(parents=True,exist_ok=True)
 items=[(m,'DEF') for m in a.months]
 if a.include_pre_septiembre:items.append(('2026-09','PRE'))
 if a.phase in ['download','all']:
  with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
   futures=[pool.submit(download,*x) for x in items]
   for f in concurrent.futures.as_completed(futures):f.result()
 if a.phase in ['extract','all']:
  for x in items:extract(*x)
if __name__=='__main__':main()
