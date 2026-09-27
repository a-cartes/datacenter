# Precios históricos de Batuco: disponibilidad, todavía sin asignación causal

La selección v0.2.0 y el panel v8 no incluyen Batuco. Se inspeccionaron los originales históricos ya archivados y se verificó su disponibilidad como una capa nueva, sin modificar esa entrega ni calcular efectos.

Los siete libros definitivos de abril a octubre de 2022 contienen `BATUCO________013` y `BATUCO________110`, además de `QUILLOTA______110` y `QUILLOTA______220`. La revisión conserva 856 filas de soporte barra–día. En la ventana condicional de operación declarada de ODATA hay **105 días previos y 90 posteriores con idéntico conjunto de 24 etiquetas en las cuatro series**. Esto acredita presencia de celdas de precio y soporte horario publicado; no identifica una barra física ni una intervención.

| Ventana condicional | Fechas | Días con soporte común |
|---|---|---:|
| Previa, −112 a −8 desde g | 12 abril–25 julio de 2022 | 105 |
| Posterior, 0 a 89 desde g | 2 agosto–30 octubre de 2022 | 90 |

La convención `g=2 de agosto` solo prepara el calendario posterior al día operacional declarado por el titular. No certifica que ese día comience la demanda ni que los siete días excluidos absorban todas las pruebas. Los libros mantienen etiquetas 1–25 sin conversión UTC. Las fechas fuera de la ventana siguen en el archivo de soporte.

**Falta el puente de identidad.** No se dispone de homologación mensual de estos libros de 2022. La etiqueta de 13 kV no representa automáticamente la BP3 de 23 kV que figura en el plano candidato. El precio de 110 kV podría ser un resultado aguas arriba si se acredita el recorrido de suministro y la barra histórica, pero no se asigna usando el código InfoTécnica actual. Lampa no sustituye a Batuco por proximidad o pertenecer al mismo campus.

`verificar_soporte.py` lee OOXML sin ejecutar macros y no calcula medias, diferencias ni coeficientes. `verificacion_soporte.json` conserva las huellas de siete libros y los conteos por serie; `validacion_pares_comunes.json` verifica independientemente la igualdad de conjuntos de etiquetas por fecha. `soporte_diario_etiquetas.csv` permite repetir esa comparación sin abrir magnitudes de precios. La lectura de magnitudes y ampliación del panel quedan para una adenda posterior al cierre del evento y su ruta.

Reproducción: ejecutar `verificar_soporte.py --datos-raiz <carpeta con SOCHER_2026_v7_2020_2026>` con Python estándar. Requiere los siete libros originales preservados, no incluidos de nuevo en esta carpeta.
