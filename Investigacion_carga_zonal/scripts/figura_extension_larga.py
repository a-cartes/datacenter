from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S=Path(__file__).resolve().parents[1];out=S/'figuras/20261011_extension_larga';out.mkdir(exist_ok=True);plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
d=pd.read_csv(S/'resultados/20261011_variaciones_carga/carga_diaria.csv');d['fecha']=pd.to_datetime(d.fecha);r=pd.read_csv(S/'resultados/20261011_estimacion_larga_v1/estimaciones.csv');r=r[r.resultado.eq('zona_lejos5')&r.contraste.eq('solar')].set_index('modelo')
f,ax=plt.subplots(2,1,figsize=(11,8),gridspec_kw={'height_ratios':[1.4,1]});a=ax[0];a.plot(d.fecha,d.MW,color='#285b7e',lw=1.2,label='HT1 + HT2, mediana diaria');a.set_ylabel('MW');a.set_title('Cambios de carga detectados sin utilizar precios',loc='left');a.legend(loc='upper left',bbox_to_anchor=(0,.9));a.grid(axis='y',alpha=.2)
for day,label in [('2024-08-08','8 ago 2024'),('2025-12-19','19 dic 2025'),('2026-05-15','15 may 2026')]:a.axvline(pd.Timestamp(day),color='#aa793a',ls=':',alpha=.8);a.text(pd.Timestamp(day),10.2,label,ha='center',fontsize=8)
a.set_ylim(0,11)
models=['largo_BESS_H1','antes_dic2025_BESS_H1','dic2025_feb2026_BESS_H1','desde_mar2026_BESS_H1'];labels=['Período largo común (696 días)','Antes de dic 2025 (424 días)','Dic 2025–feb 2026 (90 días)','Desde mar 2026 (182 días)'];a=ax[1]
for i,(m,label) in enumerate(zip(models,labels)):
 x=r.loc[m];a.errorbar(x.beta,i,xerr=[[x.beta-x.lo95],[x.hi95-x.beta]],fmt='o',color='#285b7e' if i!=2 else '#aa793a',capsize=4);a.text(5.5,i,f'{x.beta:.2f}',va='center',fontsize=9)
a.set_yticks(range(4),labels);a.invert_yaxis();a.axvline(0,color='gray',ls='--',lw=1);a.set_xlabel('Pendiente diurna (USD/MWh por MW), con controles físicos e intervalo aproximado 95%');a.set_title('La pendiente de los 90 días no representa todo el período',loc='left');f.tight_layout(rect=(0,.055,1,.98));f.text(.04,.012,'CEN: mediciones físicas y precios. Asociaciones condicionadas; los efectos fijos de día absorben diferencias entre niveles diarios.',fontsize=8);f.savefig(out/'extension_y_ventanas.png',dpi=170);f.savefig(out/'extension_y_ventanas.pdf');plt.close(f)
e=pd.read_csv(S/'resultados/20261011_diagnostico_variaciones_v1/episodio_documentado.csv');f,ax=plt.subplots(2,1,figsize=(10,7),sharex=True)
for col,label,color in [('MW','HT1 + HT2','#285b7e'),('D_HT1','HT1','#b56d2c'),('D_HT2','HT2','#487950')]:ax[0].plot(e.hora0+.5,e[col],'-o',label=label,color=color,ms=3)
ax[0].set_ylabel('MW medios horarios');ax[0].legend(ncol=3,loc='upper right');ax[0].set_title('3 de diciembre de 2024: consumo y normalización no coinciden',loc='left');ax[1].plot(e.hora0+.5,e.CANTERAS_110,label='Precio Las Canteras',color='#285b7e');ax[1].plot(e.hora0+.5,e.Q,label='Precio Quillota',color='#b56d2c',ls='--');ax[1].set_ylabel('USD/MWh');ax[1].legend(loc='upper right')
for a in ax:a.axvspan(5.6,21+19/60,color='gray',alpha=.15);a.axvline(16.75,color='#487950',ls=':',lw=1);a.set_xlim(0,24);a.grid(axis='y',alpha=.2)
ax[1].set_xticks(range(0,25,2));ax[1].set_xlabel('Hora local (puntos al centro de cada intervalo)');f.tight_layout(rect=(0,.075,1,1));f.text(.055,.02,'Gris: barra 23 kV fuera según EAF563. Línea vertical: desconexión de transformador 16:45.\nLa recuperación agregada se observa por HT2 antes de normalizar HT1 a las 21:19; es una conciliación, no un efecto causal.',fontsize=8);f.savefig(out/'episodio_20241203.png',dpi=170);f.savefig(out/'episodio_20241203.pdf');plt.close(f)
