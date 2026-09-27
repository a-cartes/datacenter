# Protocolo de análisis de la etapa v8

**Proyecto:** Entrada de centros de datos y diferenciales nodales de costo marginal: evidencia causal para Chile.  
**Registro:** 27 de septiembre de 2026. **Estado:** decisiones anteriores a las estimaciones v8; no constituye un prerregistro prospectivo. Las etapas anteriores ya examinaron mediciones y contrastes de precios del caso Las Canteras. Las modificaciones posteriores requieren fecha, motivo y salidas conocidas al modificarlas.

La especificación legible por programas está en [protocolo_config.json](protocolo_config.json). Este protocolo actualiza, para la base v0.2.0, las reglas de `SOCHER_2026_repositorio/docs/metodologia.md`. No altera el contrato ni los activos de esa entrega.

## 1. Pregunta y población

Se investiga si la entrada de nueva carga de un centro de datos cambia el costo marginal publicado en su barra respecto de otras barras, y si existen respuestas en nodos eléctricamente expuestos. La población empírica inicial es el conjunto de barras seleccionadas en la entrega congelada, con cobertura DEF entre el 1 de enero de 2020 y el 18 de septiembre de 2026. No es una muestra aleatoria de todas las barras del SEN ni un censo de todos los centros de datos de Chile.

Hay tres objetos de intervención distintos: **primera entrada de carga del campus**, **ampliación incremental de un campus existente** y **transferencia de suministro o nueva conexión de carga existente**. Una cuarta categoría, cambio de medición o hecho indeterminado, no habilita tratamiento de demanda. El análisis principal de entrada no agrupa las otras categorías. Las ampliaciones, si se habilitan, tienen su propio estimando: conservar las fases existentes y retirar contrafactualmente la ampliación. Una transferencia no se denomina entrada neta; solo puede analizarse como intervención de conexión con donantes y mecanismos propios.

La unidad del resultado es la barra de precios, la unidad documental es campus–fase–evento y la unidad de asignación independiente debe determinarse desde el proyecto y la red. Varios medidores de un campus no constituyen varias intervenciones. Varias barras del mismo proyecto pueden ser resultados diferentes de una única asignación. Si dos campus afectan inseparablemente la misma barra en la ventana, se define un evento conjunto o se excluye el contraste individual.

## 2. Construcción del resultado

La base congelada tiene 3.411.527 filas y 31 columnas. Sus valores no se sustituyen. Las homologaciones nuevas se incorporan como una capa adicional con procedencia y vigencia. `barra_mes_id` es una clave mensual, no una identidad física longitudinal. Un segmento de etiqueta/código sin cambios facilita el almacenamiento, pero no certifica continuidad física. La muestra causal exige una cadena documental entre los segmentos usados.

El panel general conserva una fila por barra del registro × fecha publicada × régimen. Para cada día se guarda el conjunto de etiquetas horarias observadas y su firma, el número de precios y el número de pares válidos con cada referencia. El régimen histórico mantiene 1–25 y el moderno HRA 0–24; no se crea UTC ni se supone que restar uno los alinea. No se enlaza carga y precio por una hora física no acreditada.

Para una referencia `r`, el resultado diario es

\[
Y^{(r)}_{bd}=|H_{bd}^{(r)}|^{-1}\sum_{h\in H_{bd}^{(r)}}(P_{bdh}-P_{rdh}),
\]

donde cada par comparte fecha, régimen y etiqueta original. Se reporta en USD/MWh. El resultado principal previsto usa Quillota 110; Quillota 220 y precios en niveles son resultados complementarios. La barra de referencia se excluye de la muestra cuyo diferencial consigo misma es cero. Quillota define la variable dependiente, pero **no queda por ello habilitada como control**.

La selección principal diaria requiere exactamente 24 etiquetas únicas, todas con precio numérico y pareja válida; en una comparación se exige el mismo conjunto de etiquetas para tratados y comparadores en cada fecha. Los días con 23, 25 o menos etiquetas se conservan para descripción y controles de cobertura. Esta restricción define una media de etiquetas de días ordinarios, no acredita por sí sola una media física de 24 horas. No se imputan faltantes ni se balancea por interpolación. Los días omitidos simultáneamente en todas las barras no se detectan comparando solamente su unión observada; la cobertura por calendario debe publicarse por separado.

El 15 de julio de 2024 cambia el régimen de publicación. Las ventanas que lo cruzan requieren demostrar comparabilidad de la definición del precio y del agregado diario de ambos regímenes; agrupar por fecha no resuelve esa ruptura. Mientras el puente siga pendiente, el análisis principal no cruza el corte y las estadísticas se presentan separadas por régimen. Un contraste que pierda la ventana mínima por esta restricción se declara sin soporte principal; no se desplaza el evento para recuperarlo.

No se calcula un diferencial restando medias con soportes horarios diferentes. La muestra mensual descriptiva puede ponderar por el número de etiquetas presentes; el ATT principal asigna peso igual a barras y días admisibles, sin favorecer barras por más horas o más medidores. El filtrado por cobertura puede cambiar la población; se documentará la distribución temporal de exclusiones y no se supondrá ignorabilidad automática.

Si los controles usan una referencia común y exactamente las mismas fechas, horas y ponderaciones, su componente se cancela en el DiD. En esas condiciones cambiar de Quillota 110 a 220 no proporciona una réplica independiente. Un efecto nulo sobre el diferencial tampoco descarta una respuesta común del nivel de precios.

## 3. Calendario y ventanas registradas

`fecha_realizacion_desde` y `fecha_realizacion_hasta` expresan el intervalo documental del hecho. No se reemplaza una fecha realizada por el anuncio, PES prevista, publicación de carta, inauguración corporativa o primera lectura disponible. Se preservan por separado esos hitos y sus fuentes.

Para fechas realizadas con precisión diaria y mecanismo cerrado, `g` es el primer día completo después de la realización: al no conocerse la hora, el día del hecho queda en transición y `g = fecha_realizacion + 1 día`. Si la fuente acredita operación desde el comienzo de un día se permite usar ese día, con motivo explícito. Este desplazamiento de calendario no acredita cuándo comenzó la demanda: solo se aplica **después** de acreditar la naturaleza y realización del tratamiento definido.

Las decisiones iniciales son:

| Decisión | Regla principal |
|---|---|
| Escala | Días civiles publicados; sin enlace horario carga–precio |
| Ventana previa | Días relativos −112 a −8, ambos incluidos |
| Anticipación | Excluir −7 a −1; el expediente debe justificar que no hay respuesta operativa relevante antes de ese margen |
| Base de ATT(g,t) | Día g−8 observado y comparable |
| Ventana posterior | Días 0 a 89, ambos incluidos |
| Cobertura de entrada | Al menos 95 de 105 días previos y 81 de 90 posteriores de calidad, además de base y soporte para cada celda |
| Parámetro resumen | Media de ATT de los días 0–89 efectivamente identificados, con días y pesos publicados; si faltan días, se denomina efecto en días observados, no efecto completo de 90 días |
| Dinámica | ATT diario; representación en bloques de siete días con igual peso por día dentro del bloque y composición publicada |
| Ponderaciones | Igual peso por barra elegible dentro de cohorte; agregación entre cohortes según número de barras elegibles en soporte común |
| Umbral sustantivo | No se fija un signo obligatorio ni se excluyen resultados nulos |

Los umbrales de cobertura son decisiones de este proyecto, no resultados teóricos ni prueba de tendencias paralelas. La ventana de 112 días permite investigar casos de 2020 con la base disponible. No ofrece un ciclo anual previo. Se prevé la sensibilidad de 365 días previos para los casos con soporte; no se atribuye ese soporte a los casos tempranos. La pandemia y otros choques contemporáneos de 2020 exigen evaluación de concurrencias aunque exista cobertura.

Un evento realizado después del 20 de junio de 2026 carece de los 90 días civiles completos hasta el corte del 18 de septiembre bajo la convención anterior; el último `g` con esa ventana completa es el 21 de junio. La puerta aplica fechas exactas, sin completar con PRE. Las ventanas cortas de 28 días son un estimando secundario separado, sujeto a las mismas condiciones documentales y de comparación. No sustituyen silenciosamente la ventana principal.

Una fecha realizada solo acotada a un intervalo no habilita una cohorte diaria puntual. Se conservará el intervalo y se podrá definir un contraste agregado con transición desde el inicio menos anticipación hasta el final. Las fechas extremas se mostrarán conjuntamente en una sensibilidad identificada como tal; no se seleccionará la más significativa. Anticipación 0 o 14 días, ventana post de 28 días y calidad no restringida a 24 etiquetas son sensibilidades predefinidas; requieren justificación del hecho y no eliminan brechas de enlace o exposición.

## 4. Puertas de habilitación, separadas y auditables

Se aplica lógica de tres estados: `true`, `false`, `null` (desconocido). Una puerta solo aprueba con todos los campos requeridos en `true`; desconocido nunca se convierte en falso tratamiento o exposición cero. La tabla de bloqueos debe enumerar cada requisito no aprobado.

**Puerta documental del evento.** Exige identidad de campus/fase, hecho realizado, naturaleza del cambio, fecha apropiada a la escala, ausencia de duplicación por equipos y cadena campus–instalación–barra con vigencia. La correspondencia puede ser directa mediante documentación eléctrica o pasar por medidores; conocer todos los medidores no es indispensable si existe otro enlace directo suficiente. Una EO administrativa acredita ese hito, no necesariamente incremento neto de demanda. Se necesita además justificar si se analiza entrada, ampliación o conexión.

**Puerta del diseño.** Exige intervención estable en la ventana o definición que admita su trayectoria, continuidad de barra, período previo no afectado, comparadores con historia suficiente, concurrencias examinadas y un argumento de identificación y exposición. Si obra y carga cambian conjuntamente y no pueden separarse, el evento debe definirse como conjunto, sin atribuir todo a consumo informático.

**Puerta de la celda (g,t).** Exige al menos una barra tratada y una de comparación con resultado y base observados bajo reglas idénticas, tratamiento conocido, control no tratado ni anticipante en esos períodos y exposición compatible con el contraste. La mera posibilidad de calcular una diferencia no aprueba las otras puertas. Cada celda publica barras, campus, eventos independientes, cohortes, controles, fechas, pesos y razones de exclusión.

**Puerta de inferencia.** Es distinta de la del punto estimado. Requiere estructura de dependencia justificable, número de asignaciones independientes reportado y procedimiento apropiado. Sin ella puede publicarse un contraste descriptivo o un estimado condicional claramente delimitado, pero no intervalos presentados como precisos por tener muchas horas. Dos cohortes son necesarias para hablar de adopción escalonada observada; una sola cohorte no impide por sí misma un DiD, aunque pocos proyectos restringen inferencia y generalización.

## 5. Controles y ATT por cohorte y período

La matriz de controles contiene, para cada barra–ventana, historia de entradas/ampliaciones/conexiones, fuente, vigencia, anticipación y exposición. La ausencia del nombre de un centro en un catálogo no demuestra ausencia de tratamiento. El grupo principal admite barras documentadas sin la intervención definida durante la ventana; se agregan controles todavía no tratados solo si su fecha y anticipación son conocidas y `G_control > t + 7 días`. Se excluyen ya tratados del diseño de primera adopción, historias desconocidas y exposición no resuelta para el contraste elegido.

El parámetro es

\[
ATT^{(r)}(g,t)=E[Y^{(r)}_{bt}(g)-Y^{(r)}_{bt}(\infty)\mid G_b=g].
\]

DiD es la estrategia para identificarlo; el estudio de eventos organiza su dinámica. No son tres pruebas independientes. El marco de Callaway y Sant’Anna permite efectos por grupo y tiempo y requiere, entre otras condiciones, tratamiento absorbente, anticipación limitada, tendencias paralelas y soporte de comparación. Su formulación usa muestreo independiente entre unidades; una red eléctrica no hereda esa condición por construir una tabla de panel. [Fuente primaria, §§2–3](https://arxiv.org/pdf/1803.09015).

La primera estimación será el contraste no ajustado con las mismas fechas y reglas: diferencia del cambio desde `g−8` entre barras tratadas y comparadoras. Su interpretación causal exige tendencias paralelas **sin condicionar**, lo cual se argumentará antes de ejecutarlo como ATT. Si solo es defendible un supuesto condicionado, se requiere otra especificación previa y soporte suficiente; no se interpretará el contraste simple como si ya ajustara.

Solo covariables predeterminadas y documentadas pueden entrar al ajuste: características eléctricas previas, calendario y medidas de condiciones de oferta exógenas a la intervención, con fuentes y relojes resueltos. Carga, despacho, flujos y congestión realizados después del evento pueden ser mediadores; no se usan automáticamente para obtener un supuesto efecto total. La inclusión de efectos de fecha absorbe choques comunes, no choques diferenciales por barra ni endogeneidad de la localización.

Se agrega dinámica con pesos no negativos publicados, y se muestra una ventana con cohortes comunes cuando exista. Los coeficientes de una regresión convencional de efectos fijos con anticipos y rezagos pueden mezclar efectos de distintos períodos ante heterogeneidad; no serán el estimador principal de la dinámica. [Sun y Abraham, §3](https://arxiv.org/pdf/1804.05785).

## 6. Interferencia y mecanismos

La exposición se especifica mediante vínculos eléctricos documentados y vigentes, con fuente, alcance y fecha de cada arista. No se usa distancia comunal como sustituto principal ni se aprende la red de correlaciones de precios posteriores. `W_desconocido` permanece nulo. La falta de una arista documentada no prueba exposición cero.

Se distinguen efecto del tratamiento propio, efecto sobre barras sin tratamiento directo expuestas y respuesta total de una intervención conjunta. En un diferencial importan exposición de barra y de referencia. Si todas las barras comparables responden o si exposición y tratamiento propio son colineales, sus efectos separados carecen de soporte. La comparación podría medir una respuesta relativa del conjunto, siempre que su contrafactual pueda defenderse; no un efecto directo aislado.

El trabajo de Butts formaliza contaminación de comparadores por spillovers y requiere condiciones explícitas para recuperar efectos; su condición de exposición local no equivale a afirmar que los efectos eléctricos desaparecen por distancia geográfica. [Fuente primaria, §§2–3](https://arxiv.org/pdf/2105.03737). La matriz eléctrica pendiente de este proyecto no queda validada por citar ese modelo.

Se examinarán mecanismos económicos si existen mediciones suficientes: respuesta en períodos de distinta oferta y relación con restricciones de red documentadas. El signo del diferencial no se impone: nueva carga y obras asociadas pueden producir respuestas distintas, y una referencia puede moverse más que la barra tratada. No se interpreta el diferencial como tarifa minorista ni como componente oficial de congestión.

## 7. Incertidumbre, sensibilidad y ML

Los conglomerados de asignación reúnen barras y fases del mismo proyecto; la dependencia eléctrica entre proyectos puede requerir agrupación más amplia. No se define el conglomerado como transformador, hora o réplica de precio. Deben publicarse números de tratados y controles independientes y concentración de pesos. No hay un umbral universal que vuelva válida la inferencia; la puerta no se abre solo por superar un número arbitrario de barras.

La literatura de pocos grupos tratados muestra fallas posibles tanto en errores agrupados convencionales como en bootstrap. Una permutación temporal o espacial no es inferencia por aleatorización sin un mecanismo de asignación defendible. [MacKinnon y Webb, fuente editorial primaria](https://onlinelibrary.wiley.com/doi/full/10.1111/ectj.12107). No se informarán bandas simultáneas ni p-valores si su procedimiento no cumple una justificación aplicable a la muestra efectiva.

Se conservarán efectos nulos y negativos. Se publicarán todas las ventanas y controles predefinidos habilitados, pruebas previas conjuntas si la inferencia lo permite, exclusión de un campus a la vez y sensibilidad a desviaciones de tendencias paralelas. Esta última puede emplear restricciones sobre la magnitud de desviaciones posteriores cuando los coeficientes y su covarianza sean válidos; no resuelve por sí sola pocos grupos o falta de controles. [Rambachan y Roth, §2.4](https://www.jonathandroth.com/assets/files/HonestParallelTrends_Main.pdf).

No se ejecutará ML causal en esta etapa sin variación independiente suficiente, covariables justificadas y una tarea auxiliar concreta. La predicción no identifica un efecto. Si se incorporara ajuste flexible, usaría una puntuación compatible con el estimando y separación de muestras por unidades independientes y bloques temporales, nunca particiones aleatorias de horas del mismo evento. El trabajo de Chernozhukov et al. motiva ortogonalización y cross-fitting, pero no valida automáticamente su adaptación a esta red dependiente. [Fuente primaria](https://arxiv.org/abs/1608.00060). Un ejercicio predictivo futuro debe compararse fuera de muestra con una media estacional y un modelo lineal simple, y publicarse separado de causalidad.

## 8. Salidas y reglas de actualización

Se entregan panel diario y mensual descriptivo, diccionario, matriz de eventos con sus fuentes, matriz de controles, conteo de soporte por diseño, libro Excel de revisión y tablas/figuras provenientes del código. El panel completo horario se conserva en CSV/Parquet; no se intenta introducirlo en una sola hoja Excel.

Una salida sin ATT habilitados se registra como **no identificado con el expediente vigente**, con número y razón de cada bloqueo, nunca como efecto cero. Las secciones de resultados del manuscrito solo incorporan salidas ejecutadas. Se permite cerrar evidencia y actualizar elegibilidad sin cambiar resultados ni precios originales. Cambiar ventana, estimando, controles o inferencia requiere una adenda fechada anterior a su nueva ejecución, que declare lo ya observado.
