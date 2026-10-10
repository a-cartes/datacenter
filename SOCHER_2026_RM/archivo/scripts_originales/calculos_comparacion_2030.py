"""Equivalencias condicionales de energía y valoración, sin estimar efectos de precios."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'resultados/socher_20261005'
OUT.mkdir(exist_ok=True)
inputs = {
    'fecha_calculo': '2026-10-05',
    'fuente': 'https://systep.cl/data-centers-cuadruplicaran-su-demanda-de-energia-a-2030-alza-presionara-al-sistema-electrico/',
    'fecha_publicacion': '2025-09-23',
    'atribucion': 'Systep reproduce proyecciones atribuidas al Coordinador; no se obtuvo su tabla técnica original.',
    'chile_2025_MW': 325,
    'chile_2030_MW': 1207,
    'RM_2030_MW': 1038,
    'RM_2025_MW': None,
    'definicion_MW': 'Demanda eléctrica proyectada reportada. La nota no aclara si es potencia máxima, media o contratada.',
    'horas_2030': 8760,
    'supuesto': 'Los casos fijan potencia media anual en 60%, 80% y 100% del valor publicado. No son factores de carga medidos ni intervalos de pronóstico. Si los MW originales son ya potencia media, solo corresponde el caso 100%.',
    'formula_energia': 'E_MWh = 1038 MW * fraccion * 8760 h',
    'formula_valoracion': 'V_USD = E_MWh * variacion_uniforme_USD_por_MWh',
    'alcance_valoracion': 'Cambio hipotético en valoración spot bruta de la energía del sector. No es gasto contractual efectivo, costo social, costo de operación del sistema, tarifa residencial ni impacto causal de centros de datos.',
    'restricciones': ['No se suma cartera de proyectos al agregado de 1038 MW.', 'No se extrapola el ATT histórico por MW.', 'No se calcula crecimiento RM sin base RM 2025.', 'No se aplica PUE a MW cuya definición técnica no está confirmada.'],
}
metrics = {
    'crecimiento_chile_porcentaje': (1207 / 325 - 1) * 100,
    'multiplicador_chile': 1207 / 325,
    'CAGR_chile_2025_2030_porcentaje': ((1207 / 325) ** (1/5) - 1) * 100,
    'participacion_RM_2030_porcentaje': 1038 / 1207 * 100,
}
rows = []
for f in (0.6, 0.8, 1.0):
    mwh = 1038 * f * 8760
    rows.append(dict(fraccion_potencia_publicada=f, potencia_media_MW=1038*f,
                     energia_TWh=mwh/1e6,
                     millones_USD_por_1_USD_MWh=mwh/1e6,
                     millones_USD_por_10_USD_MWh=mwh*10/1e6))
with (OUT / 'sensibilidad_demanda_RM_2030.csv').open('w', newline='') as fp:
    w=csv.DictWriter(fp, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
result = {'insumos': inputs, 'metricas': metrics, 'escenarios_ilustrativos': rows,
          'evidencia_conexion': {
              'fuente': 'https://cartas.coordinador.cl/download_saved_file/6887c8cf3563571c24dc6f4a',
              'documento': 'Coordinador DE 04560-25, 25 de julio de 2025',
              'proyecto': 'Ascenty Data Center Santiago Chile 4',
              'subestacion_propuesta': 'Nueva S/E Seccionadora Punta Verde 110 kV',
              'fin_2027_MW': 50, 'fin_2028_MW': 150,
              'estado': 'Demanda proyectada y aprobación del informe por el Coordinador; no certifica operación ni autorización final de la CNE.',
              'nota': 'Cronogramas de fin de año, no consumo a esa potencia durante todo el año. La carta documenta insuficiencia N-1 en Chacabuco.'}}
(OUT / 'comparacion_2030.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps({'metricas': metrics, 'escenarios': rows}, ensure_ascii=False, indent=2))
