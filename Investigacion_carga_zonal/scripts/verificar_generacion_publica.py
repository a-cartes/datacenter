"""Reproducción de 375 contrastes y dos verificaciones numéricas independientes."""
from pathlib import Path
import argparse,json
import pandas as pd
from estimar_operacion_canteras import fit
from estimar_heterogeneidad_horaria import sha
from verificar_operacion_publica import independent,compare
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args();assert not a.salida.exists();p=S/'resultados/20261011_generacion_v3';d=pd.read_csv(p/'panel_generacion.csv.gz');target=pd.read_csv(p/'estimaciones.csv');params=pd.read_csv(p/'parametros.csv');rows=[];out={}
 assert not d.duplicated(['fecha','hora0']).any();assert d.groupby('fecha').size().eq(24).all()
 for spec in json.loads((p/'especificaciones.json').read_text()):
  z=d[d.fecha.isin(spec['fechas'])].copy();assert len(z)==spec['n'];assert not z[spec['extras']].isna().any().any();r,_=fit(z,spec['extras'],spec['modelo'],spec['familia']);rows+=r
  if spec['modelo'] in ['base_google','google_PV']:
   expected=params[params.modelo.eq(spec['modelo'])&params.resultado.eq('zona_lejos5')].set_index('variable').loc[['MW','MW_solar','MW_tarde']+spec['extras'],'beta'].to_numpy();out['LSQR_'+spec['modelo']]=independent(z,spec['extras'],expected)
 out['reproduccion']=compare(rows,target)
 h=pd.read_csv(p/'insumos_sha256.csv');assert all(sha(S/r.archivo)==r.sha256 for r in h.itertuples());out.update(insumos_preservados=len(h),estado='OK',requiere_originales_privados=False)
 a.salida.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
