# Decisiones, evidencia y criterios de cierre

[Inicio](../README.md) · [Proceso](proceso.md) · [Método](metodologia.md) · [Reproducción](reproducir.md) · [Auditoría](auditoria.md)

Este registro identifica decisiones observadas en la base y asuntos todavía abiertos. Se redacta el **25 de septiembre de 2026** a partir de documentación y controles conservados. Esa fecha corresponde a la sistematización: no se atribuye retrospectivamente como fecha original de cada decisión ni como revisión independiente.

Los identificadores `DEC-01` a `DEC-10` se introducen en esta guía. Los estados tienen un alcance específico: **aplicada** significa implementada en la construcción observada; **abierta** significa que falta evidencia o una definición; **parcial** identifica un componente comprobado y otro pendiente. Ninguno equivale por sí mismo a validez causal.

## Decisiones aplicadas a la base observada

| ID y estado | Decisión y motivo | Evidencia | Cuándo revisarla |
|---|---|---|---|
| **DEC-01 · Aplicada** | Mantener una fila por identidad histórica de barra y etiqueta de tiempo. Una barra vinculada a varios centros conserva un solo resultado de precio, para evitar duplicar observaciones. | [Constructor de precios](../SOCHER_2026_dataset/scripts/construir_panel_precios.py); [relaciones documentales](../SOCHER_2026_dataset/documentacion/Eventos_relaciones_y_red.md) | Si una fuente acredita continuidad o cambio de identidad; conservar el enlace entre códigos anteriores y nuevos sin borrar la versión original. |
| **DEC-02 · Aplicada** | Conservar los valores observados y añadir indicadores de calidad. La selección estricta exige homologación exacta, precio observado y ausencia de marca de revisión en barra y referencia. La media diaria estricta exige todos los pares esperados del día. | [Reglas implementadas](../SOCHER_2026_dataset/scripts/construir_panel_precios.py); [control de precios](../SOCHER_2026_dataset/controles/construccion_panel_precios.json) | Al disponer de homologaciones faltantes o revisiones oficiales; documentar el cambio de muestra antes de comparar efectos. |
| **DEC-03 · Aplicada** | Preservar meses sin datos y desconocidos como ausencias. Los ceros publicados se conservan como observaciones; una celda vacía causal no es «nunca tratado». | [Guía de datos](datos.md); [verificación integral](../SOCHER_2026_dataset/controles/verificacion_integral.json) | Si nuevas fuentes completan cobertura o permiten adjudicar una variable; nunca sustituir ausencias por cero por comodidad de estimación. |
| **DEC-04 · Aplicada, alcance limitado** | Agregar únicamente los canales D de HT1+HT2 con ambos equipos y cuatro etiquetas completas. Mantener HT3 separado y excluir líneas de tránsito. El resultado representa los transformadores seleccionados, no el consumo total acreditado del campus. | [Mediciones y reloj](../SOCHER_2026_dataset/documentacion/Mediciones_y_reloj.md); [control de mediciones](../SOCHER_2026_dataset/controles/verificacion_mediciones.json) | Cuando se acrediten polaridad, vigencia de la configuración y perímetro de consumo de otros equipos. |
| **DEC-05 · Aplicada como restricción** | Preservar etiquetas originales y no unir mediciones con precios hasta conciliar el reloj. La correspondencia con America/Santiago no resuelve si la etiqueta es inicio o fin del intervalo. | [Mediciones y reloj](../SOCHER_2026_dataset/documentacion/Mediciones_y_reloj.md) | Cuando una especificación y su comprobación en fechas ordinarias y de cambio horario acrediten la correspondencia de ambas fuentes. |
| **DEC-06 · Aplicada como restricción** | Separar hitos administrativos, previsiones, hechos operativos y cambios medidos. Dejar fechas causales y cohortes nulas; los 24 hitos son antecedentes y no 24 tratamientos. | [Registro de eventos](../SOCHER_2026_dataset/documentacion/Eventos_relaciones_y_red.md); [comprobaciones](../SOCHER_2026_dataset/documentacion/verificacion_eventos_relaciones.json) | Después de cerrar identidad, fase, naturaleza del cambio y fecha/intervalo efectivamente realizado. |
| **DEC-07 · Aplicada como restricción** | Mantener las relaciones de red como evidencia documental. No convertir proximidad ni coincidencia de códigos en suministro histórico; no interpretar un par ausente como conexión de peso cero. | [Registro de red](../SOCHER_2026_dataset/documentacion/Eventos_relaciones_y_red.md) | Cuando se acredite la vigencia del vínculo y una regla de exposición aplicable a los períodos analizados. |
| **DEC-08 · Parcial** | Reconstruir desde extractos archivados mediante un ejecutor portable. La instalación en un entorno virtual nuevo y la secuencia completa se comprobaron en el mismo equipo macOS ARM64; la réplica externa y la adquisición completa de originales siguen pendientes. | [Inventario](../SOCHER_2026_dataset/documentacion/inventario_insumos_repositorio.json); [auditoría del entorno nuevo](auditoria.md) | Al repetir la prueba en otro equipo o plataforma y al incorporar adquisición/extracción completa con sus propios registros. |
| **DEC-09 · Aplicada a las entregas verificadas** | Entregar el mismo panel en CSV y Excel. Tras el fallo de guardado documentado, usar escritura secuencial y verificar todas las filas, vacíos y diccionario. La nueva ejecución conserva el SHA-256 original del CSV; el Excel regenerado pasa los controles de contenido y estructura pese a tener otra huella. | [Registro previo del proceso](../SOCHER_2026_dataset/documentacion/Reproducibilidad_y_plan_GitHub.md); [verificación del entorno nuevo](evidencia/2026-09-25/verificacion_exportacion_excel_csv.json); [auditoría](auditoria.md) | Cada nueva exportación requiere su propio control; no hereda automáticamente la comprobación de la entrega anterior. |
| **DEC-10 · Abierta** | Elegir tratamientos, comparación principal, ventana, anticipación, estimando e inferencia antes de examinar los efectos. La base observada no define aún una muestra causal. | [Contrato de estimación](../SOCHER_2026_dataset/documentacion/Contrato_para_estimacion.md) | Cuando estén cerradas las adjudicaciones y se verifique que existe soporte suficiente para el diseño elegido. |

## Expedientes que faltan para pasar a estimación

| Expediente | Qué debe quedar acreditado | Criterio mínimo de cierre | Consecuencia si permanece abierto |
|---|---|---|---|
| Identidad y fases del establecimiento | Qué campus o fase corresponde a cada evidencia; qué unidades son independientes | Fuente con localizador, identificación consistente y explicación de agrupación | No contar fases o equipos como entradas independientes |
| Fecha y naturaleza del cambio | Entrada, ampliación, energización o traslado de suministro; realizado frente a previsto | Fecha o intervalo defendible, evidencia de realización y tratamiento explícito de su incertidumbre | No construir cohorte ni `post_evento` definitivo |
| Centro–medidor–barra | Correspondencia y vigencia del suministro antes y después del evento | Documento histórico y período de validez; discrepancias resueltas o acotadas | No atribuir a un centro el precio de una barra por proximidad |
| Reloj y medición | Intervalo físico de medición y correspondencia con precios 1–25 | Regla documentada y verificable, incluidos cambios horarios | No presentar la unión precio–carga como validada |
| Comparadores y cobertura | Series comparables antes/después y ausencia o grado de exposición a otros eventos | Regla de inclusión previa, cobertura suficiente y evaluación de contaminación | No asumir que cualquier barra no adjudicada es control |
| Exposición de red | Qué conexiones y estados representan el período relevante | Matriz o medida de exposición definida con vigencia, incertidumbre y fuente | No estimar spillovers con pesos documentales sin validar |
| Diseño e inferencia | Estimando, supuestos, dependencias entre unidades y análisis de sensibilidad | Protocolo versionado y viable con los eventos efectivamente acreditados | Mantener el análisis como descriptivo |
| Reproducción externa | Repetir en otro equipo la instalación y ejecución ya verificadas en un entorno virtual nuevo del equipo original | Registro externo con entradas, entorno, salidas y verificaciones satisfactorias | Describir el alcance como instalación y reconstrucción desde extractos comprobadas en el mismo equipo macOS ARM64 |
| Adquisición completa | Descargar y extraer nuevamente los originales nacionales con trazabilidad hasta el panel | Registro de adquisición, huellas, extracción y equivalencia frente a los extractos utilizados | Mantener explícito que la reproducción parte de extractos archivados y no verifica nuevamente originales ausentes |

El aumento de filas horarias mejora la descripción temporal, pero no aumenta por sí solo el número de entradas independientes. Si la evidencia no permite sostener un DiD escalonado, la elección del diseño deberá ajustarse a los eventos acreditados; ejecutar más estimadores no resuelve esa limitación.

## Plantilla para una decisión nueva o revisada

La [plantilla de validación del repositorio](../.github/ISSUE_TEMPLATE/validacion.yml) sirve para reunir antecedentes. La incorporación al dataset requiere además una decisión registrada y una nueva versión de los archivos afectados.

| Campo | Contenido requerido |
|---|---|
| Identificador y estado | Código estable; propuesta, aceptada, rechazada o sustituida |
| Objeto | Centro, fase, evento, medidor, barra o relación identificados |
| Pregunta | Afirmación específica que se intenta validar |
| Evidencia | Fuente, URL, archivo, SHA-256 cuando exista y página/sección/fila |
| Tiempo | Fecha del hecho o intervalo; precisión; vigencia del vínculo; fecha de revisión |
| Alternativas | Interpretaciones consideradas y evidencia que las distingue |
| Decisión y criterio | Regla aplicada, fundamento y condiciones para revisarla |
| Incertidumbre | Lo que no está acreditado y el tratamiento de esa limitación |
| Responsabilidad | Persona que propone y persona que revisa, cuando exista revisión; no inventar una segunda revisión |
| Impacto | Columnas, registros, muestra y resultados afectados |
| Versión | Estado anterior, cambio incorporado y comprobaciones de la nueva ejecución |

Una corrección posterior conserva la decisión previa y explica qué evidencia motivó el cambio. Una fuente nueva puede corregir un vínculo sin cambiar precios; una regla nueva puede cambiar la muestra sin alterar ningún archivo de origen. Ambas situaciones deben poder distinguirse al revisar el historial.

## Límite de este registro

Este documento sistematiza decisiones visibles en los artefactos conservados; no certifica que cada una haya tenido revisión externa. No se presentan estimaciones ATT, DiD, estudios de eventos ni spillovers como ya realizadas. La integridad computacional, la correspondencia de las fuentes y la identificación causal requieren evidencias diferentes, que se mantienen explícitas en el [modelo de proceso](proceso.md).
