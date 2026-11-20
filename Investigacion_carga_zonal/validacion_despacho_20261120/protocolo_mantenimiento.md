# ¿Cuándo conviene adelantar una obra de transmisión ante una gran carga?

Protocolo prospectivo, versión 1 del 20 de noviembre de 2026. Corredor Alto Jahuel–Lo Aguirre, Chile. La decisión es adelantar un año la etapa 3 del NUP 1530. Primero se contrastará el despacho con dos ventanas de mantenimiento que aún requieren confirmación de ejecución. Luego se estimará el costo de operar el SEN bajo dos calendarios de obra. El análisis publicará también un resultado nulo, de signo inverso o incompatible con la decisión.

## 1. Qué se medirá y dónde

| Nivel | Dato o activo | Función en el artículo |
|---|---|---|
| 500 kV | C1 y C2 entre Alto Jahuel y Lo Aguirre. Brecha firmada = CMg Lo Aguirre menos CMg Alto Jahuel | Aquí cambia la red. Validar flujos y brechas en mantenimiento. La brecha de +0,748 USD/MWh en 2024 y los cocientes de 521/320 MW pertenecen a estos extremos. |
| 220 kV | Lo Aguirre frente a BP1 y BP2 de Alto Jahuel | Sensibilidad histórica del gasto de compra. A 50 MW planos, en 2024 el diferencial fue +USD 357.141 frente a BP1 y −USD 181.331 frente a BP2. |
| 110 kV | S/E Punta Verde, conexión proyectada de SCL4 al tramo Tap Libertadores–Las Canteras | Aquí se incorpora el retiro incremental del caso principal. La red debe representar la conexión, los transformadores y el camino hasta el corredor. Las fechas y potencias del expediente son escenarios. |

El DS 15T exige al menos 1.950 MVA por circuito a 35 °C con sol. La referencia previa del titular es 1.250 MVA por circuito. En octubre de 2024, la solución día-antes usó 1.660 MW para el corredor y el máximo medido de envío de los dos circuitos juntos fue 1.747,34 MW. Para obtener la capacidad segura se necesitan la topología, el sentido, la contingencia determinante y los límites aplicables a ese estado. [Decreto, art. 1](https://www.diariooficial.interior.gob.cl/publicaciones/2026/10/27/44584/01/2891196.pdf) · [Antecedente técnico del titular](https://cartas.coordinador.cl/show/6aecee7f35635758766e2efa) · [Resolución de Punta Verde](https://www.cne.cl/archivos_bajar/REX%20550-2025.PDF)

## 2. Ventanas, unidad de análisis y elegibilidad

| Aviso | Circuito solicitado fuera | Fechas solicitadas, inclusive, hora de Chile continental |
|---|---|---|
| 2026003217 | C2 | 30 de noviembre–8 de diciembre de 2026 |
| 2026003311 | C1 | 12–20 de diciembre de 2026 |

La carta del 16 de noviembre informa la suspensión del retiro de C1 antes previsto para ese día. La unidad es el intervalo físico de 15 minutos, identificado en UTC y presentado en America/Santiago. Confirmar apertura y reposición efectivas en registros del Coordinador y conciliar con el estado del circuito compañero y la medición por circuito en ambos extremos. Un flujo próximo a cero por sí solo deja el estado indeterminado. Conservar URL, versión y SHA-256 de cada fuente. [Carta OR-000322-2026](https://cartas.coordinador.cl/show/6afb99133563573c0aa47015)

Para la prueba principal admitir cuartos completos dentro de la ventana anunciada con un circuito fuera y el otro en servicio. Registrar aparte transiciones, estados desconocidos, datos faltantes, reposiciones intermedias y toda hora que se desplace fuera de las fechas previstas. Si se cancela una ventana, el cuadro mostrará cero observaciones para ese episodio. Inventariar maniobras concurrentes con sus marcas horarias. Mantenerlas en la comparación principal con la misma topología de fondo en las dos simulaciones y publicar como sensibilidad la exclusión de intervalos con otra maniobra documentada en el corredor o sus subestaciones terminales. Publicar exclusiones y cobertura por episodio, incluidos los intervalos perdidos por falta de salida de alguno de los modelos.

## 3. Contraste prospectivo del despacho

**Resultado primario.** En cada cuarto elegible se observará la brecha firmada de precios de 500 kV en USD/MWh. Para ese mismo cuarto se producirán dos predicciones con los mismos insumos y parámetros. Una representa el circuito efectivamente retirado y la otra mantiene ambos en servicio. Para cada episodio se calculará la media de |predicción con dos circuitos − observación| menos |predicción con uno − observación|. La estadística primaria es el promedio con igual peso de los dos episodios. Un valor positivo indica que representar la maniobra reduce el error. Se publicarán ambos componentes, sus signos, los conteos y el porcentaje de cobertura. Con un solo episodio se publica solo su resultado individual. Con ninguno la prueba queda sin observaciones.

La validación es **condicional** a demanda, afluentes, disponibilidades ajenas a la maniobra y topología de fondo realizados. El despacho y los precios se resuelven para cada topología. Los precios observados y el flujo realizado del enlace sirven exclusivamente para evaluar las predicciones. Los costos marginales de 500 kV archivados como cero en PLEXOS 2024 exigen contrastar el método de lectura o derivación del precio del modelo antes de la prueba. Si solo hay datos horarios del modelo, agregar los cuatro cuartos completos a la hora, informar resolución y presentar ese contraste como secundario. Evitar repetir una predicción horaria cuatro veces como si tuviera resolución de 15 minutos.

**Congelación del modelo.** Antes de la primera apertura y de consultar sus resultados, archivar el código ejecutable, parámetros, correspondencias de barras, reglas de disponibilidad y series de entrada conocidas, con hash y fecha verificable. Registrar por separado los insumos realizados que se incorporen después. Si el modelo queda congelado después de la primera apertura, etiquetar la evaluación de los datos ya observables como retrospectiva. El protocolo fechado por sí solo fija la pregunta y la métrica. Una enmienda debe conservar esta versión e indicar fecha, motivo y datos conocidos al modificarla.

**¿Cuánto varió la brecha observada?** Para cada cuarto tratado, usar como referencia el promedio de los cuartos de la misma hora y minuto local y del mismo tipo de día (hábil, sábado, domingo/festivo) entre el 2 y el 29 de noviembre de 2026 con dos circuitos confirmados. Excluir referencias con maniobras documentadas en el enlace. Informar cuartos sin par, número de días de referencia y la brecha tratada menos su referencia por episodio. Publicar además el cambio en la magnitud absoluta, el error de flujo en MW y resultados por sentido físico del flujo. El emparejamiento se define por calendario y topología, sin seleccionar por flujo o precios posteriores. La selección operativa del mantenimiento y los cambios de oferta o demanda limitan la atribución causal.

Mostrar diferencias por día, por episodio y al omitir un día a la vez. Dos episodios cercanos ofrecen poca información sobre la variación entre mantenimientos. Se evitará inferencia basada en cuartos independientes. Examinar por separado si un modelo mejora el flujo y empeora la brecha. Si los errores aumentan en un episodio, conservarlo y evaluar cuánto cambia la decisión con ambas representaciones de red.

## 4. Resultado económico del artículo

Comparar calendarios temprano y tardío con idéntica capacidad final, desplazando un año la disponibilidad y las intervenciones asociadas. Usar cronogramas verificables, documentar los intervalos de obra y el inicio efectivo de la habilitación. Resolver la red con capacidad segura por configuración y sentido. Un retiro temporal identifica una configuración con un circuito indisponible. Extrapolar al conductor reforzado exige sus parámetros, contingencias y restricciones de la red restante.

El resultado en dólares para carga L es **B(L) = VP[costo de operación con calendario tardío − costo de operación con calendario temprano]**. Incluir el redespacho durante los trabajos, combustible, arranques, detenciones y energía no servida valorada explícitamente si corresponde. Comparar trayectorias hidrotérmicas enlazadas con afluentes y estados iniciales comunes, valor terminal comparable y costos ponderados a las mismas fechas. Resolver el mismo perfil de carga bajo cada calendario. Repetir con la red del programa y con la representación operativa validada. Reportar B(0), B(L), B(L) − B(0) y la diferencia de valoración entre representaciones de red.

Para SCL4, el caso de expediente pasa a 50 MW en diciembre de 2027 y a 150 MW totales en diciembre de 2028. Si solo consta el mes, usar el día 1 local como convención de escenario. Comparar con la misma rampa desplazada un año y con una conexión hipotética en el extremo de Alto Jahuel, identificando explícitamente su barra. Usar perfiles planos mientras se desconozca el horario del cliente, y 20/100 MW como sensibilidades. Para otros puntos físicos se publicará su mapeo antes de correrlos. [Expediente de conexión, tabla 4-3](https://www.coordinador.cl/wp-content/uploads/2025/07/Minuta_Solicitud_Nueva_Subestacion_Seccionadora_Punta_Verde_110_kV-V2.pdf)

Definir K como el valor presente adicional de adelantar desembolsos y O&M **remanentes de la etapa 3**, incluyendo cualquier diferencia de reposición o valor residual. La carga cambia la decisión si B(0) < K < B(L). Si falta K, publicar el intervalo de K donde cambia la decisión y el máximo sobrecosto compatible con adelantar. El umbral ilustrativo de USD 3,52 millones al 7 % corresponde al proyecto completo y tiene otra base de costos. Presentar el costo de operación incremental y la sensibilidad al 5, 7 y 10 %. Mantener separados los pagos spot del cliente.

## 5. Organización del manuscrito

El cuerpo reunirá la decisión de calendario, la red y la conexión, la validación observada de los dos eventos y la tabla contrafactual en USD por barra y fecha. Los apéndices conservarán el estudio SOCHER y los pilotos de 2021 y Las Canteras como antecedentes, octubre de 2024 y enero de 2025 como diagnóstico del despacho, el contraste BP1/BP2 como sensibilidad y los manifiestos con el diseño de muestreo. Las celdas que requieren la ejecución de las ventanas o del modelo quedan pendientes.
