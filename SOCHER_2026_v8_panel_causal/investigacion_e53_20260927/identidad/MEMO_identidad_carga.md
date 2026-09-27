# Identidad y naturaleza de la carga Ascenty E53

Revisión: 27 de septiembre de 2026. Investigación de fuentes públicas primarias, acotada a identidad de fases, suministro previo y naturaleza del NUP5417. No se editaron archivos v0.2.0, matriz v8, configuración causal ni Git. Los códigos E53I se resuelven en `catalogo_fuentes_identidad.csv`; S001/S002/S003 son fuentes ya preservadas en `../../eventos/catalogo_fuentes.csv`.

**Resultado: se cierra el suministro territorial anterior del campus y la identidad ambiental de Chile 2, pero no la equivalencia E53-fase ni la demanda neta incremental.** Hay evidencia expresa de una alimentación Ascenty anterior a mayo de 2025. La conexión E53 permanece elegible para descripción de un hito de infraestructura; no queda habilitada como primera entrada de campus o shock de nueva demanda.

| Evidencia | Certeza que aporta | Lo que no establece |
|---|---|---|
| RCA 486, pp. 3 y 16 | Chile 2 es etapa 3 ambiental; suministro anterior Enel en Unidad 2 y nuevo punto previsto en Unidad 3 | Equivalencia comercial SCL03 o conexión E53 |
| EAF 456/2024 y EAF 089/2025 | Carga Ascenty observada antes de mayo de 2025 | Balance neto de ampliación o transferencia |
| S003 ya conservada | E53 energizado el 5 de mayo de 2025 | Fecha de nueva demanda efectiva |
| CNE Res. 190 y minuta Chile 2 | Proyecto T10 justificado por trayectoria de nueva demanda | Ejecución T10 ni identidad con E53 |
| Certificado TIA SCL03 | Instalación construida en Guacolda, certificada en agosto de 2025 | Primera operación ni punto de suministro |
| Anexos S001/S002 | Ambos enlaces públicos expiraron al consultarlos | Contenido de los anexos ni ausencia de una equivalencia en ellos |

## Identidad que sí se puede registrar

1. **Data Center Chile 2 es la etapa 3 ambiental.** El original SEA de RCA 486/2021, p. 3, distingue la etapa 1 no ingresada al SEIA, la etapa 2 amparada por RCA 113/2021 y Chile 2 como etapa 3, jurídicamente independiente de las anteriores. La numeración no coincide necesariamente con los nombres comerciales SCL01/SCL02/SCL03. [Original SEA, p. 3](https://firma.sea.gob.cl/publicaciones/2b/80/2152538781).
2. **Ya había un suministro Enel al complejo anterior.** La RCA p. 16, sección 4.4.2 Energía, describe una instalación realizada por Enel Distribución: alimentador de 23 kV desde Chacabuco a Guacolda 2100 lote PC-9, sala de transferencia ENEL Chile 1 situada en Unidad 2 del Condominio Industrial Kúrcula. Para Chile 2 se proyecta otra acometida, sala ENEL Chile 2, en Unidad 3; cada data center tiene su sala. Esto documenta el suministro anterior y la separación física prevista, sin fechar realización de la nueva sala. [Original SEA, p. 16](https://firma.sea.gob.cl/publicaciones/2b/80/2152538781).
3. **La obra T10 pertenece documentalmente a ese proyecto ambiental.** CNE Res. 190 de 17 de abril de 2025, p. 2, liga el nuevo transformador de 110/23 kV de 40 MVA con Chile 2 y RCA 486, y recoge una trayectoria proyectada de 1,5 MW en 2025 a 20,4 MW en 2031. La p. 4 contempla una futura interconexión de su barra de 23 kV con la barra del T7. Esa relación futura no prueba que E53 alimente Chile 2. [CNE Res. 190](https://www.coordinador.cl/wp-content/uploads/2025/04/OP00973-25.pdf).
4. **SCL03 construido en Guacolda está acreditado, sin equivalencia eléctrica.** Certificado EPI publicado por TIA identifica DC SCL03, Ascenty Chile, Guacolda 2100, instalación construida con certificación inicial de 21 de agosto de 2025. Ni esa fecha ni el anuncio corporativo de inauguración se convierten en PES de E53. [Certificado](https://tiaonline.org/wp-content/uploads/2025/08/Chile_Ascenty-DC-SCL03_DCCC-epi_TIA942CL250821001-Signed.pdf).

## Demanda anterior observada

Dos informes oficiales de falla documentan carga en un alimentador Ascenty en Chacabuco antes de E53:

| Fecha/etiqueta local de la fuente | Carga desconectada | Clientes | Fuente |
|---|---:|---:|---|
|29 de agosto de 2024, 04:14|3,429 MW|2|EAF456/2024,p. 144, informe Enel sección 6; agregado CEN p. 4 redondea 3,43 MW|
|25 de febrero de 2025, 15:16|5,82 MW|2|EAF089/2025,p. 64; fecha de falla en p. 1|

Se comprobó visualmente cada fila. [EAF456](https://www.coordinador.cl/wp-content/uploads/2024/09/EAF-456-2024.pdf); [EAF089](https://www.coordinador.cl/wp-content/uploads/2025/03/EAF-089-2025.pdf). Son instantáneas de consumo afectado, no una curva de carga, ni consumos por edificio. Los dos clientes no se cuentan como dos centros o intervenciones. No se calcula diferencia incremental entre estas instantáneas, no se infiere UTC y no se adjudican al E53 posterior. Esto descarta interpretar el 5 de mayo de 2025 como primera aparición de cualquier demanda Ascenty en Chacabuco, pero no descarta una ampliación neta ese día.

## Qué queda abierto

S001 declara intención de iniciar un proyecto y prevé 8,37 MW, mientras S003 acredita energización y explotación el 5 de mayo de 2025. No se halló un documento primario que una E53 con una sala/fase concreta, identifique un medidor nuevo o indique retirada/traspaso de una alimentación anterior. Tampoco se halló balance antes/después para distinguir adición neta, transferencia o uso redundante. No se suman 1,5 MW, 8,37 MW y 20,4 MW: son proyecciones de distinto alcance y horizonte.

Los enlaces SharePoint de anexos de S001 y S002 se probaron anónimamente y ambos responden **«El vínculo ha expirado»**. `accesos_anexos.json` conserva URL, fecha, estado y mensaje. No se utilizó autenticación ni se contactó a terceros. La brecha es específica: informe descriptivo/formulario de conexión E53, plano de llegada a sala de transferencia y retiros de todos los puntos del campus. El plano público aguas arriba ya conservado en v8 no identifica la carga final.

Se buscaron combinaciones de Ascenty/E53/NUP5417, Chacabuco, Guacolda, Chile 2, traslado y transferencia en CEN, Enel, SEA y sitio corporativo. Las búsquedas sin resultado no se convierten en prueba de ausencia. No se usaron perfiles personales, prensa ni coincidencias de dirección para inferir la equivalencia pendiente.

## Implicación para el artículo

La unidad de intervención defendible sigue siendo **conexión E53 de naturaleza incremental no resuelta**. La historia del campus exige una variable de ampliación/transferencia y no un indicador absorbente de primera entrada en 2025. Mantener ese hito fuera del ATT de entrada mientras se estudia descriptivamente su ventana registrada.

El mecanismo tampoco obliga a esperar una gran diferencia de precios. La minuta CEN Chile 2 de enero de 2025, pp. 12-14, simula el proyecto de 20,4 MW para 2031 y no encuentra congestión en las líneas adyacentes en los escenarios considerados. Es una expectativa técnica modelada, con supuestos de red y Renca, y no un efecto empírico de 2025 ni una prueba sobre E53. [Minuta CEN](https://www.coordinador.cl/wp-content/uploads/2025/01/Minuta_Solicitud_Nuevo_Transformador_para_Data_Center_Chile.pdf).

## Calidad y reproducción

`descargar_identidad.py` descarga únicamente originales pertinentes y calcula SHA256. `construir_registro.py` reproduce catálogo, 12 hechos, 2 instantáneas y extractos de páginas sin red. Los PDF nuevos disponibles son 7; 3 fuentes adicionales quedaron registradas como no descargadas (MMA: cadena TLS no validable; SEA/Cámara y Ascenty: HTTP 403). Sus lecturas web son apoyo, no originales locales. El archivo SEA servido contiene campos de plantilla en portada: el número/fecha se contrastaron con la minuta CEN p. 12 y la resolución MMA 122/2021 (vistos), que dicen 5 de julio de 2021. La Res. 190 p. 2 dice 5 de junio de 2021; se conserva esa discrepancia sin reproducirla como fecha ambiental correcta. [MMA122](https://airerm.mma.gob.cl/wp-content/uploads/2022/05/2021_RES.EX_.122_RCA-486-2021.pdf).

Revisión visual realizada: RCA pp. 3/16, CNE pp. 2/4, EAF456 p. 144, EAF089 p. 64 y certificado TIA p. 1. Los originales completos quedan preservados; los extractos de validación son auxiliares. Ninguno de los hechos registrados habilita automáticamente un comparador o exposición cero.
