"""Auditoría posterior de generación nocturna; no altera datos ni modelos anteriores."""
from pathlib import Path
import argparse,json
import pandas as pd
from estimar_operacion_canteras import fit
from estimar_heterogeneidad_horaria import sha
S=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ejecucion',default='20261011_calidad_generacion_v1');a=ap.parse_args();o=S/'resultados'/a.ejecucion;assert o.parent.resolve()==(S/'resultados').resolve();o.mkdir();files=[S/'resultados/20261011_generacion_v3/panel_generacion.csv.gz',S/'ADENDA_CALIDAD_GENERACION_20261011.md',Path(__file__)];before=[sha(f) for f in files];d=pd.read_csv(files[0]);night=d.hora0.isin([0,1,2,3,4,5,22,23]);an=d[night & d.DonHumberto_MW.gt(.1)];an[['fecha','hora0','DonHumberto_MW','SantiagoSolar_MW']].to_csv(o/'registros_nocturnos.csv',index=False)
 sets=[('completa',d)];audit=[]
 for v in [.1,1.]:
  days=d.loc[night&d.DonHumberto_MW.gt(v),'fecha'].unique();sets.append((f'umbral{v}',d[~d.fecha.isin(days)].copy()));audit.append(dict(umbral_MW=v,horas_marcadas=int((night&d.DonHumberto_MW.gt(v)).sum()),dias_excluidos=len(days),SantiagoSolar_horas_marcadas=int((night&d.SantiagoSolar_MW.gt(v)).sum())))
 rows=[];params=[];specs=[]
 for label,z in sets:
  for model,extras in [('base',['TAP_R12']),('Santiago',['TAP_R12','SantiagoSolar_MW']),('ambas',['TAP_R12','SantiagoSolar_MW','DonHumberto_MW'])]:
   name=label+'_'+model;r,p=fit(z,extras,name,'calidad_posterior');rows+=r;params+=p;specs.append(dict(modelo=name,extras=extras,fechas=sorted(z.fecha.unique().tolist()),n=len(z)))
 pd.DataFrame(rows).to_csv(o/'estimaciones.csv',index=False);pd.DataFrame(params).to_csv(o/'parametros.csv',index=False);(o/'especificaciones.json').write_text(json.dumps(specs,indent=2));(o/'auditoria.json').write_text(json.dumps(audit,indent=2));pd.DataFrame([dict(archivo=str(f.relative_to(S)),sha256=h) for f,h in zip(files,before)]).to_csv(o/'insumos_sha256.csv',index=False);assert before==[sha(f) for f in files]
 r=pd.DataFrame(rows);print(audit);print(r[r.resultado.eq('zona_lejos5')&r.contraste.eq('solar')][['modelo','n_horas','beta','lo95','hi95']].to_string(index=False))
if __name__=='__main__':main()
