"""Calendario documental separado de inferencias a partir de medidores."""
from pathlib import Path
import json,hashlib
import pandas as pd
from pypdf import PdfReader
S=Path(__file__).resolve().parents[1];O=S/'resultados/20261011_maniobras_generacion_v1';O.mkdir();src=S/'fuentes_operacion/20261011_maniobras_generacion'
refs=[('EAF-092-2025.pdf','https://www.coordinador.cl/wp-content/uploads/2025/03/EAF-092-2025.pdf',[1,2,3,4]),('EAF-093-2025.pdf','https://www.coordinador.cl/wp-content/uploads/2025/03/EAF-093-2025.pdf',[1,2,3,5]),('EAF-108-2025.pdf','https://www.coordinador.cl/wp-content/uploads/2025/03/EAF-108-2025.pdf',[64,67,84,106,107]),('IRF2026001051.pdf','https://www.coordinador.cl/wp-content/uploads/2026/02/IRF_11022026_Linea-de-110-kV-Punta-Peuco-Loma-Los-Colorados_IF2026001051.pdf',[1])]
manifest=[];texts=[]
for file,url,pages in refs:
 f=src/file;r=PdfReader(f);manifest.append(dict(archivo=str(f.relative_to(S)),url=url,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),paginas=pages))
 texts +=[dict(archivo=file,pagina=i,texto=r.pages[i-1].extract_text()) for i in pages]
(O/'fuentes.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));(O/'extractos.json').write_text(json.dumps(texts,ensure_ascii=False,indent=2))
events=[
 dict(fecha='2025-01-22',instalacion='Las Canteras–Santiago Solar 110 kV',inicio='12:54',fin='17:52',tipo='Ctx y prorrata',evidencia='Intervalo de restricción; distinto del horario de la desconexión programada',fuente='EAF039/2025 pp58,65; SD2025004130 p136; SI2025005181 p101'),
 dict(fecha='2025-02-26',instalacion='Cerro Navia–Tap Libertadores C2',inicio='13:36',fin='19:48',tipo='Falla',evidencia='Ramas próximas a conductores; Tap Libertadores–Canteras C2 normaliza19:40',fuente='EAF092/2025 pp1–3'),
 dict(fecha='2025-02-26',instalacion='Tap Libertadores–Las Canteras C1',inicio='14:41',fin='20:08',tipo='Falla',evidencia='Mismo vano con vegetación; tramo Cerro Navia–Tap Libertadores normaliza20:19',fuente='EAF093/2025 pp1–3'),
 dict(fecha='2025-03-06',instalacion='Las Canteras–Cerro Navia C1',inicio='',fin='23:50',tipo='Reparación forzosa',evidencia='14:12 solicitud por punto con temperatura;18:36 HR Las Vegas cerrado;23:50 línea cerrada. Apertura efectiva pendiente',fuente='EAF108/2025 anexos pp84,106,107; SDCF2025023534'),
 dict(fecha='2026-02-11',instalacion='Punta Peuco–Loma Los Colorados 110 kV',inicio='12:15',fin='',tipo='Falla',evidencia='Causa preliminar: intervención fortuita durante trabajos en Rucasol; sin término certificado en IRF',fuente='IRF2026001051 p1')]
pd.DataFrame(events).to_csv(O/'eventos_documentados.csv',index=False)
p=pd.read_csv(S/'resultados/20261011_generacion_v3/panel_generacion.csv.gz');p=p[p.episodio4].copy()
# Solo intervalos completos de eventos con extremos documentados. No se imputa ausencia al resto.
for name,day,start,end in [('ctx_local','2025-01-22',12*60+54,17*60+52),('falla_C2','2025-02-26',13*60+36,19*60+40),('falla_C1','2025-02-26',14*60+41,20*60+8)]:
 p[name+'_minutos']=pd.NA;ix=p.fecha.eq(day);lo=p.loc[ix,'hora0']*60;p.loc[ix,name+'_minutos']=(pd.concat([lo+60,pd.Series(end,index=lo.index)],axis=1).min(axis=1)-pd.concat([lo,pd.Series(start,index=lo.index)],axis=1).max(axis=1)).clip(lower=0)
cols=['fecha','hora0','MW','TAP_R12','SantiagoSolar_MW','DonHumberto_MW','PV_total_MW','F_H1','F_H2','F_H3','F_H4','zona_lejos5']+[c for c in p if c.endswith('_minutos')];p[cols].to_csv(O/'calendario_episodios.csv',index=False)
checks=[dict(comprobacion='H3 y H4 nulos durante horas15–18 del26feb',valor=bool(p[p.fecha.eq('2025-02-26')&p.hora0.between(15,18)][['F_H3','F_H4']].eq(0).all().all())),dict(comprobacion='HT12 positivo durante esas horas; EAF092 declara0MWprevio en otra frontera/informe',valor=float(p[p.fecha.eq('2025-02-26')&p.hora0.between(15,18)].MW.mean()))]
(O/'observaciones_medicion.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print(json.dumps(checks,ensure_ascii=False))
