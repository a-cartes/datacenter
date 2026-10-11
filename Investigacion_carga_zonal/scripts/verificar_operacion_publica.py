"""Reproduce tablas públicas y contrasta coeficientes con dummies y LSQR independiente."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix,hstack
from scipy.sparse.linalg import lsqr
from estimar_operacion_canteras import fit
from estimar_estados_rio import fit_states
S=Path(__file__).resolve().parents[1]
def independent(d,extras,expected):
 x=np.column_stack([d.MW,d.MW*d.solar,d.MW*d.tarde]+[d[c].to_numpy() for c in extras]);blocks=[]
 for key in [d.fecha,d.mes+'_'+d.hora0.astype(str),d.hora_semana]:
  ix=pd.factorize(key,sort=True)[0];blocks.append(csr_matrix((np.ones(len(d)),(np.arange(len(d)),ix)),shape=(len(d),ix.max()+1)))
 X=hstack([csr_matrix(x)]+blocks,format='csr');r=lsqr(X,d.zona_lejos5.to_numpy(),atol=1e-12,btol=1e-12,iter_lim=20000);err=float(np.max(np.abs(r[0][:x.shape[1]]-expected)))
 assert err<1e-6,(err,r[1]);return dict(error=err,iteraciones=r[2],estado_solver=r[1])
def compare(rows,target):
 key=['modelo','resultado','contraste'];a=pd.DataFrame(rows).set_index(key).sort_index();b=target.set_index(key).sort_index();assert a.index.equals(b.index)
 cols=['beta','se_HAC4_semanas','se_cluster_mes','lo95','hi95'];err=float(np.max(np.abs(a[cols].to_numpy()-b[cols].to_numpy())));assert err<1e-8
 return dict(contrastes=len(a),error_maximo=err)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--salida',type=Path,required=True);ap.add_argument('--incluir-rio',action='store_true');a=ap.parse_args()
 if a.salida.exists():raise ValueError('No sobrescribir verificaciones')
 out={};p=S/'resultados/20261011_estimacion_operacion_v1';full=pd.read_csv(p/'panel_fisica.csv.gz');com=pd.read_csv(p/'panel_comercial.csv.gz');target=pd.read_csv(p/'estimaciones.csv');params=pd.read_csv(p/'parametros.csv');rows=[]
 flows=[f'F_H{i}' for i in range(1,5)];jobs=[('fisica_base',full,[]),('fisica_google',full,['TAP_R12']),('fisica_google_LBR',full,['TAP_R12','D_LBR1','D_LBR2','D_LBR4']),('fisica_flujos',full,flows),('fisica_google_flujos',full,['TAP_R12']+flows),('comercial_base',com,[]),('comercial_ajustada',com,['Google_MW','Ascenty013_MW','Ascenty023_MW'])]
 for label,d,extras in jobs:
  rr,_=fit(d,extras,label,'verificacion');rows+=rr
  if label in ['fisica_google','comercial_ajustada']:
   expected=params[(params.modelo==label)&params.resultado.eq('zona_lejos5')].set_index('variable').loc[['MW','MW_solar','MW_tarde']+extras,'beta'].to_numpy();out['LSQR_'+label]=independent(d,extras,expected)
 out['reproduccion_operacion']=compare(rows,target)
 q=S/'resultados/20261011_flujo500_v1';d=pd.read_csv(q/'panel_sensibilidad_2026.csv.gz');rows=[]
 for label,extras in [('base_2026',[]),('google_2026',['TAP_R12']),('google_flujo500_2026',['TAP_R12','AJLA_extremo_AltoJahuel'])]:rr,_=fit(d,extras,label,'verificacion');rows+=rr
 out['reproduccion_flujo500']=compare(rows,pd.read_csv(q/'estimaciones.csv'))
 if a.incluir_rio:
  q=S/'resultados/20261011_estimacion_rio_v3';d=pd.read_csv(q/'panel_estimacion.csv.gz');rows=[]
  for label in ['base','google','bloques_ctx']:rr,_,_=fit_states(d,label);rows+=rr
  out['reproduccion_RIO']=compare(rows,pd.read_csv(q/'estimaciones.csv'))
  c=pd.read_csv(S/'resultados/20261011_calendario_rio_v1/calendario_estados_largo.csv.gz');assert not c.duplicated(['fecha','hora0','tipo']).any()
  assert np.allclose(c[['minutos_restriccion','minutos_sin_control','minutos_desconocidos']].sum(axis=1),60)
  out['calendario_RIO']=dict(filas=len(c),duraciones_horarias=60,claves_unicas=True)
 out.update(estado='OK',requiere_originales=False,modifica_bases=False);a.salida.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
