"""Panel largo y ventanas fijadas: mismos controles/muestras, cinco resultados."""
from pathlib import Path
import argparse,json
import pandas as pd
import numpy as np
from statsmodels.stats.multitest import multipletests
from estimar_operacion_canteras import fit
from verificar_operacion_publica import independent,compare
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1]
def complete(d,cols):
 z=d.dropna(subset=cols);cnt=z.groupby('fecha').hora0.agg(['size','nunique']);return z[z.fecha.isin(cnt.index[cnt['size'].eq(24)&cnt['nunique'].eq(24)])].copy()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ejecucion',default='20261011_estimacion_larga_v1');a=ap.parse_args();out=S/'resultados'/a.ejecucion;assert out.parent.resolve()==(S/'resultados').resolve();out.mkdir();f=S/'resultados/20261011_humberto_largo_panel_v1/panel_largo.csv.gz';d=pd.read_csv(f);full=complete(d,['TAP_R12','SantiagoSolar_MW','D_FB123','R_FB123','H1_neto']);h1=complete(d,['TAP_R12','SantiagoSolar_MW','H1_neto']);full.to_csv(out/'panel_BESS_completo.csv.gz',index=False);h1.to_csv(out/'panel_H1_completo.csv.gz',index=False)
 jobs=[];basic=[('base',['TAP_R12']),('Santiago',['TAP_R12','SantiagoSolar_MW']),('BESS',['TAP_R12','SantiagoSolar_MW','D_FB123','R_FB123']),('BESS_H1',['TAP_R12','SantiagoSolar_MW','D_FB123','R_FB123','H1_neto'])]
 for sample,z in [('largo',full),('antes_dic2025',full[full.fecha.lt('2025-12-01')]),('dic2025_feb2026',full[full.fecha.between('2025-12-01','2026-02-28')]),('desde_mar2026',full[full.fecha.ge('2026-03-01')])]:
  for name,x in basic:jobs.append((sample+'_'+name,sample,z,x))
 for name,x in [('base',['TAP_R12']),('Santiago',['TAP_R12','SantiagoSolar_MW']),('H1',['TAP_R12','SantiagoSolar_MW','H1_neto'])]:jobs.append(('H1_25meses_'+name,'H1_25meses',h1,x))
 rows=[];pars=[];spec=[];checks=[]
 for label,sample,z,x in jobs:
  r,p=fit(z,x,label,sample);rows+=r;pars+=p;spec.append(dict(modelo=label,familia=sample,extras=x,fechas=sorted(z.fecha.unique().tolist()),horas=len(z)))
  if label in ['largo_base','largo_BESS_H1']:
   pp=pd.DataFrame(p);expected=pp[pp.resultado.eq('zona_lejos5')].set_index('variable').loc[['MW','MW_solar','MW_tarde']+x,'beta'].to_numpy();checks.append(dict(modelo=label,**independent(z,x,expected)))
 r=pd.DataFrame(rows);r['p_Holm_interacciones_largo']=np.nan;ix=r.index[r.familia.eq('largo')&r.resultado.ne('D_zona')&r.contraste.isin(['solar_menos_resto','tarde_menos_resto'])];r.loc[ix,'p_Holm_interacciones_largo']=multipletests(r.loc[ix,'p'],method='holm')[1];r.to_csv(out/'estimaciones.csv',index=False);pd.DataFrame(pars).to_csv(out/'parametros.csv',index=False);(out/'especificaciones.json').write_text(json.dumps(spec,indent=2));again=[]
 for label,sample,z,x in jobs:rr,_=fit(z,x,label,sample);again+=rr
 replay=compare(again,pd.read_csv(out/'estimaciones.csv'));inp=[f,Path(__file__),S/'scripts/estimar_operacion_canteras.py',S/'scripts/estimar_heterogeneidad_horaria.py',S/'PROTOCOLO_EXTENSION_LARGA_20261011.md'];pd.DataFrame([dict(archivo=str(f.relative_to(S)),sha256=sha(f)) for f in inp]).to_csv(out/'insumos_sha256.csv',index=False);(out/'verificacion.json').write_text(json.dumps(dict(estado='OK',reproduccion=replay,LSQR=checks,horas_BESS=len(full),horas_H1=len(h1)),indent=2));print(r[r.resultado.eq('zona_lejos5')&r.contraste.eq('solar')][['modelo','n_horas','beta','lo95','hi95']].to_string(index=False))
if __name__=='__main__':main()
