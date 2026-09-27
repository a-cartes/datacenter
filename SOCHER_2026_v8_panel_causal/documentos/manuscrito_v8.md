# Entrada de centros de datos y diferenciales nodales de costo marginal: evidencia causal para Chile

Alan Cartes Fica · Universidad del Bío-Bío

Manuscrito de trabajo en español con resumen en inglés · Datos de panel y evaluación de impacto · SOCHER 2026 · Primera revista objetivo: *Energy Economics* · 27 de septiembre de 2026.

**Estado de la versión.** La expresión «evidencia causal» identifica el objetivo del artículo. Esta entrega desarrolla el panel y el expediente de identificación; no dispone todavía de un ATT habilitado. Introducción, datos, mecanismos y diseño están redactados. Los resultados documentales y de cobertura se distinguen de las estimaciones causales pendientes. No se ha enviado el manuscrito a revista o congreso.

## Resumen

Este trabajo investiga cómo la entrada y ampliación de centros de datos se relaciona con los diferenciales nodales de costo marginal en Chile. Se construye un panel de 142.151 filas de calendario barra–día a partir de 3.411.527 precios horarios publicados, conservados en una entrega auditada que abarca del 1 de enero de 2020 al 18 de septiembre de 2026. La estrategia distingue campus, fases, equipos, barras y vigencias para evitar que anuncios, nuevas conexiones o primeras mediciones se clasifiquen automáticamente como demanda incremental. La descripción del diferencial respecto de Quillota 110 kV utiliza 139.277 filas barra–día con 24 pares de etiquetas, excluyendo la referencia. El protocolo define efectos por cohorte y período, dinámica de eventos e interferencia eléctrica antes de estimar la nueva etapa. La revisión documental identifica hechos realizados y precisa enlaces nominales, pero mantiene separadas la validación de una obra, la naturaleza de la carga y la identificación del contrafactual. Ningún evento ni comparador queda todavía habilitado para una estimación causal. Este estado no constituye un efecto nulo y no permite concluir que los centros de datos encarezcan o abaraten causalmente la electricidad. La contribución empírica en desarrollo consiste en relacionar infraestructura digital, conexiones eléctricas y resultados nodales bajo reglas verificables de tratamiento y comparación.

**Palabras clave:** centros de datos; costos marginales nodales; diferencias en diferencias; datos de panel; redes eléctricas; Chile.

## Abstract

This paper investigates how data center entry and expansion affect nodal marginal cost differentials in Chile. We construct a panel of 142,151 node–calendar-day rows from an audited release containing 3,411,527 published hourly price records between January 1, 2020, and September 18, 2026. The design distinguishes campuses, phases, equipment, electrical connections, and their periods of validity. Announcements, connection works, and the first available measurement are not automatically classified as incremental demand. Descriptive analysis of the differential relative to Quillota 110 kV uses 139,277 node–day rows with 24 matched published time labels, excluding the reference node. The reference is not presumed to be an unaffected comparison unit. The analysis protocol specifies group-time treatment effects, event-time dynamics, and conditions for studying electrical spillovers. Documentary evidence establishes realized infrastructure milestones and nominal electrical paths, but load classifications and counterfactual comparisons remain unresolved. No event or comparison unit is yet eligible for causal estimation. This is an identification limitation rather than an estimated zero effect. The empirical contribution under development is a reproducible connection between digital infrastructure, electrical supply, and nodal outcomes that keeps event evidence separate from the assumptions required for causal interpretation.

**Keywords:** data centers; nodal marginal costs; difference-in-differences; panel data; electrical networks; Chile.

## 1. Introducción

La expansión de infraestructura digital plantea una pregunta económica localizada: ¿qué ocurre con el costo marginal de abastecer distintos puntos de la red cuando un centro de datos incorpora demanda? Una inversión puede estar situada en una comuna y conectarse a instalaciones cuyos efectos operativos atraviesan límites administrativos. La respuesta no se obtiene únicamente sumando capacidades anunciadas ni comparando precios antes y después de una inauguración. Requiere identificar qué carga cambió, en qué momento, mediante qué conexión y frente a qué evolución contrafactual.

El Plan Nacional de Data Centers 2024–2030 incorpora entre sus objetivos el desarrollo regional de esta industria y propone una herramienta territorial que reúna disponibilidad energética, suelo, conectividad y variables socioambientales. Esa propuesta sitúa la coordinación entre localización digital y capacidad eléctrica dentro de un problema público concreto. El artículo estudia una dimensión acotada de esa coordinación: la distribución espacial de costos marginales publicados, sin evaluar íntegramente el plan ni atribuirle las inversiones observadas. [Ministerio de Ciencia, 2024, objetivos y medida 1, pp. impresas 12–13](https://minciencia.gob.cl/uploads/filer_public/95/6b/956b8c9f-d937-4b4d-8f6c-a871495a52ff/plan_nacional_de_data_centers_pdata.pdf).

La pregunta de investigación se formula como un efecto relativo. El costo marginal de una barra puede cambiar por una perturbación local, por condiciones comunes de oferta o por alteraciones de red. Si la referencia también responde, el diferencial refleja ambas respuestas. La barra utilizada para expresar el resultado no reemplaza al grupo necesario para construir el contrafactual. Esta distinción tiene consecuencias tanto para la interpretación económica como para la selección de controles.

El aporte que se desarrolla tiene dos partes. Primero, organiza precios y expedientes de proyectos en unidades compatibles, manteniendo fechas y enlaces con su evidencia y vigencia. Segundo, establece una estrategia para estimar efectos cuando la adopción, la comparación y la exposición eléctrica permitan identificarlos. No se reivindica novedad por usar DiD ni se presenta una auditoría de archivos como sustituto de identificación causal. La búsqueda sectorial y la delimitación de la contribución frente a otros estudios de centros de datos deberán completarse antes de una versión destinada a revista.

## 2. Contexto institucional y mecanismos económicos

El Coordinador Eléctrico Nacional define el costo marginal considerando el costo de abastecer una unidad adicional en la barra y la operación determinada por el propio Coordinador. Se trata de una medida de valorización asociada a la operación eléctrica. En este artículo se utiliza su publicación como resultado; no se equipara con el precio contratado por un centro de datos ni con la tarifa que pagan hogares o empresas. [Coordinador Eléctrico Nacional, Costo Marginal Real](https://www.coordinador.cl/mercados/graficos/costos-marginales/costo-marginal-real/).

La hipótesis económica es que una nueva carga puede modificar la combinación de abastecimiento requerida y las transferencias relevantes en la red. La respuesta nodal dependerá de la oferta disponible, las pérdidas y las restricciones operativas. No se impone que el diferencial aumente: la referencia puede responder de otra forma y una inversión puede venir acompañada de refuerzos de conexión. Estas son posibilidades del mecanismo, no hallazgos estimados en esta versión.

Los tres tipos de intervención tienen contrafactuales diferentes. En una primera entrada se compara con ausencia de esa carga del campus. En una ampliación se mantienen las fases existentes y se pregunta por la carga incremental. En una transferencia se mantiene la demanda previa y cambia su conexión o punto de retiro. Si la conexión y la carga nueva forman un conjunto inseparable, el efecto del conjunto no puede atribuirse exclusivamente a los equipos informáticos. No se ha acreditado qué fracción de los centros estudiados sirve a inteligencia artificial, por lo que no se utiliza esa categoría como tratamiento.

El territorio pertinente para medir exposición es eléctrico. La comuna permite describir ubicación, pero no demuestra qué nodos responden ni dónde termina el efecto. Los vínculos de un diseño técnico tampoco certifican estados operativos posteriores. Se distinguen topología prevista, obra realizada y operación vigente, y se examinan las concurrencias antes de asignar un evento.

## 3. Datos y construcción del panel

### 3.1. Base congelada y alcance de cobertura

La entrega v0.2.0 conserva 3.411.527 filas y 31 columnas. El CSV y el Parquet fueron comparados en todas sus columnas y presentan igualdad de valores; su verificación registra error máximo cero en las comparaciones numéricas. La cobertura DEF seleccionada comienza el 1 de enero de 2020 y termina el 18 de septiembre de 2026. No constituye un panel balanceado ni cubre todo 2026. El estado DEF identifica la selección documental conservada, no una garantía de incorporar cualquier reliquidación posterior. [Verificación de la entrega](../../SOCHER_2026_v7_2020_2026/entrega/Verificacion_entrega.json).

| Año | Filas de precios de la base congelada |
|---|---:|
| 2020 | 480.991 |
| 2021 | 482.599 |
| 2022 | 490.616 |
| 2023 | 508.138 |
| 2024 | 522.732 |
| 2025 | 537.277 |
| 2026, hasta el 18 de septiembre | 389.174 |
| Total | 3.411.527 |

Fuente: [Cobertura por año](../../SOCHER_2026_v7_2020_2026/entrega/Cobertura_por_anio.csv). Las filas no representan intervenciones independientes.

Los precios preliminares permanecen separados y no prolongan la muestra principal. La nueva etapa conserva los originales y transforma sus representaciones en un panel analítico propio. El panel diario resultante contiene 142.151 filas y 35 columnas; el mensual contiene 4.756 filas y 38 columnas. Se conservan 64 etiquetas distintas y 266 segmentos observacionales, que no equivalen a 64 o 266 activos físicos certificados. Los archivos no tienen claves duplicadas. [Validación ejecutada del panel v8](../validacion/validacion_panel.json).

La homologación nueva de agosto de 2023 produce 53 enlaces literales entre las 58 etiquetas de ese mes y añade metadatos a 39.432 precios sin alterar sus valores. Permanecen sin correspondencia BJOSDMNA______012, BJOSDMNA______110, LA_POLVORA____110, P.HURTADO_____110 y TAP_QUILICURA_110. Los códigos se aplican solo al mes acreditado; no se transportan a otros por semejanza del nombre. [Unión validada de agosto de 2023](../panel/homologacion_agosto2023_validada.csv).

### 3.2. Identidad, calendario y agregación

Las claves distinguen campus, fase, medidor, instalación eléctrica y barra de precios. Un código mensual no constituye por sí solo una identidad física estable. En particular, el cambio literal de muchos códigos entre septiembre y octubre de 2023 requiere un puente documental; no se resuelve uniendo automáticamente cadenas parecidas. Los segmentos de registro permiten controlar esas rupturas sin fingir una continuidad que todavía no está acreditada.

El régimen histórico conserva etiquetas 1–25; el moderno conserva HRA 0–24. No se ha demostrado que las etiquetas correspondan al mismo intervalo físico mediante una simple resta. La fecha utilizada en el panel es la fecha civil publicada y no una fecha UTC construida. El cambio de régimen del 15 de julio de 2024 se registra como una ruptura que exige verificar la comparabilidad del resultado antes de utilizar ventanas causales que lo atraviesen.

La agregación diaria empareja el precio de barra y referencia en la misma fecha, régimen y etiqueta. Su resultado es la media de diferencias de esos pares, no la diferencia entre medias calculadas con horas distintas. El panel conserva los días incompletos y sus conteos. La muestra principal prevista exige exactamente 24 etiquetas únicas y conjuntos iguales dentro de cada comparación. Los días de 23 o 25 etiquetas no desaparecen de la base descriptiva; se identifican fuera de la selección principal. Esta regla controla composición de etiquetas y no certifica automáticamente su duración física.

Cada precio barra–período aparece una sola vez aunque abastezca a varios centros. Multiplicarlo por campus o transformador no añade observaciones independientes. La ponderación principal es igual por barra elegible y por día identificado. Las estadísticas mensuales descriptivas deben declarar si ponderan etiquetas observadas; no se confunden con los pesos del ATT.

### 3.3. Carga y evidencias del tratamiento

La capa de mediciones se mantiene separada de los precios hasta resolver unidades, orientación, vigencia y correspondencia temporal. Una energía de 15 minutos en kWh permite calcular potencia media en MW dividiendo por 250 cuando la duración está acreditada. Esa conversión no resuelve si un canal representa retiro, inyección o tránsito. Tampoco demuestra consumo total de un campus.

HT1 y HT2 de Las Canteras pertenecen al mismo proyecto y su suma no representa dos centros tratados. HT3 y los circuitos de tránsito no se incorporan mecánicamente al consumo. La primera observación de un medidor no se utiliza como fecha de entrada. La curva de retiro puede contribuir a describir un cambio, pero su calendario no reemplaza documentación que distinga ampliación, transferencia y modificación de medición.

## 4. Del registro documental a un tratamiento elegible

La matriz centro/fase–evento–barra–vigencia registra hechos y fuentes con localizadores. Los anuncios, fechas previstas, PES, energización, EO, inauguración y cambios observados en carga ocupan campos diferentes. La elegibilidad exige comprobar realización y naturaleza del cambio, además del enlace eléctrico. Un documento de término de una obra puede cerrar su fecha y mantener abierta la interpretación de la carga.

La revisión de la nueva etapa ilustra esa separación con el alimentador Ascenty E53 en S/E Chacabuco, NUP 5417. La carta de Sociedad Transmisora Metropolitana de 4 de junio de 2025 señala energización y entrega a explotación el 5 de mayo. Es una realización acreditada de la conexión; no basta para determinar por sí sola campus, fase, demanda incremental o sustitución de un suministro anterior. Por tanto, no se transforma automáticamente en la entrada de «Ascenty Chile 2». [Carta de término, p. 1](https://cartas.coordinador.cl/download_saved_file/684213aa3563577698e6da48).

La carta de modificación vincula E53 a BP7 de 23 kV. El unifilar del proyecto permite seguir la ruta nominal E53–BP7–T7–BP1 de 110 kV, correspondiente al enlace nominal con CHACABUCO110. BP7 no se equipara a la barra de costo marginal de 23 kV identificada como BP2. Esta mejora cierra la ambigüedad de ruta nominal, pero no acredita por sí sola todos los estados operativos históricos ni la naturaleza de la carga. [Carta BP7, p. 1](https://cartas.coordinador.cl/download_saved_file/678a9ac43563572012d6e461); [unifilar NUP 5417, láminas 8 y 1 del archivo oficial](https://api-infotecnica.coordinador.cl/v1/subestaciones/683/documentos/470265/).

El caso Las Canteras también exige distinguir retiro medido y entorno operativo. El informe diario del Coordinador del 24 de junio de 2024 registra apertura de Las Vegas 52H4 a las 21:40 por control de transferencias Quillota–San Pedro; también registra una apertura en Santiago Solar desde el 22 de junio. Son concurrencias documentadas durante la ventana del cambio observado de retiro. No acreditan su causa ni una simultaneidad física minuto a minuto, porque el reloj de la medición y el del informe no están conciliados. Sí impiden asumir sin examen que la operación de la red relevante y los comparadores permanecieron ajenos al episodio. [Informe diario del 24 de junio, p. 24 del archivo](https://www.coordinador.cl/wp-content/uploads/2024/06/Informe-Diario-24-06-2024.pdf). El informe del día siguiente registra el término de ese episodio de Las Vegas a las 12:09 y otra apertura a las 16:09; no se trata como una configuración permanentemente abierta. [Informe del 25 de junio, p. 24](https://www.coordinador.cl/wp-content/uploads/2024/06/Informe-Diario-25-06-2024.pdf).

La verificación es acumulativa: cerrar un enlace o una fecha reduce una brecha concreta, pero no aprueba en bloque el expediente causal. Las fuentes y la matriz completa acompañan esta versión. Los antecedentes anteriores de Las Canteras se conservan en sus entregas originales; sus contrastes de ventanas cortas no se trasladan a esta etapa como efectos causales del panel 2020–2026.

## 5. Estrategia empírica

### 5.1. Resultado y parámetro

Para barra `b`, día `d` y referencia `r`, el resultado es

\[
Y^{(r)}_{bd}=\frac{1}{|H_{bd}^{(r)}|}\sum_{h\in H_{bd}^{(r)}}(P_{bdh}-P_{rdh}),
\]

con soporte de etiquetas coincidente y unidad USD/MWh. Quillota 110 es la referencia principal prevista; Quillota 220 y los niveles de precios complementan la interpretación. Ninguna de las dos referencias se presume causalmente no expuesta. Con soporte y pesos idénticos, el término de referencia se cancela en un DiD de barras; cambiarla no constituye entonces una validación independiente.

Para una intervención persistente y apropiadamente definida, `G_b=g` identifica la cohorte y `D_bt=1(t≥g)` su adopción. El parámetro buscado es

\[
ATT^{(r)}(g,t)=E[Y^{(r)}_{bt}(g)-Y^{(r)}_{bt}(\infty)\mid G_b=g],\quad t\geq g.
\]

Se refiere a barras elegibles de esa cohorte, no automáticamente a centros, MW instalados o toda la red chilena. Un tratamiento que revierte o transfiere carga requiere otro objeto o una ventana adecuada; no se fuerza la hipótesis de adopción absorbente.

### 5.2. Comparación, anticipación y dinámica

El protocolo de esta etapa fija antes de estimar una ventana previa de días −112 a −8, siete días de anticipación excluidos y 90 días posteriores. Cuando solo se conoce el día de un hecho validado, `g` es el primer día completo siguiente. Un intervalo documental de realización no se convierte en fecha puntual. La base de cada contraste es `g−8`. Se requiere cobertura mínima, resultado en la base y en `t`, y comparadores válidos bajo las mismas reglas; la cobertura es necesaria, pero no suficiente para causalidad. [Protocolo completo](protocolo_previo_v8.md).

Los controles admisibles son barras con historia documentada sin la intervención definida en la ventana o todavía no tratadas y fuera de su anticipación. Una historia desconocida no se codifica como nunca tratada. El marco de efectos por grupo y tiempo permite organizar estas comparaciones bajo supuestos explícitos; la condición de tendencias paralelas puede ser no condicionada o requerir covariables previas. El primer contraste previsto es no ajustado y solo se interpretará como ATT si se justifica el supuesto correspondiente. [Callaway y Sant’Anna, 2021](https://arxiv.org/abs/1803.09015).

La dinámica agrega los efectos identificados por distancia al evento, con pesos y composición publicados. Se utiliza soporte común entre cohortes cuando exista para evitar interpretar cambios de composición como evolución temporal. El estimando ATT, la estrategia DiD y el estudio de eventos forman partes de una misma investigación. Una regresión convencional con efectos fijos, anticipos y rezagos no reemplaza automáticamente esa construcción ante efectos heterogéneos. [Sun y Abraham, 2021](https://arxiv.org/abs/1804.05785).

La ventana principal de 112 días previos hace posible examinar casos de 2020 sin atribuirles un año previo inexistente. La sensibilidad de 365 días solo se ejecutará donde haya soporte. La pandemia y perturbaciones diferenciales de oferta o red requieren evaluación sustantiva. Los efectos de fecha no eliminan automáticamente esos riesgos. Las ventanas que atraviesen julio de 2024 quedan condicionadas al puente entre regímenes. Una intervención reciente sin 90 días posteriores puede permitir un estimando corto separado, pero no completar el principal con precios PRE.

### 5.3. Exposición eléctrica

La interferencia se representa mediante exposición propia y ajena documentada. Una posible notación es `E_bt=Σ_j W_bj,t D_jt`, donde los pesos deben proceder de vínculos eléctricos vigentes y no de correlaciones de precios posteriores. Desconocer un vínculo no equivale a observar peso cero. El resultado relativo exige considerar la exposición de la barra y de su referencia.

La separación de efecto directo y spillover requiere barras y períodos que sostengan ambos contrastes. Si tratamiento y exposición se mueven siempre juntos, no se identifican por separado solo por introducir dos regresores. La literatura sobre spillovers muestra que respuestas en comparadores pueden contaminar DiD; trasladar su lógica a este caso exige un mapa eléctrico propio y supuestos defendibles, sin convertir cercanía geográfica en ausencia de exposición. [Butts, 2023](https://arxiv.org/abs/2105.03737).

### 5.4. Inferencia y comprobaciones

La precisión depende de asignaciones independientes. Horas, transformadores y fases del mismo campus no multiplican ese número. Se informarán campus, barras tratadas, eventos, cohortes, comparadores y agrupaciones para cada estimación. La dependencia temporal y eléctrica debe guiar la agrupación. Con pocos grupos tratados, tanto errores agrupados convencionales como bootstrap pueden fallar; una permutación no se interpreta como aleatorización sin justificar el mecanismo. [MacKinnon y Webb, 2018](https://onlinelibrary.wiley.com/doi/full/10.1111/ectj.12107).

Las comprobaciones incluyen trayectorias previas, fechas alternativas documentadas, calidad de datos, soporte común y dependencia de un campus. No rechazar una prueba previa no demuestra paralelismo. Cuando exista inferencia defendible se examinará sensibilidad a desviaciones del supuesto, declarando las restricciones que la sostienen. [Rambachan y Roth, 2023](https://www.jonathandroth.com/assets/files/HonestParallelTrends_Main.pdf).

El aprendizaje automático no se incorpora como resultado causal autónomo. Podría mejorar un ajuste auxiliar si hubiera covariables justificadas y suficientes unidades independientes para separar entrenamiento y evaluación. Ortogonalización y cross-fitting son principios pertinentes, pero sus condiciones no se obtienen tratando horas correlacionadas como unidades independientes. [Chernozhukov et al., versión consultada 2024](https://arxiv.org/abs/1608.00060). La etapa actual no habilita ese componente.

## 6. Resultados disponibles y estado de identificación

El resultado verificado de construcción es un panel diario de 142.151 filas de calendario. Hay 141.723 filas barra–día con 24 etiquetas y parejas completas, 407 con 25 etiquetas y 21 días de barra sin precio, conservados con valores ausentes. Estos últimos corresponden a 504 etiquetas horarias faltantes respecto de la unión observada. No se detecta una ausencia común a todas las barras mediante ese criterio. Los diferenciales horarios reconstruidos coinciden exactamente con los de v0.2.0; la comparación entre agregaciones mensuales y diarias ponderadas presenta diferencias solo del orden de precisión numérica. [Validación ejecutada](../validacion/validacion_panel.json).

Al excluir la propia referencia Quillota 110 y restringir a 24 pares de etiquetas quedan 139.277 filas para descripción. La siguiente tabla usa igual peso por barra–día; conserva 2024 por régimen y no transforma las etiquetas de barra en identidades físicas longitudinales.

| Año y régimen | Filas barra–día | Media | Mediana | Percentil 10 | Percentil 90 |
|---|---:|---:|---:|---:|---:|
| 2020, histórico | 19.619 | 1,16 | 0,90 | −0,01 | 2,20 |
| 2021, histórico | 19.687 | 4,73 | 2,21 | 0,30 | 8,39 |
| 2022, histórico | 20.020 | 5,91 | 2,67 | 0,27 | 12,69 |
| 2023, histórico | 20.748 | 1,61 | 1,25 | −0,47 | 5,44 |
| 2024, histórico hasta 14 de julio | 11.323 | 2,74 | 1,21 | −0,08 | 7,22 |
| 2024, moderno desde 15 de julio | 10.030 | −0,57 | 0,27 | −1,81 | 1,33 |
| 2025, moderno | 21.959 | 1,07 | 0,93 | 0,03 | 3,32 |
| 2026, moderno hasta 18 de septiembre | 15.891 | 1,27 | 0,90 | −0,02 | 3,63 |

Unidad: USD/MWh del diferencial diario respecto de Quillota 110. Fuente: [tabla descriptiva anual ejecutada](../resultados/tabla_descriptiva_anual.csv). Los percentiles describen dispersión de resultados observados; no son intervalos de confianza. La composición de barras y días cambia, de modo que las diferencias entre filas no identifican una evolución causal de una población fija.

**Figura 1. Precios relativos en las barras seleccionadas.** [Ver gráfico mensual](../figuras/01_diferenciales_descriptivos.png). La línea es la media con igual peso por barra–día; la banda comprende percentiles 10–90. Los regímenes se presentan separados. Los valores de 2021–2022 muestran mayor dispersión en esta selección que varios años posteriores, sin atribución a centros de datos.

**Figura 2. Dispersión del diferencial diario por año y régimen.** [Ver gráfico de distribución](../figuras/02_distribucion_anual.png). Los puntos indican mediana y los extremos percentiles 10 y 90. La media negativa de la submuestra moderna de 2024 coexiste con una mediana positiva; describe asimetría y composición de esa distribución, no un efecto de entrada ni del cambio metodológico de publicación.

La revisión documental aporta fechas realizadas de obras, enlaces eléctricos progresivamente precisados y concurrencias operativas que deben incorporarse al diseño. El caso E53 demuestra por qué una fecha de conexión y una fecha de nueva demanda no son intercambiables. El informe de junio de 2024 muestra por qué no corresponde certificar comparadores solo con sus series de precios.

**ATT y estudio de eventos.** La revisión ejecutada registra 24 eventos y cero eventos, campus, barras tratadas o comparadores habilitados. Sus campos ATT, error estándar y dinámica causal permanecen nulos. La habilitación depende de cerrar conjuntamente la naturaleza del tratamiento, la continuidad de barra, la comparación y la exposición. Esta ausencia no es una estimación igual a cero ni evidencia de inexistencia de efectos. Las estadísticas y figuras anteriores describen la muestra observada y no son resultados de impacto. [Estado de estimación](../resultados/estado_estimacion.json); [soporte por evento y ventana registrada](../resultados/soporte_eventos_ventana_registrada.csv).

**Spillovers.** No se publica un efecto indirecto sin mapa de exposición y soporte. La documentación de enlaces es un insumo para ese análisis, no una estimación de transmisión de impactos. Las filas con exposición desconocida conservan ese estado.

## 7. Discusión y conclusión provisional

El paso decisivo para evaluar centros de datos en la red chilena es convertir un proyecto comercial en una intervención eléctrica definida. La base disponible permite observar precios durante varios años, pero la cantidad de registros no determina cuántas entradas independientes existen ni cuáles tienen un contrafactual defendible. Nuevas conexiones pueden abastecer carga existente; distintas fases pueden compartir campus; una referencia puede responder a las mismas maniobras que la barra analizada.

La versión actual establece un panel y un protocolo que conservan esas distinciones. Su conclusión sustantiva permanece abierta: todavía no se puede afirmar que los centros estudiados eleven o reduzcan causalmente los diferenciales nodales. La evaluación avanzará mediante el cierre de expedientes concretos y la aplicación de las comparaciones habilitadas, conservando resultados nulos o contrarios a la hipótesis. Si las condiciones no permiten separar efectos, el alcance final deberá reflejarlo expresamente.

Para la planificación territorial, la pregunta relevante combina demanda realizada, secuencia de conexión y exposición de la red. Sin resultados identificados no se recomiendan regiones específicas para relocalizar centros, no se calculan beneficios sociales y no se atribuyen cambios tarifarios a sus proyectos. La contribución verificable de esta etapa es establecer qué evidencia permite formular esos contrastes y qué información adicional hace falta para responderlos.

## Disponibilidad, reproducción y estado editorial

Los archivos originales y la entrega v0.2.0 permanecen intactos. La etapa v8 contiene código Python, paneles analíticos, diccionarios, matrices de eventos y controles, registros de fuentes y salidas de validación. La configuración metodológica se conserva junto al manuscrito, de modo que cambios posteriores de ventana, tratamiento o comparación puedan identificarse. El libro de revisión no pretende contener millones de filas en una sola hoja.

El artículo está en elaboración para el curso y SOCHER 2026, con *Energy Economics* como primera revista objetivo. La preparación editorial final, la literatura sectorial y los resultados causales no se consideran completos. La prórroga del congreso al 9 de octubre de 2026 fue comunicada por el autor y no se presenta como verificación independiente de un sitio del congreso.

## Referencias

- Butts, K. (2023). *Difference-in-Differences Estimation with Spatial Spillovers*. Prepublicación, versión 3. [Texto y versiones](https://arxiv.org/abs/2105.03737).
- Callaway, B. y Sant’Anna, P. H. C. (2021). Difference-in-Differences with Multiple Time Periods. *Journal of Econometrics*, 225(2), 200–230. [Versión de autores](https://arxiv.org/abs/1803.09015).
- Chernozhukov, V., Chetverikov, D., Demirer, M., Duflo, E., Hansen, C., Newey, W. y Robins, J. *Double/Debiased Machine Learning for Treatment and Causal Parameters*. Prepublicación; versión 7 consultada, 2024. [Texto y versiones](https://arxiv.org/abs/1608.00060). Esta referencia identifica la versión efectivamente consultada.
- Coordinador Eléctrico Nacional (sin fecha). *Costo Marginal Real*. Consulta: 27 de septiembre de 2026. [Definición y acceso a datos](https://www.coordinador.cl/mercados/graficos/costos-marginales/costo-marginal-real/).
- MacKinnon, J. G. y Webb, M. D. (2018). The wild bootstrap for few (treated) clusters. *The Econometrics Journal*, 21, 114–135. [Artículo](https://onlinelibrary.wiley.com/doi/full/10.1111/ectj.12107).
- Ministerio de Ciencia, Tecnología, Conocimiento e Innovación (2024). *Plan Nacional de Data Centers 2024–2030*. [Documento oficial](https://minciencia.gob.cl/uploads/filer_public/95/6b/956b8c9f-d937-4b4d-8f6c-a871495a52ff/plan_nacional_de_data_centers_pdata.pdf).
- Rambachan, A. y Roth, J. (2023). A More Credible Approach to Parallel Trends. *Review of Economic Studies*, 90(5), 2555–2591. [Texto del autor](https://www.jonathandroth.com/assets/files/HonestParallelTrends_Main.pdf).
- Sun, L. y Abraham, S. (2021). Estimating Dynamic Treatment Effects in Event Studies with Heterogeneous Treatment Effects. *Journal of Econometrics*, 225(2), 175–199. [Versión de autoras](https://arxiv.org/abs/1804.05785).

Las fuentes operacionales por proyecto, incluyendo cartas, informes diarios y unifilares, se identifican individualmente en la matriz y su manifiesto; no se sustituyen por estas referencias metodológicas.
