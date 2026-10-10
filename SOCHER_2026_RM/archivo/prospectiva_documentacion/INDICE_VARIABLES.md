# Índice: qué archivo aporta cada variable del modelo

Rutas relativas a `prospectiva_2030/`. La CNE usa 24 bloques representativos por mes y el PLP recibido usa 10. Ambos son modelos por bloques; la correspondencia horaria del PLP no equivale a optimización cronológica horaria. Procedencia y hash de cada original: `fuentes/registro_fuentes.csv`.

Identificadores: los archivos de la CNE usan el nombre de barra OSE2000 (`BarNom`, p. ej. «Cerro Navia 110»); la previsión de demanda usa «punto de conexión» con otra grafía (p. ej. «Chacabuco 012»); Infotécnica usa `id` y nemotécnico. **No hay todavía tabla de correspondencia** entre ellos ni con los códigos del panel histórico.

## Demanda

| Variable | Archivo | Unidad y resolución | Notas |
|---|---|---|---|
| Demanda por barra, 2026-07 a 2037-03 | `extraidos/cne_pncp_2026_2/energia_barra_mes_bloque.parquet` | GWh por barra, mes y bloque | 960 barras; en 2030 solo 251 tienen demanda (está agregada) |
| Demanda máxima por barra | `extraidos/cne_pncp_2026_2/demanda_punta_barra.csv` | MW por barra, bloque y mes | Volcado de una tabla dinámica filtrada a 2027 |
| Clientes libres por cliente y punto de conexión, 2025–2045 | `extraidos/cne_prevision_demanda_2025_2045/clientes_libres_mensual.parquet` | MWh mensuales | `mwh` sin y `mwh_ee` con eficiencia energética; el modelo CNE usa `mwh_ee` |
| Ídem, resumen anual | `.../clientes_libres_anual.csv` | MWh anuales | |
| Regulados por subestación primaria, 2025–2045 | `.../regulados_se_primaria_mensual.parquet` | MWh mensuales | |
| Demanda total del SEN por año | `extraidos/cne_pncp_2026_2/tablas_informe/Tabla_1.csv` | GWh anuales | |
| Correspondencia hora–bloque | `.../tablas_informe/Tabla_2.csv` | hora del día → bloque, por mes | |
| Duración de bloques | `.../tablas_informe/Tabla_3-4.csv` | % del mes | |
| Escenarios bajo, medio y alto del Coordinador | `extraidos/texto/2511-C13-INF-DPR-01-V1-Proy_Dda_25-45.txt` | texto y figuras | Sin datos por barra |
| Demanda por barra del Coordinador PLP, 2030 | `extraidos/pet26/demanda_2030_PLP.csv` | MW y MWh por barra y bloque | Tres escenarios; conciliada con la salida oficial |
| Correspondencia horaria PLP | `fuentes/originales/pet26/CEN_PET26_BD_PLP/IPLP-PET26/IPLP-PET26/<escenario>/indhor.csv` | Calendario hora a bloque | No es simulación horaria independiente |

## Carga digital

| Variable | Archivo | Notas |
|---|---|---|
| Carga digital incluida en la base CNE, por cliente y punto | `extraidos/demanda_digital/clientes_digitales_cne_anual.csv` y `..._mensual.csv` | MWh y MW medios; columna `clase` separa operadores de carga mixta |
| Totales por clase y año | `extraidos/demanda_digital/resumen_digital_cne.csv` | |
| Proyectos por etapa (potencia, fecha, tipo de magnitud) | `extraidos/demanda_digital/proyectos_digitales_etapas.csv` | Curado; distingue MW de demanda, MVA de conexión y cifras de prensa; cada fila cita el pasaje |
| Inventario de instalaciones existentes | `../datos/instalaciones/instalaciones.csv` | Del proyecto; no se modificó |

## Generación

| Variable | Archivo | Unidad | Notas |
|---|---|---|---|
| Costos variables de centrales térmicas | `.../tablas_informe/Tabla_5.csv` | US$/MWh; combustible y consumo específico | 336 unidades |
| Precios de carbón, GNL y Brent | `.../tablas_informe/Tabla_6-7-8.csv` | proyección | |
| Disponibilidad de gas natural | `.../tablas_informe/Tabla_9.csv` | m³ | |
| Obras de generación comprometidas | `.../tablas_informe/Tabla_10.csv` | MW, fecha, barra | |
| Programa indicativo de generación y almacenamiento | `.../tablas_informe/Tabla_27.csv` | MW, fecha, barra | Desde 2031 |
| Cierre y reconversión de carbón | `.../tablas_informe/Tabla_12.csv` | fechas | |
| Disponibilidad eólica y solar | `.../tablas_informe/Tabla_15-16.csv`, `Tabla_17-18-19.csv` | factor por bloque y zona | |
| Costo de falla | `.../tablas_informe/Tabla_42.csv` | US$/MWh por profundidad | |
| Unidades existentes: potencia, mínimo técnico, subestación | `extraidos/infotecnica/fichas_largas_unidades-generadoras.parquet` | formato largo, un concepto por fila | 1.645 unidades; conserva estado de certificación |
| Escenarios de expansión del parque (PET 2026) | `extraidos/texto/Informe-Final-PET2026.txt` (tabla 3-1) | texto | |
| Disponibilidad y mantenimiento por central | Entradas PLP: `plpmance.dat`, `plpcenpmax.dat` | Por interpretar según formato PLP | Archivos recibidos |

## Hidrología y embalses

| Variable | Archivo | Notas |
|---|---|---|
| Energía afluente anual por año hidrológico | `.../tablas_informe/Gráfico_1-2.csv` | Agregada para el SEN |
| Cotas iniciales de embalses al 01-07-2026 | `.../tablas_informe/Tabla_13.csv` | |
| Descripción del tratamiento (34 hidrologías, OSE2000) | `extraidos/texto/CNE_ITD-PNCP-Jul-2026.txt` | texto |
| Afluentes, embalses y convenios | Entradas PLP: `plpaflce.dat`, `plpcnfce.dat`, `plpmanem.dat`, `plpfilemb.dat` y archivos de riego | Recibidos; 30 hidrologías declaradas; pendiente implementar restricciones |

## Transmisión

| Variable | Archivo | Notas |
|---|---|---|
| Secciones de línea existentes: kV, km, R, X, B, límite térmico | `extraidos/infotecnica/secciones_lineas.csv` | 2.915 secciones; MVA derivado de kV y kA; estados de certificación incluidos |
| Extremos de cada tramo | `extraidos/infotecnica/tramos_extremos.csv` | Texto (paño y subestación); falta convertir a nodo–rama |
| Transformadores: capacidad, impedancias | `extraidos/infotecnica/fichas_largas_transformadores-2d.parquet` | 2.111 equipos |
| Subestaciones y barras con coordenadas | `../datos/geo/` | Del proyecto |
| Indisponibilidad de transmisión | `.../tablas_informe/Tabla_21.csv` | |
| Red reducida PLP y cambios temporales | Entradas PLP: `plpcnfli.dat`, `mantlin.csv`; seis PFD en la base PowerFactory | 349 barras y 496 líneas PLP; PFD sin convertir |

## Almacenamiento

| Variable | Archivo | Notas |
|---|---|---|
| Proyectos comprometidos: potencia, capacidad, autonomía | `.../tablas_informe/Tabla_10.csv` | Formato «MW/MW/h» |
| Programa indicativo | `.../tablas_informe/Tabla_27.csv` | |
| Modelación y eficiencia de ciclo | `extraidos/texto/CNE_ITD-PNCP-Jul-2026.txt` | texto |
| Parámetros de baterías | Entradas PLP: `plpcenbat.dat` y `plpcnfce.dat` | Recibidos; pendiente implementar restricciones |

## Obras futuras y fechas

| Variable | Archivo | Notas |
|---|---|---|
| Obras críticas de la RM y sus fechas | `extraidos/obras/obras_criticas_rm.csv` | Curado; Punta Verde, Cerro Navia, HVDC, Lo Campino, Huechuraba, Enea |
| Obras de transmisión en construcción (SEN) | `.../tablas_informe/Tabla_11.csv` | 30 obras con fecha estimada |
| Obras propuestas PET 2026 y complemento | `extraidos/texto/Informe-Final-PET2026.txt`, `Informe-CPET26.txt` | Sin tabular; son propuestas, no obras decretadas |
| Plan de expansión CNE 2025 | `extraidos/texto/CNE_ITD-Plan-de-Expansion-de-la-Transmision-2025.txt` | Sin tabular |

## Resultados oficiales para contraste

| Variable | Archivo | Notas |
|---|---|---|
| Costo marginal esperado por barra, mes y bloque | `extraidos/cne_pncp_2026_2/cmg_barra_mes_bloque.parquet` | US$/MWh; 2030 completo; incluye Cerro Navia, El Salto, Polpaico, Lampa, Los Libertadores, Punta Verde |
| Costo marginal y demanda en Polpaico 220 kV | `.../tablas_informe/Tabla_28.csv` | mensual |
| Precios de nudo y factores de penalización | `.../tablas_informe/Tabla_31.csv`, `Tabla_38.csv` | |
| Precios históricos por barra | `../datos/panel/`, `../datos/precios_mod/` | Del proyecto; no se modificaron |
| Precios y demanda oficiales PLP 2030 | `extraidos/pet26/precios_demanda_oficiales_2030_PLP.csv` | 125.640 filas en tres escenarios; son resultados base, no efectos digitales |
| Otras salidas oficiales PLP | TAR original `OPLP-PET26.tar.gz`; índice `extraidos/pet26/inventario_resultados_PLP.csv` | Generación, flujos, embalses, costos y planos conservados en el archivo |

## Rutas de las entradas PLP

Los nombres de archivos PLP de este índice están dentro de `fuentes/originales/pet26/CEN_PET26_BD_PLP/IPLP-PET26/IPLP-PET26/<escenario>/`, con escenarios `PET26_E01_v19`, `PET26_E02_v19` y `PET26_E03_v19`. El inventario completo está en `extraidos/pet26/inventario_CEN_PET26_BD_PLP.csv`.
