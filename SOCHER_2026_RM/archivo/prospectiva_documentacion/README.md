# Prospectiva 2030: insumos para la simulación con restricciones de transmisión

Carpeta creada el 5 de octubre de 2026. Reúne los insumos para comparar 2030 con y sin expansión adicional de centros de datos. No contiene estimaciones de efectos y no modifica nada fuera de esta carpeta.

Leer primero: `INFORME_VIABILIDAD.md` (qué se puede hacer y qué falta) e `INDICE_VARIABLES.md` (qué archivo aporta cada variable).

**Pendiente principal:** los dos ZIP del Anexo VII del Coordinador no se pudieron descargar de forma automática. Descárguelos con el navegador y ejecute `python scripts/ingresar_bases_pet26.py`.

## Estructura

| Ruta | Contenido |
|---|---|
| `fuentes/lista_fuentes.csv` | Lista de fuentes con URL y versión |
| `fuentes/registro_fuentes.csv` | Registro de descarga: estado, bytes, SHA-256, Last-Modified y ETag del servidor, fecha de consulta |
| `fuentes/originales/` | Archivos originales sin modificar. `infotecnica/manifiesto.json` resume las 6.671 fichas de la API |
| `fuentes/paginas/` | Páginas de la CNE consultadas |
| `extraidos/` | Insumos en CSV y Parquet, y texto de los PDF en `extraidos/texto/` |
| `scripts/` | Programas de descarga y extracción |
| `logs/` | Salidas de ejecución y respuestas de la API de la CNE |

## Reproducción

Con el entorno del proyecto (`../.venv`):

```
python scripts/descargar_fuentes.py              # descarga lo pendiente de la lista y actualiza el registro
python scripts/extraer_cne_pncp.py               # costos marginales, energía y cuadros del informe CNE
python scripts/extraer_cne_prevision_demanda.py  # previsión de demanda por cliente y punto de conexión
python scripts/construir_demanda_digital.py      # carga digital incluida en la base CNE
python scripts/descargar_infotecnica_red.py      # red y unidades existentes (usa caché local)
python scripts/ingresar_bases_pet26.py           # registra e inventaría los ZIP del Anexo VII, una vez descargados
```

`extraidos/demanda_digital/proyectos_digitales_etapas.csv` y `extraidos/obras/obras_criticas_rm.csv` son tablas curadas a mano; cada fila cita su fuente y el pasaje de respaldo.
