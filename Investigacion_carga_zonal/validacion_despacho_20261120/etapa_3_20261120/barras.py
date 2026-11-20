"""Audita la diferencia de costo de compra histórico entre las barras del estudio."""
import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

BARRAS={'A.JAHUEL______220':'BP1','A.JAHUEL2_____220':'BP2','LO_AGUIRRE____220':'LA'}

def salto(path,fecha):
    with ZipFile(path) as z:
        n,=[n for n in z.namelist() if 'promediosbarras' in n.lower() and n.lower().endswith('_r.csv')]
        d=pd.read_csv(z.open(n),encoding='latin1',sep=';')
    q=d[d.BARRA.isin(BARRAS) & d.HORA.eq(0)]
    col,=[c for c in q if c in ('CMg[mills/kWh]','CMg[USD/MWh]')]
    assert q.FECHA.eq(fecha).all() and q.INTERVALO.eq(15).all()
    p=q.pivot(index='MINUTO',columns='BARRA',values=col)
    assert sorted(p.columns)==sorted(BARRAS) and list(p.index)==[0,15,30,45] and p.eq(0).all().all()

def main():
    a=argparse.ArgumentParser()
    for k in ['panel','septiembre24','septiembre25','salida']:
        a.add_argument(k,type=Path)
    args=a.parse_args()
    salto(args.septiembre24,20240908)
    salto(args.septiembre25,20250907)
    d=pd.read_parquet(args.panel)
    d=d[d.anio.isin([2024,2025]) & d.barra.isin(BARRAS)]
    assert d.horas_P.eq(d.horas_filas).all() and d.sum_P.notna().all()
    p=d.groupby(['mes','barra'])[['sum_P','horas_P']].sum().unstack()
    assert len(p)==24 and p.horas_P.nunique(axis=1).eq(1).all()
    out=pd.DataFrame(index=p.index)
    out['horas_fisicas']=[((s+pd.DateOffset(months=1))-s)/pd.Timedelta(hours=1)
                          for s in (pd.Timestamp(str(m)+'01',tz='America/Santiago') for m in p.index)]
    desvio=p.horas_P.iloc[:,0]-out.horas_fisicas
    assert desvio[desvio.ne(0)].to_dict()=={202409:1,202509:1}
    precio=p.sum_P.rename(columns=BARRAS)
    for barra in ('BP1','BP2'):
        diff=precio.LA-precio[barra]
        out[f'brecha_{barra}_USD_MWh']=diff/out.horas_fisicas
        out[f'compras_50MW_{barra}_USD']=50*diff
    out.to_csv(args.salida,float_format='%.8f')
    print('SHA-256 de los insumos:')
    for path in (args.panel,args.septiembre24,args.septiembre25):
        print(hashlib.sha256(path.read_bytes()).hexdigest())
if __name__=='__main__':
    main()
