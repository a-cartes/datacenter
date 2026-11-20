"""Compara revisiones de demandas nodales e indisponibilidad declarada de unidades."""
import argparse
import io
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd


def matrices(z,dia):
    tablas=[]
    for f in ('Nod_Load.csv','Gen_UnitsOut.csv','Lin_Units.csv'):
        n,=[s for s in z.namelist() if Path(s).name==f]
        v=pd.read_csv(z.open(n),encoding='latin1')
        v=v[(v.YEAR==2024)&(v.MONTH==10)&(v.DAY==dia)]
        if 'NAME' in v:
            assert v.BAND.eq(1).all()
            v=v.pivot(index='PERIOD',columns='NAME',values='VALUE').reindex(range(1,25)).ffill()
        else:
            if 'BAND' in v: assert v.BAND.eq(1).all()
            v=v.drop(columns=['YEAR','MONTH','DAY','BAND'],errors='ignore').set_index('PERIOD').reindex(range(1,25))
        tablas.append(v)
    return tablas


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directorio',type=Path)
    p.add_argument('bases_octubre',type=Path)
    a=p.parse_args()
    h=pd.read_csv(a.directorio/'revisiones_octubre.csv',parse_dates=['inicio_local']).dropna(subset=['revision_PID'])
    salida=[]
    for revision,g in h.groupby('revision_PID'):
        dia=g.inicio_local.iloc[0].day
        with ZipFile(a.bases_octubre/f'{dia:02}.zip') as z:
            with ZipFile(io.BytesIO(z.read(f'DATOS202410{dia:02}.zip'))) as datos:
                original=matrices(datos,dia)
        with ZipFile(a.directorio/'pid'/(revision+'.zip')) as datos:
            cambios=matrices(datos,dia)
        series=[]
        for v,w in zip(original,cambios):
            # Objetos observables en ambas bases. Registrar cobertura de columnas.
            cols=v.columns.intersection(w.columns)
            x=v[cols]-w[cols]
            series.append(x)
        for r in g.itertuples():
            per=r.inicio_local.hour+1
            row=dict(inicio_local=r.inicio_local,revision=revision,FP_octubre=r.FP_octubre)
            for etiqueta,tabla in zip(('carga_nodal','gen_unitsout','lin_units'),series):
                par=tabla.loc[per].dropna()
                row[etiqueta+'_comparados']=len(par)
                row[etiqueta+'_cambios']=int((par.abs()>1e-4).sum())
            row['ajuste_flujo_MW']=r.revision_MW
            salida.append(row)
    pd.DataFrame(salida).sort_values('inicio_local').to_csv(a.directorio/'cambios_insumos.csv',index=False)


if __name__=='__main__':main()
