"""Comprueba el panel público, agrega a meses y contrasta FE con dummies explícitas dispersas."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix,hstack
from scipy.sparse.linalg import lsqr
S=Path(__file__).resolve().parents[1]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--salida',type=Path);a=ap.parse_args();p=S/'resultados/20261011_horas_v1';d=pd.read_csv(p/'panel_horario.csv.gz');est=pd.read_csv(p/'estimaciones_principales.csv');checks=[]
 assert not d.duplicated(['fecha','hora0']).any();assert d.groupby('fecha').size().eq(24).all();assert len(d)==18168
 old=pd.read_csv(S/'resultados/20261011_controles_distantes_v1/panel_mensual_comun.csv').set_index('mes');m=d.groupby('mes')[['MW','zona_lejos5']].mean();errm=float(np.max(np.abs(m.MW-old.MW)));errp=float(np.max(np.abs(m.zona_lejos5-old.brecha_zona_K5)));assert max(errm,errp)<1e-9
 checks.append(dict(prueba='agregacion_reproduce_panel_anterior',error=max(errm,errp)))
 # One coefficient system with full day and month-hour FE, using a distinct solver.
 x=np.column_stack([d.MW,d.MW*d.solar,d.MW*d.tarde]);keys=[d.fecha,d.mes+'_'+d.hora0.astype(str),d.hora_semana]
 blocks=[]
 for key in keys:
  idx=pd.factorize(key,sort=True)[0];blocks.append(csr_matrix((np.ones(len(d)),(np.arange(len(d)),idx)),shape=(len(d),idx.max()+1)))
 X=hstack([csr_matrix(x)]+blocks,format='csr');fit=lsqr(X,d.zona_lejos5.to_numpy(),atol=1e-11,btol=1e-11,iter_lim=15000);b=fit[0][:3]
 expected=est[(est.FE=='B_dia_meshora_horasemana')&(est.modelo=='bloques')&(est.resultado=='zona_lejos5')].set_index('contraste');target=np.array([expected.loc['resto','beta'],expected.loc['solar_menos_resto','beta'],expected.loc['tarde_menos_resto','beta']]);error=float(np.max(np.abs(b-target)));assert error<1e-6
 checks.append(dict(prueba='FE_con_dummies_LSQR_independiente',error=error,iteraciones=fit[2],estado_solver=fit[1]))
 # Residual variation and arithmetic of interaction slopes.
 for (fe,model,y),g in est.groupby(['FE','modelo','resultado']):
  q=g.set_index('contraste').beta
  if model=='bloques':assert abs(q.solar-q.resto-q.solar_menos_resto)<1e-9;assert abs(q.tarde-q.resto-q.tarde_menos_resto)<1e-9
  if model=='carga_alta':assert abs(q.carga_sobre_p75-q.carga_hasta_p75-q.alta_menos_baja)<1e-9
  if model=='precio_alto':assert abs(q.Q_mayor_igual100-q.Q_menor100-q.Q_alto_menos_bajo)<1e-9
 checks.append(dict(prueba='identidades_pendientes_y_diferencias',error=0))
 result=dict(estado='OK',n_horas=len(d),n_dias=d.fecha.nunique(),comprobaciones=checks,originales_necesarios=False)
 if a.salida:
  if a.salida.exists():raise SystemExit('No sobrescribir salida')
  a.salida.write_text(json.dumps(result,indent=2,ensure_ascii=False))
 print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
