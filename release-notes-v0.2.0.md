# v0.2.0 — Precios nodales 2020–2026

La ampliación reúne **3.411.527 observaciones y 31 variables** de precios nodales y diferenciales descriptivos. Cubre desde el **1 de enero de 2020 hasta el 18 de septiembre de 2026**, corte efectivo de los definitivos consultados el 27 de septiembre. No representa todo el año 2026 ni un panel balanceado.

Se integran 55 particiones del régimen histórico y 27 del moderno: 81 meses calendario, con julio de 2024 dividido en dos regímenes. Los precios PRE de septiembre se conservan aparte. Los 178.016 precios de la versión anterior coinciden exactamente con la nueva extracción; v0.1.0 permanece disponible.

## Archivos

| Archivo | Contenido |
|---|---|
| `Dataset_precios_barra_hora_2020_2026.csv.gz` | CSV completo comprimido; descomprimir antes de importar. |
| `CSV_por_anio_2020_2026.zip` | Siete CSV anuales, diccionario, fuentes, cobertura y faltantes. |
| `Dataset_precios_barra_hora_2020_2026.parquet` | Copia tipada y comprimida del panel de precios. |
| `Capas_complementarias_2020_2026.zip` | Cuatro capas horarias de mediciones, 1.862.581 registros de 15 minutos en CSV comprimido y precios PRE separados. |
| `Insumos_reproduccion_2020_2026.zip` | Particiones extraídas y metadatos para reconstrucción exacta. |
| `Diccionario_precios.csv` | Definición de las 31 variables. |
| `Verificacion_entrega.json` | Comparación integral de CSV/Parquet y archivos anuales. |
| `SHA256SUMS.txt` | Huellas para verificar todas las descargas de datos. |

El CSV completo supera el límite de filas de una hoja de Excel. **Para Excel, usar los CSV anuales**: UTF-8, separador coma y decimal punto. Cada archivo anual tiene menos de 538.000 filas. Los códigos de barra deben importarse como texto.

## Reproducibilidad y alcance

La verificación local contrastó todas las filas y las 31 columnas: identificadores y posiciones vacías coinciden exactamente; el error numérico máximo fue cero. Los CSV anuales concatenados y el gzip descomprimido reproducen exactamente el CSV principal. Las descargas y extracciones de cuatro meses también se comprobaron en Linux mediante GitHub Actions.

El paquete de insumos reconstruye los entregables desde particiones archivadas. **No incluye todos los originales nacionales**. La adquisición desde el proveedor constituye una etapa adicional, documentada mediante fuentes, scripts y hashes. Las versiones DEF no se presentan como la última reliquidación disponible. Los CSV no mezclan silenciosamente revisiones ni completan valores ausentes.

**Reconstrucción completa en Linux aprobada:** [GitHub Actions](https://github.com/a-cartes/datacenter/actions/runs/36295132374). Se verificaron 258 insumos y las 3.411.527 filas; el CSV reconstruido tiene exactamente el mismo SHA-256 que la versión publicada. Las pruebas de referencias, corrupción de datos y del lector de paquetes también aprobaron. El flujo corrigió el orden de preparación de sus pruebas; el constructor, contrato y datos siguen congelados en el tag v0.2.0.

## Alcance científico

La unidad es una barra y una hora publicada; las identidades históricas y sockets no son centros independientes. Se preservan etiquetas horarias y códigos mensuales sin inferir continuidad física o UTC. Quillota 110 y 220 son referencias descriptivas. Las capas de medición no se han unido automáticamente al precio y el agregado HT1 + HT2 no acredita consumo total de campus.

La versión prepara los datos del artículo *Entrada de centros de datos y diferenciales nodales de costo marginal: evidencia causal para Chile*. Todavía requiere validar eventos, vínculos eléctricos, reloj, comparadores y exposición antes de ATT, DiD escalonado, estudio de eventos o spillovers. No contiene estimaciones causales.
