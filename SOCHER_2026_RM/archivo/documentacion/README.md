# Réplica sobre centros de datos y precios eléctricos en la Región Metropolitana

Réplica adaptada de Mamkhezri, Sun y Yang, *The Hidden Cost of the Cloud: Data Centers and Transmission-Induced Electricity Prices* (marzo de 2026, SSRN 5736562). La prioridad acordada el 1 de octubre de 2026 es construir primero la réplica base y evaluar después las extensiones para Chile. Las investigaciones anteriores del directorio no se usan como insumo analítico. Solo se reutilizaron archivos **originales** del Coordinador descargados por el usuario, verificados por hash o ETag (ver REGISTRO_DECISIONES.md, D-03 y D-05).

## Estado al 2 de octubre de 2026

**Orientación actual solicitada:** conservar la réplica histórica, comparar Virginia con la RM y evaluar escenarios hacia 2030. El [diseño comparado y prospectivo](DISENO_COMPARADO_Y_ESCENARIOS_2030.md) define la pregunta, el contrafactual y los entregables. Es una propuesta de trabajo; las simulaciones aún no están estimadas.

**Lea primero la [auditoría de datos y estimación](AUDITORIA_REPLICA.md), posterior al [informe de avance](INFORME_AVANCE.md).** La auditoría reproduce los cálculos, pero identifica una atribución incorrecta del p de permutaciones, nueva evidencia sobre la inauguración de ST01 en 2022 y diferencias entre la agregación principal y el artículo. La réplica continúa en revisión; las estimaciones anteriores se conservan para trazabilidad. El informe anterior resumía:

- La medida eléctrica quedó validada, con una descomposición exacta de D = P − P_Quillota en pérdidas y desacople.
- El panel de precios 2017–2025 está completo y la continuidad entre regímenes fue verificada.
- El inventario reúne 63 instalaciones y 138 hitos con fuentes primarias.
- La réplica se estimó, pero con 2 a 4 tratamientos independientes según la unidad. Las estimaciones no son robustas y no admiten interpretación causal.

## Documentos

| Documento | Contenido |
|---|---|
| [DISENO_COMPARADO_Y_ESCENARIOS_2030.md](DISENO_COMPARADO_Y_ESCENARIOS_2030.md) | Réplica histórica, comparación Virginia y RM, y evaluación prospectiva orientada a Energy Economics |
| [AUDITORIA_REPLICA.md](AUDITORIA_REPLICA.md) | Pruebas ejecutadas, errores de presentación, nuevas fuentes de fechas y diferencias con el original |
| [INFORME_AVANCE.md](INFORME_AVANCE.md) | Qué está verificado, qué es provisional y qué está pendiente |
| [REGISTRO_DECISIONES.md](REGISTRO_DECISIONES.md) | Decisiones fechadas, alternativas y momento respecto de los resultados |
| [VALIDACION_MEDIDA.md](VALIDACION_MEDIDA.md) | Piloto de conciliación, descomposición, versiones, continuidad y cambios de nombre |
| [INVENTARIO_INSTALACIONES.md](INVENTARIO_INSTALACIONES.md) | Inventario histórico, primeras entradas y conexiones documentadas |
| [UNIDADES_Y_PERIODO.md](UNIDADES_Y_PERIODO.md) | Comparación de unidades, período y exposición por la red |
| [PANEL_Y_VIABILIDAD.md](PANEL_Y_VIABILIDAD.md) | Construcción del panel, covariables, soporte y viabilidad |
| [RESULTADOS_REPLICA.md](RESULTADOS_REPLICA.md) | Estimaciones, estudio de eventos, sensibilidad e interpretación |
| [REPRODUCCION.md](REPRODUCCION.md) | Requisitos, orden de ejecución y estructura de carpetas |
| [PROTOCOLO_REPLICA.md](PROTOCOLO_REPLICA.md), [FICHA_ARTICULO.md](FICHA_ARTICULO.md) | Diseño y ficha del original (1 de octubre) |
| [DATOS_Y_DECISIONES.md](DATOS_Y_DECISIONES.md), [DISPONIBILIDAD_CHILE.md](DISPONIBILIDAD_CHILE.md), [COMPARABILIDAD_PRECIOS.md](COMPARABILIDAD_PRECIOS.md), [FUENTES_OPERACION.md](FUENTES_OPERACION.md), [GEOGRAFIA_Y_COVARIABLES.md](GEOGRAFIA_Y_COVARIABLES.md) | Revisión inicial de fuentes (1 de octubre); se conservan como antecedentes |

## Carpetas

- `fuentes/` contiene los originales: precios, Infotécnica, SEA, SNIFA, cartas, páginas web, directorios y cartografía INE. Se guardan con hash y procedencia.
- `datos/` contiene los derivados: precios extraídos, diccionario de barras, panel, instalaciones, unidades, covariables y muestras analíticas.
- `scripts/` contiene los programas; `scripts/ejecutar_todo.sh` reproduce el procesamiento.
- `resultados/` contiene diagnósticos JSON, estimaciones y figuras. `logs/` guarda las ejecuciones.


## Cierre analítico del 9 de octubre de 2026

Versión actual del resumen: `entregables/socher_2026/Resumen_extendido_SOCHER_2026_revision_20261009.docx`. Resultados preliminares cerrados para presentación; sin atribución causal robusta ni simulación contrafactual de precios 2030.

El diagnóstico, los contrastes, las matrices de correspondencia con Virginia y de conexiones/potencias están en `resultados/cierre_socher_20261009/`. Comenzar por `INFORME_CIERRE.txt`. Las bases y los documentos previos se conservan; el documento fechado el 9 de octubre incorpora las correcciones de interpretación de Lampa y controles.
