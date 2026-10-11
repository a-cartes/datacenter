"""Figura descriptiva y comparación de pendientes en muestras constantes."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S=Path(__file__).resolve().parents[1]
def main():
 out=S/'resultados/20261011_operacion_v1/figura_operacion.png'
 if out.exists():raise ValueError('No sobrescribir figura')
 h=pd.read_csv(S/'resultados/20261011_operacion_v1/perfil_hora.csv');a=pd.read_csv(S/'resultados/20261011_estimacion_operacion_v1/estimaciones.csv');b=pd.read_csv(S/'resultados/20261011_flujo500_v1/estimaciones.csv')
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
 fig,axes=plt.subplots(2,2,figsize=(12,8));ax=axes[0,0]
 ax.plot(h.hora0,h.MW,color='#176080',lw=2);ax.set(title='A. Carga Las Canteras HT1+HT2',xlabel='Hora local',ylabel='MW medios');ax.axvspan(9.5,16.5,color='#e4c769',alpha=.2);ax.set_xticks([0,6,12,18,23]);ax.set_ylim(0,6)
 ax=axes[0,1]
 for i in range(1,5):ax.plot(h.hora0,h[f'F_H{i}'],label=f'H{i}',lw=1.8)
 ax.axhline(0,color='grey',lw=.7);ax.axvspan(9.5,16.5,color='#e4c769',alpha=.2);ax.set(title='B. Tránsito local por canal',xlabel='Hora local',ylabel='MW medios con signo D−R');ax.set_xticks([0,6,12,18,23]);ax.legend(ncol=4,frameon=False)
 def forest(ax,data,models,labels,title):
  z=data[data.resultado.eq('zona_lejos5')&data.contraste.eq('solar')].set_index('modelo').loc[models]
  y=list(range(len(z)));ax.errorbar(z.beta,y,xerr=[z.beta-z.lo95,z.hi95-z.beta],fmt='o',color='#176080',capsize=4);ax.axvline(0,color='grey',ls='--',lw=1);ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_title(title,loc='left');ax.set_xlabel('(USD/MWh) por MW de Las Canteras');ax.set_xlim(-1,1.55)
 forest(axes[1,0],a,['fisica_base','fisica_google','fisica_google_flujos'],['Base','+ proxy Google','+ proxy Google\n+ flujos locales'],'C. Misma muestra: 18.168 horas, 2024–2026')
 forest(axes[1,1],b,['base_2026','google_2026','google_flujo500_2026'],['Base','+ proxy Google','+ proxy Google\n+ flujo AJ–LA'],'D. Misma muestra: 5.692 horas, 2026')
 fig.suptitle('Las Canteras: carga, tránsito y asociación diurna con precios',fontsize=15,y=.98)
 fig.text(.04,.02,'C–D: pendientes entre 10 y 16 h e intervalos del 95% (HAC semanal, 4 rezagos); FE día, mes×hora y hora de semana.\nDiferencial zonal frente a cinco controles distantes. Los flujos son posibles mediadores; estos ajustes no identifican causalidad.',fontsize=9)
 fig.tight_layout(rect=[0,.09,1,.95],w_pad=2.5,h_pad=2.8);fig.savefig(out,dpi=180);print(out)
if __name__=='__main__':main()
