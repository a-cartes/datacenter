# Diagnóstico de datos para medir carga y efectos zonales

Fecha de corte: 11 de octubre de 2026. Auditoría de archivos existentes, sin cambios en bases anteriores.

## Resultado principal

**Sí disponemos de mediciones que permiten mejorar sustantivamente la exposición eléctrica.** Encontramos y comprobamos retiros comerciales en días muestreados, registros físicos de 15 minutos, series históricas de subestaciones y documentación de conexiones por etapa. El principal trabajo pendiente es vincular esas piezas con una frontera de medición y vigencia histórica verificables, y luego construir comparaciones eléctricas adecuadas.

El enfoque anterior clasificaba primeras entradas en distritos censales. El nuevo pregunta cuánto retiro adicional aparece, por qué conexión y bajo qué condiciones de red. Son objetos distintos: la nueva etapa puede captar rampas de consumo y cambios de conexión que una fecha de inauguración no representa.

## 1. Datos efectivamente encontrados y revisados

| Recurso | Disponibilidad comprobada | Uso y límite concreto |
|---|---|---|
| Originales de demanda | 653 archivos, 26,54 GB; todos existen y conservan el tamaño inventariado | Reextracción selectiva de meses/puntos; no hace falta volver a descargarlos masivamente. Incluyen familias, versiones y archivos que no deben sumarse. |
| Retiros comerciales SIP | 27.425 registros cliente–barra–hora; 21 pares y 11 etiquetas empresariales; 89 fechas entre diciembre de 2023 y julio de 2026 | 18.053 registros no ambiguos con valor; 9.372 ambiguos. Son días muestreados, generalmente 5, 15 y 25, no series mensuales completas. Las etiquetas no equivalen a 11 operadores independientes. |
| Mediciones físicas v7 | 1.862.581 registros de 15 minutos, 30 sockets candidatos, mayo de 2023–agosto de 2026 | Se localizaron las tablas en Descargas y se verificó su identidad con cinco hashes publicados. Los sockets incluyen tránsito, transformadores y extremos de equipos: no representan 30 centros. |
| Las Canteras HT1+HT2 | 21.912 horas por etiquetas y 913 fechas locales, febrero de 2024–agosto de 2026, con abril de 2024 ausente | Agregado recalculado desde ambos HT y conciliado con la tabla anterior; error numérico máximo menor a 2×10⁻¹² kWh. Excluye HT3 y líneas de tránsito. |
| Panamericana | Piloto octubre de 2023–marzo de 2024: 4.392 horas completas, cuatro canales de transformadores | Se reprodujo la frontera D−R heredada. Mide el suministro seleccionado, compartido; falta aislar o acotar la carga del centro. |
| Historia Chacabuco | 24 puntos, 105 meses distintos entre enero de 2018 y septiembre de 2026, cobertura desigual por punto | Aporta antecedentes para examinar etapas y cambios de rotulado. Se mantienen los canales separados. |
| Antecedentes Dataluna | 20.447 valores horarios 2020–2022, 744 en enero de 2023 y 8.548 observaciones hora×canal de febrero–abril de 2023 | Existen tablas, verificadas por hash; unidad/signo y continuidad de las primeras fuentes pendientes de homologación. |
| Precios y red | 117 archivos horarios de precios; panel RM previo; 1.939 aristas y 2.482 fichas de transformadores en los catálogos locales | Disponibilidad no equivale a cobertura homogénea. Hay parámetros de impedancia/capacidad, con distintos estados de certificación; falta una red histórica validada. |
| Inventario y conexión | 63 registros de instalaciones, etapas y proyectos; cartas y matriz de conexiones del cierre anterior | Se generó una tabla de disponibilidad para los 63 registros. La búsqueda por operador produce candidatos, no asignaciones certificadas de carga a cada edificio. |

Fuentes de las cifras: [resumen recalculado](resultados/20261011_inventario_v2/resumen_auditoria.json), [control de tablas v7](resultados/20261011_inventario_v2/comprobacion_mediciones_legacy.json) y tablas de cobertura enlazadas en el índice.

## 2. Casos prioritarios y brechas específicas

| Caso | Conexión/medición disponible | Qué falta para usarlo como exposición |
|---|---|---|
| **EdgeConneX – Las Canteras** | HT1 y HT2, 30 meses observados; HT3 desde octubre de 2024. SIP en CANTERAS_110: 62 fechas, 61 con 24 etiquetas válidas. Carta de energización de paños del 29-05-2024. | Confirmar qué campus/etapas alimenta cada HT y la continuidad de su configuración; determinar frontera de HT3; resolver reloj inicio/fin. El nodo de precios aparece en abril de 2024, por lo que su propio pre es corto. |
| **ODATA ST01 – Batuco/Lampa/Nueva Lampa** | Retiros SIP en Batuco hasta noviembre de 2025 y Lampa desde febrero de 2026. Sockets J9 desde mayo de 2025, JT5 desde junio y ET5 desde agosto de 2025. SAC documenta 30 MW de proyecto. | Conciliar el traslado o coexistencia entre puntos, suministro inicial desde 2022, fechas efectivas y cargas por etapa. No sumar J9/JT5/ET5: pueden medir sucesivamente la misma energía. Los 30 MW solicitados no son retiro observado. |
| **ODATA ST02 – Panamericana/Lo Espejo** | Piloto físico 2023–2024; SIP Panamericana tiene 80 fechas, 37 completas; Lo Espejo aparece en julio de 2026. Sockets ODATA desde mayo de 2025 y Panamericana H3/H4 desde julio. Carta de fin de puesta en servicio del 08-09-2026. | Documentar ruta inicial, transferencia hacia nueva instalación y polaridad de HT/CT. Separar carga ODATA de otros usuarios de Panamericana y ampliar ventana previa. La apertura de 2023 y la puesta en servicio de 2026 corresponden a hitos distintos. |
| **Ascenty – Chacabuco** | SIP CHACABUCO_013 y _023: 86 y 88 fechas completas, respectivamente. Historia física de Chacabuco y ET7. | Enlazar edificios/etapas a empalmes. Confirmar discrepancia de tensión 012/013 entre catálogos. ET7 es suministro compartido y cambió de rotulado D/R: no se atribuye todo a Ascenty. |
| **Google/Dataluna – Chacabuco/Libertadores** | Tres LBR y dos puntos Libertadores, 38–40 meses según canal; SIP Google en TLIBERTADORES_110 con 88 fechas completas. | Cerrar frontera entre suministro directo y distribución; resolver registros ambiguos de Dataluna y signos históricos. La conciliación anterior de LBR con SIP no cierra. |
| **Amazon – Padre Hurtado** | SIP: 33 fechas, solo cuatro completas; sockets E6/E7 desde julio de 2025. | Acreditar campus y usuarios servidos, distinguir tránsito/inyección/retiro y completar registros comerciales. |
| **Scala** | SIP Placilla con 75 fechas completas; también aparecen Chacabuco y Lampa, esta última con registros ambiguos. | Resolver correspondencia con instalación y vigencia; diferenciar movimientos de comercialización y conexiones nuevas. |
| **Sonda y Cirion/antecesores** | Retiros en Quilicura, Chacabuco y otros puntos, con cobertura y conflictos distintos | Construir historia de titulares y empalmes; evitar contar cambios de razón social como nuevas cargas. |
| **Microsoft** | Puntos candidatos documentados en previsiones/conexiones | No se identificó una serie individual en el panel SIP auditado. Hace falta identificar empalmes/medidores y sus denominaciones. Un cero en previsión no representa consumo cero. |
| **Otros registros y proyectos futuros** | Inventario de 63 registros y fuentes existentes | La matriz individual marca pistas por operador y faltantes. Las capacidades futuras se reservan para escenarios; no entran como consumo histórico. |

La [cobertura física](resultados/20261011_inventario_v2/cobertura_fisica_socket.csv) distingue primera observación de fecha de operación. Las fechas de presencia en archivos no se utilizan automáticamente como fechas de tratamiento.

## 3. Dos señales de carga que ya podemos mostrar

**Las Canteras.** En HT1+HT2, el canal de retiro D tiene una potencia media observada de **0,265 MW en junio de 2024**, **2,158 MW en diciembre de 2024** y **9,829 MW en agosto de 2026**. Es una rampa registrada en los equipos seleccionados. Los ceros de febrero y marzo se conservan como valores publicados; no prueban ausencia total de operación del campus. La serie excluye HT3 y no es todavía una medición del consumo total de todas las instalaciones EdgeConneX. [Tabla mensual recalculada](resultados/20261011_inventario_v2/canteras_HT1_HT2_mes.csv).

En la auditoría anterior, para el 15-10-2024, HT1+HT2 suman 49,3031 MWh y el retiro comercial EdgeConneX 49,3194 MWh: diferencia aproximada de −0,033 %. Es una conciliación prometedora de un día, conservada como antecedente; debe extenderse a las fechas disponibles y verificar límites/etiquetas por documentación, sin elegir un desfase por conveniencia estadística.

**Panamericana.** Se recalculó la media de octubre–noviembre de 2023 (**23,141 MW**) y febrero–marzo de 2024 (**24,122 MW**) para los cuatro canales del piloto: diferencia **+0,981 MW, aproximadamente 4,24 %**. Esta comparación incluye estacionalidad y otros consumidores. Sirve para comprobar que tenemos series físicas analizables y orientar la separación del suministro, sin atribuir esa diferencia a ODATA. [Comprobación](resultados/20261011_inventario_v2/comprobacion_panamericana.json).

## 4. Lo que falta, en orden de rendimiento

1. **Cerrar correspondencias, empezando por Las Canteras y las dos rutas ODATA.** Tabla de sitio–etapa–titular–empalme–medidor–barra con inicio/fin de vigencia, fuente y condición exclusiva/compartida/tránsito. Usar primero cartas, actas y catálogos archivados.
2. **Conciliar consumos comerciales y físicos.** Ampliar el contraste Las Canteras a todos los días muestreados; documentar desbalances y cambios de frontera. Separar puntos de suministro alternativos y reemplazos de cliente.
3. **Resolver relojes y unidad.** Acreditar si cada etiqueta corresponde al inicio o final del intervalo; conservar UTC y hora civil, con 23/25 horas cuando corresponda. Homologar libros antiguos sin inferir signos por magnitud.
4. **Completar ventanas de las zonas seleccionadas.** Reextraer de los originales locales los meses/puntos pertinentes, incluida Panamericana antes de octubre de 2023. Después pedir solo los faltantes. Si SIP permite fechas completas, obtener el intervalo del caso seleccionado, no extrapolar tres días a un mes.
5. **Construir exposición y zonas de red.** Usar circuitos, transformación, restricciones y modificaciones operativas; separar presión directa y propagada. Validar estados de certificación de capacidades. Una barra no tiene, por sí sola, una capacidad de abastecimiento equivalente a la suma de placas.
6. **Formar el panel carga–precio y estimar.** Primero curvas de carga, balances y respuesta descriptiva; luego diseño de identificación y sensibilidad. Los datos existentes hacen viable empezar; la atribución depende del cierre de las correspondencias y del contrafactual.

Las solicitudes externas, si se necesitan, serían específicas: retiros por empalme y etapa, vigencia de configuración/polaridad, fechas de transferencia de carga y actas de puesta en servicio. No se contactó a operadores.

## 5. Qué cambia respecto de la réplica

Se mantiene como referencia el resultado principal **+1,0526 USD/MWh**, el resultado sin Lampa **+0,0327** y el contraste con el promedio previo **−0,0866**, con sus definiciones originales. Esta auditoría no recalculó esos efectos: conserva su tabla y sus huellas.

La nueva hipótesis se formula sobre **aumentos medidos de carga, exposición de red y condiciones de abastecimiento**. No se necesita concluir que D era un error de datos: es un diferencial de precios válido para su definición, con pérdidas y separación de subsistemas. La exposición era otra variable y puede representarse mejor. Además, un diseño con efectos temporales comunes identifica cambios relativos entre zonas, no todo el efecto sistémico de la demanda digital.

La ganancia inmediata es concreta: pasar de inaugurar un edificio en una comuna a observar una trayectoria de consumo en una conexión, sin perder el registro de lo que se había estimado antes.
