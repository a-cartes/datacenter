# Ampliación del dataset 2020–2026

Artículo: **Entrada de centros de datos y diferenciales nodales de costo marginal: evidencia causal para Chile**.

Esta ampliación reúne **3.411.527 registros horarios de precios definitivos**, del **1 de enero de 2020 al 18 de septiembre de 2026**, para el mismo artículo del curso de datos de panel y evaluación de impacto y de SOCHER 2026. La entrega corresponde a datos y controles de calidad. Todavía no contiene una estimación causal de la entrada de centros de datos.

## Qué contiene la entrega

El archivo principal es `SOCHER_2026_v7_2020_2026/entrega/Dataset_precios_barra_hora_2020_2026.csv`. Incluye los precios definitivos seleccionados, sus identificadores originales, el régimen de publicación y diferenciales descriptivos respecto de Quillota 110 y 220. Tiene **31 variables**. Se acompaña de archivos CSV por año, una copia comprimida gzip y una copia Parquet.

La observación es una **etiqueta de barra × fecha × hora de la fuente**, dentro de un mes y régimen. En el régimen moderno, la observación horaria reúne cuatro precios de 15 minutos, únicamente cuando están presentes los minutos 0, 15, 30 y 45. El número de filas no equivale al número de unidades independientes para inferencia: hay dependencia temporal y eléctrica entre observaciones.

Las 83 claves históricas de barra documentadas en una versión anterior **no eran 83 centros de datos** y tampoco acreditaban 83 activos físicos estables a lo largo del tiempo. La ampliación vuelve a contar las etiquetas y sus identificadores en cada mes. De igual manera, los 30 sockets de la capa de mediciones no representan 30 centros de datos. Algunos son transformadores o circuitos de tránsito de una misma infraestructura.

## Cobertura y estado de verificación

Los conteos siguientes proceden de la entrega final y su verificación local del 27 de septiembre de 2026. Se integraron las **82 particiones DEF** previstas: 55 históricas y 27 modernas. Julio de 2024 aparece en ambos grupos porque cambia el régimen el día 15; no se duplican las fechas de observación.

| Componente | Período o corte comprobado | Registros definitivos | Estado |
|---|---|---:|---|
| Precios históricos DEF | Enero de 2020–14 de julio de 2024; 55 particiones mensuales | 2.240.276 | Integrado y verificado |
| Precios modernos DEF | 15 de julio de 2024–18 de septiembre de 2026; 27 particiones | 1.171.251 | Integrado y verificado |
| CSV principal de precios y diferenciales | Unión de los dos regímenes, 31 variables | 3.411.527 | Todas las celdas CSV/Parquet verificadas |
| Precios PRE de septiembre de 2026 | Días 1–23 y HRA=0 del día 24 | 34.839 horas de fuente en el extracto auditado | Archivo separado; no completa el DEF |
| Mediciones de 15 minutos | Mayo de 2023–agosto de 2026; 40 fuentes mensuales, 30 sockets seleccionados | 1.862.581 | Auditado localmente |
| Agregado HT1 + HT2 | Febrero de 2024–agosto de 2026; enero y abril de 2024 ausentes | 21.912 horas de etiquetas | Auditado; enlace temporal a precios pendiente |
| DATALUNA 2020–2022 | Septiembre de 2020–diciembre de 2022 | 20.447 valores horarios | Unidad y signo sin homologación completa |
| DATALUNA enero de 2023 | Enero de 2023 | 744 valores horarios | Unidad sin homologación completa |
| Canales de tránsito H1/H2 de TAP Libertadores | Febrero–abril de 2023 | 8.548 registros hora × canal | Signo original conservado; no consumo total de campus |
| Adquisición y extracción en GitHub Actions | Septiembre/octubre de 2025 y enero/febrero de 2026 | 714.240 intervalos; 178.560 horas | Cuatro jobs Linux aprobados e importación verificada |
| Reconstrucción completa en GitHub Actions | Linux; código de v0.2.0 | 3.411.527 filas y 258 insumos | **Completada; CSV idéntico al publicado** |

La fuente DEF moderna de septiembre de 2026 termina el **18 de septiembre, HRA=23, MIN=45**. PRE termina el **24 de septiembre, HRA=0, MIN=45**: no cubre todo el día 24. Estas expresiones conservan el reloj publicado; no certifican un instante UTC. La fecha de revisión es el 27 de septiembre de 2026. No se crean observaciones para fechas futuras ni se rellenan los días pendientes con ceros o PRE.

| Año | Registros DEF | Meses observados | Etiquetas de barra distintas en el año |
|---|---:|---:|---:|
| 2020 | 480.991 | 12 | 55 |
| 2021 | 482.599 | 12 | 56 |
| 2022 | 490.616 | 12 | 56 |
| 2023 | 508.138 | 12 | 58 |
| 2024 | 522.732 | 12 | 61 |
| 2025 | 537.277 | 12 | 62 |
| 2026, hasta el 18 de septiembre | 389.174 | 9 | 63 |

No hay precios nulos en las filas DEF entregadas y todas las horas modernas incluidas satisfacen el requisito de cuatro intervalos. **Eso no convierte la base en un panel balanceado.** El diagnóstico registra 504 ausencias de etiqueta frente a otras barras del mismo mes: 72 para LA_POLVORA____220 entre el 2 y el 4 de enero de 2025, y 432 para PANAMERICANA__110 entre el 1 y el 18 de agosto de 2026. Estas ausencias no se imputan ni se interpretan como entrada de un centro. También se enumeran los nueve días del 19 al 27 de septiembre de 2026 sin DEF en la selección. Una hora omitida simultáneamente por todas las barras no sería detectable usando sólo la unión de etiquetas observadas.

Las referencias Quillota 110 y 220 estuvieron disponibles sin ambigüedad para los 3.411.527 registros de esta entrega. Cada diferencial se conserva como resultado descriptivo.

## Relojes, identidades y referencias

El histórico conserva etiquetas horarias **1–25** y termina el 14 de julio de 2024. El nuevo CMg Real conserva HRA **0–24** y comienza el 15 de julio. Se mantienen columnas separadas. No se resta una unidad para unirlas y no se inventa UTC. Incluso cuando aparecen 24 etiquetas en un día, eso no prueba correspondencia automática con las horas civiles de Santiago durante cambios de hora.

`barra_mes_id` identifica un registro dentro de un mes y régimen. Los códigos físicos históricos se conservan sólo cuando existe homologación mensual exacta. ID_INFO, los nombres modernos y sus marcadores se preservan como fueron publicados; un marcador `0`, `-` o `nan` no acredita una identidad física válida. La continuidad de una etiqueta no sustituye la revisión de vigencia de la conexión eléctrica.

Entre septiembre y octubre de 2023 cambian literalmente 56 de 58 códigos históricos compartidos, con aparente incorporación de ceros. No se normalizaron para presumir continuidad física. El informe `SOCHER_2026_v7_2020_2026/auditoria/Diferencias_nemotecnico_202309_202310.json` conserva esa comparación.

Las referencias usan las etiquetas exactas `QUILLOTA______110` y `QUILLOTA______220`. Cada una exige una observación única con el mismo mes, régimen, fecha y hora, y un precio horario válido. Se entrega su precio, su identificador mensual y el diferencial **precio de la barra menos precio de referencia**, en USD/MWh. Una referencia ausente, ambigua o incompleta produce valores vacíos. No se modifica el precio original.

Quillota es una referencia descriptiva, no un control causal declarado. Puede responder al mismo choque. Un aumento común a la barra y la referencia puede cancelarse en el diferencial; el efecto sobre ese resultado sería un efecto relativo, no necesariamente el cambio absoluto del precio.

Se emplean los DEF del índice histórico. Las reliquidaciones posteriores —en particular las catalogadas para 2022— no se mezclan en esta entrega. DEF no implica selección de la revisión más reciente de cada fecha. También se documentaron diferencias entre el DEF de octubre de 2023 y una exportación local anterior. No se rellenan huecos con esa exportación de versión distinta.

## Mediciones separadas

Los cuatro CSV horarios están en `entrega/mediciones_separadas/`. D y R se mantienen separados; la energía se expresa en kWh cuando la fuente acredita esa unidad. Para HT1 + HT2, la potencia media de las cuatro etiquetas se obtiene como kWh/1000 por hora. Sólo se suman intervalos simultáneos de ambos medidores. HT3 y circuitos de tránsito se excluyen del agregado.

El agregado no certifica consumo total del campus ni vigencia permanente de la orientación de los canales. La capa de 15 minutos conserva los tiempos local y UTC explícitos y sus fuentes. El significado físico inicio/fin del intervalo sigue pendiente de conciliación con los precios. Los antecedentes DATALUNA de unidad no acreditada conservan sus valores firmados; no se llaman consumo MW homologado.

No se ha unido consumo con precios y no se convierte la primera observación de un socket en fecha de inauguración. ATT, DiD escalonado, estudio de eventos y spillovers requieren resolver la conexión centro–nodo, las fechas de tratamiento, el reloj y la exposición de los posibles controles.

## Reconstrucción desde la versión privada

El repositorio mantiene código, guías y contratos pequeños. Los CSV y el paquete de insumos se distribuyen como archivos de la versión privada **v0.2.0**, evitando duplicar datos voluminosos en el historial Git.

El archivo `Insumos_reproduccion_2020_2026.zip` contiene particiones extraídas y sus metadatos; no incluye todos los archivos nacionales originales. Permite reconstruir el CSV completo desde esas particiones. Volver a adquirir las fuentes originales es otra etapa, documentada mediante scripts, manifiestos y URLs. El portal histórico puede requerir descarga desde su interfaz cuando el acceso HTTP directo responde 403.

Desde un checkout limpio del tag publicado, con la versión de Python indicada en `.python-version`, estos comandos sirven en macOS o Linux:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
gh release download v0.2.0 --pattern 'Insumos_reproduccion_2020_2026.zip' --dir artifacts/insumos
.venv/bin/python scripts/reproducir_2020_2026.py --insumos artifacts/insumos/Insumos_reproduccion_2020_2026.zip
```

GitHub CLI debe estar autenticado con acceso al repositorio privado. No se incorporan credenciales al paquete. El wrapper comprueba el contrato en `contracts/insumos_2020_2026.json`, el SHA-256 del paquete, cada miembro y el código del constructor antes de reconstruir. Rechaza rutas externas, miembros duplicados y archivos locales diferentes. Sus controles siguen activos con Python optimizado.

Si las particiones ya están disponibles en la carpeta de trabajo, la integración local se ejecuta así:

```sh
.venv/bin/python SOCHER_2026_v7_2020_2026/scripts/construir_entrega.py
.venv/bin/python SOCHER_2026_v7_2020_2026/scripts/construir_entrega.py --verificar
```

La comparación CSV/Parquet recorre las 31 columnas en bloques de memoria. Exige igualdad de identificadores, enteros, booleanos y posiciones vacías. Para flotantes permite un error absoluto de serialización de hasta 1e-10. La concatenación de CSV anuales y la descompresión de gzip deben reproducir exactamente los bytes del CSV principal.

El informe de reconstrucción se guarda en `artifacts/reproduccion_2020_2026.json`. Los controles de datos están en `entrega/Manifiesto_entrega.json` y `entrega/Verificacion_entrega.json`. El wrapper compara además el SHA-256 del CSV reconstruido con el de la versión publicada. Los informes con fechas de ejecución no tienen que ser idénticos byte a byte entre equipos.

## Evidencia ya obtenida y pendiente

El [control posterior de descargas del 27/09/2026](integridad_descargas_20260927.md) no detectó truncación en los archivos de precios utilizados. Las tres fuentes de precios recuperadas desde transferencias interrumpidas coinciden con nuevas descargas completas. Se conservó aparte una homologación adicional de agosto de 2023, pendiente de incorporación en una próxima versión. Esta evidencia complementa la reproducción del paquete; no la sustituye ni convierte la base en una muestra causal validada.

La verificación final comparó las **31 columnas de las 3.411.527 filas**, con error numérico máximo **cero**. Los archivos anuales concatenados y el gzip descomprimido son idénticos al CSV principal. La prueba local del wrapper cubrió 14 casos con y sin Python optimizado: paquete válido y rechazo de hash incorrecto, miembro alterado, ruta externa, nombres duplicados, archivo local diferente y constructor distinto. Esas pruebas de casos controlados se hicieron en directorios temporales. Las reglas de referencia también se comprobaron ante coincidencia exacta, ausencia, ambigüedad y hora incompleta.

La adquisición y extracción de cuatro meses sí se ejecutó en Linux mediante [la matriz de tres meses](https://github.com/a-cartes/datacenter/actions/runs/36293680186) y [el job de septiembre de 2025](https://github.com/a-cartes/datacenter/actions/runs/36293933388), en el repositorio privado. Los cuatro jobs terminaron correctamente. Se comprobaron nuevamente los hashes de gzip, TSV descomprimido y resultados al incorporarlos al equipo local. El registro seguro está en `SOCHER_2026_v7_2020_2026/moderno/fuentes/ejecuciones_ci.json` e informa Ubuntu 24.04 x64, Python 3.13.15 y las dependencias efectivamente instaladas.

La **reconstrucción completa del paquete final en Linux** terminó correctamente en [GitHub Actions](https://github.com/a-cartes/datacenter/actions/runs/36295132374). Se verificaron 258 insumos y se obtuvo el CSV de 3.411.527 filas con el mismo SHA-256 de la entrega: `19bc55d1a30cc59d63c2160a494ea39a42b625cdbb5f66761c360616e3f00d0b`. Las pruebas de referencias, integridad de valores y del wrapper también aprobaron. La reconstrucción local desde el paquete produjo los mismos bytes. Esta comprobación acredita la reconstrucción desde particiones archivadas; no sustituye la validación causal ni una nueva descarga de todos los originales nacionales.

La primera ejecución remota se detuvo porque la prueba de referencias se ejecutó antes de extraer sus datos. Se corrigió el orden del workflow en `f846acae9dfb4fc67a8a9dbb1b1459771c48aff1`, manteniendo el checkout del constructor y el contrato en el tag inmutable **v0.2.0**, commit `437e6477ca67298baf64bc976ab40f0a54996213`. No se modificaron los datos publicados. La evidencia de adquisición de cuatro meses y la reconstrucción completa son comprobaciones distintas.

El CSV nuevo tampoco es una mera conversión del Excel anterior: amplía los años y las observaciones. El principal ocupa **1.212.668.988 bytes** (aproximadamente 1,21 GB); gzip, **71.073.343 bytes**; y Parquet, **55.818.438 bytes**. Los tamaños no son comparables directamente porque CSV repite texto sin compresión, Excel comprime XML y Parquet comprime por columnas. Para comparar entregas deben usarse períodos, variables y conteos. El archivo completo excede el límite de filas de una hoja de Excel; para la base íntegra conviene R, Python o DuckDB.
