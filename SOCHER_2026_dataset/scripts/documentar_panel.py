"""Diccionario semántico del panel principal con tipos y faltantes efectivos."""
from pathlib import Path
import pandas as pd
B=Path(__file__).resolve().parents[1]
DESCS={
'fecha': 'Fecha de la etiqueta publicada; no se reasigna por UTC.',
'hora_etiqueta': 'Etiqueta original de la hora, incluidos valores adicionales como 25; no es hora UTC.',
'barra_cmg': 'Nombre abreviado de la serie en el libro oficial.',
'nemotecnico': 'Código oficial según homologación mensual o enlace provisional indicado.',
'clave_barra_historica': 'Combinación de etiqueta CMg y código conservada sin fusionar cambios históricos.',
'entidad_busqueda': 'Familia usada para localizar series; no identifica un centro de datos.',
'tension_kv_etiqueta': 'Tensión inferida del sufijo nominal de la etiqueta; puede diferir de la homologación.',
'tension_kv_homologacion': 'Tensión que figura en el nombre físico de la homologación.',
'barra_aux': 'Nombre físico conservado de la homologación, incluidas marcas originales.',
'precio_usd_mwh': 'Costo marginal horario publicado; mills/kWh numéricamente equivale a USD/MWh.',
'estado_identidad': 'Homologación mensual exacta o coincidencia adyacente provisional; no valida causalidad.',
'meses_evidencia_identidad': 'Meses de las homologaciones que respaldan la identificación.',
'nota_identidad': 'Diferencias de nombre o advertencias registradas durante el enlace.',
'marcas_fuente': 'Marcas de publicación, incluidas EN_REVISION y NO_MOSTRAR; vacía indica ninguna marca recuperada.',
'mes_fuente': 'Mes del libro de precios del que se extrajo la observación.',
'archivo_fuente': 'Ruta relativa al proyecto del libro oficial preservado.',
'hoja_fuente': 'Hoja del libro original.',
'fila_excel': 'Fila original del libro, contada desde uno.',
'columna_barra_excel': 'Número de columna original que contiene la barra en ese bloque.',
'archivo_homologacion': 'Archivo o archivos usados para enlazar la identidad.',
'fila_homologacion': 'Fila o filas originales de la homologación.',
'regimen_temporal': 'Indicador temporal heredado de extracción; por sí solo no define metodología CMg Real.',
'vinculo_centro_datos': 'Advierte que la capa de precios no adjudica centros ni eventos.',
'barra_id': 'Identificador estable derivado de la clave histórica; no equivale a campus independiente.',
'observacion_id': 'Clave única barra histórica, fecha y etiqueta horaria.',
'periodo_fuente_id': 'Fecha y hora en la convención de la publicación; usada para emparejar precios.',
't_dia': 'Días de calendario desde 1970-01-01. No comprime meses sin datos.',
'mes_calendario': 'Mes YYYY-MM de la fecha publicada.',
'dia_semana': 'Día de semana de la fecha publicada: lunes=0, domingo=6.',
'timestamp_utc_validado': 'Reloj UTC del precio; nulo hasta conciliar la convención horaria.',
'estado_reloj': 'Estado de validación del reloj del precio.',
'homologacion_exacta': 'Verdadero únicamente cuando existe homologación del mismo mes.',
'tiene_marca_revision': 'Verdadero si se recuperó al menos una marca de revisión o no publicación.',
'precio_revision_estricta': 'Precio observado, con homologación exacta y sin marcas; es una regla de calidad, no de identificación causal.',
'precio_observado': 'Verdadero cuando el valor de precio está presente; un precio cero sigue siendo observado.',
'unidad_precio': 'Unidad de precio declarada para cálculos: USD/MWh.',
'regimen_valorizacion': 'Procedimiento de los libros históricos integrados, anterior al 15 de julio de 2024.',
'tratado_it': 'Estado de tratamiento en el período; nulo si no se ha adjudicado, nunca cero por desconocimiento.',
'post_evento': 'Indicador de período posterior al evento analítico; nulo mientras no se haya definido y verificado.',
'control_validado': 'Elegibilidad como comparación para un diseño específico; nulo en la base actual.',
'cohorte_g_dia': 'Primera fecha de adopción en la escala de t_dia; nula hasta validar. Cero se reserva para no tratados documentados al exportar.',
'tiempo_evento_dias': 'Días relativos al evento causal elegido; nulo en esta versión.',
'tiempo_evento_horas': 'Horas físicas relativas al evento; nulo hasta verificar evento y reloj.',
'exposicion_red': 'Medida de exposición eléctrica al tratamiento de otros; nula mientras no existan vigencia y regla defendibles.',
'carga_asignada_mw': 'Potencia de carga atribuible al resultado y período con enlace verificado; nula por suministro/reloj pendientes.',
'evento_id_asignado': 'Evento analítico asignado a la observación; nulo, aunque existan hitos documentados por separado.',
'fecha_tratamiento_causal': 'Fecha de intervención elegida y defendida; no equivale automáticamente a EO o PES.',
'estado_asignacion_causal': 'Explica el estado pendiente de evento, comparación y exposición.',
'elegible_estimacion_causal': 'Falso en esta entrega; no se ha cerrado una muestra causal.',
'estado_enlace_carga': 'Estado del enlace entre mediciones y precios, incluida su vigencia y reloj.'
}

def description(c):
    if c in DESCS:return DESCS[c]
    for tag,ref in [('q110','Quillota 110 kV'),('q220','Quillota 220 kV')]:
        if c.endswith('_'+tag):
            base=c[:-(len(tag)+1)]
            if base in DESCS:return DESCS[base]+' En este campo corresponde a la referencia '+ref+'.'
        if c==f'diferencial_{tag}_usd_mwh':return 'Precio de la barra menos precio de '+ref+' en la misma etiqueta y régimen; resultado relativo descriptivo.'
        if c==f'es_referencia_{tag}':return 'La observación corresponde a '+ref+'; su diferencial consigo misma es cero y se excluye de los pares estrictos.'
        if c==f'par_precio_estricto_{tag}':return 'Ambos precios observados, identidad mensual exacta y sin marcas; excluye autorreferencia '+ref+'. No valida grupo de control.'
    raise ValueError('Variable sin definición: '+c)

def main():
    p=pd.read_parquet(B/'tablas/panel_barra_hora.parquet')
    rows=[]
    for col in p:
        unit=''
        if 'usd_mwh' in col:unit='USD/MWh'
        elif 'tension_kv' in col:unit='kV'
        elif col=='carga_asignada_mw':unit='MW'
        elif col in ['t_dia','cohorte_g_dia','tiempo_evento_dias']:unit='día de calendario'
        elif col=='tiempo_evento_horas':unit='hora física (pendiente)'
        rows.append({'tabla':'panel_barra_hora','variable':col,'definicion':description(col),'unidad':unit,'tipo':str(p[col].dtype),'n_nulos':int(p[col].isna().sum())})
    pd.DataFrame(rows).to_csv(B/'documentacion/diccionario_panel.csv',index=False,encoding='utf-8-sig')
    print(f'Diccionario del panel: {len(rows)} variables definidas.')
if __name__=='__main__':main()
