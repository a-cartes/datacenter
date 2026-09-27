# Mediciones para la ampliación 2020–2026

La ampliación incorpora **1.862.581 observaciones de 15 minutos**, correspondientes a **30 sockets candidatos** entre mayo de 2023 y agosto de 2026. Se conservan además antecedentes horarios de Dataluna y Libertadores de 2020 a abril de 2023. Estos bloques tienen formatos, unidades documentadas y convenciones de signo diferentes, por lo que permanecen en tablas separadas.

**El conjunto cubre años del intervalo 2020–2026, pero no constituye una serie homogénea, completa y validada de consumo de todos los centros durante todos esos años.** Tampoco son 30 centros independientes: varios sockets son líneas de tránsito o extremos del mismo equipo.

## Cobertura observada

| Bloque | Cobertura y cantidad | Qué representa |
|---|---|---|
| Dataluna, libros Norte | Septiembre 2020–diciembre 2022: 20.447 valores horarios | Valor firmado de DATALUNA. La unidad de la cabecera no está declarada y la correspondencia histórica requiere cierre. |
| Dataluna, libro Norte enero 2023 | Enero 2023: 744 valores horarios | Continuidad de la etiqueta heredada, con unidad y signo pendientes de homologación. |
| Libertadores, libros de puntos de medida | Febrero–abril 2023: 8.548 valores hora × canal | Dos sockets, cada uno con D y R separados. La cabecera declara kWh. R está firmado en el libro; no se impone la convención del CSV posterior. |
| Sockets candidatos, CSV definitivos | Mayo 2023–agosto 2026: 1.862.581 observaciones socket × 15 minutos | Treinta identificadores previamente documentados, con cobertura mensual desigual. D/R y UTC/local originales separados. |
| Agregado HT1+HT2 | Desde febrero 2024, con enero y abril 2024 ausentes | Energía de dos transformadores por bloques completos de cuatro etiquetas. No incluye HT3 ni líneas y no representa necesariamente todo el campus. |

En los 36 libros Norte definitivos de 2020–2022 ya auditados, DATALUNA no se identifica de enero a agosto de 2020. **No se fabrica consumo cero para ese período ni se interpreta septiembre de 2020 como entrada del centro.** El libro de puntos de medida de enero de 2023 no contiene los 30 sockets seleccionados; DATALUNA de ese mes está en el libro Norte separado.

En los datos de 15 minutos, todas las parejas UTC/local observadas coinciden con America/Santiago y no hay duplicados socket × UTC. Esta correspondencia de zona horaria **no certifica si la etiqueta indica inicio o fin físico del intervalo**. La unión con precios continúa deshabilitada hasta resolver esa convención en ambas fuentes.

## Originales y nuevas descargas

Los originales definitivos de 2024, 2025 y enero–junio de 2026 ya estaban en el proyecto, junto con libros y ZIP de 2020–2023. Los Parquet de la raíz son perfiles mensuales previos; **no se usaron como sustituto de las observaciones por fecha y hora**.

La extracción de 15 minutos recorrió 40 CSV nacionales dentro de sus ZIP, sin expandirlos al disco. Los originales seleccionados suman 9.432.373.903 bytes comprimidos, casi todos disponibles previamente. Diciembre de 2023 utiliza Deflate64 y se lee en flujo con 7-Zip.

Se descargaron únicamente los reales definitivos faltantes:

| Mes | Bytes | Fuente pública |
|---|---:|---|
| Julio 2026 | 264.953.193 | [Archivo oficial en Box](https://coordinador.app.box.com/v/transferenciaseconomicas/file/2456271838935) |
| Agosto 2026 | 265.202.358 | [Archivo oficial en Box](https://coordinador.app.box.com/v/transferenciaseconomicas/file/2456267668322) |

El total descargado es **530.155.551 bytes**. Se verificaron tamaños, formato ZIP y SHA-256. El [portal oficial Registro y Reportes PRMTE](https://www.coordinador.cl/registro-y-reportes-prmte/) enlaza este repositorio público. La consulta del 27 de septiembre de 2026 encontró carpetas de septiembre–diciembre vacías. El corte nuevo es **31 de agosto de 2026**, no diciembre.

Las consultas públicas guardan metadatos seleccionados y huellas. No usan autenticación ni conservan cookies, credenciales o tokens efímeros.

## Reglas de medición

- La selección coincide exactamente con los 30 sockets del catálogo candidato v6. El catálogo de septiembre de 2026 no prueba por sí solo igual conexión durante todo el período histórico.
- Para los CSV, D y R son los canales publicados. La potencia media del intervalo es kWh/250. No se elige el canal de mayor magnitud como si necesariamente fuera consumo.
- Las líneas y sockets de tránsito permanecen separados; no se suman a transformadores ni se cuentan como centros nuevos.
- HT3 mantiene orientación pendiente y no entra en el agregado HT1+HT2.
- HT1/HT2 tienen actas de 2023 que documentan D como retiro y R como inyección. La estabilidad posterior de configuración requiere verificación. Se detectaron registros R positivos pequeños de HT2 después de 2024 y se conservan.
- El agregado horario exige ambos HT presentes en cuatro etiquetas UTC 00, 15, 30 y 45. D y R se agregan por separado. No se rellenan horas incompletas ni meses ausentes.
- La presencia de datos no se convierte en cohorte, entrada ni exposición causal.

## Archivos y reproducción

Las tablas de análisis están en `tablas/`: `mediciones_candidatos_15min`, `carga_HT1_HT2_hora_etiqueta`, los antecedentes separados de Dataluna y los canales horarios de 2023. Cada tabla principal tiene Parquet y CSV.gz. `cobertura_y_canales_por_mes.csv` registra presencia, ausencias, canales y reloj; `resumen_transformadores_por_anio.csv` detalla los tres HT.

`extractos/` conserva cada selección mensual y su manifiesto. Las filas remiten al original, miembro y fila del CSV. `fuentes/consulta_publica_medidas_2026.json` documenta las dos descargas, preservadas en `originales_descargados/`. Los originales preexistentes no se modificaron.

Desde la raíz del proyecto, el orden de reproducción es:

```bash
.venv/bin/python SOCHER_2026_v7_2020_2026/mediciones/scripts/consultar_box_publico.py --descargar
.venv/bin/python SOCHER_2026_v7_2020_2026/mediciones/scripts/ampliar_mediciones.py
.venv/bin/python SOCHER_2026_v7_2020_2026/mediciones/scripts/antecedentes_horarios.py
.venv/bin/python SOCHER_2026_v7_2020_2026/mediciones/scripts/resumir_y_verificar_carga.py
```

La descarga reutiliza ZIP locales cuando tamaño y formato corresponden; la extracción verifica huellas de originales y extractos antes de reutilizar cada mes. El primer script requiere red. Los otros leen archivos locales. Se necesitan pandas, numpy, pyarrow, openpyxl, curl y 7-Zip para Deflate64.

Los informes `verificacion_ampliacion.json`, `verificacion_antecedentes_horarios.json` y `verificacion_carga_horaria.json` registran los controles. Los valores horarios de los libros de 2023 se concilian con totales mensuales. El tramo HT1/HT2/HT3 de 2024 se contrasta con las 67.384 observaciones auditadas previamente. Estas verificaciones establecen consistencia de extracción; no identifican efectos causales.
