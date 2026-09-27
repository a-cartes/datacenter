# ODATA ST01: conexión histórica y mediciones

Fecha de revisión: 27 de septiembre de 2026. No se consultaron resultados de precios ni se estimó un efecto causal. Los archivos originales y el protocolo v8 permanecen intactos.

## Resultado útil para la identificación

La conexión que debe investigarse para la apertura de 2022 **es anterior al conjunto Nueva Lampa J9–Lampa JT5/ET5**. La DIA identifica una primera alimentación por la «línea Batuco», con empalme frente al predio. Un plano primario de S/E Batuco identifica un alimentador homónimo, N°22, interruptor 52D22, asociado a la barra principal N°3 de 23 kV. Esta coincidencia permite dirigir la búsqueda, pero **todavía no prueba el empalme efectivamente utilizado por ODATA ni su fecha de toma de carga**.

El plano de Nueva Lampa de julio de 2024 rotula el destino de J9 como **futuro paño JT5, transformador N°5 de S/E Lampa**. Por tanto, las mediciones actuales de esos puntos no deben trasladarse retrospectivamente a 2022. Nueva Lampa J9 y Lampa JT5 son extremos de una misma conexión proyectada, no dos cargas independientes.

## Inicio de operación y conexión de distribución previa

La carta ODCH-ST01-061-2022, emitida el 18 de agosto de 2022 y presentada a la SMA, declara el **1 de agosto de 2022 como inicio de la fase de operación** del proyecto RCA 098/2021. El original se conserva en `../entrada/fuentes/SMA_carta_inicio_operacion_ODCH_ST01_061_2022_original.pdf`; expediente SNIFA 1005711, UF20619. Es una fecha declarada del proyecto, no una certificación de primera energización, demanda positiva o carga de servidores. La carta no identifica empalme, alimentador, potencia ni medidor.

La consultora GridEnergy informa, en su [experiencia 2020–2021](https://gridenergy.cl/wp-content/uploads/2025/01/experiencia-gridenergy.pdf), PDF p.4, la gestión y tramitación de un **empalme de distribución de 6,5 MW con Enel Distribución para ODATA Chile, mediante Anabática**. En la misma página distingue estudios y tramitación de otra conexión de 30 MW. Se conserva el PDF original, su hash y una imagen de la página revisada. Es una declaración de servicios de la propia consultora; no es acta del empalme construido, no nombra Batuco y no acredita 6,5 MW de carga realizada. Permite dirigir una solicitud documental específica a ese expediente de distribución, en lugar de asumir que el proyecto posterior de 30 MW abasteció la apertura.

## Cadena inicial candidata

1. **Campus y acometida propuesta.** DIA 2020, capítulo 1, PDF p.31 (numeración impresa 1-18), sección 1.4.1.13: el edificio ST01 se conectaría a la línea Batuco que pasa por Av. Eduardo Frei Montalva, con empalme aéreo y acometida subterránea hasta un cubículo de medición. La declaración no nombra el socket, la barra ni la fecha realizada. Fuente archivada por el equipo documental en `../entrada/fuentes/SEA_DIA2020_Cap1.pdf`.
2. **Alimentador homónimo.** [InfoTécnica, documento 315338 de S/E Batuco 678](https://api-infotecnica.coordinador.cl/v1/subestaciones/678/documentos/315338/), subido el 4 de julio de 2022: lámina 1 `DU-BATUCO-110_23_12KV- LAM.01.pdf`, plano CHI-28926, sello revisión C del 11 de noviembre de 2020. Se observa «ALIMENTADOR N°22 BATUCO», interruptor 52D22, acceso a la barra principal N°3 y barra auxiliar, transformador N°3 y conexión superior al sistema de 110 kV. El sello dice emitido para revisión; la fecha de carga en InfoTécnica no certifica la ejecución ni la vigencia continua del esquema.
3. **Identificadores actuales.** [Elementos de S/E Batuco](https://api-infotecnica.coordinador.cl/v1/subestaciones/678/elementos/): paño D22 id29053, `PA061T0835SE005T0835`; BP3 23 kV id680, `BA07T0835SE005T0835`; BP1 110 kV id674, `BA01T0835SE005T0835`; BP2 110 kV id675. Son identificadores consultados en 2026; la coincidencia de nombre no demuestra continuidad histórica ni permite elegir automáticamente BP1 como barra causal.
4. **Medición.** El catálogo completo del 24 de septiembre de 2026 no contiene un socket dedicado ODATA en Batuco. `BATUCO_023_ET3_CHL` figura como transformador 3, no consumo exclusivo del campus. Su serie no fue extraída en esta revisión porque no se ha cerrado la pertenencia histórica del campus y del punto. No se suma ni se atribuye la demanda total del transformador a ODATA.
5. **Precio.** El panel v8 no incluye etiquetas Batuco. Antes de estimar hará falta homologar una barra pertinente en los archivos fuente y cerrar el empalme y su fecha. La selección de la barra no puede fundarse en el resultado de sus precios.

La segunda alimentación propuesta desde Lampa 23 kV, descrita en la DIA y en la consulta de pertinencia de octubre de 2023, se conserva como ruta distinta. «ST02» dentro de esos documentos de Lampa es un edificio del mismo proyecto y no debe confundirse con el campus comercial ODATA San Bernardo.

## Conexión posterior y por qué no sumar puntos

[InfoTécnica, Nueva Lampa documento 433735](https://api-infotecnica.coordinador.cl/v1/subestaciones/2211/documentos/433735/), archivo de agosto de 2024, plano `CHI-28840-002-NL_7.pdf`, sello 15 de julio de 2024: J9 sale por cable subterráneo hacia «S/E Lampa (FUTURO), a paño JT5, transformador N°5, CHI-33461-001». La leyenda identifica el proyecto ODATA y coordina su puesta en servicio con DS171. Se verificaron la lámina completa y los detalles ampliados.

El catálogo de sockets identifica `LAMPA_220_JT5_ODT`, `LAMPA_023_ET5_ODT` y `NUELAMPA_220_J9_ODT`, todos con coordinado ODATA. La asociación ET5–lado de baja de T5 es nominal por denominación, tensión y proyecto; falta el plano específico CHI-33461-001 o una ficha de conexión para certificarla. Se mantienen los tres puntos separados incluso cuando sus valores son cercanos.

El [informe diario del 6 de julio de 2025](https://www.coordinador.cl/wp-content/uploads/2025/07/Informe-diario-06-07-2025.pdf), PDF p.24, sección 4.3, registra a las 20:05 primera energización de un transformador 220/23 kV de 60 MVA, ET5 y barra de 23 kV en Lampa, empresa STS y centro de control STM. El acto se transcribe como energización del equipo; **no acredita apertura del campus ni primera demanda de ODATA**. El informe no imprime NUP2129. La documentación CNE revisada por el equipo de diseño describe ODATA con 50 MVA y período de pruebas ya iniciado antes del 30 de abril de 2025. Esos documentos deben conciliarse antes de asignar identidad y fecha de evento; período de pruebas y primera energización tampoco son necesariamente el mismo hito.

## Cobertura reproducida

Se verificaron los hashes de los 40 extractos ya archivados de mayo de 2023 a agosto de 2026 y sus manifiestos. Las 120 combinaciones mes–punto contienen 128.736 registros. La comparación con los totales v7 arroja diferencia máxima 0 kWh en D y 4,45 × 10⁻¹⁶ kWh en R, por representación numérica. No hay duplicados de la clave punto–fecha local–fecha UTC dentro de cada mes.

| Punto | Primer mes con registros en los archivos revisados | Último mes | Meses con registros | Registros |
|---|---|---|---:|---:|
| Nueva Lampa J9 | Mayo de 2025 | Agosto de 2026 | 16 | 46.848 |
| Lampa JT5 | Junio de 2025 | Agosto de 2026 | 15 | 43.872 |
| Lampa ET5 | Agosto de 2025 | Agosto de 2026 | 13 | 38.016 |

Los meses previos sin esos identificadores no equivalen a consumo cero del campus. La primera observación no se interpreta como fecha de entrada. Este examen no afirma ausencia en archivos anteriores a mayo de 2023 ni en otros sockets.

Los canales originales `kWhD` y `kWhR` permanecen separados. El catálogo de 2026 llama retiro a R en JT5 y a D en ET5/J9, mientras las cantidades observadas son mayoritariamente D en los tres puntos. No se impone retrospectivamente esa polaridad actual ni se calcula demanda neta del campus. Los campos `DATETIME` y `UTCDATETIME` se preservan como etiquetas impresas; no se realiza unión horaria con precios ni conversión entre regímenes.

Para dejar visible la escala de la medición sin confundirla con carga incremental: en enero de 2026, las sumas D de JT5, ET5 y J9 son respectivamente 2.369.363, 2.359.074 y 2.365.819 kWh (redondeadas). Son tres observaciones de la conexión; **no se suman**. Tampoco demuestran cuánto consumo era nuevo y cuánto pudo trasladarse desde otra alimentación.

## Archivos y reproducción

- `resumir_mediciones_odata.py`: reconstrucción desde los extractos originales, lectura del catálogo completo y reconciliación independiente con v7.
- `cobertura_canales_odata_mensual.csv`: 120 filas, ausencias explícitas y canales D/R separados.
- `canales_odata_diarios.csv`: 1.341 filas punto–día impreso; conserva días de longitud distinta sin convertirlos a un día físico de 24 horas.
- `catalogo_sockets_lampa_odata.csv`: extracto del catálogo completo para Lampa, ODATA y Batuco, con hoja y fila original.
- `mapa_conexion.csv`: afirmaciones documentales, vigencia observada y límites de identificación.
- `verificacion_mediciones.json`: hashes y controles.
- `fuentes/`: respuestas públicas de InfoTécnica y documentos originales. Las imágenes y textos extraídos son ayudas de revisión, no nuevas fuentes.

Ejecutar con el Python del proyecto: `.venv/bin/python SOCHER_2026_v8_panel_causal/investigacion_odata_20260927/medicion/resumir_mediciones_odata.py`.

## Documento que aún falta

No se localizó en las fuentes públicas revisadas un acta o constancia de Enel que vincule la apertura de agosto de 2022 con el empalme efectivamente ejecutado. La pieza concreta es el **acta de conexión/energización y recepción del empalme inicial de distribución de ODATA ST01, en Av. Eduardo Frei Montalva 17.400, asociado a la tramitación de 6,5 MW**, o documentación equivalente. Debe contener:

- Identidad del proyecto y número de cliente, empalme o expediente de Enel.
- Fecha efectiva de conexión y, por separado si existe, inicio de suministro medido.
- Nombre/código del alimentador, subestación y nivel de tensión vigentes en 2022.
- Número de serie del medidor y eventuales reemplazos; historial de facturación o intervalos medidos si es público o se obtiene con autorización.

Para cerrar específicamente la ruta candidata hace falta que esa evidencia enlace el campus con el alimentador Batuco N°22/52D22, o que identifique otro alimentador real. El nombre de la línea en la DIA, la fecha de operación de la carta SMA y el plano homónimo de S/E Batuco son tres piezas distintas; todavía no constituyen ese enlace realizado. Un certificado interior aislado tampoco demostraría por sí solo el alimentador de suministro o la fecha de toma de carga.

Se revisaron el expediente público SNIFA 1005711 (carta y comprobante), DIA/pertinencia archivadas, planos y API de InfoTécnica, el catálogo actual completo y búsquedas específicas de ODATA con empalme, Enel, energización, Batuco y medidor. La falta de hallazgo no demuestra inexistencia del documento. No se amplió la descarga de catálogos ni de mediciones históricas nacionales. El registro acotado de la búsqueda está en `busqueda_empalme_2022.csv`.

La pieza faltante debe resolverse antes de presentar el nodo candidato como tratamiento causal observado. No se estima un efecto ni se elige la barra por su comportamiento de precios.
