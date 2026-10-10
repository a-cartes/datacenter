# Disponibilidad de fuentes chilenas para la réplica

Revisión al 1 de octubre de 2026. Se investigaron fuentes primarias y se descargaron dos muestras nuevas del Coordinador Eléctrico Nacional. El trabajo se realizó desde el diseño de esta carpeta, sin incorporar bases ni clasificaciones de la investigación anterior.

## Resultado de esta etapa

Hay fuentes utilizables para comenzar la construcción de datos: precios por barra y antecedentes de cálculo, documentos de operación de centros de datos y estadísticas territoriales. La equivalencia exacta con la variable de Virginia, la primera entrada por unidad territorial y los controles todavía requieren resolución.

El avance más concreto es que los archivos eléctricos incluyen factores de penalización y antecedentes de subsistemas o centrales marginales. Por tanto, podemos investigar la medida de transmisión con información adicional al precio final. Esto no acredita aún una descomposición chilena idéntica a la del artículo.

## Matriz de disponibilidad

| Necesidad | Evidencia localizada y examinada | Alcance verificado | Falta resolver |
|---|---|---|---|
| Precios históricos por barra | Archivo definitivo de diciembre de 2017 del Coordinador | 1.235 columnas de barras únicas y 744 períodos horarios en la hoja de dólares | Cobertura del resto de los años, barras relevantes para RM y cambios de nombres |
| Precios recientes y versiones | Archivo definitivo del 15 de julio de 2024 del Coordinador | 1.500 barras con 96 intervalos de 15 minutos; columnas de precios en línea, preliminares y reales en el comparativo | Continuidad histórica y correspondencia de versiones |
| Pérdidas y red | Factores, mapeos y subsistemas en las muestras oficiales | Factores históricos por bloques; factores recientes por intervalo y registros de desacople | Conciliar referencias, factores ajustados y precios, a igual frecuencia |
| Fechas de centros de datos | Siete casos revisados mediante operadores, memorias y comunicados | Disponibilidad de hitos de operación o inauguración, con distintos grados de precisión | Inventario exhaustivo, primera entrada territorial y conexión eléctrica |
| Geografía y demografía | Portales y manuales del INE para censos 2002, 2017 y 2024 | Distintas escalas disponibles en microdatos, agregados y cartografía | Descargar extractos, verificar variables y homologar límites |
| Ingreso previo | CASEN y estimaciones de pobreza comunal del Ministerio de Desarrollo Social | Fuentes disponibles con restricciones de representatividad y concepto | No hay equivalencia automática al ingreso mediano de los sectores censales de Virginia |

Los conteos eléctricos son del conjunto nacional de cada archivo de muestra; no representan barras de la RM ni unidades de tratamiento. Los siete casos documentales tampoco son siete unidades tratadas.

## Qué comprobamos en los archivos eléctricos

La [publicación histórica de 2017](https://www.coordinador.cl/mercados/documentos/transferencias-economicas/costos-marginales-de-energia/2017-costos-marginales-de-energia/) ofrece el archivo definitivo de diciembre. La hoja de precios examinada contiene 918.840 posiciones de barra por hora, de las cuales 1.512 están vacías. El libro también incluye factores de penalización, centrales marginales por barra y costos de centrales. Se leyeron los datos guardados, sin ejecutar macros ni recalcular el libro.

La [publicación del 15 de julio de 2024](https://www.coordinador.cl/mercados/documentos/costo-marginal-real/2024-costo-marginal-real-transferencias-economicas/julio-2024-costo-marginal-real-transferencias-economicas/15-julio-2024-costo-marginal-real-transferencias-economicas/) ofrece un paquete definitivo y otro preliminar. Se descargó el definitivo, publicado el 24 de julio. Cada uno de sus dos CSV de precios tiene 144.000 filas, sin claves repetidas ni precios reales vacíos en la inspección. El paquete contiene 147.360 registros de factores y archivos de mapeo y subsistemas. Estos conteos no prueban equivalencia de sus universos: todavía falta cruzar las claves entre archivos.

El [portal de costos marginales](https://www.coordinador.cl/costos-marginales/) separa explícitamente el histórico hasta el 14 de julio de 2024 y la publicación nueva desde el día siguiente. Además, distingue versiones en línea, preliminares y reales. Unir períodos exige documentar frecuencia, metodología y revisión, no solo concatenar archivos. El corte no determina por sí solo un salto estadístico de precios.

Los datos originales y la inspección reproducible están descritos en [las muestras de precios](fuentes/precios/README.md). Los archivos examinados acreditan acceso y estructura, no un panel multianual terminado.

## Qué significa esto para la pregunta del artículo

La [nota de comparabilidad](COMPARABILIDAD_PRECIOS.md) distingue tres objetos: el precio total de una barra, una diferencia respecto de una referencia y el componente de congestión más pérdidas. No son automáticamente la misma variable.

Existe, sin embargo, una propiedad útil: en una regresión lineal con efectos temporales completos, restar a todas las unidades una misma serie temporal deja inalterado el coeficiente del tratamiento, manteniendo iguales muestra, pesos y demás regresores. Esta es una deducción algebraica, no un hallazgo empírico chileno. En promedios anuales requiere que la referencia agregada sea común; coberturas horarias distintas pueden romper esa condición. La propiedad ayuda a conservar la lógica de comparación del artículo, pero no demuestra que cualquier diferencial sea una descomposición física observada.

Por ahora se mantiene la pregunta acordada y la variable final continúa abierta. El siguiente paso de medición será conciliar precios, factores y subsistemas en intervalos concretos. Si solo se valida un resultado relativo, la adaptación se declarará dentro de la réplica base.

## Fechas y geografía

La [revisión de fechas](FUENTES_OPERACION.md) confirma por qué debemos separar instalación y unidad territorial. SONDA documenta un centro de Quilicura anterior a la puesta en marcha de Google en 2015. El lanzamiento posterior de otra instalación en esa comuna no puede tratarse como primera entrada comunal. Microsoft, por otra parte, comunica una región operativa con varias ubicaciones; ese anuncio no permite asignar una fecha eléctrica a cada sitio.

La [nota sobre geografía y covariables](GEOGRAFIA_Y_COVARIABLES.md) muestra que hay opciones más finas que la comuna, pero su utilidad depende de precios y exposición. El Censo 2024 no es una línea base válida para centros que ya operaban antes de su levantamiento. Elegir una unidad más pequeña tampoco garantiza independencia eléctrica ni resuelve por sí solo la identificación.

## Decisiones que permite tomar esta revisión

1. Utilizar las publicaciones originales del Coordinador como ruta de recolección y conservar sus versiones. Las descargas públicas examinadas permiten avanzar sin condicionar esta etapa a una clave de API.
2. Conservar precios, factores, mapeos y subsistemas juntos. El archivo reducido de precios por sí solo perdería información útil para validar el resultado.
3. Construir el inventario a nivel de instalación y etapa, y derivar después la primera entrada en la geografía seleccionada.
4. Evaluar las covariables según su fecha efectiva y escala, antes de decidir el emparejamiento.

La próxima entrega empírica debe contener la conciliación de una muestra eléctrica y fichas históricas por instalación con localización precisa. Con ello se podrá comparar unidades territoriales candidatas y contar tratamientos y controles defendibles. En esta etapa no se estimaron efectos causales ni se seleccionaron extensiones.
