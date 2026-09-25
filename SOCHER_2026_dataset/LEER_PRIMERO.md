# Dataset del artículo: centros de datos y costos marginales

**Primera versión estructurada de la base para el mismo artículo del curso, SOCHER y su desarrollo hacia revista.** La base observada está construida y verificada. La asignación de tratamientos, cohortes y exposición sigue pendiente de validación documental y metodológica.

El ATT es el efecto que queremos estimar. DiD, DiD escalonado, el estudio de eventos y los spillovers requieren comparaciones y datos adecuados; no se ejecutan automáticamente como una lista de pruebas. Primero cerramos el dataset y la muestra analítica.

## Archivo del dataset para abrir y revisar

El panel completo de **178.016 filas y 66 columnas** está disponible en [Excel](../outputs/01a0d6c3-09cd-7aa3-903d-5ee59e65c071/Dataset_articulo.xlsx) y en [CSV sin comprimir](../outputs/01a0d6c3-09cd-7aa3-903d-5ee59e65c071/Dataset_articulo.csv). El Excel incluye filtros y una hoja `Diccionario` que explica las variables. El CSV usa UTF-8, coma como separador y punto decimal. Ambos conservan el orden y los valores del panel de origen; las variables pendientes permanecen vacías.

## Qué contiene

| Componente | Archivo principal en `tablas/` | Cobertura o contenido |
|---|---|---|
| Panel barra × hora | `panel_barra_hora.parquet` | **178.016 filas**, con precios, diferenciales frente a Quillota 110 y 220, procedencia y calidad |
| Panel barra × día | `panel_barra_dia.parquet` | **7.415 filas**, medias de todas las etiquetas y alternativas estrictas claramente separadas |
| Identidades de barra | `barras.parquet` | **83 claves históricas** de etiqueta y código; no son 83 centros independientes |
| Centros y candidatos | `centros.parquet` | **10 registros**: nueve filas de campus/proyectos candidatos y una barra sin centro adjudicado |
| Hitos de los proyectos | `eventos_documentados.parquet` | **24 hechos**, distinguiendo previsiones, energización, entrada formal y cambios medidos |
| Centros y barras | `relaciones_centros_barras.parquet` | **17 relaciones documentales**, con función y límites de vigencia |
| Relaciones con precios disponibles | `relaciones_con_cobertura.parquet` | Coincidencia de código en **12 de las 17 relaciones**; no verifica suministro histórico ni crea precios adicionales |
| Conexiones de red | `conexiones_red_documentadas.parquet` | **20 vínculos documentales**; todavía no una matriz de exposición eléctrica |
| Medidas originales | `carga_medidor_15min.parquet` | **67.384 registros** de HT1, HT2 y HT3 de Las Canteras |
| Carga agregada por etiquetas | `carga_campus_hora.parquet` | **7.319 bloques horarios** de HT1+HT2 en 305 días; no representan todo el consumo del campus |

Las tablas tienen copias CSV o CSV comprimido para inspección. Parquet conserva mejor los tipos, fechas y nulos. El [catálogo](documentacion/catalogo_tablas.csv) incluye las restantes tablas de períodos y fuentes, sus dimensiones y hashes.

## Períodos disponibles y vacíos

Los precios integrados corresponden a **febrero, abril, mayo, junio y 1–14 de julio de 2024**. Hay 137.096 filas con homologación mensual exacta y 40.920 con enlace provisional de mayo. Se preservan 12.581 filas con marcas de revisión o no publicación para decidir su uso; las reglas estrictas las excluyen. Los 3.961 precios candidatos sin identificación mensual de la versión anterior permanecen allí y no se incorporaron silenciosamente a este panel.

No se rellenaron enero, marzo ni el resto del año. La [cobertura por barra y mes](tablas/cobertura_barra_mes.csv) distingue ausencia de registros de valores observados iguales a cero. Tampoco se empalmó automáticamente la valorización posterior al 15 de julio.

Las mediciones disponibles son de Las Canteras durante 2024. Enero y abril no tienen observaciones de estos transformadores en los extractos integrados. Las 1.440 horas con cero en febrero y marzo son ceros publicados, no imputados. Las series de otros centros deben incorporarse con identidad, unidades y polaridad verificadas.

## Cómo están relacionadas las tablas

El panel conserva una observación por barra, fecha y etiqueta de hora. Su `barra_id` enlaza con el registro de barras. Las relaciones conectan candidatos y puntos eléctricos, y la tabla con cobertura permite localizar qué códigos ya tienen precios. Los hitos enlazan con centros mediante `centro_id`; las mediciones conservan identificadores de equipo y campus.

**Compartir una barra no duplica el precio.** Las relaciones se mantienen separadas para evitar contar la misma trayectoria como varias unidades independientes. Una coincidencia de código no valida por sí sola que el centro recibiera suministro allí durante todo el período.

Los precios tienen etiquetas originales, incluida una hora 25. Las mediciones conservan UTC y hora local, pero la interpretación de inicio/final de intervalo sigue pendiente. Por ello, la carga todavía no se incorpora a las filas horarias de precios. Su unión requerirá conciliar el reloj y la vigencia de suministro; no basta con restar una hora por intuición.

## Variables previstas para los modelos

| Uso | Variables | Estado actual |
|---|---|---|
| Resultado | `precio_usd_mwh`, `diferencial_q110_usd_mwh`, `diferencial_q220_usd_mwh` | Calculadas y comprobadas |
| Unidad y tiempo | `barra_id`, `fecha`, `hora_etiqueta`, `t_dia` | Disponibles en convención de fuente; UTC del precio pendiente |
| Tratamiento | `fecha_tratamiento_causal`, `tratado_it`, `post_evento` | Nulas hasta adjudicar la intervención |
| Adopción escalonada | `cohorte_g_dia` | Nula; desconocido no se codifica como grupo nunca tratado |
| Estudio de eventos | `tiempo_evento_dias`, `tiempo_evento_horas` | Nulas hasta validar evento y escala temporal |
| Comparación | `control_validado` | Nula; solicitudes rechazadas no constituyen controles automáticos |
| Spillovers | `exposicion_red`, conexiones documentales | Exposición nula; falta vigencia y regla de transmisión |
| Consumo enlazado | `carga_asignada_mw` | Nula en el panel de precios; mediciones en tablas separadas |

Nulo significa desconocido o no adjudicado, no cero. Las marcas estrictas de calidad de precio tampoco acreditan causalidad. En el panel diario, las medias generales incluyen todas las etiquetas; los diferenciales estrictos solo se calculan cuando todos los pares esperados de ese día cumplen la regla.

El [contrato para la estimación](documentacion/Contrato_para_estimacion.md) detalla estas decisiones. El [diccionario del panel](documentacion/diccionario_panel.csv) define cada variable. El [diccionario de mediciones](documentacion/diccionario_mediciones.csv) describe unidades, canales y reloj.

## Qué falta para cerrar la muestra causal

1. **Fechas y naturaleza de cada intervención:** distinguir carga nueva, ampliación, traslado de suministro y cambios de medida. Los 24 hitos no equivalen a 24 tratamientos.
2. **Historia alrededor de cada evento:** Dataluna y Ascenty/Sonda tienen antecedentes de 2020; requieren precios, homologaciones y mediciones de ese período. Los candidatos documentados en 2025/2026 requieren su propia historia.
3. **Enlace horario y eléctrico:** validar inicio/final de intervalos, vigencia de equipos y barra exacta. Resolver cambios de código antes de concatenar identidades.
4. **Comparadores y exposición:** documentar condiciones de red, intervenciones concurrentes y variables necesarias. Una arista no registrada no significa ausencia de exposición.

Con esas piezas se definirá la muestra que permite estimar ATT por cohorte y período, su dinámica y posibles spillovers. Esta entrega no presenta estimaciones causales.

## Verificación y reproducción

El [registro del proceso y plan para GitHub](documentacion/Reproducibilidad_y_plan_GitHub.md) describe las etapas realizadas, los entornos observados, las dependencias aún pendientes de hacer portables y el orden de validación. La versión actual queda identificada en `controles/versiones/base_observada_2026-09-25.json`. Ese manifiesto registra huellas de archivos; no equivale a un repositorio remoto ni a una copia de los datos.

La verificación cruzada compara todos los precios con la extracción anterior, recalcula ambos diferenciales desde sus fuentes, contrasta 105 días de Canteras–Quillota con la versión 4, comprueba claves entre tablas y conserva los nulos analíticos. En mediciones se contrastan los doce extractos mensuales y la reextracción de junio, y se comprueba conservación de energía al agrupar.

El [informe integral](controles/verificacion_integral.json) y el registro de ejecución están guardados. Para reconstruir desde la raíz del proyecto:

```text
.venv/bin/python SOCHER_2026_dataset/scripts/reproducir_dataset.py
```

El entorno requiere pandas, numpy, pyarrow y openpyxl para lectura. Este comando parte de los extractos auditados ya preservados en las versiones 3, 4 y 6. No descarga nuevamente todos los originales y no presenta esa ejecución parcial como una adquisición completa independiente. Los scripts y las fuentes anteriores permanecen en el proyecto.
