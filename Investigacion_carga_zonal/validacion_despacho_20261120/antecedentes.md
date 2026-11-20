# Centros de datos, precios eléctricos y oportunidad de los refuerzos de transmisión en Chile

**Documento consolidado para revisión económica · 20 de noviembre de 2026**

La pregunta del artículo es **cuánto cuesta abastecer una nueva carga eléctrica cuando el refuerzo de transmisión llega después de su conexión**. El proyecto comenzó midiendo cambios de precios tras la apertura de centros de datos en la Región Metropolitana. La evidencia reunida permite medir retiros y describir el comportamiento de los precios en horas concretas. El valor económico de adelantar una obra sigue pendiente de un modelo de despacho validado y una comparación entre fechas de inversión.

## Resultados para el revisor

| Ejercicio | Resultado observado | Alcance |
|---|---|---|
| DiD anual de SOCHER, 2017–2025 | +1,05 USD/MWh después de la apertura. En el año −2 ya aparece +2,05 frente al año −1. Al excluir La Vilana, el resultado posterior queda en +0,03. | La estimación depende de la trayectoria previa y de la composición de la muestra. |
| Maniobras de 2021 y estudio de eventos | Al excluir 113 horas completas con maniobras documentadas, la estimación posterior pasa a +0,72 y el contraste del año −2 a +1,67 USD/MWh. | El filtro muestra cuánto cambia el resultado al retirar esas horas. Persiste una diferencia previa a la entrada. |
| Interrupción de Las Canteras, 3 de diciembre de 2024 | El Coordinador registró 1,12 MW desconectados. Frente a 16 martes comparables, el retiro cae 1,23 MW y el diferencial respecto de Quillota cambia −0,25 USD/MWh. | La perturbación física es medible. Once martes tuvieron desviaciones de precio iguales o mayores. Ocho de diez horas tuvieron precios cero en ambas barras. |
| Reconstrucción de precios de agosto de 2021 | Agregar la bitácora de Polpaico–Lo Aguirre reduce el error absoluto medio de 19,31 a 17,43 USD/MWh al ajustar con julio. | La marca operativa aporta información sobre la brecha entre los controles y La Vilana. El precio y el flujo en los extremos del corredor requieren una validación física propia. |
| Control en Alto Jahuel–Lo Aguirre, octubre y noviembre de 2024 | En 741 horas de 35 fechas, el diferencial Las Canteras–Quillota es 0,61 USD/MWh mayor con control. Al comparar el mismo mes y la misma hora, la diferencia es −0,15. | El signo depende de las horas comparadas. Este ejercicio describe el régimen operativo y la composición horaria. |

**Interpretación para el artículo.** Los 11 de 16 martes constituyen un recuento descriptivo. La etiqueta de prorrata y los precios cero son compatibles con una respuesta pequeña del precio en esas horas. Estimar esa respuesta exige comparar cargas alternativas bajo las mismas condiciones. El siguiente contraste económico consiste en calcular cuánto reduce un refuerzo el costo de atender la carga adicional y luego valorar en el tiempo dos fechas factibles para la misma obra. Los escenarios de 20, 50 y 100 MW son supuestos de simulación.

## Preguntas que surgieron en SOCHER

**¿Qué variables eran dummy?** El costo marginal por barra y su diferencial respecto de Quillota son variables numéricas en USD/MWh. Las cinco covariables del emparejamiento son logaritmos o proporciones. Los años y sectores entran como categorías en los efectos fijos, y el estudio de eventos usa indicadores de cohorte y tiempo relativo a la apertura, con el año −1 como referencia. En el piloto de 2021 sí hay un indicador que toma el valor uno cuando una hora completa cae dentro de una ventana de maniobra documentada. Un cero en ese indicador significa que la hora quedó fuera de esas ventanas. La activación de otras restricciones sigue siendo posible.

**¿Qué agregaría un indicador de Navidad o Año Nuevo?** Distinguir día y noche permite comparar horarios. Un festivo permite preguntar si, por ejemplo, las 10 h de Navidad se comportan de forma diferente a las 10 h de fechas comparables. En una especificación con un efecto fijo por cada fecha, el nivel común del festivo ya está absorbido. Para estudiar si cambia el *perfil intradiario*, se podría interactuar el indicador de festivo con los bloques horarios. Los resultados reunidos aquí no estiman un efecto de los festivos ni suponen que el consumo deba aumentar.

**¿El cambio anterior a la apertura fue un shock o una política pública?** El gráfico muestra cuándo divergieron las trayectorias. La bitácora documenta una maniobra asociada al control de transferencias el 13 de agosto de 2021. Esa evidencia permite una prueba de sensibilidad con horas identificadas. La atribución de toda la divergencia previa a una falla, un apagón masivo o una política pública permanece abierta. [Gráfico original del estudio de eventos](https://github.com/a-cartes/datacenter/blob/69a68ee3ab015257b797579fd77cd1b71b2f200b/SOCHER_2026_RM/referencia/socher_20261005/figura_eventos.png) · [Datos del gráfico](https://github.com/a-cartes/datacenter/blob/69a68ee3ab015257b797579fd77cd1b71b2f200b/SOCHER_2026_RM/referencia/socher_20261005/figura_eventos_datos.csv)

**¿Qué aportaría un DiD sintético?** Permitiría comprobar si una combinación ponderada de sectores reproduce mejor la trayectoria previa del tratado. Para interpretar los resultados habría que revisar el ajuste anterior a cada apertura, cuánto depende de un control concreto y si los controles están expuestos a perturbaciones de red distintas. La comparación con Virginia y las objeciones del revisor se desarrollan en las secciones 1 y 2.

**¿Dónde entra la inteligencia artificial?** La expansión de la demanda de cómputo motiva la pregunta económica. Los datos observan retiro eléctrico del centro. La fracción de ese consumo dedicada a IA requeriría información sobre el uso de sus equipos. El estimando propuesto se expresa en MW de carga efectivamente conectada y en costo de abastecerla.

## Documentos y cálculos

Las secciones siguientes conservan la nota inicial, los dos comentarios de revisión y los dos informes empíricos. La secuencia permite ver qué se propuso antes de cada prueba y qué se obtuvo después.

- [1. Diseño presentado en SOCHER y comparación con Virginia](#socher)
- [2. Revisión económica del diseño original](#revision)
- [3. Resultados de Las Canteras y Polpaico–Lo Aguirre](#pilotos)
- [4. Evaluación recibida y propuesta de despacho](#hoja)
- [5. Validación horaria, cálculos y código reproducible](#horaria)

<a id="socher"></a>

## 1. Diseño presentado en SOCHER y comparación con Virginia

*La nota original presenta el diseño anual y las hipótesis que dieron origen a los pilotos.*

**Proyecto** · Centros de datos y costos marginales eléctricos en la Región Metropolitana de Chile  
**Propósito** · Evaluar si conviene fortalecer el diseño de diferencias en diferencias presentado en SOCHER o reorientar el artículo hacia el efecto de la carga eléctrica efectiva y su interacción con las restricciones de transmisión. La revista objetivo es *Energy Economics*.

### 1. La decisión de investigación

El enfoque original pregunta **qué cambió en el diferencial de costo marginal de un sector después de la primera apertura documentada de un centro de datos**. El enfoque propuesto pregunta **cuánto cambia el costo marginal cuando varía la carga efectiva de un centro de datos, y cómo depende ese efecto de la capacidad de la red**.

La distinción importa. Una apertura puede ir seguida de una incorporación gradual de carga. Además, más consumo puede elevar el costo total de abastecimiento con poco cambio en el costo marginal si la misma unidad sigue fijando el precio y la red tiene holgura. Si la carga activa una restricción o exige generación más cara, el efecto puede concentrarse en determinadas barras y horas. El signo y la magnitud del efecto sobre el diferencial nodal quedan como preguntas empíricas.

### 2. Enfoque original presentado en SOCHER

**Pregunta.** ¿Cuánto cambió el diferencial de costo marginal respecto de Quillota 220 kV tras la primera entrada documentada de un centro de datos en un sector censal de Santiago?

| Elemento | Diseño implementado |
|---|---|
| Datos y unidad de análisis | Costos marginales horarios por barra del Coordinador Eléctrico Nacional. Panel final de **21 sectores censales × 9 años**, con **189 observaciones únicas** entre 2017 y 2025. |
| Variable dependiente | Costo marginal de cada barra menos el de Quillota 220 kV en la misma hora, en USD/MWh. Se agrega por barra y año y luego por sector censal. La especificación principal admite barras con cobertura anual de al menos 90 %. |
| Tratamiento | Primera apertura documentada en Algarrobal, Colina (**2021**), La Vilana, Lampa (**2022**), y Chena, San Bernardo (**2023**). Las fechas de apertura, conexión de etapas y retiro efectivo pueden diferir. |
| Selección de controles | Probit con cinco características del Censo 2017. Se seleccionan diez vecinos por tratado, con reemplazo, lo que produce 18 controles distintos. Las covariables son los logaritmos de población y viviendas, las proporciones de población inmigrante y de pueblos originarios, y la materialidad aceptable de la vivienda. |
| Estimación | Diferencias en diferencias escalonadas de Sun y Abraham, con efectos fijos de sector y año y errores agrupados por sector. El estudio de eventos usa el año −1 como referencia. El resultado principal promedia 12 contrastes cohorte–año posteriores a la entrada. |

[Documentación metodológica y datos del proyecto SOCHER](https://github.com/a-cartes/datacenter/tree/main/SOCHER_2026_RM)

#### Resultado y problema de identificación

La estimación principal es **+1,05 USD/MWh** en el diferencial respecto de Quillota. El estudio de eventos ya muestra una diferencia de **+2,05 USD/MWh en el año −2**, comparado con el año −1. La observación plantea una duda concreta sobre tendencias paralelas. **¿Habría seguido La Vilana la misma trayectoria que los controles en ausencia de la apertura?**

En La Vilana, entre 2020 y 2021, el diferencial respecto de Quillota subió **0,85 USD/MWh**, frente a **5,01 USD/MWh** en los controles. Diecisiete de los 18 controles registraron un aumento y la composición de barras se mantuvo en ambos años. La Vilana quedó relativamente abajo justo en el año que sirve de referencia para medir el cambio posterior. Si esa diferencia se hubiera revertido en parte por las condiciones de la red, el DiD podría atribuir a la entrada un movimiento que habría ocurrido de todos modos. [Informe de cierre y diagnóstico de La Vilana](https://github.com/a-cartes/datacenter/blob/main/SOCHER_2026_RM/referencia/cierre_socher_20261009/INFORME_CIERRE.txt)

| Especificación | Estimación posterior promedio | Diferencia previa en el año −2 |
|---|---:|---:|
| Muestra completa | +1,05 | +2,05 |
| Sin julio y agosto de cada año, con los mismos sectores y controles | +0,31 | +0,78 |
| Sin 113 horas completas dentro de ventanas con maniobras documentadas en Polpaico–Lo Aguirre en 2021 | +0,72 | +1,67 |
| Sin La Vilana | +0,03 | — |
| Contraste descriptivo respecto del promedio de todo el período previo de cada cohorte | −0,09 | — |

*Cifras en USD/MWh. La exclusión de La Vilana cambia la composición de la muestra. El contraste con todo el período previo cambia la referencia. El filtro horario aplica a todas las barras en las mismas horas.*

La bitácora del **13 de agosto de 2021** confirma una maniobra asociada al control de transferencias en Polpaico–Lo Aguirre durante el episodio más pronunciado de agosto. Esa coincidencia ayuda a interpretar el comportamiento de los controles. La causa de toda la divergencia previa sigue abierta y los dos filtros dejan diferencias antes de la entrada. La lectura que propongo es reportar **+1,05 como estimación de la muestra completa**, con una atribución causal todavía frágil. [Informe diario del Coordinador, 13 de agosto de 2021](https://www.coordinador.cl/wp-content/uploads/2021/08/Informe-diario-13-08-2021.pdf)

#### Comparación con Virginia

Mamkhezri, Sun y Yang usan un diseño escalonado comparable y reportan **+2,49 USD/MWh** sobre el componente de congestión y pérdidas marginales de PJM. En su estudio de eventos, las diferencias previas son pequeñas y compatibles con cero, lo que da mayor respaldo al supuesto de tendencias paralelas. En Chile medimos el **diferencial respecto de Quillota**, por lo que las magnitudes de ambos trabajos corresponden a variables distintas. Una posible extensión del diseño chileno sería probar **DiD sintético** para examinar si una combinación ponderada de controles reproduce mejor la trayectoria previa de cada sector tratado. Quedaría por evaluar la calidad del ajuste previo, la sensibilidad a los pesos y la posible exposición de los controles a efectos indirectos de la misma red. [Documento de trabajo de Mamkhezri, Sun y Yang](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5736562)

### 3. Enfoque propuesto. Carga efectiva y capacidad de transmisión

**Pregunta principal.** ¿Cuánto cambia el costo marginal local cuando cambia la carga efectiva de un centro de datos y cómo varía ese efecto según la capacidad de transmisión disponible?

**Hipótesis económica.** La respuesta del costo marginal a un mismo aumento de carga depende de la barra y del estado de la red. El efecto puede ser pequeño con holgura y mayor si cambia la unidad marginal o se activa una restricción. La hipótesis se puede evaluar aunque el promedio anual sea cercano a cero.

#### A. Evidencia empírica a partir de una variación de carga

El caso disponible es **EdgeConneX II, en Colina**. El 3 de diciembre de 2024, a las **05:36**, el Coordinador registró una desconexión accidental de **1,12 MW** en la subestación Las Canteras. El proyecto vinculó los cuatro alimentadores afectados con un único cliente y documentó una caída medida de carga del mismo orden de magnitud. Las comparaciones preliminares también muestran variaciones de generación cercana, por lo que el episodio sigue siendo un **candidato a experimento natural**. [Informe de falla EAF 563/2024](https://www.coordinador.cl/wp-content/uploads/2024/12/EAF-563-2024.pdf) · [Análisis horario y documentación del proyecto](https://github.com/a-cartes/datacenter/blob/main/Investigacion_carga_zonal/INFORME_EXTENSION_LARGA_20261011.md)

El diseño consistiría en **seguir la caída y la recuperación del retiro efectivo**, observando el costo marginal local y su diferencial respecto de Quillota. La comparación usaría horas equivalentes de días cercanos y barras con exposición eléctrica comparable. También se examinarían ventanas placebo y la sensibilidad a las referencias de precio. Para una lectura causal, habría que comprobar si la falla modificó por sí misma la topología relevante para el precio y si otras variaciones de generación, demanda u operación coinciden con el episodio. Con un solo evento, el estimando sería **el efecto local y de corto plazo de esa reducción de carga, bajo las condiciones observadas**, con alcance limitado para extrapolar a aperturas completas o aumentos permanentes.

#### B. Simulación de despacho validada con datos observados

La simulación respondería la pregunta de planificación. **¿Cuánto cambia el costo de atender la misma carga cuando el refuerzo está disponible al entrar el centro de datos?**

| Capacidad de transmisión | Carga de referencia | Carga de referencia más el incremento del centro |
|---|---|---|
| Red con la capacidad observada | Escenario 1 | Escenario 2 |
| Red con mayor capacidad en el elemento estudiado | Escenario 3 | Escenario 4 |

El contraste **2 − 1** mide la respuesta a la carga con la capacidad observada. El contraste **4 − 3** mide la respuesta con mayor capacidad. Comparar ambos cuantifica **cuánto modifica el refuerzo el impacto de la carga**, manteniendo comunes los demás insumos del escenario.

Antes de interpretar el contrafactual, el modelo tendría que reproducir razonablemente **despacho, flujos y diferenciales de precios** en horas observadas con y sin restricciones. Reportaría por separado **el costo marginal por barra**, que es una señal de precio, y **el costo variable de operación del sistema**, que mide el costo de abastecer la carga en la simulación. Una evaluación de inversión requeriría además considerar el costo del refuerzo.

### 4. Propuesta para el artículo y preguntas para el revisor

Mi propuesta es usar el **DiD de aperturas como evidencia de partida** y evaluar si el **episodio de carga efectiva y la simulación validada** pueden sostener la contribución principal. El aporte sería cuantificar cómo la capacidad disponible al momento de la conexión cambia el costo de incorporar una gran carga. Así, el artículo se conecta directamente con la pregunta doctoral sobre **coordinación temporal entre grandes cargas y refuerzos de transmisión**.

Me interesa especialmente su opinión sobre estas decisiones:

1. **Identificación.** ¿Vale la pena intentar recuperar el diseño de aperturas con DiD sintético y controles seleccionados por comportamiento eléctrico previo, dados los tres sectores tratados?
2. **Experimento natural.** ¿Qué evidencia exigiría para interpretar la interrupción de Las Canteras como una variación exógena del retiro con efecto identificable sobre el precio local? ¿Sería suficiente un episodio bien documentado para una contribución acotada?
3. **Estimando principal.** ¿Conviene centrar el artículo en el **precio nodal**, en el **costo incremental de abastecimiento** o en la **diferencia que produce disponer del refuerzo al momento de la conexión**?
4. **Contribución para *Energy Economics*.** ¿Le parece más convincente un artículo centrado en identificación empírica a partir de carga medida, o uno que combina evidencia horaria con un contrafactual de despacho validado? ¿Qué pieza de evidencia considera decisiva antes de elegir?

<a id="revision"></a>

## 2. Revisión económica del diseño original

*Dictamen recibido antes de ejecutar los pilotos. La exposición diferenciada de los controles a un shock de red plantea un problema de comparabilidad. Para establecer un derrame causado por la entrada del centro habría que demostrar que esa entrada afectó a los controles.*

Reorientar el artículo hacia la interacción entre **carga eléctrica efectiva, restricciones de transmisión y oportunidad de los refuerzos** es la decisión más sólida para apuntar a *Energy Economics*. Tanto el diseño anual de diferencias en diferencias (DiD) presentado en SOCHER como un experimento natural apoyado en una sola falla de 1,12 MW enfrentan objeciones estructurales muy difíciles de levantar ante árbitros de una revista Q1 en economía de la energía. En cambio, un artículo que combine evidencia empírica horaria sobre congestión y carga con un modelo de despacho nodal rigurosamente validado ataca directamente una pregunta económica de frontera y conversa de forma natural con la tesis doctoral sobre coordinación temporal.

### 1. Identificación: por qué no conviene rescatar el DiD de aperturas

Invertir esfuerzo en recuperar el DiD anual con **DiD sintético (SDID)** y controles eléctricos tiene un retorno esperado bajo para *Energy Economics* por cinco problemas simultáneos:

* **Tamaño efectivo de muestra e inferencia.** Con solo **tres sectores tratados** (Algarrobal en 2021, La Vilana en 2022 y Chena en 2023) y 18 controles en un panel de 189 observaciones, los errores estándar agrupados por sector sufren severo sesgo de muestra pequeña. Incluso migrando a inferencia por permutación (tipo placebo en el espacio), el poder estadístico mínimo con $N_{\text{tratados}} = 3$ vuelve casi imposible distinguir un efecto real del ruido de red.
* **Desalineación teórica de los controles originales.** Emparejar barras mediante un *probit* con variables sociodemográficas del Censo 2017 (población, viviendas, inmigración, pueblos originarios y materialidad) carece de fundamento en la formación de precios nodales. El diferencial respecto de Quillota 220 kV depende de topología de red (factores de distribución de flujo o PTDF), nivel de tensión, generación local y saturación de corredores, no de composición censal.
* **Violación de SUTVA por derrames de red.** Incluso si se reconstruyen los pesos con SDID usando trayectorias eléctricas previas, en una red enmallada metropolitana los controles no son independientes de las restricciones que afectan a los tratados. El episodio de 2021 lo ilustra bien: maniobras de control de transferencias en Polpaico–Lo Aguirre afectaron a 17 de los 18 controles (+5,01 USD/MWh) mientras La Vilana apenas subió 0,85 USD/MWh. Un choque de red asimétrico sobre el grupo de control viola el supuesto contrafactual y el SDID no puede inmunizar el diseño contra derrames eléctricos en el período posterior.
* **Fragilidad concentrada en una sola unidad y agregación anual.** El hecho de que la estimación caiga de +1,05 USD/MWh a +0,03 USD/MWh al excluir La Vilana —y a $-0,09$ USD/MWh al usar todo el período previo como referencia— deja la atribución causal prácticamente indefendible ante un revisor. Además, promediar el año completo diluye la naturaleza altamente no lineal y horaria de la congestión, y usar la fecha de primera apertura introduce error de medición porque la carga de un centro de datos escala gradualmente por etapas.

A diferencia de Mamkhezri, Sun y Yang —quienes explotan una densidad mucho mayor de centros de datos y miden directamente el componente de congestión y pérdidas en PJM con pre-tendencias limpias—, el caso chileno aún tiene muy pocas entradas documentadas para sostener un DiD reducido creíble. Si decides conservar este bloque, conviene degradarlo a una **sección breve de contexto descriptivo** (o removerlo por completo para no abrir un flanco débil desde la introducción).

### 2. Experimento natural de Las Canteras: qué exigiría un revisor

El episodio del 3 de diciembre de 2024 a las 05:36 en la subestación Las Canteras (EdgeConneX II, Colina) —una desconexión accidental de **1,12 MW** documentada en el EAF 563/2024— enfrenta dos barreras críticas para sostenerse como experimento natural causal sobre precios:

* **Magnitud física y relación señal-ruido.** En un sistema del tamaño del SEN chileno, una variación de 1,12 MW a las 05:36 AM (hora valle de madrugada, justo antes de la rampa matinal) difícilmente desplaza a la unidad marginal del despacho o activa/libera una restricción térmica troncal, salvo que un transformador o línea local estuviera exactamente en su límite en ese minuto. Cualquier diferencia observada en el costo marginal a esa hora corre un alto riesgo de ser ruido de rampa, redespacho hidráulico/térmico o variaciones de generación cercana —algo que ya detectaste en tus comparaciones preliminares.
* **Exogeneidad operativa en un sistema auditado de costos.** A diferencia de un mercado de ofertas (*bid-based*), el Coordinador Eléctrico Nacional calcula el costo marginal real a partir de la operación auditada, la unidad marginal y las restricciones activas. Para defender una lectura causal, un árbitro exigiría cuatro pruebas mínimas:
  1. **Verificación forense en registros del Coordinador:** demostrar explícitamente qué unidad fijó el costo marginal y qué línea o transformador estuvo saturado en los bloques de 15 minutos u horarios antes, durante y después de las 05:36, confirmando que la caída y recuperación de los 1,12 MW alteró efectivamente la restricción activa o el despacho marginal.
  2. **Restricción de exclusión topológica:** probar que la falla en los cuatro alimentadores no modificó la configuración de red ni gatilló protecciones o redespachos de seguridad que afectaran el precio por un canal distinto al retiro de carga.
  3. **Control por generación cercana y demanda vecina:** aislar los movimientos simultáneos de generación local mediante datos horarios de inyección de las centrales cercanas y flujos medidos en las líneas adyacentes.
  4. **Inferencia robusta con placebos temporales y espaciales:** mostrar que el salto estimado en el diferencial de precios se ubica en la cola extrema de una distribución placebo construida con las mismas horas (05:00–07:00) en días laborales similares sin falla.

Incluso superando las cuatro pruebas, **un solo episodio de 1,12 MW no alcanza para sostener la contribución empírica principal en *Energy Economics***. Su validez externa respecto a la conexión de centros de datos de decenas de megawatts en horas punta es demasiado estrecha. Su mejor rol es como **evidencia micro-forense de validación** o como motivación de cómo se comporta el retiro real en barra, a menos que logres ensamblar un panel de múltiples eventos de desconexión/conexión de mayor magnitud o explotar la serie horaria continua de retiros medidos de centros de datos.

### 3. Estimando principal: precio nodal, costo del sistema o valor del refuerzo

La elección del estimando define si el artículo se lee como un ejercicio descriptivo de precios o como una contribución en economía de la regulación y planificación eléctrica.

| Estimando | Interpretación económica | Ventaja para *Energy Economics* | Limitación principal |
|---|---|---|---|
| **Precio nodal ($CMg_i$ o diferencial)** | Señal marginal de escasez y efecto distributivo (rentas de congestión entre generadores y demanda). | Alta visibilidad práctica y fácil de validar contra datos reales del Coordinador. | Es discontinuo (plano con holgura, salta al saturarse) y no mide bienestar agregado sino transferencias. |
| **Costo incremental de abastecimiento ($\Delta CV_{\text{op}}$)** | Costo económico real de corto plazo (redespacho fuera de mérito) de atender la nueva carga. | Métrica rigurosa de eficiencia asignativa; capta efectos aunque el precio marginal cambie poco. | Por sí solo no responde cómo debe actuar el planificador de transmisión. |
| **Valor de la coordinación temporal: $(E_2 - E_1) - (E_4 - E_3)$** | Ahorro en costo de operación (y cambio en congestión) al tener el refuerzo disponible al conectarse la carga. | **Es el aporte más original y con mayor tracción de política pública**; conecta directo con tu tesis. | Exige contrastarse contra el **costo de inversión (CapEx)** del refuerzo para hablar de bienestar neto. |

Conviene **centrar el artículo en el tercer estimando** —cuánto reduce el refuerzo oportuno el sobrecosto de integrar la gran carga— reportando **en paralelo** el costo variable total del sistema (eficiencia) y el precio nodal / rentas de congestión (distribución e incentivos de localización). Para blindar el argumento frente a la crítica obvia de que "más transmisión siempre reduce el costo variable", incorpora un **análisis de punto de equilibrio (*breakeven*)**: calcula qué costo anualizado de inversión (o cuántos años de desfase entre la entrada del centro de datos y el refuerzo) hace socialmente rentable adelantar la obra. Así conviertes una comparación técnica de escenarios en un resultado económico completo.

### 4. Estrategia para *Energy Economics* y la pieza decisiva antes de elegir

En *Energy Economics*, el diseño más convincente —y realista dado el estado actual del parque de centros de datos en Santiago— es el **enfoque híbrido: caracterización empírica horaria + contrafactual de despacho validado**. Un artículo puramente empírico de identificación causal a partir de carga medida solo sería superior si contaras con retiros horarios observados de varios centros de datos de gran escala (decenas de MW) operando a través de regímenes con y sin congestión en los corredores clave de la Región Metropolitana.

Para que la arquitectura híbrida sea publicable, el flujo debería ordenarse así:

1. **Evidencia empírica horaria (no anual):** reemplazar el DiD de sectores censales por un análisis de alta frecuencia (horario) sobre las barras del norte y sur de la RM, documentando en qué horas del día y meses se acoplan o desacoplan los precios respecto de Quillota 220 kV, qué restricciones de transmisión explican esos desacople (ej. corredor Polpaico–Lo Aguirre) y cómo interactúan con perfiles típicos de carga constante de centros de datos (y, si existe acceso a balances de transferencias, retiros horarios efectivos).
2. **Modelo de despacho nodal validado:** calibrar un flujo de potencia óptimo en corriente continua (DC-OPF) o despacho económico con restricciones de red usando parámetros públicos del Coordinador, y demostrar cuantitativamente que reproduce flujos, frecuencias de congestión y diferenciales nodales observados tanto en horas con holgura como en horas saturadas.
3. **Contrafactual de coordinación (matriz $2 \times 2$ extendida):** evaluar el contraste $(E_2 - E_1) - (E_4 - E_3)$ no solo para un nivel fijo de carga, sino parametrizado por **escala del centro de datos** (por ejemplo, rampas de 20, 50 y 100+ MW), **localización nodal** (barras con holgura vs. barras aguas abajo de corredores congestionados) y **rezago del refuerzo** (1 a 3 años de retraso, o incluso flexibilidad de la carga en horas críticas).

Antes de comprometer meses de trabajo en esta ruta, hay **dos piezas de evidencia decisivas** que debes verificar de inmediato:

* **Diagnóstico 1 (descarte rápido del experimento natural):** revisar en la bitácora y cálculo de costos marginales reales del 3 de diciembre de 2024 (05:00–07:00) si la salida de 1,12 MW en Las Canteras modificó alguna restricción activa o la unidad marginal. Si no hubo cambio en la restricción activa ni en la unidad marginal, descarta Las Canteras como estrategia de identificación causal sin dudarlo.
* **Diagnóstico 2 (prueba de fuego del modelo de despacho):** correr una validación piloto del modelo de red sobre un período con episodios documentados de congestión (por ejemplo, semanas de invierno y verano de un año reciente) y medir su capacidad para replicar el signo, magnitud y horas de activación de los diferenciales respecto de Quillota. Si el modelo replica bien los episodios de saturación observados —sin exigir supuestos *ad hoc*—, tienes la columna vertebral de un manuscrito sólido para *Energy Economics*.

¿Ya cuentas con acceso a retiros horarios medidos a nivel de alimentador/subestación en los Balances de Transferencias Económicas del Coordinador, o el análisis de carga efectiva se apoyaría por ahora en el caso de Las Canteras y perfiles proyectados de demanda?

<a id="pilotos"></a>

## 3. Resultados de Las Canteras y Polpaico–Lo Aguirre

*Resultados del piloto con precios, retiros, fechas comparables y errores fuera del mes de ajuste.*

**Fecha** · 20 de noviembre de 2026  
**Objetivo** · Identificar cuál es la limitación empírica antes de estimar cuánto cuesta que una gran carga entre antes de que esté disponible un refuerzo de transmisión.

### Resultado para decidir el diseño

En **Las Canteras** se distingue bien la caída de carga, pero la respuesta del diferencial de precios queda dentro de la variación habitual de los martes comparables. En **Polpaico–Lo Aguirre** sí aparece una señal de precios asociada a las ventanas operativas documentadas, que aporta información fuera del mes de ajuste. Los episodios cumplen funciones distintas. Las Canteras permite verificar una perturbación de carga y su contexto de operación. Polpaico–Lo Aguirre ofrece un caso exigente para validar si un modelo reproduce la separación de precios.

Lo que queda por reconstruir es **un estado de despacho sincronizado por hora**, con la restricción activa, sus flujos y límites operativos, la topología, la demanda por barra y las unidades disponibles con sus costos variables y restricciones de operación. Con esos elementos se puede simular la misma hora con y sin la carga y con y sin el refuerzo. El piloto cuantifica la señal observada y el rendimiento de una referencia estadística. El costo de adelantar la obra queda pendiente de ese contrafactual físico.

### 1. Las Canteras. ¿La caída de carga se distingue en los precios?

El evento del **3 de diciembre de 2024 a las 05:36** afectó la barra N.º 1 de 23 kV. El Coordinador registró **1,12 MW** de consumo desconectado. El proyecto dispone de carga horaria observada en HT1 y HT2, precios en barras locales y externas, e inyección neta en un punto de Don Humberto. [Informe EAF 563/2024](https://www.coordinador.cl/wp-content/uploads/2024/12/EAF-563-2024.pdf) · [Informe del proyecto](https://github.com/a-cartes/datacenter/blob/main/Investigacion_carga_zonal/INFORME_EXTENSION_LARGA_20261011.md)

| Fase del día, hora local de inicio de bloque | Retiro HT1 + HT2 (MW) | CMg Las Canteras (USD/MWh) | CMg Quillota (USD/MWh) | Diferencial (USD/MWh) |
|---|---:|---:|---:|---:|
| Previa, bloques 00 a 04 | 2,080 | 76,22 | 74,58 | 1,64 |
| Primeras dos horas completas, bloques 06 y 07 | 0,879 | 60,40 | 59,07 | 1,33 |
| Caída, bloques 06 a 15 | 0,907 | 12,08 | 11,81 | 0,27 |
| Recuperación parcial, bloques 17 a 20 | 1,937 | 31,81 | 30,61 | 1,20 |

Amplié la comparación del proyecto a **los ocho martes anteriores y ocho posteriores**. Para cada fecha calculé el cambio frente a sus propios bloques 00 a 04. Resté al cambio del evento el promedio de los cambios de los 16 martes comparables. También conté cuántos martes tuvieron una desviación absoluta respecto de ese promedio igual o mayor a la del evento. Es una comparación descriptiva porque la fecha corresponde a una falla y los días tienen condiciones de red y generación diferentes.

| Variable | Contraste en bloques 06 a 15 | Martes con desviación igual o mayor |
|---|---:|---:|
| Retiro HT1 + HT2 | −1,232 MW | 0 de 16 |
| CMg Las Canteras | −20,39 USD/MWh | 6 de 16 |
| CMg Quillota | −20,14 USD/MWh | 6 de 16 |
| Diferencial Las Canteras menos Quillota | −0,25 USD/MWh | 11 de 16 |
| Diferencial Las Canteras menos comparadores distantes | −1,12 USD/MWh | 9 de 16 |
| Inyección neta H1 de Don Humberto | +24,44 MW | 0 de 16 |

En los bloques **06 y 07**, ambos con precios positivos, el contraste de retiro es **−1,193 MW** y el diferencial respecto de Quillota cambia **−0,28 USD/MWh**, con **11 de 16** martes igualmente o más extremos. En los bloques 06 a 15 hubo **ocho de diez horas con precio cero en ambas barras**. Al revisar los registros de instrucciones de operación (RIO) del mismo día, hallé que a las **08:08** aparece por primera vez la anotación **«Prorrata Generalizada costo SEN 0»**, en 186 registros de esa hora de instrucción. El resumen diario del Coordinador también muestra una caída matinal del costo marginal en varias barras. La coincidencia da un contexto sistémico al bloque de precios cero. En los registros revisados quedó sin verificar qué unidad fijó el costo marginal de Las Canteras alrededor de la desconexión y qué restricción, si alguna, cambió con la falla. [RIO archivado y su manifiesto](https://github.com/a-cartes/datacenter/tree/main/Investigacion_carga_zonal/fuentes_operacion/20261011_rio_202412_completo) · [Resumen diario del Coordinador](https://www.coordinador.cl/wp-content/uploads/2024/12/Resumen-Ejecutivo-de-Operacion-03-12-2024.pdf)

**Conclusión del caso.** La caída observada de carga es excepcional dentro de la comparación. El diferencial de precios presenta alta variación habitual y el entorno operativo cambió durante el día. Usaría el episodio para verificar la medición de carga y probar cómo responde el modelo ante una perturbación pequeña en ese estado de la red. Su alcance para identificar una respuesta causal de precios queda limitado.

### 2. Polpaico–Lo Aguirre. ¿La bitácora aporta información fuera del mes de ajuste?

Reconstruí **1.488 horas de julio y agosto de 2021** para los mismos 18 sectores de control de SOCHER y La Vilana, con un promedio simple de barras por sector y de sectores en el grupo de control. La variable es **el CMg medio de los controles menos el CMg de La Vilana**. Quillota se cancela algebraicamente al restar los dos diferenciales que la usan como referencia.

Usé **19 ventanas con inicio y fin documentados** de las maniobras del reactor de Polpaico asociadas al control de transferencias de la línea Polpaico–Lo Aguirre. El indicador marca las **113 horas completas** dentro de dichas ventanas. Las demás horas se codifican como no cubiertas por ese indicador. Pueden contener otras restricciones, o episodios sin ambos extremos documentados. [Archivo de costos marginales 2021](https://www.coordinador.cl/mercados/documentos/transferencias-economicas/costos-marginales-de-energia/2021-costos-marginales-de-energia/) · [Bitácora del 7 de julio](https://www.coordinador.cl/wp-content/uploads/2021/07/Informe-diario-07-07-2021.pdf) · [Bitácora del 13 de agosto](https://www.coordinador.cl/wp-content/uploads/2021/08/Informe-diario-13-08-2021.pdf)

| Mes | Brecha media dentro de las ventanas (USD/MWh) | Brecha media en las demás horas (USD/MWh) | Horas con brecha > 20 USD/MWh cubiertas por el indicador |
|---|---:|---:|---:|
| Julio 2021 | 47,92 | 10,88 | 20 de 69 |
| Agosto 2021 | 98,02 | 7,71 | 78 de 110 |

Ajusté una regresión con indicadores por hora y fin de semana y la comparé con una que añade el indicador de bitácora. Cada modelo se evaluó en el otro mes, usando el estado operativo registrado de las horas de evaluación. La prueba mide **reconstrucción fuera de muestra condicionada a un dato operativo contemporáneo**.

| Mes de ajuste → mes de evaluación | MAE, calendario | MAE, calendario + bitácora | RMSE, calendario | RMSE, calendario + bitácora |
|---|---:|---:|---:|---:|
| Julio → agosto | 19,31 | 17,43 | 37,50 | 33,38 |
| Agosto → julio | 16,43 | 10,72 | 23,19 | 23,82 |

*Errores en USD/MWh. Cada evaluación comprende 744 horas.*

**Conclusión del caso.** Incorporar la bitácora reduce el error absoluto medio en ambas direcciones. El error cuadrático empeora ligeramente al ajustar con agosto y evaluar julio. La intensidad de las brechas cambia mucho entre meses y el indicador deja episodios grandes sin cubrir. El resultado ofrece una **referencia de comparación para el despacho** y documenta cuánto aporta observar el estado operativo. La evidencia disponible todavía deja abierta la atribución de la brecha a una restricción individual y el valor de aumentar la capacidad.

### 3. Qué se puede resolver con los insumos disponibles

| Insumo | Estado verificado en este piloto |
|---|---|
| Precios horarios y pequeños cambios observados de retiro | Disponibles en los paneles de SOCHER y Las Canteras. Se reprodujeron las 24 observaciones del día del evento contra el archivo de diagnóstico. |
| Eventos y registros del operador | Disponibles para los episodios revisados. Las tres primeras páginas de RIO contrastadas coinciden con las huellas del manifiesto y cubren las 24 horas del 3 de diciembre. La bitácora ofrece marcas operativas para Polpaico. |
| Parámetros físicos y mediciones de red | Existe un catálogo local con ocho secciones y cuatro canales alrededor de Las Canteras. Contiene reactancias y límites nominales declarados. Su documentación distingue esos límites de la capacidad operativa de cada fecha y de las restricciones de seguridad. |
| Estado de despacho reproducible para cada hora | Queda por ensamblar y verificar una fotografía coherente que vincule estados de equipos, flujos, límites activos, demanda por nodo, disponibilidad y costos de generación. Los insumos parciales revisados ya acotan la búsqueda a horas y corredores concretos. |

[Catálogo y alcance de topología del proyecto](https://github.com/a-cartes/datacenter/tree/main/Investigacion_carga_zonal/resultados/20261011_topologia_operativa_v1)

La prueba decisiva del artículo sería **reproducir, en horas que no se usaron para calibrar el despacho, qué corredor se restringe, en qué dirección fluye la energía y cuánto se separan los precios**. Polpaico–Lo Aguirre ofrece un contraste observable para esas horas. El calendario y la bitácora ya dan una referencia estadística contra la cual juzgar cuánto valor añade el modelo físico.

Una vez validado el caso base, el artículo puede estimar el **ahorro de operación atribuible a contar con el refuerzo para atender la carga** como la diferencia entre dos costos incrementales. Primero, el costo de añadir la carga a la red original. Segundo, el costo de añadir esa misma carga a la red reforzada. El valor de adelantar la obra exige luego integrar esos ahorros en el período de desfase y compararlos con el costo de anticipar la inversión. Ese es el resultado económico que aún falta para evaluar el manuscrito para *Energy Economics*.

### Reproducción y alcance

- Repositorio del proyecto, revisión `69a68ee3ab015257b797579fd77cd1b71b2f200b`.
- Las Canteras. Panel `panel_H1_completo.csv.gz` y diagnóstico `episodio_documentado.csv`. El contraste resta el cambio medio de los 16 martes al cambio del 3 de diciembre, siempre con bloques 00 a 04 como base.
- Polpaico. Muestra SOCHER 2017–2025, mapas de barra a sector, precios horarios definitivos de julio y agosto de 2021 y bitácoras diarias de ambos meses. La prueba conserva las reglas de composición de barras de SOCHER para 2021. El mes evaluado queda fuera del ajuste.
- El piloto aporta cálculos descriptivos y una referencia de reconstrucción. Los efectos causales de la entrada y el valor monetario del refuerzo quedan pendientes de identificación y validación.

<a id="hoja"></a>

## 4. Evaluación recibida y propuesta de despacho

*Se conserva la evaluación recibida para que el lector pueda contrastarla con los cálculos. Las expresiones «p-valor de permutación», «derivada estrictamente cero» y «cifra exacta» son interpretaciones del dictamen. El alcance empírico y económico se precisa en la síntesis y en la sección 5.*

Los resultados del piloto cierran limpiamente la discusión sobre el experimento natural y confirman exactamente por qué el aporte del artículo está en el modelo de despacho validado. El dato de **«Prorrata Generalizada costo SEN 0»** en Las Canteras es mucho más valioso de lo que parece a primera vista: convierte un resultado nulo en una demostración empírica directa de la hipótesis central del trabajo.

### 1. Lectura económica de los dos pilotos

* **Las Canteras (3 de diciembre de 2024): cierre definitivo y uso óptimo.** Un cambio de $-0,25$ USD/MWh superado en 11 de 16 martes comparables descarta sin ambigüedad a este episodio como fuente de identificación causal de precios (equivalente a un *p*-valor de permutación superior a 0,70). Sin embargo, el registro de precio cero simultáneo en Las Canteras y Quillota durante 8 de las 10 horas de caída —bajo prorrata generalizada— **prueba empíricamente la dependencia de régimen** que planteaste en la nota metodológica: en horas de sobreoferta o vertimiento del sistema, la derivada del costo marginal respecto de la carga es estrictamente cero ($\partial CMg / \partial L = 0$). En el artículo, este episodio cumple dos funciones limpias y difíciles de atacar: validar que el retiro real de un centro de datos es medible en barra y mostrar por qué las regresiones promedio incondicionales diluyen el efecto real de la carga.
* **Polpaico–Lo Aguirre (julio–agosto 2021): señal real, límite del enfoque reducido.** Que incorporar las maniobras de bitácora reduzca el MAE fuera de muestra en agosto de 19,31 a 17,43 USD/MWh demuestra que las restricciones operativas explican parte del desacople nodal. Al mismo tiempo, un MAE residual de **17,43 USD/MWh** sigue siendo demasiado alto para sostener contrafactuales de política energética con un modelo estadístico reducido. Ese residuo justifica ante cualquier revisor por qué necesitas pasar de una aproximación reducida a un **modelo estructural de despacho con restricciones de red** capaz de capturar no linealidades, cambios de unidad marginal y límites térmicos/operativos.

### 2. Riesgo de arbitraje: no depender solo del régimen de 2021

Antes de reconstruir toda la operación de julio–agosto de 2021, conviene anticipar una objeción casi segura de un árbitro de *Energy Economics*: **¿es representativo de la red actual un episodio de 2021?**

El invierno de 2021 en el SEN combinó una sequía severa, alta participación de generación térmica cara en el margen y una topología de transmisión en la Región Metropolitana previa a obras recientes y al despliegue masivo de generación solar y almacenamiento (BESS). Si validas el modelo **únicamente** en julio–agosto de 2021, un revisor puede argumentar que sobreestimas el costo del desfase carga–refuerzo para centros de datos que entran hoy o hacia 2027–2030.

La forma más sólida de blindarte es un esquema de **doble validación**:

1. **Validación histórica de estrés (julio–agosto 2021):** demuestra que tu modelo estructural reproduce con precisión las brechas de precio y la activación de límites documentados en Polpaico–Lo Aguirre (como el episodio del 13 de agosto).
2. **Validación en régimen reciente (un período de 2024 o 2025):** demuestra que el mismo modelo, actualizado con la topología, costos variables y perfiles renovables actuales (incluyendo horas de prorrata a precio cero), reproduce el patrón vigente de acoplamiento y desacople. Luego ejecutas los contrafactuales de desfase sobre la red actualizada, o comparas explícitamente ambos regímenes (año seco/térmico vs. sistema con alta penetración solar).

### 3. Hoja de ruta para la prueba decisiva de validación

El mayor peligro en esta etapa es intentar replicar el SEN completo barra por barra y quedar atrapado meses depurando datos de subestaciones irrelevantes. Para *Energy Economics*, una **red equivalente reducida y auditable** (por ejemplo, un modelo DC-OPF con pérdidas linealizadas concentrado en el anillo metropolitano y sus corredores de entrada —Quillota 220 kV, Polpaico, Lo Aguirre, Alto Jahuel, Chena y Las Canteras—, agregando el norte y el sur del SEN como inyecciones/retiros netos o nodos equivalentes) es más transparente y mucho más fácil de diagnosticar.

| Capa de datos (Coordinador Eléctrico Nacional) | Qué debes sincronizar por hora | Punto crítico de calibración |
|---|---|---|
| **Flujos y topología** | Flujos horarios medidos en Polpaico–Lo Aguirre y líneas paralelas del anillo RM; estados de conexión/desconexión de elementos. | Distinguir entre **límite térmico nominal** y **límite operativo temporal** impuesto por maniobras o seguridad (bitácoras e Informes Diarios). |
| **Generación disponible y costos** | Generación horaria real, disponibilidad declarada (o techo de inyección renovable/hidro) y costos variables auditados (CVNC/combustibles). | Identificar la unidad marginal real reportada por el Coordinador en cada hora; las centrales hidroeléctricas de embalse deben entrar con su valor del agua implícito o generación fija observada si no modelas despacho multietapa. |
| **Demanda por barra** | Retiros horarios medidos por barra en la zona de estudio y saldo neto en las barras frontera (Quillota y sur). | Verificar consistencia de balance nodal ($\sum \text{Gen} - \sum \text{Dem} - \text{Pérdidas} = \text{Flujo neto}$) antes de correr la optimización. |
| **Precios de contraste** | Costo marginal real horario en Quillota 220 kV y barras de la RM. | Separar explícitamente horas acopladas ($\Delta CMg \approx 0$), horas de prorrata ($CMg = 0$) y horas con restricción activa. |

Para que la validación fuera de muestra convenza a un revisor, evita depender solo del MAE global y reporta **cuatro métricas complementarias** sobre horas reservadas fuera de calibración:

1. **Clasificación de régimen de congestión:** precisión y sensibilidad (*precision/recall*) del modelo para predecir en qué horas exactas la restricción Polpaico–Lo Aguirre se vuelve activa ($\mu > 0$).
2. **Error condicional en horas congestionadas:** MAE y sesgo del diferencial $\Delta CMg$ *solo* en las horas con separación real de precios (donde el modelo reducido suele fallar más).
3. **Ajuste de flujos físicos:** correlación y RMSE entre el flujo simulado y el flujo medido en el corredor restringido (sin acertar el flujo, acertar el precio es casualidad).
4. **Identidad de la unidad marginal / costo de operación:** verificar que las brechas de precio simuladas emergen por el mismo mecanismo económico (redespacho térmico fuera de mérito) que ocurrió en la bitácora.

### 4. Cerrar el aporte económico: del despacho al costo del desfase

Una vez que el modelo supere la validación fuera de muestra, la matriz $2 \times 2$ de tu nota metodológica se traduce directamente en el resultado principal del paper al conectar el despacho con la economía de la expansión:

* **Inyección de carga realista:** en lugar de un único bloque arbitrario, simula una curva de escalamiento representativa de centros de datos en la RM (por ejemplo, perfiles planos 24/7 de 20, 50 y 100 MW en nodos específicos con distinta sensibilidad de flujo hacia el corredor crítico).
* **Descomposición del efecto:** para cada nivel de carga, calcula por separado la diferencia en **costo variable de operación del sistema** $(CV_{E2} - CV_{E1}) - (CV_{E4} - CV_{E3})$ (eficiencia productiva real), el cambio en el **precio marginal nodal** y las **rentas de congestión** (efecto distributivo entre generadores y demanda).
* **Regla económica de coordinación temporal:** contrasta el ahorro operativo anual generado por adelantar el refuerzo contra la **anualidad de inversión y operación (AVI + COMA)** de una obra equivalente en el Plan de Expansión de la Transmisión. Esto te permite responder con una cifra exacta cuántos meses o años de desfase entre la entrada de la carga y la entrada de la línea convierten el atraso en una pérdida neta de bienestar social —y bajo qué umbral de MW conviene exigir refuerzo previo o esquemas de conexión flexible/interrumpible.

<a id="horaria"></a>

## 5. Validación horaria, cálculos y código reproducible

*Esta sección contiene el ejercicio más reciente, con las 741 horas de octubre y noviembre de 2024, las reglas para comparar una misma hora del día y el código Python de la tabla ampliada.*

### Revisión de los pilotos y prueba empírica para el artículo

**Pregunta económica.** ¿Cuánto cambia el costo de abastecer la misma carga si el refuerzo de transmisión entra al mismo tiempo que el centro de datos o llega después?

**Resultado de esta revisión.** En octubre y noviembre de 2024, el diferencial de precios de Las Canteras respecto de Quillota fue mayor, en promedio, en horas con una instrucción de control en Alto Jahuel–Lo Aguirre. Al comparar dentro del mismo mes y hora del día, cambia el signo de la diferencia. Esto establece que la comparación es sensible a la composición horaria. La contribución pendiente es cuantificar el costo incremental de la carga mediante un despacho que reproduzca precios y flujos observados en horas reservadas para evaluación.

### 1. Comparación reciente con los datos del proyecto

Usé como variable de resultado el costo marginal horario de **Las Canteras 110 kV menos Quillota 220 kV**, en USD/MWh. Los estados provienen de instrucciones sobre **Alto Jahuel–Lo Aguirre 500 kV**. La brecha elegida mide el precio relativo del punto donde interesa la carga. Ninguna de estas dos barras de precio es un extremo del corredor controlado.

#### Tres fechas con respaldo documental

Clasifiqué una hora solo cuando sus 60 minutos quedaron dentro de un mismo estado documentado. Recalculé el diferencial directamente desde los dos precios horarios. Las columnas de precios muestran medias simples por estado.

| Fecha de 2024 | Horas con control | Horas sin ese control | Transición o desconocido | Diferencial con control | Diferencial sin ese control |
|---|---:|---:|---:|---:|---:|
| 7 de octubre | 7 | 16 | 1 | 2,03 | 0,64 |
| 26 de octubre | 8 | 14 | 2 | 1,22 | 0,27 |
| 6 de noviembre | 4 | 16 | 4 | 0,95 | 0,37 |

Las 19 horas completas con control comenzaron a las 23 h o entre las 00 y las 06 h. Las 46 horas completas sin ese control comenzaron entre las 07 y las 22 h. En estas tres fechas, **ninguna hora del reloj aparece en ambos estados**. Un modelo que clasificara las horas por calendario podría acertar estas distinciones sin representar la física de la red. La marca «sin ese control» se refiere exclusivamente a la maniobra estudiada. [Intervalos documentados](https://github.com/a-cartes/datacenter/blob/69a68ee3ab015257b797579fd77cd1b71b2f200b/Investigacion_carga_zonal/resultados/20261011_episodios_horarios_v1/intervalos_interpretados.csv) · [Eventos extraídos de los informes del Coordinador](https://github.com/a-cartes/datacenter/blob/69a68ee3ab015257b797579fd77cd1b71b2f200b/Investigacion_carga_zonal/resultados/20261011_episodios_horarios_v1/eventos_extraidos_CEN.csv)

#### Ampliación al registro horario

Tomé todas las horas de octubre y noviembre de 2024 incluidas en el panel de estimación del proyecto con estado conocido del corredor. Hay **741 horas de 35 fechas** entre el 4 de octubre y el 22 de noviembre. La muestra es parcial. En ella hay 148 horas con la instrucción y 593 sin ella. En la comparación general, el diferencial medio fue de 1,539 y 0,928 USD/MWh, respectivamente.

Para comparar una misma hora del reloj, agrupé los días por mes y hora de inicio del bloque. Dentro de cada grupo calculé el diferencial medio con control menos el diferencial medio sin ese control. Luego promedié los contrastes dando el mismo peso a cada grupo con ambos estados. La comparación sigue siendo observacional porque demanda, generación, disponibilidad de equipos y otras instrucciones pueden cambiar entre fechas.

| Regla de comparación | Grupos mes × hora | Horas con / sin control | Diferencia con menos sin control (USD/MWh) |
|---|---:|---:|---:|
| Todos los registros, promedio por estado | — | 148 / 593 | +0,61 |
| Mismo mes y hora, ≥1 fecha por estado | 15 | 129 / 86 | −0,15 |
| Mismo mes y hora, ≥2 fechas por estado | 9 | 79 / 40 | −0,44 |
| Mismo mes y hora, ≥3 fechas por estado | 7 | 64 / 36 | −0,49 |

El cambio de signo combina selección de horas comparables y ponderación. Si se retienen las mismas 215 horas de la segunda fila y se promedian directamente por estado, el contraste ya es **−0,17 USD/MWh**. Dar el mismo peso a los 15 grupos lo lleva a **−0,15**. En esta muestra, la selección de horas comparables explica la mayor parte de la diferencia respecto del promedio general. Las tres reglas muestran cómo cambia la descripción al exigir más observaciones. Se publican juntas, sin seleccionar un umbral por el resultado. [Panel horario de estimación](https://github.com/a-cartes/datacenter/blob/69a68ee3ab015257b797579fd77cd1b71b2f200b/Investigacion_carga_zonal/resultados/20261011_estimacion_rio_v3/panel_estimacion.csv.gz)

**Uso inmediato.** Las 05 h ofrecen 21 fechas con control y ocho sin él. Dos ejemplos consecutivos son el 7 y el 8 de octubre, con y sin control respectivamente y con retiros HT1+HT2 de 2,004 y 2,022 MW. Este par permite comprobar si un modelo que conoce la hora e incorpora los insumos físicos reproduce estados distintos. Sirve para diagnosticar la reconstrucción. Una evaluación independiente debe reservar otras fechas completas antes de ajustar parámetros y mantener los precios observados fuera de la calibración de esas fechas.

### 2. Alcance de los dos pilotos anteriores

**Las Canteras, 3 de diciembre de 2024.** El Coordinador documentó una desconexión de 1,12 MW a las 05:36. El contraste del retiro observado en HT1+HT2 para los bloques 06 a 15 fue de −1,23 MW respecto de 16 martes cercanos, tomando en cada día los bloques 00 a 04 como base. Ningún martes comparable mostró una desviación del retiro tan grande. Para el diferencial Las Canteras–Quillota, el contraste fue −0,25 USD/MWh y 11 de 16 martes tuvieron una desviación absoluta igual o mayor. Este recuento es descriptivo. Interpretarlo como un valor p de permutación requeriría justificar la intercambiabilidad de las fechas y el procedimiento de reasignación.

En ocho de las diez horas hubo precio cero en ambas barras. La primera anotación «Prorrata Generalizada costo SEN 0» del día aparece a las 08:08, después de la falla. Los registros muestran una reducción de carga medible y un régimen posterior compatible con baja sensibilidad del precio. Observar ese precio para la carga realizada deja abierta la pregunta de cuánto habría cambiado con otra carga en la misma hora. Incluso en las dos primeras horas completas, con precios positivos, el diferencial de −0,28 USD/MWh queda dentro de la dispersión de los martes. [EAF 563/2024](https://www.coordinador.cl/wp-content/uploads/2024/12/EAF-563-2024.pdf) · [RIO archivado](https://github.com/a-cartes/datacenter/tree/69a68ee3ab015257b797579fd77cd1b71b2f200b/Investigacion_carga_zonal/fuentes_operacion/20261011_rio_202412_completo)

**Polpaico–Lo Aguirre, julio y agosto de 2021.** Al agregar la marca contemporánea de bitácora, el error absoluto medio de la reconstrucción de agosto baja de 19,31 a 17,43 USD/MWh. En la prueba inversa también baja el error absoluto medio, aunque el error cuadrático medio en raíz sube de 23,19 a 23,82. La variable reconstruida es el promedio de precios de los 18 sectores de control menos el de La Vilana. Las cifras sirven de referencia al evaluar un despacho sobre ese mismo resultado. Un juicio de suficiencia económica exige comparar errores, incertidumbre y tamaño del efecto que se quiere medir. Las maniobras identifican control de transferencias. La atribución de una brecha a un límite vinculante requiere contrastes físicos adicionales. [Informe diario del 13 de agosto de 2021](https://www.coordinador.cl/wp-content/uploads/2021/08/Informe-diario-13-08-2021.pdf)

### 3. De la prueba física al resultado económico

1. **Reconstruir horas con estados diferentes.** Usar el episodio del 13 de agosto de 2021 para Polpaico–Lo Aguirre, los pares recientes para Alto Jahuel–Lo Aguirre y Las Canteras para el caso de precios cero. Son exigencias distintas para un mismo modelo. La estructura del modelo se mantiene y los datos de red, demanda, oferta y disponibilidad corresponden a cada fecha. Para evaluar Polpaico–Lo Aguirre en 2024 hacen falta observaciones recientes del propio corredor.
2. **Contrastar precios y operación de forma independiente.** Reunir por hora el sentido y la magnitud del flujo medido en el corredor, el límite operativo aplicable, los estados de equipos, las disponibilidades y costos, los retiros y los precios en los extremos y barras de interés. Comprobar el balance físico y reservar fechas enteras de prueba. Informar errores de flujo y de diferenciales por régimen frente al modelo de calendario. Una instrucción permite contrastar el régimen documentado. Atribuirle un precio sombra positivo requiere evidencia de que el límite restringía económicamente el despacho. Para evaluar la capacidad de reproducir precios cero, mantenerlos como resultado de prueba.
3. **Calcular el costo de atender la carga.** Sobre la red reducida, simular la misma hora con carga base y con carga adicional, para la red original y la reforzada. Permitir que los intercambios con el resto del sistema respondan a la nueva demanda dentro de límites y costos justificables. Si la base ya incluye el retiro observado del centro, explicitar si el experimento simula su expansión o su entrada desde cero para evitar doble conteo. Validar el caso base antes de extrapolar a escenarios de 20, 50 o 100 MW.
4. **Comparar fechas de entrada de la obra.** La diferencia entre los dos costos incrementales mide cuánto ahorra el refuerzo al atender la carga adicional. Para valorar un adelanto, integrar los ahorros en horas representativas del período de desfase y comparar en valor presente dos calendarios de inversión y operación para la misma obra. Si el objetivo es bienestar total, incluir también ahorros de la obra para la demanda de base y explicitar otros beneficios valorados. El resultado debe identificar el nodo, los MW, la obra y el período bajo los que se obtiene. Los datos revisados aquí aún no permiten dar una cifra en dólares ni un umbral de meses.

### Reproducción de la tabla ampliada

El siguiente cálculo usa el archivo comprimido del panel horario enlazado arriba, en la revisión `69a68ee3ab015257b797579fd77cd1b71b2f200b` del proyecto. Cada fila representa una fecha y una hora local. La regla mínima cuenta fechas distintas porque ese par es único.

```python
import pandas as pd

panel = pd.read_csv("panel_estimacion.csv.gz")
datos = panel[panel["fecha"].str.startswith(("2024-10", "2024-11"))].copy()
assert not datos.duplicated(["fecha", "hora0"]).any()
assert datos[["CANTERAS_110", "QUILLOTA_220", "ctx_AJLA"]].notna().all().all()
datos["mes"] = datos["fecha"].str[:7]
datos["brecha"] = datos["CANTERAS_110"] - datos["QUILLOTA_220"]
medias = datos.groupby("ctx_AJLA")["brecha"].mean()
print("Comparación general", medias[1] - medias[0])
grupos = datos.groupby(["mes", "hora0", "ctx_AJLA"])["brecha"]
resumen = grupos.agg(["size", "mean"]).unstack()
for minimo in (1, 2, 3):
    elegibles = resumen["size"].fillna(0).min(axis=1) >= minimo
    muestra = resumen.loc[elegibles]
    contraste = muestra["mean"][1] - muestra["mean"][0]
    print(minimo, len(muestra), muestra["size"].sum(), contraste.mean())
```
