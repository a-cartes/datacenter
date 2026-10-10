# Diseño comparado y evaluación prospectiva de centros de datos

Propuesta del 2 de octubre de 2026. Orientación solicitada: conservar la réplica histórica, comparar Virginia y la Región Metropolitana y evaluar impactos hacia 2030, con aspiración de publicación en Energy Economics. Este documento define el trabajo siguiente; no presenta proyecciones calculadas ni nuevos efectos causales estimados.

## Pregunta y contribución

¿Bajo qué condiciones de oferta y transmisión la expansión de centros de datos encarece la electricidad, y qué costos podría evitar la Región Metropolitana mediante inversiones oportunas y una mejor localización hacia 2030?

La contribución propuesta es explicar la respuesta de los costos eléctricos a nuevas cargas digitales en sistemas con condiciones distintas de demanda, generación y red. Virginia sirve como referencia empírica de una industria de mayor escala; la RM permite estudiar un sistema con expansión digital y oportunidades de aprovechar energía renovable. No se presupone que la RM recorra la misma trayectoria ni que el efecto histórico tenga que coincidir en signo, tamaño o significancia.

La hipótesis de trabajo es que la respuesta depende de la carga efectivamente conectada respecto de la capacidad disponible para abastecerla en el lugar y hora requeridos. Un crecimiento reducido del consumo agregado puede coexistir con presión local sobre la red. También puede coexistir con aumentos en centros de datos compensados por otros sectores. El estancamiento agregado, por sí solo, no prueba ausencia de impacto.

## Tres componentes de un mismo artículo

| Componente | Trabajo | Resultado que puede sostener |
|---|---|---|
| Réplica histórica | Mantener entrada, matching, diferencias en diferencias y estudio de eventos del artículo, documentando adaptaciones institucionales | Estimación histórica y evaluación de los supuestos para interpretarla causalmente |
| Comparación Virginia y RM | Comparar carga digital, demanda regional, recursos de generación, restricciones y respuesta histórica de precios con definiciones compatibles | Evidencia sobre mecanismos y condiciones de aplicación de los resultados |
| Evaluación prospectiva | Simular expansión digital con y sin refuerzos de red bajo supuestos explícitos | Impacto ex ante condicionado al modelo y costo evitable de retrasos o localizaciones alternativas |

La comparación no convierte a Virginia en control de la RM. Una regresión entre dos series regionales no reemplaza los contrafactuales territoriales de la réplica. Si solo se dispone de los resultados publicados de Virginia, se utilizarán como referencia; una nueva estimación comparada requiere sus microdatos y reglas de construcción.

## Réplica con decisiones cerradas

Conservar la especificación original como referencia y terminar la corrección de los errores identificados en AUDITORIA_REPLICA.md. Fijar una regla uniforme para entradas durante el año y una sensibilidad al primer año completo. Una inauguración al final de diciembre puede justificar esa sensibilidad, pero el mes no debe suponerse sin evidencia. No seleccionar la regla según el coeficiente obtenido.

Usar la incorporación de nodos al promedio territorial de manera consistente con el artículo. Resolver las incertidumbres que cambien tratamiento, comparación o resultado; llevar las comprobaciones secundarias al apéndice. No abrir nuevas variantes salvo evidencia que invalide una decisión o una prueba necesaria del mecanismo.

El matching mejora comparación en observables, pero no convierte por sí solo una fecha de entrada en exógena ni elimina exposición compartida. Los errores estándar, intervalos y pruebas deben corresponder a la misma muestra y estimador. El resultado histórico conservará la incertidumbre que efectivamente tengan los datos.

## Comparación económica

Construir una figura anual y una tabla con un período común, usando la RM y Virginia como territorios de comparación y el SEN y PJM como contexto de sus sistemas interconectados. Evitar comparar directamente el consumo nacional de Chile con el de un estado para inferir diferencias de presión regional.

| Dimensión | Medida preferida |
|---|---|
| Escala digital | Demanda eléctrica observada de centros de datos; capacidad conectada separada de capacidad anunciada |
| Penetración | Consumo de centros de datos dividido por demanda regional, con igual definición y cobertura |
| Evolución de la demanda | Demanda regional y descomposición sectorial, cuando exista información compatible |
| Disponibilidad de suministro | Oferta accesible, restricciones de importación o transmisión y entrada de infraestructura |
| Resultado comparable | Costos marginales y diferencias espaciales, declarando la diferencia entre precios chilenos y componentes PJM |
| Costos a consumidores | Análisis separado si se incorpora una traducción explícita a contratos y tarifas |

La IA forma parte de las cargas de centros de datos y no se sumará como una demanda adicional independiente. La electromovilidad y las demás cargas se incorporarán al escenario de demanda de fondo; no serán tratamientos nuevos en este artículo.

## Evaluación hacia 2030

La opción preferida es un modelo de despacho con restricciones de transmisión, calibrado con datos chilenos y contrastado con precios y desacoples históricos. Los datos de precios ya construidos sirven para esa validación. Todavía debe verificarse la disponibilidad de topología, capacidades de transferencia, costos de generación y perfiles de carga suficientes para implementarlo.

La cantidad principal será el cambio de costo de operación del sistema y la respuesta de precios atribuibles a la expansión digital. Para cada escenario, comparar el mismo año 2030 bajo idéntico clima, combustibles, otras demandas e infraestructura, variando únicamente la carga de centros de datos respecto de su nivel de referencia. Es una evaluación condicionada al modelo; no un efecto futuro observado.

| Escenario | Demanda digital | Infraestructura |
|---|---|---|
| Referencia | Nivel del año base, sin expansión adicional | Obras previstas bajo el calendario elegido |
| Expansión con obras oportunas | Trayectoria central de proyectos que efectivamente podrían entrar | Calendario previsto |
| Expansión con retrasos | Misma trayectoria digital | Retrasos de obras críticas definidos previamente |
| Expansión con localización alternativa | Igual demanda digital total | Distribución entre conexiones factibles, con sus costos de adaptación |

Para aislar el efecto de los centros en el escenario de retrasos, calcular también su contraparte sin expansión digital y con esos mismos retrasos. Para estimar el costo evitable de obras oportunas, comparar ambas infraestructuras con la misma demanda. Presentar por separado el ahorro operativo bruto y los costos de inversión; no llamar beneficio neto al primero.

Evaluar sensibilidad a demanda digital menor y mayor, hidrología, disponibilidad de generación y utilización de los centros. Convertir potencia a energía con perfiles horarios y utilización explícitos. Aplicar PUE únicamente si el punto de partida es potencia informática y no demanda eléctrica total del establecimiento.

No multiplicar el ATT de Virginia por tres, por el número de proyectos o por los MW futuros: el coeficiente de una primera entrada territorial no es una elasticidad ni un costo por MW. Si falta información suficiente para el despacho, limitar la salida a escenarios de demanda y exposición; no presentar una regresión predictiva como evaluación causal de precios.

Validar el modelo fuera del período usado para calibrarlo, incluyendo niveles de precios y episodios de restricciones. La evidencia histórica puede disciplinar sus supuestos; no debe imponerse el signo de Virginia como condición para aceptar la validación.

## Fuentes revisadas y alcance

- [JLARC, Data Centers in Virginia, 2024](https://jlarc.virginia.gov/landing-2024-data-centers-in-virginia.asp): informa que la demanda estatal estuvo esencialmente plana entre 2006 y 2020 y presenta una proyección de fuerte crecimiento impulsada por centros de datos. Esto hace pertinente estudiar transiciones de escala, pero no demuestra que Chile vaya a repetirlas.
- [Publicación institucional del Coordinador](https://es.linkedin.com/posts/coordinador-el%C3%A9ctrico-nacional_datacenters-demandael%C3%A9ctrica-planificaci%C3%B3nenerg%C3%A9tica-activity-7379587532046516224-ZGFx): proyecta más de 1.300 MW de demanda de centros de datos hacia 2032 y una concentración del 80% en la RM. Es una comunicación prospectiva, no consumo observado. No equivale a triplicar la demanda total chilena. Para parametrizar 2030 debe recuperarse la trayectoria y versión del estudio técnico correspondiente.
- [Portal de proyecciones del Coordinador](https://www.coordinador.cl/desarrollo/graficos/planificacion-de-la-transmision/proyeccion-de-demanda-de-largo-plazo/): punto de partida para identificar escenarios oficiales y fechas de corte.
- [Publicación de Ana Lía Rojas aportada por el usuario](https://es.linkedin.com/posts/ana-lia-rojas_la-demanda-el%C3%A9ctrica-se-estanc%C3%B3-la-oferta-activity-7507764478084714497-A71k): plantea el desacople entre expansión de oferta y crecimiento reducido de demanda. Se utilizará como motivación, contrastando las cifras con series oficiales.
- [CENTRA sobre precios residenciales](https://centra.uai.cl/solo-lo-supera-guatemala-el-precio-de-la-electricidad-en-chile-es-el-segundo-mas-caro-de-latinoamerica/?lang=en): describe tarifas de hogares, no el componente espacial mayorista del artículo.
- Los enlaces de Environment Virginia y Forbes aportan discusión pública. No se usarán para atribuir causalmente tarifas a centros de datos. El video enlazado no pudo recuperarse y no se le atribuyen contenidos.

El texto pegado por el usuario es material de referencia pendiente de verificación. Su tabla presenta descensos en 2023 y 2024, mientras la publicación enlazada describe 2025 como primer registro negativo del siglo. Esas series no deben combinarse sin identificar definiciones y fuentes. Esta comprobación se resolverá al construir la figura comparada, sin convertirse en un proyecto separado.

## Entregables y criterio editorial

Los siguientes resultados concretos son: una tabla comparada con definiciones homogéneas; una réplica histórica corregida; una validación del mecanismo y del modelo; y una tabla de escenarios con costos, precios e incertidumbre. Las nuevas descargas se limitarán a datos que alimenten alguno de esos resultados.

Energy Economics es el destino aspiracional indicado por el usuario. La contribución propuesta deberá sostenerse en un mecanismo económico identificable, un contrafactual defendible y una evaluación cuantitativa reproducible. Una comparación descriptiva acompañada de matching y proyecciones agregadas no garantiza por sí sola una contribución suficiente. No se ha confirmado novedad mediante una revisión completa de la literatura ni evaluado probabilidad de aceptación. La página editorial consultada no fue accesible.

Título provisional de trabajo: Data center growth and electricity network constraints: Evidence from Virginia and prospective impacts in Santiago.
