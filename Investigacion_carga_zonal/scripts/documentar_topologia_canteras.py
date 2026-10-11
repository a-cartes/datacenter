"""Extracto trazable de topología del catálogo; no reconstruye límites históricos N-1."""
from pathlib import Path
import argparse,json
import pandas as pd
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--proyecto',type=Path,required=True);a=ap.parse_args()
 root=a.proyecto.resolve();folder=root/'Replica_RM_desde_cero/prospectiva_2030/extraidos/infotecnica';out=S/'resultados/20261011_topologia_operativa_v1'
 if out.exists():raise ValueError('Se exige salida nueva')
 files=[folder/'tramos_extremos.csv',folder/'secciones_lineas.csv'];hashes=[sha(p) for p in files];out.mkdir()
 mapping=pd.DataFrame([('H1',5445,'TAP BATUCO'),('H2',5674,'TAP BATUCO'),('H3',5673,'TAP OFF LIBERTADORES H2'),('H4',5444,'TAP OFF LIBERTADORES H1')],columns=['canal_Canteras','id_tramo','extremo_remoto_resumen'])
 tramos=pd.read_csv(files[0]);sections=pd.read_csv(files[1]);m=mapping.merge(tramos,left_on='id_tramo',right_on='id',validate='one_to_one')
 assert len(m)==4 and m.extremo1_descripcion.str.cat(m.extremo2_descripcion).str.contains('CANTERAS').all()
 sec=mapping.merge(sections,on='id_tramo',validate='one_to_many');assert len(sec)==8
 m.to_csv(out/'canales_y_extremos.csv',index=False);sec.to_csv(out/'secciones_y_limites_catalogo.csv',index=False)
 checks=[dict(referencia=str(p.relative_to(root)),sha256=h,sin_cambios=sha(p)==h) for p,h in zip(files,hashes)];assert all(v['sin_cambios'] for v in checks)
 pd.DataFrame(checks).to_csv(out/'fuentes_y_verificacion.csv',index=False)
 (out/'alcance.json').write_text(json.dumps(dict(estado='OK',canales=4,secciones=8,interpretacion='Catálogo disponible: trazado local y límites por sección. No certifica la topología de cada fecha, ni límites operativos N-1. La potencia activa medida en MW no equivale a la potencia aparente nominal en MVA. Se conservan rótulos originales, incluso C1 en el tramo 5674.',originales_modificados=0),ensure_ascii=False,indent=2))
 print(m[['canal_Canteras','id_tramo','nombre','extremo_remoto_resumen']].to_string(index=False))
if __name__=='__main__':main()
