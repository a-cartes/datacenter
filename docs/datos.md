# Leer y utilizar la base

[Inicio](../README.md) · [Reproducción](reproducir.md) · [Método](metodologia.md)

## Qué representa una fila

Una identidad histórica de barra, una fecha y una etiqueta horaria publicada. `observacion_id` es la clave única del panel. `barra_id` conserva la combinación histórica de nombre y código; no se deben fusionar cambios de identidad sin demostrar continuidad.

Los dos diferenciales disponibles comparan el precio de la barra con Quillota 110 y 220 kV en la misma etiqueta horaria. La unidad es USD/MWh. Los indicadores de calidad permiten separar series provisionales y observaciones con marcas de revisión.

## Cobertura y formatos

| Producto | Tamaño lógico | Función |
|---|---:|---|
| Panel horario | 178.016 × 66 | Base de precios y variables previstas para el diseño |
| Panel diario | 7.415 filas | Agregación descriptiva con reglas de calidad documentadas |
| Centros y candidatos | 10 registros | Nueve registros candidatos de campus/proyecto y una barra sin centro adjudicado |
| Hitos documentados | 24 registros | Antecedentes que deben clasificarse antes de definir tratamientos |
| Relaciones centro–barra | 17 registros | Vínculos documentales y sus límites |
| Mediciones originales integradas | 67.384 registros | Lecturas a 15 minutos de HT1, HT2 y HT3 de Las Canteras |
| Carga horaria por etiqueta | 7.319 bloques | Agregación HT1+HT2, aún sin enlace al panel de precios |

Los precios cubren febrero, abril, mayo, junio y del 1 al 14 de julio de 2024. La ausencia de enero, marzo y otros períodos no se reemplaza por ceros.

El CSV sin comprimir de la entrega original ocupa 169,7 MB. El Excel ocupa 41,1 MB porque su contenido está comprimido. La diferencia de tamaño no implica menos observaciones. El formato Parquet conserva de manera compacta tipos y valores nulos.

## Variables por completar

`tratado_it`, `post_evento`, `control_validado`, `cohorte_g_dia`, los tiempos relativos, `exposicion_red`, `carga_asignada_mw` y la fecha causal quedan vacíos hasta validar su asignación. No deben usarse como ceros en una regresión. `elegible_estimacion_causal` es falso en esta versión.

El reloj UTC del precio también está pendiente. Las etiquetas horarias pueden incluir una hora 25; no deben convertirse automáticamente en horas físicas continuas.

## Diccionarios y procedencia

- [Diccionario del panel](../SOCHER_2026_dataset/documentacion/diccionario_panel.csv).
- [Diccionario de mediciones](../SOCHER_2026_dataset/documentacion/diccionario_mediciones.csv).
- [Catálogo de tablas de la entrega original](../SOCHER_2026_dataset/documentacion/catalogo_tablas.csv).
- [Mediciones, unidades y reloj](../SOCHER_2026_dataset/documentacion/Mediciones_y_reloj.md).
- [Eventos y relaciones](../SOCHER_2026_dataset/documentacion/Eventos_relaciones_y_red.md).

El conteo `n_nulos` del diccionario original distingue nulos según el tipo de la tabla de origen; las cadenas de texto vacías pueden no estar incluidas. En CSV y Excel ambas pueden verse como celdas vacías. Las comprobaciones de exportación contrastan todos los vacíos con el CSV fuente.
