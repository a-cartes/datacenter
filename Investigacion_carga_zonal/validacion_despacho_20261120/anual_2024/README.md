# Cobertura anual y localización de la carga en 2024

¿Qué tendría que ahorrar el refuerzo de Alto Jahuel–Lo Aguirre para justificar adelantarlo un año? La respuesta requiere comparar costos de despacho en dos redes. Antes de cambiar la red, reconstruimos dos referencias que el modelo debe poder reproducir: el presupuesto operativo programado en el SEN y la diferencia de precio entre ambas ubicaciones a lo largo del año.

## Localización en las 8.784 horas de 2024

Agregamos el costo marginal del [panel barra–mes](../../../SOCHER_2026_RM/datos/panel/barra_mes.parquet) para AJAHUEL_______500 y LO_AGUIRRE____500. La brecha Lo Aguirre menos Alto Jahuel alcanzó **+0,748 USD/MWh en el año**, con **−7,897 en abril**, **−4,101 en mayo**, **+9,091 en octubre** y **+5,910 en noviembre**. El promedio de octubre supera doce veces el promedio anual. Se trata aquí de todas las horas, mientras que los 57,17 USD/MWh del piloto corresponden únicamente a las horas completas con control de transferencia en octubre.

El panel tiene dos registros por barra en julio debido al cambio de formato de origen (336 y 408 horas). En abril cuenta la hora repetida (721). En septiembre incluye cuatro cuartos de hora a precio cero durante la hora local inexistente del 8 de septiembre en ambos nodos. Verificamos la planilla definitiva y usamos 719 horas físicas en septiembre. La suma anual de precios queda intacta y el denominador pasa de 8.785 a 8.784. [Fuente del 8 de septiembre](https://www.coordinador.cl/wp-content/uploads/2024/09/Antecedentes_CMG_Real_def_240908.zip) · [Doce resultados mensuales](localizacion.csv)

Para una carga plana valorada al costo marginal histórico, la ubicación en Lo Aguirre aumenta la valoración spot anual respecto de Alto Jahuel en **USD 131.417, 328.542 y 657.084** para 20, 50 y 100 MW. Esta cuenta mantiene fijos todos los precios. Una carga de ese tamaño puede modificar el despacho y corresponder a un contrato con un precio diferente. Para estimar el ahorro operativo de la obra se necesita reoptimizar ambas redes.

## Costo base oficial con una muestra de los doce meses

Dividimos cada mes en cuatro grupos consecutivos de días de tamaños tan iguales como permite el calendario. Sorteamos dos fechas sin reemplazo dentro de cada grupo, con dos secuencias seudoaleatorias reproducibles, independientemente de precios o restricciones. Esto produce 96 días, 48 estratos y ponderadores que suman 366 días. El diseño representa el calendario de 2024. El análisis de hidrologías distintas requiere escenarios adicionales. Para cada fecha usamos las 24 columnas horarias de la primera jornada del PRG del Coordinador y verificamos fecha, etiquetas de períodos y suma contra el total diario de costos de operación y encendido/detención. Cada archivo figura con URL y SHA-256. Son programas diarios publicados en la versión indicada en el manifiesto. Pueden existir revisiones posteriores.

El costo total programado estimado para el año asciende a **USD 1.498,01 millones**, con error estándar de diseño de **USD 23,57 millones**. Calculamos el total sumando, para cada estrato, el número de días por el costo medio de los dos días seleccionados. La varianza de cada total estratificado se estima como N² × (1 − 2/N) × s² / 2, donde s² es la varianza muestral entre los dos costos diarios. Las varianzas se suman sobre estratos.

El error estándar mide incertidumbre por muestreo de fechas, condicional a 2024 y a los archivos utilizados. Los costos reales realizados o el efecto del refuerzo requieren su propia medición. Para valorar la inversión, usar los mismos días en todas las corridas y calcular el error estándar de las *diferencias diarias pareadas*. Si el intervalo de esas diferencias abarca el umbral de decisión, ampliar hasta los 366 días. El período de calentamiento anterior a cada fecha y el estado inicial de embalses, baterías y unidades deben ser comunes a los escenarios. [Fechas y programas originales](programas.csv) · [Contribuciones por estrato](estratos.csv)

## Umbral financiero y decisión contrafactual

La inversión adjudicada de referencia para el conjunto de obras es USD 40.980.000 y el costo anual de operación, mantenimiento y administración USD 655.680. Suponiendo desembolso al habilitar, adelanto de un año, trayectorias posteriores idénticas y sin diferencia terminal, el umbral al final del año es inversión por tasa más el costo de operación adicional. Al inicio se descuenta dividiendo por uno más la tasa.

| Tasa ilustrativa | Umbral al inicio (USD) | Umbral al cierre (USD) |
|---|---:|---:|
| 5 % | 2.575.886 | 2.704.680 |
| 7 % | 3.293.720 | 3.524.280 |
| 10 % | 4.321.527 | 4.753.680 |

Para adelantar una etapa individual se requieren sus desembolsos evitables y su costo operativo incremental. Una parte de la obra podría estar ya ejecutada. [Sensibilidad por tasa y carga](sensibilidad.csv) · [Antecedentes de la adjudicación](../validacion_verano/README.md)

Para cada representación de la red, comparar el costo de operar sin y con el refuerzo para siete condiciones: cero carga nueva y 20, 50 y 100 MW adicionales en cada uno de los dos nodos. Son 28 celdas por supuesto de capacidad reforzada contando las dos redes y las dos representaciones. B(L) es el ahorro de operación producido por la obra con esa carga instalada. B(0) mide el beneficio que la obra entregaría de todos modos. Publicar B(L), B(0), la diferencia y si adelantar cruza el umbral financiero. El efecto de usar una u otra representación es la diferencia entre sus respectivos B(L), manteniendo todos los otros insumos comparables, incluida la información disponible al momento de decidir.

**Capacidad efectiva pendiente.** El Coordinador identifica una limitación asociada a transformadores de corriente en situaciones con altas transferencias desde el sur. El programa de octubre fija 1.660 MW en el corredor. Los anexos técnicos posteriores informan capacidades por equipo en MVA, y el análisis de seguridad operacional incluye el 1 de febrero de 2027 como fecha prevista para la etapa 3. Esos antecedentes permiten identificar la obra y el mecanismo. Para parametrizar la red reforzada hacen falta límites seguros en MW por estado y dirección, contingencia determinante, topología habilitada y respaldo de la fecha de servicio. El límite bajo operación observada debe validarse con consignas o estudios independientes: imponer como capacidad el flujo medido ajustaría la red al resultado que se intenta explicar. El error residual del programa intradiario también puede incorporar diferencias en costos, disponibilidades y demanda. La tasa de descuento actúa sobre la decisión financiera, sin requerir repetir el despacho físico.

[Informe del Coordinador sobre limitaciones de equipos](https://www.coordinador.cl/wp-content/uploads/2023/12/Requerimientos-Mejoras-Instalaciones-Transmision-2023_Informe-Final.pdf) · [Anexos ERST 2025](https://www.coordinador.cl/wp-content/uploads/2026/02/Informe-Preliminar-ERST-2025-Anexos.pdf) · [Calendario utilizado en análisis de seguridad](https://cartas.coordinador.cl/download_anexos/69a6cd6b356357194016ea0c/1)

## Reproducción

Ejecutar desde esta carpeta con Python 3.11 o posterior, pandas, NumPy, openpyxl y pyarrow.

```bash
python anual.py ../../../SOCHER_2026_RM/datos/panel/barra_mes.parquet
python muestra.py
python prg.py
python estimar.py
```

SHA-256 del panel: 5d96fd413a13cec2f149d337cedbeb43ff3bb53c39cdb313cc586e9ef4f743bb. SHA-256 del archivo de septiembre: b559a55eede8129a04c319b069dff4370f93d0a4734609c0d227c6a4ef67b563. Los datos de la red reforzada y los ahorros de despacho siguen abiertos.
