# Protocolo de réplica sobre centros de datos y precios eléctricos en la Región Metropolitana

Este protocolo organiza una investigación nueva a partir del artículo de Mamkhezri, Sun y Yang, versión de marzo de 2026. Define la réplica base y deja explícitas las decisiones que requieren información chilena. Es un diseño inicial fechado el 1 de octubre de 2026; no constituye un prerregistro ni certifica la factibilidad de la estimación.

## Pregunta de investigación

¿Cuál es el efecto causal de la entrada de centros de datos en la Región Metropolitana sobre el componente de los precios mayoristas de electricidad asociado a congestión y pérdidas de transmisión?

Esta pregunta conserva el objeto económico del original. Su implementación depende de identificar una medida comparable en Chile y un conjunto creíble de unidades de comparación. El término causal expresa el objetivo del diseño; la interpretación de los resultados dependerá de sus supuestos y de la evidencia disponible.

## Objetivo general y objetivos específicos

El objetivo general es estimar el efecto de la primera entrada de centros de datos en unidades territoriales de la Región Metropolitana sobre el componente espacial de los precios mayoristas asociado a congestión y pérdidas, siguiendo la estrategia del artículo de referencia.

Los objetivos específicos son:

1. Establecer la correspondencia entre el resultado medido en el artículo y la información eléctrica disponible para Chile.
2. Reconstruir la primera operación de centros de datos por unidad de análisis, incluyendo la presencia anterior a la ventana de estudio.
3. Construir un panel de precios y características previas al tratamiento con cobertura, geografía y agregación documentadas.
4. Estimar efectos medios y dinámicos mediante diferencias en diferencias con entradas en distintos momentos, si la muestra lo permite.
5. Evaluar comparabilidad, tendencias previas, efectos sobre zonas de comparación y sensibilidad a decisiones de construcción del panel.

## Hipótesis y significado del efecto

El mecanismo del artículo sugiere que una nueva carga localizada puede aumentar la congestión y las pérdidas de transmisión. Esta es una hipótesis para contrastar en Chile. La estimación admitirá efectos positivos, nulos o negativos y reportará su incertidumbre.

El parámetro de interés es el efecto medio posterior a la entrada en las unidades tratadas elegibles, respecto de la trayectoria que habrían seguido sin esa entrada. Se definirán los pesos por cohorte y período antes de la estimación final. La comparación espacial no identifica por sí sola un aumento de precios común a todo el sistema ni un cambio en la cuenta de electricidad de los hogares.

## Alcance de la primera etapa

La réplica base conservará la primera operación como evento principal, el componente de congestión y pérdidas como resultado objetivo, y la comparación de trayectorias entre unidades tratadas y comparables como estrategia.

Las ampliaciones se registrarán para comprender la historia de las instalaciones, pero no se convertirán en primeras entradas. La estimación posterior a la primera entrada puede recoger la evolución posterior de la actividad en esa unidad, incluidas ampliaciones; no debe interpretarse automáticamente como el efecto aislado del primer edificio.

Las estimaciones por intensidad de consumo, nuevas preguntas distributivas y otros mecanismos chilenos se evaluarán una vez construida y examinada la réplica base. Las mejoras necesarias para medir correctamente el tratamiento, el resultado y la incertidumbre forman parte del trabajo de réplica.

## Correspondencia entre el artículo y Chile

| Elemento | Artículo original | Decisión para la réplica |
|---|---|---|
| Territorio de interés | Virginia | Región Metropolitana |
| Unidad | Sector censal por año | Unidad territorial estable por seleccionar; comuna no queda impuesta |
| Período | 2015 a 2024 | Según cobertura homogénea y soporte anterior y posterior a la entrada |
| Tratamiento | Primera operación desde 2017 en la muestra elegible | Primera operación verificada dentro de la ventana que se defina |
| Resultado | Congestión más pérdidas marginales, en USD/MWh | Equivalencia o reconstrucción por documentar |
| Comparación | Sectores sin entrada durante la muestra | Unidades elegibles con historia conocida y exposición indirecta evaluada |
| Emparejamiento | Probit y diez vecinos con reemplazo | Referencia inicial, condicionada a covariables y soporte común |
| Estimador principal | Sun y Abraham | Referencia principal si existe soporte para el diseño |
| Contrastes | Callaway y Sant’Anna y efectos fijos de unidad y año | Comparaciones metodológicas, con sus límites documentados |

No hay una barra de referencia seleccionada. Si solo fuera posible utilizar diferencias de costos marginales entre barras, se documentaría como una adaptación de la variable y de su interpretación; no se denominaría automáticamente congestión más pérdidas.

## Tratamiento y unidades de comparación

Para cada unidad se identificará el año de primera operación, denominado G. La variable de tratamiento valdrá cero antes de G y uno desde G, siguiendo la definición persistente del original. Los casos de cierre o interrupción sostenida requerirán una regla explícita.

Las fechas de anuncio, permiso, construcción, energización, pruebas e inicio de operación se distinguirán. Si una fuente solo permite establecer un intervalo, se conservará esa incertidumbre. El año de entrada puede contener meses anteriores a la operación; ese punto se considerará al interpretar el efecto contemporáneo.

Las unidades con centros anteriores al período elegible no se clasificarán como controles por carecer de aperturas recientes. Tampoco se interpretará la ausencia de información como ausencia de centros.

La RM delimita las entradas de interés. El universo de comparación se justificará por comparabilidad y exposición eléctrica; cualquier incorporación de unidades externas quedará declarada como adaptación geográfica. La pertenencia a comunas distintas no garantiza ausencia de efectos compartidos.

## Precios y construcción del panel

La unidad territorial debe permitir relacionar ubicación, precios y características previas de manera reproducible. La ubicación de una barra y la conexión efectiva de un centro son relaciones distintas y tendrán fuentes separadas.

El original promedia precios de nodos dentro de sectores censales e incorpora nodos nuevos. Se documentarán la vigencia y composición de los nodos chilenos para distinguir variaciones de precio de cambios en el conjunto observado. Una geografía fija no elimina por sí sola este problema.

Se establecerán reglas de cobertura, datos faltantes, versiones de precios, zona horaria, unidades y agregación antes de comparar efectos posteriores. La frecuencia anual es la referencia del artículo; utilizar otra frecuencia requerirá una razón explícita.

## Estimación e interpretación

La estrategia de referencia combina emparejamiento con variables anteriores al tratamiento y diferencias en diferencias para entradas escalonadas. El estudio de eventos mostrará las trayectorias relativas al período anterior a la entrada, con intervalos de confianza y número de unidades que sustenta cada horizonte.

Antes de estimar se resolverán la ponderación del emparejamiento, el soporte común, los horizontes temporales y la inferencia. La ficha del original registra una particularidad importante: pondera las copias de controles por el inverso de su frecuencia de duplicación.

Las tendencias paralelas y la ausencia de anticipación requieren justificación. Coeficientes previos no significativos no prueban esos supuestos. También se documentarán cambios concurrentes de generación, transmisión y otras grandes cargas. Las obras inducidas por los propios centros pueden ser mecanismos del efecto y no se introducirán automáticamente como controles.

La incertidumbre debe reflejar las unidades independientes de tratamiento y su dependencia por red. Aumentar la frecuencia temporal no sustituye disponer de más unidades tratadas. Con pocos grupos se evaluará la inferencia apropiada y, si el soporte es insuficiente, se reportará ese límite antes de presentar una conclusión causal.

## Productos de la réplica base

1. Matriz de correspondencia y disponibilidad de datos para Chile.
2. Inventario histórico de instalaciones y primeras entradas, con fuentes y precisión temporal.
3. Panel reproducible y resumen de cobertura, unidades tratadas, cohortes y controles.
4. Tabla de comparabilidad y balance antes y después del emparejamiento.
5. Efecto medio, estudio de eventos y pruebas de sensibilidad, si el diseño es viable.
6. Discusión de diferencias respecto de Virginia y límites de interpretación.

La viabilidad se juzgará por equivalencia de medida, historia verificable, soporte temporal y comparaciones defendibles. Si alguna condición falla, se describirá la adaptación necesaria. Las decisiones no se seleccionarán buscando reproducir el signo o la significancia del original.

## Estructura del futuro artículo

| Sección | Contenido previsto |
|---|---|
| Introducción | Pregunta, motivación chilena y contribución como réplica adaptada |
| Marco conceptual e institucional | Mecanismo de demanda localizada y funcionamiento relevante del mercado chileno |
| Datos y construcción de variables | Fuentes, fechas, ubicación, precios, cobertura y correspondencia con el original |
| Estrategia empírica | Selección de muestra, emparejamiento, estimación y supuestos |
| Resultados de la réplica | Efectos medios y dinámicos, con incertidumbre |
| Robustez y limitaciones | Sensibilidad, exposición indirecta, composición de nodos y eventos concurrentes |
| Discusión para Chile | Alcance de los hallazgos para infraestructura y localización de proyectos |
| Conclusiones | Respuesta respaldada por la evidencia y preguntas posteriores |

Las secciones de resultados son una estructura futura, no hallazgos anticipados. Una eventual extensión tendrá una pregunta y resultados identificables por separado.

## Fuente metodológica

Mamkhezri, J., Sun, X. y Yang, Y. (marzo de 2026). *The Hidden Cost of the Cloud: Data Centers and Transmission-Induced Electricity Prices*. SSRN 5736562. La correspondencia detallada con las páginas del ejemplar aportado se encuentra en [la ficha del artículo](FICHA_ARTICULO.md).
