"""Reconstrucción horaria por UTC de los canales físicos, con ausencia explícita."""
from pathlib import Path
import argparse,json,gzip
import pandas as pd
import numpy as np
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ejecucion',default='20261011_humberto_largo_panel_v1');a=ap.parse_args();out=S/'resultados'/a.ejecucion;assert out.parent.resolve()==(S/'resultados').resolve();out.mkdir();parts=[];cov=[];inputfiles=[];bad=[];nr=0
 for name in ['20261011_humberto_largo_fuentes','20261011_humberto_fuentes_final2026']:
  src=S/'resultados'/name;m=json.loads((src/'manifiesto.json').read_text());assert m['estado']=='OK';inputfiles.append(src/'manifiesto.json')
  for row in m['meses']:
   f=S/row['seleccion_reutilizada'] if 'seleccion_reutilizada' in row else src/row['mes']/'seleccion_original.csv.gz';assert sha(f)==row['seleccion_sha256'];inputfiles.append(f);q=pd.read_csv(f,sep=';',decimal=',',encoding='utf-8-sig');q['IDSOCKET']=q.IDSOCKET.str.strip();q['hora_utc']=pd.to_datetime(q.UTCDATETIME,utc=True);local=q.hora_utc.dt.tz_convert('America/Santiago');q['discordancia_hora']=local.dt.tz_localize(None).ne(pd.to_datetime(q.DATETIME));q['mes_fuente']=row['mes'];nr+=len(q)
   if q.discordancia_hora.any():bad.append(q[q.discordancia_hora].copy())
   assert not q.duplicated(['IDSOCKET','hora_utc']).any();assert q[['kWhD','kWhR']].notna().all().all();q['hora_utc']=q.hora_utc.dt.floor('h')
   h=q.groupby(['hora_utc','IDSOCKET']).agg(n=('ID_SOC','size'),D=('kWhD','sum'),R=('kWhR','sum'),discordancia=('discordancia_hora','max'));h[['D','R']]=h[['D','R']].where(h.n.eq(4)&~h.discordancia,np.nan,axis=0)/1000
   for sock,zz in h.groupby('IDSOCKET'):cov.append(dict(mes=row['mes'],socket=sock,horas=len(zz),horas_validas=int(zz.D.notna().sum()),D_MWh=zz.D.sum(),R_MWh=zz.R.sum()))
   w=h[['D','R']].unstack('IDSOCKET');w.columns=[c+'_'+v for c,v in w.columns];parts.append(w.reset_index())
 pd.DataFrame(cov).to_csv(out/'cobertura_canales.csv',index=False)
 if bad:pd.concat(bad).to_csv(out/'discordancias_tiempo.csv.gz',index=False)
 w=pd.concat(parts,ignore_index=True);assert not w.hora_utc.duplicated().any();w=w.sort_values('hora_utc')
 for c in ['D','R']:w[c+'_FB123']=w[[c+f'_DNHUMBER_033_FB{i}_EGP' for i in (1,2,3)]].sum(axis=1,min_count=3)
 w['H1_neto']=w.D_DNHUMBER_110_H1_EGP-w.R_DNHUMBER_110_H1_EGP;w['residuo_H1_menos_FB']=w.H1_neto-w.D_FB123+w.R_FB123;ll=w.hora_utc.dt.tz_convert('America/Santiago');w['fecha']=ll.dt.strftime('%Y-%m-%d');w['hora0']=ll.dt.hour;w.to_csv(out/'medicion_horaria.csv.gz',index=False)
 f=S/'resultados/20261011_generacion_v3/panel_generacion.csv.gz';inputfiles.append(f);d=pd.read_csv(f);d['hora_utc']=pd.to_datetime(d.hora_utc,utc=True);d=d.merge(w.drop(columns=['fecha','hora0']),on='hora_utc',how='left',validate='one_to_one');d.to_csv(out/'panel_largo.csv.gz',index=False)
 old=S/'resultados/20261011_bess_fisico_v1/panel_fisico.csv.gz';inputfiles.append(old);o=pd.read_csv(old);cols=['D_FB123','R_FB123','H1_neto'];j=d[['fecha','hora0']+cols].merge(o[['fecha','hora0']+cols],on=['fecha','hora0'],suffixes=('_nuevo','_anterior'),validate='one_to_one');err=max(float((j[c+'_nuevo']-j[c+'_anterior']).abs().max()) for c in cols);assert len(j)==2160 and err<1e-9
 inputfiles+=[Path(__file__),S/'PROTOCOLO_EXTENSION_LARGA_20261011.md',S/'ADENDA_EXTENSION_FUENTES_20261011.md'];pd.DataFrame([dict(archivo=str(f.relative_to(S)),sha256=sha(f)) for f in inputfiles]).to_csv(out/'insumos_sha256.csv',index=False)
 info=dict(estado='OK',meses=25,registros_15min=nr,horas_fisicas=len(w),horas_en_panel=len(d),horas_H1=int(d.H1_neto.notna().sum()),horas_BESS=int(d[cols].notna().all(axis=1).sum()),registros_discordancia_temporal=sum(len(x) for x in bad),error_reproduccion_90dias=err,meses_sin_FB1=['2024-08','2024-09']);(out/'verificacion.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
if __name__=='__main__':main()
