"""Conserva anomalías del CSV Qlik y limita la sensibilidad a 2026, sin reescalar."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from estimar_operacion_canteras import fit
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1]
def main():
 out=S/'resultados/20261011_flujo500_v1'
 if out.exists():raise ValueError('Salida ya existente')
 inputs=[S/'fuentes_operacion/20261011_qlik_AJLA/potencia_transitada_AJLA_C1_original.csv',S/'resultados/20261011_operacion_v1/panel_operativo.csv.gz',S/'ADENDA_OPERACION_20261011.md',Path(__file__).resolve(),S/'scripts/estimar_operacion_canteras.py'];hs=[sha(p) for p in inputs];out.mkdir()
 raw=pd.read_csv(inputs[0],sep=';',encoding='utf-8-sig');d=raw.copy();d['potencia_original']=d['Potencia (MWh)'];d['valor_MWh']=pd.to_numeric(d.potencia_original.str.replace('.','',regex=False).str.replace(',','.',regex=False),errors='coerce');d['mes']=d.Fecha.str[:7];d['ssee']=d.SSEE.str.strip();d['linea']=d['Nombre Línea'].str.strip()
 assert d['ID Nombre Línea'].eq(929).all();assert not d.duplicated(['Fecha','Intervalos','ssee']).any();assert d.valor_MWh.notna().all()
 d['cero']=d.valor_MWh.eq(0);d['magnitud_mayor10000']=d.valor_MWh.abs().gt(10000)
 d.groupby(['mes','ssee']).agg(n=('valor_MWh','size'),ceros=('cero','sum'),magnitud_mayor10000=('magnitud_mayor10000','sum'),media=('valor_MWh','mean'),minimo=('valor_MWh','min'),maximo=('valor_MWh','max')).to_csv(out/'auditoria_mensual.csv')
 d.to_csv(out/'serie_interpretada_sin_corregir.csv.gz',index=False)
 w=d[d.Fecha.ge('2026-01-01')].pivot(index=['Fecha','Intervalos'],columns='ssee',values='valor_MWh').rename(columns={'Alto Jahuel 500 kV':'AJLA_extremo_AltoJahuel','Lo Aguirre 500 kV':'AJLA_extremo_LoAguirre'}).reset_index().rename(columns={'Fecha':'fecha','Intervalos':'hora0'})
 w['suma_extremos']=w.AJLA_extremo_AltoJahuel+w.AJLA_extremo_LoAguirre;w['magnitud_media_extremos']=(w.AJLA_extremo_AltoJahuel.abs()+w.AJLA_extremo_LoAguirre.abs())/2
 w['balance_compatible_5pct_o5MWh']=w.suma_extremos.abs().le(np.maximum(5,.05*w.magnitud_media_extremos))&w.suma_extremos.notna();w.to_csv(out/'contraste_extremos_2026.csv',index=False)
 base=pd.read_csv(inputs[1]);panel=base.merge(w,on=['fecha','hora0'],how='inner',validate='one_to_one');z=panel.dropna(subset=['AJLA_extremo_AltoJahuel','TAP_R12']).copy();z.to_csv(out/'panel_sensibilidad_2026.csv.gz',index=False)
 rows=[];params=[]
 for label,xx in [('base_2026',[]),('google_2026',['TAP_R12']),('google_flujo500_2026',['TAP_R12','AJLA_extremo_AltoJahuel'])]:
  r,p=fit(z,xx,label,'flujo500_sensibilidad');rows+=r;params+=p
 r=pd.DataFrame(rows);r.to_csv(out/'estimaciones.csv',index=False);pd.DataFrame(params).to_csv(out/'parametros.csv',index=False)
 check=[dict(referencia=str(p.relative_to(S)),sha256=h,sin_cambios=sha(p)==h) for p,h in zip(inputs,hs)];assert all(x['sin_cambios'] for x in check);pd.DataFrame(check).to_csv(out/'insumos_y_verificacion.csv',index=False)
 paired=panel.dropna(subset=['suma_extremos']);summary=dict(estado='OK',filas_originales=len(d),horas_sensibilidad=len(z),dias_sensibilidad=z.fecha.nunique(),meses_sensibilidad=z.mes.nunique(),horas_pareadas_2026=len(paired),correlacion_extremos=paired.AJLA_extremo_AltoJahuel.corr(paired.AJLA_extremo_LoAguirre),fraccion_balance_compatible=paired.balance_compatible_5pct_o5MWh.mean(),serie_pre2026_utilizada=False,convencion_hora='Intervalos locales 0–23; pendiente certificación externa; días DST ya excluidos en panel',originales_modificados=0)
 (out/'verificacion.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary));print(r[r.resultado.eq('zona_lejos5')][['modelo','contraste','beta','lo95','hi95']].to_string(index=False))
if __name__=='__main__':main()
