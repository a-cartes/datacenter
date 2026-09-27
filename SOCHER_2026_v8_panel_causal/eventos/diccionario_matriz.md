# Diccionario de la matriz documental

| Campo | Significado |
|---|---|
| evento_id | Identificador único de hito; no unidad independiente de tratamiento. |
| centro_id | Candidato del registro v6 o nuevo candidato E53. |
| campus_grupo_id | Agrupa fases y evita contar transformadores/hitos como campus distintos; grupos pendientes no equivalen campus validados. |
| fase | Nombre documentado de fase o incertidumbre explícita. |
| tipo_evento | Separa operación, prueba, PES, EO administrativa, inauguración, proyecto y medición. |
| nup | Identificador de proyecto cuando conocido; varios separados por punto y coma. |
| fecha_min, fecha_max | Límites de fecha documentada. Un año incierto se conserva como intervalo anual; vacío significa desconocido. No se usa el mínimo como tratamiento automático. |
| precision_fecha | Resolución y si es previsión. |
| fecha_realizada | SI: hito realizado; NO: previsión; OBSERVADO: cambio en medición; SI_ESTADO_FECHA_PENDIENTE: prueba/PES con ejecución exitosa pero sin fecha efectiva visible ni EO final; NO_CERRADO: falta evidencia. |
| barra_cmg | Etiqueta candidata del precio. Puede representar punto aguas arriba o ruta no cerrada: leer estado del enlace. Vacío no significa exposición cero. |
| barra_fisica | Instalación/cadena nominal y tensión con alcance de evidencia. |
| nemotecnico_fisico | Identificador físico relevante; no una homologación automática para todos los años. |
| vigencia_desde, vigencia_hasta | Fecha/intervalo de evidencia del vínculo. Vacío no implica infinito. |
| tipo_vigencia | Si es una observación puntual, proyección, inicio o esquema nominal; no inventa continuidad. |
| fuente_ids | Referencias al catálogo separadas por punto y coma. |
| localizadores | Página, figura, registro, lámina o IDs de objetos en la fuente. |
| enlace_precio_exacto | SI_NOMINAL_AGUAS_ARRIBA no implica precio de empalme; SI_BP1_NO_BP2 solo cierra BP1; NO_BP2 conserva diferencia de barra; NO no cierra enlace; SI_NOMINAL_RETROSPECTIVO requiere cautela histórica. |
| historia_suministro_cerrada | NO hasta conocer suministro anterior y distinguir carga nueva de traslado. |
| elegible_evento_causal | NO en las 24 filas. La decisión requiere tratamiento, enlaces, vigencia y diseño comparativo adecuados. |
| elegible_descriptivo | SI permite descripción documental/observada; no habilita estimación causal. |
| razon_elegibilidad | Criterio aplicado sin depender de precios, signos o significación. |
| brecha_pendiente | Evidencia específica que falta y limita la identificación. |

`catalogo_fuentes.csv` separa `DISPONIBLE` (archivo que existe y cuya huella se computó) de `NO_ARCHIVADO` (URL y lectura mediada/antecedente sin copia nueva). Las rutas son relativas a la carpeta `eventos`; `../../` apunta a etapas anteriores del proyecto. Reubicar solo esta carpeta exige conservar esas etapas o copiar su evidencia y actualizar explícitamente la referencia.
