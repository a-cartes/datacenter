"""BESS Don Humberto: publicaciones operativas, medidores y estados documentados."""
from pathlib import Path
import argparse,json,gzip
import numpy as np
import pandas as pd
from pypdf import PdfReader
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1]
IDS={16908:'BESS_iny_MW',16909:'BESS_central_MW',17487:'BESS_sistema_MW'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ejecucion',default='20261011_bess_conciliacion_v1');a=ap.parse_args();out=S/'resultados'/a.ejecucion;assert out.parent.resolve()==(S/'resultados').resolve();out.mkdir();inputs=[];rows=[];coverage=[]
 for name in ['diciembre2025','enero2026','febrero2026']:
  src=S/f'fuentes_operacion/20261011_bess_{name}';f=src/'manifiesto.json';m=json.loads(f.read_text());assert m['estado']=='completo_pendiente_auditoria';inputs.append(f)
  n=0
  for p in m['paginas']:
   f=src/p['archivo'];assert sha(f)==p['sha256'];inputs.append(f);d=json.loads(gzip.open(f).read())['data'];assert len(d)==p['filas'];n+=len(d)
   rows.extend([r for r in d if r['id_opreal'] in IDS and m['inicio']<=r['fecha_hora'][:10]<m['fin']])
  coverage.append(dict(ventana=name,filas_descargadas=n,paginas=len(m['paginas'])))
 raw=pd.DataFrame(rows);raw.to_csv(out/'BESS_seleccion_original.csv.gz',index=False);g=raw.drop_duplicates().copy();assert not g.duplicated(['id_opreal','fecha_hora']).any();assert g.gen_real_mw.ge(0).all()
 g['fecha']=g.fecha_hora.str[:10];g['hora0']=pd.to_datetime(g.fecha_hora).dt.hour;assert g.hora0.eq(g.hora-1).all();g['variable']=g.id_opreal.map(IDS)
 g.groupby(['variable','fecha']).agg(horas=('gen_real_mw','count'),energia_MWh=('gen_real_mw','sum')).to_csv(out/'cobertura_BESS.csv')
 b=g.pivot(index=['fecha','hora0'],columns='variable',values='gen_real_mw').reset_index();assert len(b)==90*24 and b[list(IDS.values())].notna().all().all();b.to_csv(out/'BESS_horaria.csv.gz',index=False)
 pf=S/'resultados/20261011_generacion_v3/panel_generacion.csv.gz';inputs.append(pf);panel=pd.read_csv(pf);d=panel.merge(b,on=['fecha','hora0'],how='inner',validate='one_to_one');assert len(d)==2160;d.to_csv(out/'panel_90dias.csv.gz',index=False)
 f=S/'resultados/20261011_medidores_humberto/seleccion_original.csv.gz';inputs.append(f);q=pd.read_csv(f,sep=';',decimal=',',encoding='utf-8-sig');q['IDSOCKET']=q.IDSOCKET.str.strip();q['utc']=pd.to_datetime(q.UTCDATETIME,utc=True);local=q.utc.dt.tz_convert('America/Santiago');assert local.dt.tz_localize(None).equals(pd.to_datetime(q.DATETIME));assert not q.duplicated(['IDSOCKET','utc']).any();assert q[['kWhD','kWhR']].dtypes.eq('float64').all();assert q[['kWhD','kWhR']].notna().all().all();q['fecha']=local.dt.strftime('%Y-%m-%d');q['hora0']=local.dt.hour
 h=q.groupby(['fecha','hora0','IDSOCKET']).agg(n=('ID_SOC','size'),D=('kWhD','sum'),R=('kWhR','sum'));assert h.n.eq(4).all();h[['D','R']]/=1000
 w=h[['D','R']].unstack('IDSOCKET');w.columns=[c+'_'+v for c,v in w.columns];w=w.reset_index();assert len(w)==744
 j=d.merge(w,on=['fecha','hora0'],validate='one_to_one');assert len(j)==744
 for c in ['D','R']:j[c+'_FB123']=j[[c+f'_DNHUMBER_033_FB{i}_EGP' for i in (1,2,3)]].sum(axis=1)
 j['BESS_retiro_total']=j.BESS_central_MW+j.BESS_sistema_MW;j['H1_neto']=j.D_DNHUMBER_110_H1_EGP-j.R_DNHUMBER_110_H1_EGP;j['FB_neto']=j.D_FB123-j.R_FB123
 # Residuo de fronteras, NO generación solar certificada: incluye pérdidas/auxiliares y posibles fronteras faltantes.
 j['residuo_H1_menos_FB']=j.H1_neto-j.FB_neto;j['API_suma_algebraica']=j.DonHumberto_MW+j.BESS_iny_MW-j.BESS_retiro_total
 j['error_suma_API_vs_H1']=j.API_suma_algebraica-j.H1_neto;j['noche']=j.hora0.isin([0,1,2,3,4,5,22,23]);j['PFV_nocturno_positivo']=j.noche&j.DonHumberto_MW.gt(.1)
 metrics=[]
 for api,physical in [('BESS_iny_MW','D_FB123'),('BESS_retiro_total','R_FB123')]:
  for lag in [-1,0,1]:
   a=j[api];p=j[physical].shift(lag);ok=a.notna()&p.notna();e=p[ok]-a[ok];metrics.append(dict(API=api,medicion=physical,desfase_horas=lag,n=int(ok.sum()),MAE_MW=e.abs().mean(),max_abs_MW=e.abs().max(),sesgo_MW=e.mean(),WAPE_pct=100*e.abs().sum()/a[ok].abs().sum(),correlacion=a[ok].corr(p[ok])))
 pd.DataFrame(metrics).to_csv(out/'conciliacion_API_medidores.csv',index=False)
 stat=[]
 for label,sel in [('todas',pd.Series(True,index=j.index)),('noche',j.noche),('noche_PFV_positivo',j.PFV_nocturno_positivo),('otras_horas',~j.PFV_nocturno_positivo)]:
  z=j[sel];stat.append(dict(grupo=label,n=len(z),dias=z.fecha.nunique(),PFV_MWh=z.DonHumberto_MW.sum(),BESS_inyeccion_MWh=z.BESS_iny_MW.sum(),H1_neto_MWh=z.H1_neto.sum(),MAE_suma_API_H1=z.error_suma_API_vs_H1.abs().mean(),sesgo_suma_API_H1=z.error_suma_API_vs_H1.mean(),MAE_PFV_H1=(z.DonHumberto_MW-z.H1_neto).abs().mean(),residuo_H1_menos_FB_medio=z.residuo_H1_menos_FB.mean()))
 pd.DataFrame(stat).to_csv(out/'diagnostico_frontera.csv',index=False);j.to_csv(out/'conciliacion_enero.csv.gz',index=False);j[j.PFV_nocturno_positivo].to_csv(out/'PFV_nocturno_diagnostico.csv',index=False)
 # Valores transcritos de tablas reales (no programación), precisión impresa 0.1 MWh.
 pdf=S/'fuentes_operacion/20261011_bess_estados_documentos/EAF-008-2026.pdf';inputs.append(pdf)
 vals={'DonHumberto_MW':(52,[0,0,0,0,0,0,0,6.5,25.7,36.5,41,48.4,52.9,55.7,52.6,44.9,36.6,30.7,24.8,21.7,2.3,0,0,44.2]),'BESS_iny_MW':(58,[40.6,25,.5,.5,11.4,.1,2.1,26.3,0,0,0,0,0,0,0,0,0,0,0,0,38.8,.8,24.7,44.9]),'BESS_central_MW':(64,[0,0,0,0,0,0,0,0,8.3,.7,.2,.3,.3,.3,.3,.3,.2,16.4,12.8,21.7,.9,0,0,0]),'BESS_sistema_MW':(64,[0,1.9,2.8,6.3,0,.9,.4,0,0,0,0,0,0,0,0,0,0,0,0,12.6,0,47.4,2.4,0])}
 checks=[];day=j[j.fecha.eq('2026-01-10')].sort_values('hora0')
 for col,(page,v) in vals.items():
  e=np.abs(day[col].to_numpy()-v);assert max(e)<=.051;checks.extend([dict(variable=col,pagina=page,hora0=k,API=float(x),impreso=y,error=abs(x-y)) for k,(x,y) in enumerate(zip(day[col],v))])
 pd.DataFrame(checks).to_csv(out/'contraste_informe_diario.csv',index=False)
 # Estado efectivo: tramos/paños y planta separados. Fuera del intervalo no se infiere normalidad universal.
 ev=pd.DataFrame([
  ['SD2025023534','Cerro Navia 52H3 abierto','2025-03-06 14:17','2025-03-06 23:50','EAF-108-2025.pdf',114],
  ['IF2026001051','Punta Peuco–Loma Los Colorados 110 kV fuera','2026-02-11 12:15','2026-02-11 13:55','Informe-Diario-11-02-2026.pdf',19],
  ['IF2026001051_planta','Loma Los Colorados 2 fuera (7 MW previos)','2026-02-11 12:15','2026-02-11 14:45','Informe-Diario-11-02-2026.pdf',19]],columns=['id','estado','inicio_local','fin_local','fuente','pagina']);ev.to_csv(out/'estados_efectivos.csv',index=False)
 hourly=[]
 for _,r in ev.iterrows():
  start=pd.Timestamp(r.inicio_local);end=pd.Timestamp(r.fin_local)
  for t in pd.date_range(start.floor('h'),end.floor('h'),freq='h'):
   minutes=(min(t+pd.Timedelta(hours=1),end)-max(t,start)).total_seconds()/60
   if minutes>0:hourly.append(dict(id=r.id,fecha=t.strftime('%Y-%m-%d'),hora0=t.hour,minutos_estado=minutes,fraccion_hora=minutes/60))
 hh=pd.DataFrame(hourly);hh.to_csv(out/'estados_fracciones_horarias.csv',index=False);assert hh.groupby('id').minutos_estado.sum().to_dict()=={'IF2026001051':100.,'IF2026001051_planta':150.,'SD2025023534':573.}
 z=panel[panel.fecha.eq('2025-03-06')].copy();z['diferencia_H4_TAP1']=z.F_H4-z.R_TAP1;z=z.merge(hh[hh.id.eq('SD2025023534')][['fecha','hora0','fraccion_hora']],on=['fecha','hora0'],how='left');z.to_csv(out/'episodio_CerroNavia.csv',index=False);full=z[z.fraccion_hora.eq(1)]
 net=dict(horas_completas=len(full),flujo_H4_MW=float(full.F_H4.mean()),retiro_TAP1_MW=float(full.R_TAP1.mean()),MAE_MW=float(full.diferencia_H4_TAP1.abs().mean()),WAPE_pct=float(100*full.diferencia_H4_TAP1.abs().sum()/full.R_TAP1.abs().sum()),MW_Canteras=float(full.MW.mean()))
 # Conservar extractos literales y hashes de los documentos que fijan estados.
 docs=[(S/'fuentes_operacion/20261011_maniobras_generacion/EAF-108-2025.pdf',[114]),(S/'fuentes_operacion/20261011_bess_estados_documentos/Informe-Diario-11-02-2026.pdf',[19]),(pdf,[52,58,64])];extract=[]
 for f,pages in docs:
  inputs.append(f);r=PdfReader(f)
  for p in pages:extract.append(dict(archivo=str(f.relative_to(S)),pagina=p,texto=r.pages[p-1].extract_text()))
 (out/'extractos_fuentes.json').write_text(json.dumps(extract,ensure_ascii=False,indent=2))
 inputs += [S/'PROTOCOLO_BESS_Y_ESTADOS_20261011.md',S/'ADENDA_BESS_VENTANA_20261011.md',Path(__file__)];inputs=list(dict.fromkeys(inputs));pd.DataFrame([dict(archivo=str(f.relative_to(S)),sha256=sha(f)) for f in inputs]).to_csv(out/'insumos_sha256.csv',index=False)
 pd.DataFrame(coverage).to_csv(out/'descargas.csv',index=False);info=dict(estado='OK',horas_BESS=len(b),horas_medicion=len(j),filas_15min=len(q),duplicados_BESS_exactos=len(raw)-len(g),noches_PFV_positivo=int(j.PFV_nocturno_positivo.sum()),episodio_CerroNavia=net);(out/'verificacion.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2));print(pd.DataFrame(metrics).to_string(index=False));print(pd.DataFrame(stat).to_string(index=False))
if __name__=='__main__':main()
