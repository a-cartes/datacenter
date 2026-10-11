"""Extracción selectiva del ZIP definitivo existente; no modifica originales."""
from pathlib import Path
import argparse,zipfile,gzip,hashlib,json
import pandas as pd
S=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--zip',type=Path,required=True);ap.add_argument('--ejecucion',required=True);a=ap.parse_args();out=S/'resultados'/a.ejecucion;assert out.parent.resolve()==(S/'resultados').resolve();out.mkdir()
 inv=pd.read_csv(S/'resultados/20261011_inventario_v2/originales_disponibilidad.csv');matches=inv[inv.ruta_relativa.map(lambda v:str(a.zip).endswith(v))];assert len(matches)==1;before=sha(a.zip);assert before==matches.iloc[0].sha256
 n=0;hits=0
 with zipfile.ZipFile(a.zip) as z,gzip.open(out/'seleccion_original.csv.gz','wb') as dst:
  assert len(z.namelist())==1
  with z.open(z.namelist()[0]) as f:
   dst.write(f.readline())
   for line in f:
    n+=1;parts=line.split(b';',3);head=b';'.join(parts[:3]).upper()
    if any(p in head for p in [b'HUMBER',b'DHUMB']):dst.write(line);hits+=1
 d=pd.read_csv(out/'seleccion_original.csv.gz',sep=';',decimal=',',encoding='utf-8-sig');d.groupby(['ID_SOC','IDSOCKET','SUBESTACION','TENSION']).agg(n=('ID_SOC','size'),D=('kWhD','sum'),R=('kWhR','sum')).to_csv(out/'canales.csv')
 after=sha(a.zip);assert before==after
 (out/'manifiesto.json').write_text(json.dumps(dict(archivo_original=a.zip.name,referencia='mediciones_legacy:'+matches.iloc[0].ruta_relativa,sha256=before,filas_revisadas=n,filas_seleccionadas=hits,sin_cambios=True),indent=2));print(d.groupby(['IDSOCKET','SUBESTACION']).size().to_string())
if __name__=='__main__':main()
