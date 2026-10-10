# Datos y decisiones para construir la réplica en Chile

> Actualización del 2 de octubre de 2026: el estado de cada decisión se resolvió en los documentos indicados; ver INFORME_AVANCE.md.

Este documento define la información que se necesita reunir desde cero. La [primera revisión de fuentes chilenas](DISPONIBILIDAD_CHILE.md), completada el 1 de octubre de 2026, acredita documentación y dos muestras eléctricas. La cobertura multianual y la muestra analítica aún deben construirse; las fechas y clasificaciones de trabajos anteriores no se incorporan automáticamente.

## Decisiones previas a la estimación

| Decisión | Evidencia necesaria | Estado |
|---|---|---|
| Universo de centros | Criterio sobre campus, edificios, instalaciones comerciales e institucionales y continuidad de operación | Resuelto 2026-10-02: INVENTARIO_INSTALACIONES.md (D-10, D-12) |
| Resultado comparable | Definición y disponibilidad de componentes de precios; método de reconstrucción, si corresponde | Resuelto: D = P − P_Quillota validado; L y C hasta 2023 (VALIDACION_MEDIDA.md) |
| Unidad territorial | Geografía estable, resolución de precios y posibilidad de asociar instalaciones y características previas | Resuelto: distrito censal 2017; alternativas comuna y nodo (D-13) |
| Ventana temporal | Cobertura homogénea y suficientes períodos anteriores y posteriores por cohorte | Resuelto: 2017–2025; entradas elegibles 2019–2025 (D-09) |
| Primeras entradas | Historia previa y fechas operativas con fuentes y precisión | 3 distritos tratados; fechas con intervalo (D-11) |
| Comparadores | Ausencia documentada de operación local y evaluación de exposición indirecta | 57 distritos de control; exposición por red documentada (UNIDADES_Y_PERIODO.md) |
| Emparejamiento | Covariables anteriores al tratamiento, equivalencia conceptual y soporte común | Probit con covariables Censo 2017 sustitutas (D-16, D-17) |
| Estimación e inferencia | Número de unidades y cohortes, pesos, dependencia por red y horizontes identificables | Estimado; soporte insuficiente para interpretación causal (RESULTADOS_REPLICA.md) |

La existencia de datos de precios no basta para aprobar el diseño. Deben coincidir una medida interpretable, una historia verificable de tratamiento y comparaciones defendibles. La disponibilidad se examinará antes de observar estimaciones posteriores al tratamiento.

## Tablas necesarias

La estructura siguiente es un diccionario inicial del futuro panel. Existen muestras originales de precios y una matriz documental de casos; todavía no están integradas en estas tablas analíticas. Identificadores y relaciones deberán mantenerse estables durante la construcción.

| Tabla | Unidad del registro | Campos mínimos |
|---|---|---|
| Fuentes | Documento o conjunto de datos y versión | Identificador, emisor, título, enlace o archivo, fecha de publicación, consulta, versión y pasaje pertinente |
| Instalaciones | Campus o instalación identificable | Identificador, nombres históricos, operador, coordenadas, tipo de instalación, campus o etapa, continuidad histórica y fuentes |
| Hitos | Hito de una instalación | Instalación, tipo de hito, fecha o límites del intervalo, precisión, evidencia y estado de validación |
| Unidades territoriales | Territorio de análisis | Identificador, geometría, versión de límites, vigencia y fuente |
| Correspondencias | Asociación válida durante un intervalo | Instalación o nodo, unidad territorial o conexión eléctrica, vigencia, método y fuente |
| Precios originales | Nodo e intervalo temporal | Nodo, tiempo local y UTC cuando sea posible, duración, resultado publicado, componentes, moneda, unidad, versión y estado de dato |
| Historia de exposición | Unidad territorial | Presencia previa, primera operación, intervalo temporal, incertidumbre, búsqueda realizada y fuentes |
| Covariables | Unidad, variable y fecha de referencia | Definición, valor, unidad, período efectivamente medido, fuente y fecha anterior al tratamiento |
| Eventos eléctricos | Cambio de red, generación u otra gran carga | Activo, localización o conexión, tipo, fecha operativa, magnitud y evidencia |
| Panel analítico | Unidad territorial y período | Resultado, cobertura, composición de nodos, primera entrada, tratamiento, cohorte, covariables y reglas aplicadas |

La correspondencia geográfica y la eléctrica serán relaciones separadas. La barra físicamente más cercana no se considerará conexión acreditada sin evidencia.

## Reglas de registro

1. Separar anuncio, aprobación, construcción, energización, pruebas, operación y expansión. Ninguno reemplaza automáticamente a otro.
2. Conservar incertidumbre temporal: una fecha conocida solo por año o un límite de presencia previa no se convierte en un día preciso.
3. Distinguir identificadores de instalación, campus y fase para evitar contar un cambio de nombre o propietario como una nueva entrada.
4. Mantener como desconocida la presencia no investigada. La búsqueda sin resultados se documenta, junto con sus límites.
5. Conservar precios originales y sus revisiones. Registrar intervalos faltantes, valores cero y cambios de frecuencia; un cero observado no es un dato faltante.
6. Registrar capacidad nominal, potencia conectada y demanda efectiva como magnitudes diferentes, con unidades y fuentes propias. Estos campos pueden ayudar a caracterizar casos, pero no son indispensables para el tratamiento binario base.
7. Usar covariables cuyo período de medición sea anterior al tratamiento. Una publicación posterior puede describir un período previo; ambas fechas deben quedar registradas.

## Secuencia de construcción

Primero se documentará qué medida de precio puede observarse y a qué resolución. En paralelo se definirá el universo de centros y se reunirá su historia operativa. Con esas dos piezas se elegirá la unidad geográfica y una ventana candidata, con justificación explícita.

Después se construirá una tabla de soporte que cuente unidades únicas tratadas, cohortes, comparadores y períodos disponibles. Este diagnóstico precederá al emparejamiento y a las regresiones. También identificará nodos nuevos, fechas inciertas y exposición compartida.

Si hay soporte, se fijarán muestra, resultado, agregación, covariables, ponderación y reglas de inferencia. Si hace falta cambiar alguno de los elementos centrales del original, se explicará la modificación y el parámetro que pasa a estimarse.

## Registro de decisiones

Cada decisión posterior conservará fecha, evidencia, alternativas consideradas, elección, efecto sobre la interpretación y si se tomó antes o después de observar resultados. La existencia de exploraciones anteriores en el directorio se declarará cuando corresponda; empezar una carpeta nueva no convierte el trabajo en un estudio prerregistrado.

La decisión inicial del 1 de octubre de 2026 es construir primero la réplica base y evaluar extensiones posteriormente. No hay aún decisiones adoptadas sobre comuna, barra de referencia, período chileno, tamaño de muestra o efecto esperado.
