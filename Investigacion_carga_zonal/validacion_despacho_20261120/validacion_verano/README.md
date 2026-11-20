# ¿Se repite en verano el error del programa de octubre?

El corredor Alto Jahuel–Lo Aguirre permite contrastar el flujo programado con el medido y distinguir las horas con control de transferencia documentado. El signo del error medio cambia entre octubre de 2024 y enero de 2025. El programa de octubre reproducido en dos formatos coincidía en 744 de 744 horas. Esa comprobación valida la extracción del programa. La exactitud frente a la operación se mide comparando con los medidores.

## Una prueba fuera de muestra

Se registraron el mes de prueba, la dirección del flujo y el umbral antes de calcular los resultados. Cada hora reúne cuatro intervalos de 15 minutos. Se suman los dos circuitos en el extremo de envío de Alto Jahuel. La brecha es el costo marginal de Lo Aguirre menos el de Alto Jahuel. Para comparar regímenes, se separan las horas con 60, entre 1 y 59, y cero minutos de control en esa dirección. [Protocolo](protocolo.md) · [Piloto de octubre](../octubre_2024/README.md)

| Indicador | Octubre 2024 | Enero 2025 |
|---|---:|---:|
| Horas con programa y medida | 744 | 744 |
| Error medio, programa menos medida (MW) | +321,73 | −36,90 |
| Error absoluto medio (MW) | 342,66 | 218,21 |
| Horas completas con control / parciales / sin marca | 98 / 39 / 607 | 5 / 2 / 737 |
| Brecha media con control completo (USD/MWh) | 57,17 | 10,81 |
| Brecha media sin marca (USD/MWh) | 0,24 | 0,15 |

En enero, las cinco horas completas con control pertenecen al 2 de enero. La media programada fue 112,36 MW y la medida 149,26 MW. El umbral de flujo **medido** fijado en octubre (1.404,50965625 MW) señaló las cinco horas con control y 19 de las 737 sin marca. En las 742 horas clasificables hubo 5 verdaderos positivos, 19 falsos positivos, 718 verdaderos negativos y 0 falsos negativos. Es una regla diagnóstica contemporánea, distinta de la alerta de congestión del programa. Las cinco horas representan un único episodio para la inferencia entre eventos. La coincidencia de signo en la brecha por estado permite una comparación descriptiva. Dos meses tampoco identifican un efecto estacional por sí solos.

## Qué cambió con la reprogramación de octubre

Se recuperaron 27 programas intradiarios (PID) en 20 fechas. Se asignó a cada hora la última revisión cuyo período de inicio ya había comenzado ese día. La comparación reconstruye vigencias declaradas ex post. Una prueba de predicción en tiempo real exigiría además las horas de publicación. Se dispone de una revisión para 307 horas y quedan 437 sin observación emparejada. Para cada hora cubierta se verificó la identidad entre el error diario, la corrección de programa (diario menos intradiario) y el error restante (intradiario menos medido).

| Muestra emparejada | Horas | Error medio diario (MW) | Error medio intradiario (MW) | Reducción del sesgo (MW) |
|---|---:|---:|---:|---:|
| Todas las horas con revisión | 307 | +382,19 | +375,37 | 6,82 aprox. |
| Falsos positivos del programa diario con revisión | 81 | +365,71 | +327,84 | 37,87 |

El error absoluto medio de las 307 horas pasó de 392,65 a 388,73 MW. De los 174 falsos positivos del programa diario frente a la bitácora, 81 tienen revisión y 93 carecen de ella. En esos 81, el límite declarado del corredor siguió en 1.660 MW. En 52 horas el flujo revisado quedó en ese límite y en 29 cayó por debajo. La bitácora identifica el control de transferencia registrado. Una hora sin marca puede tener otras restricciones.

Los insumos del modelo permiten distinguir mecanismos candidatos. En las 81 horas cambió la indisponibilidad declarada de al menos una unidad de generación. Cambió algún valor de demanda nodal en 9 horas y el campo de número de unidades de línea en 0. En las otras 226 horas con revisión, las cifras respectivas fueron 226, 7 y 0. Se compararon solo objetos presentes con valor en ambas bases, con tolerancia absoluta de 0,0001 en la unidad nativa. Un cambio de disponibilidad común a todas las horas tampoco explica por sí solo por qué algunas quedaron al límite. Para atribuir dólares o MW a cada mecanismo hacen falta corridas que sustituyan individual y conjuntamente demanda, disponibilidad y consigna, manteniendo los demás insumos fijos. Las diferencias entre los costos totales de dos programas publicados mezclan todos los cambios simultáneos.

## Obra real y umbral en dólares

La obra escogida es el aumento de capacidad de la línea 2×500 kV Alto Jahuel–Lo Aguirre y la ampliación en S/E Lo Aguirre. El Plan de Expansión 2018 especifica cambio de conductor para al menos 3.000 MVA por circuito a 35 °C con sol. Para simular la obra, hay que reconstruir la capacidad efectiva de transferencia con sus contingencias y las etapas que estaban en servicio en cada escenario. El dato de placa en MVA por circuito no determina por sí solo esa capacidad en MW. [Plan CNE, sección 3.1.7](https://www.cne.cl/wp-content/uploads/2018/01/Res-Ex-CNE-14-2019-ITF-Plan-Expansion-Anual-Tx-2018.pdf) · [Decreto 18, adjudicación, fila 22](https://www.bcn.cl/leychile/navegar?idNorma=1157657)

Como referencia reproducible, la adjudicación inicial arroja USD 40.980.000 de inversión y USD 655.680 anuales de operación, mantenimiento y administración. Con una tasa **ilustrativa** del 5 %, desembolso íntegro al habilitar y un año adicional de operación, adelantar un año todo el proyecto cuesta en valor presente (40.980.000 × 0,05 + 655.680) / 1,05 = **USD 2.575.886** al comienzo del año. El umbral equivalente al cierre es **USD 2.704.680**. Se supone idéntica trayectoria después del primer año, sin diferencias de valor residual. Los costos por etapa, el calendario real de desembolsos y el costo final requieren verificación. No se suma la anualidad regulada a la inversión porque duplicaría parte del costo.

| Nueva carga continua | MWh en 8.760 horas | Umbral al cierre dividido por la energía de la carga (USD/MWh) |
|---|---:|---:|
| 20 MW | 175.200 | 15,44 |
| 50 MW | 438.000 | 6,18 |
| 100 MW | 876.000 | 3,09 |

La división solo expresa la escala del umbral. Para estimar el beneficio incremental asociado a un centro de datos hay que descontar lo que la obra ya ahorraría sin esa carga. Para cada perfil L, calcular el ahorro operativo B(L) = C(red sin refuerzo, L) − C(red reforzada, L), con los mismos combustibles, afluentes, disponibilidades y demanda de fondo. B(0) recoge el beneficio base y B(L) − B(0) el beneficio adicional atribuible a la carga dentro del modelo. Un caso de coordinación de inversiones ocurre cuando B(0) queda por debajo del costo de anticipar y B(L) lo supera, sobre el mismo horizonte y en la misma fecha monetaria. Conviene repetir el cálculo con restricciones del programa y restricciones operativas reconstruidas, y reportar si cambia la decisión. Quedan por verificar la fecha efectiva y el límite operativo por etapa y por ejecutar esas corridas. Ninguna de las cifras de la tabla representa ahorro simulado. Los dos meses no dan ponderaciones anuales defendibles.

## Reproducción y archivos

Los manifiestos incluyen la URL de cada archivo oficial y su SHA-256. Enero usa 31 planillas de programa diario, 31 archivos de costos marginales definitivos y el archivo mensual de medidores. Los ZIP originales no se duplican en el repositorio. Desde esta carpeta, guardar cada descarga en la ruta de la columna archivo de [fuentes.csv](fuentes.csv) y [fuentes_pid.csv](fuentes_pid.csv). Para octubre, descargar también las columnas zip de [fuentes_prg.csv](../octubre_2024/fuentes_prg.csv) y [fuentes_pcp.csv](../octubre_2024/fuentes_pcp.csv) en prg_octubre/DD.zip y bases_octubre/DD.zip, respectivamente, con DD de dos dígitos. Usar Python 3.11 o posterior con pandas, NumPy y openpyxl.

```sh
python validar.py .
python revisiones.py . prg_octubre ../octubre_2024
python insumos.py . bases_octubre
```

Resultados horarios con encabezados y hora local de inicio: [enero.csv.gz](enero.csv.gz), [revisiones_octubre.csv.gz](revisiones_octubre.csv.gz) y [cambios_insumos.csv.gz](cambios_insumos.csv.gz). Los costos de las planillas PRG/PID en el panel de revisiones están en miles de USD. Los campos vacíos en las horas sin PID conservan esa falta de cobertura.

[Continuación: cobertura anual, localización y sensibilidad financiera en 2024](../anual_2024/README.md)
