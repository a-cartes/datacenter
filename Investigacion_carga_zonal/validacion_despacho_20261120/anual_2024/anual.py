"""Brecha histórica de localización y sensibilidad financiera de la adjudicación inicial."""
import argparse
import hashlib
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile
from zoneinfo import ZoneInfo
import pandas as pd

AJ = 'AJAHUEL_______500'
LA = 'LO_AGUIRRE____500'
SEPT = 'https://www.coordinador.cl/wp-content/uploads/2024/09/Antecedentes_CMG_Real_def_240908.zip'
p = argparse.ArgumentParser()
p.add_argument('panel',type=Path)
args = p.parse_args()
datos = pd.read_parquet(args.panel)
datos = datos[(datos.anio==2024)&datos.barra.isin([AJ,LA])]
tabla = datos.groupby(['mes','barra'])[['sum_P','horas_P','horas_filas']].sum().unstack()
assert len(tabla)==12 and (tabla.horas_P==tabla.horas_filas).all().all()
assert tabla.horas_P[LA].equals(tabla.horas_P[AJ])
if not Path('sept.zip').exists():
    urlretrieve(SEPT,'sept.zip')
with ZipFile('sept.zip') as z:
    n, = [i for i in z.namelist() if 'PromediosBarras' in i and i.lower().endswith('_r.csv')]
    precios = pd.read_csv(z.open(n),sep=';',encoding='latin1')
cero = precios[precios.BARRA.isin([AJ,LA]) & precios.FECHA.eq(20240908) & precios.HORA.eq(0)]
assert len(cero)==8 and cero['CMg[mills/kWh]'].eq(0).all()
assert all(sorted(g.MINUTO)==[0,15,30,45] for _,g in cero.groupby('BARRA'))
salida = pd.DataFrame(index=tabla.index)
salida['horas_panel'] = tabla.horas_P[AJ]
zona = ZoneInfo('America/Santiago')
for mes in tabla.index:
    inicio = pd.Timestamp(str(mes)+'01',tz=zona)
    fin = inicio + pd.DateOffset(months=1)
    salida.loc[mes,'horas_fisicas'] = (fin-inicio)/pd.Timedelta(hours=1)
dif = salida.horas_panel-salida.horas_fisicas
assert dif[dif.ne(0)].to_dict()=={202409:1}
salida['suma_brecha'] = tabla.sum_P[LA]-tabla.sum_P[AJ]
salida['brecha_USD_MWh'] = salida.suma_brecha/salida.horas_fisicas
salida.to_csv('localizacion.csv',float_format='%.8f')
assert salida.horas_fisicas.sum()==8784
finanzas = []
for r in (0.05,0.07,0.10):
    costo = 40980000*r+655680
    for mw in (20,50,100):
        finanzas.append(dict(tasa=r,MW=mw,umbral_cierre_USD=costo,
                            umbral_inicio_USD=costo/(1+r),
                            umbral_por_MWh=costo/(8784*mw),
                            diferencia_valoracion_spot_USD=salida.suma_brecha.sum()*mw))
pd.DataFrame(finanzas).to_csv('sensibilidad.csv',index=False,float_format='%.6f')
print('SHA-256 panel y ZIP de septiembre')
for path in [args.panel,Path('sept.zip')]:
    print(hashlib.sha256(path.read_bytes()).hexdigest())
