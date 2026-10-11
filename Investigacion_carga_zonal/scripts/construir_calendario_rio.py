"""Audita RIO mensual y reconstruye estados intradiarios con evidencia explícita."""
from pathlib import Path
import argparse,gzip,json,re,unicodedata
import numpy as np
import pandas as pd
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1]
def norm(x):
 return re.sub(r'\s+',' ',''.join(c for c in unicodedata.normalize('NFKD',str(x or '')) if not unicodedata.combining(c)).lower()).strip()
def target(s):return all(w in s for w in ['aguirre','jahuel','500'])
def build(out):
 inputs=[Path(__file__).resolve(),S/'ADENDA_OPERACION_20261011.md',S/'PROTOCOLO_OPERACION_20261011.md',S/'resultados/20261011_operacion_v1/panel_operativo.csv.gz',S/'resultados/20261011_episodios_horarios_v1/episodios_horarios.csv'];records=[];coverage=[];zones=[];matches=[];bad=[]
 hs=[dict(referencia=str(f.relative_to(S)),sha256=sha(f),bytes=f.stat().st_size) for f in inputs]
 dirs=sorted((S/'fuentes_operacion').glob('20261011_rio_*_completo'))
 for folder in dirs:
  mf=folder/'manifiesto.json'
  if not mf.exists():coverage.append(dict(carpeta=folder.name,estado='sin_manifiesto'));continue
  hs.append(dict(referencia=str(mf.relative_to(S)),sha256=sha(mf),bytes=mf.stat().st_size));m=json.loads(mf.read_text());inputs.append(mf)
  if m['estado']!='descargado_requiere_validacion':coverage.append(dict(carpeta=folder.name,estado=m['estado']));continue
  parts=[];pagecounts=[]
  for page in m['paginas']:
   file=folder/page['archivo'];assert sha(file)==page['sha256'];hs.append(dict(referencia=str(file.relative_to(S)),sha256=page['sha256'],bytes=file.stat().st_size));inputs.append(file);obj=json.loads(gzip.open(file).read());parts.append(pd.DataFrame(obj['data']));pagecounts.append(obj['totalPages'])
  assert len(set(pagecounts))==1
  assert [p['pagina_solicitada'] for p in m['paginas']]==list(range(1,pagecounts[0]+2))
  assert m['paginas'][-1]['filas']==0
  d=pd.concat(parts,ignore_index=True);n=len(d);api_cols=list(d.columns);d=d.drop_duplicates();dupexact=n-len(d)
  conflict=d.id_instruccion.duplicated(False)&d.id_instruccion.notna()
  if conflict.any():bad.extend(d[conflict].assign(carpeta=folder.name).to_dict('records'))
  d=d[~conflict].copy();d['fecha']=d.fecha.astype(str).str[:10];assert d.fecha.between(m['inicio'],m['fin']).all()
  d['motivo_n']=d.motivo.map(norm);d['zona_n']=d.zona_desaclope.map(norm);d['texto_n']=d.motivo_n+' '+d.zona_n
  required=pd.date_range(m['inicio'],m['fin'],freq='D').strftime('%Y-%m-%d');missing=sorted(set(required)-set(d.fecha))
  coverage.append(dict(carpeta=folder.name,estado='auditable' if not missing else 'dias_faltantes',filas=n,duplicados_exactos=dupexact,identificadores_conflictivos=int(conflict.sum()),dias=d.fecha.nunique(),dias_faltantes=';'.join(missing),inicio=m['inicio'],fin=m['fin']))
  for zone,g in d.groupby('zona_n'):
   if zone:zones.append(dict(mes=m['inicio'][:7],zona=zone,registros=len(g),dias=g.fecha.nunique()))
  selected=d[d.texto_n.str.contains(r'aguirre|jahuel|canteras|batuco|chacabuco|lampa|libertadores|cerro navia|san antonio|leyda|quelentaro|estrella|pajaritos|punta peuco|san pablo|san jose|altamirano',regex=True)].copy()
  matches.extend(selected[api_cols].assign(fuente=folder.name).to_dict('records'))
  for day,g in d.groupby('fecha'):
   sub=g[g.texto_n.map(target)].copy()
   transitions={'ctx':[],'prorrata':[]}; invalid=False
   for row in sub.itertuples():
    motive=row.motivo_n;isctx='ctx' in motive or 'control de transferencia' in motive;ispror='prorrata' in motive
    action=1 if re.match(r'^(inicia|inicio|inician)\b',motive) else (0 if re.match(r'^(finaliza|finalizo|finalizan|termina)\b',motive) else None)
    time=pd.to_timedelta(row.hora,errors='coerce')
    if pd.isna(time):
     if action is not None and (isctx or ispror):invalid=True
     continue
    second=time.total_seconds()
    if not 0<=second<86400:invalid=True;continue
    named_motive=target(motive) or bool(re.fullmatch(r'(inicia|inicio|inician|finaliza|finalizo|finalizan|termina) (ctx|prorrata|control de transferencia)',motive))
    if action is not None and (isctx or ispror) and named_motive:
     # Recurso debe estar nombrado en motivo o zona; no inferir otros circuitos.
     for k,yes in [('ctx',isctx),('prorrata',ispror)]:
      if yes:transitions[k].append((second,action,'instruccion',row.id_instruccion,row.hora,row.motivo,row.zona_desaclope))
    elif second==0 and target(row.zona_n):transitions['ctx'].append((0,1,'zona_inicial',row.id_instruccion,row.hora,row.motivo,row.zona_desaclope))
   for k,ev in transitions.items():
    bytime={}
    for sec,act,origin,ident,hh,mot,zone in ev:
     bytime.setdefault(sec,[]).append((act,origin,ident));records.append(dict(fecha=day,tipo=k,segundo=sec,estado=act,origen=origin,id_instruccion=ident,hora=hh,motivo=mot,zona=zone,fuente=folder.name))
    times=sorted(bytime);intervals=[];last=0;state=np.nan
    for sec in times:
     if sec>last:intervals.append((last,sec,state))
     explicit=[v[0] for v in bytime[sec] if v[1]=='instruccion'];vals=explicit or [v[0] for v in bytime[sec]]
     state=vals[0] if len(set(vals))==1 else np.nan;last=sec
    intervals.append((last,86400,state))
    for hour in range(24):
     lengths={0:0.,1:0.,'unknown':0.}
     for start,end,state in intervals:
      overlap=max(0,min(end,(hour+1)*3600)-max(start,hour*3600))
      lengths['unknown' if pd.isna(state) else int(state)]+=overlap
     status=1 if lengths[1]==3600 else (0 if lengths[0]==3600 else np.nan)
     if invalid:status=np.nan
     yield dict(fecha=day,hora0=hour,tipo=k,estado=status,minutos_restriccion=lengths[1]/60,minutos_sin_control=lengths[0]/60,minutos_desconocidos=lengths['unknown']/60,dia_instruccion_sin_hora=invalid)
 # Return other artifacts through filesystem after full consumption.
 pd.DataFrame(coverage).to_csv(out/'auditoria_descargas.csv',index=False);pd.DataFrame(records).to_csv(out/'eventos_AJLA.csv',index=False);pd.DataFrame(zones).to_csv(out/'zonas_declaradas_por_mes.csv',index=False);pd.DataFrame(matches).to_csv(out/'registros_entorno_y_comparadores.csv.gz',index=False);pd.DataFrame(bad).to_csv(out/'identificadores_conflictivos.csv',index=False)
 assert all(sha(S/r['referencia'])==r['sha256'] for r in hs)
 pd.DataFrame(hs).to_csv(out/'insumos_sha256.csv',index=False)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ejecucion',default='20261011_calendario_rio_v1');a=ap.parse_args();out=S/'resultados'/a.ejecucion
 if out.exists() or out.parent.resolve()!=(S/'resultados').resolve():raise ValueError('Salida nueva requerida')
 out.mkdir();cal=pd.DataFrame(list(build(out)));assert not cal.duplicated(['fecha','hora0','tipo']).any();cal.to_csv(out/'calendario_estados_largo.csv.gz',index=False)
 w=cal.pivot(index=['fecha','hora0'],columns='tipo',values='estado').reset_index().rename(columns={'ctx':'ctx_AJLA','prorrata':'prorrata_AJLA'})
 panel=pd.read_csv(S/'resultados/20261011_operacion_v1/panel_operativo.csv.gz');d=panel.merge(w,on=['fecha','hora0'],how='left',validate='one_to_one');d['RIO_dia_descargado']=d.fecha.isin(cal.fecha);d.to_csv(out/'panel_con_RIO.csv.gz',index=False)
 cov=d.assign(ctx_estado=d.ctx_AJLA.fillna(-1)).groupby(['mes','bloque','ctx_estado']).agg(horas=('MW','size'),MW_media=('MW','mean'),MW_min=('MW','min'),MW_max=('MW','max'),brecha_media=('zona_lejos5','mean')).reset_index();cov.to_csv(out/'cobertura_y_soporte_estados.csv',index=False)
 prior=pd.read_csv(S/'resultados/20261011_episodios_horarios_v1/episodios_horarios.csv')[['fecha','hora0','estado']];v=prior.merge(w,on=['fecha','hora0'],how='left');v['previo']=v.estado.map({'restriccion':1,'sin_control_documentado':0,'sin_ese_control':0,'sin_control':0});v.to_csv(out/'contraste_EAF_previo.csv',index=False)
 hs=pd.read_csv(out/'insumos_sha256.csv');assert all(sha(S/r.referencia)==r.sha256 for r in hs.itertuples())
 summary=dict(estado='OK',meses_RIO=d.loc[d.RIO_dia_descargado,'mes'].nunique(),dias_RIO=d.loc[d.RIO_dia_descargado,'fecha'].nunique(),horas_ctx_1=int(d.ctx_AJLA.eq(1).sum()),horas_ctx_0=int(d.ctx_AJLA.eq(0).sum()),horas_ctx_desconocido=int(d.ctx_AJLA.isna().sum()),insumos_preservados=len(hs),originales_modificados=0)
 (out/'verificacion.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary));print(v.groupby(['estado','ctx_AJLA'],dropna=False).size().to_string())
if __name__=='__main__':main()
