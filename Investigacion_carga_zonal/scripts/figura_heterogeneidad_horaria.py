from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/codex_mpl_carga_zonal');os.environ.setdefault('XDG_CACHE_HOME','/tmp/codex_cache_carga_zonal')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
S=Path(__file__).resolve().parents[1];out=S/'figuras/20261011_horas'
if out.exists():raise SystemExit('No sobrescribir figura')
out.mkdir(parents=True)
r=pd.read_csv(S/'resultados/20261011_horas_v1/estimaciones_principales.csv');r=r[(r.FE=='B_dia_meshora_horasemana')&(r.resultado=='zona_lejos5')&(r.modelo=='bloques')].set_index('contraste').loc[['solar','tarde','resto']]
a=pd.read_csv(S/'resultados/20261011_episodios_horarios_v1/descomposicion_pendiente_mensual.csv');a=a[a.resultado.eq('zona_lejos5')].set_index('bloque').loc[['solar_10_16','tarde_19_23','resto','TOTAL']]
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(1,2,figsize=(12,5.6),gridspec_kw={'width_ratios':[1,1.35]});colors=['#c68124','#35658d','#687d78','#202e3a']
labels=['10–16 h','19–23 h','Resto','Promedio mensual']
ax[0].barh(labels,a.contribucion_beta_agregada,color=colors);ax[0].invert_yaxis();ax[0].axvline(0,color='gray',lw=.8)
for i,v in enumerate(a.contribucion_beta_agregada):ax[0].text(v+.002,i,f'{v:+.4f}',va='center',fontsize=10)
ax[0].set_xlim(-.014,.115);ax[0].set_title('A. Qué compone la pendiente mensual',loc='left',fontweight='bold');ax[0].set_xlabel('Contribución a USD/MWh por MW')
for i,(_,row) in enumerate(r.iterrows()):ax[1].errorbar(row.beta,i,xerr=[[row.beta-row.lo95],[row.hi95-row.beta]],fmt='o',color=colors[i],capsize=5,ms=7)
ax[1].set_yticks(range(3),['10–16 h','19–23 h','Resto']);ax[1].invert_yaxis();ax[1].axvline(0,color='gray',ls='--');ax[1].set_title('B. Asociación dentro del mismo día',loc='left',fontweight='bold');ax[1].set_xlabel('USD/MWh por MW; intervalo condicional 95%');ax[1].grid(axis='x',alpha=.2)
fig.suptitle('Las Canteras: una señal diurna, todavía imprecisa',fontsize=17,fontweight='bold',x=.03,ha='left')
fig.text(.03,.06,'Zona frente a cinco comparadores distantes. Agosto 2024–agosto 2026: 18.168 horas, 757 días.\nA: descomposición aritmética de 25 medias mensuales. B: efectos fijos de día y perfiles horarios; HAC semanal.\nLas dos partes miden relaciones distintas. Ninguna identifica por sí sola un efecto causal.',fontsize=10,color='#444444')
fig.tight_layout(rect=(0,.18,1,.90),w_pad=3);fig.savefig(out/'senal_horaria.png',dpi=160);fig.savefig(out/'senal_horaria.pdf');plt.close(fig)
