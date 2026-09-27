# ODATA Lampa: una fecha operacional documentada y el diseño pendiente

Actualización del 27 de septiembre de 2026 para el artículo sobre centros de datos y diferenciales nodales en Chile.

**Avance principal:** se recuperó la carta original del titular que declara el **1 de agosto de 2022** como inicio de operación de ODATA Lampa. Además, se encontraron precios históricos de Batuco fuera de la selección inicial y se verificó soporte temporal completo para el calendario propuesto. No se ha estimado un efecto causal: falta acreditar qué suministro estaba vigente y justificar la comparación.

## El evento que ahora podemos investigar

La carta ODCH-ST01-061-2022 está fechada el 18 de agosto de 2022 y se recibió ese mismo día. Su texto identifica la RCA098/2021 y declara el inicio de operación para el 1 de agosto. Se conservaron la carta firmada, el comprobante, sus huellas y el registro público. La SMA certifica la recepción de información cuya veracidad corresponde al titular; no certifica primera energización o primera toma de carga. La redacción original utiliza un tiempo futuro pese a la fecha posterior de la carta, circunstancia que se conserva en la lectura. [Expediente SNIFA1005711](https://snifa.sma.gob.cl/SeguimientoAmbiental/Ficha/1005711); [carta original preservada](entrada/fuentes/SMA_carta_inicio_operacion_ODCH_ST01_061_2022_original.pdf).

**Discrepancia temporal conservada:** la cartera OGP de abril de 2023 rotula octubre de 2022 como inicio de operación de ODATA. La tabla no aclara si se refiere a otra fase o definición. No se descarta esa fecha como mera actualización administrativa ni se elige entre agosto y octubre observando los precios. Antes de estimar hay que conciliar los hitos o registrar el tratamiento de esa incertidumbre. [OGP, p.47](https://ogp.economia.cl/wp-content/uploads/2023/05/202304.pdf); [cronología y fuentes](entrada/memo_entrada_odata.md).

El proyecto de distribución previo y la conexión de alta tensión posterior deben mantenerse separados. La consultora declara haber tramitado un empalme Enel de 6,5 MW en su experiencia 2020–2021; es capacidad del trámite, no carga medida ni fecha de realización. Los planos y mediciones de Nueva Lampa J9–Lampa JT5/ET5 aparecen después y no fechan la apertura de 2022. [Fuentes eléctricas y límites](medicion/README_medicion_conexion.md).

La documentación ambiental contiene **dos rutas propuestas**: línea Batuco para el edificio ST01 y suministro desde Lampa de 23 kV. La [Adenda de octubre de 2020, respuesta 6, p.7](https://seia.sea.gob.cl/archivos/2020/10/01/5bf_Adenda_Odata_Datacenter.pdf) mantiene distribución pública para ST01 y amplía la línea dedicada de Lampa al proyecto completo. La consulta de octubre de 2023 recapitula esa situación aprobada y llama principal a la segunda fuente. No indica cuál alimentaba efectivamente al campus el 1 de agosto de 2022. El alimentador Batuco N°22/52D22 es un candidato nominal; todavía no es un empalme ODATA acreditado. «ST02» en ese expediente es un edificio de Lampa, no el campus comercial de San Bernardo.

## Qué está cerrado y qué falta

| Pieza del diseño | Resultado de esta revisión |
|---|---|
| Fecha de fase operacional | Aviso original del titular para el 1 de agosto de 2022; recepción el 18 de agosto. OGP registra octubre: discrepancia por conciliar. |
| Alimentación inicial | Dos rutas propuestas documentadas. Falta acta o constancia del empalme realizado y su vigencia. |
| Precios anteriores y posteriores | Los originales contienen Batuco 13/110 y Quillota 110/220; 105 días previos y 90 posteriores con conjuntos idénticos de 24 etiquetas. |
| Identidad de barra | Falta homologación histórica suficiente. Batuco13 no equivale a BP3 de 23 kV; Batuco110 requiere acreditar el recorrido aguas arriba. |
| Comparación causal | Aún no seleccionada. Se debe justificar la evolución contrafactual de la brecha y revisar cambios concurrentes de red, generación y otras cargas. |
| Efecto estimado | No disponible. No se calcula un coeficiente con una asignación de nodo todavía incierta. |

La comprobación de precios usa presencia de celdas y etiquetas publicadas, sin examinar magnitudes. No es una nueva validación numérica ni un puente físico de barras. Los siete libros y sus huellas están identificados; una segunda revisión confirmó las firmas de etiquetas. [Soporte verificable](precios_batuco/README.md); [revisión independiente](revision_independiente/revision_alcance.md).

## Siguiente paso concreto

La pieza prioritaria es una **constancia de conexión o recepción del empalme Enel del campus**, identificando alimentador, fecha efectiva y, si figura, cliente o medidor. Debe aclarar si existió suministro para pruebas antes de la fecha declarada y si hubo transferencia entre Batuco y Lampa. Una serie individual de carga sería valiosa, pero no es una exigencia universal para un efecto reducido de operación: lo indispensable es acreditar qué intervención representa la fecha y dónde se produjo.

Quedó preparada una [solicitud de antecedentes para revisión del autor](solicitud_antecedente_empalme.md), sin destinatario adjudicado y sin envío.

Con ese enlace y la conciliación de hitos se puede fijar una adenda del diseño antes de calcular resultados de este caso. El calendario condicional ya está preparado: `g=2 de agosto`, pre 12 de abril–25 de julio, transición 26 de julio–1 de agosto y post 2 de agosto–30 de octubre de 2022. Si las pruebas comenzaron antes, siete días pueden ser insuficientes; la transición debe responder a la evidencia, no al salto de precios. [Calendario y decisión](diseno/actualizacion_fecha_SNIFA.md).

El objeto propuesto es el efecto de la intervención sobre una brecha de precios. Permite que ambos nodos respondan, sin imponer artificialmente efecto cero en toda la red. Exige justificar cómo habría evolucionado esa brecha sin ODATA. Un caso y muchos días siguen siendo una intervención; las barras o transformadores no multiplican las asignaciones. [Diseño y alternativas](diseno/memo_identificacion.md).

## Correcciones que protegen la interpretación

- **Alto Jahuel:** el expediente Ensolution localizado contiene solicitud en 2024 y operación prevista en 2028. No respalda una entrada realizada en 2024 ni acredita por sí solo que el centro de consumo sea un data center. [Corrección documentada](revision_alto_jahuel/README.md).
- **Literatura:** ya existen trabajos sobre centros de datos y precios nodales. La contribución debe demostrar identificación y un mecanismo económico pertinente; aplicar DiD en Chile no basta por sí solo. [Cuatro antecedentes primarios y alcance](literatura/README.md).
- **E53:** sus contrastes anteriores permanecen descriptivos. No se reinterpretan como efecto causal porque este expediente haya avanzado.

## Archivos y estado

Las carpetas `entrada`, `medicion` y `diseno` conservan fuentes y localizadores propios. `precios_batuco` añade solo soporte de etiquetas; `literatura` y `revision_alto_jahuel` contienen revisiones acotadas. La matriz inicial v8 de 24 hitos/33 fuentes es una instantánea previa y no incorpora automáticamente estos hallazgos. Sus ceros de elegibilidad no representan efectos cero. La entrega v0.2.0 y el protocolo original no se modifican.

La revisión está terminada hasta el alcance de la evidencia pública localizada; no se obtuvo el acta de empalme. El avance resuelve una fecha documental y disponibilidad de resultados, pero no la identificación causal. No se ha contactado a instituciones ni enviado el manuscrito. Energy Economics continúa como objetivo; la publicación depende de resultados, contribución y revisión editorial.
