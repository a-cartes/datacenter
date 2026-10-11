"""Reproduce 80 regresiones desde CSV públicos, con OLS/HAC independientes del estimador original."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
S=Path(__file__).resolve().parents[1]

def independent_fit(d,y,cols):
 d=d[[y]+cols].dropna();X=np.column_stack([np.ones(len(d)),d[cols].to_numpy(float)]);v=d[y].to_numpy(float);n,k=X.shape
 b=np.linalg.lstsq(X,v,rcond=None)[0];u=v-X@b;z=X*u[:,None];meat=z.T@z
 for lag in range(1,4):
  term=z[lag:].T@z[:-lag];meat+=(1-lag/4)*(term+term.T)
 bread=np.linalg.pinv(X.T@X);cov=bread@meat@bread*n/(n-k)
 return b[1],float(np.sqrt(max(cov[1,1],0))),n

def main():
 p=argparse.ArgumentParser();p.add_argument('--salida',type=Path);a=p.parse_args();checks=[]
 for run in ['20261011_controles_externos_v1','20261011_controles_distantes_v1']:
  root=S/'resultados'/run;m=pd.read_csv(root/'panel_mensual_comun.csv').set_index('mes');daily=pd.read_csv(root/'panel_dias_con_otras_cargas.csv').set_index('fecha')
  for kind,file in [('mensual','estimaciones_mensuales.csv'),('otras_cargas','estimaciones_otras_cargas.csv')]:
   rows=pd.read_csv(root/file)
   for r in rows.itertuples():
    x=['MW'];d=m.copy() if kind=='mensual' else daily.copy()
    if kind=='mensual':
     if r.modelo=='tendencia':x+=['t']
     if r.modelo=='diferencias':d=d.diff()
     if r.modelo=='dif12':d=d.diff(12)
     if r.modelo.startswith('red'):
      x+=['t','Batuco_HT4','Lampa_JT4','Lampa_JT6']
      if r.modelo=='red_sin_meses_entrada':d=d.drop(index=['2025-05','2025-07','2026-01'],errors='ignore')
    else:
     if r.modelo!='sin_otras_cargas':x+=['Google_MW','Ascenty013_MW','Ascenty023_MW']
     if r.modelo=='otras_cargas_tendencia':x+=['t']
     if r.modelo=='otras_cargas_FE_mes':
      z=pd.get_dummies(d.mes,drop_first=True,dtype=float,prefix='mes');d=d.join(z);x+=list(z)
    b,se,n=independent_fit(d,r.resultado,x);errb=abs(b-r.beta);errs=abs(se-r.se_HAC3)
    if errb>1e-8 or errs>1e-6 or n!=r.n:raise ValueError((run,r.modelo,r.resultado,b,se,n,r.beta,r.se_HAC3,r.n))
    checks.append(dict(ejecucion=run,tipo=kind,modelo=r.modelo,resultado=r.resultado,error_beta=errb,error_se=errs,n=n))
 result=dict(estado='OK',regresiones_reproducidas=len(checks),error_max_beta=max(c['error_beta'] for c in checks),error_max_se_HAC=max(c['error_se'] for c in checks),originales_necesarios=False,metodo='OLS NumPy; sandwich Bartlett HAC3 con corrección n/(n-k), independiente de statsmodels')
 if a.salida:
  if a.salida.exists():raise SystemExit('No sobrescribir salida')
  a.salida.write_text(json.dumps(result,indent=2,ensure_ascii=False))
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
