# Actualización del diseño: operación declarada de ODATA el 1 de agosto de 2022

27 de septiembre de 2026. Complementa `memo_identificacion.md`; no modifica el protocolo v8 ni ejecuta resultados nuevos.

## Lo que ahora sí está fechado

La carta original ODCH-ST01-061-2022, de 18 de agosto de 2022, declara inicio de la fase de operación del proyecto ODATA Datacenter desde el **1 de agosto de 2022**. La formulación usa futuro pese a que la fecha indicada es anterior a la carta. El expediente SNIFA 1005711 y su comprobante acreditan recepción el 18 de agosto; la declaración corresponde al titular. El original fue recuperado y verificado por el agente documental. Se referencia por ruta y SHA256 en `decision_diseno.json`; se conserva en `../entrada/fuentes/`.

La carta no comunica MW, módulo específico, medidor, empalme ni origen eléctrico. Por eso mejora la fecha operacional del campus y acota la búsqueda, sin convertirse por sí sola en fecha de primera energización o de aumento neto de carga. Tampoco adjudica retroactivamente el suministro a la conexión Nueva Lampa J9/transformador T5 de 2025.

## Ventana exacta que puede prepararse

Si el expediente eléctrico permite adoptar esa fecha para la intervención definida, la regla ya registrada da:

| Elemento | Fecha | Días civiles |
|---|---|---:|
| Operación declarada, día de transición | 1 agosto 2022 | 1 |
| Primer día completo propuesto, g | 2 agosto 2022 | — |
| Pre registrado [-112,-8] | 12 abril–25 julio 2022 | 105 |
| Base g−8 | 25 julio 2022 | 1, incluido en pre |
| Anticipación/transición [-7,-1] | 26 julio–1 agosto 2022 | 7 |
| Post registrado [0,89] | 2 agosto–30 octubre 2022 | 90 |

`calendario_ventana_operacion_declarada_20220801.csv` contiene las 202 fechas y sus roles, calculadas sin abrir resultados de precios. No verifica calidad, homologación ni cobertura: los umbrales de 95 días previos y 81 posteriores siguen pendientes. La elección del 2 de agosto deriva de la regla existente, no de un salto observado de precios o demanda.

Esta ventana está después de la incorporación de Nueva Lampa en enero de 2021 y antes de la obra Nueva Lampa/ODATA en puesta en servicio en 2025. Esos dos cambios **no caen dentro de la ventana propuesta**. Tampoco cruza julio de 2024. Evitar esos cortes no demuestra que la topología de abril–octubre de 2022 permaneciera fija.

## Concurrencias: búsqueda ahora acotada

La ruta de suministro que surja del expediente decide el alcance. La pista actual es una línea denominada Batuco, posiblemente vinculada a distribución. El agente de conexión encontró un DUF de S/E Batuco cargado el 4 de julio de 2022 que representa el alimentador Batuco N22/52D22 sobre BP3 de 23 kV/transformador 3, pero la similitud del nombre no acredita todavía que haya abastecido ODATA. Debe corroborarse la arista campus–alimentador y su realización.

No basta con un precio rotulado **Batuco 13 kV o 110 kV** para asignar la barra de 23 kV. Si finalmente el consumo está en BP3 de 23 kV, un resultado en la barra de 110 kV solo podrá definirse como resultado aguas arriba y tras documentar su conexión vigente; no se renombra como precio del punto de consumo. Un precio de 13 kV podría ser otro ramal y no se incorpora por cercanía de nombre. El inventario de cobertura o una ampliación de barras fuera de v0.2.0 debe conservar esa distinción.

La búsqueda pública dirigida recuperó registros de poda con líneas energizadas y sin consumo afectado en Nueva Lampa durante julio de 2022: solicitudes 2022060163/0165/0168, en EAF267/273/291. Son pistas operativas para comprobar en los originales, **no una prueba de cambio permanente de red ni una razón automática para eliminar días**. Las fechas indexadas son de inicio programado en algunas tablas; no se transforman en fecha efectiva sin revisar las columnas completas. Los enlaces se preservan en `busqueda_concurrencias_focalizada.csv`.

No se encontró en esta búsqueda limitada un evento de energización simultánea verificable para el 1 de agosto en la ruta inicial; esto no acredita ausencia de concurrencias. El cierre útil es revisar entre el 12 de abril y el 30 de octubre, para el alimentador y sus barras fuente acreditadas: maniobras que cambien el origen de suministro, transformadores en servicio/fuera de servicio, nuevos grandes retiros y centrales directamente pertinentes. La audiencia ODATA/Enel de 21 de julio de 2022 cae en el pre; habla de obras y no prueba ni descarta cargas de construcción o pruebas anteriores a la operación.

## Siguiente diseño ejecutable, sin cambiar de fecha por los resultados

1. **Cerrar el enlace inicial:** buscar el empalme/recepción eléctrica o una constancia realizada de suministro que conecte ODATA con el alimentador vigente el 1 de agosto. La RCA/DIA describe el diseño aprobado; el aviso SMA fecha la operación declarada. Su combinación es útil pero aún no prueba toda la realización eléctrica.
2. **Definir el resultado antes de abrir el post:** barra del suministro si está disponible, o barra aguas arriba explícitamente identificada. Mantener la definición de diferencial y calidad del protocolo. No imputar 23 kV desde 13 kV ni utilizar J9/T5 de 2025 como identidad de 2022.
3. **Congelar una comparación relativa y su argumento contrafactual:** seleccionar nodos por su posición eléctrica y cambios documentados, no por la significación. Pueden responder a la misma entrada; el parámetro sería el efecto diferencial entre esas respuestas. El precio de referencia Quillota no adquiere por sí solo condición de control.
4. **Comprobar el pre y las concurrencias sin ver el post:** verificar estabilidad de identidades, firmas horarias, soporte y cambios de red; registrar exclusiones por reglas documentales. Con 105 días no se observa un ciclo anual. Una sensibilidad con historia previa adicional debe fijarse antes del post y permanecer después del cambio estructural de comienzos de 2021. Una validación previa de predicción permite descartar una mala comparación, pero no seleccionar retrospectivamente la que entregue el mayor efecto.
5. **Ejecutar si el evento y el diseño quedan cerrados:** conservar pre 12 abril–25 julio y post 2 agosto–30 octubre. Reportar magnitud y dinámica como efecto relativo condicional a la identificación. La inferencia para un único proyecto necesita procedimiento temporal/dependencia justificado; muchas barras u horas no crean asignaciones independientes.

Si no aparece constancia suficiente de la ruta inicial, el próximo resultado honesto es un evento de operación **fechado pero todavía sin barra eléctrica adjudicada**, no otra estimación de precios seleccionados por comuna. La fecha nueva reduce sustancialmente la búsqueda documental y separa la entrada de 2022 de la conexión posterior; no resuelve sola la causalidad.

## Corrección final: discrepancia con OGP y dos fuentes de suministro

La cartera OGP de abril de 2023, p.47, incluye la fila **ODATA**, inversión de **217 MMUS$**, etapa **Operación**, y **octubre de 2022** en la columna expresamente titulada fecha de inicio de operación. El original `../entrada/fuentes/OGP_cartera_abril2023.pdf` y su página renderizada están archivados y fueron verificados por el frente documental. Esta es una **discrepancia real** frente al 1 de agosto declarado ante la SMA; no hay evidencia para descartarla como una mera actualización administrativa.

En consecuencia, el calendario con g = 2 de agosto permanece como **escenario condicional**, sin fecha de tratamiento eléctrico habilitada. Antes de consultar nuevos resultados debe resolverse si ambas fuentes usan la misma definición, fase y alcance de operación. Si no se resuelve y se justifica que describen el mismo evento, se debe registrar por adelantado un tratamiento de la incertidumbre temporal —por ejemplo, un intervalo de transición y todas las sensibilidades pertinentes—, sin escoger la fecha que produzca el mayor efecto. No se crea ahora un día ficticio de octubre ni se declara automáticamente agosto–octubre como un intervalo verificado de toma de carga. Si los hitos corresponden a fases diferentes, se mantendrán separados.

Además, la **Adenda del 1 de octubre de 2020, respuesta6, p.7 PDF**, mantiene dos fuentes: distribución pública para ST01 y una línea dedicada de 23 kV desde S/E Lampa para abastecer todo el proyecto. Esto amplía el alcance potencial de la segunda fuente respecto de la DIA inicial, pero **no elimina la primera fuente denominada Batuco ni certifica cuál estaba operativa en agosto u octubre de 2022**. El cierre del enlace debe resolver las dos alternativas y sus vigencias. La cronología no habilita asignar una barra por defecto ni seleccionar entre rutas según el comportamiento de sus precios.
