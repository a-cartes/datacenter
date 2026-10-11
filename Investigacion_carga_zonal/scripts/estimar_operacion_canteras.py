"""Asociaciones condicionales de carga y bloques, comparación en muestras idénticas."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests
from estimar_heterogeneidad_horaria import absorb,sha,YCOL
S=Path(__file__).resolve().parents[1]

def fit(d,extras,label,family):
 x=d[['MW']].copy();x['MW_solar']=d.MW*d.solar;x['MW_tarde']=d.MW*d.tarde
 for c in extras:x[c]=d[c]
 keys=[d.fecha,d.mes+'_'+d.hora0.astype(str),d.hora_semana]
 z,it,err=absorb(np.column_stack([x,d[YCOL]]),keys);X=z[:,:len(x.columns)];Y=z[:,len(x.columns):]
 rank=np.linalg.matrix_rank(X);sv=np.linalg.svd(X/np.maximum(X.std(axis=0),1e-30),compute_uv=False);cond=float(sv[0]/sv[-1]);rows=[];params=[]
 assert rank==X.shape[1],(label,rank,X.shape[1])
 beta=np.linalg.lstsq(X,Y,rcond=None)[0];bread=np.linalg.inv(X.T@X);res=Y-X@beta
 residualMW=X[:,0]-X[:,1:]@np.linalg.lstsq(X[:,1:],X[:,0],rcond=None)[0]
 week=pd.to_datetime(d.fecha).dt.to_period('W-SUN');calendar=pd.period_range(week.min(),week.max(),freq='W-SUN');wg=calendar.get_indexer(week);present=week.nunique()
 mg,mu=pd.factorize(d.mes,sort=True)
 for j,y in enumerate(YCOL):
  scores=X*res[:,j,None];ss=np.zeros((len(calendar),X.shape[1]));np.add.at(ss,wg,scores);meat=ss.T@ss
  for lag in range(1,5):v=ss[lag:].T@ss[:-lag];meat+=(1-lag/5)*(v+v.T)
  V=bread@meat@bread*(present/(present-1))
  mm=np.zeros((len(mu),X.shape[1]));np.add.at(mm,mg,scores);Vm=bread@(mm.T@mm)@bread*(len(mu)/(len(mu)-1))
  for name,vec in [('resto',[1,0,0]),('solar',[1,1,0]),('tarde',[1,0,1]),('solar_menos_resto',[0,1,0]),('tarde_menos_resto',[0,0,1])]:
   c=np.zeros(X.shape[1]);c[:3]=vec;b=float(c@beta[:,j]);se=float(np.sqrt(max(c@V@c,0)));sem=float(np.sqrt(max(c@Vm@c,0)))
   rows.append(dict(modelo=label,familia=family,resultado=y,contraste=name,n_horas=len(d),n_dias=d.fecha.nunique(),n_meses=d.mes.nunique(),semanas_observadas=present,semanas_calendario=len(calendar),beta=b,se_HAC4_semanas=se,lo95=b-1.95996398454*se,hi95=b+1.95996398454*se,se_cluster_mes=sem,p=2*norm.sf(abs(b/se)) if se else np.nan,sd_MW_tras_FE=float(X[:,0].std()),sd_MW_parcial=float(residualMW.std()),condicion_X_estandarizada=cond,parametros=len(x.columns),rango=rank,error_absorcion=err))
  for i,c in enumerate(x.columns):params.append(dict(modelo=label,resultado=y,variable=c,beta=beta[i,j]))
 return rows,params

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--panel',type=Path,default=S/'resultados/20261011_operacion_v1/panel_operativo.csv.gz');ap.add_argument('--ejecucion',default='20261011_estimacion_operacion_v1');a=ap.parse_args();out=S/'resultados'/a.ejecucion
 if out.exists() or out.parent.resolve()!=(S/'resultados').resolve():raise ValueError('Salida nueva requerida')
 inputs=[a.panel,S/'PROTOCOLO_OPERACION_20261011.md',Path(__file__).resolve(),S/'scripts/estimar_heterogeneidad_horaria.py'];before=[sha(f) for f in inputs];out.mkdir()
 pd.DataFrame([dict(referencia=str(f.relative_to(S.parent)),sha256=h) for f,h in zip(inputs,before)]).to_csv(out/'insumos_sha256.csv',index=False)
 d=pd.read_csv(a.panel);commercial=['Google_MW','Ascenty013_MW','Ascenty023_MW'];flows=[f'F_H{i}' for i in range(1,5)];channels=['TAP_R12','D_LBR1','D_LBR2','D_LBR4']
 full=d.dropna(subset=channels+flows).copy();sample=d.dropna(subset=commercial).copy()
 # Mantener días completos en comparación comercial para no alterar soporte intradiario.
 count=sample.groupby('fecha').hora0.agg(['size','nunique']);sample=sample[sample.fecha.isin(count[(count['size']==24)&count['nunique'].eq(24)].index)].copy()
 jobs=[('fisica_base','fisica',full,[]),('fisica_google','fisica',full,['TAP_R12']),('fisica_google_LBR','fisica',full,channels),('fisica_flujos','mediadores',full,flows),('fisica_google_flujos','mediadores',full,['TAP_R12']+flows),('comercial_base','comercial',sample,[]),('comercial_ajustada','comercial',sample,commercial)]
 rows=[];params=[]
 for label,family,z,xx in jobs:
  r,p=fit(z,xx,label,family);rows+=r;params+=p
 r=pd.DataFrame(rows);r['p_Holm_interacciones']=np.nan
 for family in r.familia.unique():
  ix=r.index[r.familia.eq(family)&r.contraste.isin(['solar_menos_resto','tarde_menos_resto'])&r.resultado.ne('D_zona')];r.loc[ix,'p_Holm_interacciones']=multipletests(r.loc[ix,'p'],method='holm')[1]
 r.to_csv(out/'estimaciones.csv',index=False);pd.DataFrame(params).to_csv(out/'parametros.csv',index=False)
 for name,z in [('fisica',full),('comercial',sample)]:
  z[['fecha','hora0','hora_utc','MW','mes','hora_semana','solar','tarde']+YCOL+channels+flows+commercial].to_csv(out/f'panel_{name}.csv.gz',index=False)
  z.groupby('mes').agg(horas=('MW','size'),dias=('fecha','nunique'),MW=('MW','mean')).to_csv(out/f'cobertura_{name}.csv')
 checks=[dict(referencia=str(f.relative_to(S.parent)),sin_cambios=sha(f)==h) for f,h in zip(inputs,before)];assert all(x['sin_cambios'] for x in checks);pd.DataFrame(checks).to_csv(out/'verificacion_insumos.csv',index=False)
 (out/'verificacion.json').write_text(json.dumps(dict(estado='OK',modelos=7,resultados_por_modelo=5,contrastes=len(r),horas_fisicas=len(full),horas_comerciales=len(sample),dias_comerciales=sample.fecha.nunique(),originales_modificados=0),indent=2))
 print(r[r.resultado.eq('zona_lejos5')][['modelo','contraste','beta','lo95','hi95','p_Holm_interacciones','sd_MW_parcial','condicion_X_estandarizada']].to_string(index=False))
if __name__=='__main__':main()
