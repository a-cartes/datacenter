from pathlib import Path
import json,argparse
import pandas as pd
from estimar_operacion_canteras import fit
from verificar_operacion_publica import compare
S=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('--ejecucion',default='20261011_bess_influencia_meses');a=ap.parse_args();out=S/'resultados'/a.ejecucion;assert out.parent.resolve()==(S/'resultados').resolve();out.mkdir();d=pd.read_csv(S/'resultados/20261011_bess_fisico_v1/panel_fisico.csv.gz');rows=[];spec=[]
for mes in sorted(d.mes.unique()):
 z=d[d.mes.ne(mes)]
 for name,x in [('base',['TAP_R12']),('fisico',['TAP_R12','SantiagoSolar_MW','D_FB123','R_FB123','H1_neto'])]:
  label='sin_'+mes+'_'+name;r,_=fit(z,x,label,'posthoc');rows+=r;spec.append(dict(modelo=label,mes_excluido=mes,extras=x))
pd.DataFrame(rows).to_csv(out/'estimaciones.csv',index=False);(out/'especificaciones.json').write_text(json.dumps(spec,indent=2));again=[]
for sp in spec:
 r,_=fit(d[d.mes.ne(sp['mes_excluido'])],sp['extras'],sp['modelo'],'verificacion');again+=r
(out/'verificacion.json').write_text(json.dumps(compare(again,pd.read_csv(out/'estimaciones.csv')),indent=2));r=pd.DataFrame(rows);print(r[r.resultado.eq('zona_lejos5')&r.contraste.eq('solar')][['modelo','n_horas','beta','lo95','hi95','sd_MW_parcial']].to_string(index=False))
