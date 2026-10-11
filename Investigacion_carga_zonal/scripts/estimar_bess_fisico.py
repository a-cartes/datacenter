"""Conciliación y sensibilidad usando fronteras físicas separadas (tres meses)."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
from estimar_operacion_canteras import fit
from verificar_operacion_publica import independent,compare
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ejecucion',default='20261011_bess_fisico_v1');a=ap.parse_args();out=S/'resultados'/a.ejecucion;assert out.parent.resolve()==(S/'resultados').resolve();out.mkdir();parts=[];inputs=[]
 for folder in ['20261011_medidores_humberto_dic2025','20261011_medidores_humberto','20261011_medidores_humberto_feb2026']:
  f=S/'resultados'/folder/'seleccion_original.csv.gz';inputs.append(f);q=pd.read_csv(f,sep=';',decimal=',',encoding='utf-8-sig');q['IDSOCKET']=q.IDSOCKET.str.strip();q['utc']=pd.to_datetime(q.UTCDATETIME,utc=True);ll=q.utc.dt.tz_convert('America/Santiago');assert ll.dt.tz_localize(None).equals(pd.to_datetime(q.DATETIME));assert not q.duplicated(['IDSOCKET','utc']).any();assert q[['kWhD','kWhR']].notna().all().all();assert q[['kWhD','kWhR']].dtypes.eq('float64').all();q['fecha']=ll.dt.strftime('%Y-%m-%d');q['hora0']=ll.dt.hour;h=q.groupby(['fecha','hora0','IDSOCKET']).agg(n=('ID_SOC','size'),D=('kWhD','sum'),R=('kWhR','sum'));assert h.n.eq(4).all();h[['D','R']]/=1000;w=h[['D','R']].unstack('IDSOCKET');w.columns=[c+'_'+v for c,v in w.columns];parts.append(w.reset_index())
 w=pd.concat(parts,ignore_index=True);assert len(w)==2160 and not w.duplicated(['fecha','hora0']).any()
 f=S/'resultados/20261011_bess_conciliacion_v2/panel_90dias.csv.gz';inputs.append(f);d=pd.read_csv(f).merge(w,on=['fecha','hora0'],how='left',validate='one_to_one')
 for c in ['D','R']:d[c+'_FB123']=d[[c+f'_DNHUMBER_033_FB{i}_EGP' for i in (1,2,3)]].sum(axis=1,min_count=3)
 d['H1_neto']=d.D_DNHUMBER_110_H1_EGP-d.R_DNHUMBER_110_H1_EGP;d['residuo_H1_menos_FB']=d.H1_neto-d.D_FB123+d.R_FB123
 assert d[['D_FB123','R_FB123','H1_neto']].notna().all().all();d.to_csv(out/'panel_fisico.csv.gz',index=False)
 d['retiro_API_sumado']=d.BESS_central_MW+d.BESS_sistema_MW;metrics=[];disc=[]
 for mes,z in d.groupby('mes'):
  for api,phy in [('BESS_iny_MW','D_FB123'),('retiro_API_sumado','R_FB123')]:
   zz=z.dropna(subset=[api,phy]);e=zz[api]-zz[phy];metrics.append(dict(mes=mes,API=api,fisico=phy,n=len(zz),sesgo_MW=e.mean(),MAE_MW=e.abs().mean(),max_abs_MW=e.abs().max(),WAPE_pct=100*e.abs().sum()/zz[phy].abs().sum()))
  valid=z.dropna(subset=['retiro_API_sumado']);e=valid.retiro_API_sumado-valid.R_FB123
  overlap=e.gt(.1)&(valid.BESS_central_MW-valid.R_FB123).abs().le(.051)&valid.BESS_sistema_MW.gt(.1)
  missing=e.lt(-.1);disc.append(dict(mes=mes,horas_comparables=len(valid),horas_retiro_API_mayor_fisico=int(e.gt(.1).sum()),horas_patron_solapamiento=int(overlap.sum()),horas_retiro_API_menor_fisico=int(missing.sum()),MWh_sobreconteo_patron=float(e[overlap].sum())))
 pd.DataFrame(metrics).to_csv(out/'conciliacion_tres_meses.csv',index=False);pd.DataFrame(disc).to_csv(out/'patrones_retiro.csv',index=False)
 jobs=[('base',['TAP_R12']),('Santiago',['TAP_R12','SantiagoSolar_MW']),('Santiago_BESS_fisico',['TAP_R12','SantiagoSolar_MW','D_FB123','R_FB123']),('Santiago_BESS_frontera_H1',['TAP_R12','SantiagoSolar_MW','D_FB123','R_FB123','H1_neto'])];rows=[];pars=[];spec=[];checks=[]
 # Muestra90días física y87días idénticos a la comparación API; cambios de muestra visibles.
 api_dates=set(pd.read_csv(S/'resultados/20261011_estimacion_bess_v1/panel_estimacion.csv.gz').fecha)
 for sample,z in [('fisica90',d),('comun87',d[d.fecha.isin(api_dates)]),('sin_11feb89',d[d.fecha.ne('2026-02-11')])]:
  for name,x in jobs:
   label=sample+'_'+name;r,p=fit(z,x,label,sample);rows+=r;pars+=p;spec.append(dict(modelo=label,extras=x,fechas=sorted(z.fecha.unique().tolist())))
   if sample=='fisica90' and name in ['Santiago_BESS_fisico','Santiago_BESS_frontera_H1']:
    pp=pd.DataFrame(p);expected=pp[pp.resultado.eq('zona_lejos5')].set_index('variable').loc[['MW','MW_solar','MW_tarde']+x,'beta'].to_numpy();checks.append(dict(modelo=label,**independent(z,x,expected)))
 rr=pd.DataFrame(rows);rr['alcance']='Asociaciones exploratorias; tres meses; controles simultaneos potencialmente endogenos';rr.to_csv(out/'estimaciones.csv',index=False);pd.DataFrame(pars).to_csv(out/'parametros.csv',index=False);(out/'especificaciones.json').write_text(json.dumps(spec,indent=2))
 again=[]
 for sp in spec:
  r,_=fit(d[d.fecha.isin(sp['fechas'])],sp['extras'],sp['modelo'],'verificacion');again+=r
 replay=compare(again,pd.read_csv(out/'estimaciones.csv'));inputs += [S/'ADENDA_BESS_MEDICION_FISICA_20261011.md',S/'scripts/estimar_operacion_canteras.py',S/'scripts/estimar_heterogeneidad_horaria.py',Path(__file__)];pd.DataFrame([dict(archivo=str(f.relative_to(S)),sha256=sha(f)) for f in inputs]).to_csv(out/'insumos_sha256.csv',index=False)
 (out/'verificacion.json').write_text(json.dumps(dict(estado='OK',horas=2160,mediciones_15min=43200,modelos=len(spec),reproduccion=replay,LSQR=checks),indent=2));print(pd.DataFrame(metrics).to_string(index=False));print(pd.DataFrame(disc).to_string(index=False));print(rr[rr.resultado.eq('zona_lejos5')&rr.contraste.eq('solar')][['modelo','n_horas','beta','lo95','hi95']].to_string(index=False))
if __name__=='__main__':main()
