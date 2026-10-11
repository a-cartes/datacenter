"""Comparación exploratoria BESS en soporte común; no identificación causal."""
from pathlib import Path
import argparse,json
import pandas as pd
import numpy as np
from estimar_operacion_canteras import fit
from estimar_heterogeneidad_horaria import sha
from verificar_operacion_publica import independent,compare
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--conciliacion',default='20261011_bess_conciliacion_v1');ap.add_argument('--ejecucion',default='20261011_estimacion_bess_v1');a=ap.parse_args();src=S/'resultados'/a.conciliacion;out=S/'resultados'/a.ejecucion;assert out.parent.resolve()==(S/'resultados').resolve();out.mkdir()
 inputs=[src/'panel_90dias.csv.gz',S/'PROTOCOLO_BESS_Y_ESTADOS_20261011.md',S/'ADENDA_BESS_VENTANA_20261011.md',S/'scripts/estimar_operacion_canteras.py',S/'scripts/estimar_heterogeneidad_horaria.py',Path(__file__)];before=[sha(f) for f in inputs];d=pd.read_csv(inputs[0]);bess=['BESS_iny_MW','BESS_central_MW','BESS_sistema_MW'];bad=d[['MW','SantiagoSolar_MW','TAP_R12']+bess].isna().any(axis=1);excluded=sorted(d.loc[bad,'fecha'].unique().tolist());d=d[~d.fecha.isin(excluded)].copy();(out/'dias_excluidos_por_faltantes.json').write_text(json.dumps(excluded));assert d.groupby('fecha').size().eq(24).all()
 jobs=[('base',['TAP_R12']),('Santiago',['TAP_R12','SantiagoSolar_MW']),('Santiago_BESS',['TAP_R12','SantiagoSolar_MW']+bess),('Santiago_BESS_PFV_sensible',['TAP_R12','SantiagoSolar_MW']+bess+['DonHumberto_MW'])];rows=[];pars=[];spec=[];ind=[]
 for sample,z in [('completa',d),('sin_11feb',d[d.fecha.ne('2026-02-11')])]:
  for name,x in jobs:
   label=sample+'_'+name;r,p=fit(z,x,label,sample);rows+=r;pars+=p;spec.append(dict(modelo=label,extras=x,fechas=sorted(z.fecha.unique().tolist()),horas=len(z)))
   if sample=='completa' and name in ['base','Santiago_BESS']:
    pp=pd.DataFrame(p);expected=pp[pp.resultado.eq('zona_lejos5')].set_index('variable').loc[['MW','MW_solar','MW_tarde']+x,'beta'].to_numpy();ind.append(dict(modelo=label,**independent(z,x,expected)))
 rr=pd.DataFrame(rows);rr['alcance_inferencia']='Exploratorio: 3 clusters mensuales; HAC corto; sin afirmacion causal';rr.to_csv(out/'estimaciones.csv',index=False);pd.DataFrame(pars).to_csv(out/'parametros.csv',index=False);(out/'especificaciones.json').write_text(json.dumps(spec,indent=2));d.to_csv(out/'panel_estimacion.csv.gz',index=False)
 pd.DataFrame([dict(archivo=str(f.relative_to(S)),sha256=h,sin_cambios=sha(f)==h) for f,h in zip(inputs,before)]).to_csv(out/'insumos_sha256.csv',index=False);assert before==[sha(f) for f in inputs]
 # Segunda corrida íntegra más solver independiente para coeficientes principales.
 again=[]
 for sp in spec:
  z=d[d.fecha.isin(sp['fechas'])];r,_=fit(z,sp['extras'],sp['modelo'],'verificacion');again+=r
 check=compare(again,pd.read_csv(out/'estimaciones.csv'));(out/'verificacion.json').write_text(json.dumps(dict(estado='OK',reproduccion=check,LSQR=ind,originales_modificados=0,meses=int(d.mes.nunique())),indent=2));print(rr[rr.resultado.eq('zona_lejos5')&rr.contraste.isin(['solar','solar_menos_resto'])][['modelo','contraste','n_horas','beta','lo95','hi95']].to_string(index=False))
if __name__=='__main__':main()
