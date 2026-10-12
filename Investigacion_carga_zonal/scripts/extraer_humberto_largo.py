"""Selección de fuentes definitivas; extracción streaming y preservación por SHA."""
from pathlib import Path
import argparse,json,gzip,zipfile,hashlib,concurrent.futures
import pandas as pd
S=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def extract(job):
 root,rel,expected,dest=job;p=Path(root)/rel;o=Path(dest);o.mkdir();before=sha(p);assert before==expected;lines=0;hits=0
 with zipfile.ZipFile(p) as z,gzip.open(o/'seleccion_original.csv.gz','wb') as dst:
  assert len(z.namelist())==1
  with z.open(z.namelist()[0]) as f:
   dst.write(f.readline())
   for line in f:
    lines+=1
    if b'HUMBER' in line.upper():dst.write(line);hits+=1
 assert sha(p)==before
 info=dict(referencia='mediciones_legacy:'+rel,sha256=before,filas_revisadas=lines,filas_seleccionadas=hits,sin_cambios=True,seleccion_sha256=sha(o/'seleccion_original.csv.gz'));(o/'manifiesto.json').write_text(json.dumps(info,indent=2));return dict(mes=o.name,**info)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--originales',type=Path,required=True);a=ap.parse_args();out=S/'resultados/20261011_humberto_largo_fuentes';out.mkdir();inv=pd.read_csv(S/'resultados/20261011_inventario_v2/originales_disponibilidad.csv');q=inv[inv.ruta_relativa.str.contains('/Definitivo/1_Transferencia_Puntos_de_Medida_15MIN_CSV.zip',regex=False)].copy();q['mes']=q.ruta_relativa.str[:4]+'-'+q.ruta_relativa.str[5:7];q=q[q.mes.between('2024-08','2026-06')].sort_values('mes');assert len(q)==23 and q.mes.nunique()==23;q.to_csv(out/'fuentes_seleccionadas.csv',index=False)
 reuse={'2025-12':'20261011_medidores_humberto_dic2025','2026-01':'20261011_medidores_humberto','2026-02':'20261011_medidores_humberto_feb2026'};jobs=[];results=[]
 for _,r in q.iterrows():
  if r.mes in reuse:
   src=S/'resultados'/reuse[r.mes];m=json.loads((src/'manifiesto.json').read_text());assert m['sha256']==r.sha256;assert sha(a.originales/r.ruta_relativa)==r.sha256
   results.append(dict(mes=r.mes,referencia=m['referencia'],sha256=r.sha256,filas_seleccionadas=m['filas_seleccionadas'],sin_cambios=True,seleccion_reutilizada=str((src/'seleccion_original.csv.gz').relative_to(S)),seleccion_sha256=sha(src/'seleccion_original.csv.gz')))
  else:jobs.append((str(a.originales),r.ruta_relativa,r.sha256,str(out/r.mes)))
 with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
  for item in pool.map(extract,jobs):results.append(item);(out/'avance.json').write_text(json.dumps(results,indent=2));print(json.dumps(dict(mes=item['mes'],filas=item['filas_seleccionadas'])),flush=True)
 (out/'manifiesto.json').write_text(json.dumps(dict(estado='OK',meses=sorted(results,key=lambda x:x['mes'])),indent=2));print('FIN 23 meses',flush=True)
if __name__=='__main__':main()
