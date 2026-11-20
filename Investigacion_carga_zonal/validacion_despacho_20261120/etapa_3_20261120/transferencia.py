"""Volumen histórico por encima de un techo hipotético de potencia activa, por dirección."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

def indicadores(flujo, horas, techo):
    exceso=(flujo.abs()-techo).clip(lower=0)
    return dict(n=len(flujo),horas_AJ_LA=(flujo>techo).sum()*horas,
                horas_LA_AJ=(flujo < -techo).sum()*horas,
                MWh_AJ_LA=((flujo-techo).clip(lower=0)*horas).sum(),
                MWh_LA_AJ=((-flujo-techo).clip(lower=0)*horas).sum(),
                max_abs_MW=flujo.abs().max(),max_exceso_MW=exceso.max())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('base',type=Path,help='Carpeta validacion_despacho_20261120')
    ap.add_argument('salida',type=Path)
    a=ap.parse_args()
    meses=[('octubre_2024','octubre_2024/horas.csv','octubre_2024/programado.csv'),
           ('enero_2025','validacion_verano/enero.csv.gz',None)]
    filas=[]
    for mes,fuente,programa in meses:
        tab=pd.read_csv(a.base/fuente,index_col='inicio_local',parse_dates=True)
        if programa:
            plan=pd.read_csv(a.base/programa,index_col='inicio_local',parse_dates=True)
            assert tab.index.equals(plan.index)
            tab['programado_MW']=plan.flujo_PCP_MW
        assert len(tab)==744 and tab.index.is_unique and np.isfinite(tab[['envio_MW','programado_MW']]).all().all()
        for serie in ['envio_MW','programado_MW']:
            for umbral in [1250,1950]:
                filas.append(dict(mes=mes,serie=serie,techo_MW=umbral,
                                  **indicadores(tab[serie],1,umbral)))
    pd.DataFrame(filas).to_csv(a.salida,index=False,float_format='%.6f')

if __name__=='__main__':
    main()
