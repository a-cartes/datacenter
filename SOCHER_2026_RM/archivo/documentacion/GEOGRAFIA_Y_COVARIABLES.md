# Geografía y covariables previas para la réplica chilena

Revisión de fuentes oficiales al 1 de octubre de 2026. Se verificaron documentación y disponibilidad publicada; todavía no se descargaron ni armonizaron los conjuntos censales completos.

## Escalas disponibles

| Fuente | Disponibilidad documentada | Límite para la réplica |
|---|---|---|
| Censo 2017 | Microdatos con comuna, distrito, área y zona o localidad; variables de población, viviendas y escolaridad | Los microdatos individuales no identifican manzanas. Los agregados manzana o entidad son un producto distinto, sujeto a confidencialidad |
| Cartografía 2017 | División censal y administrativa y capas de población y vivienda | Los límites deben fijarse y documentarse; no son equivalentes por definición a sectores censales estadounidenses |
| Microdatos Censo 2024 | Personas, hogares y viviendas a escala de comuna y área | No asumir acceso individual público a distrito, zona o manzana |
| Agregados Censo 2024 | Publicación de 189 variables a escalas de manzana, entidad, zona y localidad, junto con cartografía | Permiten los cruces e indicadores publicados, no cualquier cruce individual; falta inspeccionar el diccionario completo |
| Censos 1992 y 2002 | Accesos REDATAM en el portal oficial | Son candidatos para períodos previos tempranos, con extractos y correspondencias espaciales aún por verificar |

Fuentes: [Manual del usuario Censo 2017, capítulos II a IV y anexo 3](https://redatam-ine.ine.cl/manuales/Manual-Usuario.pdf); [Geodatos abiertos INE](https://www.ine.gob.cl/herramientas/portal-de-mapas/geodatos-abiertos); [publicación de microdatos 2024 del 4 de diciembre de 2025](https://www.ine.gob.cl/sala-de-prensa/prensa/general/noticia/2025/12/04/ine-publica-base-de-datos-del-censo-de-poblaci%C3%B3n-y-vivienda-2024); [publicación de agregados y cartografía del 16 de diciembre de 2025](https://www.ine.gob.cl/sala-de-prensa/prensa/general/noticia/2025/12/16/ine-publica-bases-de-datos-a-nivel-de-manzana-y-cartograf%C3%ADa-del-censo-de-poblaci%C3%B3n-y-vivienda-2024); [portal REDATAM](https://redatam.ine.gob.cl/).

Durante la revisión, dos enlaces antiguos de descarga ArcGIS del portal de geodatos devolvieron 404. Esto no demuestra ausencia del producto: el portal y el visualizador seguían accesibles. Debe verificarse la descarga específica antes de declarar disponible una capa para el procesamiento.

## Ingreso y comparabilidad con el artículo

CASEN ofrece ingresos, educación y vivienda, y un complemento con identificadores territoriales. Sin embargo, desde 2011 su diseño prioriza representatividad nacional, regional y por área urbana o rural. El código de comuna no garantiza precisión para esa comuna, y menos para zonas o manzanas. Los cálculos deben respetar el diseño muestral y evaluar sus errores. Fuentes: [CASEN 2022](https://observatorio.ministeriodesarrollosocial.gob.cl/encuesta-casen-2022) y [preguntas frecuentes oficiales sobre información y estadísticas](https://observatorio.ministeriodesarrollosocial.gob.cl/preguntas-frecuentes).

Las [estimaciones de pobreza comunal](https://observatorio.ministeriodesarrollosocial.gob.cl/pobreza-comunal-2022) son otra posibilidad, según año disponible. Una tasa de pobreza estimada mediante áreas pequeñas no equivale al ingreso mediano del hogar utilizado por el artículo. Si se propone esa covariable, deberá explicarse la sustitución conceptual y respetar su escala.

El [cuestionario del Censo 2024](https://censo2024.ine.gob.cl/wp-content/uploads/2025/03/Cuestionario-Viviendas-Particulares_CPV2024.pdf) incluye educación y empleo, pero no aporta un monto de ingreso del hogar equivalente al del artículo. La selección final de covariables chilenas permanece pendiente.

## Reglas de construcción propuestas

La fecha de referencia de la covariable debe ser anterior a la entrada que se estudia. La fecha posterior de publicación no invalida un dato referido a un período previo; a la inversa, disponer hoy del Censo 2024 no lo convierte en información previa para entradas de 2015 o 2020.

Se fijará una cartografía de referencia y se construirán correspondencias explícitas al combinar años. No se verificó una tabla oficial completa de homologación entre 2002, 2017 y 2024 en esta revisión. Los polígonos agrupados o suprimidos por confidencialidad conservarán esa condición; no se interpretarán como observaciones de población cero.

Además de los cambios de límites, cambia el concepto de población: el censo de 2017 fue de hecho y el de 2024 utiliza residencia habitual. El INE explica su tratamiento en la [nota técnica de comparación de población](https://censo2024.ine.gob.cl/wp-content/uploads/2025/04/N3_Nota_Tecnica_Comparacion_Poblacion_CPV2024.pdf). Una variación entre ambos no debe atribuirse íntegramente a cambios demográficos sin atender esa diferencia.

La unidad final se elegirá cruzando resolución de precios, localización de instalaciones, historia de tratamiento y covariables. La disponibilidad de una capa cartográfica, por sí sola, no determina la unidad econométrica.
