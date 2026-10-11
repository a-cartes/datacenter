# Consumo efectivo y exposición eléctrica zonal

**Inicio: 11 de octubre de 2026. Estado: disponibilidad auditada, conciliación de Las Canteras/ODATA realizada y panel exploratorio zonal preparado.**

Tenemos mediciones con las que avanzar hacia una exposición basada en carga y conexión. La prioridad es aprovecharlas y completar sus correspondencias históricas. Esta etapa preserva la réplica anterior y no reemplaza sus resultados por una nueva regresión.

## Avance de conciliación

- [Informe de conciliación, conexiones e indicios zonales](INFORME_CONCILIACION_20261011.md).
- [Protocolo previo a los nuevos resultados](PROTOCOLO_CONCILIACION_20261011.md) y [adenda exploratoria posterior](ADENDA_DIAGNOSTICOS_20261011.md).
- [Panel mensual preparado](resultados/20261011_conciliacion_v2/panel_zonal_mensual_exploratorio.csv).
- [Conexiones revisadas](CONEXIONES_CONCILIACION_20261011.csv) y [huellas de sus fuentes](FUENTES_CONEXIONES_20261011.csv).

## Documentos de trabajo

- [Informe: qué tenemos, qué falta y qué casos priorizar](INFORME_INICIAL.md).
- [Diseño de estimación zonal y reglas de medición](DISENO_ZONAL.md).
- [Bitácora de lo ejecutado](BITACORA.md).
- [Control de cambios](CONTROL_CAMBIOS.csv).
- [Reproducción y preservación de insumos](REPRODUCCION.md).
- [Resultados vigentes de la auditoría](resultados/20261011_inventario_v2/resumen_auditoria.json).
- [Cobertura por cliente y barra](resultados/20261011_inventario_v2/cobertura_retiros_cliente.csv).
- [Cobertura de los 30 puntos físicos candidatos](resultados/20261011_inventario_v2/cobertura_fisica_socket.csv).
- [Revisión de los 63 registros del inventario](resultados/20261011_inventario_v2/revision_63_registros.csv).

## Punto de partida preservado

El cierre anterior sigue en `SOCHER_2026_RM/`, versión **v0.3.0**, commit `cb61a5b87af5c5037890a71defe6f5af8c3b2cff`. La nueva etapa está en la rama `codex/carga-zonal-20261011`. Se añadieron archivos exclusivamente en esta carpeta; las bases históricas y el manuscrito se mantienen.

La auditoría vigente verificó nuevamente el SHA-256 de **271 insumos**, antes y después de procesarlos. Para los **653 originales, que suman 26,54 GB**, comprobó existencia y tamaño contra el inventario anterior: sus hashes se conservan, pero no se recalcularon esos 26,54 GB. La primera ejecución y su código se retienen en `resultados/20261011_inventario/` e `historial/`.

**Alcance de reproducibilidad:** los informes y resultados de esta auditoría están versionados. Su reproducción completa necesita los insumos locales de etapas anteriores y las tablas v7 recuperadas en Descargas; este directorio no es un paquete autónomo con todas esas bases. No se hicieron descargas ni contactos con terceros.

## Comparadores externos de Las Canteras

La [estimación zonal y revisión de cargas y red](INFORME_CONTROLES_ZONALES_20261011.md) añade controles fuera del corredor, una comparación fuera de la RM, retiros concurrentes y validación previa. Conserva ambas selecciones y todos los signos. Consulte el [protocolo](PROTOCOLO_CONTROLES_EXTERNOS_20261011.md) y la [adenda de controles distantes](ADENDA_CONTROLES_DISTANTES_20261011.md).

## Heterogeneidad horaria y prioridad Energy Economics

La [revisión horaria de Las Canteras](INFORME_HETEROGENEIDAD_HORARIA_20261011.md) distingue bloques de reloj, carga alta y restricciones operativas documentadas. Incluye18.168 horas, descomposición exacta de la asociación mensual, efectos fijos intradiarios, sensibilidad de reloj y subperíodos. Conserva el cierre SOCHER y las comparaciones anteriores. [Protocolo](PROTOCOLO_HORARIO_20261011.md).
