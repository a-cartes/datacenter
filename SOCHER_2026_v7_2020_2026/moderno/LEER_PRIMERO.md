# Precios publicados bajo el régimen CMg Real desde el 15 de julio de 2024

Este módulo preserva los TSV mensuales oficiales, selecciona barras candidatas y construye precios por intervalo de 15 minutos y por hora. El conjunto temporal solicitado es julio de 2024 a septiembre de 2026, con corte del estudio el **27 de septiembre de 2026**. La cobertura efectiva se calcula leyendo cada fuente; no se rellena el resto del mes.

## Fuente pública validada

El [portal de Costos Marginales del Coordinador](https://www.coordinador.cl/costos-marginales/) ofrece la descarga mensual y distingue E (en línea), P (preliminar) y R (real definitivo). Su botón «Costo Marginal Real» implementa, en el JavaScript público `temporal.js?v=2.0`, esta ruta:

```text
https://cen-datalake-public.s3.amazonaws.com/costos_marginales/CMG_REAL/{año}/{mes}/{año}_{mes:02}_REAL-DEF.tsv
```

Para preliminares el sufijo es `REAL-PRE.tsv`. El directorio usa el mes sin cero inicial y el archivo lo usa con dos dígitos. Los enlaces mensuales se validaron con HTTP HEAD antes de descargar; las muestras HTTP Range están identificadas como fragmentos y nunca se confunden con fuentes completas. La descarga no usa API key ni requiere acceso a cuentas.

El canal diario de antecedentes y sus ZIP constituyen otra vía oficial; no se mezclan indiscriminadamente con los TSV. El libro histórico de costos hasta el 14 de julio de 2024 y el CMg Real posterior conservan regímenes y procedencias diferentes.

## Datos y separación de versiones

El TSV proporciona `ID_INFO`, `BARRA_INFO`, `BARRA_TRANSF`, `FECHA`, `HRA`, `MIN`, los dos precios y `VERSION`. Las fuentes más recientes rotulan los precios `CMg[USD/MWh]` y `CMg[CLP/KWh]`; julio de 2024 utiliza `CMg[mills/kWh]` y `CMg[$/KWh]`. El lector reconoce esos alias explícitos, conserva el encabezado original y registra factor numérico 1: mills/kWh es numéricamente equivalente a USD/MWh. El precio en pesos se interpreta en el contexto de valorización en pesos chilenos que explica el portal del Coordinador.

- Se conserva `ID_INFO` como identificador publicado. **No se transforma en un nemotécnico histórico** ni se le asigna automáticamente un centro de datos.
- Se conserva la resolución original de **15 minutos**. Las horas resultan de la media aritmética de cuatro precios, únicamente cuando están presentes los minutos 0, 15, 30 y 45. La media observada y la bandera de completitud permanecen disponibles para horas incompletas; el precio horario completo queda vacío en esos casos.
- La completitud de una hora observada no acredita un panel balanceado. Una hora totalmente ausente no genera una fila: las coberturas diaria y mensual permiten detectar esos vacíos, las incorporaciones de etiquetas y los extremos parciales del período.
- `HRA` y `MIN` se conservan según la fuente. El lector admite `HRA=24` si está publicada, sin eliminarla, cambiarla de fecha ni forzarla a UTC. No supone cómo representa el archivo los cambios de hora. El enlace con las etiquetas del período histórico y con mediciones eléctricas exige conciliar la convención temporal.
- `REAL-DEF` y `REAL-PRE` se almacenan en particiones separadas. El preliminar de septiembre permite documentar un alcance temporal distinto, pero no reemplaza silenciosamente la versión definitiva.
- Una marca `[NO_MOSTRAR]` o `[EN_REVISION]` permanece visible. Identidad publicada no equivale a elegibilidad analítica.
- Un precio de cero es un dato publicado; una barra o fecha ausente no se convierte en cero.

Como control observado, el TSV de abril de 2025 contiene para **2025-04-05** las 25 etiquetas `HRA=0…24`. Esa etiqueta 24 permanece en la fecha publicada; no se reubica como una hora del día siguiente. El reporte diario conserva el número de etiquetas por fecha para detectar estas situaciones antes de cruzar con otras fuentes.

## Selección de barras

`config/seleccion_barras_v6.csv` es una copia exacta del inventario previo, con su hash y procedencia. La extracción distingue tres criterios:

1. Etiqueta literal presente en v6.
2. Otro nivel de tensión publicado dentro de una familia de etiquetas previamente seleccionada.
3. Búsqueda candidata adicional por nombre físico o etiqueta para Nueva Lampa, Santa Teresa, ODATA, Lo Campino, Punta Verde, Pudahuel, Colina, Curauma y Quilicura.

Estos criterios amplían la **capa de precios**. No homologan instalaciones retrospectivamente ni acreditan relación centro–barra. Las filas con ID o nombre vacío quedan como candidatos sin identidad completa. También se consideran marcadores sin identidad válida el ID «0» y los nombres «-», «nan», «null» o «none»; se conservan sus valores literales y sus precios. Se genera además el catálogo nacional mensual de nombres y códigos, de modo que posteriores cambios justificados en la selección puedan reproducirse desde las fuentes preservadas.

La muestra definitiva de septiembre de 2026 contiene, entre otras, `NVALAMPA______220` (ID 3231), `PANAMERICANA__110` (ID 868), `PUDAHUEL______013` (ID 875, nombre físico 12 kV), `PUDAHUEL______110` (ID 873, marcado NO_MOSTRAR), y Canteras 110/23 (ID 3969/3972). Padre Hurtado110 y Tap Quilicura110 tienen precios publicados con ID/nombre incompletos; no se convierten en barras plenamente identificadas.

## Reproducción

Dependencias: Python, pandas, numpy y pyarrow. El módulo usa bibliotecas estándar para la descarga. Los originales TSV se comprimen localmente en gzip sin alterar su contenido; el manifiesto conserva SHA256 tanto del TSV recibido como del gzip local, ETag, tamaño, cabeceras y momento de consulta. El ETag multipart de S3 **no se presenta como MD5 del contenido**. `If-Match` exige consistencia del objeto durante la descarga.

Ejemplo de descarga y extracción, ejecutadas por separado:

```text
python scripts/descargar_extraer_moderno.py --months 2025-06 2026-09 --include-pre-septiembre --phase download
python scripts/descargar_extraer_moderno.py --months 2025-06 2026-09 --include-pre-septiembre --phase extract
```

Cada archivo se guarda como `{AAAAMM}_{DEF|PRE}_{15min|horario}.parquet` y `.csv.gz`. Los catálogos, coberturas y metadatos usan el mismo prefijo. Los meses ya preservados se verifican antes de reutilizarse. Si existe un manifiesto preservado pero el archivo remoto cambió, el código detiene la reproducción en lugar de sustituir silenciosamente la versión histórica.

Para GitHub se deben versionar el código propio, la selección, los manifiestos y la documentación. Los TSV nacionales comprimidos son archivos de trabajo voluminosos que deben conservarse fuera de Git ordinario. Las páginas y los scripts públicos de descubrimiento se conservan localmente como evidencia, pero no son dependencias necesarias del programa ni contienen instrucciones que este ejecute. La reproducción exacta futura depende de conservar el archivo original o de que el proveedor siga publicando la misma versión y hash.

## Control de cobertura

`fuentes/indice_tsv_moderno.json` registra la comprobación inicial de disponibilidad y tamaño. Los archivos `fuentes/metadatos/*_extraccion.json` son la evidencia de **fechas efectivamente leídas**, tamaños de panel, resolución, versiones y anomalías. No interpretar el nombre «septiembre» ni el Last-Modified del archivo como cobertura de todo septiembre. La versión definitiva de ese mes, leída íntegramente durante esta ejecución, llega al **18 de septiembre de 2026**.

La fuente preliminar de septiembre llega al **24 de septiembre de 2026, HRA 0 y MIN 45**: publica solamente cuatro intervalos de ese último día. No equivale a tener el día 24 completo. El definitivo llega al **18 de septiembre, HRA 23 y MIN 45**. Los dos archivos se conservan; el verificador compara el solape y registra las revisiones sin sustituir versiones.
