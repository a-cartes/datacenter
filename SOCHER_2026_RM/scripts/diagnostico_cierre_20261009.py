from pathlib import Path
import pandas as pd, numpy as np, json, hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]; O=R/'resultados/cierre_socher_20261009'; O.mkdir(exist_ok=True)
S=pd.read_csv(R/'resultados/socher_20261005/muestra_principal.csv').drop_duplicates(['unidad','anio'])
A=pd.read_parquet(R/'datos/panel/barra_anio.parquet'); M=pd.read_parquet(R/'datos/panel/barra_mes.parquet')
B=pd.read_csv(R/'datos/geo/barras_diccionario.csv').merge(pd.read_csv(R/'datos/geo/subestaciones_unidades.csv')[['id_subestacion','distrito_nombre']],on='id_subestacion',validate='many_to_one')
b=A[A.cobertura_D>=.9].merge(B[['barra','distrito_nombre','nivel_kv_codigo','subestacion']],on='barra',validate='many_to_one')
b=b[b.distrito_nombre.isin(S.unidad.unique())]
re=b.groupby(['distrito_nombre','anio']).D.mean().reset_index().merge(S,left_on=['distrito_nombre','anio'],right_on=['unidad','anio'],suffixes=('_r',''))
assert len(re)==len(S) and np.max(abs(re.D_r-re.D))<1e-8
controls=S[S.G==0].unidad.unique(); grp=S[S.G==0].groupby('anio')[['D','L','C','P','E']].mean()
co=[]
for unit in S[S.G>0].unidad.unique():
 z=S[S.unidad==unit].set_index('anio'); g=int(z.G.iloc[0]); rr=z.D-grp.D
 co.append(dict(unidad=unit,G=g,n_post=sum(z.index>=g),ultimo_pre=rr[g-1],promedio_pre=rr[rr.index<g].mean(),promedio_post=rr[rr.index>=g].mean(),ATT=rr[rr.index>=g].mean()-rr[g-1],contraste_pre_completo=rr[rr.index>=g].mean()-rr[rr.index<g].mean()))
co=pd.DataFrame(co); co.to_csv(O/'contrastes_cohortes.csv',index=False)
# Annual accounting by Lampa and control average; exact L+C only years with complete factors.
l=S[S.unidad=='LAMPA-4'].set_index('anio')[['D','L','C','P','E']]
ann=pd.concat({'Lampa':l,'Controles':grp},names=['grupo','anio']).reset_index(); ann.to_csv(O/'series_grupos_anuales.csv',index=False)
y=S[S.unidad.isin(controls)&S.anio.isin([2020,2021])].pivot(index='unidad',columns='anio',values=['D','L','C','P'])
delc=pd.DataFrame({k:y[k][2021]-y[k][2020] for k in ['D','L','C','P']}); delc['aporte_cambio_D']=delc.D/len(controls); delc.sort_values('D',ascending=False).to_csv(O/'cambios_controles_2020_2021.csv')
b[b.anio.isin([2020,2021])].to_csv(O/'barras_2020_2021.csv',index=False)
# Monthly means weighted in each year by observed hours, consistent with annual input.
keys=b[['barra','anio','distrito_nombre']]; m=M.merge(keys,on=['barra','anio'],validate='many_to_one')
m=m.groupby(['barra','distrito_nombre','mes'],as_index=False)[['sum_D','sum_L','sum_C','sum_P','sum_E','horas_D','horas_LC']].sum()
for v in ['D','P','E']: m[v]=m['sum_'+v]/m.horas_D
for v in ['L','C']: m[v]=m['sum_'+v]/m.horas_LC.replace(0,np.nan)
mo=m.groupby(['distrito_nombre','mes'])[['D','L','C','P','E']].mean().reset_index()
mo['grupo']=np.where(mo.distrito_nombre=='LAMPA-4','Lampa',np.where(mo.distrito_nombre.isin(controls),'Controles','Otros tratados'))
mg=mo[mo.grupo!='Otros tratados'].groupby(['grupo','mes'])[['D','L','C','P','E']].mean().reset_index(); mg.to_csv(O/'series_grupos_mensuales.csv',index=False)
# Matched control composition check and simple, noncausal voltage breakdown.
b['grupo']=np.where(b.distrito_nombre=='LAMPA-4','Lampa',np.where(b.distrito_nombre.isin(controls),'Controles','Otros tratados'))
b[b.anio.isin([2020,2021])].groupby(['grupo','anio','nivel_kv_codigo']).agg(n_barras=('barra','nunique'),D=('D','mean'),L=('L','mean'),C=('C','mean')).to_csv(O/'diagnostico_tension.csv')
# Geography to forecasting-connection mapping, preserve absent voltage matches.
f=pd.read_csv(R/'prospectiva_2030/extraidos/demanda_digital/clientes_digitales_cne_anual.csv')
f=f[(f.anio==2025)&f.clase.eq('operador_centro_datos')].copy(); f['naturaleza']='Base de previsión CNE; no usar como retiro histórico observado'
f.to_csv(O/'conexiones_operadores_CNE_2025.csv',index=False)
B[B.barra.str.contains('BATUCO|CANTERAS|LAMPA|CHACABUCO|PANAMERICANA')].to_csv(O/'diccionario_nodos_relevantes.csv',index=False)
info={'sha256_articulo':json.loads((R/'procedencia/articulo_virginia.json').read_text())['sha256'],'ATT':float(np.average(co.ATT,weights=co.n_post)),'contraste_pre_completo':float(np.average(co.contraste_pre_completo,weights=co.n_post)),'cambio_Lampa_2020_2021':(l.loc[2021]-l.loc[2020]).to_dict(),'cambio_controles_2020_2021':(grp.loc[2021]-grp.loc[2020]).to_dict(),'controles_suben_D':int((delc.D>0).sum()),'controles':len(controls),'n_barras_Lampa':b[b.distrito_nombre=='LAMPA-4'].groupby('anio').barra.nunique().to_dict(),'n_barras_controles':b[b.distrito_nombre.isin(controls)].groupby('anio').barra.nunique().to_dict()}
(O/'diagnostico.json').write_text(json.dumps(info,ensure_ascii=False,indent=2))
fig,ax=plt.subplots(1,2,figsize=(10.4,3.1),layout='constrained')
for name,d,c in [('Lampa',l,'#17587a'),('Promedio de 18 controles',grp,'#9c4c23')]:
 ax[0].plot(d.index,d.D,'o-',label=name,color=c,lw=1.6,ms=3)
ax[0].set(ylabel='D (USD/MWh)',xlabel='Año',title='Diferencias respecto de Quillota');ax[0].legend(fontsize=8)
rr=l.D-grp.D;ax[1].plot(rr.index,rr,'o-',color='#17587a',ms=3);ax[1].axhline(0,color='grey',lw=.6);ax[1].set(title='Lampa menos controles',ylabel='Diferencia (USD/MWh)',xlabel='Año')
for a in ax:
 a.axvline(2021.5,ls='--',lw=.9,color='grey');a.spines[['top','right']].set_visible(False);a.tick_params(labelsize=8);a.set_xticks([2017,2019,2021,2023,2025])
fig.savefig(O/'diagnostico_lampa.png',dpi=240);plt.close(fig)
print(json.dumps(info,ensure_ascii=False,indent=2));print(co.to_string(index=False));print(delc.to_string())
