"""Figura del diferencial de compra entre Lo Aguirre y dos barras de Alto Jahuel."""
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import pandas as pd

d=pd.read_csv('mensual.csv')
d['fecha']=pd.to_datetime(d.mes.astype(str),format='%Y%m')
fig,ax=plt.subplots(figsize=(8.0,3.6),layout='constrained')
ax.axhline(0,color='#616161',lw=.8)
ax.axvline(pd.Timestamp('2024-12-16'),color='#bbb',lw=.7,ls=':')
for col,color,marker in [('BP1','#00658b','o'),('BP2','#aa4e0a','s')]:
    ax.plot(d.fecha,d[f'brecha_{col}_USD_MWh'],label=f'Alto Jahuel {col}',color=color,
            marker=marker,ms=3.6,lw=1.6,linestyle='-' if col=='BP1' else '--')
ticks=d.fecha.iloc[::3]
ax.set_xticks(ticks,[['ene','abr','jul','oct'][i%4]+' '+str(t.year) for i,t in enumerate(ticks)],fontsize=8)
ax.set_ylabel('Lo Aguirre menos Alto Jahuel (USD/MWh)',fontsize=9)
ax.yaxis.set_major_locator(MultipleLocator(2))
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='y',alpha=.14)
ax.legend(loc='upper right',ncol=2,frameon=False,fontsize=8)
for fmt in ['png','pdf']:
    fig.savefig(f'brecha_por_barra.{fmt}',dpi=180,bbox_inches='tight')
