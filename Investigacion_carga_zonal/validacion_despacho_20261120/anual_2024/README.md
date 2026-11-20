# Cobertura anual y localización de la carga en 2024

¿Qué tendría que ahorrar el refuerzo de Alto Jahuel–Lo Aguirre para justificar adelantarlo un año? La respuesta requiere comparar costos de despacho en dos redes. Antes de cambiar la red, reconstruimos dos referencias que el modelo debe poder reproducir: el presupuesto operativo programado en el SEN y la diferencia de precio entre ambas ubicaciones a lo largo del año.

## Localización en las 8.784 horas de 2024

Agregamos el costo marginal del [panel barra–mes](../../../SOCHER_2026_RM/datos/panel/barra_mes.parquet) para AJAHUEL_______500 y LO_AGUIRRE____500. La brecha Lo Aguirre menos Alto Jahuel alcanzó **+0,748 USD/MWh en el año**, con **−7,897 en abril**, **−4,101 en mayo**, **+9,091 en octubre** y **+5,910 en noviembre**. El promedio de octubre supera doce veces el promedio anual. Se trata aquí de todas las horas, mientras que los 57,17 USD/MWh del piloto corresponden únicamente a las horas completas con control de transferencia en octubre.

El panel tiene dos registros por barra en julio debido al cambio de formato de origen (336 y 408 horas). En abril cuenta la hora repetida (721). En septiembre incluye cuatro cuartos de hora a precio cero durante la hora local inexistente del 8 de septiembre en ambos nodos. Verificamos la planilla definitiva y usamos 719 horas físicas en septiembre. La suma anual de precios queda intacta y el denominador pasa de 8.785 a 8.784. [Fuente del 8 de septiembre](https://www.coordinador.cl/wp-content/uploads/2024/09/Antecedentes_CMG_Real_def_240908.zip) · [Doce resultados mensuales](localizacion.csv)

Para una carga plana valorada al costo marginal histórico, la ubicación en Lo Aguirre aumenta el costo anual de compra a precios spot históricos respecto de Alto Jahuel en **USD 131.417, 328.542 y 657.084** para 20, 50 y 100 MW. Esta cuenta mantiene fijos todos los precios. Una carga de ese tamaño puede modificar el despacho y corresponder a un contrato con un precio diferente. Para estimar el ahorro operativo de la obra se necesita reoptimizar ambas redes.

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

Para adelantar una etapa individual se requieren sus desembolsos evitables y su costo operativo incremental. El informe de diciembre de 2025 del Coordinador confirma que las etapas 1 y 2 ya estaban en servicio a la fecha del informe. Por tanto, en una decisión posterior sobre la etapa 3 corresponde usar el costo y el cronograma remanentes. [Informe final del Coordinador de 2025](https://www.coordinador.cl/wp-content/uploads/2025/12/Requerimientos-Mejoras-Instalaciones-Transmision-2025_Version-Final.pdf) [Sensibilidad por tasa y carga](sensibilidad.csv) · [Antecedentes de la adjudicación](../validacion_verano/README.md)

Para cada representación de la red, comparar el costo de operar sin y con el refuerzo para siete condiciones: cero carga nueva y 20, 50 y 100 MW adicionales en cada uno de los dos nodos. Son 28 celdas por supuesto de capacidad reforzada contando las dos redes y las dos representaciones. B(L) es el ahorro de operación producido por la obra con esa carga instalada. B(0) mide el beneficio que la obra entregaría de todos modos. Publicar B(L), B(0), la diferencia y si adelantar cruza el umbral financiero. El efecto de usar una u otra representación es la diferencia entre sus respectivos B(L), manteniendo todos los otros insumos comparables, incluida la información disponible al momento de decidir.

**Capacidad efectiva pendiente.** El Coordinador identifica una limitación asociada a transformadores de corriente en situaciones con altas transferencias desde el sur. El programa de octubre fija 1.660 MW en el corredor. Los anexos técnicos posteriores informan capacidades por equipo en MVA, y el análisis de seguridad operacional incluye el 1 de febrero de 2027 como fecha prevista para la etapa 3. Esos antecedentes permiten identificar la obra y el mecanismo. Para parametrizar la red reforzada hacen falta límites seguros en MW por estado y dirección, contingencia determinante, topología habilitada y respaldo de la fecha de servicio. El límite bajo operación observada debe validarse con consignas o estudios independientes: imponer como capacidad el flujo medido ajustaría la red al resultado que se intenta explicar. El error residual del programa intradiario también puede incorporar diferencias en costos, disponibilidades y demanda. La tasa de descuento actúa sobre la decisión financiera, sin requerir repetir el despacho físico.

[Informe del Coordinador sobre limitaciones de equipos](https://www.coordinador.cl/wp-content/uploads/2023/12/Requerimientos-Mejoras-Instalaciones-Transmision-2023_Informe-Final.pdf) · [Anexos ERST 2025](https://www.coordinador.cl/wp-content/uploads/2026/02/Informe-Preliminar-ERST-2025-Anexos.pdf) · [Calendario utilizado en análisis de seguridad](https://cartas.coordinador.cl/download_anexos/69a6cd6b356357194016ea0c/1)

## Revisión económica de la capacidad de equilibrio

La pregunta para la inversión es cuánto reduce la obra el costo de abastecer el sistema, dados el estado de los embalses, la operación de las unidades y la ubicación de la demanda. La siguiente cuenta permite dimensionar esa pregunta con precios históricos.

| Período | Horas | Suma de brechas horarias positivas × 1 hora (USD por MW) | Capacidad equivalente al umbral del proyecto completo al 7 % |
|---|---:|---:|---:|
| Octubre | 744 | 6.763,47 | 521,08 MW |
| Noviembre | 720 | 4.254,86 | — |
| Octubre y noviembre | 1.464 | 11.018,32 | 319,86 MW |

Se verificaron las 720 horas de noviembre en los 30 archivos diarios definitivos. En ambos meses la brecha horaria mínima fue cero. En octubre, las 98 horas completas de control aportaron 5.602,20 USD/MW (82,83 % de la suma). Las transiciones aportaron 1.014,38 y las horas sin marca, 146,88. Usando solo las 98 horas, la capacidad equivalente sube a 629,09 MW. Los cocientes usan USD 3.524.280 al cierre del año y mantienen las brechas de precio fijas.

**Cuándo sería una cota.** En un despacho convexo que solo relaja el lado derecho de una restricción de capacidad, el ahorro para un aumento finito está acotado superiormente por el precio sombra inicial de esa restricción multiplicado por el aumento. En un modelo de dos nodos sin pérdidas con una sola interconexión, la brecha positiva puede coincidir con ese precio sombra direccional. En el SEN, pérdidas, rutas paralelas y otras restricciones también separan los precios. Una obra puede cambiar impedancias, topología y varias restricciones simultáneamente. Por ello, 320 MW dimensiona una hipótesis a precios fijos: no establece una cota empírica ni una capacidad suficiente para rentabilizar la etapa 3. Incluso bajo la aproximación convexa ideal, alcanzar el umbral con la tangente sería una condición necesaria para cubrirlo usando solo esos meses, no suficiente. Para una decisión sobre la etapa 3 se requiere además el costo de anticipar **esa etapa**.

**Flujos y precios.** La suma horaria de flujo enviado × brecha da USD 10.677.404 en octubre. Valorando por separado la energía recibida al precio de Lo Aguirre y la enviada al de Alto Jahuel, la diferencia es USD 10.527.395. Ambas usan medias horarias y flujos con signo. Son indicadores contables del corredor. Ni la renta atribuible a una restricción concreta ni una liquidación oficial se identifican con esos productos. Una liquidación a 15 minutos requeriría multiplicar antes de agregar. En abril la brecha media fue negativa: en promedio el MWh marginal era más barato en Lo Aguirre. Una restricción aislada en el sentido Alto Jahuel → Lo Aguirre no explica ese signo. Para distinguir flujo inverso, pérdidas u otras restricciones se deben cruzar las horas negativas con mediciones de flujo, bitácoras direccionales y precios sombra. La media mensual no permite adjudicar la causa.

**Precisión para decidir.** El umbral al 7 % representa 0,235 % del costo programado anual. El error estándar del nivel equivale a 6,69 veces el umbral. Con dos días por estrato, la aproximación t de Welch–Satterthwaite aplicada a las contribuciones de varianza del nivel da 4,41 grados efectivos y un intervalo de 95 % aproximado de USD 1.434,92–1.561,10 millones. Esta aproximación es sensible a la dispersión estimada con dos días. Para B(L) se repite el cálculo sobre diferencias diarias pareadas, que tienen su propia varianza y grados de libertad. El pareo reduce el error cuando los costos en ambas redes covarían, pero el sesgo estructural diferencial requiere validación separada. Los +322 MW de error de flujo en octubre justifican probar la sensibilidad de B(L) al modelado de la red; por sí solos no determinan ni el signo ni los dólares de ese sesgo.

**Diseño para el despacho.** Mantener la muestra original como referencia. Para un nuevo diseño, etiquetar el marco completo de fechas con hora y dirección de control, transiciones e hidrología. Con una corrida piloto estimar la desviación de la *diferencia de costos diaria* en cada estrato. A igualdad de costos de simulación, la asignación de Neyman es proporcional al tamaño del estrato multiplicado por esa desviación. Conservar probabilidad positiva para días sin marca, registrar pesos de inclusión y reservar fechas independientes para validar. La concentración observada en octubre–noviembre motiva estratificar; la dispersión del ahorro decidirá la asignación. Para valorar un año hidrotérmico, vincular el balance de los embalses entre períodos, mantener iguales estados iniciales y afluentes y usar un valor terminal comparable. Un horizonte móvil semanal o mensual con arrastre de estados permite contrastar la sensibilidad al horizonte diario. Los días muestrales sirven para medir diferencias dentro de trayectorias coherentes; tratarlos como días independientes con valores del agua fijos omitiría la reasignación intertemporal. Con una vida útil finita, incorporar el valor residual o el calendario de reemplazos en ambas alternativas. El umbral simplificado presupone que las diferencias posteriores al primer año se cancelan.

**Fundamento de carga.** Para Data Center Chile 2, una solicitud publicada por el Coordinador proyecta cerca de 1,5 MW iniciales y 20,4 MW finales. Para SCL4, la tabla 4-3 de Punta Verde consigna 50 MW en diciembre de 2027 y 150 MW en diciembre de 2028. Así, 20 y 50 MW tienen anclajes específicos, y 100 MW es una sensibilidad intermedia. Las fechas y potencias son proyecciones de solicitudes; estudiar la realización de demanda requiere retiros medidos. Las conexiones físicas y los perfiles horarios también deben modelarse para pasar de ubicaciones ilustrativas a instalaciones individuales. [Data Center Chile 2](https://www.coordinador.cl/wp-content/uploads/2025/01/Minuta_Solicitud_Nuevo_Transformador_para_Data_Center_Chile.pdf) · [SCL4, anexo 3](https://www.coordinador.cl/wp-content/uploads/2025/07/Minuta_Solicitud_Nueva_Subestacion_Seccionadora_Punta_Verde_110_kV-V2.pdf)

**Ubicación en la literatura.** Gonzales, Ito y Reguant (2023) estudian la integración de mercados y la inversión renovable en Chile. Davis y Hausman (2016) conectan una alteración de oferta con restricciones de transmisión y costos de redispatch. LaRiviere y Lyu (2022) estudian restricciones, renovables intermitentes y bienestar. Aquí el margen económico específico es la decisión de *cuándo* adelantar una etapa ante una nueva carga localizada, descontando el beneficio que existiría aun sin ella. [Econometrica](https://doi.org/10.3982/ECTA20769) · [AEJ: Applied Economics](https://doi.org/10.1257/app.20140473) · [JEEM](https://doi.org/10.1016/j.jeem.2022.102618)

Para reproducir esta revisión, desde anual_2024 ejecutar `python noviembre.py` y luego `python calculo.py` con pandas y SciPy. El primer script descarga los definitivos diarios y registra sus URL y SHA-256. El segundo contrasta ambas sumas mensuales con el panel anual y calcula los indicadores y el intervalo.

## Reproducción

Ejecutar desde esta carpeta con Python 3.11 o posterior, pandas, NumPy, openpyxl y pyarrow.

```bash
python anual.py ../../../SOCHER_2026_RM/datos/panel/barra_mes.parquet
python muestra.py
python prg.py
python estimar.py
```

SHA-256 del panel: 5d96fd413a13cec2f149d337cedbeb43ff3bb53c39cdb313cc586e9ef4f743bb. SHA-256 del archivo de septiembre: b559a55eede8129a04c319b069dff4370f93d0a4734609c0d227c6a4ef67b563. Los datos de la red reforzada y los ahorros de despacho siguen abiertos.
