"""Selección previa de comparadores, dosis física y cargas concurrentes; solo derivados nuevos."""
from pathlib import Path
from datetime import datetime
import argparse, hashlib, json, subprocess
import numpy as np
import pandas as pd
import statsmodels.api as sm
from conciliar_canteras_odata import normal_day
S=Path(__file__).resolve().parents[1]; R=S.parent
ZONE=['BATUCO_110','TLIBERTADORES_110','C.NAVIA_110']

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()

def regress(df,y,x,label,extra=None):
 cols=[y]+x; d=df[cols].dropna(); X=sm.add_constant(d[x].astype(float),has_constant='add')
 rank=np.linalg.matrix_rank(X)
 if rank<X.shape[1] or len(d)<=X.shape[1]+3:
  return dict(modelo=label,resultado=y,n=len(d),rango=rank,parametros=X.shape[1],estado='no_estimable'),None
 fit=sm.OLS(d[y].astype(float),X).fit(cov_type='HAC',cov_kwds={'maxlags':3,'use_correction':True},use_t=False)
 row=dict(modelo=label,resultado=y,n=len(d),rango=rank,parametros=X.shape[1],estado='diagnostico_condicional',beta=fit.params['MW'],se_HAC3=fit.bse['MW'],lo95=fit.conf_int().loc['MW',0],hi95=fit.conf_int().loc['MW',1],R2=fit.rsquared,sd_residuo=float(fit.resid.std(ddof=X.shape[1])))
 # Scale invariant variance inflation for MW given other regressors.
 other=[c for c in X if c!='MW']; aux=sm.OLS(X.MW,X[other]).fit();row['VIF_MW']=1/(1-aux.rsquared) if aux.rsquared<1 else np.inf
 return row,fit

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--proyecto',type=Path,required=True);ap.add_argument('--ejecucion',default='20261011_controles_externos_v1');a=ap.parse_args();project=a.proyecto.resolve();n=project/'Panel_datos/codex_panel_nacional';out=S/'resultados'/a.ejecucion
 if out.exists() or out.parent.resolve()!=(S/'resultados').resolve():raise SystemExit('Se requiere carpeta nueva')
 prior=S/'resultados/20261011_conciliacion_v2'
 inputs=[n/'metadata/barra_subestacion.csv',n/'data/exposure.csv.gz',n/'data/exposure_pesimista.csv.gz',n/'data/withdrawals/cliente_hora.parquet',n/'data/panel_barra_mes.parquet',prior/'fronteras_diarias.csv',project/'Panel_datos/eventos_conexion/inventario_eventos_conexion.csv',n/'metadata/inputs/topologia/aristas_fechadas.csv',n/'metadata/inputs/topologia/obras_linea_documentadas.csv',project/'Panel_datos/topologia/nodos.csv',S/'PROTOCOLO_CONTROLES_EXTERNOS_20261011.md',Path(__file__).resolve(),S/'scripts/conciliar_canteras_odata.py']
 pricefiles=[n/f'data/hourly/REAL_{p.strftime("%Y%m")}.parquet' for p in pd.period_range('2024-08','2026-08',freq='M')]; inputs+=pricefiles
 def ref(p):return 'repositorio:'+str(p.relative_to(R)) if p.is_relative_to(R) else 'proyecto:'+str(p.relative_to(project))
 hashes=[dict(referencia=ref(p),bytes=p.stat().st_size,sha256=sha(p)) for p in inputs];out.mkdir(parents=True);pd.DataFrame(hashes).to_csv(out/'insumos_sha256.csv',index=False)
 (out/'inicio.json').write_text(json.dumps(dict(fecha=datetime.now().isoformat(),commit_previo=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),protocolo_sha256=sha(inputs[10])),indent=2))
 bm=pd.read_csv(inputs[0]);e=pd.concat([pd.read_csv(inputs[1]),pd.read_csv(inputs[2])]);sip=pd.read_parquet(inputs[3])
 ex=e[e.evento_id.str.startswith('DC')&e.clase.isin(['directa','mismo_corredor'])];exnodes=set(ex.nodo.dropna())|set(bm[bm.barra.isin(sip.barra)].nodo.dropna())
 panel=pd.read_parquet(inputs[4]);panel=panel[(panel.variante=='dias_24h')&(panel.bloque=='total')].copy();panel.loc[~panel.elegible_95,['spread','cmg']]=np.nan
 if panel.duplicated(['barra','mes']).any():raise ValueError('Panel mensual duplicado')
 wide=panel.pivot(index='mes',columns='barra',values='spread');pre=pd.period_range('2022-05','2024-04',freq='M').astype(str);train=pre[:12];valid=pre[12:];post=pd.period_range('2024-06','2026-08',freq='M').astype(str);required=list(pre)+list(post)
 target=wide[ZONE].mean(axis=1,skipna=False); records=[];seen=set()
 for _,b in bm.sort_values('barra').iterrows():
  if not b.barra.endswith('_110') or b.zona not in ['Metropolitana','Valparaíso',"O'Higgins–Maule"]:continue
  reasons=[]
  if pd.isna(b.nodo):reasons.append('sin_nodo')
  if b.metodo!='nemotécnico homologación':reasons.append('identidad_no_homologada')
  if b.nodo in exnodes:reasons.append('exposicion_DC_directa_corredor_o_retiro')
  complete=b.barra in wide and wide[b.barra].reindex(required).notna().all()
  if not complete:reasons.append('cobertura_incompleta')
  if not reasons and b.nodo in seen:reasons.append('subestacion_ya_representada')
  if not reasons:seen.add(b.nodo)
  r=b.to_dict();r['elegible']=not reasons;r['motivos']=';'.join(reasons)
  if not reasons:
   delta=target.loc[train]-wide.loc[train,b.barra];r['ajuste_entrenamiento']=float(delta.mean());r['RMSE_entrenamiento_centrado']=float(np.sqrt(np.mean((delta-delta.mean())**2)))
  records.append(r)
 cand=pd.DataFrame(records);rank=cand[cand.elegible].sort_values(['RMSE_entrenamiento_centrado','barra']).copy();rank['rango']=np.arange(1,len(rank)+1)
 if len(rank)<10:raise ValueError('Menos de10 comparadores elegibles')
 cand.to_csv(out/'candidatos_y_exclusiones.csv',index=False);rank.to_csv(out/'ranking_previo.csv',index=False)
 selected=rank.head(10).barra.tolist();pd.DataFrame([dict(barra=b,K5=b in selected[:5],K10=True) for b in selected]).merge(bm,on='barra').to_csv(out/'controles_seleccionados.csv',index=False)
 histories=[];hstats=[]
 for k in [5,10]:
  control=wide[selected[:k]].mean(axis=1,skipna=False);gap=target-control;hist=pd.DataFrame({'D_zona':target,'D_control':control,'brecha':gap}).loc[required].copy();hist['periodo']=np.where(hist.index.isin(pre),'previo','posterior');hist['K']=k;histories.append(hist.rename_axis('mes').reset_index())
  for exclusion in [False,True]:
   pp=[m for m in post if not(exclusion and m=='2024-07')]
   hstats.append(dict(K=k,sin_julio2024=exclusion,n_pre=len(pre),n_post=len(pp),contraste_USD_MWh=float(gap.loc[pp].mean()-gap.loc[pre].mean()),placebo_previo=float(gap.loc[valid].mean()-gap.loc[train].mean()),RMSE_validacion=float(np.sqrt(np.mean((gap.loc[valid]-gap.loc[train].mean())**2))),sesgo_validacion=float(gap.loc[valid].mean()-gap.loc[train].mean())))
 pd.concat(histories).to_csv(out/'contraste_historico_mensual.csv',index=False);pd.DataFrame(hstats).to_csv(out/'contraste_historico_resumen.csv',index=False)
 # Hourly sources, aggregated only on complete normal local days, common to all bars.
 bars=ZONE+['CANTERAS_110','QUILLOTA_220']+selected;daily=[]
 for f in pricefiles:
  q=pd.read_parquet(f,columns=['barra','fecha','hora0','cmg_usd_mwh','spread_usd_mwh'],filters=[('barra','in',bars)])
  q['barra']=q.barra.astype(str);q['fecha']=q.fecha.astype(str)
  if q.duplicated(['barra','fecha','hora0']).any():raise ValueError('Precio duplicado')
  agg=q.groupby(['fecha','barra'],observed=True).agg(n=('hora0','size'),nh=('hora0','nunique'),nv=('cmg_usd_mwh','count'),P=('cmg_usd_mwh','mean'),D=('spread_usd_mwh','mean')).reset_index()
  agg=agg[agg.n.eq(24)&agg.nh.eq(24)&agg.nv.eq(24)&agg.fecha.map(normal_day)];daily.append(agg)
 prices=pd.concat(daily);prices.to_csv(out/'precios_diarios_seleccion.csv.gz',index=False)
 ph=pd.read_csv(inputs[5]);ph=ph[ph.frontera.eq('Canteras_HT12_D')&ph.completo].set_index('fecha').MWh/24
 w=prices.pivot(index='fecha',columns='barra',values='P').reindex(columns=bars).dropna().join(ph.rename('MW')).dropna();w['zona']=w[ZONE].mean(axis=1);w['Q']=w.QUILLOTA_220;w['mes']=w.index.str[:7]
 for k in [5,10]:
  w[f'control{k}']=w[selected[:k]].mean(axis=1);w[f'brecha_zona_K{k}']=w.zona-w[f'control{k}'];w[f'brecha_canteras_K{k}']=w.CANTERAS_110-w[f'control{k}']
 w.to_csv(out/'panel_diario_comun.csv');numeric=w.select_dtypes('number').columns;m=w.groupby('mes')[numeric].mean();m['dias']=w.groupby('mes').size();m=m[m.dias.ge(20)];m['t']=np.arange(len(m));m['Batuco_HT4']=(m.index>='2025-06').astype(int);m['Lampa_JT4']=(m.index>='2025-08').astype(int);m['Lampa_JT6']=(m.index>='2026-02').astype(int);m.to_csv(out/'panel_mensual_comun.csv')
 estimates=[];params=[]
 for k in [5,10]:
  for outcome in [f'brecha_zona_K{k}',f'brecha_canteras_K{k}']:
   for spec in ['niveles','tendencia','diferencias','dif12','red','red_sin_meses_entrada']:
    df=m.copy();xx=['MW']
    if spec=='tendencia':xx+=['t']
    if spec=='diferencias':df=df.diff()
    if spec=='dif12':df=df.diff(12)
    if spec.startswith('red'):
     xx+=['t','Batuco_HT4','Lampa_JT4','Lampa_JT6']
     if spec=='red_sin_meses_entrada':df=df.drop(index=['2025-05','2025-07','2026-01'],errors='ignore')
    r,fit=regress(df,outcome,xx,spec);r['K']=k;estimates.append(r)
    if fit is not None:
     params.extend([dict(modelo=spec,resultado=outcome,variable=var,coef=float(val)) for var,val in fit.params.items()])
 pd.DataFrame(estimates).to_csv(out/'estimaciones_mensuales.csv',index=False);pd.DataFrame(params).to_csv(out/'parametros_mensuales.csv',index=False)
 # Individual donor sensitivity, all10 retained.
 individual=[]
 for b in selected:
  d=m.copy();d['gap_individual']=d.zona-d[b];r,_=regress(d,'gap_individual',['MW'],'control_individual');r['barra']=b;individual.append(r)
 pd.DataFrame(individual).to_csv(out/'sensibilidad_control_individual.csv',index=False)
 # Measured commercial other DC withdrawals, no ambiguous sums.
 sip['valido']=~sip.clave_ambigua&sip.retiro_mwh.notna();sd=sip.groupby(['empresa','barra','fecha'],observed=True).agg(n=('hora0','size'),nh=('hora0','nunique'),nv=('valido','sum'),MWh=('retiro_mwh',lambda s:s.sum(min_count=1))).reset_index();sd['completo']=sd.n.eq(24)&sd.nh.eq(24)&sd.nv.eq(24)&sd.fecha.map(normal_day);sd['MW']=sd.MWh/24;sd.to_csv(out/'otras_cargas_cobertura_diaria.csv',index=False)
 pairs=[('Google','TLIBERTADORES_110','Google_MW'),('Ascenty','CHACABUCO_013','Ascenty013_MW'),('Ascenty','CHACABUCO_023','Ascenty023_MW')]
 sw=w.copy()
 for emp,bar,col in pairs:
  x=sd[sd.empresa.eq(emp)&sd.barra.eq(bar)&sd.completo].set_index('fecha').MW;sw=sw.join(x.rename(col))
 xs=[x[2] for x in pairs];sample=sw.dropna(subset=xs).copy();sample['t']=(pd.to_datetime(sample.index)-pd.Timestamp('2024-08-01')).days/30.4375
 sample.to_csv(out/'panel_dias_con_otras_cargas.csv');sample[['MW']+xs].corr().to_csv(out/'correlaciones_cargas.csv')
 ds=[]
 for k in [5,10]:
  for outcome in [f'brecha_zona_K{k}',f'brecha_canteras_K{k}']:
   for spec in ['sin_otras_cargas','otras_cargas','otras_cargas_tendencia','otras_cargas_FE_mes']:
    d=sample.copy();xx=['MW']
    if spec!='sin_otras_cargas':xx+=xs
    if spec=='otras_cargas_tendencia':xx+=['t']
    if spec=='otras_cargas_FE_mes':
     dum=pd.get_dummies(d.mes,prefix='mes',drop_first=True,dtype=float);d=d.join(dum);xx+=list(dum)
    r,fit=regress(d,outcome,xx,spec);r['K']=k;ds.append(r)
 pd.DataFrame(ds).to_csv(out/'estimaciones_otras_cargas.csv',index=False)
 # Sources for simultaneous works. Candidate dates are not upgraded to confirmed entry.
 inv=pd.read_csv(inputs[6]);inv.to_csv(out/'eventos_red_y_cargas_revisados.csv',index=False)
 nodes=pd.read_csv(inputs[9]);edges=pd.read_csv(inputs[7]);selected_nodes=set(bm[bm.barra.isin(bars)].nodo.dropna());affected=edges[edges.nodo1.isin(selected_nodes)|edges.nodo2.isin(selected_nodes)].copy();affected.to_csv(out/'aristas_entorno_seleccion.csv',index=False)
 changed=affected[affected.fecha_efectiva.fillna('').between('2022-01-01','2026-08-31')];changed.to_csv(out/'aristas_fechadas_2022_2026.csv',index=False)
 after=[dict(referencia=h['referencia'],sin_cambios=sha(p)==h['sha256']) for p,h in zip(inputs,hashes)];pd.DataFrame(after).to_csv(out/'verificacion_insumos.csv',index=False)
 if not all(r['sin_cambios'] for r in after):raise ValueError('Cambio en insumos')
 summary=dict(estado='OK',insumos_preservados=len(inputs),candidatos_elegibles=len(rank),controles5=selected[:5],controles10=selected,n_meses=len(m),n_dias_otras_cargas=len(sample),originales_modificados=0)
 (out/'verificacion.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False));print(json.dumps(summary,ensure_ascii=False));print(pd.DataFrame(hstats).to_string(index=False));print(pd.DataFrame(estimates).to_string(index=False));print(pd.DataFrame(ds).to_string(index=False))
if __name__=='__main__':main()
