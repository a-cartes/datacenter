"""Calendario y conciliación horaria; insumos de solo lectura y salida nueva."""
from pathlib import Path
import argparse, json, subprocess
import numpy as np
import pandas as pd
from estimar_heterogeneidad_horaria import sha

S=Path(__file__).resolve().parents[1]; R=S.parent
SOCKETS={**{f'H{i}':f'LSCANTRS_110_H{i}_EDG' for i in range(1,5)},
 **{f'HT{i}':f'LSCANTRS_110_HT{i}_EDG' for i in range(1,4)},
 **{f'TAP{i}':f'TPLIBERT_110_H{i}_DLA' for i in (1,2)},
 **{f'LBR{i}':f'CHCABUCO_023_LBR{i}_CHL' for i in (1,2,4)}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--proyecto',type=Path,required=True);ap.add_argument('--mediciones-legacy',type=Path,required=True);ap.add_argument('--ejecucion',default='20261011_operacion_v1');a=ap.parse_args()
 p=a.proyecto.resolve();legacy=a.mediciones_legacy.resolve();out=S/'resultados'/a.ejecucion
 if out.exists() or out.parent.resolve()!=(S/'resultados').resolve():raise ValueError('Salida nueva requerida')
 inputs=[legacy/'tablas/mediciones_candidatos_15min.parquet',p/'Panel_datos/codex_panel_nacional/data/withdrawals/cliente_hora.parquet',S/'resultados/20261011_horas_v1/panel_horario.csv.gz',S/'resultados/20261011_episodios_horarios_v1/episodios_horarios.csv',S/'resultados/20261011_controles_distantes_v1/eventos_red_y_cargas_revisados.csv',S/'PROTOCOLO_OPERACION_20261011.md',Path(__file__).resolve(),R/'SOCHER_2026_v3/mapeo/Memo_mapeo_electrico_y_unidades.md']
 def ref(f):
  for name,root in [('repositorio',R),('mediciones_legacy',legacy),('proyecto',p)]:
   if f.is_relative_to(root):return name+':'+str(f.relative_to(root))
  raise ValueError(f)
 hs=[dict(referencia=ref(f),sha256=sha(f),bytes=f.stat().st_size) for f in inputs];out.mkdir();pd.DataFrame(hs).to_csv(out/'insumos_sha256.csv',index=False)
 (out/'inicio.json').write_text(json.dumps(dict(commit_previo=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),fecha=pd.Timestamp.now(tz='UTC').isoformat()),indent=2))
 q=pd.read_parquet(inputs[0],columns=['IDSOCKET','etiqueta_utc','energia_D_kwh','energia_R_kwh']);q=q[q.IDSOCKET.isin(SOCKETS.values())].copy()
 assert not q.duplicated(['IDSOCKET','etiqueta_utc']).any()
 q['hora_utc']=q.etiqueta_utc.dt.floor('h');q['minuto']=q.etiqueta_utc.dt.minute
 assert set(q.minuto.unique())<=set([0,15,30,45])
 q['canal']=q.IDSOCKET.map({v:k for k,v in SOCKETS.items()})
 h=q.groupby(['canal','hora_utc']).agg(n=('minuto','size'),nmin=('minuto','nunique'),nd=('energia_D_kwh','count'),nr=('energia_R_kwh','count'),D=('energia_D_kwh','sum'),R=('energia_R_kwh','sum')).reset_index()
 for c,nc in [('D','nd'),('R','nr')]:h[c]=h[c].where(h.n.eq(4)&h.nmin.eq(4)&h[nc].eq(4))/1000
 h['F']=h.D-h.R
 w=h.pivot(index='hora_utc',columns='canal',values=['D','R','F']);w.columns=[f'{c}_{s}' for c,s in w.columns];w=w.reset_index()
 local=w.hora_utc.dt.tz_convert('America/Santiago');w['fecha']=local.dt.strftime('%Y-%m-%d');w['hora0']=local.dt.hour
 d=pd.read_csv(inputs[2]);d['hora_utc']=pd.to_datetime(d.hora_utc,utc=True);d=d.merge(w.drop(columns=['fecha','hora0']),on='hora_utc',how='left',validate='one_to_one')
 err=float((d.MW-d.D_HT1-d.D_HT2).abs().max());assert err<1e-8
 d['TAP_R12']=d.R_TAP1+d.R_TAP2;d['LBR_D124']=d.D_LBR1+d.D_LBR2+d.D_LBR4
 d['lineas_neto_DR']=d[[f'F_H{i}' for i in range(1,5)]].sum(axis=1,min_count=4)
 d['lineas_absoluto']=d[[f'F_H{i}' for i in range(1,5)]].abs().sum(axis=1,min_count=4)
 d['residuo_balance_DR']=d.lineas_neto_DR+d.F_HT1+d.F_HT2+d.F_HT3
 # Las identidades algebraicas no certifican orientación ni exhaustividad de fronteras.
 sip=pd.read_parquet(inputs[1]);sip=sip[~sip.clave_ambigua & sip.retiro_mwh.notna()].copy();sip['fecha']=sip.fecha.astype(str)
 pairs=[('Google','TLIBERTADORES_110','Google_MW'),('Ascenty','CHACABUCO_013','Ascenty013_MW'),('Ascenty','CHACABUCO_023','Ascenty023_MW')]
 for emp,bar,col in pairs:
  z=sip[sip.empresa.eq(emp)&sip.barra.eq(bar)][['fecha','hora0','retiro_mwh']].rename(columns={'retiro_mwh':col});assert not z.duplicated(['fecha','hora0']).any();d=d.merge(z,on=['fecha','hora0'],how='left',validate='one_to_one')
 physical=[f'{c}_{s}' for s in SOCKETS for c in ['D','R','F']]+['TAP_R12','LBR_D124','lineas_neto_DR','lineas_absoluto','residuo_balance_DR']
 comercial=[v[2] for v in pairs]
 reconc=[]
 for c in ['TAP_R12','LBR_D124','D_LBR1','D_LBR2','D_LBR4']:
  z=d.dropna(subset=[c,'Google_MW']);e=z[c]-z.Google_MW
  reconc.append(dict(candidato=c,comercial='Google_MW',horas=len(z),dias=z.fecha.nunique(),media_fisica=z[c].mean(),media_comercial=z.Google_MW.mean(),sesgo_MWh=e.mean(),WAPE_pct=100*e.abs().sum()/z.Google_MW.abs().sum(),correlacion=z[c].corr(z.Google_MW)))
  z[['fecha','hora0',c,'Google_MW']].assign(diferencia=e).to_csv(out/f'conciliacion_{c}.csv.gz',index=False)
 pd.DataFrame(reconc).to_csv(out/'conciliacion_candidatos_google.csv',index=False)
 d.groupby(['mes','bloque'])[physical+comercial+['MW','zona_lejos5']].mean().to_csv(out/'perfiles_mes_bloque.csv')
 d.groupby('hora0')[physical+comercial+['MW','zona_lejos5']].mean().to_csv(out/'perfil_hora.csv')
 cov=[]
 for mes,g in d.groupby('mes'):
  for col in physical+comercial:cov.append(dict(mes=mes,variable=col,horas_panel=len(g),horas_validas=g[col].notna().sum(),dias_con_valor=g.loc[g[col].notna(),'fecha'].nunique(),media=g[col].mean(),minimo=g[col].min(),maximo=g[col].max()))
 pd.DataFrame(cov).to_csv(out/'cobertura_variables.csv',index=False)
 # Calendario íntegro UTC: conserva días DST y horas sin panel como faltantes explícitos.
 ticks=pd.date_range('2024-08-01','2026-09-01',freq='h',inclusive='left',tz='America/Santiago').tz_convert('UTC')
 cal=pd.DataFrame({'hora_utc':ticks});ll=cal.hora_utc.dt.tz_convert('America/Santiago');cal['fecha']=ll.dt.strftime('%Y-%m-%d');cal['hora0']=ll.dt.hour;cal['utc_offset']=ll.map(lambda t:t.strftime('%z'))
 cal=cal.merge(d[['hora_utc','MW']+physical+comercial],on='hora_utc',how='left',validate='one_to_one');cal['en_panel_estimacion']=cal.MW.notna();cal['RIO_revisado']=False
 episodes=pd.read_csv(inputs[3]);episodes.to_csv(out/'episodios_previos_preservados.csv',index=False)
 # Esquema fuente conocido por lectura del CSV; conservar clasificación original al unir.
 epcols=[c for c in episodes.columns if c not in d.columns or c in ['fecha','hora0']]
 ep=episodes[epcols];assert not ep.duplicated(['fecha','hora0']).any()
 cal=cal.merge(ep,on=['fecha','hora0'],how='left',validate='many_to_one')
 cal.to_csv(out/'calendario_horario.csv.gz',index=False);d.to_csv(out/'panel_operativo.csv.gz',index=False)
 pd.read_csv(inputs[4]).to_csv(out/'hitos_red_previamente_revisados.csv',index=False)
 stats=[]
 for c in [f'F_H{i}' for i in range(1,5)]:
  for b,g in d.groupby('bloque'):stats.append(dict(canal=c,bloque=b,n=g[c].count(),media_MW=g[c].mean(),fraccion_DR_positivo=g.loc[g[c].notna(),c].gt(0).mean(),media_absoluta_MW=g[c].abs().mean(),correlacion_MW=g[c].corr(g.MW)))
 pd.DataFrame(stats).to_csv(out/'flujos_por_bloque.csv',index=False)
 d[['MW']+physical+comercial].corr().to_csv(out/'correlaciones_diagnostico.csv')
 check=[dict(referencia=v['referencia'],sin_cambios=sha(f)==v['sha256']) for f,v in zip(inputs,hs)];assert all(x['sin_cambios'] for x in check);pd.DataFrame(check).to_csv(out/'verificacion_insumos.csv',index=False)
 summary=dict(estado='OK',insumos_preservados=len(inputs),horas_panel=len(d),horas_calendario=len(cal),horas_otras_comerciales=int(d[comercial].notna().all(axis=1).sum()),error_reconciliacion_HT12=err,horas_RIO=0,originales_modificados=0)
 (out/'verificacion.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary));print(pd.DataFrame(reconc).to_string(index=False));print(pd.DataFrame(stats).to_string(index=False))
if __name__=='__main__':main()
