"""Figura derivada de ejecuciones archivadas; no sobrescribe."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/codex_mpl_carga_zonal')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/codex_cache_carga_zonal')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import pandas as pd
import numpy as np
S=Path(__file__).resolve().parents[1];out=S/'figuras/20261011_controles_zonales'
if out.exists():raise SystemExit('Conservar figura existente')
out.mkdir(parents=True)
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,1,figsize=(11.5,8.5));colors=['#256e89','#b96520']
for run,label,color in zip(['20261011_controles_externos_v1','20261011_controles_distantes_v1'],['Fuera del corredor directo (5 controles)','Fuera de RM y del componente 110 kV (5 controles)'],colors):
 p=S/'resultados'/run;h=pd.read_csv(p/'contraste_historico_mensual.csv');h=h[h.K.eq(5)].copy();h['fecha']=pd.to_datetime(h.mes);adj=h[h.mes.between('2022-05','2023-04')].brecha.mean()
 axes[0].plot(h.fecha,h.brecha-adj,label=label,color=color,lw=1.8)
 m=pd.read_csv(p/'panel_mensual_comun.csv');x=m.MW;y=m.brecha_zona_K5
 axes[1].scatter(x,y-y.mean(),color=color,alpha=.65,s=25)
 b=np.polyfit(x,y-y.mean(),1);xx=np.linspace(x.min(),x.max(),100);axes[1].plot(xx,np.polyval(b,xx),color=color,label=f'{label}: pendiente {b[0]:+.3f}')
axes[0].axvline(pd.Timestamp('2024-05-29'),color='#333333',ls='--',lw=1);axes[0].axvspan(pd.Timestamp('2022-05-01'),pd.Timestamp('2023-04-30'),color='#dddddd',alpha=.35);axes[0].axhline(0,color='gray',lw=.6)
axes[0].set_title('A. La comparación distante se separa antes de la expansión',loc='left',fontweight='bold');axes[0].set_ylabel('Brecha zona − controles\nUSD/MWh, centrada en entrenamiento');axes[0].xaxis.set_major_formatter(md.DateFormatter('%m/%Y'));axes[0].legend(frameon=False,fontsize=9,loc='upper left');axes[0].grid(alpha=.18)
axes[1].axhline(0,color='gray',lw=.6);axes[1].set_title('B. La asociación con carga depende de la zona de comparación',loc='left',fontweight='bold');axes[1].set_xlabel('Retiro físico medio Las Canteras HT1+HT2 (MW)');axes[1].set_ylabel('Brecha zona − controles\nUSD/MWh, centrada en su media');axes[1].legend(frameon=False,fontsize=9);axes[1].grid(alpha=.18)
fig.suptitle('Las Canteras: consumo medido y comparadores externos',fontsize=17,fontweight='bold',x=.07,ha='left')
fig.text(.07,.025,'Zona fija: Batuco 110, Libertadores 110 y Cerro Navia 110. B: agosto 2024–agosto 2026, 25 meses.\nComparaciones descriptivas; las pendientes no identifican por sí solas un efecto causal.',fontsize=10,color='#444444')
fig.tight_layout(rect=(0,.075,1,.95),h_pad=2);fig.savefig(out/'controles_y_carga.png',dpi=160);fig.savefig(out/'controles_y_carga.pdf');plt.close(fig)
