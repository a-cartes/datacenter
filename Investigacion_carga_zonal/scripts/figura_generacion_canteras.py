from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S=Path(__file__).resolve().parents[1];out=S/'figuras/20261011_generacion_auditada';out.mkdir();p=S/'resultados/20261011_generacion_v3';h=pd.read_csv(p/'perfil_horario.csv');r=pd.read_csv(S/'resultados/20261011_calidad_generacion_v1/estimaciones.csv');e=pd.read_csv(p/'episodios.csv')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(2,2,figsize=(13,9),layout='constrained')
a=axs[0,0]
for col,lab,colr in [('SantiagoSolar_MW','Santiago Solar','#d98c00'),('DonHumberto_MW','Don Humberto (rótulo API PFV)' ,'#25857b')]:a.plot(h.hora0,h[col],label=lab,color=colr,lw=2)
a.set(title='Generación reportada: anomalía nocturna en Don Humberto',ylabel='MW',xlabel='Hora local');a.legend(frameon=False);a.axvspan(10,17,color='#efc871',alpha=.12)
a=axs[0,1];a.plot(h.hora0,h.MW,color='#244971',lw=2);a.set(title='Carga media de Las Canteras (HT1+HT2)',ylabel='MW',xlabel='Hora local',ylim=(0,6));a.axvspan(10,17,color='#efc871',alpha=.12)
a=axs[1,0];labs=['completa_base','completa_Santiago','umbral0.1_base','umbral0.1_Santiago'];names=['Muestra completa: base','Completa: + Santiago Solar','Sin días marcados: base','Sin días marcados: + Santiago']
z=r[r.resultado.eq('zona_lejos5')&r.contraste.eq('solar')].set_index('modelo').loc[labs];idx=np.arange(len(z));a.errorbar(z.beta,idx,xerr=np.array([z.beta-z.lo95,z.hi95-z.beta]),fmt='o',color='#244971',capsize=4);a.set_yticks(idx,names);a.invert_yaxis();a.axvline(0,color='gray',lw=1);a.set(title='Asociación diurna: comparación distante',xlabel='(USD/MWh) por MW de Las Canteras; IC95%')
a=axs[1,1];z=e[e.fecha.eq('2025-01-22')]
a.plot(z.hora0,z.F_H1,label='H1, D−R',lw=2);a.plot(z.hora0,z.F_H2,label='H2, D−R',lw=2);a.plot(z.hora0,z.PV_total_MW,label='Suma generación solar',lw=2,color='#d98c00');a.axvspan(12.9,17.8667,color='gray',alpha=.18,label='Restricción documentada');a.set(title='22 enero 2025: tránsito y generación',ylabel='MW; signo de flujo según medidor',xlabel='Hora local');a.legend(frameon=False,fontsize=8)
fig.suptitle('Las Canteras: generación vecina, carga y maniobras de red',fontsize=16)
fig.get_layout_engine().set(rect=(0,.055,1,.95));fig.text(.02,.01,'756 días completos; 658 al excluir días con generación nocturna anómala. Asociaciones condicionales.\nFuentes: CEN, mediciones v7, API generación real y EAF039/2025. Errores semanales HAC4.',fontsize=9,color='#444444')
fig.savefig(out/'generacion_y_carga.png',dpi=180);plt.close(fig)
