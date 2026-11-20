"""Extrae costos diarios publicados del programa base por fecha muestral."""
import csv
import datetime as dt
import hashlib
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import openpyxl

def obtener(r):
    dia = dt.date.fromisoformat(r['fecha'])
    nombre = f'PROGRAMA{dia:%Y%m%d}.zip'
    if r['fecha']=='2024-06-12':
        nombre=nombre.replace('.zip','-1.zip')
    url = f'https://www.coordinador.cl/wp-content/uploads/{dia-dt.timedelta(days=1):%Y/%m}/{nombre}'
    try:
        cache = Path('cache') / nombre
        if not cache.exists():
            with urlopen(url, timeout=28) as resp:
                contenido = resp.read()
            with ZipFile(io.BytesIO(contenido)) as z:
                assert z.namelist()
            cache.write_bytes(contenido)
        with ZipFile(cache) as z:
            n, = [n for n in z.namelist() if Path(n).name.upper().startswith('PRG') and n.lower().endswith('.xlsx')]
            libro = openpyxl.load_workbook(io.BytesIO(z.read(n)),read_only=True,data_only=True)
            filas = iter(libro['PROGRAMA'].values)
            fecha_validada=False
            for fila in filas:
                if fila[2] == 'Costos Totales [kUSD]':
                    assert fecha_validada
                    costos = [float(v) for v in fila[4:28]]
                    assert abs(sum(costos)-float(fila[28])) < 0.05
                    break
                if isinstance(fila[2],dt.datetime):
                    assert fila[2].date()==dia and list(fila[4:28])==list(range(1,25))
                    fecha_validada=True
            else:
                raise ValueError('Falta fila costos')
        return dict(**r,url=url,sha256=hashlib.sha256(cache.read_bytes()).hexdigest(),kUSD_dia=sum(costos))
    except Exception as exc:
        print(dia,type(exc).__name__,str(exc)[:120],flush=True)
        return dict(**r,url=url,sha256='',kUSD_dia='')
if __name__=='__main__':
    Path('cache').mkdir(exist_ok=True)
    with open('muestra.csv') as archivo:
        muestra=list(csv.DictReader(archivo))
    with ThreadPoolExecutor(6) as pool:
        datos=list(pool.map(obtener,muestra))
    with open('programas.csv','w',newline='') as archivo:
        salida=csv.DictWriter(archivo,fieldnames=list(datos[0]))
        salida.writeheader()
        salida.writerows(datos)
