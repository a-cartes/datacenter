"""Verificación independiente de agregados y revisión de red/cargas; preserva ejecuciones."""
from pathlib import Path
import json,hashlib
import pandas as pd
import numpy as np
S=Path(__file__).resolve().parents[1];R=S.parent;P=R.parent
OUT=S/'resultados/20261011_verificacion_zonal_v1'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 if OUT.exists():raise SystemExit('La verificación ya existe: conservarla')
 sources=[P/'Replica_RM_desde_cero/prospectiva_2030/extraidos/infotecnica/fichas_largas_transformadores-2d.parquet',P/'Panel_datos/topologia/fichas_transformadores.csv',P/'Panel_datos/retiros_chacabuco/mensual_por_punto.csv',P/'Panel_datos/revision_causal_2026_09_28/fuentes/CEN_ECS2025_pp76_77.txt',Path(__file__).resolve()]
 for run in ['20261011_controles_externos_v1','20261011_controles_distantes_v1']:
  sources+=list((S/'resultados'/run).glob('*.csv'))+list((S/'resultados'/run).glob('*.csv.gz'))
 before=[{'referencia':('repositorio:'+str(p.relative_to(R))) if p.is_relative_to(R) else ('proyecto:'+str(p.relative_to(P))),'sha256':sha(p),'bytes':p.stat().st_size} for p in sources];OUT.mkdir();pd.DataFrame(before).to_csv(OUT/'insumos_sha256.csv',index=False)
 checks=[]
 for run in ['20261011_controles_externos_v1','20261011_controles_distantes_v1']:
  base=S/'resultados'/run;m=pd.read_csv(base/'panel_mensual_comun.csv');d=pd.read_csv(base/'panel_diario_comun.csv');coef=pd.read_csv(base/'estimaciones_mensuales.csv');prices=pd.read_csv(base/'precios_diarios_seleccion.csv.gz')
  assert not d.fecha.duplicated().any();assert len(m)==25
  for r in coef[coef.modelo.eq('niveles')].itertuples():
   xc=m.MW-m.MW.mean();yc=m[r.resultado]-m[r.resultado].mean();manual=float(xc.dot(yc)/xc.dot(xc));assert abs(manual-r.beta)<1e-10
   checks.append(dict(prueba='pendiente_covarianza_varianza',ejecucion=run,resultado=r.resultado,error=abs(manual-r.beta)))
  pp=prices.pivot(index='fecha',columns='barra',values='P');dd=prices.pivot(index='fecha',columns='barra',values='D');error=(pp.sub(pp.QUILLOTA_220,axis=0)-dd).abs().max().max();assert error<1e-9
  checks.append(dict(prueba='D_igual_P_menos_Quillota',ejecucion=run,error=float(error)))
  recon=d.groupby('mes').MW.mean().reindex(m.mes).to_numpy();assert np.allclose(recon,m.MW);assert set(d.groupby('mes').size())==set(m.dias)
  sel=pd.read_csv(base/'controles_seleccionados.csv');assert len(sel.nodo)==sel.nodo.nunique()
  if 'distantes' in run:
   comp=set(pd.read_csv(base/'componente110_canteras.csv').nodo);assert not set(sel.nodo)&comp;assert not sel.zona.eq('Metropolitana').any()
  checks.append(dict(prueba='soporte_y_controles_sin_duplicar',ejecucion=run,error=0))
  # Leave-one-donor-out is recorded after main results, as a diagnostic of influence.
  rr=[]
  for k in coef.K.unique():
   pool=sel.barra.tolist()[:int(k)]
   for drop in pool:
    gap=m.zona-m[[b for b in pool if b!=drop]].mean(axis=1);xc=m.MW-m.MW.mean();beta=xc.dot(gap-gap.mean())/xc.dot(xc)
    rr.append(dict(K=k,excluido=drop,beta=float(beta)))
  pd.DataFrame(rr).to_csv(OUT/f'exclusion_un_control_{run}.csv',index=False)
 tech=pd.read_parquet(sources[0]);pattern='BATUCO|LAMPA|CANTERAS|RAFAEL|LEYDA|SAN ANTONIO|QUELENTARO|ESTRELLA|PORTEZUELO|CERRO CALERA'
 rows=tech[tech.nombre.str.contains(pattern,case=False,na=False)&tech.concepto.str.contains('Fecha de entrada',case=False,na=False)]
 rows.to_csv(OUT/'fechas_tecnicas_transformadores.csv',index=False)
 f=pd.read_csv(sources[1]);f[f.fecha_entrada.eq('2026-01-26')].to_csv(OUT/'antecedente_JT6_inventario.csv',index=False)
 # Historical physical channels: separate D/R, no sum across transformers or attribution to non-DC demand.
 ch=pd.read_csv(sources[2]);ch['MW_R']=ch.MWh_R/ch.horas;ch['periodo']=np.where(ch.mes.between('2024-01','2024-06'),'enero_junio2024',np.where(ch.mes.between('2026-01','2026-06'),'enero_junio2026','otro'))
 h=ch[ch.periodo.ne('otro')].groupby(['punto','periodo']).agg(meses=('mes','nunique'),horas=('horas','sum'),MWh_D=('MWh_D','sum'),MWh_R=('MWh_R','sum')).reset_index();h['MW_D']=h.MWh_D/h.horas;h['MW_R']=h.MWh_R/h.horas;h['alcance']='canal físico separado; frontera y signo histórico pendientes; no demanda no-DC aislada';h.to_csv(OUT/'canales_chacabuco_semestres_comparables.csv',index=False)
 (OUT/'ECS2025_pp76_77_extracto.txt').write_text(sources[3].read_text())
 pd.DataFrame(checks).to_csv(OUT/'comprobaciones.csv',index=False)
 after=[dict(referencia=b['referencia'],sin_cambios=sha(p)==b['sha256']) for p,b in zip(sources,before)];assert all(x['sin_cambios'] for x in after);pd.DataFrame(after).to_csv(OUT/'verificacion_insumos.csv',index=False)
 (OUT/'verificacion.json').write_text(json.dumps(dict(estado='OK',comprobaciones=len(checks),insumos_preservados=len(sources),originales_modificados=0),indent=2))
 print(json.dumps({'estado':'OK','comprobaciones':len(checks),'insumos':len(sources)}))
if __name__=='__main__':main()
