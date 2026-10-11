"""Episodios operativos documentados y descomposición exacta de agregación mensual."""
from pathlib import Path
import argparse,hashlib,json,re
import numpy as np
import pandas as pd
from pypdf import PdfReader
S=Path(__file__).resolve().parents[1];R=S.parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--proyecto',type=Path,required=True);ap.add_argument('--ejecucion',default='20261011_episodios_horarios_v1');a=ap.parse_args();project=a.proyecto.resolve();out=S/'resultados'/a.ejecucion
 if out.exists():raise SystemExit('Conservar ejecución existente')
 base=S/'resultados/20261011_horas_v1';pdfdir=project/'Panel_datos/revision_causal_2026_09_28/fuentes';cases=[('499','07-10-2024'),('519','26-10-2024'),('534','06-11-2024')]
 inputs=[base/'panel_horario.csv.gz',S/'PROTOCOLO_HORARIO_20261011.md',Path(__file__).resolve()]+[pdfdir/f'CEN_EAF{k}_2024.pdf' for k,_ in cases]
 hashes=[dict(referencia=('repositorio:'+str(p.relative_to(R))) if p.is_relative_to(R) else ('proyecto:'+str(p.relative_to(project))),sha256=sha(p),bytes=p.stat().st_size) for p in inputs];out.mkdir();pd.DataFrame(hashes).to_csv(out/'insumos_sha256.csv',index=False)
 records=[];coverage=[]
 for number,date in cases:
  pdf=pdfdir/f'CEN_EAF{number}_2024.pdf';reader=PdfReader(pdf);pages=[]
  for i,page in enumerate(reader.pages):
   if i<50:continue
   text=page.extract_text(extraction_mode='layout')
   if date not in text[:180] or 'Hora Movi.' not in text[:2000]:continue
   pages.append(i+1)
   for line in text.splitlines():
    if 'Alto Jahuel' in line and ('Ctx' in line or 'Inicia Prorrata' in line):records.append(dict(pdf=pdf.name,fecha=pd.to_datetime(date,dayfirst=True).strftime('%Y-%m-%d'),pagina=i+1,texto=re.sub(r'\s+',' ',line).strip()))
  coverage.append(dict(pdf=pdf.name,fecha=date,paginas_log_revisadas=len(pages),paginas=';'.join(map(str,pages))))
 pd.DataFrame(records).to_csv(out/'eventos_extraidos_CEN.csv',index=False);pd.DataFrame(coverage).to_csv(out/'cobertura_revision_documental.csv',index=False)
 # Explicit intervals based on operative text. Nov6 before01:34 remains unknown;
 # partial hours are never assigned a complete-hour status.
 intervals=[('2024-10-07',0,390,'restriccion','estado00 y FinalizaCtx06:30'),('2024-10-07',390,1380,'sin_ese_control','Finaliza06:30; Inicia23:00'),('2024-10-07',1380,1440,'restriccion','IniciaCtx23:00'),('2024-10-26',0,462,'restriccion','estado00 y FinalizaCtx07:42'),('2024-10-26',462,1350,'sin_ese_control','Finaliza07:42; Inicia22:30'),('2024-10-26',1350,1440,'restriccion','IniciaCtx22:30'),('2024-11-06',94,388,'restriccion','IniciaProrrata01:34 y FinalizaCtx06:28; no inferir estado00'),('2024-11-06',388,1390,'sin_ese_control','Finaliza06:28; Inicia23:10'),('2024-11-06',1390,1440,'restriccion','IniciaCtx23:10')]
 pd.DataFrame(intervals,columns=['fecha','desde_minuto','hasta_minuto','estado','evidencia']).to_csv(out/'intervalos_interpretados.csv',index=False)
 d=pd.read_csv(base/'panel_horario.csv.gz');e=d[d.fecha.isin([v[0] for v in intervals])].copy();e['estado']='transicion_o_desconocido'
 for day,start,end,state,evidence in intervals:
  mask=e.fecha.eq(day)&(e.hora0*60>=start)&((e.hora0+1)*60<=end);e.loc[mask,'estado']=state
 e.to_csv(out/'episodios_horarios.csv',index=False);summary=e.groupby(['fecha','estado']).agg(horas=('MW','size'),MW=('MW','mean'),Q=('Q','mean'),D_zona=('D_zona','mean'),zona_cerca=('zona_cerca','mean'),zona_lejos5=('zona_lejos5','mean')).reset_index();summary.to_csv(out/'episodios_resumen.csv',index=False)
 # Common all-hour x makes the covariance decomposition exact. No mixing slopes from different regressors.
 m=d.groupby('mes').mean(numeric_only=True);x=m.MW-m.MW.mean();var=float(x.dot(x));rows=[]
 for y in ['zona_cerca','zona_lejos5','zona_lejos7','canteras_lejos5','D_zona']:
  contributions=[]
  for block,w in [('resto',12/24),('solar_10_16',7/24),('tarde_19_23',5/24)]:
   b=d[d.bloque.eq(block)].groupby('mes')[y].mean().reindex(m.index);beta=float(x.dot(b-b.mean())/var);c=w*beta;contributions.append(c);rows.append(dict(resultado=y,bloque=block,peso_horas=w,beta_con_MW_medio_total=beta,contribucion_beta_agregada=c))
  total=float(x.dot(m[y]-m[y].mean())/var);assert abs(total-sum(contributions))<1e-10
  rows.append(dict(resultado=y,bloque='TOTAL',peso_horas=1,beta_con_MW_medio_total=total,contribucion_beta_agregada=sum(contributions)))
 pd.DataFrame(rows).to_csv(out/'descomposicion_pendiente_mensual.csv',index=False)
 preserved=[dict(referencia=h['referencia'],sin_cambios=sha(p)==h['sha256']) for p,h in zip(inputs,hashes)];assert all(x['sin_cambios'] for x in preserved);pd.DataFrame(preserved).to_csv(out/'verificacion_insumos.csv',index=False)
 (out/'verificacion.json').write_text(json.dumps(dict(estado='OK',insumos_preservados=len(inputs),dias_caso=e.fecha.nunique(),horas_por_estado=e.estado.value_counts().to_dict(),nota='Ausencia de ese control no prueba ausencia de otras restricciones; casos no aleatorios'),indent=2,ensure_ascii=False))
 print(summary.to_string(index=False));print(pd.DataFrame(rows).query("resultado=='zona_lejos5'").to_string(index=False))
if __name__=='__main__':main()
