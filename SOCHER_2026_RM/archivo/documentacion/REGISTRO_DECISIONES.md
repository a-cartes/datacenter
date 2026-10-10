# Registro de decisiones de la réplica

Cada entrada indica fecha, evidencia, alternativas, elección, efecto sobre la interpretación y si se adoptó **antes (A)** o **después (D)** de observar estimaciones de efectos. Hasta D-19, todas son anteriores a cualquier contraste entre unidades tratadas y de comparación. La única información de resultados vista antes de D-19 fue descriptiva: promedios nacionales anuales de D y el piloto del 15/07/2024.

Las investigaciones anteriores del directorio no se usaron como insumo analítico. Como se explica en D-03, sí se emplearon archivos **originales** del Coordinador descargados manualmente por el usuario. Su integridad se verificó por hash o ETag.

| Id | Fecha | Decisión | Evidencia | Alternativas consideradas | Efecto | A/D |
|---|---|---|---|---|---|---|
| D-01 | 2026-10-02 | Referencia de precio: Quillota 220 kV | En ambas muestras, FP = 1 en todos los intervalos y la barra siempre está en el subsistema principal (SD1) | Promedio ponderado por carga (no reconstruible), otra barra | D = P − P_Quillota es exactamente L + C bajo la normalización chilena. No es la referencia distribuida de PJM | A |
| D-02 | 2026-10-02 | Resultado principal: D = P − E; L = E(FP − 1) y C = P − E·FP como descomposición secundaria | Identidad P = λ_s·FP verificada (mediana del error relativo 3e-8 en 2024; 99,97% < 0,5% en 2017) | Solo P; diferencia contra otra barra | L y C quedan definidos respecto de Quillota. C solo capta separación de subsistemas | A |
| D-03 | 2026-10-02 | Usar libros mensuales DEF descargados manualmente por el usuario (2017-01 a 2024-07) | El Coordinador responde 403 a descargas automáticas. Dic-2017 tiene el mismo SHA-256 que la descarga propia (6b02a5d4…) | Esperar descarga manual nueva | Integridad acreditada para un mes por hash. En los demás, la procedencia es declarada | A |
| D-04 | 2026-10-02 | Versiones: nov-2017 = cmg1711_def (SEN); oct-2018 = DEF; may-2024 = cmg2405_def.zip | cmg2405_def-2 truncado; archivo de 1.489 bytes = HTML 416 | Usar versión SIC de nov-2017 | El SIC de nov-2017 queda disponible para contraste | A |
| D-05 | 2026-10-02 | Régimen nuevo desde S3 público (CMG_REAL, REAL-DEF), verificado por ETag multiparte | 11 copias previas idénticas al objeto vigente. Jun–dic 2025 descargados por el proyecto | Versión PRE | Precios modernos con trazabilidad byte a byte | A |
| D-06 | 2026-10-02 | Convención horaria: hora histórica h = promedio de los cuartos HORA = h; moderno HRA = h − 1 | Abril 2024: 99,9% < 0,01 USD/MWh; desplazado: 31% | Sin ajuste | Alineación hora a hora entre regímenes | A |
| D-07 | 2026-10-02 | Factores históricos por tramos: horas 1–8, 9–18 y 19–24 | Búsqueda empírica en dic-2017 y en cada mes 2017–2024 | Otros cortes | L y C horarios son aproximaciones cuando el FP real varía dentro del tramo | A |
| D-08 | 2026-10-02 | Código canónico de barra: Ñ→N (20 barras desde 2023-06) y alias LAMPA 23 kV (2024-05) | Períodos complementarios sin superposición | No unificar | Evita contar barras renombradas como nodos nuevos | A |
| D-09 | 2026-10-02 | Ventana 2017–2025, frecuencia anual | Originales disponibles desde 2017-01. Faltan 2015–2016 | 2015–2024 como el artículo | Primeras entradas elegibles desde 2019, con 2 años previos como mínimo | A |
| D-10 | 2026-10-02 | Universo de instalaciones: SEA, cartas CEN, SNIFA, operadores y directorios (DC Atlas, Inflect, Data Center Map en Wayback) | Data Center Map listaba 7 centros en Santiago en 2016 y 11 en 2022 | Solo Data Center Map, como el artículo | Inventario más completo. La exhaustividad de salas urbanas pequeñas sigue sin acreditarse | A |
| D-11 | 2026-10-02 | Fecha de tratamiento: G_doc = año de la primera operación documentada; G_min = año del límite inferior como sensibilidad | Intervalos amplios (p. ej., ODATA ST01: mayo 2021 a nov 2023) | Fijar un mes probable | La incertidumbre de G se mantiene visible | A |
| D-12 | 2026-10-02 | Expansiones, cambios de titular y cambios de nombre no son entradas | Protocolo y artículo | — | Quilicura, Pudahuel y Colina-1 quedan con presencia previa | A |
| D-13 | 2026-10-02 | Unidad principal: distrito censal 2017. Comuna y entorno de nodo (2 y 3 km) como alternativas | Diagnóstico de unidades (resultados/diagnostico_unidades.json) | Zona censal (solo urbana y sin precios propios), subestación por conexión documentada | Es la unidad más cercana al sector censal; separa Colina-3 de Colina-1 | A |
| D-14 | 2026-10-02 | Exclusión: unidades con operación previa a 2019 o con instalaciones de fecha ambigua | Regla del artículo (p. 9) | Tratar como controles | Pocos controles urbanos en la zona central | A |
| D-15 | 2026-10-02 | Panel de barras balanceado (cobertura ≥ 0,9 en los 9 años); promedio simple entre barras de la unidad. Variante no balanceada | 194 barras RM balanceadas | Incluir nodos nuevos (artículo) | El panel balanceado evita cambios de composición; la variante no balanceada se aproxima al artículo | A |
| D-16 | 2026-10-02 | Covariables Censo 2017: log población, log viviendas, % inmigrantes, % pueblos originarios, % de viviendas con materialidad aceptable | Capas INE. No contienen ingreso ni escolaridad por distrito | CASEN comunal (no representativa) | Sustitución conceptual: el «% blanco» y el ingreso del artículo no tienen análogo | A |
| D-17 | 2026-10-02 | Emparejamiento: probit, 10 vecinos con reemplazo, exclusión fuera de soporte y peso 1/m por copia | FICHA_ARTICULO | Pesos de frecuencia | Comprobado: el TWFE ponderado coincide con el de controles únicos sin ponderar (0,439277) | A |
| D-18 | 2026-10-02 | Estimadores: TWFE, Sun y Abraham (fixest, referencia t = −1) y Callaway y Sant'Anna (nunca tratados, base variable, implementación propia) | Artículo, pp. 11–12 | Paquete `did` (no instalado) | CS y SA coinciden sin covariables, como se espera | A |
| D-19 | 2026-10-02 | Inferencia: conglomerados por unidad e inferencia por aleatorización (2.000 asignaciones de los G observados) | 2–3 tratados: los errores por conglomerado no son fiables | Bootstrap salvaje (no instalado) | Los p de aleatorización son la referencia de incertidumbre | A |
| D-20 | 2026-10-02 | Pruebas de exposición: controles a ≥ 5 km de cualquier instalación; correlación previa (2017–2018, mensual) < 0,5 con el promedio de tratados | Artículo, p. 18 | Exclusión por subsistema SD4 (solo un día de evidencia) | Se añadieron tras ver el resultado principal, como robustez prevista por el artículo. No se eligieron por su signo | D |
| D-21 | 2026-10-02 | Dejar fuera una unidad tratada a la vez | Solo 3 tratados | — | Muestra la dependencia de cada unidad | D |

## Decisiones no adoptadas y pendientes

- No se fijó un mes de operación para ODATA ST01, Microsoft SCL03, Cirion SAN2 ni Scala Huechuraba sin una fuente primaria.
- No se usó la conexión eléctrica documentada como unidad principal. Solo existe para algunos casos (Ascenty y Microsoft en S/E Chacabuco; Cirion y Scala en S/E Quilicura; EdgeConneX en S/E Las Canteras) y no para el universo de controles.
- No se estimaron efectos con frecuencia mensual. El artículo usa frecuencia anual, y aumentar la frecuencia no añade tratamientos independientes.


## Cierre analítico del 9 de octubre de 2026

Todas las decisiones siguientes son posteriores a observar resultados (D). Las reglas de esta revisión se guardaron antes de los nuevos contrastes en `resultados/cierre_socher_20261009/REGLAS_REVISION.txt`.

| Id | Decisión | Motivo y alcance | A/D |
|---|---|---|---|
| D-22 | Conservar panel y matching del 05/10, con Lampa 2022; calcular 2023 en idéntica muestra | Aislar cambio de fecha de cambios de barras y matching; no seleccionar por signo | D |
| D-23 | Comparar post con promedio del pre propio de cada cohorte, preservando ponderación post | Diagnóstico descriptivo, no nuevo efecto causal; evita mezclar cohortes de horizontes distintos | D |
| D-24 | Descomponer 2020-2021 por unidad, mes y componentes; revisar precios originales del día de mayor C promedio de agosto | Comprueba origen numérico y muestra de precios; no identifica por sí sola contingencia física | D |
| D-25 | Informar singularidad del test previo completo y test exploratorio de ventana común | Covarianza de 12 restricciones tiene rango 5; ventana común −4,−3,−2 tiene rango 3. Inferencia convencional no resuelve tres tratados | D |
| D-26 | Separar apertura, autorización, energización, MW TI, MW eléctricos, MVA y previsión | No existe serie histórica homogénea de dosis por instalación en las fuentes revisadas; no forzar regresión por MW | D |
| D-27 | Corregir solo copia auditada del registro CNE Lo Espejo Data Center SpA | Carta OP02215-26 identifica titular de ODATA ST02; la atribución previa GTD no está respaldada. Original conservado | D |
