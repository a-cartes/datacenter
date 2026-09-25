# Del dataset a la evaluación de impacto

El panel es la organización de los datos. El ATT es el efecto medio sobre las unidades tratadas que se quiere estimar. DiD y sus extensiones proporcionan comparaciones bajo supuestos; un estudio de eventos examina la dinámica relativa al tratamiento. El análisis de spillovers añade respuestas por exposición a otras intervenciones. No son cinco resultados que deban producirse automáticamente por disponer de muchas filas.

La versión inicial del dataset integra evidencia observada, conserva incertidumbres y permite auditar la futura muestra. No certifica una muestra causal ni convierte los hitos documentados en tratamientos exógenos.

## Identidades y resultado

- La clave de observación es `observacion_id`, definida por `barra_id`, fecha y etiqueta horaria original. Los precios no se replican por cada consumidor asociado.
- `barra_id` conserva la combinación histórica de etiqueta de precio y código oficial. Los cambios de código y de denominación quedan separados hasta demostrar continuidad física. El número de claves no se interpreta como centros independientes.
- Los centros y campus tienen claves distintas. Las fases del mismo campus y los centros que comparten barra deben conservar su dependencia y sus exposiciones conjuntas.
- El resultado principal candidato es el diferencial `precio_barra − precio_Quillota110`. Se conserva la alternativa frente a Quillota 220. Son diferencias de costos marginales publicados en USD/MWh, no tarifas pagadas ni un componente oficial aislado de congestión.
- La respuesta causal de la referencia forma parte del efecto relativo. Una unidad empleada para representar la evolución sin intervención cumple una función diferente y requiere una justificación de comparación.

## Reloj y cobertura

La fecha y `hora_etiqueta` se emparejan entre precios de la misma publicación. No se traducen automáticamente a UTC. Se conserva la hora adicional de abril. `t_dia` cuenta días de calendario desde el 1 de enero de 1970; por tanto, un vacío entre febrero y abril no se comprime como si fueran días consecutivos.

El panel diario es una agregación descriptiva de etiquetas publicadas. Sus medias generales incluyen filas provisionales y marcadas; los campos `diferencial_estricto_q110/q220_usd_mwh` solo tienen valor si todos los pares esperados de ese día cumplen la regla estricta de calidad. Los conteos permiten distinguir ambas muestras. Una media diaria no corrige por sí sola la convención horaria ni certifica que cada etiqueta represente la misma duración. Al unir precios y medidores se debe conciliar UTC/local, inicio o final del intervalo, cambios de hora, polaridad y unidades.

La cobertura de doce meses es una tabla de conteos para localizar vacíos. Cero registros no significa precio cero, consumo cero ni inexistencia del nodo. El panel observado no se completa con valores imputados para conseguir balance. Un estimador que elimina automáticamente unidades incompletas cambiaría la muestra y esa pérdida debe documentarse.

## Variables de tratamiento

`fecha_tratamiento_causal`, `cohorte_g_dia`, `tratado_it`, `post_evento` y `tiempo_evento_dias/horas` quedan nulos mientras no exista una asignación analítica validada por instalación, fase y resultado. Las fechas administrativas y las mediciones observadas están en el registro de hechos.

El código `g = 0` se reservará exclusivamente para un grupo realmente documentado como no tratado dentro del diseño elegido. Una instalación con historia desconocida no pertenece a ese grupo. Ser aún no tratado también requiere una historia verificada y atención a la anticipación y exposición por otras entradas.

La primera adopción no resume automáticamente ampliaciones, rampas de carga o cambios de suministro. Un estudio escalonado convencional exige definir qué intervención permanece activa y qué hacer con nuevas fases. Si dos entradas son inseparables sobre la misma barra, no se pueden atribuir sus efectos individualmente solo duplicando sus filas.

El tiempo de evento se calcula como diferencia en una escala temporal validada. No se obtiene restando cadenas YYYYMMDD ni números que concatenan fecha y hora. La versión diaria de la cohorte debe usar la misma escala que `t_dia`; la versión horaria necesita primero un reloj conciliado.

## Spillovers y variables de control

Las conexiones documentadas son antecedentes para construir la exposición. No constituyen todavía una matriz de efectos eléctricos. Faltan vigencias operativas, sentido del mecanismo y, cuando corresponda, pesos basados en la red. Una conexión no observada se clasifica como desconocida, no como exposición cero.

`exposicion_red` permanece nula. Una distancia entre comunas no reemplaza un vínculo eléctrico. Las respuestas comunes en precios pueden cancelarse en un diferencial, por lo que la exposición debe definirse para el resultado pertinente.

Las variables de operación, clima, generación y red se incorporarán con reloj y fuente documentados. Antes de usarlas como controles se distinguirán perturbaciones previas/exógenas y mecanismos posteriores del tratamiento: controlar indiscriminadamente carga, despacho o flujo que el propio proyecto modifica puede cambiar el efecto estimado.

## Condiciones de una exportación para estimación

Una muestra de estimación requiere especificar resultado y referencia, historia de intervención, unidades y períodos de comparación, anticipación, exposición a otras entradas, calidad de enlace y soporte previo/posterior. Se deben justificar también ponderaciones y la inferencia con dependencia temporal y entre barras.

La marca `par_precio_estricto_q110/q220` solo señala que los dos precios tienen homologación mensual exacta, carecen de marcas de revisión y no son el mismo nodo de referencia. No significa que el par sea un control válido ni que identifique un efecto.

La marca `elegible_estimacion_causal` es falsa en esta versión por falta de cierre de la muestra. No se ha generado un ATT ni un DiD sobre fechas inferidas. Tampoco se fija un número mágico de horas o centros que garantice identificación.

## Fuentes primarias consultadas

La documentación de los autores de [att_gt](https://bcallaway11.github.io/did/reference/att_gt.html) define el formato largo, primera fecha de tratamiento, grupo no tratado, grupos todavía no tratados y tratamiento del panel desbalanceado. Consultada el 25 de septiembre de 2026. Se usa para evitar codificar desconocidos como grupo no tratado; no implica que debamos usar ese programa ni que sus supuestos se cumplan.

[Butts, Difference-in-Differences with Spatial Spillovers](https://www.kylebutts.com/papers/spatial-spillovers/) explica que la exposición de comparadores y de las propias unidades tratadas modifica la comparación causal. Consultado el 25 de septiembre de 2026. Su argumento motiva conservar conexiones y exposiciones por separado de la clasificación administrativa.
