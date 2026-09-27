# Dataset de precios y mediciones para el artículo SOCHER

La entrega contiene **3,411,527 registros de precio de barras seleccionadas**, desde **2020-01-01 hasta 2026-09-18**. Fecha de corte de la revisión: 2026-09-27. Se integraron 82 de 82 fuentes mensuales esperadas (55 históricas y 27 modernas). Estado: **82_fuentes_DEF_integradas**. El nombre 2020–2026 describe el período de estudio, no significa que 2026 esté completo.

## Archivo que se debe abrir

- `Dataset_precios_barra_hora_2020_2026.csv` es la base principal: una fila por etiqueta de barra, fecha y hora de la fuente dentro del régimen. CSV UTF-8, separador coma, decimal punto, encabezado y campos vacíos para datos no disponibles. Conservar códigos como texto.
- `por_anio/` contiene la misma base dividida por año, sin duplicar observaciones dentro de cada archivo. La unión de esos archivos equivale al principal.
- `Dataset_precios_barra_hora_2020_2026.csv.gz` descomprime al mismo CSV. `Dataset_precios_barra_hora_2020_2026.parquet` conserva tipos y ocupa menos espacio.
- `Diccionario_precios.csv` explica todas las variables. `Fuentes_precios.csv` relaciona cada `fuente_id` con su archivo original, derivado, hash, unidades y método.
- `Cobertura_por_anio.csv`, `Cobertura_por_mes_regimen.csv` y `Cobertura_por_mes_barra.csv` muestran la cobertura real. `Faltantes_precios_detalle.csv` identifica archivos pendientes, días ausentes hasta la fecha de corte, precios horarios inválidos y huecos respecto de etiquetas observadas en otras barras del mismo mes.

## Cómo interpretar el tiempo, el precio y la barra

El histórico termina el 14 de julio de 2024 y conserva `hora_etiqueta_historica` (1–25). El régimen moderno comienza el 15 de julio y conserva `hora_fuente_moderna` (0–24). Ambas son etiquetas originales. No se deduce UTC, no se resta automáticamente una unidad ni se unen ambas horas a mediciones. No se completa una cuadrícula artificial de 24 horas por día: los cambios de hora requieren una concordancia documental específica.

El histórico conserva el valor horario publicado. En el moderno, `precio_usd_mwh` sólo se calcula si existen los cuatro minutos 0, 15, 30 y 45; `precio_usd_mwh_media_intervalos` preserva la media disponible para auditar las horas incompletas. Un mill/kWh equivale numéricamente a un USD/MWh. El precio local moderno se conserva aparte como CLP/kWh. No se hace conversión de moneda con un tipo de cambio inventado.

Las seis columnas de referencia añaden el precio de Quillota 110 y 220, el diferencial nodo menos referencia y el identificador mensual de cada referencia. Se exigen las etiquetas exactas `QUILLOTA______110` y `QUILLOTA______220`, una sola observación con esa fecha y hora en el mismo mes/régimen y un precio horario válido. Si falta o hay más de una candidata, las tres columnas de esa referencia quedan vacías. El precio original no se modifica. Estos diferenciales son descriptivos: Quillota puede recibir el mismo choque y no se presume un control causal no afectado.

`barra_mes_id` sirve como llave dentro de cada mes y régimen. No acredita una identidad longitudinal. Los códigos históricos provienen únicamente de homologaciones mensuales exactas; los ID_INFO modernos se conservan cuando la fuente los informa. No se rellena una identidad con meses vecinos ni se presume que dos nombres iguales representen un mismo activo en todo 2020–2026. La selección reúne barras relacionadas con el diseño del artículo y sus referencias, no todos los nodos del país.

La llave de fila es `barra_mes_id`, `fecha` y la columna de hora aplicable al régimen. `version_fuente` es DEF o REAL-DEF. Los archivos PRE, cuando existen, están en `preliminares_separados/` y no complementan ni reemplazan valores de la base definitiva.

Se utilizan los definitivos del índice histórico. Existen reliquidaciones posteriores, en particular para 2022, que se inventarían separadamente y no se mezclan aquí. DEF no significa que se haya seleccionado la revisión más reciente de cada fecha.

Una comparación con la exportación local anterior encontró diferencias en octubre de 2023 aun usando códigos físicos coincidentes. Se conserva el valor de estos libros DEF y su versión, sin llenar huecos con aquella exportación. El informe `../auditoria/Comparacion_DEF_con_exportacion_local.json` documenta esa discrepancia y evita confundir cambios de versión con errores de extracción o efectos económicos.

Los faltantes respecto de la unión de etiquetas del mes son un diagnóstico de desigualdad de cobertura: no prueban que una barra existiera antes de su primera observación o después de la última. Si todas las barras omiten simultáneamente una hora, esta comparación no puede detectarla. Los días enteros ausentes se enumeran por separado. Meses posteriores a septiembre de 2026 y fechas posteriores al corte no se crean como observaciones.

## Mediciones que se entregan separadamente

`mediciones_separadas/` contiene cuatro CSV horarios y su guía específica:

- HT1 + HT2: 21.912 horas completas de etiquetas, febrero de 2024–agosto de 2026; faltan enero y abril de 2024. D y R se mantienen separados, en kWh y media MW. Se exigen cuatro pares de intervalos. HT3 y líneas de tránsito se excluyen. No representa automáticamente consumo total del campus. El archivo conserva reloj explícito y las banderas de validación pendientes.
- DATALUNA 2020–2022: 20.447 horas observadas desde septiembre de 2020, con unidad y signo histórico todavía no homologados a consumo MW.
- DATALUNA enero de 2023: 744 valores horarios originales, también sin unidad homologada.
- Canales horarios de febrero–abril de 2023: 8.548 registros hora × canal de H1/H2 de TAP Libertadores; energía rotulada kWh y signo original conservado. Son canales de tránsito, no una medición independiente del consumo de un campus.

La capa completa de 1.862.581 observaciones de 15 minutos de 30 sockets está en `../mediciones/tablas/mediciones_candidatos_15min.parquet` y `.csv.gz` desde esta carpeta. No son 30 centros de datos. Las fuentes y unidades se conservan en cada capa; el reloj físico inicio/fin y la vigencia de algunas correspondencias siguen pendientes. Los CSV de mediciones no se han unido a precios y la aparición de un socket no se usa como inauguración.

## Uso en la investigación

Esta entrega permite describir y comparar cobertura y precios. ATT, DiD escalonado, estudio de eventos y spillovers necesitan todavía fechas de entrada acreditadas, correspondencia centro–nodo vigente, diseño de comparación y validación del reloj. El CSV no contiene tratamientos inferidos, efectos estimados ni resultados causales.

## Reproducción y control

Desde la raíz del proyecto, ejecutar `.venv/bin/python SOCHER_2026_v7_2020_2026/scripts/construir_entrega.py`. Las rutas dependen de la ubicación del script. Usa sólo derivados locales; descargar las fuentes originales corresponde a los extractores históricos, modernos y de mediciones. `--verificar` comprueba SHA-256 de todos los entregables, equivalencia byte a byte CSV/gzip y concatenación anual, y todas las celdas de CSV/Parquet en bloques de memoria. La igualdad de identificadores, enteros, booleanos y posiciones vacías es exacta. Para flotantes se permite sólo un error absoluto de serialización de hasta 1e-10, sin redondear los valores de salida. `--permitir-parcial --salida entrega_ensayo` permite una revisión durante las descargas sin confundirla con la entrega completa.

La reconstrucción de este CSV es completa desde las 82 particiones Parquet preservadas y sus metadatos. El paquete de insumos de la entrega permite repetir esa reconstrucción sin descargar archivos nacionales de varios gigabytes. La adquisición original es otra etapa: conserva scripts, manifiestos y URLs verificables, y algunos archivos del portal histórico pueden requerir descarga mediante la interfaz cuando el acceso HTTP directo responde 403. No se afirma reproducibilidad automática de esa adquisición bajo todas las condiciones de red. En la publicación del repositorio, el código y las guías se mantienen en Git y los datos se distribuyen como archivos de la versión.

Este CSV no es una conversión del Excel anterior: incorpora más años, fuentes, barras y observaciones. El peso en megabytes no mide la cantidad de información comparable porque CSV repite texto sin compresión, Excel almacena XML comprimido y Parquet comprime por columnas. Para comparar entregas deben usarse los conteos, períodos y variables documentados, no sólo el tamaño del archivo. El CSV completo puede exceder el límite de filas de una hoja de Excel; para trabajar con toda la base conviene R, Python, DuckDB o Parquet.

`Manifiesto_entrega.json` registra fuentes, cobertura, hashes y versión del constructor. `Verificacion_entrega.json` contiene el resultado de los controles. Se conserva el corte del 27/09/2026; para una actualización posterior deben ampliarse explícitamente las fuentes esperadas y revisarse los nuevos períodos.
