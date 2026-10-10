# Centros de datos y costos marginales eléctricos en la Región Metropolitana

Repositorio de datos, código y evidencia del estudio **¿Dónde se conecta la inteligencia artificial? Centros de datos y costos marginales eléctricos en la Región Metropolitana ante el horizonte 2030**.

La versión vigente es el **cierre analítico para SOCHER 2026**, con precios 2017–2025, inventario trazable y documentación eléctrica por etapa. Establece una línea de base ante la expansión digital: **no demuestra un incremento causal robusto de precios ni contiene una simulación contrafactual de 2030**.

[Reproducir el cierre](SOCHER_2026_RM/README.md) · [Manuscrito](SOCHER_2026_RM/manuscrito/Resumen_extendido_Alan_Cartes.pdf) · [Método](SOCHER_2026_RM/documentacion/METODO.md) · [Mapa de resultados](SOCHER_2026_RM/documentacion/MAPA_RESULTADOS.md) · [Historia y decisiones](SOCHER_2026_RM/documentacion/TRAZABILIDAD.md)

## Resultados de esta versión

| Resultado | Valor o alcance |
|---|---|
| Inventario | 63 registros de instalaciones o etapas, 138 hitos, 65 fuentes |
| Muestra principal | 3 distritos tratados, 18 controles, 189 observaciones distrito-año |
| Estimación histórica principal | 1,05263 USD/MWh; sensible a Lampa y a la evolución previa de los controles |
| Misma muestra con fecha anterior de Lampa | 1,01514 USD/MWh |
| Exclusión de Lampa | 0,03273 USD/MWh |
| Contraste descriptivo con todo el período previo | −0,08663 USD/MWh |
| Diagnóstico de conexiones | Apertura, conexión y utilización de capacidad son hitos distintos |
| Escala 2030 | 5,455728–9,09288 TWh/año bajo supuestos explícitos; sensibilidad, no impacto de precios estimado |

La [nota metodológica](SOCHER_2026_RM/documentacion/METODO.md) explica las dos ponderaciones, los intervalos convencionales, el test previo singular y los límites de comparación con Virginia. La [Tabla 1 reproducida](SOCHER_2026_RM/evidencia/tabla_1.csv) conserva la sensibilidad a fechas y exclusión de Lampa.

![Lampa y sus controles](SOCHER_2026_RM/evidencia/figura_1.png)

## Ejecutar el análisis

Desde una copia de este repositorio, con Python 3.13 y R disponibles:

```bash
python3 -m venv .venv-socher
source .venv-socher/bin/activate
python -m pip install -r SOCHER_2026_RM/requirements-lock.txt
Rscript SOCHER_2026_RM/scripts/instalar_R.R
python SOCHER_2026_RM/scripts/reproducir.py
```

El programa comprueba hashes, reconstruye muestras y emparejamiento, ejecuta las regresiones, regenera la figura y contrasta los resultados con referencias congeladas. Publica un informe verificable en `SOCHER_2026_RM/salidas/reproduccion/verificacion.json`. No requiere credenciales ni conexión a internet después de instalar dependencias. Se conservan los [resultados de la verificación local](SOCHER_2026_RM/evidencia/verificacion_local.json) y existe un [flujo de comprobación en GitHub Actions](.github/workflows/socher-rm.yml).

La reproducción comienza en **paneles derivados**, no en una nueva descarga de todos los originales. La [guía de fuentes](SOCHER_2026_RM/documentacion/FUENTES_Y_RECONSTRUCCION.md) detalla lo incluido, los manifiestos, los programas de extracción y las tareas manuales necesarias para ese alcance adicional.

## El trabajo detrás de los resultados

```mermaid
flowchart LR
    A[Originales y manifiestos] --> B[Extracción y continuidad de precios]
    B --> C[Barra y subestación a distrito]
    D[Inventario y hitos documentados] --> E[Historia de exposición]
    C --> F[Panel y covariables]
    E --> G[Emparejamiento y estimación]
    F --> G
    G --> H[Auditoría Lampa y controles]
    H --> I[Tabla y figura SOCHER]
```

- [Decisiones fechadas y revisiones posteriores](SOCHER_2026_RM/archivo/documentacion/REGISTRO_DECISIONES.md).
- [Validación de la medida eléctrica y cambios de publicación](SOCHER_2026_RM/archivo/documentacion/VALIDACION_MEDIDA.md).
- [Inventario de instalaciones y fuentes](SOCHER_2026_RM/datos/instalaciones/instalaciones.csv).
- [Matriz de conexiones y potencia](SOCHER_2026_RM/referencia/cierre_socher_20261009/matriz_conexiones_potencias.csv).
- [Diagnóstico de Lampa y de los controles](SOCHER_2026_RM/referencia/cierre_socher_20261009/INFORME_CIERRE.txt).
- [Comparabilidad del diseño con Virginia](SOCHER_2026_RM/referencia/cierre_socher_20261009/correspondencia_virginia.csv).
- [Bases PET26 y viabilidad de la siguiente etapa](SOCHER_2026_RM/archivo/prospectiva_documentacion/INFORME_VIABILIDAD.md).

## Investigación anterior y siguientes etapas

Las carpetas `SOCHER_2026_dataset` y v2–v8 se conservan como antecedentes. La [portada histórica de v8](README_historico_v8.md) documenta aquella etapa 2020–2026; no es el estado vigente del resumen RM. Las versiones publicadas v0.1.0 y v0.2.0 mantienen sus archivos. No se reescribe el historial ni se mezclan automáticamente sus muestras con el cierre 2017–2025.

La [hoja de ruta](ROADMAP.md) separa esta línea de base de la simulación de red pendiente y de la futura evaluación causal con retiros medidos por instalación. Este repositorio no acredita aceptación en SOCHER ni publicación en una revista.

## Autoría y citación

**Alan Cartes Fica, Ricardo Troncoso y Rodrigo Romo — Universidad del Bío-Bío, Chile.** Correspondencia: alancartes@outlook.com.

Use [CITATION.cff](CITATION.cff), identifique la versión o el commit consultado y cite las fuentes primarias correspondientes. El [registro de cambios](CHANGELOG.md) permite distinguir entregas. Las [condiciones de reutilización](REUSE.md) distinguen el trabajo propio de las fuentes de terceros.
