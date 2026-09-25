# Construcción, reproducción y versionado del dataset

Fecha del registro: 25 de septiembre de 2026.

Artículo: **Entrada de centros de datos y diferenciales nodales de costo marginal: evidencia causal para Chile**. El título expresa la pregunta de investigación; esta entrega contiene la base observada y no resultados causales.

## Decisión de trabajo

Conservar y documentar la base actual antes de adjudicar tratamientos. La validación de las fechas de entrada y del suministro eléctrico será una etapa posterior, registrada con sus fuentes y decisiones. Esto permite comprobar qué cambió entre versiones y evita reconstruir esas decisiones después de conocer los resultados.

Se recomienda un repositorio privado de GitHub para el trabajo en curso. Esta carpeta todavía no es un repositorio Git ni tiene un destino remoto configurado. El registro local descrito aquí no equivale a una publicación en GitHub.

## Qué contiene esta versión

El panel horario tiene 178.016 filas y 66 variables, con una observación por identidad histórica de barra, fecha y etiqueta horaria publicada. Las 83 identidades históricas de barra no representan 83 centros de datos. Se preservan las etiquetas de hora originales, incluida la hora 25; el reloj UTC de los precios sigue sin validar.

Los precios disponibles corresponden a febrero, abril, mayo, junio y del 1 al 14 de julio de 2024. No se imputaron los meses ausentes. Hay 137.096 filas con homologación mensual exacta y 40.920 con enlace provisional de mayo. Las 12.581 filas con marcas de revisión o no publicación se mantienen identificadas, y las reglas estrictas de calidad las excluyen.

El Excel y el CSV contienen este mismo panel. El libro añade un diccionario. Los campos de tratamiento, cohorte, tiempo relativo al evento, control y exposición permanecen vacíos mientras no exista una adjudicación defendible. Los precios iguales a cero se conservan como valores observados.

## Proceso que produjo la base

| Etapa | Operación realizada | Evidencia guardada |
|---|---|---|
| Recuperación previa | Descarga, preservación y extracción de archivos públicos y homologaciones del Coordinador, junto con fuentes documentales de proyectos. Esta etapa está distribuida entre versiones anteriores. | Manifiestos y fuentes en `SOCHER_2026_v2`, `v3`, `v4` y `v6_multicentros`. |
| Identificación de precios | Integración de series por identidad histórica de barra, fecha y etiqueta de hora, preservando origen y estado de homologación. | `scripts/construir_panel_precios.py`; `tablas/barras.parquet` y `tablas/periodos_fuente.parquet`. |
| Resultados descriptivos | Cálculo de diferencias respecto de Quillota 110 y 220 kV en el mismo período publicado, con indicadores de calidad y de autorreferencia. | Panel horario, panel diario y `controles/verificacion_integral.json`. |
| Centros, eventos y red | Registro separado de candidatos, hitos, relaciones documentales y conexiones. Una coincidencia de código no acredita suministro histórico. | `scripts/construir_eventos_relaciones.py`; tablas de centros, eventos, relaciones y red. |
| Mediciones | Integración de 67.384 registros de medidores de Las Canteras y agregación de HT1 y HT2 en 7.319 bloques horarios publicados. | `scripts/construir_mediciones.py`; controles de mediciones y documentación del reloj. |
| Verificación | Comparación con extracciones anteriores, comprobación de claves, diferenciales, energía, cobertura y valores desconocidos. | `controles/verificacion_integral.json` y controles de mediciones. |
| Entrega para revisión | Exportación del panel a CSV UTF-8 sin comprimir y a Excel con tipos, filtros y diccionario. | `controles/verificacion_exportacion_excel_csv.json`. |

Las mediciones no se han unido a las filas de precios: falta conciliar reloj, suministro y vigencia. Tampoco se han estimado ATT, DiD, estudio de eventos ni spillovers sobre esta base.

## Qué significa reproducible en el estado actual

**Reconstrucción local comprobada:** existe una ejecución exitosa de seis pasos desde los extractos conservados, registrada en `controles/registro_reproduccion.json`. Las exportaciones finales se verificaron celda por celda frente a la fuente: 178.016 filas, 66 variables, identificadores únicos y vacíos preservados. El error numérico máximo del Excel fue 5,684 × 10⁻¹⁴, inferior a la tolerancia de 10⁻¹⁰. Las 66 definiciones del diccionario, filtros y paneles congelados también fueron comprobados.

**Reconstrucción independiente pendiente:** todavía no se ha probado un clon limpio en otro equipo. El ejecutor actual usa extractos previos y no vuelve a descargar ni a extraer todos los archivos originales. Subir únicamente esta subcarpeta no bastaría.

Los requerimientos guardados recogen las versiones principales observadas. No sustituyen un archivo completo de dependencias fijadas ni una prueba de instalación limpia. Se usaron Python 3.13.15 para la reconstrucción y Python 3.12.14 para la exportación y su verificación.

## Secuencia local existente

Desde la raíz del proyecto, con los insumos anteriores presentes:

```text
.venv/bin/python SOCHER_2026_dataset/scripts/reproducir_dataset.py
```

Ese comando no genera las entregas finales de Excel y CSV. La secuencia adicional, con Python 3.12.14 y las dependencias de exportación, es:

```text
python SOCHER_2026_dataset/scripts/preparar_exportacion_excel_csv.py
python SOCHER_2026_dataset/scripts/exportar_excel_por_bloques.py
python SOCHER_2026_dataset/scripts/verificar_exportacion_excel_csv.py
```

Estos comandos reconstruyen productos y actualizan controles; deben ejecutarse en una copia de trabajo si se desea conservar una versión anterior. Las rutas de salida siguen vinculadas a la carpeta `outputs/01a0d6c3-09cd-7aa3-903d-5ee59e65c071` y los scripts comprueban las dimensiones de esta entrega.

La primera exportación mediante Artifact Tool construyó y permitió revisar el diseño, pero falló al guardar el libro por agotamiento de memoria. La entrega final se produjo mediante escritura secuencial con openpyxl y se verificó íntegramente. El script alternativo está conservado; no es necesario ejecutar el intento fallido para reproducir la entrega.

## Ajustes pendientes para GitHub

1. **Reunir los insumos realmente necesarios.** Identificar un conjunto mínimo de extractos y fuentes, con URL, fecha de adquisición y huella SHA-256, conservando las dependencias documentales de v2/v3/v4/v6. El catálogo de tablas no sustituye este inventario de entradas.
2. **Eliminar dependencias del equipo de origen.** El manifiesto `SOCHER_2026_v4/territorio/fuentes_manifest.csv` incluye rutas absolutas. Su tratamiento actual en `construir_eventos_relaciones.py` puede fallar al mover el proyecto. También debe parametrizarse la carpeta de exportación.
3. **Fijar el entorno y la ejecución completa.** Integrar reconstrucción, exportación y verificación en una secuencia documentada. Probarla desde un entorno nuevo con solo las entradas declaradas y registrar cualquier diferencia.
4. **Separar código y distribución de datos.** Git conservará scripts, documentación, diccionarios y registros de decisiones. El dataset se ofrecerá como un archivo de versión descargable o desde un archivo de investigación, vinculado mediante su huella. No hace falta versionar copias grandes de CSV, Excel y datos intermedios en cada cambio.
5. **Preparar la versión citable.** Una vez cerrada la muestra del artículo, publicar una versión identificada y archivarla con DOI. Documentar por separado las condiciones de reutilización del código y de las fuentes redistribuidas.

El CSV de 169,7 MB supera el límite de 100 MiB de archivos ordinarios de GitHub. GitHub documenta Git LFS y los archivos adjuntos a releases como alternativas. El Excel pesa 41,1 MB; no es necesario incluir ambas representaciones en el historial Git. Fuente: [GitHub, archivos grandes](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

GitHub también documenta el archivo de versiones públicas mediante Zenodo para obtener un DOI. Esa publicación debe corresponder a una versión concreta del análisis. Fuente: [GitHub, referencia y citación](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content).

## Validación que seguirá a esta base

Cada asignación centro–barra–evento deberá registrar: identificador del centro y fase, naturaleza del hito, fecha o intervalo acreditado, código de barra, vigencia del vínculo, fuente y página o sección, criterio de aceptación, incertidumbre y responsable de la revisión. Debe distinguir energización, entrada operacional, ampliación, traslado de suministro y primer consumo medido.

Las reglas para elegir tratamientos, comparadores, ventanas y exposición se documentarán antes de examinar los efectos estimados. Las correcciones posteriores conservarán el motivo y la versión anterior. La base actual permanecerá identificable mediante su manifiesto; validar un vínculo producirá una nueva versión.

## Registro de esta entrega

`controles/versiones/base_observada_2026-09-25.json` registra las huellas de scripts, tablas, documentación, controles y las dos entregas finales existentes. Permite detectar cambios respecto de este punto de partida. No contiene copias de los archivos, no sustituye una copia de seguridad y no acredita por sí solo validez causal ni reproducción en otro equipo.

Para el artículo, la descripción del proceso corresponde a la sección de datos y a un apéndice de reproducibilidad. El aporte sustantivo debe apoyarse en la pregunta económica, la identificación y los resultados que finalmente puedan defenderse.
