"""Recupera las brechas horarias de las dos barras a partir de los archivos diarios definitivos."""
import csv
import hashlib
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile
import pandas as pd

def dia(d):
    mes_publicacion = '11' if d <= 21 else '12'
    url=f'https://www.coordinador.cl/wp-content/uploads/2024/{mes_publicacion}/Antecedentes_CMG_Real_def_2411{d:02}.zip'
    path=Path(f'{d:02}.zip')
    if not path.exists():
        with urlopen(url,timeout=30) as r:
            b=r.read()
        with ZipFile(io.BytesIO(b)) as z:
            assert z.namelist()
        path.write_bytes(b)
    with ZipFile(path) as z:
        n,=[n for n in z.namelist() if 'promediosbarras' in n.lower() and n.lower().endswith('_r.csv')]
        p=pd.read_csv(z.open(n),sep=';',encoding='latin1')
    barras=['AJAHUEL_______500','LO_AGUIRRE____500']
    p=p[p.BARRA.isin(barras)]
    assert p.FECHA.eq(20241100+d).all() and p.INTERVALO.eq(15).all()
    col,=[c for c in p if c in ['CMg[mills/kWh]','CMg[USD/MWh]']]
    q=p.pivot(index=['HORA','MINUTO'],columns='BARRA',values=col)
    assert len(q)==96 and q.notna().all().all()
    h=(q[barras[1]]-q[barras[0]]).groupby(level=0).mean()
    return (d,url,hashlib.sha256(path.read_bytes()).hexdigest(),h)
if __name__=='__main__':
    with ThreadPoolExecutor(8) as pool:
        datos=list(pool.map(dia,range(1,31)))
    with open('noviembre.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['dia','hora','brecha_USD_MWh','url','sha256'])
        for d,url,sha,h in datos:
            w.writerows((d,k,v,url,sha) for k,v in h.items())
