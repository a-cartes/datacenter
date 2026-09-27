# Etapa v8: construcción analítica y expedientes

Avance del 27 de septiembre de 2026. [Manuscrito](../SOCHER_2026_v8_panel_causal/documentos/manuscrito_v8.md) · [Protocolo](../SOCHER_2026_v8_panel_causal/documentos/protocolo_previo_v8.md) · [Evidencia de eventos](../SOCHER_2026_v8_panel_causal/eventos/README_evidencia_y_decisiones.md).

## Entrega construida

| Producto | Dimensión |
|---|---:|
| Panel diario | 142.151 filas, 35 columnas |
| Panel mensual | 4.756 filas, 38 columnas |
| Etiquetas distintas de precio | 64 |
| Segmentos observacionales, sin identidad física certificada | 266 |
| Hitos documentales | 24 |
| Fuentes catalogadas | 33 |
| Eventos y comparadores causales habilitados | 0 |

El [panel diario comprimido](../SOCHER_2026_v8_panel_causal/panel/panel_diario.csv.gz) contiene el CSV íntegro, también disponible como [Parquet](../SOCHER_2026_v8_panel_causal/panel/panel_diario.parquet). El [CSV mensual](../SOCHER_2026_v8_panel_causal/panel/panel_mensual.csv) y el [Excel de revisión](../SOCHER_2026_v8_panel_causal/revision/Revision_panel_causal_v8.xlsx) permiten revisar agregados, eventos, controles, fuentes y diccionario sin cargar millones de registros en una hoja.

La base v0.2.0 permanece inmutable. La homologación adicional de agosto de 2023 enlaza exactamente 53/58 etiquetas y añade metadatos a 39.432 precios sin modificarlos. Se conservan 21 días-barra sin precio, equivalentes a las 504 etiquetas ausentes frente a la unión observada. Hay 141.723 días-barra con 24 pares y 407 con 25; esas etiquetas no certifican horas físicas.

## Qué cerró la revisión documental

- **Ascenty E53, NUP 5417:** energización y entrega a explotación realizadas el 05/05/2025. Unifilar y catálogo documentan ruta nominal E53–BP7–T7–BP1 de Chacabuco 110 kV. No se iguala BP7 a la barra CMg de 23 kV ni se presume nueva demanda del campus.
- **Las Canteras, junio de 2024:** informes diarios documentan maniobras concurrentes de Las Vegas y Santiago Solar. El informe del día 25 muestra variación posterior del estado. La fecha/noche publicada no prueba simultaneidad física con mediciones aún sin reloj conciliado.
- **Sonda:** se precisa la ruta BP8–T8–BP2 en diciembre de 2024; no se aplica retroactivamente a septiembre de 2020.
- **ODATA:** se separan operación comercial del campus, ampliación y obra eléctrica. El registro de pruebas de ST02 no demuestra una fecha efectiva diaria a partir de su fecha programada.

Cada hito conserva intervalo de fecha, vigencia y localizador en la [matriz](../SOCHER_2026_v8_panel_causal/eventos/matriz_eventos_elegibilidad.csv). El catálogo diferencia fuentes archivadas de documentos solo consultados o recuperados en etapas anteriores; no se declara archivado un archivo ausente.

## Análisis ejecutado

La [tabla descriptiva](../SOCHER_2026_v8_panel_causal/resultados/tabla_descriptiva_anual.csv) utiliza 139.277 barra-días de 24 pares, excluye la propia referencia Quillota 110 y pondera igual cada barra-día observado. Separa los dos regímenes de 2024. Sus medias y percentiles reflejan una muestra de composición variable; no son efectos de tratamientos. Las bandas de las figuras son percentiles 10–90, no intervalos de confianza.

El [diagnóstico de soporte](../SOCHER_2026_v8_panel_causal/resultados/soporte_eventos_ventana_registrada.csv) aplica las ventanas registradas de días −112 a −8 y 0 a 89. Separa conteos brutos de compatibilidad temporal: cruzar el 15/07/2024 sin puente validado impide considerar la ventana compatible. La cobertura individual no demuestra comparación común ni identificación.

La [puerta de estimación](../SOCHER_2026_v8_panel_causal/resultados/estado_estimacion.json) se ejecutó y conserva ATT, dinámica causal, spillovers e incertidumbre como no disponibles. Ningún expediente cierra simultáneamente naturaleza del tratamiento, conexión vigente e historia de comparadores. No disponible no significa efecto nulo.

## Validación y reproducción

El [informe de construcción](../SOCHER_2026_v8_panel_causal/validacion/validacion_panel.json) verifica unicidad y conservación de las 3.411.527 observaciones horarias. Los diferenciales recomputados coinciden exactamente con v0.2.0. Una [reconstrucción desde otro directorio](../SOCHER_2026_v8_panel_causal/validacion/reproduccion_panel_independiente.json) produjo 12 tablas idénticas por SHA-256. Es una réplica local, no una nueva ejecución en Linux ni revisión de otro investigador.

El Excel se creó con el runtime de documentos y se revisó visualmente por hoja. La relectura del archivo guardado contrasta todas las celdas de datos contra la especificación tipada. Es una instantánea de revisión; no se presenta como un modelo editable de estimación ni como prueba de ejecución en Excel de escritorio.

Para reproducir, disponer en la raíz de los insumos v0.2.0 indicados en su [guía](ampliacion_2020_2026.md), incluido el CSV congelado, su Parquet, manifiesto y metadatos. La homologación adicional ya está preservada en auditoría y no modifica el contrato anterior. Desde la raíz:

```bash
python SOCHER_2026_v8_panel_causal/scripts/construir_panel.py --root .
python SOCHER_2026_v8_panel_causal/eventos/construir_matriz_eventos.py
python SOCHER_2026_v8_panel_causal/eventos/catalogar_fuentes.py
python SOCHER_2026_v8_panel_causal/scripts/02_evaluar_diseno.py --root .
python SOCHER_2026_v8_panel_causal/scripts/03_descriptivos_y_soporte.py --root .
python SOCHER_2026_v8_panel_causal/scripts/04_preparar_revision.py --root .
```

El entorno observado es Python 3.13.15, pandas 3.0.5, numpy 2.5.3, pyarrow 25.0.1, openpyxl 3.1.5 y matplotlib 3.11.1. La creación del libro usa `crear_excel_revision.mjs` con `@oai/artifact-tool` del runtime de documentos. Los resultados científicos y CSV no dependen de ese runtime. Los scripts de adquisición pública se mantienen separados y no son necesarios para repetir las transformaciones con las fuentes preservadas.

La carpeta v8 del proyecto es la copia canónica de desarrollo. Su copia en este repositorio se verifica por hash; el CSV diario se publica comprimido y los archivos temporales de revisión visual permanecen locales. El manifiesto de descargas conserva rutas históricas de la máquina de adquisición; `catalogo_fuentes.csv` proporciona los localizadores relativos portables.

## Brechas que delimitan el siguiente análisis

Ascenty E53 ofrece fecha realizada y cobertura temporal, pero requiere adjudicar campus/fase y suministro anterior. Las Canteras exige separar cambio de demanda de maniobras o traslado y cerrar continuidad de precio/reloj. Los casos de 2020 necesitan historia eléctrica del alimentador en esa fecha, sin retrotraer catálogos de 2024–2026. Los controles requieren un argumento documentado de historia y exposición; no se escogerán por obtener tendencias o significación favorables.

El manuscrito está redactado con resultados descriptivos comprobados. La identificación causal y la preparación para envío siguen pendientes. No se ha enviado a Energy Economics ni a SOCHER.
