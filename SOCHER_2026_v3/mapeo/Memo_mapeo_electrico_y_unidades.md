# Mapeo eléctrico, fases y unidades: verificación oficial

Fecha de consulta: 25 de septiembre de 2026. Los archivos originales se conservan con sus hashes en los manifiestos de esta carpeta.

## Resultado que cambia el diagnóstico

**Se acepta el enlace CANTERAS______110 ↔ BA01T0487SE001T0487 ↔ S/E LAS CANTERAS (SE001T0487, id 2433), propiedad de Edgeconnex Chile V SpA.** La sospecha de que esta barra CMg correspondiera a una instalación de Biobío no se sostiene para este código. El enlace ya no depende de coincidencia de nombres.

La prueba es la hoja `HOMOLOGACIÓN`, fila 175, del archivo oficial `CEN_Homologacion_barras_cmg_2407_def.xlsx`, miembro de [cmg2407_def.zip del CEN](https://www.coordinador.cl/wp-content/uploads/2024/08/cmg2407_def.zip). Sus columnas relacionan Barra CMG, Barra AUX y Nemotécnico. El miembro fue descargado en Safari porque la petición directa devolvía HTTP 403. Safari descomprimió el ZIP; se preservó el libro de homologación en el proyecto. La hoja `2024-08-22-Barra.tsv` confirma además la nomenclatura física vigente en ese extracto.

El código largo coincide exactamente con el CSV histórico descargado por el investigador (`../precios/CEN_CMg_historico_2024_Canteras_Quillota.csv`) y con [Infotécnica, elementos de la subestación 2433](https://api-infotecnica.coordinador.cl/v1/subestaciones/2433/elementos/). La [ficha de la subestación](https://api-infotecnica.coordinador.cl/v1/subestaciones/2433/) identifica propietario y código SE001T0487. El histórico contiene 2.521 registros Las Canteras desde el 1 de abril hasta el 14 de julio de 2024. Esta cobertura no demuestra ausencia de operación antes de abril.

| Barra CMg | Nemotécnico físico | Descripción oficial | Fila homologación |
|---|---|---|---:|
| CANTERAS______110 | BA01T0487SE001T0487 | Las Canteras 110 kV BP1 | 175 |
| CANTERAS______023 | BA04T0487SE001T0487 | Las Canteras 23 kV BP1 | 174 |
| QUILLOTA______110 | BA01T0002SE032T0002 | Quillota 110 kV BP1 | 992 |
| QUILLOTA______220 | BA02T0002SE032T0002 | Quillota 220 kV BP1-1 | 993 |
| C.NAVIA_______110 | BA01T0002SE008T0002 | Cerro Navia 110 kV BP1 | 139 |
| C.NAVIA_______220 | BA03T0002SE008T0002 | Cerro Navia 220 kV BP1 | 140 |
| TLIBERTADORES_110 | BA01T0043SE001T0043 | Tap Libertadores 110 kV BP1 | 1225 |

**La barra de referencia declarada por el CSV histórico es Quillota 220 kV BP1-1, no Quillota 110 kV.** Si se calcula un diferencial con Quillota 110 debe denominarse comparación elegida por el investigador, sin atribuirla a la referencia publicada por el CEN.

El XLSX nuevo `../precios/CEN_CMg_2024_0715_1231_Canteras_Quillota_CerroNavia_def_horario.xlsx` contiene las primeras cinco barras de 110/220 kV indicadas arriba (excepto Tap Libertadores): 4.080 filas del 15 de julio al 31 de diciembre, Real Definitivo, sin claves Fecha/Hora duplicadas ni precios nulos. Las cinco columnas tienen 4.080 valores. Unidad USD/MWh según [página madre CEN](https://www.coordinador.cl/costos-marginales/), no rotulada en el libro. El mapeo de identidad está resuelto; **no implica homogeneidad del procedimiento de valorización antes/después del 15 de julio**. El CEN identifica esa fecha como inicio de uso de los nuevos costos para balances de energía y SSCC.

Todos los días del XLSX nuevo tienen 24 etiquetas 0–23. No declara zona horaria y esto no acredita continuidad UTC en el cambio de hora de septiembre. Mantener el índice original y auditar la correspondencia temporal con las medidas de 15 minutos; no desplazar automáticamente por UTC ni interpolar.

## Fases de Las Canteras: no son tres centros independientes

La documentación operacional enlaza los NUP con equipo físico, y separa energización/PES, entrada en operación administrativa y carga observada:

| Proyecto/hito | Evidencia operacional | Equipo | Qué permite afirmar |
|---|---|---|---|
| NUP 3016 | EAF 143/2024, PDF p. 105, maniobras reales 7-04-2024 08:52–21:24 | S/E 2433, paños de red HR/HS y líneas | Trabajo de continuación de PES de la subestación; no primera carga informática |
| NUP 3975 | EAF 143/2024, p. 105, registros 2024032530 y 2024032531, mismo intervalo | Transformador 1 id3593, HT1/ET1/ESA1; transformador 2 id3594, HT2/ET2/ESA2 | Los dos transformadores corresponden al mismo proyecto en Las Canteras |
| NUP 3349 | EAF 414/2024, p. 99, registro 2024080203, ejecución 6-08-2024 09:32–16:03 | Transformador 3, paño HT3 id35045/ET3, alimentadores E9–E12; energización desde barra 110 kV N°2 | Energización/PES de T3 el 6 de agosto, distinta de EO 19 de agosto y de primera carga medida |

Fuentes: [EAF 143/2024](https://www.coordinador.cl/wp-content/uploads/2024/04/EAF-143-2024.pdf), [EAF 414/2024](https://www.coordinador.cl/wp-content/uploads/2024/08/EAF-414-2024.pdf). Se preservan originales, extractos por página y recortes visuales de las filas. Las fechas EO y sus anexos ya se conservan en v2; este memo aporta el enlace de las fases con los equipos y medidores.

La aparente denominación distinta también está documentada: el [acta CMN de 9-08-2023](https://www.monumentos.gob.cl/sites/default/files/20230809_acta_sesion_ord_env_def_f_0.pdf), p. 106, ítem 108, denomina el proyecto Las Canteras y señala su nombre anterior Subestación Seccionadora Colina en 110 kV. No debe equipararse por eso cualquier socket o barra llamada COLINA con Edgeconnex: existe una instalación distinta con ese nombre.

## Medición: equipos identificados, sentido sujeto a control

[Infotécnica 2433/elementos](https://api-infotecnica.coordinador.cl/v1/subestaciones/2433/elementos/) vincula por nodo de conexión:

| Paño | Trafo id | Medidor id | Nodo conexión de ambos | Socket en catálogo actual |
|---|---:|---:|---:|---|
| HT1 | 3593 | 5085 | 35096 | LSCANTRS_110_HT1_EDG |
| HT2 | 3594 | 5084 | 35091 | LSCANTRS_110_HT2_EDG |
| HT3 | 3653 | 5690 | 36558 | LSCANTRS_110_HT3_EDG |

La barra CMg publicada es BP1; la maniobra de T3 menciona BP2. El enlace a la subestación es válido, pero no demuestra que BP1 y BP2 nunca se separen operacionalmente. Para un estudio de interferencia de red detallado hay que preservar configuración y estado de acoplamiento, y evitar imputar a un solo alimentador todo el consumo del complejo.

El [catálogo SOCKET_HABILITADO](https://medidas.coordinador.cl/SOCKET/SOCKET_HABILITADO.xlsx), hoja 24092026, identifica Las Canteras en región 13. Filas5465/5466/5730 corresponden a HT1/HT2/HT3. Sus columnas explícitas asignan retiro activo a kWhD e inyección activa a kWhR. H1–H4 se clasifican como tránsito: no sumar estas líneas a HT1/HT2 porque duplicaría flujos. **El catálogo es una captura de septiembre de 2026 y no acredita por sí solo igual configuración durante todo 2024.**

El [Documento Técnico de Medidas 2021](https://medidas.coordinador.cl/public/DOCUMENTACION/NORMATIVA/Documento%20T%C3%A9cnico%20Sistema%20de%20Medidas%20de%20Energ%C3%ADa%202021.pdf), pp.8–9, establece energía activa en kWh, canales directos para retiros y reversos para inyección respecto de la barra, e integración de 15 minutos. No deben confundirse kWh con kW: una energía de intervalo se divide por 0,25 h para obtener potencia media kW. Después se divide entre 1.000 para MW. Para agregar energía horaria se suman intervalos completos.

HT3 conserva una anomalía material: el catálogo lo clasifica G_C, mientras HT1/HT2 figuran R. La auditoría de originales 2024 halló HT3 sólo en octubre–diciembre, D cero y R positivo de unos18 MWh mensuales. **No invertir automáticamente R ni atribuir estos ~25 kW a nueva demanda informática.** El [reporte de configuración de medidor 5690](https://api-infotecnica.coordinador.cl/v1/medidores/5690/documentos/412527/), creado el 27-09-2023, confirma serial MZ-2208A680-01 y etiquetas Las Canteras/HT3 (pp.1–2), canales de energía directa/reversa (p.11) e integración de 15 minutos (p.12). No demuestra la orientación física de los transformadores de corriente en 2024 ni explica G_C. Hasta resolverlo, HT3 debe permanecer como canal separado de diagnóstico; no integra una medida principal de carga IT. El documento contiene configuración técnica ajena al análisis, que no se replica en los productos del artículo.

## Dataluna / Tap Libertadores y límite retrospectivo

[Infotécnica subestación 2136](https://api-infotecnica.coordinador.cl/v1/subestaciones/2136/) identifica DATALUNA como propietario, código SE001T0043, S/E TAP OFF LIBERTADORES; [sus elementos](https://api-infotecnica.coordinador.cl/v1/subestaciones/2136/elementos/) identifican BA01T0043SE001T0043 (barra 2967, 110 kV BP1). La homologación 2024 une esta barra a TLIBERTADORES_110. El catálogo actual relaciona sockets TPLIBERT_110_H1_DLA y TPLIBERT_110_H2_DLA, filas 3452–3453, con Dataluna/Google y los clasifica de tránsito.

Esta prueba **no establece** que la columna agregada DATALUNA de Transferencia Norte 2020–2022 sea idéntica a la suma de estos sockets actuales ni que su primera aparición sea la inauguración del centro. La columna Norte está rotulada TAP LIBERTADORES 110, pero su celda de unidad está vacía y sus valores llevan signo. No transferir automáticamente unidades/sentido de otra zona, año o catálogo. Queda pendiente localizar diccionario histórico o regla oficial de agregación/convención de signo de esos libros. La continuidad y conciliación mensual que hizo la auditoría son necesarias, pero no sustituyen esa documentación.

## Decisión para el artículo

Se puede construir un panel descriptivo reproducible de carga HT1/HT2 y CMg Las Canteras con enlace oficial, y comparar diferenciales con referencias explícitas. Ya no hace falta presentar el precio de Canteras como candidato sin identidad. Deben separarse fases y fechas, conservar el quiebre metodológico del 15 de julio y la ambigüedad HT3, y no describir la carga como IA/GPU sin evidencia adicional. Estos datos no convierten por sí solos la entrada endógena de infraestructura en un experimento causal.
