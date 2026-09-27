# Panel analítico y expedientes causales — etapa v8

Esta etapa continúa el artículo **Entrada de centros de datos y diferenciales nodales de costo marginal: evidencia causal para Chile**, en español y con resumen en inglés. El título expresa la pregunta de investigación; la atribución causal está condicionada al cierre de cada expediente y su comparación.

La entrega de precios **v0.2.0 permanece congelada**: 3.411.527 filas, 31 columnas, 1 de enero de 2020 a 18 de septiembre de 2026, DEF. Los PRE se mantienen separados. Esta carpeta contiene transformaciones posteriores y evidencia adicional, sin alterar los originales, activos, contratos o etiquetas de esa entrega.

**Construido y verificado:** panel diario de 142.151 filas y 35 columnas, mensual de 4.756 filas y 38 columnas, 24 hitos y 33 fuentes catalogadas. [Manuscrito](documentos/manuscrito_v8.md) · [Excel de revisión](revision/Revision_panel_causal_v8.xlsx) · [Panel diario CSV](panel/panel_diario.csv) · [Panel diario comprimido](panel/panel_diario.csv.gz) · [Panel mensual](panel/panel_mensual.csv) · [Expedientes](eventos/README_evidencia_y_decisiones.md).

Los descriptivos utilizan 139.277 barra-días de 24 pares, excluyendo la propia referencia. El diagnóstico ejecutado mantiene **cero eventos y comparadores habilitados**: no se estima ATT, dinámica causal ni spillovers con expedientes incompletos. Ascenty E53 tiene fecha realizada y ruta nominal a Chacabuco 110 kV; faltan naturaleza de la carga, fase/campus y comparación defendible.

## Productos

- `panel/`: panel diario y mensual, cobertura y diccionario. Las identidades observacionales no certifican continuidad física.
- `eventos/`: matriz centro/fase–evento–barra–vigencia, fuentes públicas y decisiones de elegibilidad.
- `documentos/`: protocolo registrado para esta etapa, manuscrito y referencias.
- `resultados/` y `figuras/`: salidas descriptivas y diagnóstico de soporte. Una estimación no habilitada se representa como no disponible, nunca como efecto cero.
- `revision/`: insumos y libro para revisión. El archivo diario íntegro se conserva en CSV/Parquet y el Excel muestra agregados manejables.
- `validacion/`: manifiestos y comprobaciones específicas de las nuevas transformaciones.
- `scripts/`: construcción reproducible. La copia canónica se mantiene en esta carpeta del proyecto; la copia publicada en el repositorio debe coincidir por contenido.

## Reglas de interpretación

Cada precio barra–período aparece una sola vez. Una barra compartida por centros no multiplica las observaciones. Los canales de medida, transformadores y fases no se cuentan como intervenciones independientes.

Las medias diarias se calculan sobre las etiquetas publicadas. No se resta uno a las horas históricas ni se inventa una hora UTC. Los diferenciales se forman sobre pares de etiquetas dentro de un mismo régimen antes de agregarlos. Los vacíos se conservan; ni una fecha faltante ni una conexión desconocida se convierten en cero.

La actualización de homologación de agosto de 2023 solo añade metadatos con unión exacta validada. No transporta códigos hacia otros meses ni acredita por sí misma la continuidad de activos.

Las referencias Quillota 110 y 220 definen resultados relativos. No son controles causales certificados. La ausencia de una barra en el registro de candidatos tampoco acredita ausencia de tratamiento o exposición.

## Alcance editorial

Energy Economics es la primera revista objetivo. La prórroga de SOCHER al 9 de octubre de 2026 procede de la comunicación del autor. No se ha enviado el artículo a revista o congreso.

## Repetir las transformaciones

Desde la raíz del proyecto, con los insumos v0.2.0 ya preservados:

```bash
python SOCHER_2026_v8_panel_causal/scripts/construir_panel.py --root .
python SOCHER_2026_v8_panel_causal/eventos/construir_matriz_eventos.py
python SOCHER_2026_v8_panel_causal/eventos/catalogar_fuentes.py
python SOCHER_2026_v8_panel_causal/scripts/02_evaluar_diseno.py --root .
python SOCHER_2026_v8_panel_causal/scripts/03_descriptivos_y_soporte.py --root .
python SOCHER_2026_v8_panel_causal/scripts/04_preparar_revision.py --root .
```

Entorno científico observado: Python 3.13.15, pandas 3.0.5, numpy 2.5.3, pyarrow 25.0.1, openpyxl 3.1.5 y matplotlib 3.11.1. `crear_excel_revision.mjs` consume el JSON de revisión y requiere `@oai/artifact-tool` del runtime de documentos; recibe entrada JSON, salida XLSX y directorio de QA. El análisis científico y sus CSV no dependen de ese runtime. `05_verificar_excel.py --xlsx <ruta>` relee las celdas exportadas. Los scripts de descarga son opcionales y están separados.

Una reconstrucción local desde otro directorio produjo 12 tablas idénticas por SHA-256. Los informes están en `validacion/`. No se ha repetido esta etapa en un equipo independiente ni en Linux. El CSV diario cabe en Excel, pero la revisión usa el resumen mensual para facilitar su manejo. En Git, el diario se conserva como gzip y Parquet; al descomprimir gzip se recupera el CSV íntegro.
