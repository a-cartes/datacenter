# Mediciones de carga y correspondencia temporal

La capa de carga contiene **67.384 observaciones medidor × 15 minutos** de Las Canteras en 2024. A partir de HT1 y HT2 se construyen **7.319 bloques de cuatro etiquetas**, equivalentes a una hora de energía. Cubren **305 fechas locales**. Los archivos se publican en CSV comprimido y Parquet, con los mismos campos y registros.

Esta capa todavía **no está unida a los precios barra × hora**. La unidad, duración y polaridad de HT1/HT2 están documentadas, pero falta conciliar la convención temporal de publicación de las dos fuentes.

## Alcance y trazabilidad

| Tabla | Clave | Contenido |
|---|---|---|
| `tablas/carga_medidor_15min` | `medidor_id`, `etiqueta_utc` | Canales D y R, etiquetas temporales originales, conversiones y procedencia de cada fila |
| `tablas/carga_campus_hora` | `centro_id`, `punto_medida_id`, `hora_utc_etiqueta` | Agregado HT1+HT2 de cuatro etiquetas, con conteos y estado del reloj |

`centro_id` y `campus_grupo_id` conservan `EDGE_COLINA`, identificador del registro multicentro anterior. El nombre `carga_campus_hora` indica el campus al que se vincula el punto de medida. **La variable mide los dos transformadores seleccionados, no el consumo total del campus**. La columna `representa_consumo_total_campus` lo declara expresamente.

La entrada es `SOCHER_2026_v3/consumo/las_canteras_transformadores_15min_2024.csv.gz`. Se cotejan sus 67.384 filas contra los doce extractos mensuales previamente conservados. Las huellas de los extractos mensuales se verifican contra los manifiestos de extracción v3. Los archivos nacionales ZIP no se vuelven a recorrer ni se descargan en este paso. Las huellas de esos ZIP se conservan como antecedentes previamente registrados, sin presentarlas como nuevas verificaciones.

Cada fila conserva el ZIP y miembro de origen, archivo y SHA-256 de ambos extractos y número de fila en los CSV descomprimidos, incluyendo la cabecera en el conteo. Los campos originales `DATETIME`, `UTCDATETIME`, `kWhD`, `kWhR` y metadatos permanecen como texto literal. Los campos numéricos y temporales derivados son adicionales. El diccionario completo está en `documentacion/diccionario_mediciones.csv`.

## Energía y polaridad

Los archivos originales declaran kWhD y kWhR. La configuración y actas de auditoría de HT1 y HT2 documentan intervalos de 15 minutos y delivered como retiro, received como inyección. Las conversiones son:

- Potencia media de un intervalo de 15 minutos: **kWh / 250 = MW**.
- Energía de cuatro intervalos completos: **suma de los cuatro kWh**.
- Potencia media del bloque de una hora: **kWh sumados / 1.000 = MW**.

No se aplican multiplicadores adicionales PT/CT a las energías publicadas. La clasificación histórica y los parámetros de los equipos no demuestran por sí solos que nada cambió durante 2024.

HT1 y HT2 aportan **29.276 observaciones cada uno**. Sus canales R son cero en todos los intervalos observados. La suma principal exige ambos canales D presentes en la misma etiqueta UTC y cuatro etiquetas completas por hora. No se promedian horas parciales como si estuvieran completas.

HT3 aporta **8.832 observaciones de octubre a diciembre**. Sus canales D/R permanecen separados, con `estado_polaridad=HT3_ORIENTACION_PENDIENTE`; `retiro_validado_kwh` es nulo. HT3 no se añade ni se resta a HT1+HT2. Las líneas H1–H4 son tránsito y quedan fuera de esta capa de consumo para evitar doble conteo. Dataluna Norte 2020–2022 permanece fuera porque unidad, signo y correspondencia con el campus requieren documentación histórica adicional.

Fuentes de la decisión: [memo de identidad y unidades](../../SOCHER_2026_v3/mapeo/Memo_mapeo_electrico_y_unidades.md), [apéndice histórico HT1/HT2](../../SOCHER_2026_v4/eventos/Apendice_configuracion_HT1_HT2.md) y sus originales preservados. El [Documento Técnico del CEN de 2021](https://medidas.coordinador.cl/public/DOCUMENTACION/NORMATIVA/Documento%20T%C3%A9cnico%20Sistema%20de%20Medidas%20de%20Energ%C3%ADa%202021.pdf), páginas 8–9, es el antecedente normativo de unidades e integración.

## Reloj y horario estacional

`UTCDATETIME` es la etiqueta UTC explícita del publicador. No se deriva UTC a partir de una hora local ambigua. Las diferencias entre ambas etiquetas son −180 y −240 minutos, y **todas las observaciones presentes coinciden con America/Santiago**. `YEARX`, `MONX`, `DAYX` y `HOURX` también coinciden con `DATETIME`.

La concordancia de zona horaria no resuelve el inicio o fin del intervalo. La página 3 de las actas HT1/HT2 indica primer período diario a las 00:15, mientras el CSV publicado empieza con etiqueta 00:00. No se ha acreditado el diccionario que explica esa relación. Por ello:

1. No se desplazan las observaciones automáticamente 15 minutos.
2. La agrupación usa el piso de la etiqueta UTC y exige minutos 00, 15, 30 y 45. `hora_utc_etiqueta` designa ese bloque contable, **no un comienzo físico certificado**.
3. `sentido_etiqueta_inicio_fin=NO_ACREDITADO` y `enlace_precio_habilitado=false` se conservan en ambas capas.
4. Las etiquetas de precios 1–25 no se convierten mediante `hora−1` ni se igualan automáticamente a `HOURX`. Una unión requiere verificar su correspondencia, días de 23/25 horas y el régimen de publicación de precios.

El 8 de septiembre de 2024 se conservan 23 horas locales observadas, sin inventar la hora 00 ausente por el cambio horario. Enero y abril no tienen HT1/HT2 en los extractos reales definitivos. Abril contiene el otro cambio horario en precios, pero no hay mediciones de estos transformadores para verificarlo aquí.

## Faltantes, ceros y comprobaciones

La tabla horaria incluye solamente bloques presentes. Los meses ausentes se documentan en `controles/cobertura_mediciones_mensual.csv`: el conteo de registros es cero y la energía permanece nula. **No se rellenan ausencias con consumo cero**. Febrero y marzo sí contienen mediciones cero: equivalen a **1.440 horas observadas**. La ausencia o primera presencia de un socket no se interpreta como cierre, inauguración ni fecha de tratamiento.

Los controles ejecutados comprueban claves únicas, valores no negativos, cuatro intervalos completos por hora, igualdad de campos originales entre extractos, conservación de energía y lectura posterior del Parquet. También reproducen los totales diarios y mensuales v3 y las ventanas de HT1+HT2 v4. Junio se contrasta con las **5.760 filas HT1/HT2 de la reextracción original v4**. Estas verificaciones prueban consistencia entre representaciones de los mismos datos, no una medición externa independiente ni la causa de los cambios de carga.

El informe ejecutado queda en `controles/verificacion_mediciones.json`. Registra versiones del entorno, huellas, diferencias numéricas, procedencia y límites. El script reproducible es `scripts/construir_mediciones.py`. Ejecutarlo desde la carpeta del proyecto con `.venv/bin/python SOCHER_2026_dataset/scripts/construir_mediciones.py` reconstruye únicamente esta capa a partir de los extractos conservados.
