from pathlib import Path
import json,gzip
import pandas as pd
from estimar_operacion_canteras import fit
from verificar_operacion_publica import compare,independent
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1];p=S/'resultados/20261011_calidad_generacion_v1';d=pd.read_csv(S/'resultados/20261011_generacion_v3/panel_generacion.csv.gz');rows=[];out={};pars=pd.read_csv(p/'parametros.csv')
for spec in json.loads((p/'especificaciones.json').read_text()):
 z=d[d.fecha.isin(spec['fechas'])];assert len(z)==spec['n'];r,_=fit(z,spec['extras'],spec['modelo'],'calidad_posterior');rows+=r
 if spec['modelo']=='completa_Santiago':
  v=pars[pars.modelo.eq(spec['modelo'])&pars.resultado.eq('zona_lejos5')].set_index('variable').loc[['MW','MW_solar','MW_tarde']+spec['extras'],'beta'].to_numpy();out['LSQR_Santiago']=independent(z,spec['extras'],v)
out['reproduccion']=compare(rows,pd.read_csv(p/'estimaciones.csv'));h=pd.read_csv(p/'insumos_sha256.csv');assert all(sha(S/r.archivo)==r.sha256 for r in h.itertuples())
m=json.loads((S/'fuentes_operacion/20261011_generacion_completa/manifiesto.json').read_text());names={364:'PFV SANTIAGO SOLAR',2209:'PFV DON HUMBERTO'}
for row in m['paginas']:
 f=S/'fuentes_operacion/20261011_generacion_completa'/row['archivo'];assert sha(f)==row['sha256'];obj=json.loads(gzip.open(f).read());records=obj.get('data',obj.get('content',[]));assert all(x['central']==names[row['idCentral']] and x['tipo_tecnologia']=='Solar' for x in records)
f=S/'resultados/verificacion_calidad_generacion_20261011.json';assert not f.exists();out.update(estado='OK',nombres_y_tipo_API_verificados=True,rotulo_API_no_certifica_frontera_PV=True);f.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
