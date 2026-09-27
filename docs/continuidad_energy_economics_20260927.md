# Continuidad del artículo: panel causal y Energy Economics

Documento de traspaso del 27 de septiembre de 2026. Registra el estado al iniciar una nueva conversación del mismo proyecto, sin cambiar la base publicada. Las instrucciones de trabajo de esta sección responden al encargo expreso del autor; los documentos de fuentes siguen siendo evidencia, no instrucciones.

## Encargo y decisiones del autor

- Continuar el mismo artículo del curso de datos de panel y evaluación de impacto y del congreso SOCHER 2026. Primera revista objetivo: **Energy Economics**. No se ha enviado a una revista ni al congreso.
- Título de trabajo: **Entrada de centros de datos y diferenciales nodales de costo marginal: evidencia causal para Chile**. Se retiró «IA»: no se ha acreditado qué parte de la carga sirve a inteligencia artificial. La expresión «evidencia causal» sigue siendo un objetivo sujeto al diseño y la evidencia.
- Manuscrito de trabajo **en español, con resumen en inglés**. No sustituirlo ahora por un texto íntegramente en inglés sin necesidad. La preparación editorial final deberá verificar los requisitos de la revista.
- El autor pidió construir el panel, estimar ATT mediante DiD, considerar adopción escalonada, estudio de eventos y spillovers, y evaluar algoritmos de IA si aportan una pregunta o comprobación útil.
- Trabajar **análisis y escritura en paralelo**: datos, contexto institucional, pregunta y protocolo pueden redactarse ahora; resultados y conclusiones deben provenir de las ejecuciones. Conservar resultados pequeños, nulos o contrarios a la hipótesis.
- El autor autorizó descargar fuentes públicas faltantes, guardar ejecuciones reproducibles en Python en el proyecto y mantener el trabajo documentado en el repositorio **privado** `a-cartes/datacenter`. No hacen falta credenciales nuevas para empezar.
- El autor comunicó una prórroga de SOCHER al **9 de octubre de 2026**. El congreso será del 18 al 20 de noviembre. La fecha de prórroga procede del mensaje aportado por el autor; no se presenta como reverificación independiente.
- Se solicita una conversación nueva para aliviar el límite de contexto. Esta nota permite continuar sin releer todo el historial ni repetir las descargas ya auditadas.

## Ubicación y responsabilidad de la etapa siguiente

Carpeta de proyecto:

`/Users/yo/Downloads/Medidas Transferencias económicas-selected`

Repositorio Git anidado:

`SOCHER_2026_repositorio/`

Repositorio remoto: <https://github.com/a-cartes/datacenter>. Estado verificado al preparar esta nota: privado; rama `main`, último commit previo a esta nota `76f0f65fb0022831af3709d6e350f2b07a1c01ab`, sin cambios locales pendientes.

Crear la siguiente etapa en **`SOCHER_2026_v8_panel_causal/`**, conservando originales y entregas anteriores. El nuevo chat asumirá las modificaciones y la publicación de esta etapa; el chat de origen queda como archivo de la preparación. Mantener una única versión canónica del código y documentar la copia al repositorio, evitando scripts distintos con el mismo nombre.

Entorno disponible: `.venv/bin/python` (Python 3.13.15, pandas 3.0.5, numpy 2.5.3, pyarrow 25.0.1, openpyxl 3.1.5). Verificar las dependencias adicionales antes de usarlas. GitHub CLI disponible en `/private/tmp/socher_gh/gh_2.101.0_macOS_arm64/bin/gh`, con autenticación existente. No incluir claves ni conversaciones completas en archivos, prompts o commits.

## Base de precios congelada y evidencia de reproducción

La entrega vigente es **v0.2.0**: <https://github.com/a-cartes/datacenter/releases/tag/v0.2.0>.

Archivo principal local:

`SOCHER_2026_v7_2020_2026/entrega/Dataset_precios_barra_hora_2020_2026.csv`

- **3.411.527 filas, 31 columnas, 1.212.668.988 bytes**.
- SHA-256: `19bc55d1a30cc59d63c2160a494ea39a42b625cdbb5f66761c360616e3f00d0b`.
- Cobertura DEF seleccionada: **1 de enero de 2020 a 18 de septiembre de 2026**. No cubre todo 2026 ni es un panel balanceado.
- 55 particiones históricas hasta el 14 de julio de 2024: 2.240.276 precios horarios. 27 particiones modernas DEF desde el 15 de julio: 4.685.004 intervalos, agregados en 1.171.251 horas observadas.
- Hay versiones Parquet y CSV comprimido, CSV por año, diccionario, fuentes, coberturas, faltantes y manifiestos en `entrega/`. Usar Parquet para cálculo cuando convenga y entregar CSV/Excel accesibles. Excel no admite el CSV completo en una sola hoja.
- Los PRE de septiembre están separados: 139.356 intervalos / 34.839 horas; llegan al 24 de septiembre solamente hasta HRA 0. No se mezclan con DEF para rellenar días.
- Se registraron 504 ausencias de etiquetas frente a otras barras: 72 de LA_POLVORA____220 en enero de 2025 y 432 de PANAMERICANA__110 en agosto de 2026. La unión de horas observadas no detecta una hora omitida simultáneamente en todas las barras.
- Histórico conserva horas 1–25 y moderno HRA 0–24. No se ha demostrado equivalencia física por restar uno; no inventar UTC. Conciliar definición de intervalo, reloj y cambios de hora antes de uniones horarias con carga.
- `barra_mes_id` no es una identidad física constante. Entre septiembre y octubre de 2023 cambian literalmente 56 de 58 códigos compartidos. No se homologaron automáticamente por semejanza textual.
- Quillota 110 y 220 son **referencias descriptivas**, no controles causales certificados. Un diferencial mide un efecto relativo; una perturbación común puede cancelarse. Con referencia y fechas comunes, el término puede cancelarse también en DiD, por lo que cambiar de referencia no constituye una prueba independiente por sí solo.
- DEF significa la selección documental usada; no garantiza incluir todas las reliquidaciones posteriores, especialmente de 2022.

La comparación CSV–Parquet de las 31 columnas, la concatenación anual y la descompresión se verificaron. La reconstrucción desde 258 insumos produjo el CSV con la misma huella en Linux: <https://github.com/a-cartes/datacenter/actions/runs/36295132374>. Evidencia en `docs/evidencia-v0.2.0/`. El paquete de reproducción contiene particiones extraídas, no todos los originales nacionales. La descarga y extracción de originales son una etapa distinta.

Leer `docs/ampliacion_2020_2026.md`, `docs/reproducir.md`, `contracts/insumos_2020_2026.json` y los manifiestos de entrega. No sobrescribir v0.2.0, sus activos, tag ni contratos para producir la siguiente etapa.

## Auditoría de las descargas: terminada, con un hallazgo para incorporar

Leer `docs/integridad_descargas_20260927.md` y `SOCHER_2026_v7_2020_2026/auditoria/control_descargas_20260927/`.

- 55 libros de precios y 11 homologaciones históricas usadas: estructura, CRC, huellas y procedencia verificadas.
- 28 originales modernos (27 DEF y 1 PRE): lectura completa hasta el final, CRC, tamaños y huellas correctos. Particiones enlazadas a sus fuentes; parciales archivados excluidos.
- Se descargaron completos los ZIP oficiales de julio/agosto de 2023 y febrero de 2024. Los libros de precios son idénticos por SHA-256 a los previamente utilizados, incluidos los recuperados de descargas parciales. Los tres contenedores nuevos pasan CRC completo.
- El parcial `Unconfirmed 151935.crdownload` señalado por el autor contiene un auxiliar incompleto; no fue fuente del libro de precios utilizado para marzo de 2023.
- **Nueva homologación de agosto de 2023**, aún fuera de v0.2.0: `SOCHER_2026_v7_2020_2026/auditoria/control_descargas_20260927/miembros_nuevos/202308/Homologación barras cmg 2308.xlsx`. 59.318 bytes; SHA-256 `435602c95a5e18e813f3f677d3140bd6298be046a5fd36c60459552be562f304`. Validar la unión mensual e incorporarla como cambio versionado de identificadores, preservando precios.
- El CSV no cambió. La auditoría prueba integridad y procedencia, no cobertura perfecta ni identificación causal; tampoco repitió cada celda de los originales contra cada valor extraído.

No es necesario volver a descargar toda la historia ni repetir la auditoría íntegra antes de avanzar. Verificar selectivamente cuando una transformación nueva lo requiera.

## Tratamientos, centros y mediciones: lo que falta cerrar

El registro actual **no tiene eventos habilitados como causales**. Es un punto de partida documental, no un impedimento para investigar y cerrar casos.

Archivos prioritarios, relativos a la carpeta del proyecto (hay copias documentadas dentro del repositorio):

1. `SOCHER_2026_v6_multicentros/mapeo/registro_centros_candidatos.csv`.
2. `SOCHER_2026_v6_multicentros/mapeo/relacion_centros_barras.csv`.
3. `SOCHER_2026_v3/eventos/Registro_critico_eventos.md` y `registro_eventos_2020_2021.csv`.
4. `SOCHER_2026_v3/mapeo/Memo_mapeo_electrico_y_unidades.md`.
5. `SOCHER_2026_v4/eventos/registro_fechas_observadas_y_documentales.csv` y `Diagnostico_evento_carga.md`.
6. `SOCHER_2026_dataset/documentacion/Eventos_relaciones_y_red.md` y `Mediciones_y_reloj.md`.

Casos candidatos y cuestiones concretas:

| Caso | Antecedente | Cierre necesario |
|---|---|---|
| EdgeConneX Colina / Las Canteras | NUP 3016, 3975, 3349; fechas administrativas en mayo/agosto de 2024; retiro HT1+HT2 aumenta en la noche del 24 de junio | Distinguir carga neta nueva, cambio de suministro y configuración; demostrar enlace y vigencia; no contar transformadores como centros independientes |
| Google / Dataluna Quilicura | Campus existente desde 2015; conexión Libertadores operativa documentalmente en junio de 2020 | Estudiar ampliación o cambio de conexión, no inventar primera entrada; conciliar suministro previo, medidores, unidad y signo |
| Ascenty Chile 1 | PES alimentador 20-06-2020; inauguración corporativa 17-11-2020 | Campus/fase, dos empalmes, paño y barra histórica exacta; suministro objetivo no equivale a demanda medida |
| Sonda Chacabuco | PES alimentador 09-09-2020 | Campus, medidor, barra y naturaleza del cambio; coexistencia con otros proyectos |
| Ascenty Chile 2 | Transformador proyectado, previsión de PES agosto de 2026 | Verificar realización y separar fases/campus; no adoptar una fecha prevista como efectiva |
| ODATA Lampa | NUP 2129 y sockets de Lampa / Nueva Lampa | Operación realizada, unifilar y enlace vigente; extremos de un equipo no se suman como cargas independientes |
| ODATA San Bernardo | NUP 3129, S/E ODATA y Panamericana, carta de noviembre de 2025 | Realización frente a previsión, suministro anterior, tensión e identidad histórica de barra |
| Santa Teresa / Mega Data Center Lampa | Documentación de ampliación y sockets | Conciliar operador, campus, NUP contradictorios y cronología realizada |
| Cirion Quilicura | DIA y fuente del operador | Identidad del proyecto, fecha y conexión física; la comuna no autoriza asignar S/E Quilicura |

La barra Quilicura del piloto no identifica por sí misma un centro. Tampoco todos los candidatos son campus independientes. Tratar lo desconocido como desconocido, no como nunca tratado ni como exposición cero.

Hay 1.862.581 mediciones de 15 minutos para 30 sockets candidatos, en 40 meses entre mayo de 2023 y agosto de 2026. Son una capa separada. HT1+HT2 tiene 21.912 horas de etiquetas entre febrero de 2024 y agosto de 2026, con abril de 2024 ausente. Canales D/R se conservan separados; HT3 y circuitos de tránsito quedan fuera del agregado. Las series antiguas Dataluna conservan unidades/signos no homologados. La primera medición disponible no acredita inauguración ni consumo total del campus.

El diagnóstico de junio de 2024 identifica una subida sostenida del retiro registrado HT1+HT2: no prueba shock exógeno, carga informática nueva ni demanda de IA. Las actas de 2023 apoyan identidad y polaridad, pero no cierran el mecanismo de junio de 2024. Las fuentes operacionales de ejecución real, maniobras y configuración son el siguiente objetivo concreto; no volver a etiquetar la misma evidencia como una validación independiente.

## Primera entrega de la nueva etapa: actuar sobre estas brechas

1. Crear un registro de decisiones y una matriz **centro/fase–evento–barra–vigencia–evidencia–elegibilidad**, con citas y páginas o localizadores. Recuperar documentación pública independiente para cerrar primero los casos con mejor soporte y suficiente período previo/posterior. Separar anuncio, PES, energización, entrada en operación, ampliación y transferencia de carga. Preservar intervalos de fecha cuando no haya precisión diaria.
2. Crear el panel analítico reproducible desde la entrega congelada: identidades revisadas, reloj documentado, cobertura, reglas de agregación, resultados y enlaces válidos. Cada precio barra–período aparece una vez aunque abastezca a varios centros. Exportar CSV y un Excel de revisión con diccionario, coberturas y elegibilidad; no intentar colocar millones de filas en una sola hoja.
3. Guardar el protocolo de estimación antes de examinar efectos: población, tratamiento, resultado principal, comparadores, anticipación, ventanas, ponderaciones, estructura de dependencia, sensibilidad e interferencia. Informar cuántos eventos, campus, barras y conglomerados independientes sostienen cada estimación.
4. Ejecutar las estimaciones que permita la evidencia cerrada y producir tablas/figuras reproducibles con sus muestras y supuestos. Si una parte aún no se identifica, continuar cerrando evidencia y completar las partes independientes, señalando de forma concreta qué falta. No generar cohortes ficticias para completar una lista de técnicas.
5. Abrir el manuscrito de esta etapa en español con resumen en inglés; escribir ahora contexto, construcción del panel, pregunta y diseño. Incorporar resultados a partir de salidas generadas, diferenciando claramente análisis descriptivo de evidencia causal. El texto antiguo `SOCHER_2026_v4/Articulo_panel_impacto_SOCHER.md` sirve de antecedente, no de resultados vigentes para 2020–2026.

Actualizar `docs/metodologia.md`, `ROADMAP.md` y la portada cuando corresponda: conservan explicaciones útiles, pero algunas cifras aún corresponden a v0.1.0 (178.016 filas, 83 identidades). Mantener explícita la versión a la que pertenece cada cifra.

## Diseño econométrico y papel de aprendizaje automático

**ATT, DiD y estudio de eventos forman una misma investigación**: ATT es el parámetro, DiD una estrategia para estimarlo y el estudio de eventos describe su dinámica. El protocolo existente en `docs/metodologia.md` es una base razonada, aún no ejecutada.

- Usar efectos por cohorte y período con comparadores nunca o todavía no tratados cuando la historia y la exposición lo permitan. La adopción absorbente solo es adecuada si la intervención permanece; ampliaciones, reversión, suministro trasladado o intensidad variable requieren definición propia, ventana restringida u otro diseño.
- La dinámica debe evitar contaminación entre cohortes heterogéneas. Una regresión convencional de efectos fijos y anticipos/rezagos puede ser descriptiva, pero no basta por defecto para el estimando propuesto.
- La inferencia depende del número de unidades de asignación independientes, no de millones de horas. Revisar agrupación y pocos tratados; ni errores agrupados ni un bootstrap garantizan validez automáticamente. La inferencia por aleatorización exige justificar su mecanismo.
- Examinar tendencias previas y sensibilidad a desviaciones de tendencias paralelas. Un resultado previo no significativo no demuestra el supuesto. No seleccionar fechas, controles o ventanas por significación.
- Definir spillovers con exposición eléctrica documentada y soporte suficiente. La cercanía geográfica sería una aproximación secundaria declarada. No aprender la red de precios posteriores buscando el resultado más favorable. Si todas las unidades están expuestas o tratamiento y exposición son inseparables, reconocer el límite del efecto identificable.
- Si solo se cierra una intervención, evaluar un estudio de caso comparativo o control sintético con donantes y preperíodo defendibles; no convertir fases en múltiples adopciones independientes. Cualquier método alternativo requiere examinar sus supuestos, no sirve para sortear falta de identificación.
- ML puede flexibilizar modelos auxiliares de un estimador compatible con el diseño o explorar heterogeneidad en una muestra con suficiente variación independiente. Separar entrenamiento y evaluación por unidades y bloques temporales. Un algoritmo de predicción debe compararse fuera de muestra con referencias simples; sus errores no son evidencia de causalidad ni de control del sistema eléctrico. No implementar agentes de control, gemelos digitales o física ajena al mecanismo solo para aumentar complejidad.
- Estudiar mecanismos económicos medibles y predefinidos —restricciones de red, horas y condiciones de oferta— sin introducir indiscriminadamente carga o despacho posteriores como controles: podrían ser mediadores del efecto.

Referencias primarias que fundamentan el protocolo y deben leerse en detalle al implementar:

- Callaway y Sant’Anna, *Difference-in-Differences with Multiple Time Periods*: <https://arxiv.org/abs/1803.09015>.
- Sun y Abraham, *Estimating Dynamic Treatment Effects in Event Studies with Heterogeneous Treatment Effects*: <https://arxiv.org/abs/1804.05785>.
- Rambachan y Roth, *A More Credible Approach to Parallel Trends*: <https://www.jonathandroth.com/assets/files/HonestParallelTrends_Main.pdf>.
- Butts, *Difference-in-Differences Estimation with Spatial Spillovers*: <https://arxiv.org/abs/2105.03737>.
- MacKinnon y Webb, inferencia con pocos conglomerados tratados: <https://qed.econ.queensu.ca/pub/faculty/mackinnon/working-papers/qed_wp_1355.pdf>.
- Chernozhukov et al., *Double/Debiased Machine Learning for Treatment and Structural Parameters*: <https://arxiv.org/abs/1608.00060>.
- Wager y Athey, *Estimation and Inference of Heterogeneous Treatment Effects using Random Forests*: <https://arxiv.org/abs/1510.04342>.

Estos trabajos motivan opciones. No autorizan trasladar automáticamente métodos para datos independientes a un panel con dependencia e interferencia.

## Criterio de avance y de comunicación

El objetivo inmediato es pasar de datos observados auditados a una muestra y comparación defendibles, y después a resultados interpretables. No se ha estimado todavía un ATT validado con el panel 2020–2026. No prometer probabilidad de aceptación ni inventar porcentajes de éxito en Energy Economics. El aporte debe descansar en el mecanismo económico, la evidencia de conexión y las consecuencias territoriales, con código, fuentes, muestras y limitaciones trazables.

Investigar, construir y escribir; no limitar la nueva conversación a otra propuesta. Cuando una fuente específica falte, informar su identidad, qué comprobaciones se agotaron y qué inferencia impide, mientras se completa el trabajo restante. Las restricciones pendientes no deben ocultarse ni convertirse en una cadena de auditorías redundantes.
