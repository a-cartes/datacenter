#!/usr/bin/env python3
"""Prepara el contenido tipado del libro de revisión desde salidas verificadas."""
from pathlib import Path
import argparse
import json
import pandas as pd


def main():
    p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]); a=p.parse_args()
    stage=a.root.resolve()/'SOCHER_2026_v8_panel_causal'
    def read(rel,**kw):return pd.read_csv(stage/rel,**kw)
    def rec(d):return json.loads(d.to_json(orient='records',force_ascii=False))
    def c(key,label,width=18,**kw):return dict(key=key,label=label,width=width,**kw)
    val=json.loads((stage/'validacion/validacion_panel.json').read_text())
    status=json.loads((stage/'resultados/estado_estimacion.json').read_text())
    ev=read('eventos/matriz_eventos_elegibilidad.csv',dtype=str).fillna('')
    ctrl=read('resultados/matriz_controles_revision.csv',dtype=str).fillna('')
    mon=read('panel/panel_mensual.csv',dtype={'codigo_documentado':str})
    cov=read('panel/cobertura_mes_reloj.csv')
    dictionary=read('panel/diccionario_panel.csv')
    annual=read('resultados/tabla_descriptiva_anual.csv')
    support=read('resultados/soporte_eventos_ventana_registrada.csv')
    summary=[
        {'medida':'Precios horarios de origen','valor':val['filas_horarias_fuente'],'alcance':'DEF v0.2.0; fuente congelada de 31 columnas.'},
        {'medida':'Filas del panel diario','valor':val['filas_diarias'],'alcance':'Incluye 21 días-barra sin precio.'},
        {'medida':'Filas del panel mensual','valor':val['filas_mensuales'],'alcance':'Julio 2024 mantiene dos regímenes.'},
        {'medida':'Etiquetas de barra distintas','valor':val['etiquetas_distintas'],'alcance':'No equivalen a centros ni activos físicos independientes.'},
        {'medida':'Días-barra con 24 pares','valor':val['dias_barra_24_parejas_completas'],'alcance':'Incluye barras de referencia; no certifica 24 horas físicas.'},
        {'medida':'Etiquetas horarias ausentes','valor':val['ausencias_horarias_frente_union'],'alcance':'Frente a unión observada. No detecta faltantes comunes a todas las barras.'},
        {'medida':'Enlaces agosto 2023','valor':val['homologacion_agosto2023']['enlaces_exactos'],'alcance':'53 de 58 etiquetas. Cambian metadatos, no precios.'},
        {'medida':'Eventos registrados','valor':status['eventos_en_registro'],'alcance':'Hitos, fases y maniobras; no adopciones independientes.'},
        {'medida':'Eventos causales habilitados','valor':status['eventos_habilitados'],'alcance':'Véanse razones y brechas en Eventos.'},
        {'medida':'Comparadores habilitados','valor':status['comparadores_habilitados'],'alcance':'Desconocido no equivale a no tratado o no expuesto.'},
        {'medida':'ATT','valor':'No estimable','alcance':'No disponible; no significa efecto cero.'},
    ]
    specs=[
      dict(name='Resumen',title='Centros de datos y precios nodales · revisión v8',note='Período: 01/01/2020–18/09/2026. Instantánea de resultados reproducibles, sin ATT habilitado.',columns=[c('medida','Medida',36),c('valor','Valor',20,format='#,##0'),c('alcance','Alcance',90,wrap=True)],rows=summary,rowHeight=35,previews=['A1:C16']),
      dict(name='Eventos',title='Elegibilidad de eventos y conexiones',note='SI en fecha realizada no certifica entrada de nueva carga. Fuentes y vigencia pertenecen a cada hito.',columns=[c('evento_id','Evento',34),c('centro_id','Centro',25),c('fase','Fase / instalación',40,wrap=True),c('fecha_min','Fecha desde',14,type='date'),c('fecha_max','Fecha hasta',14,type='date'),c('fecha_realizada','Realizado',13),c('barra_cmg','Barra CMg candidata',28),c('elegible_evento_causal','Causal habilitado',15),c('razon_elegibilidad','Decisión',58,wrap=True),c('brecha_pendiente','Brecha pendiente',65,wrap=True),c('fuente_ids','Fuentes',22,wrap=True),c('localizadores','Localizador',50,wrap=True),c('vigencia_desde','Vigencia desde',16,type='date'),c('vigencia_hasta','Vigencia hasta',16,type='date'),c('tipo_vigencia','Alcance de vigencia',52,wrap=True)],rows=rec(ev.replace('',None)),rowHeight=95,previews=['A1:H10','I5:O10'],rules=[{'column':'H','text':'NO'}]),
      dict(name='Controles',title='Revisión de comparadores',note='Registro de etiquetas, no certificación de unidades nunca tratadas. Cobertura: v0.2.0/Cobertura_por_mes_barra.csv.',columns=[c('barra_cmg','Barra CMg',30),c('centros_candidatos','Centros vinculados',48,wrap=True),c('referencia_descriptiva','Referencia de precio',17),c('historia_no_tratamiento_verificada','Historia sin tratamiento',24),c('exposicion_electrica','Exposición eléctrica',24),c('elegible_control_causal','Control habilitado',18),c('motivo','Motivo',68,wrap=True)],rows=rec(ctrl),rowHeight=56,previews=['A1:F12','G5:G12']),
      dict(name='Mensual',title='Panel mensual por etiqueta de barra',note='Fuente: panel_mensual.csv. Precio: todas las etiquetas; diferencial: días con 24 pares. Identidad física no certificada.',columns=[c('barra_cmg','Barra CMg',29),c('mes','Mes publicado',16),c('familia_reloj','Reloj H / M',12),c('n_dias_con_precio','Días con precio',17,format='#,##0'),c('n_dias_24','Días con 24 pares',18,format='#,##0'),c('precio_mean_usd_mwh','Precio medio USD/MWh',23,format='0.000'),c('dif_q110_mean_usd_mwh_dias_24','Diferencial Q110 USD/MWh (24 pares)',29,format='0.000'),c('n_horas_ausentes_frente_union','Etiquetas ausentes',20,format='#,##0'),c('id_documental_tipo','Tipo de identidad documental',30),c('codigo_documentado','Código documental',33)],rows=rec(mon),previews=['A1:G15','H5:J15']),
      dict(name='Cobertura',title='Cobertura mensual por régimen',note='H: histórico. M: moderno. Julio 2024 se divide el día 15. Fuente: cobertura_mes_reloj.csv.',columns=[c('mes','Mes',16),c('familia_reloj','Reloj',12),c('barras_etiqueta','Etiquetas de barra',19,format='#,##0'),c('filas_dia','Filas día-barra',19,format='#,##0'),c('horas_precio','Precios horarios',20,format='#,##0'),c('dias_barra_24','Días-barra 24 pares',23,format='#,##0'),c('dias_barra_sin_precio','Días-barra sin precio',24,format='#,##0'),c('horas_ausentes_union','Etiquetas ausentes',21,format='#,##0')],rows=rec(cov),previews=['A1:H15']),
      dict(name='Descriptivos',title='Distribución del diferencial diario',note='Fuente: tabla_descriptiva_anual.csv. 24 pares, excluye Quillota110. Igual peso por barra-día; composición variable.',columns=[c('anio','Año',12,format='0'),c('familia_reloj','Reloj',12),c('barra_dias','Días-barra',18,format='#,##0'),c('etiquetas_barra','Etiquetas barra',18,format='#,##0'),c('media_diferencial_usd_mwh','Media USD/MWh',21,format='0.000'),c('mediana_diferencial_usd_mwh','Mediana USD/MWh',22,format='0.000'),c('p10_diferencial_usd_mwh','Percentil 10 USD/MWh',24,format='0.000'),c('p90_diferencial_usd_mwh','Percentil 90 USD/MWh',24,format='0.000')],rows=rec(annual),previews=['A1:H14']),
      dict(name='Soporte',title='Soporte individual de ventanas candidatas',note='Cobertura no habilita causalidad. g: primer día posterior. Ventana pre: −112 a −8; post: 0 a 89.',columns=[c('evento_id','Evento',34),c('barra_cmg','Barra candidata',28),c('g_candidato','g candidato',16,type='date'),c('dias_pre_24_pares','Días pre 24 pares',20,format='#,##0'),c('dias_post_24_pares','Días post 24 pares',20,format='#,##0'),c('cruza_cambio_regimen','Cruza cambio de régimen',25),c('estado_soporte','Estado de cobertura',46),c('habilita_causalidad','Causal habilitado',18)],rows=rec(support),rowHeight=32,previews=['A1:H14']),
      dict(name='Diccionario',title='Diccionario de los paneles y enlaces',note='El CSV/Parquet conserva todos los campos. Este libro es una selección para revisión.',columns=[c('tabla','Tabla',24),c('variable','Variable',44),c('tipo','Tipo',15),c('descripcion','Definición',110,wrap=True)],rows=rec(dictionary),rowHeight=48,previews=['A1:D14']),
    ]
    sources_path=stage/'eventos/catalogo_fuentes.csv'
    if sources_path.exists():
        sources=read('eventos/catalogo_fuentes.csv',dtype=str).fillna('')
        specs.append(dict(name='Fuentes',title='Fuentes documentales de eventos',note='Registro de procedencia y alcance. Consulte los documentos originales para interpretar cada hito.',columns=[c(k,k.replace('_',' ').capitalize(),45 if ('url' in k or 'titulo' in k or 'localizador' in k) else 24,wrap=True) for k in sources.columns],rows=rec(sources),rowHeight=84,previews=['A1:F10']))
    payload={'sheets':specs}
    folder=stage/'revision'; folder.mkdir(exist_ok=True)
    (folder/'contenido_excel.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'hojas':[(s['name'],len(s['rows'])) for s in specs]},ensure_ascii=False))

if __name__=='__main__':main()
