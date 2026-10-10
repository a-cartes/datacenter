# Informe de avance: réplica base RM

Fecha: 2 de octubre de 2026. Pregunta: ¿cuál es el efecto causal de la entrada de centros de datos en la Región Metropolitana sobre el componente de los precios mayoristas asociado a congestión y pérdidas de transmisión?

## Respuesta en el estado actual

Con la estrategia del artículo y la medida chilena reconstruida, **no se obtiene un efecto robusto.** La especificación principal (distrito censal) da un ATT de Sun y Abraham de 1,32 USD/MWh (IC95 −0,02 a 2,67; p de aleatorización 0,35). El signo se invierte con fechas de entrada alternativas, con otras unidades y con controles menos expuestos. Además, se observan tendencias previas.

El diseño no sostiene una interpretación causal, por cuatro razones:

- Solo 2 a 4 tratamientos independientes (19 en Virginia).
- Fechas de entrada inciertas entre años.
- Controles conectados a la misma red de 110 kV, que se desacopla.
- Tratados periurbanos poco comparables con los controles.

## Verificado

| Tema | Evidencia |
|---|---|
| Identidad P = λ_s·FP y referencia Quillota 220 (FP = 1, subsistema principal) | Piloto dic-2017 y 15/07/2024 (VALIDACION_MEDIDA.md) |
| D = L + C exacto; equivalencia econométrica P/D con efectos de año | Piloto; coeficientes idénticos en todas las estimaciones |
| Desacople real en la RM (subsistema SD4, Cerro Navia 220/110 kV, C ≈ 25 USD/MWh) | Muestra del 15/07/2024 |
| Integridad de los originales | Hash de dic-2017 igual a la descarga propia; 18 meses modernos verificados por ETag; manifiesto con SHA-256 de 107 archivos |
| Continuidad entre regímenes | Convención horaria, identidad con la muestra oficial, universo de barras y nivel |
| Panel 2017–2025 sin faltantes de referencia | `datos/panel/` |
| Hitos fechados con fuente primaria | SONDA Q1 (04/04/2013), Google (ene 2015), Claro Liray (2013), Entel CdlV (2010), Ascenty Chile 1 (nov 2020), Kudos (dic 2020), Ascenty Chile 2 (jul–ago 2022), Ascenty SCL03 (28/08/2025), puesta en servicio de EdgeConneX 4.ª etapa (06/08/2024), ODATA ST02 (07/11/2023), Telefónica Paine (27/05/2016) |
| Data Center Map no sirve como historia en Chile | Instantáneas Wayback 2011–2024 |

## Provisional

- Fecha de primera operación de ODATA ST01 (may 2021 – nov 2023), EdgeConneX SCL01 (oct 2020 – ene 2021), Microsoft SCL03, Cirion SAN2 y Scala HB01.
- Coordenadas aproximadas: ODATA ST01 (±1–2 km), Longovilo (localidad) y geocodificaciones a nivel de calle.
- Asignación de barras a subestaciones por prefijo (132 códigos) y 235 códigos sin localizar, sobre todo derivaciones (TAP).
- Sustitución de covariables: no hay ingreso ni escolaridad por distrito.
- Exhaustividad del inventario de salas urbanas pequeñas y de centros corporativos que no pasaron por el SEA.

## Pendiente

1. Factores reales y antecedentes diarios posteriores al 15/07/2024, para L y C en 2024–2025 y para registrar desacoples. Requieren descarga manual: el portal bloquea el acceso automatizado.
2. Libros 2015–2016, para acercar la ventana a la del artículo (descarga manual).
3. Fechas primarias de operación de ODATA ST01 y de los sitios de Microsoft: memorias, declaraciones de entrada en operación o consultas a los operadores. Esto último requiere autorización del usuario; no se contactó a terceros.
4. Escolaridad del Censo 2017 por distrito, desde los microdatos de personas.
5. Decidir si se aborda alguna extensión (RESULTADOS_REPLICA.md). La de mayor valor parece un tratamiento por conexión eléctrica documentada y por intensidad.

## Archivos producidos en esta etapa

- **Documentos:** REGISTRO_DECISIONES, VALIDACION_MEDIDA, INVENTARIO_INSTALACIONES, UNIDADES_Y_PERIODO, PANEL_Y_VIABILIDAD, RESULTADOS_REPLICA, REPRODUCCION e INFORME_AVANCE. README actualizado.
- **Programas (26 archivos en `scripts/`):** ver REPRODUCCION.md y `scripts/ejecutar_todo.sh`.
- **Datos:**
  - Precios extraídos: 91 meses históricos y 18 modernos.
  - Diccionario y alias de barras, panel barra-mes y barra-año, unidades, covariables y muestras analíticas.
  - Inventario: instalaciones, hitos, fuentes, expedientes SEA y cartas.
- **Fuentes conservadas:** libros enlazados, TSV verificados, Infotécnica, fichas SEA, consultas SNIFA, cartas, páginas web, directorios, Wayback de Data Center Map y capas INE.
