# Revisión independiente del alcance ODATA ST01

27 de septiembre de 2026. Revisión por un agente distinto de quienes prepararon las fuentes, el diseño y la cobertura. Es control interno del proyecto, no revisión externa. No se consultaron magnitudes de precios ni se modificaron los productos revisados.

## Dictamen

El avance identifica una fecha de inicio de operación **declarada por el titular** y acredita disponibilidad de etiquetas publicadas en una ventana temporal viable. Todavía no identifica la toma de carga del centro ni su barra de suministro. La evidencia permite fijar una investigación eléctrica concreta alrededor del 1 de agosto de 2022; no habilita un efecto causal ni una asignación automática de ODATA a Batuco.

## Comprobaciones

1. **Fecha.** Se inspeccionaron las páginas completas de la carta original ODCH-ST01-061-2022 y del comprobante SMA. La carta está fechada y firmada el 18 de agosto de 2022, pero dice que la fase de operación «comenzará a contar del 01 de agosto de 2022». El comprobante 1005711 acredita recepción el 18 de agosto y limita expresamente su alcance a esa recepción. La precisión admisible es inicio declarado para el 1 de agosto; no fecha física de primera energización o carga, ni hecho verificado por la autoridad. El memo `diseno/actualizacion_fecha_SNIFA.md` conserva correctamente estas diferencias.
2. **Ruta.** `medicion/README_medicion_conexion.md` distingue la línea Batuco proyectada en la DIA del alimentador homónimo N22/52D22. El plano cargado en julio de 2022 lleva sello de revisión de noviembre de 2020, no certificación de puesta en servicio. La combinación orienta la búsqueda del empalme; no prueba que ODATA utilizara ese alimentador o BP3. Los identificadores de 2026 no certifican retrospectivamente el enlace. Se mantiene correctamente separada la obra Nueva Lampa/J9/T5 de 2025.
3. **Soporte.** La revisión del script confirma que cuenta celdas con contenido publicado, no que verifica valor numérico finito. La comprobación independiente del CSV de soporte encontró 856 claves barra-fecha únicas. En las cuatro etiquetas Batuco 013/110 y Quillota 110/220, las 105 fechas previas y las 90 posteriores tienen exactamente la misma firma impresa 1–24 y cero faltantes explícitos. Esta comprobación usa el producto de soporte y no reextrae los libros. SHA-256 del CSV: `d22ab62dd0ad9390cf8805f52d97e76c7f571656852c474e8c93313462ab6acc`.
4. **Interpretación del soporte.** Las firmas permiten preparar comparaciones de etiquetas coincidentes; no prueban identidad física histórica de las barras, 24 horas físicas, magnitudes válidas o ausencia de exposición de Quillota. No se debe llamar a las dos barras Batuco réplicas independientes ni seleccionar una por el efecto que produzca. La barra 13 kV no sustituye BP3 de 23 kV.

## Próximo paso con mayor valor

Cerrar el empalme o suministro inicial realizado, mediante una constancia que enlace campus, alimentador/punto de medida y vigencia. Debe aclarar si la operación declarada sucede después de pruebas o carga previa. Con esa pieza se puede definir el resultado nodal o aguas arriba y congelar el argumento contrafactual antes de examinar el post. Si no aparece, el caso queda documentado como operación declarada con fecha y ruta pendiente, sin convertir la buena cobertura temporal en tratamiento identificado.

No se detectó una atribución causal indebida en los dos memos revisados. El principal cuidado de redacción del informe integrado es conservar «declarado por el titular» y «ruta candidata»; la expresión «fecha real de entrada acreditada» excedería las fuentes actuales.
