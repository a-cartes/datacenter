# Activos locales para ampliar la base 2020–2026

Corte: 2026-09-27. Auditoría local de disponibilidad; no extracción nacional nueva ni estimación causal.

## Archivos existentes y huecos

| Año | Archivos en carpeta anual | Meses con archivos | Precios y faltantes principales |
|---|---:|---|---|
| 2020 | 72 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 | No se encontraron libros CMg mensuales ni panel nodal auditado de ese año en el alcance local. |
| 2021 | 88 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 | No se encontraron libros CMg mensuales ni panel nodal auditado de ese año en el alcance local. |
| 2022 | 93 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 | No se encontraron libros CMg mensuales ni panel nodal auditado de ese año en el alcance local. |
| 2023 | 67 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 | Solo exportaciones históricas de Quillota110/220 y Quilicura110; faltan precios multicentro y homologaciones mensuales. |
| 2024 | 50 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 | Multicentro: faltan enero/marzo, homologación exacta de mayo, y extensión desde15jul para los demás nodos. Hay cinco barras bajo nuevo régimen hasta diciembre. |
| 2025 | 48 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 | Mediciones nacionales disponibles; no se encontraron precios CMg ni homologación horaria multibarra de2025 en el alcance local. |
| 2026 | 24 | 1, 2, 3, 4, 5, 6 | Mediciones disponibles enero–junio; julio–septiembre sin archivos locales y octubre–diciembre futuros al corte. No se encontraron precios CMg multibarra de2026 en el alcance local. |

Las carpetas de meses vacías no cuentan como observaciones. Los archivos anuales son principalmente **mediciones/transferencias, no precios CMg**. En 2020–2022 predominan libros regionales con varias versiones. En 2023 conviven libros regionales y archivos de puntos de medida; desde 2024 predominan los ZIP de mediciones a 15 min. Mantener separados real, estimado e incompleto y elegir versión con trazabilidad.

Hay 210 Parquet derivados con prefijo anual en la raíz. Son productos previos y no sustituyen la inspección de encabezados/unidades/identidad de los libros originales. El inventario anterior `SOCHER_2026_v2/evidencia/inventario_parquet_verificado.csv` documenta claves y etiquetas faltantes en varios productos; no aceptarlos como panel causal por su extensión Parquet.

## Fuentes aprovechables ahora

- **precios_historicos_archivados_v3, 2023**: `SOCHER_2026_v3/precios/CEN_CMg_historicos_locales_2023_20240714_deduplicado.csv`; 26283 filas, 2023-01-01–2023-12-31, 3 códigos. No cubre todos los centros.
- **precios_historicos_archivados_v3, 2024**: `SOCHER_2026_v3/precios/CEN_CMg_historicos_locales_2023_20240714_deduplicado.csv`; 12267 filas, 2024-01-01–2024-07-14, 4 códigos. No cubre todos los centros.
- **precios_2024_v6**: `SOCHER_2026_v6_multicentros/precios/CEN_panel_barra_hora_identificado_hasta_20240714.parquet`. 83 identidades no son establecimientos; mayo tiene códigos provisionales
- **precios_regimen_nuevo_2024**: `SOCHER_2026_v3/precios/CMg_nuevo_cinco_barras_horas_originales.csv.gz`. Mantener régimen y reloj separados; no empalme automático con libros anteriores
- **dataluna_regional**: `SOCHER_2026_v3/consumo/dataluna_horario_2020_2022.csv.gz`. Serie firmada de etiqueta DATALUNA; no carga incremental validada ni primera entrada
- **canteras_15min_2024**: `SOCHER_2026_v3/consumo/las_canteras_transformadores_15min_2024.csv.gz`. HT1/HT2 y HT3 separados; falta consumo de los otros candidatos

Los libros mensuales de CMg de 2024 conservados cubren febrero, abril, mayo, junio y julio. Enero y marzo tienen homologaciones recuperadas, pero no libro completo utilizable en esta capa. Mayo sigue sin homologación mensual exacta. No se encontraron ZIP mensuales CMg completos adicionales dentro de este workspace; los ZIP nacionales de las carpetas anuales son mediciones. Descargas externas al workspace quedan fuera de esta revisión.

## Centros, conexiones y barras objetivo

El registro contiene nueve filas candidatas de campus/proyecto y una fila de S/E Quilicura sin centro adjudicado. Ascenty Chile1/2 comparte un grupo por delimitar; los transformadores de EdgeConneX son fases/equipos del mismo campus. **Las 83 claves históricas no son 83 establecimientos.**

| Candidato | Barras o equipos a investigar | Límite principal |
|---|---|---|
| EDGE_COLINA | CANTERAS______110; CHACABUCO_____110; CHICUREO______220 | Medir carga neta nueva frente a cambio de suministro; no contar HT1/HT2/HT3 como centros independientes; resolver HT3 y estado BP1/BP2 |
| DATALUNA_QUILICURA | TLIBERTADORES_110; CHACABUCO_____023 | Conciliar unidad/signo serie 2020-22, suministro previo y ampliación; H1/H2 son tránsito; no sumar con Chacabuco sin balance |
| ASCENTY_CHILE1 | CHACABUCO_____013 | Identificar los dos empalmes y series individuales; coincidencia posterior con Sonda; 6 MW de suministro objetivo no es consumo observado |
| SONDA_CHACABUCO | CHACABUCO_____023 | Medidor específico, campus y expansión frente a cambio de suministro; posición inicialmente compartida con Ascenty |
| ASCENTY_CHILE2 | CHACABUCO_____110; CHACABUCO_____023 | Comprobar ejecución, medidores y fecha; mismo grupo Ascenty hasta delimitar campus/fases; no interpretar previsiones como entrada ni carga real |
| ODATA_LAMPA | LAMPA_________220; LAMPA_________023; Nueva Lampa220 | Revisar NUP2129, unifilar y fecha realizada; JT5 y ET5 pueden representar extremos del mismo trafo: no sumar; códigos Lampa no validan Nueva Lampa |
| ODATA_SAN_BERNARDO | Panamericana110; ODATA110/13 | No usar Panamericana12 como110; reconciliar fases previas y suministro anterior; separar carga de líneas/transformadores y verificar cronología |
| SANTA_TERESA_LAMPA | Santa Teresa220; Nueva Lampa220 | Conciliar NUP y permisos con instalación realizada; no sumar extremos de la línea; conexiones autorizadas no son carga observada |
| CIRION_QUILICURA | Sin conexión adjudicada | Identificar conexión real y medidor; dirección/comuna no autorizan asignar S/E Quilicura |
| QUILICURA_SIN_DC_ADJUDICADO | QUILICURA_____110 | Recuperar solicitudes y beneficiario final; no asignar Google, Ascenty o Cirion por comuna; conciliar cambio T0054→T0835 |

Añadir Canteras23 y Chicureo23 como niveles documentados sujetos a vigencia; Quillota110/220 como referencias explícitas; Cerro Navia110/220 y Las Vegas110 BP1/BP2,44 y13 como nodos del corredor o niveles auxiliares. Una barra de referencia no se declara automáticamente control no expuesto.

Nueva Lampa220, Santa Teresa220, ODATA110/13 y Panamericana110 requieren homologación propia. **PANAMERICANA__012 no sustituye Panamericana110.** Cirion no tiene barra adjudicada. La comuna Quilicura no autoriza asignar S/E Quilicura a Google, Ascenty o Cirion.

## Identidad histórica: conservar separada

| Etiqueta CMg | Código observado | Meses con evidencia en el inventario v6 | Exactos / provisionales |
|---|---|---|---|
| `C.NAVIA_______110` | `BA01T0002SE008T0002` | 202402, 202404, 202405, 202406, 202407 | 202402, 202404, 202406, 202407 / 202405 |
| `C.NAVIA_______220` | `BA03T0002SE008T0002` | 202402, 202404, 202405, 202406, 202407 | 202402, 202404, 202406, 202407 / 202405 |
| `CANTERAS______023` | `BA04T0487SE001T0487` | 202404, 202405, 202406, 202407 | 202404, 202406, 202407 / 202405 |
| `CANTERAS______110` | `BA01T0487SE001T0487` | 202404, 202405, 202406, 202407 | 202404, 202406, 202407 / 202405 |
| `CHACABUCO_____013` | `BA03T0054SE009T0054` | 202402 | 202402 / — |
| `CHACABUCO_____013` | `BA03T0835SE009T0835` | 202404, 202405, 202406, 202407 | 202404, 202406, 202407 / 202405 |
| `CHACABUCO_____023` | `BA05T0054SE009T0054` | 202402 | 202402 / — |
| `CHACABUCO_____023` | `BA05T0835SE009T0835` | 202404, 202405, 202406, 202407 | 202404, 202406, 202407 / 202405 |
| `CHACABUCO_____110` | `BA01T0054SE009T0054` | 202402 | 202402 / — |
| `CHACABUCO_____110` | `BA01T0835SE009T0835` | 202404, 202405, 202406, 202407 | 202404, 202406, 202407 / 202405 |
| `CHICUREO______023` | `BA04T0054SE115T0054` | 202402 | 202402 / — |
| `CHICUREO______023` | `BA04T0835SE115T0835` | 202404, 202405, 202406, 202407 | 202404, 202406, 202407 / 202405 |
| `CHICUREO______220` | `BA01T0054SE115T0054` | 202402 | 202402 / — |
| `CHICUREO______220` | `BA01T0835SE115T0835` | 202404, 202405, 202406, 202407 | 202404, 202406, 202407 / 202405 |
| `L.VEGAS2______110` | `BA02T0057SE021T0057` | 202402, 202404, 202405, 202406, 202407 | 202402, 202404, 202406, 202407 / 202405 |
| `L.VEGAS_______013` | `BA05T0057SE021T0057` | 202402, 202404, 202405, 202406, 202407 | 202402, 202404, 202406, 202407 / 202405 |
| `L.VEGAS_______044` | `BA03T0057SE021T0057` | 202402, 202404, 202405, 202406, 202407 | 202402, 202404, 202406, 202407 / 202405 |
| `L.VEGAS_______110` | `BA01T0057SE021T0057` | 202402, 202404, 202405, 202406, 202407 | 202402, 202404, 202406, 202407 / 202405 |
| `LAMPA________023` | `BA03T0054SE020T0054` | 202402 | 202402 / — |
| `LAMPA________023` | `BA03T0835SE020T0835` | 202404 | 202404 / — |
| `LAMPA_________023` | `BA03T0835SE020T0835` | 202406, 202407 | 202406, 202407 / — |
| `LAMPA_________220` | `BA01T0054SE020T0054` | 202402 | 202402 / — |
| `LAMPA_________220` | `BA01T0835SE020T0835` | 202404, 202405, 202406, 202407 | 202404, 202406, 202407 / 202405 |
| `QUILICURA_____013` | `BA05T0054SE037T0054` | 202402 | 202402 / — |
| `QUILICURA_____013` | `BA05T0835SE037T0835` | 202404, 202405, 202406, 202407 | 202404, 202406, 202407 / 202405 |
| `QUILICURA_____023` | `BA03T0054SE037T0054` | 202402 | 202402 / — |
| `QUILICURA_____023` | `BA03T0835SE037T0835` | 202404, 202405, 202406, 202407 | 202404, 202406, 202407 / 202405 |
| `QUILICURA_____110` | `BA01T0054SE037T0054` | 202402 | 202402 / — |
| `QUILICURA_____110` | `BA01T0835SE037T0835` | 202404, 202405, 202406, 202407 | 202404, 202406, 202407 / 202405 |
| `QUILLOTA______110` | `BA01T0002SE032T0002` | 202402, 202404, 202405, 202406, 202407 | 202402, 202404, 202406, 202407 / 202405 |
| `QUILLOTA______220` | `BA02T0002SE032T0002` | 202402, 202404, 202405, 202406, 202407 | 202402, 202404, 202406, 202407 / 202405 |
| `TLIBERTADORES_110` | `BA01T0043SE001T0043` | 202402, 202404, 202405, 202406, 202407 | 202402, 202404, 202406, 202407 / 202405 |

Chacabuco, Chicureo, Quilicura y Lampa muestran códigos T0054/T0835 en las publicaciones examinadas. No se adjudica continuidad física solo por igualdad de nombre. Las etiquetas `LAMPA________023` y `LAMPA_________023` también se conservan explícitas. Los códigos de julio de 2024 del registro de candidatos no certifican vigencia en 2020–2026.

## Decisiones inmediatas de construcción

1. Extraer mediciones reales definitivas disponibles 2023–2026 para los sockets candidatos y conservar canales/signos; auditar las versiones regionales 2020–2022 por separado.
2. Obtener precios y homologaciones de cada año/período para las barras objetivo; aprovechar los extractos existentes como controles de solapamiento, sin duplicarlos.
3. Mantener un panel único barra×etiqueta horaria y tablas separadas de centros, fases, vínculos y eventos. No multiplicar filas de precio por número de centros asociados.
4. Cerrar identidad temporal y reloj antes de unir carga y precio; mantener desconocidos como nulos y cualquier fecha causal sin adjudicar.

El JSON acompaña el inventario completo de archivos, miembros declarados de ZIP, rutas reutilizables, mapeo y hashes de los registros pequeños utilizados. No modifica fuentes ni declara integridad del contenido nacional solo por leer el directorio ZIP.
