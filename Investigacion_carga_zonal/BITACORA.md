# Bitácora — nueva estrategia de carga zonal

## 2026-10-11 · Apertura y línea de base

Solicitud: revisar consumos efectivos y conexiones, identificar faltantes y plantear estimación zonal, preservando las bases anteriores y registrando cambios.

Se abrió la rama `codex/carga-zonal-20261011` desde `cb61a5b87af5c5037890a71defe6f5af8c3b2cff` (v0.3.0). El repositorio de publicación estaba limpio. El proyecto contenedor tenía cambios previos, registrados en `estado_inicial.json`; no se incluyeron en esta etapa. Commit del contenedor: `b58d8a94eb49f580792cbd73d45561f84d2c7547`.

Se conservó la tabla histórica de efectos como parte de la instantánea. No se cambiaron cohortes, controles, fechas, resultados o texto SOCHER.

## Ejecución 1 · Inventario local

Se leyeron catálogos, panel comercial, pilotos, documentación, inventario de instalaciones y topología. Resultado: `resultados/20261011_inventario/`, 265 insumos con SHA-256 idéntico antes/después; 653 originales con existencia/tamaño comprobados. Se reprodujo el agregado de Panamericana.

La tabla inicial de cifras históricas se serializó con `NaN` para algunas celdas vacías. Esa primera salida se conserva intacta como registro: `NaN` no representa un resultado nuevo ni cero. Se corrigió el serializador de la ejecución siguiente para generar JSON estándar con `null`. El script inicial se conserva en `historial/auditar_disponibilidad_v1.py`.

## Ejecución 2 · Tablas físicas recuperadas y conciliadas

Los informes v7 documentaban mediciones no presentes como tablas en el checkout público. La búsqueda local las encontró en Descargas, carpeta `Medidas Transferencias económicas-selected/SOCHER_2026_v7_2020_2026/mediciones` (el nombre físico usa acento Unicode descompuesto). No se trasladaron ni modificaron.

Se verificaron las cinco tablas Parquet contra las huellas y tamaños del informe v7. Se amplió la auditoría a 271 insumos y se conservaron todos sin cambio. Se recalculó HT1+HT2 desde los registros de 15 minutos, coincidiendo con 21.912 horas del agregado archivado; se generó cobertura por socket/mes y la trayectoria mensual.

Resultado vigente: `resultados/20261011_inventario_v2/`. Se distinguen datos físicos, retiros comerciales muestreados, capacidades y previsiones. La revisión de los 63 registros es una matriz de disponibilidad: las pistas por operador quedan marcadas como candidatas, no como enlace certificado por edificio.

## Cierre de esta revisión

Se entregan informe, propuesta de diseño, tabla de cambios y mecanismo de verificación de preservación. No se descargaron nuevas bases, no se contactó a nadie y no se estimó un nuevo coeficiente de precios. El crecimiento observado de carga en equipos seleccionados se informa como dato para la siguiente etapa.

La prioridad pasa a la conciliación de conexiones/etapas y fronteras, empezando por Las Canteras y ODATA. Se mantiene abierto el análisis causal, con reglas que permitan distinguir crecimiento neto, transferencia de suministro y exposición compartida.

## Regla para próximas entradas

Cada entrada indicará fecha, pregunta, insumos con hash, transformación, carpeta de salida nueva, comprobaciones, hallazgo y cambio respecto de la decisión anterior. Los intentos fallidos se conservan o documentan; nunca se presenta una ejecución revisada como si fuera la original.
