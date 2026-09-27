# ODATA ST01: diseño causal que puede defenderse y decisión ejecutable

Fecha: 27 de septiembre de 2026. Investigación documental sin abrir ni estimar nuevos resultados de precios de ODATA. No modifica el protocolo v8 ni habilita un ATT. Las estadísticas generales v8 y el episodio E53 fueron conocidos antes de esta revisión. Esta propuesta requiere adenda antes de ejecutar el nuevo contraste.

**Actualización posterior:** el aviso original SMA declara operación desde el 1 de agosto de 2022. Véase `actualizacion_fecha_SNIFA.md` para la precisión del hito, ventana propuesta y brechas eléctricas aún pendientes.

## Decisión prioritaria

El caso de primera entrada de ODATA Lampa en 2022 continúa abierto, pero la ruta actual Nueva Lampa J9 → Lampa JT5/T5 no identifica retrospectivamente esa entrada. La prioridad es cerrar la alimentación efectivamente utilizada en 2022 y la fecha o intervalo de su consumo operativo; la conexión nueva de 2025 debe mantenerse como episodio distinto. Si la RCA original confirma un suministro inicial mediante la línea Batuco, hay que seguir ese alimentador hasta su barra de precio histórica, sin sustituirlo por S/E Batuco por parecido de nombre.

La contribución causal viable puede ser **el cambio relativo entre nodos provocado por una entrada identificada**, incluso si la carga también afecta los comparadores. No se necesita demostrar que el efecto es cero en todas las demás barras del SEN. Sí se necesita justificar cómo habría evolucionado la brecha entre esos nodos sin la entrada, y mostrar qué cambios concurrentes amenazan ese supuesto.

No hay una garantía de publicación ni un mecanismo exógeno documentado para la entrada de ST01. No se propone un instrumento basado únicamente en una demora administrativa.

## Lo que cerró esta revisión de fuentes

1. **La red ya había cambiado antes de 2022.** El CEN documenta pruebas de incorporación de Nueva Lampa en enero de 2021 (EAF013/2021, p.58, solicitud 2021001942). Su EAF067/2021 contiene la configuración operativa de marzo de 2021: Lampa toma suministro del corredor Polpaico–Nueva Lampa; Nueva Lampa conecta con Cerro Navia. La figura y explicación de pp.6–7 fueron inspeccionadas visualmente. El informe de sostenibilidad Enel2021 sitúa la puesta en servicio en enero de 2021, pero su descarga directa falló403 y no se presenta como original archivado. Por tanto, usar todo2020 como si el circuito fuera invariante no está justificado. Un pre de 2021–2022 posterior a las obras podría ser posible, sujeto a la fecha real de entrada y a los registros posteriores.
2. **Lampa no es una carga exclusiva de ODATA.** EAF067/2021, pp.3,6–7, registra alimentación de Acería y Laminación, antes del año de entrada declarado por el operador de ODATA. El evento de marzo2021 afectó49,60MW de consumo de la subestación. Es evidencia de otras cargas y de la topología, no una medida de consumo ODATA. No sumar transformadores de Lampa como si fueran la demanda del campus.
3. **Había un plan, no una entrada verificada, desde2020.** El resumen CEN de solicitudes al30jun2020, p.4, registra ST01 en evaluación de admisibilidad, 30MW y fecha estimada1jul2022, en Nueva Lampa220kV. Ese día no puede convertirse en cohorte de tratamiento.
4. **Nueva cota documental de puesta en servicio de la conexión de2025.** La Resolución Exenta CNE220, fechada30abr2025, secciónIVpp.12–14, excluye del listado en construcción proyectos que ya iniciaron puesta en servicio. La tabla incluye ODATA Datacenter ST01: nuevo transformador220/23kV de50MVA, nueva bahía GIS, 30MW. Las tres páginas fueron inspeccionadas visualmente para confirmar la continuidad de la tabla. Es una cota de inicio de PES anterior o igual a30abr2025, sin acreditar día de energización, fin de pruebas, entrada comercial ni incremento neto de carga. La misma sección incluye ampliaciones Nueva Lampa NTRATMT y Batuco NTRATMT: hay concurrencias de red que deben fecharse si se analiza2025.
5. **La nomenclatura actual mezcla sectores diferentes.** La revisión CEN de1oct2025, código2510-DEN-RIC-PR6090, p.2, distingue la barra220kV del sector de J1/Tap Lampa. Cita planos de Lampa de julio2023 y de ODATA de octubre2023. El proyecto evaluado y rechazado allí es **BESS Antu NUP6090**, no ODATA. El rechazo no debe atribuirse a ST01. La descripción es de2025; no certifica por sí sola vigencia histórica2022.
6. **Obras planificadas no son cambios realizados.** El ITP CNE del Plan de Expansión2022, publicado en2023, pp.16 y79–80, propone Lo Campino y seccionamientos de Cerro Navia–Nueva Lampa. No se marca ese proyecto como un choque realizado2022/2023 basándose solo en el plan.
7. **No se encontró una asignación cuasialeatoria.** La audiencia pública de21jul2022 reúne ODATA, Enel Distribución y EnelX para abordar las obras del centro. Acredita coordinación, pero no entrega un sorteo, una regla de prioridad exógena, ni una causa de demora desligada del precio, de la demanda o de la infraestructura. La fecha estimada de2020 y las pruebas de2025 no bastan para construir un instrumento.

Fuentes primarias preservadas en `fuentes/manifest.json` con URL, archivo y SHA256. Las extracciones y páginas de verificación están en `validacion/`. ODD01 está señalado NO_ARCHIVADO; las otras siete fuentes están archivadas. El nombre local `CNE_dc_mayo2025.pdf` corresponde a la publicación encontrada en mayo; la **fecha de la resolución es30abril2025**.

## Objeto económico y comparación

Sea D la intervención particular de entrada de una fase de ODATA, con todo lo demás en su estado contrafactual sin esa intervención. Para una barra b y comparadores c con pesos w predefinidos, la cantidad de interés puede ser:

θ_rel(t) = [P_b,t(1) − P_b,t(0)] − Σ_c w_c [P_c,t(1) − P_c,t(0)], con Σ_c w_c=1.

Esto mide la respuesta relativa a la **misma intervención de ODATA**. Admite efectos de ODATA en c; no mide el efecto absoluto en b ni permite reconstruir un efecto nacional sin supuestos adicionales. Si se trabaja con diferenciales contra Quillota y soporte/ponderaciones idénticos, la referencia común se cancela exactamente. Cambiar Quillota110 por220 no produce una segunda identificación independiente.

Un contraste observado de cambios identifica θ_rel solo si el cambio contrafactual de P_b(0)−ΣwP_c(0) es el postulado por el diseño. La cancelación algebraica no prueba esa condición. El expediente debe sostener que la entrada no coincide con un cambio diferencial de generación, red, otras grandes cargas o definición del precio que explique esa brecha por otra vía. La estabilidad previa ayuda a evaluar el argumento; no demuestra el contrafactual.

**Comparación predefinible tras cerrar la ruta inicial:**

- Primer grupo: barras ubicadas en la misma ruta eléctrica documentada del suministro inicial, con nivel de tensión y posición respecto del transformador identificados. Se reportan como resultados expuestos de un único proyecto, nunca como múltiples asignaciones independientes.
- Segundo grupo: barras eléctricamente documentadas que representen los choques comunes de abastecimiento pero tengan una posición distinta respecto de la conexión de ODATA. Las candidatas pueden provenir del corredor fuente; Cerro Navia y Polpaico son nodos de red observados en el EAF2021, **no controles ya habilitados**. Se necesitan homologación vigente y revisión de cambios propios durante la ventana.
- Un diferencial23kV–220kV de la misma subestación podría estudiar la respuesta relativa a través de transformación, pérdidas y restricciones, si ambos precios corresponden al mismo camino de suministro. Ambos niveles pueden responder a ODATA. No equivale a comparar tratado y no tratado, ni separa automáticamente consumo de cambio de transformador.
- No seleccionar donantes por una correlación posterior alta, por ofrecer significación o por estar en otra comuna. Puede usarse ajuste previo para ponderar una lista admisible previamente documentada; deben congelarse lista, regla, hiperparámetros, fechas y salidas conocidas antes del post.

Una barra con un datacenter estable desde antes no tiene por qué ser inutilizable para todo contraste relativo. Puede ser admisible bajo una definición de intervención y cambios propia que lo justifique. Esto sería una **adenda con un nuevo estimando**: no debe introducirse silenciosamente en el ATT de primera adopción del protocolo v8, que excluye controles ya tratados.

## Cómo se podría estimar con un solo proyecto

Un solo proyecto no vuelve imposible una evaluación causal, pero impide fingir que64 etiquetas o miles de horas constituyen64 asignaciones. El estimador más transparente es el cambio de la brecha predefinida, con dinámica diaria/semanal y la ventana registrada. Un modelo contrafactual ponderado puede ser útil si hay una historia previa larga en la misma red y un ajuste validado fuera de la muestra de entrenamiento **dentro del período previo**. No arregla una fecha o ruta equivocada.

Si el pre disponible solo permite105días, no prometer que basta para calibrar inferencia temporal de90días ni un ciclo estacional. Antes de implementar debe justificarse la longitud y la estructura de dependencia. En una aplicación con pocos proyectos, la inferencia temporal condicional al caso podría usar residuos previos y un procedimiento conformal por bloques, **solo** tras evaluar sus supuestos de estabilidad/dependencia y la validez del predictor contrafactual. Es otra fuente de incertidumbre que inferencia basada en asignaciones aleatorias. No se presentarían permutaciones espaciales de barras heterogéneas como aleatorización física.

Fuentes metodológicas primarias consultadas: [Chernozhukov, Wüthrich y Zhu, JASA2021](https://arxiv.org/abs/1712.09089), [extensión para datos dependientes](https://arxiv.org/abs/1802.06300), [Ferman y Pinto, QE2021](https://onlinelibrary.wiley.com/doi/full/10.3982/QE1596). El ajuste imperfecto de un control sintético puede conservar sesgo, aun con mucha historia. Estos trabajos permiten considerar una implementación; no validan automáticamente el caso ODATA ni sustituyen la lectura técnica completa antes de ejecutar sus intervalos.

## Árbol de decisión concreto

| Resultado del cierre documental | Acción habilitada | Objeto que puede sostenerse |
|---|---|---|
| Primera carga2022 y suministro inicial acreditados; fecha diaria; ruta y precios estables; concurrencias y contrafactual defendibles | Congelar adenda, verificar soporte de ventana v8 y ejecutar contraste relativo predefinido; inferencia por separado | Efecto causal relativo de la primera entrada, condicionado al argumento identificador |
| Entrada2022 acreditada solo por intervalo | Excluir toda la transición documentada; registrar un contraste agregado antes/después del intervalo y sus supuestos; no fijar un día artificial | Eventual efecto de régimen operativo relativo, si existen pre/post separados y comparables; no ATT diario de entrada |
| Solo fecha administrativa o inauguración, sin suministro efectivo | Mantener cronología y búsqueda dirigida a distribuidora/SMA/operador; no ejecutar ATT | Hecho documental, sin resultado causal |
| Nueva conexión2025 realizada y carga transferida desde otra alimentación | Documentar ambos orígenes y cambio neto, revisar obras simultáneas; adenda distinta | Efecto relativo de transferencia/conexión, sin denominarlo entrada de un centro |
| Conexión2025 y ampliación conjunta inseparables, incluida obraDS171 | Definir explícitamente el paquete y contrafactual; no controlar por su flujo/carga mediadores como si fueran confusores | Efecto del paquete conexión–ampliación, no efecto puro de demanda informática |
| Fecha/ruta cerradas pero choque local simultáneo independiente indistinguible | Buscar otra fase o caso sin seleccionar por efecto; no rescatar el diseño moviendo arbitrariamente el día | Contraste descriptivo o efecto conjunto si tiene un objeto económico defendible |

**Criterio de salida de esta búsqueda:** tras cerrar el documento de suministro inicial, hay dos rutas útiles: (A) registrar y ejecutar la primera entrada si cumple el argumento de arriba; (B) declarar que ST01 no identifica entrada con los registros disponibles y transferir esfuerzo al caso con mejor fecha y ruta, conservando el hallazgo2025 como conexión. No prolongar indefinidamente búsquedas generales por toda la red, ni reclamar exposición cero de cada barra del SEN.

Alcance de la búsqueda: las fuentes encontradas no constituyen un censo diario de obras, fallas y cargas2021–2023. No haber encontrado un evento concurrente en esta revisión no acredita su ausencia. La revisión de concurrencias debe acotarse a la ruta y ventana que efectivamente establezca el expediente, y combinar registros operativos con la documentación del evento.
