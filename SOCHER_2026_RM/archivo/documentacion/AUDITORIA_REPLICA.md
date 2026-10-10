# Auditoría de datos y estimación de la réplica

Revisión del 2 de octubre de 2026, posterior a los resultados originales. Esta auditoría responde a la posibilidad de que problemas de datos, programación o adaptación metodológica expliquen los resultados. Se encontraron problemas concretos de inferencia presentada, fechas y correspondencia con el artículo. Las pruebas realizadas reproducen la aritmética del panel y del estimador; no validan todavía la identificación causal.

No corresponde describir la estimación principal de +1,32 USD/MWh como un efecto cero. Es una estimación positiva cuya interpretación causal y precisión requieren revisión. Las nuevas comprobaciones y escenarios se guardan por separado, conservando las bases y estimaciones anteriores.

## Hallazgos que requieren corrección

### El valor p corresponde a otra especificación

En `scripts/estimar.R`, la llamada `ri(F, "D")` utiliza la muestra completa sin emparejar. Su estadístico CS observado es 1,074658 y su p de permutaciones es 0,3515. El ATT principal de Sun y Abraham es 1,322219 en la muestra emparejada. El p de la primera especificación no debe presentarse como inferencia de la segunda. Lo mismo afecta la interpretación de las columnas de permutaciones de las tablas de sensibilidad: no siempre conservan la muestra tratada tras excluir unidades fuera del soporte.

La reasignación aleatoria de fechas entre los 60 distritos tampoco demuestra por sí misma que exista un mecanismo de asignación intercambiable. Hasta justificar ese supuesto, corresponde describirla como ejercicio de permutaciones. El intervalo publicado usa 1,96 veces el error estándar, mientras el p convencional de fixest usa su propia corrección de grados de libertad; la presentación de intervalos y p también debe armonizarse.

### La fecha de ST01 necesita actualizarse con evidencia anterior

El inventario usa noviembre de 2023 como cota superior documentada para ST01. Sin embargo, [InvestChile, Servicios globales e industria tecnológica en Chile, marzo de 2026, página 14](https://tools.investchile.gob.cl/hubfs/01-%20Descargables%20InvestChile/Ebooks%20sectoriales/Servicios%20Globales/InvestChile_ebook_servicios%20globales.pdf?hsLang=en-gb), identifica 2022 como año de inauguración del primer centro de ODATA en Lampa. Además, [el comunicado de Aligned del 13 de diciembre de 2022](https://www.globenewswire.com/news-release/2022/12/13/2572713/0/en/aligned-data-centers-to-acquire-odata.html) ya describe instalaciones operativas de ODATA en Chile, aunque no individualiza ST01 en ese párrafo.

Esto aporta evidencia para revisar la cota superior de operación. No establece el día del primer consumo eléctrico. Se calculó un escenario con inauguración en 2022, manteniendo muestra, pesos y las otras fechas: el ATT pasa de 1,322219 a 1,282431 USD/MWh.

La cota inferior de ST01 en mayo de 2021 proviene del inicio de construcción. Tratarla automáticamente como entrada operativa no constituye una alternativa igualmente acreditada. El cambio de signo del escenario G_min no debe presentarse como evidencia de fragilidad entre dos fechas operativas verificadas. Otras sensibilidades de controles y geografía siguen pendientes de resolver.

### El panel principal no incorpora los nodos nuevos como el artículo

El artículo, página 7 del PDF original, incorpora los nodos nuevos al promedio territorial. La especificación principal local exige nueve años completos a cada barra. Por ello, en Colina-3 solo promedia BATUCO 13 y 110 kV y excluye CANTERAS, que aparece en 2024. La variante no balanceada ya existente se aproxima más a la regla del artículo, aunque mantiene un mínimo de cobertura anual del 90%.

La auditoría separa el efecto de cambiar barras del de cambiar los controles seleccionados:

| Escenario con las fechas originales | ATT USD/MWh |
|---|---:|
| Barras balanceadas y emparejamiento original | 1,322219 |
| Incorporación de barras de la variante no balanceada, mismos distritos y pesos | 1,336164 |
| Variante no balanceada con su propio emparejamiento | 1,015139 |

En esta muestra, la exclusión de barras nuevas no explica por sí sola la falta de un resultado causal concluyente. La diferencia entre 1,32 y 1,02 mezcla cambios de barras y de comparación.

### Otras afirmaciones que deben acotarse

- La escolaridad está pendiente de extracción de microdatos de personas. Su ausencia en las capas geográficas utilizadas no demuestra que sea imposible construirla por distrito.
- La equivalencia de coeficientes de P y D se cumple numéricamente en la especificación principal, pero no exactamente en todas las variantes: en distrito no balanceado, ATT(P) menos ATT(D) es aproximadamente −0,000684 USD/MWh. Las coberturas temporales distintas pueden hacer que la referencia anual agregada varíe entre unidades. La diferencia es pequeña, pero la afirmación de igualdad universal debe corregirse.
- Los coeficientes previos del estudio de eventos corresponden a distintas composiciones de cohortes y a muy pocos tratados. Deben revisarse por cohorte y con fechas corregidas antes de atribuir su forma exclusivamente a una tendencia previa común.
- La cantidad de grupos tratados limita la inferencia, pero no es por sí sola una prueba matemática de que ningún diseño causal sea posible. Tampoco el número de archivos descargados mide la cantidad de eventos independientes.

## Comprobaciones realizadas

| Comprobación | Resultado |
|---|---|
| Reestimación de Sun y Abraham sobre la muestra guardada | Reproduce 1,322219 |
| Reconstrucción independiente por diferencias cohorte y año frente a controles nunca tratados | Reproduce 1,322219 |
| TWFE sobre la muestra guardada | Reproduce 0,439277 |
| Datos sintéticos con efectos conocidos de −2,4914, cero y +2,4914 | Ambos estimadores recuperan los valores con error menor a 0,0000001 |
| Añadir 2,4914 únicamente a tratados después de la entrada, sobre la muestra real | El ATT aumenta exactamente en 2,4914 |
| Añadir 2,4914 a todas las unidades desde el mismo año en el panel sintético | Los efectos de año lo absorben; el ATT es aproximadamente cero |
| Reconstrucción barra y año desde las sumas mensuales | Error máximo cero |
| Reconstrucción distrito y año desde las barras balanceadas y el diccionario geográfico | Error máximo inferior a 0,000000000000002 |
| Reconstrucción desde precios horarios extraídos en enero de 2017, diciembre de 2022, ambos segmentos de julio de 2024 y diciembre de 2025 | Reproduce las medias mensuales guardadas |
| Contraste con 96 celdas del libro original de enero de 2017, cuatro barras durante el 15 de enero | Coincidencia exacta |
| Claves de barra y año, copias de unidad y año y peso total de cada unidad y año | Sin duplicados en esas claves; peso total uno |

Estas pruebas descartan fallos en las operaciones verificadas. No reextraen todos los originales ni prueban la exactitud de todas las coordenadas, el primer consumo eléctrico, la independencia de controles o la potencia estadística del diseño.

El ejercicio sintético de señal común explica una limitación sustantiva: un aumento compartido por tratados y controles puede desaparecer de una estimación de diferencias. Eso no demuestra que tal contaminación ocurra en los datos reales; indica qué debe comprobarse con las conexiones eléctricas.

## Qué miden efectivamente los tres distritos

| Centro utilizado para definir la entrada | Barras del resultado principal |
|---|---|
| EdgeConneX en Colina-3 | BATUCO 13 y 110 kV, a unos 4,1 km del sitio inventariado |
| ODATA ST01 en Lampa-4 | LAMPA 220 kV, a unos 3,0 km del punto aproximado inventariado |
| ODATA ST02 en San Bernardo-11 | Tres barras de CHENA, dos de LAS ACACIAS y PANAMERICANA 12 kV |

La asignación sigue polígonos censales. Estas distancias no demuestran ni descartan conexión eléctrica. En particular, no debe describirse el resultado territorial como si midiera exclusivamente la barra donde retira energía cada centro. La localización de ST01 también sigue siendo provisional.

## Orden para cerrar la réplica

1. Registrar las nuevas fuentes y separar construcción, inauguración, energización y operación comercial de los tres eventos. Resolver ST01 y la diferencia 2020 frente a 2021 de EdgeConneX antes de elegir una fecha principal revisada.
2. Documentar la correspondencia entre cada instalación, distrito y barras que realmente entran al promedio. Completar la verificación de la ubicación de ST01 y de controles con exposición eléctrica compartida.
3. Completar escolaridad, revisar soporte y declarar qué covariables son sustitutas. Conservar el criterio del artículo para la incorporación de nodos, documentando diferencias inevitables de cobertura.
4. Reestimar una especificación revisada fijada por esas evidencias, con intervalos y pruebas referidos a la misma muestra, estimador y efecto. No escoger fechas, geografía o controles según el signo o el valor p.
5. Mantener las estimaciones anteriores como trazabilidad. La réplica revisada y la extensión por potencia conectada deben distinguirse explícitamente.

## Archivos de comprobación

Los programas `scripts/auditar_estimacion.R` y `scripts/auditar_panel.py` reproducen esta auditoría y escriben solo en `resultados/auditoria_20261002/`. Allí se conservan las comprobaciones numéricas, la descomposición del ATT por cohorte y año, los seis escenarios de fechas y las barras efectivamente tratadas. No se sobrescribieron datos ni estimaciones de la réplica original.
