"""Dossiers de candidatos y contrastes descriptivos; no estima un efecto causal."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
from estimar_heterogeneidad_horaria import sha,YCOL
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ejecucion',default='20261011_diagnostico_variaciones_v1');a=ap.parse_args();out=S/'resultados'/a.ejecucion;out.mkdir();p=S/'resultados/20261011_humberto_largo_panel_v1/panel_largo.csv.gz';d=pd.read_csv(p);d['date']=pd.to_datetime(d.fecha);columns=['MW','D_HT1','D_HT2','D_HT3','TAP_R12','SantiagoSolar_MW','D_FB123','R_FB123','H1_neto']+[f'F_H{i}' for i in range(1,5)]+YCOL+['Q','CANTERAS_110'];steps=pd.read_csv(S/'resultados/20261011_variaciones_carga/escalones_candidatos.csv');steps=steps[steps.regla.eq('principal')];rows=[];windows=[]
 for day in steps.fecha:
  t=pd.Timestamp(day)
  for span in [7,14]:
   z=d[d.date.between(t-pd.Timedelta(days=span),t+pd.Timedelta(days=span-1))].copy();z['evento']=day;z['ventana_dias']=span;z['periodo']=np.where(z.date.lt(t),'antes','despues');windows.append(z)
   for block in ['todas','solar','resto']:
    v=z if block=='todas' else z[z.solar.eq(int(block=='solar'))]
    for col in columns:
     b=v[v.periodo.eq('antes')][col];a_=v[v.periodo.eq('despues')][col];rows.append(dict(evento=day,ventana_dias=span,bloque=block,variable=col,n_antes=b.count(),n_despues=a_.count(),dias_antes=v.loc[v.periodo.eq('antes'),'fecha'].nunique(),dias_despues=v.loc[v.periodo.eq('despues'),'fecha'].nunique(),media_antes=b.mean(),media_despues=a_.mean(),cambio=a_.mean()-b.mean(),alcance='Comparación temporal descriptiva; no contrafactual validado'))
 pd.DataFrame(rows).to_csv(out/'escalones_antes_despues.csv',index=False);pd.concat(windows).drop(columns=['date']).to_csv(out/'ventanas_escalones.csv.gz',index=False)
 falls=pd.read_csv(S/'resultados/20261011_variaciones_carga/caidas_horarias_todas.csv');eventrows=[]
 for _,r in falls.iterrows():
  t=pd.Timestamp(r.inicio_utc).tz_convert('America/Santiago');z=d[d.fecha.eq(t.strftime('%Y-%m-%d'))].copy();z['evento_caida']=r.inicio_local;eventrows.append(z)
 pd.concat(eventrows).drop(columns='date').to_csv(out/'dias_caidas_horarias.csv.gz',index=False)
 t=pd.Timestamp('2024-12-03');case=d[d.date.eq(t)].copy();case['fraccion_barra23_fuera']=case.hora0.map(lambda h:max(0,min(h+1,21+19/60)-max(h,5+36/60)));assert abs(case.fraccion_barra23_fuera.sum()*60-943)<1e-8
 case.drop(columns='date').to_csv(out/'episodio_documentado.csv',index=False)
 phases={'antes_0_4':list(range(5)),'caida_6_15':list(range(6,16)),'recuperacion_16_20':list(range(16,21)),'despues_22_23':[22,23]};allstats=[];contr=[]
 for span in [7,14]:
  days=[t+pd.Timedelta(days=k) for k in range(-span,span+1,7) if k];z=d[d.date.isin(days+[t])].copy();z['tratado_dia']=z.date.eq(t)
  for phase,hours in phases.items():
   for col in columns:
    ev=case[case.hora0.isin(hours)][col].mean();ref=z[(~z.tratado_dia)&z.hora0.isin(hours)][col].mean();allstats.append(dict(ventana_dias=span,fase=phase,variable=col,evento=ev,referencia=ref,diferencia=ev-ref,dias_referencia=z.loc[~z.tratado_dia,'fecha'].nunique()))
  tmp=pd.DataFrame(allstats);tmp=tmp[tmp.ventana_dias.eq(span)]
  for phase in ['caida_6_15','recuperacion_16_20','despues_22_23']:
   for col in columns:
    a_=tmp[(tmp.fase==phase)&(tmp.variable==col)].iloc[0];b=tmp[(tmp.fase=='antes_0_4')&(tmp.variable==col)].iloc[0];contr.append(dict(ventana_dias=span,fase=phase,variable=col,cambio_relativo_a_pre=a_.diferencia-b.diferencia,alcance='Doble diferencia descriptiva entre horas y martes vecinos; no identificada causalmente'))
 pd.DataFrame(allstats).to_csv(out/'episodio_perfiles_martes.csv',index=False);pd.DataFrame(contr).to_csv(out/'episodio_contrastes_descriptivos.csv',index=False)
 baseline=case[case.hora0.between(0,4)].MW.mean();early=case[case.hora0.between(6,15)].MW.mean();late=case[case.hora0.between(17,20)].MW.mean();facts=dict(MW_antes=baseline,MW_6_15=early,MW_17_20=late,caida_bruta_MW=early-baseline,horas_precio_cero=case.loc[case.CANTERAS_110.eq(0),'hora0'].tolist(),horas_diferencial_cero=case.loc[case.zona_lejos5.eq(0),'hora0'].tolist(),minutos_barra23_fuera=943,causa_documentada='ANI1; interrupcion accidental en23kV; cuatro alimentadores de un cliente',identificacion='Candidato; no estimación causal')
 (out/'episodio_hechos.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2));inputs=[p,S/'resultados/20261011_variaciones_carga/escalones_candidatos.csv',S/'resultados/20261011_variaciones_carga/caidas_horarias_todas.csv',S/'ADENDA_EPISODIO_20241203_20261011.md',Path(__file__)];pd.DataFrame([dict(archivo=str(f.relative_to(S)),sha256=sha(f)) for f in inputs]).to_csv(out/'insumos_sha256.csv',index=False);print(json.dumps(facts,ensure_ascii=False,indent=2));print(pd.DataFrame(contr).query("variable in ['MW','zona_lejos5']").to_string(index=False))
if __name__=='__main__':main()
