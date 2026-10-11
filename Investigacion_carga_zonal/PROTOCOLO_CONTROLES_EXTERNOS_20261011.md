# Protocolo de controles externos y cargas concurrentes

11 de octubre de 2026. Revisión exploratoria solicitada después de conocer la asociación positiva de carga y diferencial en Las Canteras y su corredor. No es un prerregistro independiente del conocimiento anterior. Punto de partida publicado: 779b97c.

## Pregunta y resultados

¿El diferencial del corredor respecto de comparadores externos aumenta al crecer el retiro medido en HT1+HT2, y persiste al considerar otras cargas y cambios de red?

Resultado zonal principal: media igual de BATUCO_110, TLIBERTADORES_110 y C.NAVIA_110, composición fijada en la conciliación anterior. Resultado secundario: CANTERAS_110 desde agosto de 2024. Referencia histórica D=P−Quillota220; al restar un comparador común Quillota se cancela exactamente. No se cambia el cierre SOCHER ni se considera cada barra como una intervención independiente.

## Comparadores antes de calcular nuevos coeficientes

Universo: barras de 110 kV en Metropolitana, Valparaíso y O'Higgins–Maule, con enlace de subestación por nemotécnico de homologación. Excluir nodos directos o del mismo corredor de cualquier DC del inventario (unión de mapas documentado y conservador), y nodos con retiros DC observados. Excluir referencia, nodos sin ubicación y duplicados por subestación. Esta exclusión amplia usa conocimiento posterior para evitar controles contaminados, no constituye prueba de ausencia de influencia eléctrica. Registrar candidatos rechazados.

Exigir 24 meses previos elegibles (mayo2022–abril2024) y cobertura mensual posterior hasta agosto2026 para mantener composición. Ordenar por RMSE de las trayectorias de D centradas en su propia media durante los primeros 12 meses previos (mayo2022–abril2023). Elegir los primeros cinco; sensibilidad diez. Pesos iguales, sin optimizar sobre resultados posteriores. Los siguientes 12 meses quedan para validar sesgo y RMSE frente al ajuste de nivel del entrenamiento; una mala validación se informa, no se corrige buscando otro grupo. La cobertura posterior puede generar selección de supervivencia: se declara.

## Dos ejercicios separados

1. Contraste histórico del corredor: brecha frente a controles menos su media previa, antes mayo2022–abril2024 y después junio2024–agosto2026; mayo es transición excluida. Presentar también sin julio2024, cambio de fuente ya conocido, y placebo previo: validación menos entrenamiento. Es una comparación de la expansión conjunta de carga/red, no una entrada exclusiva exógena.
2. Intensidad: agosto2024–agosto2026, régimen moderno de precios, días de 24 horas completos comunes a todos los nodos y HT1+HT2; mínimo20 días por mes. Estimar brecha zonal y de Canteras sobre MW medios físicos en niveles, con tendencia lineal, primeras diferencias y diferencias de12meses. Comparar K5/K10 y nodos individualmente. No tratar 600 horas como600 episodios independientes.

## Cargas y red

Examinar retiros SIP diarios completos no ambiguos de Google en Libertadores y Ascenty en Chacabuco013 y023. Mantener los tres puntos separados; no sumar puntos ambiguos ni extrapolar días a meses. Estimar sobre días muestreados comunes (con medias físicas y precios del mismo día): niveles con calendario mensual fijo y sin él, incorporando Google y ambos puntos Ascenty. La muestra es selectiva y sus retiros son estimaciones comerciales contrastadas parcialmente; faltan otros consumos zonales no DC. Incluir tendencia en alternativa, reportar rango y colinealidad. No reemplaza una medición de demanda zonal total.

Identificar obras entre2024y2026 del inventario, aristas fechadas y fichas técnicas. Fechas de autorización, PES y EO quedan separadas. Diagnóstico mensual de intensidad con indicadores desde junio2025 (BatucoHT4), agosto2025 (LampaJT4) y febrero2026 (LampaJT6); sensibilidad excluyendo meses que contienen la entrada. Los indicadores describen cambios concurrentes; las obras pueden responder a la demanda y controlarlas cambia el objeto económico, por lo que no son automáticamente controles exógenos.

## Inferencia y trazabilidad

Regresiones de intensidad: informar coeficientes, N temporal, rango de matriz y dispersión residual. Errores HAC de3 rezagos mensuales o3 fechas muestreadas, intervalos normales95% solo como diagnóstico condicional; no usar significancia para seleccionar resultados ni denominar esos intervalos evidencia causal. Conservar todos los resultados, incluidos signos contrarios. Sin aleatorización documentada, no inventar p de aleatorización.

Nueva carpeta de resultados, manifiesto SHA256 antes/después, código, selección y rechazos íntegros, fechas y limitaciones de las fuentes. No sobrescribir bases, protocolos anteriores ni resultados. Inspeccionar la calidad del grupo seleccionado antes de inferir una historia causal.
