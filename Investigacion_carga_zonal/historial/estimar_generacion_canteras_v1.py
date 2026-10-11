"""PV, carga y precios: muestras comparables y auditoría de generación publicada."""
from pathlib import Path
import argparse,json,gzip
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests
from pypdf import PdfReader
from estimar_operacion_canteras import fit
from estimar_heterogeneidad_horaria import sha,absorb,YCOL
S=Path(__file__).resolve().parents[1]
GEN=['SantiagoSolar_MW','DonHumberto_MW']

def complete(d,cols):
 d=d.dropna(subset=cols).copy();n=d.groupby('fecha').hora0.agg(['size','nunique']);return d[d.fecha.isin(n.index[n['size'].eq(24)&n.nunique.eq(24)] if False else n.index[n['size'].eq(24)&n['nunique'].eq(24)])].copy()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ejecucion',default='20261011_generacion_v1');a=ap.parse_args();out=S/'resultados'/a.ejecucion;assert out.parent.resolve()==(S/'resultados').resolve();out.mkdir()
 src=S/'fuentes_operacion/20261011_generacion_completa';manifest=json.loads((src/'manifiesto.json').read_text());assert manifest['estado']=='descarga_completa_pendiente_validacion'
 inputs=[src/'manifiesto.json',S/'PROTOCOLO_GENERACION_20261011.md',S/'resultados/20261011_operacion_v1/panel_operativo.csv.gz',Path(__file__),S/'scripts/estimar_operacion_canteras.py',S/'scripts/estimar_heterogeneidad_horaria.py',S/'fuentes_operacion/20261011_EAF0392025/EAF-039-2025.pdf'];rows=[]
 for m in manifest['paginas']:
  f=src/m['archivo'];assert sha(f)==m['sha256'];inputs.append(f);o=json.loads(gzip.open(f).read());data=o.get('data',o.get('content',[]));assert len(data)==m['filas'];assert all(r['id_central']==m['idCentral'] for r in data);rows+=data
 before=[sha(f) for f in inputs];pd.DataFrame([dict(archivo=str(f.relative_to(S)),sha256=h) for f,h in zip(inputs,before)]).to_csv(out/'insumos_sha256.csv',index=False)
 raw=pd.DataFrame(rows);dup=raw.duplicated();raw[dup].to_csv(out/'duplicados_exactos.csv.gz',index=False);g=raw.drop_duplicates().copy();assert g.tipo_tecnologia.eq('Solar').all();assert g.gen_real_mw.ge(0).all()
 g['fecha']=g.fecha_hora.str[:10];g['hora0']=pd.to_datetime(g.fecha_hora).dt.hour
 # La hora 25 se mantiene en auditoría; las fechas DST ya no pertenecen al panel elegible.
 bad=g.hora0.ne(g.hora-1);g[bad].to_csv(out/'horas_especiales.csv',index=False)
 p=pd.read_csv(inputs[2]);eligible=g[g.fecha.isin(p.fecha)].copy();assert eligible.hora0.eq(eligible.hora-1).all();assert not eligible.duplicated(['id_central','fecha','hora0']).any()
 g.groupby(['central','fecha']).agg(filas=('gen_real_mw','size'),horas=('hora0','nunique'),suma_MWh=('gen_real_mw','sum')).to_csv(out/'cobertura_generacion.csv')
 wide=eligible.pivot(index=['fecha','hora0'],columns='id_central',values='gen_real_mw').rename(columns={364:GEN[0],2209:GEN[1]}).reset_index();d=p.merge(wide,on=['fecha','hora0'],how='left',validate='one_to_one')
 # Diferenciar timestamps locales y conservar UTC del panel físico. Desfases se unen por UTC, nunca por posición.
 gen_utc=d.set_index('hora_utc')[GEN].copy();gen_utc.index=pd.to_datetime(gen_utc.index,utc=True)
 for shift in [-1,1]:
  z=gen_utc.copy();z.index=z.index-pd.Timedelta(hours=shift);z.columns=[c+f'_t{shift:+}' for c in GEN]
  d=d.join(z,on=pd.to_datetime(d.hora_utc,utc=True))
 for c in GEN:d[c+'_sq']=d[c]**2
 d['PV_total_MW']=d[GEN].sum(axis=1,min_count=2)
 d['episodio3']=d.fecha.isin(['2025-01-22','2025-03-06','2026-02-11']);d['episodio4']=d.episodio3|d.fecha.eq('2025-02-26')
 full=complete(d,['TAP_R12']+GEN);full.to_csv(out/'panel_generacion.csv.gz',index=False)
 d[d[GEN].isna().any(axis=1)][['fecha','hora0']].to_csv(out/'sin_generacion.csv',index=False)
 # Comprobación independiente con tabla de generación real EAF039, precisión impresa 0.1 MWh.
 pdf=PdfReader(inputs[6]);checks=[]
 for cid,page,label in [(2209,43,'PFV-DON-HUMBERTO'),(364,45,'PFV-SANTIAGOSOLAR')]:
  line=next(l for l in pdf.pages[page-1].extract_text().splitlines() if l.startswith(label+' '));values=np.array([float(v) for v in line.split()[1:25]])
  api=g[(g.id_central.eq(cid))&g.fecha.eq('2025-01-22')].sort_values('hora0').gen_real_mw.to_numpy();err=float(np.max(np.abs(values-api)));assert err<=.051
  checks.append(dict(idCentral=cid,pagina=page,horas=24,error_maximo_MW=err,suma_API_MWh=float(api.sum()),suma_fila_impresa=float(values.sum())))
 (out/'validacion_EAF_horas.json').write_text(json.dumps(checks,indent=2))
 jobs=[('base_google','principal',full,['TAP_R12']),('google_PV','principal',full,['TAP_R12']+GEN),('google_PV_cuadratica','principal',full,['TAP_R12']+GEN+[c+'_sq' for c in GEN])]
 for label,z in [('periodo1',full[full.fecha.lt('2025-08-01')]),('periodo2',full[full.fecha.ge('2025-08-01')]),('sin_3_episodios',full[~full.episodio3]),('sin_4_episodios',full[~full.episodio4])]:
  jobs +=[(label+'_base',label,z,['TAP_R12']),(label+'_PV',label,z,['TAP_R12']+GEN)]
 for shift in [-1,1]:
  cols=[c+f'_t{shift:+}' for c in GEN];z=complete(d,['TAP_R12']+cols)
  jobs +=[(f'desfase{shift:+}_base','desfases',z,['TAP_R12']),(f'desfase{shift:+}_PV','desfases',z,['TAP_R12']+cols)]
 rr=[];pp=[];spec=[]
 for label,family,z,extras in jobs:
  r,pars=fit(z,extras,label,family);rr+=r;pp+=pars;spec.append(dict(modelo=label,familia=family,n=len(z),extras=extras,fechas=sorted(z.fecha.unique().tolist())))
 r=pd.DataFrame(rr);r['p_Holm_principal']=np.nan;ix=r.index[r.familia.eq('principal')&r.contraste.isin(['solar_menos_resto','tarde_menos_resto'])&r.resultado.ne('D_zona')];r.loc[ix,'p_Holm_principal']=multipletests(r.loc[ix,'p'],method='holm')[1]
 r.to_csv(out/'estimaciones.csv',index=False);pd.DataFrame(pp).to_csv(out/'parametros.csv',index=False);(out/'especificaciones.json').write_text(json.dumps(spec,indent=2))
 full.groupby('hora0')[['MW','TAP_R12']+GEN+['PV_total_MW','F_H1','F_H2','F_H3','F_H4','zona_lejos5']].mean().to_csv(out/'perfil_horario.csv')
 full.groupby('bloque')[['MW','TAP_R12']+GEN+['PV_total_MW','F_H1','F_H2','F_H3','F_H4','zona_lejos5']].mean().to_csv(out/'perfil_bloque.csv')
 full[full.episodio4][['fecha','hora0','MW','TAP_R12']+GEN+['PV_total_MW','F_H1','F_H2','F_H3','F_H4','zona_lejos5','D_zona']].to_csv(out/'episodios.csv',index=False)
 cols=['MW','TAP_R12']+GEN+['F_H1','F_H2','F_H3','F_H4','zona_lejos5'];full[cols].corr().to_csv(out/'correlaciones_brutas.csv');z,_,_=absorb(full[cols].to_numpy(),[full.fecha,full.mes+'_'+full.hora0.astype(str),full.hora_semana]);pd.DataFrame(z,columns=cols).corr().to_csv(out/'correlaciones_tras_FE.csv')
 assert before==[sha(f) for f in inputs]
 info=dict(estado='OK',registros_originales=len(raw),duplicados_exactos=int(dup.sum()),horas_especiales=int(bad.sum()),horas_panel=len(full),dias_panel=full.fecha.nunique(),modelos=len(jobs),contrastes=len(r),insumos_preservados=len(inputs),originales_modificados=0)
 (out/'verificacion.json').write_text(json.dumps(info,indent=2));print(info);print(r[r.resultado.eq('zona_lejos5')&r.contraste.eq('solar')][['modelo','n_horas','beta','lo95','hi95']].to_string(index=False))
if __name__=='__main__':main()
