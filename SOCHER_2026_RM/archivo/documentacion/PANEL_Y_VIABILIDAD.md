# Panel analítico y diagnóstico de viabilidad

Fecha: 2 de octubre de 2026. Programas: `construir_panel_barras.py`, `covariables_censo.py` y `preparar_muestra.py`.

## Construcción

| Tabla | Unidad | Archivo | Reglas |
|---|---|---|---|
| Precios originales extraídos | barra × día × hora (histórico); barra × día × hora con n.º de cuartos (moderno) | `datos/precios_hist/AAAAMM.parquet`, `datos/precios_mod/AAAAMM.parquet` | Valor publicado sin modificar. Vacíos como faltantes y ceros conservados. Duplicados idénticos eliminados y contados por mes (`diagnostico_AAAAMM.json`); no hubo duplicados con valores distintos |
| Barra-mes | barra × mes | `datos/panel/barra_mes.parquet` | Sumas y conteos de P, E, D, L y C. Una hora entra en D si existen P y la referencia única de Quillota |
| Barra-año | barra × año | `datos/panel/barra_anio.parquet` | Promedio ponderado por horas; cobertura = horas válidas / horas con referencia |
| Referencia | mes | `datos/panel/referencia_mes.csv` | Horas con referencia y ceros de Quillota |
| Unidad-año | unidad (copia) × año | `datos/analitico/muestra_<alt>.csv` | Promedio simple de las barras balanceadas de la unidad; pesos 1/m por copia |
| Covariables | distrito / comuna | `datos/covariables/` | Censo 2017; supresiones como faltantes, con denominadores solo sobre manzanas con dato |

**Composición de nodos.** El número de barras con precio crece de 1.239 (2017) a 1.600 (2025) a nivel nacional. En la RM hay 212 barras localizadas; 194 tienen cobertura ≥ 0,9 los 9 años. El panel principal usa solo esas 194, para que un cambio de promedio no provenga de nodos que entran o salen. Los nodos creados para centros de datos, como S/E Las Canteras (2024), no tienen años previos y quedan fuera del panel balanceado. La variante `distrito_nobal` los incorpora cuando cumplen la cobertura anual.

## Covariables previas

El Censo 2017 se levantó el 19/04/2017, antes de cualquier entrada elegible (≥ 2019).

| Artículo (ACS 2015–2016, sector censal) | Chile (Censo 2017, distrito) | Equivalencia |
|---|---|---|
| Población | log población | Directa |
| Viviendas | log viviendas | Directa |
| % blancos | % pueblos originarios; % inmigrantes | Composición demográfica; no equivalente |
| % con educación secundaria | — | No disponible en las capas por distrito (requiere microdatos de personas) |
| Ingreso mediano del hogar | % de viviendas con materialidad aceptable (indicador socioeconómico indirecto) | Sustitución conceptual declarada |

CASEN no es representativa por distrito ni, en general, por comuna (diseño nacional y regional desde 2011), por lo que no se usó. Las estimaciones de pobreza comunal por áreas pequeñas medirían otra cosa y solo existirían a escala comunal.

## Soporte

| Elemento | Distrito (principal) |
|---|---|
| Tratadas | 3: Colina-3 (G_doc 2021, G_min 2020), Lampa-4 (G_doc 2023, G_min 2021), San Bernardo-11 (2023) |
| Cohortes | 2021 (1 unidad) y 2023 (2) con G_doc; 2020, 2021 y 2023 con G_min |
| Años previos / posteriores | Cohorte 2021: 4 previos y 5 posteriores. Cohorte 2023: 6 previos y 3 posteriores |
| Controles con precio | 57 |
| Tras el emparejamiento | 16 controles únicos en 30 posiciones; ningún tratado fuera del soporte |
| Balance (dif. estandarizada, antes → después) | log pob 0,97 → −0,24; log viv 0,94 → −0,27; materialidad 0,76 → −0,12; inmigrantes 0,14 → 0,38; pueblos originarios −0,23 → −0,29 |

## Diagnóstico de viabilidad

1. **Medida.** Viable. D está reconstruido y validado como componente espacial relativo a Quillota. L y C solo existen hasta 2023 como años completos.
2. **Tratamiento.** Muy insuficiente. Hay 2 a 4 tratamientos independientes según la unidad, frente a 19 en el artículo. Dos de los tres distritos tratados tienen fecha de entrada incierta entre años, y el resultado cambia de signo con la regla de G.
3. **Comparación.** Hay muchos controles, pero los tratados son periurbanos, de baja densidad y conectados a la red de 110 kV del norponiente y del sur, que se desacopla. Los controles cercanos están expuestos y los lejanos son menos comparables.
4. **Inferencia.** Con 3 conglomerados tratados, los errores por conglomerado subestiman la incertidumbre. La inferencia por aleatorización es la referencia, pero tampoco resuelve la escasez de tratamientos.

**Conclusión.** El panel permite estimar la réplica de forma descriptiva y transparente, pero no sostiene una interpretación causal defendible del efecto medio. Muchas horas o barras no sustituyen la falta de tratamientos independientes.
