# Informe de viabilidad: simulación 2030 con y sin expansión de centros de datos

Fecha: 5 de octubre de 2026. Este documento describe qué se obtuvo, qué comparación puede ejecutarse y qué falta. No contiene efectos estimados ni modifica la réplica histórica.

## Resultado de la incorporación de las bases

Los dos ZIP descargados por el usuario fueron registrados y descomprimidos correctamente. Las entradas del modelo PLP son texto legible y contienen demanda, generación, transmisión, hidrología, embalses y baterías. También se leyeron los resultados oficiales de 2030. Se resolvió el acceso a los insumos; aún no se ejecutó un escenario contrafactual de expansión digital.

## 1. Bases PET 2026 verificadas

| Base | Contenido comprobado |
|---|---|
| PLP | Tres escenarios, 349 barras y 496 líneas en cada uno; demanda por barra y bloque, costos variables, disponibilidad de centrales, afluentes, parámetros de embalses y baterías |
| PowerFactory | Seis proyectos binarios PFD, incluido un archivo RM; se conservaron sin ejecutar |
| Resultados PLP | Costos marginales, demanda y otras salidas del escenario oficial original; 2030 extraído en CSV |

El horizonte va de abril de 2025 a marzo de 2048. Hay diez bloques representativos por mes y una tabla que asigna cada hora a un bloque. Esto permite interpretar duraciones, pero no convierte la optimización en un despacho cronológico horario. Los archivos de afluentes declaran 30 hidrologías.

| Escenario del archivo | Barras con demanda | Demanda SEN 2030 TWh | Baterías declaradas |
|---|---:|---:|---:|
| PET26_E01_v19 | 178 | 102,628 | 115 |
| PET26_E02_v19 | 180 | 114,618 | 123 |
| PET26_E03_v19 | 178 | 97,357 | 110 |

Se mantienen los nombres originales de los escenarios: difieren en demanda y configuración de generación, por lo que restar sus resultados no aísla el efecto de centros de datos.

La demanda de entrada coincide exactamente con la demanda de salida oficial en las 41.880 combinaciones barra-bloque de 2030 de cada escenario. Las duraciones de bloques coinciden con la tabla de correspondencia horaria y suman 8.760 horas en 2030. Esta conciliación valida la extracción; no valida todavía una implementación propia del despacho.

Las salidas completas ocupan 10,6 GB descomprimidas. Se conservaron dentro del TAR original y se extrajeron únicamente metadatos y precios/demanda de 2030. El estado verificable y las rutas están en `extraidos/pet26/estado_ingesta.json`; los hashes de los ZIP están en `fuentes/registro_fuentes.csv`.

## 2. Qué se obtuvo y para qué sirve

| Fuente (todas con URL, fecha y SHA-256 en `fuentes/registro_fuentes.csv`) | Aporte |
|---|---|
| CNE, Informe Técnico Definitivo de Precio de Nudo de Corto Plazo, julio 2026 (PDF y dos planillas) | **Resultados oficiales** de costo marginal esperado y energía por barra, mes y bloque, julio 2026 a marzo 2037 (modelo OSE2000). Cuadros de costos variables, combustibles, obras y disponibilidad renovable |
| CNE, Previsión de Demanda 2025-2045, informe definitivo (febrero 2026) | Demanda mensual **por cliente libre y punto de conexión** y por subestación primaria (regulados) |
| Infotécnica (API del Coordinador) | Red existente: 2.915 secciones de línea con reactancia y límite térmico, 2.111 transformadores, 1.645 unidades generadoras |
| Coordinador: informe final PET 2026, complemento (julio 2026), Anexo II, proyección de demanda 2025-2045 | Escenarios, metodología y obras propuestas (texto) |
| Cartas del Coordinador y resoluciones CNE 550/2025 y 22/2026 | Cronogramas por etapa de proyectos digitales y fechas de obras críticas de la RM |

Se verificó la coherencia entre dos de ellas: la demanda de clientes libres de 2030 del informe de precio de nudo (63.447 GWh) coincide con la suma del Anexo 2 con eficiencia energética de la previsión de demanda. Esta coincidencia respalda la compatibilidad de ambas fuentes en el agregado. Por sí sola no acredita identidad de todas las asignaciones por cliente y barra; el enlace de la carga digital con el escenario base debe confirmarse a ese nivel.

## 3. Carga digital incluida en el escenario base (riesgo de doble conteo)

**No existe una categoría «centro de datos»** en las bases abiertas. En la previsión de la CNE estos clientes figuran como «Industrial» o «CPR». La identificación se hizo por razón social (criterio propio, trazable en `scripts/construir_demanda_digital.py`), separando dos clases que no deben sumarse sin más:

| Clase | Filas RM | 2025 | 2028 | 2030 |
|---|---|---|---|---|
| Operadores de centros de datos (Ascenty, EdgeConneX, Google/Dataluna, Microsoft, ODATA, Lo Espejo DC) | 10 | 612 GWh (70 MW medios) | 722 GWh (82 MW) | 903 GWh (103 MW) |
| Telecomunicaciones y TI con centros de datos (Entel, Claro, SONDA, GTD, Telefónica, Cirion, IBM y otros); carga mixta | 40 | 341 GWh (39 MW) | 357 GWh (41 MW) | 404 GWh (46 MW) |

Son **MW medios** (energía dividida por horas), no potencia contratada, informática ni máxima.

Hallazgos que condicionan el diseño:

1. **Los grandes proyectos nuevos no aparecen identificados explícitamente en la selección CNE.** No hay filas con punto de conexión Punta Verde, Huechuraba o Enea, ni clientes Equinix, Amazon, Huawei, Oracle o NextStream. Las dos filas de Ascenty en Chacabuco quedan aproximadamente en 7 MW medios y no identifican SCL4. Esto justifica revisar su incorporación, pero no prueba que esas cargas estén ausentes de agregados o de suministros de terceros. El crecimiento de operadores ya identificados debe conciliarse por proyecto antes de añadir potencia.
2. **La barra Punta Verde 110 aparece desde diciembre de 2028 con demanda cero en la salida CNE examinada.** La carga podría estar agregada en otro nodo; tampoco la aparición del nombre basta para acreditar todos los parámetros de la obra.
3. **La base del Coordinador (PLP) usa otra proyección**, propia, que declara incluir centros de datos «existentes y nuevos informados por las empresas» y nombra a Microsoft y Scala. Su detalle por proyecto no está en el informe: solo una figura con la categoría «Datacenter» de la encuesta a clientes libres. Qué incluye exactamente **requiere desagregar la demanda y documentar su correspondencia territorial**. La regla de doble conteo depende, por tanto, de cuál base se use. El PLP recibido identifica demanda agregada por barra, sin nombres de operadores. Chacabuco, Punta Verde, Huechuraba y Enea no aparecen como barras separadas: su ausencia nominal no demuestra ausencia de sus cargas en otros nodos agregados.
4. Las cifras de 325 MW (2025), 1.207 MW (2030) y 1.038 MW en la RM atribuidas al Coordinador provienen de **notas de prensa**; no se recuperó el documento técnico ni su definición (media, máxima o conectada). Son incompatibles en orden de magnitud con los 70–103 MW medios de la base CNE, lo que sugiere definiciones distintas, no necesariamente un error. Otra nota de septiembre de 2026 habla de 2.500 MW a 2030, que es cartera de solicitudes.
5. Las filas de Microsoft muestran cambios mensuales importantes (11,4 MW tres meses y luego 1 MW). Se conservan los valores originales; su interpretación requiere comprobar el perfil y la etapa del proyecto. Los totales anuales sirven para el contraste agregado, sin suavizar la serie automáticamente.

Cronogramas documentados (detalle y citas textuales en `extraidos/demanda_digital/proyectos_digitales_etapas.csv`):

| Proyecto | Hito | Magnitud | Naturaleza |
|---|---|---|---|
| Ascenty SCL4, Quilicura | Fines de 2027 | 50 MW | Demanda eléctrica prevista, etapa 1 |
| Ascenty SCL4 | Fines de 2028 | 150 MW (total acumulado) | Demanda eléctrica prevista, etapa 2 |
| Scala Huechuraba | Octubre de 2030 | 80 MW y 80 MVA | Demanda prevista y capacidad de conexión; obra urgente aún en evaluación |
| Equinix (S/E Enea 110 kV) | Sin fecha ni potencia en la carta | — | Obra urgente autorizada en 2024; hito prorrogado en 2026 |
| Transformador «Data Center Chile 2», S/E Chacabuco | Sin fecha | 40 MVA | Capacidad de transformación, no consumo |

Ninguna fuente entrega potencia informática ni PUE: todas las cifras son eléctricas, de modo que **no corresponde aplicar PUE**. SCL4 no operó a 50 MW durante 2027 ni a 150 MW durante 2028; en 2030 sí estaría en régimen si se cumple el calendario. Huechuraba aportaría como máximo unos tres meses de 2030. Hay una tensión que resolver: la solicitud de conexión de SCL4 (septiembre de 2025) habla de 150 MW con puesta en servicio en septiembre de 2028 y no menciona la etapa de 2027.

## 4. Qué comparación puede ejecutarse

| Comparación | Estado después de incorporar los ZIP |
|---|---|
| Demanda y costos marginales oficiales de 2030 por barra | Extraídos para los tres escenarios |
| Escenarios de demanda digital por conexión | Preparables con las fuentes de proyectos; falta determinar la carga incluida en la demanda agregada del PLP |
| Contraste de una implementación propia con salidas oficiales | Ya hay referencias numéricas; el motor de despacho propio todavía no está implementado ni validado |
| Impacto de la expansión digital sobre costos de operación y precios | Requiere ejecutar pares de escenarios con el mismo resto de supuestos |
| Congestión local y retrasos de obras de la RM | Requiere reconciliar la red reducida PLP con la topología local y las obras documentadas |

El PLP contiene varios insumos que faltaban: afluentes por central, configuración de embalses, costos, disponibilidad y límites de líneas. El trabajo pendiente se concentra en interpretar sus restricciones e implementar o disponer del motor de simulación, además de definir la carga digital y su correspondencia con los nodos del modelo.

La versión local que fija los precios de las barras frontera sigue siendo un análisis de equilibrio parcial. Los resultados de precio de nudo de la CNE ofrecen otra referencia de niveles y estacionalidad, con una representación distinta de la red. No deben mezclarse sus insumos con los del Coordinador sin conciliación.

## 5. Resolución temporal

La CNE usa 24 bloques representativos por mes y resultados esperados sobre 34 hidrologías. El PLP recibido usa 10 bloques por mes y declara 30 hidrologías en su archivo de afluentes. Son bases distintas. El archivo `indhor.csv` asigna las horas de calendario a los bloques PLP; los perfiles así reconstruidos conservan la simplificación del modelo por bloques.

## 6. Software

Las entradas PLP y las salidas CSV ya se leen sin software comercial. El paquete recibido no incluye ejecutable PLP ni manual de ejecución. Antes de simular debe disponerse de un motor compatible o implementar y validar un despacho con herramientas abiertas, declarando sus simplificaciones.

Los seis archivos PowerFactory son binarios PFD; no se encontraron exportaciones de texto en ese ZIP. Su lectura completa requiere un entorno compatible. El detalle de red también puede construirse desde las fuentes Infotécnica ya descargadas, con trabajo de correspondencia y validación.

La base OSE2000 de la CNE no fue localizada; sus resultados publicados están disponibles como referencia alternativa.

## 7. Trabajo siguiente

1. Identificar la carga digital incluida en el escenario elegido y su correspondencia con las barras agregadas del PLP. Evitar tratar como demanda ausente un proyecto cuyo nombre no aparece en la base.
2. Leer y convertir los parámetros de generación, hidrología, embalses, baterías y restricciones de red; contrastar la implementación con las salidas oficiales antes de alterar demanda.
3. Construir el puente entre barras PLP, conexiones documentadas, Infotécnica y panel histórico para el análisis metropolitano.
4. Definir pares con y sin expansión digital manteniendo constantes las otras demandas, generación, combustibles, hidrología e infraestructura. Los tres escenarios oficiales no son por sí solos ese experimento.
5. Definir el retraso de obras antes de simular y mantener el mismo retraso en ambos miembros del par. La referencia documental de Punta Verde sitúa su tramitación regular hacia 2032.

## 8. Límites de lo hecho

- Se abrieron y procesaron entradas PLP y salidas oficiales de 2030. Los PFD se inventariaron y se comprobó su formato binario, sin abrirlos en PowerFactory. No se ejecutó PLP ni un modelo propio.
- La clasificación de clientes digitales es por nombre. Puede omitir centros de datos abastecidos a través de una distribuidora o de un tercero, e incluye en la clase mixta consumo que no es de centros de datos.
- Las tablas de obras y proyectos por etapa son curadas a mano desde los documentos citados; cada fila lleva el pasaje de respaldo.
- Las tablas del informe de la CNE se volcaron literalmente, sin reinterpretar unidades ni encabezados.
