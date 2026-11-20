"""Genera el gráfico desde horas.csv y programado.csv."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

p = Path(__file__).resolve().parent
h = pd.read_csv(p/"horas.csv").merge(pd.read_csv(p/"programado.csv"),on="inicio_local",validate="1:1")
fig, axes = plt.subplots(1,2,figsize=(10.4,4.2),layout="constrained")
for e, color, nombre in [("sin_marca","#59768c","Sin marca"),("transicion","#df922b","Transición"),("control","#933651","Control completo")]:
    s = h[h.estado.eq(e)]
    axes[0].scatter(s.envio_MW,s.brecha_USD_MWh,s=10,alpha=.65,c=color,label=nombre,linewidths=0)
    axes[1].scatter(s.envio_MW,s.flujo_PCP_MW,s=10,alpha=.65,c=color,linewidths=0)
axes[0].set(xlabel="Envío medido desde Alto Jahuel (MW)",ylabel="Lo Aguirre menos Alto Jahuel (USD/MWh)",title="Precio y control documentado")
axes[0].legend(fontsize=8,frameon=False)
axes[1].plot([-650,1800],[-650,1800],color="#353535",ls="--",lw=.8,label="Programado = medido")
axes[1].set(xlabel="Envío medido desde Alto Jahuel (MW)",ylabel="Flujo programado, mismo sentido (MW)",title="Programa diario y operación medida")
axes[1].legend(fontsize=8,frameon=False)
for ax in axes:
    ax.spines[["top","right"]].set_visible(False)
    ax.grid(alpha=.14)
fig.suptitle("Corredor Alto Jahuel–Lo Aguirre · Octubre de 2024",fontsize=14)
fig.savefig(p/"octubre.png",dpi=145)
