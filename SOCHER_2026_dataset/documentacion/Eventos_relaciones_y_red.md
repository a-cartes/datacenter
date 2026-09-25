# Registro de centros, hitos y relaciones eléctricas

Esta consolidación organiza los antecedentes v2–v6 para construir el dataset del artículo. No modifica las versiones anteriores, no incorpora nuevas descargas y no asigna tratamientos causales a partir de fechas administrativas, anuncios, capacidad instalada o cambios de precios.

## Tablas y claves

Cada tabla se guarda en `tablas/` en CSV y Parquet. Los CSV representan los valores desconocidos mediante celdas vacías; los Parquet conservan valores nulos. Ningún vacío significa cero, «nunca tratado» o ausencia de exposición.

| Tabla | Filas | Unidad y clave | Uso |
|---|---:|---|---|
| `centros` | 10 | Candidato de campus/proyecto o barra sin centro adjudicado; `centro_id` | 9 candidatos y una fila especial para S/E Quilicura. No es un censo de 9 establecimientos independientes. |
| `relaciones_centros_barras` | 17 | Una relación documental; `relacion_id` | Une candidatos con barras, equipos o conexiones propuestas y conserva la incertidumbre de cada vínculo. |
| `eventos_documentados` | 24 | Un hito o hecho; `evento_id` | Separa operaciones, solicitudes, PES, EO, previsiones, mediciones y reglas de agregación. |
| `conexiones_red_documentadas` | 20 | Una relación descrita por una fuente; `conexion_id` | Insumo documental para reconstruir exposición eléctrica; todavía no constituye una matriz de pesos. |
| `fuentes_eventos_red` | 36 | Una referencia heredada; `fuente_id` | URL, archivo original cuando existe, páginas y hash declarado. |

Las claves `centro_id` y `campus_grupo_id` preservan las del registro v6. Chile 1 y Chile 2 de Ascenty permanecen agrupados como `ASCENTY_GUACOLDA_POR_DELIMITAR`. Las fases de EdgeConneX comparten `EDGE_COLINA`. Una fase, transformador o medidor no se contabiliza automáticamente como un centro nuevo. `QUILICURA_SIN_DC_ADJUDICADO` conserva la barra del piloto sin adjudicarla a Google, Ascenty o Cirion por proximidad geográfica.

## Fechas y evidencia

- `fecha_desde` y `fecha_hasta` son extremos inclusivos de la información disponible. Un mes o año incompleto se representa mediante sus extremos, **sin afirmar que la operación comenzó el primer día ni terminó el último**. `precision_fecha` debe acompañar siempre a esas columnas.
- En pruebas Dataluna, «fines de enero» se conserva mediante `MES_FINES_SIN_DIA`; el intervalo enero completo es una envolvente conservadora, no 31 días de pruebas comprobadas.
- `es_fecha_prevista=True` identifica expectativas. La PES de Ascenty Chile 2 prevista para agosto de 2026 y la EO de ODATA prevista para noviembre de 2025 no se convierten en fechas realizadas por haber transcurrido ese mes.
- Las fechas de una carta, una DIA o una solicitud son fechas de esos documentos/hitos administrativos, no de consumo eléctrico.
- `nivel_evidencia_fecha` indica el tipo y procedencia de la evidencia. No es una escala numérica de probabilidad. El estado del archivo original se consulta en `fuentes_eventos_red`.
- Los hechos horarios de Las Canteras conservan etiquetas UTC y locales con su desplazamiento. No se acreditó si la etiqueta representa inicio o fin del intervalo de 15 minutos; no se atribuye mayor precisión física.

El 24 de junio de 2024 contiene tres hitos observados distintos: primera subida de HT2 a las 21:30 locales, salto principal de HT2 a las 21:45 y aumento posterior de HT1 a las 23:00. El **25 de junio** se guarda aparte como primer día local completo posterior a la transición. Ninguno se etiqueta como «entrada del centro de datos» ni como intervención exógena. La caída temporal del 8 de julio también permanece separada. Las EO del 2 y 29 de mayo y la PES del 7 de abril no se fusionan con estos hechos medidos.

## Variables causales reservadas

`fecha_tratamiento_causal` y `cohorte_g` permanecen nulas. `elegible_causal=False` significa **expediente aún no cerrado para estimación**, no inexistencia de efecto o ausencia de tratamiento. `motivo_no_elegible` y `naturaleza_tratamiento_pendiente` indican qué debe resolverse: identidad del campus, medidor, carga neta nueva, suministro anterior, obra de red concurrente o fecha realizada.

No se crean indicadores `post`, `D_it`, `event_time`, «nunca tratado» o pesos de exposición. Deben construirse después de adjudicar las intervenciones, verificar las series y definir el estimando. Los 24 hitos no son 24 cohortes ni 24 centros. Aumentar filas horarias tampoco incrementa el número de intervenciones independientes.

## Vinculación con precios y red

`relaciones_centros_barras.barra_cmg` y `nemotecnico` heredan referencias de homologación de julio de 2024 cuando existen. Pueden ayudar a localizar precios, pero **no certifican suministro activo durante todo el período**. En particular, no se extrapolan identidades eléctricas de 2024/2026 a alimentadores de 2020 ni se fusionan los códigos históricos T0054/T0835 de Quilicura. Las columnas de vigencia operativa siguen nulas. Cuando no existe código de CMg adjudicado, `barra_fisica_o_propuesta` conserva la instalación candidata.

Una barra puede estar relacionada con varios centros: primero se mantiene una sola observación de precio por barra histórica × hora. La tabla de relaciones permite describir exposiciones múltiples; no autoriza duplicar ese precio y tratar las copias como resultados independientes.

Las conexiones de red conservan diseños de 2021, PES, instantáneas de diciembre de 2024 y eventos de 2025. `nodo_desde_documental` y `nodo_hasta_documental` son etiquetas de la fuente, no sentidos de flujo ni identificadores CMg resueltos. Algunas relaciones representan corredores agregados, no adyacencia física directa. Se mantienen las limitaciones originales y las referencias a páginas.

`vigencia_operativa_validada=False`, `utilizable_W_causal=False` y los pesos nulos impiden presentar estas relaciones como una matriz de exposición histórica ya validada. **Un par ausente es desconocido, no una arista de peso cero.** Se necesitan topología y estados aplicables a cada período, o una definición de exposición más limitada y documentada, antes de estimar spillovers.

## Reproducción y verificaciones

El programa `scripts/construir_eventos_relaciones.py` se ejecuta con el entorno `.venv` de la raíz del proyecto, que contiene pandas y pyarrow. Lee las tablas y manifiestos archivados y construye las cinco tablas sin conexión de red. El manifiesto `verificacion_eventos_relaciones.json` conserva hashes de insumos y salidas, esquemas, conteos y verificaciones de integridad referencial, claves, fechas y lectura Parquet.

Las fuentes archivadas que tienen hash declarado se comparan con el archivo local. Las fuentes previamente consultadas por web sin copia local se mantienen identificadas como tales; este programa no afirma haberlas descargado ni haber vuelto a verificar sus contenidos. Los archivos de mediciones se referencian a través del registro y auditoría v4; aquí no se vuelve a estimar la carga ni a extraer los archivos originales.
