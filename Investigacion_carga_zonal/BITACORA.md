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


## 2026-10-11 · Conciliación Las Canteras y ODATA

Nueva solicitud del usuario: conciliar consumo físico y comercial, revisar conexiones y preparar la estimación zonal buscando indicios, sin modificar bases. Punto de partida: commit `f1e99a4`.

Antes de los nuevos coeficientes se guardó `PROTOCOLO_CONCILIACION_20261011.md`: fronteras, canales, pares comerciales, reglas de completitud, hipótesis horarias, nodos del corredor y cuatro diagnósticos carga/precio. Ejecución inicial: `20261011_conciliacion_v1`.

Resultados: 60 días comparables Canteras–SIP, error absoluto diario 0,44%; 18 días ST01–Lampa, 1,21%; un día ST02–Lo Espejo, 0,34%. Los casos Batuco/J9 y Panamericana012/CT no representan el mismo consumo en su ventana solapada. Se conservan todos los días, incluidos los discrepantes de junio de ST01.

La asociación Canteras carga–D fue positiva en los cuatro diagnósticos, sobre 25 meses en niveles. Se registró después `ADENDA_DIAGNOSTICOS_20261011.md` para examinar señal común del corredor, exclusión de meses y claves comerciales ST02. Esas pruebas son posteriores/exploratorias. Resultado: asociación casi igual en el corredor y una hipótesis de dos componentes comerciales que concuerda con CT1/CT2 los días 15/25 de julio. La alternativa no reemplaza los valores ambiguos originales.

Se revisó el plano J9–JT5 y la documentación de conexión/puesta en servicio. Se separó el hito de JT4 Lampa de la identificación pendiente del T5 ODATA. Se guardaron tabla de conexiones, fuentes y hashes. La figura descriptiva se inspeccionó visualmente; no presenta un efecto causal.

### Corrección interna de presentación de la tabla diaria

Pandas conservaba categorías de barras no seleccionadas al agrupar precios y generó filas vacías con cero observaciones. Todas estaban excluidas por la regla de elegibilidad; ninguna entró al panel mensual o regresiones. Se archivó el script v1 en `historial/conciliar_canteras_odata_v1.py` y se explicitó `observed=True` y una comprobación de barras permitidas. Nueva ejecución: **20261011_conciliacion_v2**, vigente.

Se preserva v1 completa. V2 reduce la tabla diaria de 1.199.095 a 10.271 filas observadas. Ocho tablas científicas son idénticas byte por byte, incluidos coeficientes, conciliación y panel; los precios diarios elegibles también son idénticos. Evidencia: `resultados/comparacion_conciliacion_v1_v2.json`. No cambió una base original ni una conclusión.

La ejecución principal verificó 33 insumos antes/después; el diagnóstico adicional, 11. La verificación previa de 271 insumos volvió a pasar. Se conservan la réplica, la versión v0.3.0 y las auditorías previas. No hubo descargas ni contactos externos.

## 2026-10-11 · Publicación de disponibilidad (CZ-012)

A petición explícita del usuario se incorpora la tabla íntegra de nueve recursos al README de GitHub, con fuentes y alcance local. Se publica el avance hasta a5275d5, sin reemplazar el cierre v0.3.0. La comprobación de preservación permite ahora únicamente README.md como excepción editorial fuera de la etapa; los archivos científicos siguen protegidos. Se archiva el comprobador anterior. No se modifican datos para esta publicación.
