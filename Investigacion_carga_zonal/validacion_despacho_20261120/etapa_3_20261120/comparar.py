"""Compara los precios de barra del programa PLEXOS con costo marginal realizado."""
import argparse
import hashlib
import io
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
import openpyxl

NODOS = {'AJahuel500': 'AJ', 'LoAguirre500': 'LA', 'Quillota220': 'Quillota_PLEXOS',
         'AJahuel220': 'AJ220_PCP', 'LoAguirre220': 'LA220_PCP'}
PROPIEDADES_LINEA = {'Flow': 'flujo_original_MW', 'Hours Congested': 'congestion',
                     'Rental': 'renta_modelo', 'Loss': 'perdida_modelo_MW'}

def interno(z, sufijo):
    n, = [n for n in z.namelist() if n.endswith(sufijo)]
    return ZipFile(io.BytesIO(z.read(n)))

def horas(ruta, dia):
    with ZipFile(ruta) as z, interno(z, f'RES202410{dia:02}.zip') as res, interno(res,'Solution.zip') as sol:
        n, = [n for n in sol.namelist() if n.endswith('Solution.xml')]
        root = ET.fromstring(sol.read(n))
        b = sol.read('t_data_0.BIN')
    def filas(nombre):
        return [{c.tag.split('}')[-1]: c.text for c in f} for f in root.findall('{*}t_'+nombre)]
    def indice(nombre, clave):
        return {f[clave]: f for f in filas(nombre)}
    obj=indice('object','object_id')
    prop=indice('property','property_id')
    mem=indice('membership','membership_id')
    key=indice('key_index','key_id')
    unidad=indice('unit','unit_id')
    calendario=indice('period_0','interval_id')
    fase=sorted(filas('phase_3'),key=lambda f:int(f['period_id']))[:24]
    idx=pd.to_datetime([calendario[f['interval_id']]['datetime'] for f in fase],dayfirst=True)
    assert idx.equals(pd.date_range(pd.Timestamp(2024,10,dia),periods=24,freq='h'))
    out=pd.DataFrame(index=idx)
    for k in filas('key'):
        if k['phase_id']!='3' or k['period_type_id']!='0':
            continue
        m=mem[k['membership_id']]
        if obj[m['parent_object_id']]['name']!='SEN':
            continue
        nombre=obj[m['child_object_id']]['name']
        pr=prop[k['property_id']]
        if nombre in NODOS and pr['name']=='Price':
            col=NODOS[nombre]
            assert unidad[pr['unit_id']]['value']=='$/MWh'
        elif nombre=='LoAguirre500->AJahuel500' and pr['name'] in PROPIEDADES_LINEA:
            col=PROPIEDADES_LINEA[pr['name']]
        else:
            continue
        ix=key[k['key_id']]
        assert int(ix['period_offset'])==0 and int(ix['length'])>=24 and col not in out
        out[col]=np.frombuffer(b,dtype='<f8',count=24,offset=int(ix['position']))
    assert len(out.columns)==9
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument('pcp',type=Path)
    p.add_argument('octubre',type=Path)
    p.add_argument('prg',type=Path)
    p.add_argument('cmg',type=Path)
    p.add_argument('salida',type=Path)
    a=p.parse_args()
    files=pd.read_csv(a.octubre/'fuentes_pcp.csv')
    dias=[]
    for r in files.itertuples():
        path=a.pcp/f'{r.dia:02}.zip'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==r.sha256
        dias.append(horas(path,r.dia))
    x=pd.concat(dias)
    x.index.name='inicio_local'
    real=pd.read_csv(a.octubre/'horas.csv',parse_dates=['inicio_local']).set_index('inicio_local')
    pcp=pd.read_csv(a.octubre/'programado.csv',parse_dates=['inicio_local']).set_index('inicio_local')
    assert len(x)==744 and x.index.equals(real.index) and x.index.equals(pcp.index)
    np.testing.assert_allclose(-x.flujo_original_MW,pcp.flujo_PCP_MW,atol=1e-6)
    np.testing.assert_array_equal(x.congestion,pcp.congestion_PCP)
    x=x.join(real[['brecha_USD_MWh','estado']])
    referencia=[]
    for r in pd.read_csv(a.octubre/'fuentes_prg.csv').itertuples():
        path=a.prg/f'{r.dia:02}.zip'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==r.sha256
        with ZipFile(path) as z:
            n,=[n for n in z.namelist() if Path(n).name.upper().startswith('PRG') and n.lower().endswith('.xlsx')]
            libro=openpyxl.load_workbook(io.BytesIO(z.read(n)),read_only=True,data_only=True)
            filas=iter(libro['PROGRAMA'].values)
            for _ in range(3):
                next(filas)
            cabecera=next(filas)
            assert cabecera[2].date()==pd.Timestamp(2024,10,r.dia).date()
            assert list(cabecera[4:28])==list(range(1,25))
            fila=next(f for f in filas if f[2]=='Costo Marginal Quillota 220 kV')
            referencia.extend(float(v) for v in fila[4:28])
    x['Quillota_PRG']=referencia
    reales=[]
    codigos={'A.JAHUEL______220':'AJ220_BP1','A.JAHUEL2_____220':'AJ220_BP2',
             'LO_AGUIRRE____220':'LA220_real'}
    for r in pd.read_csv(a.octubre/'fuentes_cmg.csv').itertuples():
        path=a.cmg/f'{r.dia:02}.zip'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==r.sha256
        with ZipFile(path) as z:
            n,=[n for n in z.namelist() if 'promediosbarras' in n.lower() and n.lower().endswith('_r.csv')]
            d=pd.read_csv(z.open(n),sep=';',encoding='latin1')
        d=d[d.BARRA.isin(codigos)]
        assert d.FECHA.eq(20241000+r.dia).all() and d.INTERVALO.eq(15).all()
        q=d.pivot(index=['HORA','MINUTO'],columns='BARRA',values='CMg[USD/MWh]').rename(columns=codigos)
        assert q.index.equals(pd.MultiIndex.from_product([range(24),range(0,60,15)]))
        assert len(q.columns)==3 and np.isfinite(q).all().all()
        h=q.groupby(level=0).mean()
        h.index=pd.date_range(pd.Timestamp(2024,10,r.dia),periods=24,freq='h')
        reales.append(h)
    precios=pd.concat(reales)
    assert x.index.equals(precios.index)
    x=x.join(precios)
    x['brecha_PCP']=x.LA-x.AJ
    x['brecha_220_programada']=x.LA220_PCP-x.AJ220_PCP
    x['brecha_220_real']=x.LA220_real-x.AJ220_BP1
    x.to_csv(a.salida,float_format='%.8f')
if __name__=='__main__':
    main()
