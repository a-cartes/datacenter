"""Conciliación ex post de la última revisión con vigencia ese día y el programa diario."""
import argparse
import hashlib
import re
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import openpyxl
import pandas as pd

LINEA = 'LoAguirre500->AJahuel500'
CAMPOS = {LINEA:'flujo','Demanda Total [MWh]':'demanda','Costos Totales [kUSD]':'costo'}


def programa(ruta,fecha,inicio,intradiario):
    with ZipFile(ruta) as z:
        nombre, = [n for n in z.namelist() if Path(n).name.upper().startswith('PRG') and n.lower().endswith('.xlsx')]
        w = openpyxl.load_workbook(z.open(nombre),read_only=True,data_only=True)
        filas = list(w['PROGRAMA'].values)
        assert filas[3][2].date()==fecha.date() and list(filas[3][4:28])==list(range(1,25))
        columnas = {}
        for etiqueta,n in CAMPOS.items():
            row, = [r for r in filas if r[2]==etiqueta]
            columnas[n] = np.asarray(row[4:28],dtype=float)
        columnas['flujo'] *= -1
        df = pd.DataFrame(columnas,index=pd.date_range(fecha,periods=24,freq='h')).iloc[inicio-1:].copy()
        if intradiario:
            nombre, = [n for n in z.namelist() if n.endswith('/Lin_MinRating.csv')]
            rating = pd.read_csv(z.open(nombre))
            valores = rating[rating.NAME.eq(LINEA)]
            assert not valores.empty and valores.VALUE.nunique()==1
            df['limite_modelado']=-valores.VALUE.iloc[0]
        return df


def main():
    ap=argparse.ArgumentParser()
    for k in ['carpeta','prg_octubre','octubre_publicado']:
        ap.add_argument(k,type=Path)
    a=ap.parse_args()
    base=pd.read_csv(a.octubre_publicado/'horas.csv',index_col=0,parse_dates=True)
    base=base.join(pd.read_csv(a.octubre_publicado/'programado.csv',index_col=0,parse_dates=True),validate='one_to_one')
    diario=pd.concat([programa(a.prg_octubre/f'{d:02}.zip',pd.Timestamp(2024,10,d),1,False) for d in range(1,32)])
    np.testing.assert_allclose(diario.flujo,base.flujo_PCP_MW,atol=1e-5)
    base=base.join(diario.add_suffix('_PCP'))
    revisiones=[]
    for r in pd.read_csv(a.carpeta/'fuentes_pid.csv').itertuples():
        ruta=a.carpeta/r.archivo
        assert hashlib.sha256(ruta.read_bytes()).hexdigest()==r.sha256
        fecha,inicio=re.search(r'PID_(\d{8})_(\d{2})',ruta.name).groups()
        prog=programa(ruta,pd.Timestamp(fecha),int(inicio),True)
        prog['revision']=ruta.stem
        prog['periodo_inicio']=int(inicio)
        revisiones.append(prog)
    lista=pd.concat(revisiones).rename_axis('inicio_local').reset_index().sort_values('periodo_inicio')
    ultima=lista.drop_duplicates('inicio_local',keep='last').set_index('inicio_local')
    out=base.join(ultima.add_suffix('_PID'),validate='one_to_one')
    out['revision_MW']=out.flujo_PCP-out.flujo_PID
    out['residuo_MW']=out.flujo_PID-out.envio_MW
    out['FP_octubre']=out.congestion_PCP.eq(1)&out.min_control.eq(0)
    ok=out.revision_MW.notna()
    np.testing.assert_allclose(out.loc[ok,'revision_MW']+out.loc[ok,'residuo_MW'],out.loc[ok,'error_flujo_MW'],atol=1e-6)
    cols=['estado','FP_octubre','envio_MW','flujo_PCP','flujo_PID','revision_PID','limite_modelado_PID',
          'revision_MW','residuo_MW','error_flujo_MW','demanda_PCP','demanda_PID','costo_PCP','costo_PID']
    out[cols].to_csv(a.carpeta/'revisiones_octubre.csv',float_format='%.8f')


if __name__=='__main__':
    main()
