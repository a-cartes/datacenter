# Inventario histórico de centros de datos en la Región Metropolitana

Fecha de corte: 2 de octubre de 2026. Datos: `datos/instalaciones/instalaciones.csv` (curado, una fila por instalación o etapa), `instalaciones_geo.csv` (con comuna y distrito asignados por polígono), `hitos.csv` (138 hitos fechados por separado) y `fuentes_instalaciones.csv` (65 fuentes; 63 archivadas localmente con SHA-256). Programas: `consultar_sea.py`, `fichas_sea.py`, `consultar_cartas_coordinador.py`, `candidatos_directorios.py`, `archivar_web.py`, `geolocalizar.py`, `hitos_instalaciones.py` y `registro_fuentes_instalaciones.py`.

## Método

1. **Universo de búsqueda.** Se combinaron directorios secundarios: DC Atlas (50 sitios en Chile), Inflect (43 en Santiago) y Data Center Map en Wayback Machine (2011–2024). Sus coordenadas y comunas no se aceptaron sin contraste. Hay errores visibles, como EdgeConneX en «Calle Larga», ODATA ST02 en «San Joaquín» o Claro Liray en «Coquimbo».
2. **SEA (e-SEIA).** Se hicieron 75 búsquedas por nombre y titular, que devolvieron 243 expedientes únicos; 35 son pertinentes. Cada ficha y su punto representativo se guardaron en `fuentes/instalaciones/sea/`. Las fichas permiten identificar titulares jurídicos, por ejemplo Inversiones y Servicios Dataluna (Google) o Lo Espejo Data Center SpA (ODATA ST02). También entregan fechas de ingreso y RCA, coordenadas y la conexión eléctrica prevista.
3. **Cartas del Coordinador.** El buscador público se consultó por razón social y por texto en cartas recibidas (2.445 cartas únicas). De ahí provienen las solicitudes de conexión, las declaraciones de puesta en servicio y las solicitudes de entrada en operación.
4. **SMA (SNIFA).** Se registró la fase de cada RCA. La fase no siempre está actualizada: ODATA ST01 figura «en construcción» aunque opera.
5. **Operadores y prensa.** Se archivaron comunicados, memorias y notas de prensa accesibles. Los medios protegidos por Cloudflare (DCD, Ascenty) quedaron fuera.

## Por qué Data Center Map no basta en Chile

El artículo usa Data Center Map. Sus instantáneas de Santiago listaban 2 centros en 2011, 7 en 2016, 11 en 2022 y 45 en 2024. Google Quilicura, SONDA, Claro Liray y EdgeConneX no aparecían antes de 2024. Usarlo como historia de exposición clasificaría como controles a comunas que ya tenían centros. La nota 2 del artículo reconoce que los años operativos son escasos en esa base; en Chile también lo es la cobertura de instalaciones.

## Instalaciones dedicadas y primera operación

| Campus | Comuna / distrito 2017 | Primera operación (intervalo) | Evidencia principal | Rol en el diseño |
|---|---|---|---|---|
| Entel Ciudad de los Valles (Equinix ST1/ST2; Data Center III) | Pudahuel / Pudahuel-7 | 2010 (ene–may) | Memoria Entel 2010; nota Entel 2020; RCA 155/2015 (edificio III) | Presencia previa |
| Entel Longovilo (Equinix ST4) | San Pedro | antes del 17/02/2017 | Uptime Institute 2017 | Presencia previa (coordenada aproximada) |
| Entel Amunátegui (ST3) | Santiago | antes de jul 2011 | Data Center Map 2011; Uptime 2017 | Presencia previa |
| HP → Telefónica / NextStream Paine | Paine | 2011 o antes | DIA de regularización (ago 2011); Telefónica 27/05/2016 | Presencia previa |
| Claro Liray | Colina / **Colina-1** | 2013 | La Tercera 2022; RCA 388/2012 | Presencia previa en Colina-1 |
| SONDA Quilicura Q1 (+ Kudos dic 2020) | Quilicura / Quilicura-3 | 04/04/2013 (inauguración) | Comunicados SONDA | Presencia previa |
| Google Quilicura (Data Center PARAM; S/E Los Libertadores 2020) | Quilicura / Quilicura-3 | ene 2015 | Google; SEA; carta DE03485-20 | Presencia previa |
| Ascenty Guacolda (Chile 1, 2 y 3) | Quilicura / Quilicura-3 | nov 2020 (Chile 1) | Developing Telecoms 2022; InvestChile 2019; Teletime 2025 | Entrada en unidad ya expuesta |
| EdgeConneX campus Colina (SCL01–04; S/E Las Canteras) | Colina / **Colina-3** | oct 2020 – 19/01/2021 | Comunicado EdgeConneX; SEA; cartas (puesta en servicio 4.ª etapa 06/08/2024) | **Primera entrada en Colina-3** |
| ODATA ST01 | Lampa / **Lampa-4** | may 2021 – nov 2023 (2022 probable, no verificado) | Portal Innova 2021; DataCentre Review 2023; carta DE02932-23 | **Primera entrada en Lampa y Lampa-4** |
| ODATA ST02 | San Bernardo / **San Bernardo-11** | 2023 (apertura anunciada el 07/11/2023) | DataCentre Review 2023; SEA; carta OP02215-26 | **Primera entrada en San Bernardo** |
| Microsoft SCL03 | Quilicura / Quilicura-3 | abr 2023 – jun 2025 (sitio no individualizado) | RCA 2023; Microsoft 19/06/2025 | Unidad ya expuesta |
| Cirion SAN2 | Quilicura / Quilicura-3 | 2025 o después (no verificado) | SEA; prensa (85% de avance) | Unidad ya expuesta |
| Scala Huechuraba HB01 | Huechuraba / Huechuraba-1 | 2025 o después (no verificado) | DIA de ampliación 2024 | Unidad ya expuesta (Cirion SAN1) |
| AWS Padre Hurtado / Huechuraba | Padre Hurtado; Huechuraba | no operan en 2025 (región prevista a fines de 2026) | SEA; InvestChile 2025 | Sin efecto en la ventana |
| Equinix ST5, Scala Lampa, Ascenty Data Hall | Pudahuel; Lampa; Quilicura | no operan en 2025 | SEA; SNIFA | Sin efecto en la ventana |
| Google Cerrillos, ODATA Santa Teresa, EdgeConneX SCL11, AWS Puente Alto | — | no construidos o desistidos | SEA; cartas | Sin efecto |

Además, el inventario contiene 26 salas urbanas (y varios campus antiguos) con fecha de inicio desconocida; 33 registros tienen solo cota superior (SONDA Teatinos, GTD, Claro Ciudad Empresarial y El Salto, Cirion SAN1, TIVIT, Kyndryl, NextStream Apoquindo y San Martín, IX de Recoleta, salas en Ñuñoa, Providencia, La Florida y Lo Barnechea, entre otros). En la mayoría solo se conoce una **cota superior**: el centro existía en la fecha del directorio. Las unidades que los contienen quedan como «previa» si la cota es anterior a 2019 o «incierta» si es posterior.

## Primera operación de una instalación frente a primera entrada en la unidad

- Ascenty (2020), Microsoft (2023–2025) y Cirion SAN2 (2025) entraron en Quilicura-3, donde SONDA operaba desde 2013 y Google desde 2015. No son primeras entradas.
- En Colina, el campus EdgeConneX está en el distrito 3 y Claro Liray en el distrito 1. EdgeConneX es primera entrada solo a escala distrital. A escala comunal, Colina queda con presencia previa.
- Las expansiones (SONDA Kudos, PARAM 2, Ascenty Chile 2 y 3, EdgeConneX SCL02–04, ST2 de Equinix, Claro 2023) y los cambios de titular (Entel → Equinix, HP → Telefónica → NextStream, ODATA → Aligned) no se codifican como entradas.

## Conexión eléctrica documentada

| Instalación | Conexión | Fuente |
|---|---|---|
| Ascenty Guacolda | Alimentadores en S/E Chacabuco (paños E53, E62–E65) | Cartas DE03899/3901/3895/3902-25, DE05568-25 y DE05659-26 |
| Microsoft SCL03 | Línea 2×110 kV a S/E Chacabuco y S/E propia de 26 MVA | Ficha SEA 2154183885 |
| Cirion SAN2; Scala2 | Nuevos alimentadores de 23 kV en S/E Quilicura | Cartas DE02793-24, DE01310-25 y DE06519-26 |
| EdgeConneX Colina | S/E Las Canteras (seccionadora de la línea 2×110 kV Cerro Navia–Las Vegas), en servicio en 2024 | SEA 2152964274; cartas NUP 3016, 3349 y 3975 |
| Google Quilicura | S/E Los Libertadores (NUP 341), en operación en 2020 | Cartas OP01036-20 y DE03485-20 |
| ODATA ST01 | Red pública para ST01; S/E interna prevista para la siguiente etapa | Ficha SEA 2147474024 |
| AWS Puente Alto (desistido) | S/E Bajos de Mena | Carta DE04810-22 |

La distancia a la subestación más cercana no se trata como conexión acreditada.

## Limitaciones

- Fechas de operación inciertas: ODATA ST01 (intervalo de 30 meses), el sitio de Microsoft, Cirion SAN2 y Scala HB01. El inicio de EdgeConneX SCL01 se apoya en el anuncio de enero de 2021.
- Faltan coordenadas en 12 sitios (Entel Pedro de Valdivia y Ñuñoa, TIVIT Alicanto y Santiago, GTD Panamericana, Kyndryl, Ufinet Magnus, PIT Chile y cuatro salas pequeñas de directorio). Sus comunas quedan como de historia incierta en el análisis por distrito y por nodo.
- La búsqueda sin resultados no prueba ausencia: centros corporativos o bancarios que no requieren SEA pueden faltar.
- No se obtuvo demanda medida por instalación. Potencias, MVA y MW TI son capacidades declaradas.
