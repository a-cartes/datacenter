"""Interacciones con Ctx observado: asociaciones por estado, no efectos causales."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests
from estimar_heterogeneidad_horaria import absorb,sha,YCOL
S=Path(__file__).resolve().parents[1]
def fit_states(d,model):
 x=d[['MW']].copy();x['MW_solar']=d.MW*d.solar;x['MW_tarde']=d.MW*d.tarde;x['ctx']=d.ctx_AJLA;x['MW_ctx']=d.MW*d.ctx_AJLA
 if model in ['google','bloques_ctx']:x['TAP_R12']=d.TAP_R12
 if model=='bloques_ctx':
  for b in ['solar','tarde']:x[b+'_ctx']=d[b]*d.ctx_AJLA;x['MW_'+b+'_ctx']=d.MW*d[b]*d.ctx_AJLA
 keys=[d.fecha,d.mes+'_'+d.hora0.astype(str),d.hora_semana];z,iterations,err=absorb(np.column_stack([x,d[YCOL]]),keys);X=z[:,:len(x.columns)];Y=z[:,len(x.columns):];rank=np.linalg.matrix_rank(X)
 if rank<X.shape[1]:return [],[],dict(modelo=model,estado='no_estimable',rango=rank,columnas=X.shape[1],motivo='Falta de soporte o colinealidad; no eliminar términos según resultado')
 beta=np.linalg.lstsq(X,Y,rcond=None)[0];bread=np.linalg.inv(X.T@X);res=Y-X@beta;weeks=pd.to_datetime(d.fecha).dt.to_period('W-SUN');cal=pd.period_range(weeks.min(),weeks.max(),freq='W-SUN');wg=cal.get_indexer(weeks);G=weeks.nunique();mg,mu=pd.factorize(d.mes,sort=True);rows=[];params=[]
 contrasts=[]
 for block in ['resto','solar','tarde']:
  for ctx in [0,1]:
   c=pd.Series(0.,index=x.columns);c.MW=1
   if block!='resto':c['MW_'+block]=1
   if ctx:c.MW_ctx=1
   if ctx and block!='resto' and model=='bloques_ctx':c['MW_'+block+'_ctx']=1
   contrasts.append((f'{block}_ctx{ctx}',c.to_numpy(),False))
  c=pd.Series(0.,index=x.columns);c.MW_ctx=1
  if block!='resto' and model=='bloques_ctx':c['MW_'+block+'_ctx']=1
  contrasts.append((f'diferencia_ctx_{block}',c.to_numpy(),True))
 for j,y in enumerate(YCOL):
  scores=X*res[:,j,None];s=np.zeros((len(cal),X.shape[1]));np.add.at(s,wg,scores);meat=s.T@s
  for lag in range(1,5):v=s[lag:].T@s[:-lag];meat+=(1-lag/5)*(v+v.T)
  V=bread@meat@bread*(G/(G-1));sm=np.zeros((len(mu),X.shape[1]));np.add.at(sm,mg,scores);Vm=bread@(sm.T@sm)@bread*(len(mu)/(len(mu)-1))
  for name,c,test in contrasts:
   b=float(c@beta[:,j]);se=float(np.sqrt(max(c@V@c,0)));se_m=float(np.sqrt(max(c@Vm@c,0)))
   rows.append(dict(modelo=model,resultado=y,contraste=name,prueba_interaccion=test,n=len(d),dias=d.fecha.nunique(),meses=d.mes.nunique(),semanas_observadas=G,beta=b,se_HAC4_semanas=se,lo95=b-1.95996398454*se,hi95=b+1.95996398454*se,se_cluster_mes=se_m,p=2*norm.sf(abs(b/se)) if se else np.nan))
  params.extend([dict(modelo=model,resultado=y,variable=c,beta=beta[i,j]) for i,c in enumerate(x.columns)])
 return rows,params,dict(modelo=model,estado='estimado_condicional',rango=int(rank),columnas=int(X.shape[1]),iteraciones_FE=int(iterations),error_absorcion=float(err))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--panel',type=Path,default=S/'resultados/20261011_calendario_rio_v1/panel_con_RIO.csv.gz');ap.add_argument('--ejecucion',default='20261011_estimacion_rio_v2');a=ap.parse_args();out=S/'resultados'/a.ejecucion
 if out.exists() or out.parent.resolve()!=(S/'resultados').resolve():raise ValueError('Salida nueva requerida')
 inputs=[a.panel.resolve(),S/'ADENDA_OPERACION_20261011.md',Path(__file__).resolve(),S/'scripts/estimar_heterogeneidad_horaria.py'];hs=[sha(p) for p in inputs];out.mkdir();d=pd.read_csv(a.panel);d=d.dropna(subset=['ctx_AJLA','TAP_R12']).copy();d.to_csv(out/'panel_estimacion.csv.gz',index=False)
 support=d.groupby(['mes','bloque','ctx_AJLA']).agg(n=('MW','size'),dias=('fecha','nunique'),MW=('MW','mean'),sd_MW=('MW','std'),min_MW=('MW','min'),max_MW=('MW','max')).reset_index();support.to_csv(out/'soporte.csv',index=False)
 rows=[];params=[];statuses=[]
 for model in ['base','google','bloques_ctx']:
  r,p,status=fit_states(d,model);rows+=r;params+=p;statuses.append(status)
 r=pd.DataFrame(rows)
 if len(r):
  r['p_Holm_interacciones']=np.nan
  # En modelos simples la diferencia es idéntica por bloque: contar una prueba por resultado/modelo.
  ix=r.index[r.prueba_interaccion & r.resultado.ne('D_zona') & (r.modelo.eq('bloques_ctx')|r.contraste.eq('diferencia_ctx_resto'))];r.loc[ix,'p_Holm_interacciones']=multipletests(r.loc[ix,'p'],method='holm')[1]
 r.to_csv(out/'estimaciones.csv',index=False);pd.DataFrame(params).to_csv(out/'parametros.csv',index=False);pd.DataFrame(statuses).to_csv(out/'estimabilidad.csv',index=False)
 checks=[dict(referencia=str(p.relative_to(S)),sha256=h,sin_cambios=sha(p)==h) for p,h in zip(inputs,hs)];assert all(v['sin_cambios'] for v in checks);pd.DataFrame(checks).to_csv(out/'insumos_y_verificacion.csv',index=False)
 (out/'verificacion.json').write_text(json.dumps(dict(estado='OK',n=len(d),dias=d.fecha.nunique(),ctx_1=int(d.ctx_AJLA.eq(1).sum()),ctx_0=int(d.ctx_AJLA.eq(0).sum()),modelos=statuses),indent=2));print(r[r.resultado.eq('zona_lejos5')][['modelo','contraste','beta','lo95','hi95','p_Holm_interacciones']].to_string(index=False));print(support.groupby(['bloque','ctx_AJLA']).n.sum())
if __name__=='__main__':main()
