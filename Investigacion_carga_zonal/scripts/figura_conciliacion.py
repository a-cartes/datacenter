"""Figura descriptiva desde resultados guardados; no estima coeficientes."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/codex_mpl_carga_zonal')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
S=Path(__file__).resolve().parents[1]
A=S/'resultados/20261011_conciliacion_v1'
B=S/'resultados/20261011_diagnosticos_adicionales_v1'
out=S/'figuras/20261011_conciliacion'
if out.exists():raise SystemExit('La figura ya tiene una versión guardada')
out.mkdir(parents=True)
a=pd.read_csv(A/'carga_mensual_dias_24h.csv'); b=pd.read_csv(B/'comparacion_corredor_mensual.csv')
fig,axes=plt.subplots(3,1,figsize=(10,10),layout='constrained')
colors=['#126782','#E07A32','#7254A3']
for case,label,color in zip(['Canteras_HT12_D','ST01_J9_D','ST02_CT12_D'],['Las Canteras: HT1+HT2, D','ODATA ST01: J9, D','ODATA ST02: CT1+CT2, D'],colors):
 x=a[a.frontera.eq(case)].copy();idx=pd.period_range(x.mes.min(),x.mes.max(),freq='M').astype(str);x=x.set_index('mes').reindex(idx)
 axes[0].plot(pd.to_datetime(x.index),x.MW_medio,label=label,color=color,marker='o',markersize=3)
axes[0].set_title('A. La carga observada crece por etapas',loc='left',fontweight='bold');axes[0].set_ylabel('MW medios observados');axes[0].legend(fontsize=9,loc='upper left');axes[0].set_ylim(bottom=-.2)
axes[1].plot(pd.to_datetime(b.mes),b.D_canteras,label='Las Canteras - Quillota 220',color=colors[0],marker='o',markersize=3)
axes[1].plot(pd.to_datetime(b.mes),b.D_corredor,label='Corredor vecino - Quillota 220',color='#E07A32',linestyle='--',marker='s',markersize=3)
axes[1].set_title('B. El diferencial de precio se mueve junto con el corredor',loc='left',fontweight='bold');axes[1].set_ylabel('USD/MWh');axes[1].legend(fontsize=9,loc='upper left')
axes[2].plot(pd.to_datetime(b.mes),b.brecha_canteras_corredor,color='#52525B',marker='o',markersize=3)
axes[2].axhline(0,color='gray',linewidth=.8)
axes[2].set_title('C. Brecha Las Canteras - promedio del corredor vecino',loc='left',fontweight='bold');axes[2].set_ylabel('USD/MWh')
for ax in axes:
 ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.18);ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4));ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'));ax.tick_params(axis='x',rotation=0)
fig.suptitle('Consumo medido y precios zonales | corte agosto de 2026',fontsize=15,fontweight='bold')
fig.supxlabel('Medias en días completos de 24 h. Corredor: Batuco 110, Tap Libertadores 110 y Cerro Navia 110.\nFronteras parciales y proxies documentados; comparación descriptiva, sin atribución causal.',fontsize=9)
fig.savefig(out/'carga_y_precios_zonales.png',dpi=170)
plt.close(fig)
