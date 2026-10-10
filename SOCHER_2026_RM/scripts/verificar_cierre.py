"""Controles de regresión científica contra resultados previos y cálculos independientes."""
from pathlib import Path
import json, sys, platform, importlib.metadata
import numpy as np
import pandas as pd

R=Path(__file__).resolve().parents[1]
PACKAGE=Path(sys.argv[1]); OUT=Path(sys.argv[2]); REF=PACKAGE/'referencia'
checks=[]
def ok(name,condition,details=None):
    if not bool(condition):raise AssertionError(name+': '+str(details))
    checks.append({'control':name,'estado':'OK','detalle':details})
def close(name,a,b,tol=1e-7):
    ok(name,np.isclose(a,b,rtol=tol,atol=tol),{'obtenido':float(a),'referencia':float(b)})
def frame(name,a,b,keys):
    a=a.sort_values(keys).reset_index(drop=True);b=b.sort_values(keys).reset_index(drop=True)
    pd.testing.assert_frame_equal(a,b,check_dtype=False,rtol=1e-7,atol=1e-8)
    ok(name,True,{'filas':len(a),'columnas':len(a.columns)})

for source in sorted((PACKAGE/'datos/analitico').glob('muestra_*.csv')):
    frame('Reconstrucción del emparejamiento '+source.stem,
          pd.read_csv(R/'datos/analitico'/source.name),pd.read_csv(source),
          ['unidad_copia','anio'] if 'sin_emparejar' not in source.name else ['unidad','anio'])
for file,keys in [('estimaciones.csv',['especificacion']),('sensibilidad_exclusion.csv',['excluida'])]:
    frame(file,pd.read_csv(R/'resultados/socher_20261005'/file),pd.read_csv(REF/'socher_20261005'/file),keys)
frame('Contrastes por cohorte',pd.read_csv(R/'resultados/cierre_socher_20261009/contrastes_cohortes.csv'),pd.read_csv(REF/'cierre_socher_20261009/contrastes_cohortes.csv'),['unidad'])
frame('Figura 1 y series anuales',pd.read_csv(R/'resultados/cierre_socher_20261009/series_grupos_anuales.csv'),pd.read_csv(REF/'cierre_socher_20261009/series_grupos_anuales.csv'),['grupo','anio'])
frame('Series mensuales',pd.read_csv(R/'resultados/cierre_socher_20261009/series_grupos_mensuales.csv'),pd.read_csv(REF/'cierre_socher_20261009/series_grupos_mensuales.csv'),['grupo','mes'])
frame('Controles Lampa 2020-2021',pd.read_csv(R/'resultados/cierre_socher_20261009/cambios_controles_2020_2021.csv'),pd.read_csv(REF/'cierre_socher_20261009/cambios_controles_2020_2021.csv'),['unidad'])
co=pd.read_csv(R/'resultados/cierre_socher_20261009/contrastes_cohortes.csv').sort_values('G')
x=pd.read_csv(R/'resultados/socher_20261005/muestra_principal.csv')
u=x.drop_duplicates(['unidad','anio'])
ok('189 observaciones únicas y 297 filas con copias',len(u)==189 and len(x)==297)
ok('Tres tratados y 18 controles',u.loc[u.G>0,'unidad'].nunique()==3 and u.loc[u.G==0,'unidad'].nunique()==18)
ok('Cada distrito-año suma peso uno',np.allclose(x.groupby(['unidad','anio']).peso.sum(),1))
ok('Pesos por cohorte 5/12,4/12,3/12',np.allclose(co.n_post/co.n_post.sum(),[5/12,4/12,3/12]))
res=json.loads((R/'resultados/socher_20261005/resultados.json').read_text())
main=res['principal'][0] if isinstance(res['principal'],list) else res['principal']
close('ATT independiente y regresión',np.average(co.ATT,weights=co.n_post),main['att'])
close('Contraste contra período previo completo',np.average(co.contraste_pre_completo,weights=co.n_post),-0.08662832481245138)
a=json.loads((R/'resultados/cierre_socher_20261009/contrastes_estadisticos.json').read_text());b=json.loads((REF/'cierre_socher_20261009/contrastes_estadisticos.json').read_text())
close('Misma muestra con Lampa 2023',a['fecha_original_misma_muestra']['ATT'],b['fecha_original_misma_muestra']['ATT'])
for n in [0,1]:close('IC fecha anterior '+str(n),a['fecha_original_misma_muestra']['IC95'][n],b['fecha_original_misma_muestra']['IC95'][n])
ok('Test completo singular',a['restricciones']==12 and a['rango_covarianza']==5)
close('Test ventana común F',a['test_previo_ventana_comun']['F'],b['test_previo_ventana_comun']['F'])
close('Test ventana común p',a['test_previo_ventana_comun']['p_convencional'],b['test_previo_ventana_comun']['p_convencional'],1e-18)
# Contrastar los 96 valores archivados con el extracto horario. No relee el XLSM original.
from comun import canon
raw=pd.read_csv(REF/'cierre_socher_20261009/muestra_original_agosto_2021.csv')
hour=pd.read_parquet(R/'datos/precios_hist/202108.parquet');hour['barra']=hour.barra.map(canon)
v=raw.merge(hour[['barra','dia','hora','P']],on=['barra','dia','hora'],validate='one_to_one',suffixes=('_archivado','_extraido'))
ok('96 precios auditados frente a extracto horario',len(v)==96 and np.max(abs(v.P_original-v.P_extraido))<1e-9)
inv=pd.read_csv(R/'datos/instalaciones/instalaciones.csv');hit=pd.read_csv(R/'datos/instalaciones/hitos.csv');sources=pd.read_csv(R/'datos/instalaciones/fuentes_instalaciones.csv')
ok('Inventario, hitos y fuentes',len(inv)==63 and len(hit)==138 and len(sources)==65,{'registros':len(inv),'hitos':len(hit),'fuentes':len(sources)})
sens=pd.read_csv(R/'resultados/socher_20261005/sensibilidad_demanda_RM_2030.csv')
ok('Sensibilidad energética independiente',np.allclose(sens.energia_TWh,1038*8760*np.array([.6,.8,1])/1e6))
# Salida lista para consultar, sin mezclar la evidencia congelada con la recién calculada.
table=pd.DataFrame([
 {'especificacion':'Principal distrital, Lampa 2022','USD_MWh':main['att'],'IC95_inferior':main['ic95_inf'],'IC95_superior':main['ic95_sup']},
 {'especificacion':'Misma muestra, Lampa 2023','USD_MWh':a['fecha_original_misma_muestra']['ATT'],'IC95_inferior':a['fecha_original_misma_muestra']['IC95'][0],'IC95_superior':a['fecha_original_misma_muestra']['IC95'][1]},
])
loo=pd.read_csv(R/'resultados/socher_20261005/sensibilidad_exclusion.csv').set_index('excluida').loc['LAMPA-4']
table=pd.concat([table,pd.DataFrame([{'especificacion':'Exclusión de Lampa','USD_MWh':loo.att,'IC95_inferior':loo.ic95_inf,'IC95_superior':loo.ic95_sup},{'especificacion':'Contraste descriptivo contra todo el período previo','USD_MWh':np.average(co.contraste_pre_completo,weights=co.n_post)}])],ignore_index=True)
table.to_csv(OUT/'tabla_1.csv',index=False)
import shutil
shutil.copy2(R/'resultados/cierre_socher_20261009/diagnostico_lampa.png',OUT/'figura_1.png')
sens.to_csv(OUT/'sensibilidad_2030.csv',index=False)
versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','pyarrow','matplotlib','statsmodels','scipy']}
report={'estado':'OK','alcance':'Regeneración desde paneles derivados, covariables e historias congeladas; sin descargar originales ni ejecutar PET26.','controles':checks,'versiones_python':versions,'versiones_R':res['versiones'],'cifras_tabla_1':json.loads(table.to_json(orient='records'))}
(OUT/'verificacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
