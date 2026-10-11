"""Calendario de menciones y episodios locales; ceros de medición no equivalen a desconexión."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from construir_calendario_rio import norm
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1]
def main():
 out=S/'resultados/20261011_calendario_local_v1'
 if out.exists():raise ValueError('Salida nueva requerida')
 files=[S/'resultados/20261011_calendario_rio_v1/registros_entorno_y_comparadores.csv.gz',S/'resultados/20261011_calendario_rio_v1/panel_con_RIO.csv.gz',S/'fuentes_operacion/20261011_EAF0392025/EAF-039-2025.pdf',S/'resultados/20261011_topologia_operativa_v1/canales_y_extremos.csv',Path(__file__).resolve()];hs=[sha(p) for p in files];out.mkdir()
 rio=pd.read_csv(files[0]);text=rio.motivo.fillna('').map(norm)+' '+rio.zona_desaclope.fillna('').map(norm);local=rio[text.str.contains(r'canteras|batuco|libertadores|chacabuco|lampa|punta peuco')].copy();local.to_csv(out/'menciones_locales_RIO.csv.gz',index=False)
 acts=local[local.motivo.fillna('').map(norm).str.match(r'^(inicia|inicio|inician|finaliza|finalizo|finalizan|termina)\b')].copy();acts.to_csv(out/'inicios_finales_mencion_local.csv',index=False)
 local.groupby(['fecha','zona_desaclope'],dropna=False).agg(registros=('id_instruccion','size'),primera_hora=('hora','min'),ultima_hora=('hora','max')).to_csv(out/'fechas_y_zonas_mencionadas.csv')
 d=pd.read_csv(files[1]);z=d[d.fecha.eq('2025-01-22')].copy();assert len(z)==24
 z['ctx_local']=np.where(z.hora0.between(13,16),1,np.where(z.hora0.ge(18),0,np.nan))
 z['estado_local']=np.where(z.ctx_local.eq(1),'restriccion_documentada',np.where(z.ctx_local.eq(0),'posterior_a_final_documentado',np.where(z.hora0.isin([12,17]),'transicion','desconocido')))
 z['fuente']='EAF039/2025 pp.58,65; SD2025004130 p.136; SI2025005181 p.101';z.to_csv(out/'episodio_20250122.csv',index=False)
 zeros=[]
 for i in range(1,5):
  q=d.assign(ambas_direcciones_cero=d[f'D_H{i}'].eq(0)&d[f'R_H{i}'].eq(0)).groupby('fecha').agg(horas_cero=('ambas_direcciones_cero','sum'),horas_observadas=('hora0','size')).reset_index();q['canal']=f'H{i}';zeros.append(q)
 pd.concat(zeros,ignore_index=True).to_csv(out/'horas_con_ambas_direcciones_cero.csv',index=False)
 integrated=d.merge(z[['fecha','hora0','ctx_local','estado_local']],on=['fecha','hora0'],how='left',validate='one_to_one');integrated['estado_local']=integrated.estado_local.fillna('no_clasificado')
 for i in range(1,5):integrated[f'H{i}_ambas_direcciones_cero']=integrated[f'D_H{i}'].eq(0)&integrated[f'R_H{i}'].eq(0)
 integrated.to_csv(out/'calendario_integrado.csv.gz',index=False)
 daily=integrated.assign(ctx_1=integrated.ctx_AJLA.eq(1),ctx_0=integrated.ctx_AJLA.eq(0),ctx_desconocido=integrated.ctx_AJLA.isna()).groupby('fecha').agg(horas=('hora0','size'),MW_Canteras=('MW','mean'),MW_Tap_proxy_Google=('TAP_R12','mean'),flujo_H1=('F_H1','mean'),flujo_H2=('F_H2','mean'),flujo_H3=('F_H3','mean'),flujo_H4=('F_H4','mean'),horas_ctx_AJLA=('ctx_1','sum'),horas_posteriores_final_AJLA=('ctx_0','sum'),horas_ctx_AJLA_desconocido=('ctx_desconocido','sum'),brecha_zonal=('zona_lejos5','mean'));daily.to_csv(out/'calendario_diario_resumen.csv')
 rows=[]
 for state,g in z.groupby('estado_local'):
  rows.append(dict(estado=state,n=len(g),horas=','.join(g.hora0.astype(str)),MW=g.MW.mean(),flujo_H1=g.F_H1.mean(),flujo_H2=g.F_H2.mean(),brecha=g.zona_lejos5.mean(),min_brecha=g.zona_lejos5.min(),max_brecha=g.zona_lejos5.max()))
 pd.DataFrame(rows).to_csv(out/'resumen_episodio.csv',index=False)
 checks=[dict(referencia=str(p.relative_to(S)),sha256=h,sin_cambios=sha(p)==h) for p,h in zip(files,hs)];assert all(r['sin_cambios'] for r in checks);pd.DataFrame(checks).to_csv(out/'fuentes_y_verificacion.csv',index=False)
 (out/'verificacion.json').write_text(json.dumps(dict(estado='OK',registros_locales=len(local),dias_menciones=local.fecha.nunique(),registros_inicio_final=len(acts),episodio_horas=24,horas_restriccion_completas=4,horas_transicion=2,alcance='Las menciones no constituyen un calendario completo de desconexiones. Los ceros son banderas de revisión, no estados de equipo. La comparación dentro del episodio es descriptiva; no identifica el efecto del centro de datos.',originales_modificados=0),ensure_ascii=False,indent=2));print(pd.DataFrame(rows).to_string(index=False));print(local.groupby('zona_desaclope',dropna=False).size().to_string())
if __name__=='__main__':main()
