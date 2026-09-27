# Panel observacional v8

Construcción desde **v0.2.0 congelado**: 3,411,527 precios DEF; 142,151 filas barra–día de calendario y 4,756 filas barra–mes–reloj. Fechas: 2020-01-01 a 2026-09-18. Ningún precio se replica por centro de datos.

## Reproducción

`python SOCHER_2026_v8_panel_causal/scripts/construir_panel.py --root /ruta/al/proyecto`

Se requieren pandas, numpy, pyarrow y openpyxl (entorno del proyecto). `--output-dir /ruta/alternativa` permite reconstruir en otra carpeta. El script verifica hashes de CSV y Parquet congelados, y del libro adicional de agosto 2023. No descarga ni modifica entregas anteriores.

## Regla de agregación

El diario tiene clave `familia_reloj, barra_cmg, fecha`; el mensual añade `mes` y conserva separados los dos relojes de julio 2024. Cada diferencial se recomputa **antes** de agregar, mediante precio de barra menos referencia Quillota única, emparejada por fecha, familia de reloj y etiqueta horaria. El mensual promedia horas observadas, no medias diarias con igual peso. Se incluye una sensibilidad mensual sobre días de exactamente 24 etiquetas. El diario conserva listas y firmas de etiquetas para exigir soporte idéntico entre barras en cualquier comparación futura. Las medias, desviaciones, mínimos y máximos son descriptivos.

Histórico: etiquetas 1–25; moderno: HRA 0–24, con cuatro intervalos válidos. No se resta una unidad, no se inventa UTC y no se une carga. La condición `soporte_24_etiquetas` es técnica; no habilita causalidad ni certifica duración física en días de cambio de hora.

El calendario amplía cada etiqueta/mes a todos los días dentro de su régimen y corte DEF. Hay 21 filas de día sin precio y 504 etiquetas horarias ausentes frente a la unión. No se imputa. La ausencia de una etiqueta durante todo un mes permanece desconocida: no se crea un cero ni un estado de tratamiento. No hay PRE en el panel.

## Identificadores y overlay

`mapeo_mensual.csv` enlaza cada fila a sus identificadores originales. `mapeo_metadatos_observados.csv` preserva cada variante exacta, incluidos vacíos, 0, nombres y [NO_MOSTRAR], con fechas de **observación**, no vigencia eléctrica. Cambios de marcadores no crean nodos ni observaciones adicionales.

La homologación nueva de agosto de 2023 enlaza literalmente 53 de 58 etiquetas (39,432 precios), sin alterar precios ni archivos v0.2.0. Los cinco enlaces no hallados permanecen vacíos. Los códigos no se transportan entre meses. Los 266 segmentos separan cambios literales, lagunas mensuales y familias de reloj; no son activos físicos certificados. En particular, los cambios septiembre–octubre de 2023 y julio de 2024 no se resuelven por semejanza.

## Archivos y alcance

CSV y Parquet diario/mensual contienen lo mismo. Las tablas de cobertura, diccionario, cambios documentales y homologación permiten revisar las uniones. `validacion/validacion_panel.json` registra conteos, errores numéricos, dependencias, hashes y límites. La base horaria íntegra permanece en v0.2.0; su clave de precio es única.

No hay tratamiento, exposición, controles certificados, ATT ni estimación de efectos en estos archivos. Las relaciones centro–evento–barra deben incorporarse desde expedientes externos con vigencia acreditada, sin multiplicar los precios por campus. Quillota 110/220 son referencias descriptivas.
