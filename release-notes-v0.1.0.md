# v0.1.0 — Base observada

Versión de trabajo del dataset y del código de reconstrucción para la investigación **Entrada de centros de datos y diferenciales nodales de costo marginal: evidencia causal para Chile**.

## Contenido

- **178.016 observaciones de barra y hora**, con **66 variables**.
- **83 identidades históricas de barra**; no equivalen a 83 centros independientes.
- Diferenciales descriptivos respecto de **Quillota 110 y 220 kV**.
- **24 hitos documentados**, separados de la asignación de tratamientos.
- **67.384 registros de medición a intervalos de 15 minutos** de HT1, HT2 y HT3 de Las Canteras. La agregación principal utiliza HT1 y HT2; HT3 conserva su orientación pendiente.

Los precios integrados cubren **febrero, abril, mayo, junio y el 1–14 de julio de 2024**. Los períodos ausentes no se rellenan con ceros. Se conservan las identidades históricas, las marcas de revisión y los vínculos provisionales.

## Archivos de entrega

| Archivo | Contenido | Tamaño |
|---|---|---:|
| `Dataset_articulo.xlsx` | Panel completo, filtros y diccionario de 66 variables | 41.062.505 bytes |
| `Dataset_articulo.csv` | Mismo panel; UTF-8, coma como separador y punto decimal | 169.702.151 bytes |
| `diccionario_panel.csv` | Definiciones, tipos, unidades y conteos de nulos | 9.064 bytes |
| `verificacion_exportacion_excel_csv.json` | Resultado de la comprobación integral de las exportaciones | — |

Excel y CSV contienen **178.016 identificadores de observación únicos**. La comparación integral terminó sin errores; en Excel, la diferencia numérica máxima fue inferior a **6 × 10⁻¹⁴**, dentro de la tolerancia absoluta de **10⁻¹⁰**. Las 66 definiciones del diccionario coinciden con las de la fuente.

## Reproducibilidad comprobada

La reconstrucción desde los extractos incluidos se ejecutó satisfactoriamente en una carpeta independiente, con dependencias instaladas en un entorno virtual nuevo. Incluyó once pasos: seis de construcción y comprobación, revisión de insumos, contrato de doce tablas y tres de exportación. Se conservan los registros de instalación y ejecución, las versiones de todas las dependencias y las huellas de los programas y resultados.

Los archivos de esta entrega se regeneraron y verificaron con Python 3.13.15 en macOS ARM64. El CSV es idéntico byte por byte a la entrega original; el Excel tiene otra huella de contenedor y conserva el contenido dentro de la tolerancia declarada.

La [reconstrucción completa en GitHub Actions sobre Linux](https://github.com/a-cartes/datacenter/actions/runs/36204205401) también terminó sin errores y produjo un CSV idéntico. Los registros locales y remotos se conservan por separado. Estas pruebas no representan revisión por otro investigador ni una nueva descarga y extracción de todos los archivos nacionales originales.

La documentación incluye una adaptación de W3C PROV-DM, ocho etapas del proceso, diez decisiones con evidencia y un modelo formal propuesto de medición, ATT, adopción escalonada y exposición eléctrica.

## Estado de la investigación

Las fechas causales, los vínculos eléctricos vigentes, los comparadores y la exposición a otros proyectos siguen en validación. Los campos pendientes permanecen vacíos y ninguna fila se declara elegible para estimación causal. Una fecha prevista, una energización, una entrada formal y un cambio de retiro medido se conservan como hechos distintos.

Esta versión **no presenta estimaciones de ATT, DiD ni spillovers**. El título expresa el objetivo del artículo; la base observada todavía no acredita evidencia causal.

## SHA-256 de las exportaciones de esta entrega

```text
6d03fd48679aacc6efb71fac6172fd3c95faac45470bab497d9ad2b8c98eda02  Dataset_articulo.xlsx
1464b1e03084046250b80a854c99c6f45a2508b0d972f5222ed348e8c4070a47  Dataset_articulo.csv
```
