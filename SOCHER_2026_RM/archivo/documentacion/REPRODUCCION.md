# Reproducción

## Requisitos

- Python 3.13 (Anaconda) con un entorno propio en `.venv` (`python3 -m venv --system-site-packages .venv`), que añade `pypdf`, `shapely` y `pyproj`. Se usan pandas, numpy, pyarrow, openpyxl, statsmodels y requests.
- R 4.x con `fixest`, `data.table` y `jsonlite`.
- `bsdtar` (libarchive), para leer el RAR de septiembre de 2017.

## Etapa A: adquisición (requiere red)

| Paso | Programa | Nota |
|---|---|---|
| Libros históricos 2017-01 a 2024-07 | `registrar_originales_historicos.py` | Crea enlaces duros desde las descargas manuales del usuario (`~/Downloads`), sin copiar bytes. Registra SHA-256 en `fuentes/precios/manifiesto_originales_historicos.csv`. Si se borran las carpetas de origen, los enlaces conservan los datos |
| Régimen nuevo 2024-07 a 2025-12 | `descargar_cmg_moderno.py verificar <copia> AAAA-MM` o `descargar AAAA-MM` | S3 público del Coordinador. Verificación byte a byte por ETag multiparte (`.json` por mes) |
| Infotécnica | `descargar_infotecnica.py` | API pública |
| SEA | `consultar_sea.py`, `fichas_sea.py` | — |
| Cartas CEN | `consultar_cartas_coordinador.py` | — |
| SNIFA | consultas guardadas en `fuentes/instalaciones/snifa/` | — |
| Directorios y web | `candidatos_directorios.py`, `archivar_web.py URL` | Registro en `fuentes/instalaciones/web/registro.csv` |
| Censo 2017 | `descargar_censo2017_ine.py` | Servicios ArcGIS del INE |

El portal www.coordinador.cl bloquea las descargas automatizadas (Cloudflare). Los libros históricos y los paquetes diarios de factores posteriores a julio de 2024 requieren descarga manual.

## Etapa B: procesamiento y estimación

```
zsh scripts/ejecutar_todo.sh
```

Duración aproximada: 30 minutos. Se ejecuta, en orden, la inspección de las muestras, el piloto, la extracción histórica y moderna, el diccionario de barras, la geolocalización, los hitos, el registro de fuentes, el panel, la continuidad, el diagnóstico de unidades, las covariables, las muestras emparejadas, las nueve estimaciones y el resumen. La geocodificación usa la caché de `fuentes/instalaciones/geocodificacion/`.

## Datos curados a mano

`datos/instalaciones/instalaciones.csv` es la fuente curada del inventario. Cada fila cita fuentes registradas en `fuentes_instalaciones.csv`. Cualquier corrección debe hacerse allí y propagarse con `ejecutar_todo.sh`.
