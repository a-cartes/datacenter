# Mapa de afirmaciones y evidencia

Las rutas siguientes son relativas a `SOCHER_2026_RM/`. Los resultados nuevos se generan en `salidas/reproduccion/trabajo/resultados/`; sus referencias de contraste están en `referencia/`.

| Afirmación del resumen | Insumo | Programa y salida |
|---|---|---|
| 63 registros, 138 hitos, 65 fuentes | `datos/instalaciones/{instalaciones,hitos,fuentes_instalaciones}.csv` | `scripts/verificar_cierre.py`; conteos y tablas de procedencia |
| Barra, subestación y distrito | `datos/geo/barras_diccionario.csv`, `subestaciones_unidades.csv` | `scripts/preparar_muestra.py`; paneles distritales y emparejamiento |
| Principal 1,05263 e IC [0,48444; 1,62082] | Muestra distrital con nodos incorporados | `scripts/resultados_socher.R`; `socher_20261005/estimaciones.csv` |
| Misma muestra con Lampa 2023: 1,01514 | Muestra principal, solo cambia G de Lampa | `scripts/contrastes_cierre_20261009.R`; `contrastes_estadisticos.json` |
| Exclusión de Lampa: 0,03273 | Muestra principal sin ese distrito | `scripts/resultados_socher.R`; `sensibilidad_exclusion.csv` |
| Promedio previo propio: −0,08663 | Diferenciales de cohortes y mismos controles | `scripts/diagnostico_cierre_20261009.py`; `contrastes_cohortes.csv` |
| Figura 1 | Precios anuales por distrito | Mismo diagnóstico; `series_grupos_anuales.csv` y `diagnostico_lampa.png` |
| 17/18 controles aumentan D; salto de 5,01062 | Paneles 2020–2021 | Mismo diagnóstico; `cambios_controles_2020_2021.csv` |
| Aportes 2,03073 de L y 2,97989 de C | Panel anual con factores | Mismo diagnóstico; descomposición contable, no causa operativa |
| Barras constantes: 2 Lampa y 52 controles | Panel barra-año y geografía | Mismo diagnóstico; `barras_2020_2021.csv`, `diagnostico.json` |
| Test previo singular y tres horizontes comunes | Coeficientes y covarianza de Sun y Abraham | `scripts/contrastes_cierre_20261009.R`; `contrastes_estadisticos.json` |
| 96 precios coinciden con el original auditado | Extracto agosto y valores archivados | `scripts/verificar_cierre.py`; cotejo del extracto con evidencia previa. Lectura original documentada en `archivo/scripts_originales/verificar_agosto_2021.py` |
| Apertura distinta de conexión o utilización | Cartas y fuentes citadas por etapa | `referencia/cierre_socher_20261009/matriz_conexiones_potencias.csv`; curación documental, no inferencia automática |
| 5,455728–9,09288 TWh/año y MUSD por 1 USD/MWh | 1.038 MW × fracción × 8.760 horas | `scripts/calculos_comparacion_2030.py`; `sensibilidad_demanda_RM_2030.csv` |

La tabla final para consulta se escribe como `salidas/reproduccion/tabla_1.csv`. La figura se copia como `figura_1.png`. La verificación compara las cifras con referencias congeladas y realiza cálculos independientes: no basta con copiar los resultados antiguos para superar los controles.
