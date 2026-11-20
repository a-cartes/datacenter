"""Estimador de total estratificado y error estándar de diseño."""
import numpy as np
import pandas as pd
d = pd.read_csv('programas.csv',parse_dates=['fecha'])
assert len(d)==d.fecha.nunique()==96 and d.kUSD_dia.notna().all()
d['mes'] = d.fecha.dt.month
filas = []
for (mes,k),g in d.groupby(['mes','estrato']):
    N = g.dias_estrato.iloc[0]
    assert len(g)==2 and g.dias_estrato.eq(N).all() and g.peso.eq(N/2).all()
    costos = 1000*g.kUSD_dia
    filas.append(dict(mes=mes,estrato=k,dias=N,total_USD=N*costos.mean(),
                      varianza_USD2=N**2*(1-2/N)*costos.var(ddof=1)/2))
s = pd.DataFrame(filas)
assert len(s)==48 and s.dias.sum()==366
s.to_csv('estratos.csv',index=False)
print('Total y error estándar, USD:', s.total_USD.sum(),np.sqrt(s.varianza_USD2.sum()))
