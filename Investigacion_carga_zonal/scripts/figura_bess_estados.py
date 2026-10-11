from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S=Path(__file__).resolve().parents[1];q=S/'resultados/20261011_bess_conciliacion_v2';d=pd.read_csv(q/'conciliacion_enero.csv.gz');v=d[d.fecha.eq('2026-01-10')&d.hora0.eq(23)].iloc[0];e=pd.read_csv(q/'episodio_CerroNavia.csv');out=S/'figuras/20261011_bess_estados';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
f,ax=plt.subplots(1,2,figsize=(12,5));a=ax[0];values=[v.DonHumberto_MW,v.D_FB123,v.H1_neto];a.bar(['Serie API\n«PFV Don Humberto»','Batería física\nFB1 + FB2 + FB3','Conexión física\nH1 neto'],values,color=['#b76b25','#347dad','#344d47'],width=.65)
for i,x in enumerate(values):a.text(i,x+.8,f'{x:.2f}',ha='center',fontweight='bold')
a.set_ylim(0,53);a.set_ylabel('MW medios de la hora');a.set_title('10 de enero de 2026, 23:00–24:00\nTres registros que no se deben sumar',loc='left',fontsize=11)
a=ax[1];a.plot(e.hora0+.5,e.F_H4,'o-',label='Tránsito Las Canteras H4',color='#347dad',ms=4);a.plot(e.hora0+.5,e.R_TAP1,'--',label='Retiro Tap Libertadores H1',color='#b76b25',lw=2);a.axvspan(14+17/60,23+50/60,color='#808080',alpha=.13,label='Cerro Navia 52H3 abierto');a.set_xlim(0,24);a.set_xticks(range(0,25,4));a.set_ylabel('MW medios de la hora');a.set_xlabel('Hora local, 6 de marzo de 2025');a.set_title('El circuito mantiene una derivación intermedia\nH4 sigue abasteciendo Tap Libertadores',loc='left',fontsize=11);a.legend(fontsize=8,loc='upper left');a.grid(axis='y',alpha=.15)
f.suptitle('Conciliación de fronteras y estados eléctricos',fontsize=15,y=.98);f.text(.04,.02,'Fuentes: medidores definitivos CEN, API de operación y EAF108/2025 (p.114). Coincidencias físicas; no estimaciones causales.',fontsize=8,color='#444444');f.tight_layout(rect=(0,.06,1,.92));f.savefig(out/'conciliacion_bess_red.png',dpi=180);f.savefig(out/'conciliacion_bess_red.pdf');plt.close(f)
