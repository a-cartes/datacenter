"""Ejecutar desde anual_2024 con noviembre.csv generado por noviembre.py."""
from pathlib import Path

import pandas as pd
from scipy.stats import t

octubre = pd.read_csv(Path('../octubre_2024/horas.csv'))
noviembre = pd.read_csv('noviembre.csv')
assert len(octubre)==744 and len(noviembre)==720
anual = pd.read_csv('localizacion.csv').set_index('mes')
for mes, tabla in [(202410, octubre),(202411, noviembre)]:
    assert abs(tabla.brecha_USD_MWh.sum()-anual.loc[mes,'suma_brecha']) < 0.01
umbral = 3524280
positivo = octubre.brecha_USD_MWh.clip(lower=0).sum()
positivo_nov = noviembre.brecha_USD_MWh.clip(lower=0).sum()
print('Suma positiva por mes:',positivo,positivo_nov)
print('MW equivalentes octubre y acumulado:',umbral/positivo,umbral/(positivo+positivo_nov))
print('Diferencial de precio por flujo enviado:',(octubre.brecha_USD_MWh*octubre.envio_MW).sum())
print('Diferencia entre extremos valorada a precios horarios:',
      (octubre.LO_AGUIRRE____500*octubre.recepcion_MW-octubre.AJAHUEL_______500*octubre.envio_MW).sum())
print('Suma de brechas por régimen:',octubre.groupby('estado').brecha_USD_MWh.sum())
estratos = pd.read_csv('estratos.csv')
v = estratos.varianza_USD2
gl = v.sum()**2 / (v**2).sum()  # n_h=2, un grado de libertad dentro de cada estrato
nivel = estratos.total_USD.sum()
se = v.sum()**0.5
margen = t.ppf(0.975,gl)*se
print('Umbral / nivel; EE / umbral:',umbral/nivel,se/umbral)
print('Grados efectivos e intervalo aproximado del nivel:',gl,nivel-margen,nivel+margen)
