from pathlib import Path
import argparse,json
from extraer_humberto_largo import extract
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--legacy',type=Path,required=True);a=ap.parse_args();out=S/'resultados/20261011_humberto_fuentes_final2026';out.mkdir();res=[]
 for month,name in [('07','Julio'),('08','Agosto')]:
  old=json.loads((a.legacy/f'extractos/medidores_candidatos_2026_{month}_manifest.json').read_text());rel=f'2026/{month}_{name}/Definitivo/1_Transferencia_Puntos_de_Medida_15MIN_CSV.zip';r=extract((str(a.legacy/'originales_descargados'),rel,old['sha256_original'],str(out/f'2026-{month}')));r['raiz_original']='mediciones_legacy:originales_descargados';r['fuente_hash_anterior']=f'mediciones_legacy:extractos/medidores_candidatos_2026_{month}_manifest.json';res.append(r);print(r['mes'],r['filas_seleccionadas'],flush=True)
 (out/'manifiesto.json').write_text(json.dumps(dict(estado='OK',meses=res),indent=2))
if __name__=='__main__':main()
