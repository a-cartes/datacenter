#!/usr/bin/env python3
"""Tablas y figuras descriptivas, sin atribuir causalidad ni estimar inferencia."""
from pathlib import Path
import argparse
import hashlib
import json
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/socher_v8_matplotlib')
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    a=parser.parse_args(); root=a.root.resolve(); stage=root/'SOCHER_2026_v8_panel_causal'
    out=stage/'resultados'; out.mkdir(exist_ok=True)
    figures=stage/'figuras'; figures.mkdir(exist_ok=True)
    config_path=stage/'documentos/protocolo_config.json'
    config=json.loads(config_path.read_text())
    panel_path=stage/'panel/panel_diario.csv'
    d=pd.read_csv(panel_path,parse_dates=['fecha'],dtype={'codigo_documentado':str},low_memory=False)
    assert not d.duplicated(['barra_cmg','familia_reloj','fecha']).any()
    d['anio']=d.fecha.dt.year
    q=d.loc[d.barra_cmg.ne('QUILLOTA______110') & d.n_pares_q110.eq(24) & d.n_horas_observadas.eq(24)].copy()
    assert q.dif_q110_mean_usd_mwh.notna().all()
    annual=q.groupby(['anio','familia_reloj']).agg(
        barra_dias=('fecha','size'), etiquetas_barra=('barra_cmg','nunique'),
        dias_calendario=('fecha','nunique'), media_diferencial_usd_mwh=('dif_q110_mean_usd_mwh','mean'),
        mediana_diferencial_usd_mwh=('dif_q110_mean_usd_mwh','median'),
        p10_diferencial_usd_mwh=('dif_q110_mean_usd_mwh',lambda s:s.quantile(.1)),
        p90_diferencial_usd_mwh=('dif_q110_mean_usd_mwh',lambda s:s.quantile(.9)),
        fraccion_diferencial_cero=('dif_q110_mean_usd_mwh',lambda s:float(s.eq(0).mean())),
    ).reset_index()
    annual.to_csv(out/'tabla_descriptiva_anual.csv',index=False)
    monthly=q.groupby(['mes','familia_reloj']).agg(
        barra_dias=('fecha','size'), etiquetas_barra=('barra_cmg','nunique'),
        media_diferencial_usd_mwh=('dif_q110_mean_usd_mwh','mean'),
        mediana_diferencial_usd_mwh=('dif_q110_mean_usd_mwh','median'),
        p10_diferencial_usd_mwh=('dif_q110_mean_usd_mwh',lambda s:s.quantile(.1)),
        p90_diferencial_usd_mwh=('dif_q110_mean_usd_mwh',lambda s:s.quantile(.9)),
    ).reset_index()
    monthly.to_csv(out/'tabla_descriptiva_mensual.csv',index=False)
    bybar=q.groupby(['barra_cmg','mes','familia_reloj']).agg(
        dias_24_pares=('fecha','size'), media_diferencial_usd_mwh=('dif_q110_mean_usd_mwh','mean'),
        precio_medio_usd_mwh=('precio_mean_usd_mwh','mean'),
    ).reset_index()
    bybar.to_csv(out/'revision_mensual_por_barra.csv',index=False)
    event_path=stage/'eventos/matriz_eventos_elegibilidad.csv'
    ev=pd.read_csv(event_path,dtype=str).fillna('')
    support=[]
    start=pd.Timestamp(config['base_fecha_desde']); end=pd.Timestamp(config['base_fecha_hasta'])
    for row in ev.to_dict('records'):
        precise=row['fecha_min']==row['fecha_max'] and bool(row['fecha_min']) and row['fecha_realizada']=='SI'
        if not precise:
            support.append({'evento_id':row['evento_id'],'barra_cmg':row['barra_cmg'],'estado_soporte':'SIN_FECHA_DIARIA_REALIZADA','habilita_causalidad':'NO'})
            continue
        g=pd.Timestamp(row['fecha_min'])+pd.Timedelta(days=1)
        pre0=g+pd.Timedelta(days=config['ventana_pre_inicio']); pre1=g+pd.Timedelta(days=config['ventana_pre_fin'])
        post1=g+pd.Timedelta(days=config['ventana_post_fin'])
        bars=row['barra_cmg'].split(';') if row['barra_cmg'] else ['']
        for bar in bars:
            bar=bar.strip(); sub=d.loc[d.barra_cmg.eq(bar)]
            quality=sub.n_horas_observadas.eq(24) & sub.n_pares_q110.eq(24)
            valid=sub.loc[quality]
            np_=int(valid.fecha.between(pre0,pre1).sum()); no_=int(valid.fecha.between(g,post1).sum())
            baseok=bool(valid.fecha.eq(pre1).any())
            cross=pre0<pd.Timestamp(config['cambio_regimen_fecha'])<=post1
            flag=bool(bar and np_>=config['min_dias_validos_pre'] and no_>=config['min_dias_validos_post'] and baseok)
            support.append({'evento_id':row['evento_id'],'barra_cmg':bar,'g_candidato':g.date().isoformat(),
                'pre_desde':pre0.date().isoformat(),'pre_hasta':pre1.date().isoformat(),'post_hasta':post1.date().isoformat(),
                'dias_pre_24_pares':np_,'dias_post_24_pares':no_,'base_observada_24_pares':baseok,
                'ventana_calendario_dentro_base':bool(pre0>=start and post1<=end),
                'cruza_cambio_regimen':cross,'soporte_mecanico_individual':flag,
                'soporte_temporal_protocolo':bool(flag and not cross),
                'estado_soporte':'CRUZA_RELOJ_SIN_PUENTE' if flag and cross else 'CANDIDATO_CON_COBERTURA' if flag else 'COBERTURA_O_ENLACE_INSUFICIENTE',
                'habilita_causalidad':'NO',
                'motivo':'Soporte individual de etiquetas. Faltan comparación común, identidad/vigencia, exposición y demás puertas del protocolo.'})
    pd.DataFrame(support).to_csv(out/'soporte_eventos_ventana_registrada.csv',index=False)

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10.5,5.5))
    for family,color,name in [('H','#305D82','Histórico'),('M','#AE6535','Moderno')]:
        s=monthly.loc[monthly.familia_reloj.eq(family)].copy()
        xx=pd.to_datetime(s.mes+'-01')
        ax.plot(xx,s.media_diferencial_usd_mwh,color=color,label=name,lw=1.8)
        ax.fill_between(xx,s.p10_diferencial_usd_mwh,s.p90_diferencial_usd_mwh,color=color,alpha=.15)
    ax.axhline(0,lw=.8,color='#555555'); ax.set_ylabel('Diferencial respecto de Quillota 110 (USD/MWh)')
    ax.set_title('Precios relativos en las barras seleccionadas',loc='left',fontweight='bold')
    ax.legend(frameon=False); ax.grid(axis='y',alpha=.15)
    fig.text(.08,.015,'Media con peso igual por barra-día. Banda: percentiles 10–90, no intervalo de confianza.\nSolo días con 24 pares. Composición variable; regímenes separados. No identifica efectos de centros de datos.',fontsize=8)
    fig.tight_layout(rect=[0,.09,1,1]); fig.savefig(figures/'01_diferenciales_descriptivos.png',dpi=180); fig.savefig(figures/'01_diferenciales_descriptivos.pdf'); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.7))
    labels=annual.anio.astype(str)+' · '+annual.familia_reloj
    x=np.arange(len(annual)); median=annual.mediana_diferencial_usd_mwh
    ax.errorbar(x,median,yerr=[median-annual.p10_diferencial_usd_mwh,annual.p90_diferencial_usd_mwh-median],fmt='o',color='#305D82',capsize=5)
    ax.axhline(0,lw=.8,color='#555555'); ax.set_xticks(x,labels); ax.set_ylabel('USD/MWh'); ax.set_title('Dispersión observada del diferencial diario',loc='left',fontweight='bold'); ax.grid(axis='y',alpha=.15)
    fig.text(.09,.02,'Punto: mediana. Barras: percentiles 10 y 90, no incertidumbre de un efecto causal.\nH: histórico; M: moderno. 2026 termina el 18 de septiembre. Muestra con composición variable.',fontsize=8)
    fig.tight_layout(rect=[0,.11,1,1]); fig.savefig(figures/'02_distribucion_anual.png',dpi=180); fig.savefig(figures/'02_distribucion_anual.pdf'); plt.close(fig)
    meta={'filas_panel_diario':len(d),'barra_dias_descripcion_24_pares_excluye_referencia':len(q),
          'evento_barras_evaluados':len(support),'efectos_causales_estimados':0,
          'protocolo_sha256':hashlib.file_digest(config_path.open('rb'),'sha256').hexdigest(),
          'panel_sha256':hashlib.file_digest(panel_path.open('rb'),'sha256').hexdigest(),
          'eventos_sha256':hashlib.file_digest(event_path.open('rb'),'sha256').hexdigest(),
          'script_sha256':hashlib.file_digest(Path(__file__).open('rb'),'sha256').hexdigest(),
          'no_es_muestra_causal':True,'bandas_figuras':'percentiles_descriptivos_no_intervalos_de_confianza'}
    (out/'manifest_descriptivos.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(meta,ensure_ascii=False))

if __name__=='__main__':main()
